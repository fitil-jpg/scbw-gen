#!/usr/bin/env python3
"""
Asset Manager
Менеджер асетів для роботи з файлами ресурсів (текстури, моделі, звуки тощо)
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from PIL import Image
import mimetypes

from file_io_utils import FileIOUtils, FileInfo
from config_manager import ConfigManager, ConfigType

LOG = logging.getLogger(__name__)


class AssetType(Enum):
    """Типи асетів"""
    TEXTURE = "texture"
    MODEL = "model"
    SOUND = "sound"
    FONT = "font"
    SCRIPT = "script"
    DATA = "data"
    CONFIG = "config"
    UNKNOWN = "unknown"


class AssetStatus(Enum):
    """Статус асету"""
    VALID = "valid"
    MISSING = "missing"
    CORRUPTED = "corrupted"
    OUTDATED = "outdated"
    UNKNOWN = "unknown"


@dataclass
class AssetInfo:
    """Інформація про асет"""
    path: Path
    name: str
    asset_type: AssetType
    size: int
    checksum: str
    mime_type: str
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None  # для аудіо/відео
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: AssetStatus = AssetStatus.UNKNOWN
    last_modified: float = 0.0


@dataclass
class AssetCategory:
    """Категорія асетів"""
    name: str
    path: Path
    asset_types: Set[AssetType]
    description: str = ""
    max_size: Optional[int] = None  # максимальний розмір в байтах
    allowed_extensions: Set[str] = field(default_factory=set)


class AssetManager:
    """Менеджер асетів"""
    
    def __init__(self, assets_root: Union[str, Path] = "assets"):
        self.assets_root = Path(assets_root)
        self.file_utils = FileIOUtils()
        self.config_manager = ConfigManager()
        
        # Кеш асетів
        self.assets: Dict[str, AssetInfo] = {}
        self.categories: Dict[str, AssetCategory] = {}
        
        # Налаштування
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tiff', '.exr'}
        self.supported_audio_formats = {'.wav', '.mp3', '.ogg', '.flac'}
        self.supported_model_formats = {'.obj', '.fbx', '.dae', '.blend', '.usd', '.usda', '.usdc', '.gltf', '.glb'}
        self.supported_font_formats = {'.ttf', '.otf', '.woff', '.woff2'}
        
        # Ініціалізувати категорії
        self._initialize_categories()
        
        # Створити кореневу директорію асетів
        self.file_utils.ensure_directory(self.assets_root)
    
    def _initialize_categories(self) -> None:
        """Ініціалізувати категорії асетів"""
        # Текстури
        self.categories["textures"] = AssetCategory(
            name="textures",
            path=self.assets_root / "textures",
            asset_types={AssetType.TEXTURE},
            description="Текстури та зображення",
            allowed_extensions=self.supported_image_formats
        )
        
        # Моделі
        self.categories["models"] = AssetCategory(
            name="models",
            path=self.assets_root / "models",
            asset_types={AssetType.MODEL},
            description="3D моделі та меші",
            allowed_extensions=self.supported_model_formats
        )
        
        # 3D моделі з інстансингом
        self.categories["3d_models"] = AssetCategory(
            name="3d_models",
            path=self.assets_root / "3d_assets" / "models",
            asset_types={AssetType.MODEL},
            description="3D моделі з підтримкою інстансингу",
            allowed_extensions=self.supported_model_formats
        )
        
        # Звуки
        self.categories["sounds"] = AssetCategory(
            name="sounds",
            path=self.assets_root / "sounds",
            asset_types={AssetType.SOUND},
            description="Аудіо файли",
            allowed_extensions=self.supported_audio_formats
        )
        
        # Шрифти
        self.categories["fonts"] = AssetCategory(
            name="fonts",
            path=self.assets_root / "fonts",
            asset_types={AssetType.FONT},
            description="Шрифти",
            allowed_extensions=self.supported_font_formats
        )
        
        # Скрипти
        self.categories["scripts"] = AssetCategory(
            name="scripts",
            path=self.assets_root / "scripts",
            asset_types={AssetType.SCRIPT},
            description="Скрипти та код",
            allowed_extensions={'.py', '.js', '.lua', '.sh', '.bat'}
        )
        
        # Дані
        self.categories["data"] = AssetCategory(
            name="data",
            path=self.assets_root / "data",
            asset_types={AssetType.DATA},
            description="Дані та конфігурації",
            allowed_extensions={'.json', '.yaml', '.yml', '.xml', '.csv', '.txt'}
        )
        
        # Створити директорії категорій
        for category in self.categories.values():
            self.file_utils.ensure_directory(category.path)
    
    def register_asset(self, file_path: Union[str, Path], 
                      category: Optional[str] = None,
                      auto_detect_type: bool = True) -> AssetInfo:
        """Зареєструвати асет"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл асету не існує: {file_path}")
        
        # Визначити тип асету
        asset_type = self._detect_asset_type(file_path)
        
        # Визначити категорію
        if category is None:
            category = self._detect_category(asset_type)
        
        if category not in self.categories:
            raise ValueError(f"Невідома категорія асету: {category}")
        
        # Отримати інформацію про файл
        file_info = self.file_utils.get_file_info(file_path)
        if not file_info:
            raise ValueError(f"Не вдалося отримати інформацію про файл: {file_path}")
        
        # Визначити MIME тип
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Отримати додаткові метадані
        metadata = self._extract_metadata(file_path, asset_type)
        
        # Створити інформацію про асет
        asset_info = AssetInfo(
            path=file_path,
            name=file_path.stem,
            asset_type=asset_type,
            size=file_info.size,
            checksum=file_info.checksum or "",
            mime_type=mime_type,
            metadata=metadata,
            last_modified=file_info.modified_time
        )
        
        # Валідувати асет
        self._validate_asset(asset_info)
        
        # Зберегти в кеші
        asset_key = f"{category}_{file_path.stem}"
        self.assets[asset_key] = asset_info
        
        LOG.info(f"Зареєстровано асет: {file_path} (тип: {asset_type.value}, категорія: {category})")
        
        return asset_info
    
    def get_asset(self, asset_key: str) -> Optional[AssetInfo]:
        """Отримати інформацію про асет"""
        return self.assets.get(asset_key)
    
    def find_assets(self, category: Optional[str] = None, 
                   asset_type: Optional[AssetType] = None,
                   name_pattern: Optional[str] = None) -> List[AssetInfo]:
        """Знайти асети за критеріями"""
        results = []
        
        for asset in self.assets.values():
            # Фільтр по категорії
            if category and not any(asset.path.is_relative_to(cat.path) 
                                  for cat in self.categories.values() 
                                  if cat.name == category):
                continue
            
            # Фільтр по типу
            if asset_type and asset.asset_type != asset_type:
                continue
            
            # Фільтр по імені
            if name_pattern and name_pattern.lower() not in asset.name.lower():
                continue
            
            results.append(asset)
        
        return results
    
    def scan_directory(self, directory: Union[str, Path], 
                      recursive: bool = True) -> List[AssetInfo]:
        """Сканувати директорію на наявність асетів"""
        directory = Path(directory)
        assets = []
        
        if not directory.exists():
            return assets
        
        # Знайти всі файли
        files = self.file_utils.find_files(directory, "*", recursive)
        
        for file_path in files:
            try:
                # Визначити категорію за шляхом
                category = self._detect_category_by_path(file_path)
                
                if category:
                    asset_info = self.register_asset(file_path, category)
                    assets.append(asset_info)
                    
            except Exception as e:
                LOG.warning(f"Помилка реєстрації асету {file_path}: {e}")
        
        return assets
    
    def validate_asset(self, asset_key: str) -> bool:
        """Валідувати асет"""
        asset = self.assets.get(asset_key)
        if not asset:
            return False
        
        return self._validate_asset(asset)
    
    def validate_all_assets(self) -> Dict[str, List[str]]:
        """Валідувати всі асети"""
        results = {"valid": [], "invalid": [], "missing": []}
        
        for asset_key, asset in self.assets.items():
            if not asset.path.exists():
                results["missing"].append(asset_key)
                asset.status = AssetStatus.MISSING
            elif self._validate_asset(asset):
                results["valid"].append(asset_key)
                asset.status = AssetStatus.VALID
            else:
                results["invalid"].append(asset_key)
                asset.status = AssetStatus.CORRUPTED
        
        return results
    
    def get_asset_dependencies(self, asset_key: str) -> List[str]:
        """Отримати залежності асету"""
        asset = self.assets.get(asset_key)
        if not asset:
            return []
        
        return asset.dependencies
    
    def find_missing_assets(self) -> List[str]:
        """Знайти відсутні асети"""
        missing = []
        
        for asset_key, asset in self.assets.items():
            if not asset.path.exists():
                missing.append(asset_key)
                asset.status = AssetStatus.MISSING
        
        return missing
    
    def cleanup_missing_assets(self) -> int:
        """Очистити записи відсутніх асетів"""
        missing_keys = self.find_missing_assets()
        
        for key in missing_keys:
            del self.assets[key]
        
        LOG.info(f"Видалено {len(missing_keys)} записів відсутніх асетів")
        
        return len(missing_keys)
    
    def export_asset_list(self, output_path: Union[str, Path], 
                         format_type: str = "json") -> Path:
        """Експортувати список асетів"""
        output_path = Path(output_path)
        
        # Підготувати дані для експорту
        export_data = {
            "assets": {},
            "categories": {},
            "summary": {
                "total_assets": len(self.assets),
                "total_size": sum(asset.size for asset in self.assets.values()),
                "asset_types": {}
            }
        }
        
        # Дані асетів
        for asset_key, asset in self.assets.items():
            export_data["assets"][asset_key] = {
                "path": str(asset.path),
                "name": asset.name,
                "type": asset.asset_type.value,
                "size": asset.size,
                "checksum": asset.checksum,
                "mime_type": asset.mime_type,
                "dimensions": asset.dimensions,
                "status": asset.status.value,
                "metadata": asset.metadata,
                "dependencies": asset.dependencies
            }
        
        # Дані категорій
        for cat_name, category in self.categories.items():
            export_data["categories"][cat_name] = {
                "name": category.name,
                "path": str(category.path),
                "description": category.description,
                "asset_types": [t.value for t in category.asset_types],
                "allowed_extensions": list(category.allowed_extensions)
            }
        
        # Підсумки по типах
        for asset in self.assets.values():
            asset_type = asset.asset_type.value
            if asset_type not in export_data["summary"]["asset_types"]:
                export_data["summary"]["asset_types"][asset_type] = 0
            export_data["summary"]["asset_types"][asset_type] += 1
        
        # Зберегти файл
        if format_type.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        elif format_type.lower() == "yaml":
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Непідтримуваний формат експорту: {format_type}")
        
        LOG.info(f"Список асетів експортовано: {output_path}")
        
        return output_path
    
    def _detect_asset_type(self, file_path: Path) -> AssetType:
        """Визначити тип асету за розширенням файлу"""
        suffix = file_path.suffix.lower()
        
        if suffix in self.supported_image_formats:
            return AssetType.TEXTURE
        elif suffix in self.supported_audio_formats:
            return AssetType.SOUND
        elif suffix in self.supported_model_formats:
            return AssetType.MODEL
        elif suffix in self.supported_font_formats:
            return AssetType.FONT
        elif suffix in {'.py', '.js', '.lua', '.sh', '.bat'}:
            return AssetType.SCRIPT
        elif suffix in {'.json', '.yaml', '.yml', '.xml', '.csv', '.txt'}:
            return AssetType.DATA
        else:
            return AssetType.UNKNOWN
    
    def _detect_category(self, asset_type: AssetType) -> str:
        """Визначити категорію за типом асету"""
        for cat_name, category in self.categories.items():
            if asset_type in category.asset_types:
                return cat_name
        
        return "data"  # за замовчуванням
    
    def _detect_category_by_path(self, file_path: Path) -> Optional[str]:
        """Визначити категорію за шляхом файлу"""
        for cat_name, category in self.categories.items():
            if file_path.is_relative_to(category.path):
                return cat_name
        
        return None
    
    def _extract_metadata(self, file_path: Path, asset_type: AssetType) -> Dict[str, Any]:
        """Витягти метадані з файлу"""
        metadata = {}
        
        try:
            if asset_type == AssetType.TEXTURE:
                # Метадані зображення
                with Image.open(file_path) as img:
                    metadata["width"] = img.width
                    metadata["height"] = img.height
                    metadata["mode"] = img.mode
                    metadata["format"] = img.format
                    
                    # EXIF дані якщо є
                    if hasattr(img, '_getexif') and img._getexif():
                        metadata["exif"] = dict(img._getexif())
            
            elif asset_type == AssetType.SOUND:
                # Базові метадані аудіо (потребує додаткових бібліотек)
                metadata["file_size"] = file_path.stat().st_size
            
            elif asset_type == AssetType.MODEL:
                # Базові метадані моделі
                metadata["file_size"] = file_path.stat().st_size
                metadata["format"] = file_path.suffix.lower()
            
        except Exception as e:
            LOG.warning(f"Помилка витягування метаданих з {file_path}: {e}")
        
        return metadata
    
    def _validate_asset(self, asset: AssetInfo) -> bool:
        """Валідувати асет"""
        try:
            # Перевірити існування файлу
            if not asset.path.exists():
                asset.status = AssetStatus.MISSING
                return False
            
            # Перевірити розмір файлу
            if asset.size == 0:
                asset.status = AssetStatus.CORRUPTED
                return False
            
            # Перевірити цілісність файлу (базова перевірка)
            if asset.asset_type == AssetType.TEXTURE:
                try:
                    with Image.open(asset.path) as img:
                        img.verify()
                except Exception:
                    asset.status = AssetStatus.CORRUPTED
                    return False
            
            asset.status = AssetStatus.VALID
            return True
            
        except Exception as e:
            LOG.warning(f"Помилка валідації асету {asset.path}: {e}")
            asset.status = AssetStatus.CORRUPTED
            return False


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення менеджера асетів
    asset_manager = AssetManager("assets")
    
    try:
        # Сканувати директорію асетів
        assets = asset_manager.scan_directory("assets", recursive=True)
        print(f"Знайдено асетів: {len(assets)}")
        
        # Знайти текстури
        textures = asset_manager.find_assets(asset_type=AssetType.TEXTURE)
        print(f"Текстур: {len(textures)}")
        
        # Валідувати всі асети
        validation_results = asset_manager.validate_all_assets()
        print(f"Валідних асетів: {len(validation_results['valid'])}")
        print(f"Невалідних асетів: {len(validation_results['invalid'])}")
        print(f"Відсутніх асетів: {len(validation_results['missing'])}")
        
        # Експортувати список асетів
        asset_manager.export_asset_list("asset_list.json", "json")
        
    except Exception as e:
        print(f"Помилка: {e}")