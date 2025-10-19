#!/usr/bin/env python3
"""
MVP Config Manager - Компактна версія менеджера конфігурацій
Розмір: ~60 рядків (замість 405)
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union

class SimpleConfigManager:
    """Простий менеджер конфігурацій для MVP"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Створити директорію конфігурацій"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Завантажити конфігурацію"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не існує: {file_path}")
        
        # Визначити формат
        if file_path.suffix.lower() in {'.yaml', '.yml'}:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        elif file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Непідтримуваний формат: {file_path.suffix}")
        
        # Зберегти в кеші
        config_name = file_path.stem
        self.configs[config_name] = data
        
        return data
    
    def save_config(self, data: Dict[str, Any], file_path: Union[str, Path], 
                   format_type: str = "yaml") -> Path:
        """Зберегти конфігурацію"""
        file_path = Path(file_path)
        
        if format_type.lower() == "yaml":
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        elif format_type.lower() == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Непідтримуваний формат: {format_type}")
        
        # Оновити кеш
        config_name = file_path.stem
        self.configs[config_name] = data
        
        return file_path
    
    def get_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Отримати конфігурацію за ім'ям"""
        return self.configs.get(name)
    
    def list_configs(self) -> list:
        """Список конфігурацій"""
        return list(self.configs.keys())
    
    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Об'єднати конфігурації"""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged