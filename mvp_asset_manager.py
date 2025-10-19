#!/usr/bin/env python3
"""
MVP Asset Manager - Компактна версія менеджера асетів
Розмір: ~80 рядків (замість 508)
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

@dataclass
class SimpleAsset:
    """Простий асет"""
    path: Path
    name: str
    asset_type: str
    size: int

class SimpleAssetManager:
    """Простий менеджер асетів для MVP"""
    
    def __init__(self, assets_root: str = "assets"):
        self.assets_root = Path(assets_root)
        self.assets: Dict[str, SimpleAsset] = {}
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Створити директорію асетів"""
        self.assets_root.mkdir(exist_ok=True)
        (self.assets_root / "textures").mkdir(exist_ok=True)
        (self.assets_root / "models").mkdir(exist_ok=True)
        (self.assets_root / "sounds").mkdir(exist_ok=True)
    
    def register_asset(self, file_path: Union[str, Path], asset_type: str = "unknown") -> SimpleAsset:
        """Зареєструвати асет"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не існує: {file_path}")
        
        asset = SimpleAsset(
            path=file_path,
            name=file_path.stem,
            asset_type=asset_type,
            size=file_path.stat().st_size
        )
        
        self.assets[asset.name] = asset
        return asset
    
    def get_asset(self, name: str) -> Optional[SimpleAsset]:
        """Отримати асет за ім'ям"""
        return self.assets.get(name)
    
    def list_assets(self, asset_type: Optional[str] = None) -> List[SimpleAsset]:
        """Список асетів"""
        if asset_type is None:
            return list(self.assets.values())
        return [asset for asset in self.assets.values() if asset.asset_type == asset_type]
    
    def scan_directory(self, directory: Optional[Union[str, Path]] = None) -> List[SimpleAsset]:
        """Сканувати директорію"""
        if directory is None:
            directory = self.assets_root
        
        directory = Path(directory)
        assets = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                asset_type = self._detect_type(file_path)
                try:
                    asset = self.register_asset(file_path, asset_type)
                    assets.append(asset)
                except Exception as e:
                    print(f"Помилка реєстрації {file_path}: {e}")
        
        return assets
    
    def _detect_type(self, file_path: Path) -> str:
        """Визначити тип файлу"""
        suffix = file_path.suffix.lower()
        
        if suffix in {'.png', '.jpg', '.jpeg', '.tga', '.bmp'}:
            return "texture"
        elif suffix in {'.obj', '.fbx', '.blend', '.usd'}:
            return "model"
        elif suffix in {'.wav', '.mp3', '.ogg'}:
            return "sound"
        else:
            return "unknown"
    
    def get_total_size(self) -> int:
        """Загальний розмір асетів"""
        return sum(asset.size for asset in self.assets.values())
    
    def cleanup_missing(self) -> int:
        """Очистити відсутні асети"""
        missing = [name for name, asset in self.assets.items() if not asset.path.exists()]
        for name in missing:
            del self.assets[name]
        return len(missing)