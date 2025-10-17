#!/usr/bin/env python3
"""
File I/O Utilities
Утиліти для роботи з файлами та директоріями
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Callable, Iterator
from dataclasses import dataclass
from enum import Enum
import hashlib
import tempfile
from contextlib import contextmanager

LOG = logging.getLogger(__name__)


class FileOperation(Enum):
    """Типи файлових операцій"""
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    CREATE = "create"
    BACKUP = "backup"


@dataclass
class FileInfo:
    """Інформація про файл"""
    path: Path
    size: int
    modified_time: float
    is_file: bool
    is_dir: bool
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.is_file and self.checksum is None:
            self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Обчислити MD5 хеш файлу"""
        if not self.is_file:
            return ""
        
        hash_md5 = hashlib.md5()
        try:
            with open(self.path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            LOG.warning(f"Не вдалося обчислити хеш для {self.path}: {e}")
            return ""


class FileIOError(Exception):
    """Помилка файлових операцій"""
    pass


class FileIOUtils:
    """Утиліти для роботи з файлами"""
    
    def __init__(self, create_backups: bool = True, backup_suffix: str = ".bak"):
        self.create_backups = create_backups
        self.backup_suffix = backup_suffix
    
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """Створити директорію якщо вона не існує"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_file_info(self, path: Union[str, Path]) -> Optional[FileInfo]:
        """Отримати інформацію про файл"""
        path = Path(path)
        
        if not path.exists():
            return None
        
        stat = path.stat()
        return FileInfo(
            path=path,
            size=stat.st_size,
            modified_time=stat.st_mtime,
            is_file=path.is_file(),
            is_dir=path.is_dir(),
        )
    
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path], 
                  overwrite: bool = False) -> bool:
        """Копіювати файл"""
        src = Path(src)
        dst = Path(dst)
        
        if not src.exists():
            raise FileIOError(f"Вихідний файл не існує: {src}")
        
        if not src.is_file():
            raise FileIOError(f"Шлях не є файлом: {src}")
        
        if dst.exists() and not overwrite:
            raise FileIOError(f"Файл призначення вже існує: {dst}")
        
        # Створити директорію призначення якщо потрібно
        self.ensure_directory(dst.parent)
        
        try:
            shutil.copy2(src, dst)
            LOG.info(f"Файл скопійовано: {src} -> {dst}")
            return True
        except Exception as e:
            raise FileIOError(f"Помилка копіювання файлу: {e}")
    
    def move_file(self, src: Union[str, Path], dst: Union[str, Path], 
                  overwrite: bool = False) -> bool:
        """Перемістити файл"""
        src = Path(src)
        dst = Path(dst)
        
        if not src.exists():
            raise FileIOError(f"Вихідний файл не існує: {src}")
        
        if not src.is_file():
            raise FileIOError(f"Шлях не є файлом: {src}")
        
        if dst.exists() and not overwrite:
            raise FileIOError(f"Файл призначення вже існує: {dst}")
        
        # Створити директорію призначення якщо потрібно
        self.ensure_directory(dst.parent)
        
        try:
            shutil.move(str(src), str(dst))
            LOG.info(f"Файл переміщено: {src} -> {dst}")
            return True
        except Exception as e:
            raise FileIOError(f"Помилка переміщення файлу: {e}")
    
    def delete_file(self, path: Union[str, Path], backup: bool = None) -> bool:
        """Видалити файл"""
        path = Path(path)
        
        if not path.exists():
            LOG.warning(f"Файл не існує: {path}")
            return False
        
        if not path.is_file():
            raise FileIOError(f"Шлях не є файлом: {path}")
        
        # Створити резервну копію якщо потрібно
        if (backup is True) or (backup is None and self.create_backups):
            backup_path = path.with_suffix(path.suffix + self.backup_suffix)
            self.copy_file(path, backup_path, overwrite=True)
            LOG.info(f"Створено резервну копію: {backup_path}")
        
        try:
            path.unlink()
            LOG.info(f"Файл видалено: {path}")
            return True
        except Exception as e:
            raise FileIOError(f"Помилка видалення файлу: {e}")
    
    def backup_file(self, path: Union[str, Path], 
                   backup_path: Optional[Union[str, Path]] = None) -> Path:
        """Створити резервну копію файлу"""
        path = Path(path)
        
        if not path.exists():
            raise FileIOError(f"Файл не існує: {path}")
        
        if backup_path is None:
            backup_path = path.with_suffix(path.suffix + self.backup_suffix)
        else:
            backup_path = Path(backup_path)
        
        self.copy_file(path, backup_path, overwrite=True)
        return backup_path
    
    def find_files(self, directory: Union[str, Path], 
                   pattern: str = "*", recursive: bool = True) -> List[Path]:
        """Знайти файли за шаблоном"""
        directory = Path(directory)
        
        if not directory.exists():
            return []
        
        if not directory.is_dir():
            return []
        
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    
    def find_files_by_extension(self, directory: Union[str, Path], 
                               extensions: List[str], 
                               recursive: bool = True) -> List[Path]:
        """Знайти файли за розширеннями"""
        directory = Path(directory)
        files = []
        
        for ext in extensions:
            pattern = f"*.{ext.lstrip('.')}"
            files.extend(self.find_files(directory, pattern, recursive))
        
        return files
    
    def get_directory_size(self, directory: Union[str, Path]) -> int:
        """Отримати розмір директорії в байтах"""
        directory = Path(directory)
        total_size = 0
        
        if not directory.exists() or not directory.is_dir():
            return 0
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def clean_directory(self, directory: Union[str, Path], 
                       pattern: str = "*", 
                       dry_run: bool = False) -> List[Path]:
        """Очистити директорію від файлів за шаблоном"""
        directory = Path(directory)
        files_to_remove = self.find_files(directory, pattern, recursive=True)
        removed_files = []
        
        for file_path in files_to_remove:
            if file_path.is_file():
                if not dry_run:
                    try:
                        file_path.unlink()
                        removed_files.append(file_path)
                        LOG.info(f"Файл видалено: {file_path}")
                    except Exception as e:
                        LOG.error(f"Помилка видалення файлу {file_path}: {e}")
                else:
                    removed_files.append(file_path)
                    LOG.info(f"Файл буде видалено (dry run): {file_path}")
        
        return removed_files
    
    def sync_directories(self, src: Union[str, Path], dst: Union[str, Path], 
                        delete_extra: bool = False) -> Dict[str, List[Path]]:
        """Синхронізувати директорії"""
        src = Path(src)
        dst = Path(dst)
        
        if not src.exists() or not src.is_dir():
            raise FileIOError(f"Вихідна директорія не існує: {src}")
        
        self.ensure_directory(dst)
        
        result = {
            "copied": [],
            "updated": [],
            "deleted": [],
            "errors": []
        }
        
        # Копіювати/оновлювати файли з src в dst
        for src_file in src.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(src)
                dst_file = dst / rel_path
                
                try:
                    # Перевірити чи потрібно оновлювати файл
                    if dst_file.exists():
                        src_info = self.get_file_info(src_file)
                        dst_info = self.get_file_info(dst_file)
                        
                        if (src_info and dst_info and 
                            src_info.checksum != dst_info.checksum):
                            self.copy_file(src_file, dst_file, overwrite=True)
                            result["updated"].append(dst_file)
                        else:
                            result["copied"].append(dst_file)
                    else:
                        self.copy_file(src_file, dst_file)
                        result["copied"].append(dst_file)
                        
                except Exception as e:
                    result["errors"].append(dst_file)
                    LOG.error(f"Помилка синхронізації файлу {src_file}: {e}")
        
        # Видалити зайві файли якщо потрібно
        if delete_extra:
            for dst_file in dst.rglob("*"):
                if dst_file.is_file():
                    rel_path = dst_file.relative_to(dst)
                    src_file = src / rel_path
                    
                    if not src_file.exists():
                        try:
                            dst_file.unlink()
                            result["deleted"].append(dst_file)
                            LOG.info(f"Видалено зайвий файл: {dst_file}")
                        except Exception as e:
                            result["errors"].append(dst_file)
                            LOG.error(f"Помилка видалення зайвого файлу {dst_file}: {e}")
        
        return result
    
    @contextmanager
    def temporary_file(self, suffix: str = ".tmp", 
                      prefix: str = "file_io_") -> Iterator[Path]:
        """Контекстний менеджер для тимчасового файлу"""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix, 
                prefix=prefix, 
                delete=False
            )
            temp_path = Path(temp_file.name)
            temp_file.close()
            yield temp_path
        finally:
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
    
    @contextmanager
    def temporary_directory(self, prefix: str = "file_io_") -> Iterator[Path]:
        """Контекстний менеджер для тимчасової директорії"""
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            yield Path(temp_dir)
        finally:
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def batch_operation(self, operations: List[Dict[str, Any]], 
                       dry_run: bool = False) -> Dict[str, Any]:
        """Виконати пакет операцій з файлами"""
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        for op in operations:
            try:
                op_type = op.get("operation")
                src = op.get("source")
                dst = op.get("destination")
                
                if not op_type or not src:
                    results["skipped"].append({"operation": op, "reason": "Недостатньо параметрів"})
                    continue
                
                if dry_run:
                    results["skipped"].append({"operation": op, "reason": "Dry run mode"})
                    continue
                
                if op_type == FileOperation.COPY.value:
                    self.copy_file(src, dst, overwrite=op.get("overwrite", False))
                    results["success"].append(op)
                elif op_type == FileOperation.MOVE.value:
                    self.move_file(src, dst, overwrite=op.get("overwrite", False))
                    results["success"].append(op)
                elif op_type == FileOperation.DELETE.value:
                    self.delete_file(src, backup=op.get("backup", None))
                    results["success"].append(op)
                elif op_type == FileOperation.BACKUP.value:
                    backup_path = self.backup_file(src, dst)
                    results["success"].append({**op, "backup_path": str(backup_path)})
                else:
                    results["skipped"].append({"operation": op, "reason": f"Невідомий тип операції: {op_type}"})
                    
            except Exception as e:
                results["failed"].append({"operation": op, "error": str(e)})
                LOG.error(f"Помилка виконання операції {op}: {e}")
        
        return results


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення утиліт
    file_utils = FileIOUtils(create_backups=True)
    
    # Приклад роботи з файлами
    try:
        # Створити тестову директорію
        test_dir = Path("test_files")
        file_utils.ensure_directory(test_dir)
        
        # Створити тестовий файл
        test_file = test_dir / "test.txt"
        test_file.write_text("Тестовий контент")
        
        # Отримати інформацію про файл
        file_info = file_utils.get_file_info(test_file)
        if file_info:
            print(f"Файл: {file_info.path}")
            print(f"Розмір: {file_info.size} байт")
            print(f"Хеш: {file_info.checksum}")
        
        # Копіювати файл
        copy_file = test_dir / "test_copy.txt"
        file_utils.copy_file(test_file, copy_file)
        
        # Знайти файли
        files = file_utils.find_files(test_dir, "*.txt")
        print(f"Знайдено файлів: {len(files)}")
        
        # Очистити тестову директорію
        file_utils.clean_directory(test_dir, dry_run=False)
        
    except Exception as e:
        print(f"Помилка: {e}")