#!/usr/bin/env python3
"""
MVP Asset Loader - Модульний завантажувач асетів
Розмір: ~50 рядків
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from mvp_asset_manager import SimpleAssetManager

class MVPAssetLoader:
    """Модульний завантажувач асетів для MVP"""
    
    def __init__(self, assets_root: str = "assets"):
        self.asset_manager = SimpleAssetManager(assets_root)
        self.loaded_assets: Dict[str, Any] = {}
    
    def load_asset_stack(self, stack_name: str, asset_paths: List[str]) -> Dict[str, Any]:
        """Завантажити стек асетів"""
        stack_assets = {}
        
        for asset_path in asset_paths:
            try:
                # Зареєструвати асет
                asset = self.asset_manager.register_asset(asset_path)
                
                # Завантажити залежно від типу
                if asset.asset_type == "texture":
                    stack_assets[asset.name] = self._load_texture(asset.path)
                elif asset.asset_type == "model":
                    stack_assets[asset.name] = self._load_model(asset.path)
                elif asset.asset_type == "sound":
                    stack_assets[asset.name] = self._load_sound(asset.path)
                else:
                    # Для невідомих типів також додаємо
                    stack_assets[asset.name] = str(asset.path)
                
                print(f"✅ Завантажено: {asset.name} ({asset.asset_type})")
                
            except Exception as e:
                print(f"❌ Помилка завантаження {asset_path}: {e}")
        
        self.loaded_assets[stack_name] = stack_assets
        return stack_assets
    
    def get_asset(self, stack_name: str, asset_name: str) -> Optional[Any]:
        """Отримати асет з стеку"""
        return self.loaded_assets.get(stack_name, {}).get(asset_name)
    
    def list_stacks(self) -> List[str]:
        """Список завантажених стеків"""
        return list(self.loaded_assets.keys())
    
    def _load_texture(self, path: Path) -> str:
        """Завантажити текстуру (повертаємо шлях)"""
        return str(path)
    
    def _load_model(self, path: Path) -> str:
        """Завантажити модель (повертаємо шлях)"""
        return str(path)
    
    def _load_sound(self, path: Path) -> str:
        """Завантажити звук (повертаємо шлях)"""
        return str(path)
    
    def create_asset_pack(self, pack_name: str, assets: Dict[str, str]) -> Dict[str, Any]:
        """Створити пакет асетів"""
        pack = {
            "name": pack_name,
            "assets": assets,
            "total_size": sum(self.asset_manager.get_asset(name).size 
                            for name in assets.keys() 
                            if self.asset_manager.get_asset(name))
        }
        return pack