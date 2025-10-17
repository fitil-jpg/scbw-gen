#!/usr/bin/env python3
"""
Configuration Manager
Менеджер конфігурацій з підтримкою різних форматів та валідації
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml

from config_parser import (
    UniversalConfigParser, ConfigFormat, ConfigSchema, 
    ValidationRule, ConfigValidationError, ConfigParseError
)
from file_io_utils import FileIOUtils, FileIOError

LOG = logging.getLogger(__name__)


class ConfigType(Enum):
    """Типи конфігурацій"""
    PACK = "pack"
    SCENE = "scene"
    BUILDINGS = "buildings"
    UNITS = "units"
    EFFECTS = "effects"
    TERRAIN = "terrain"
    CUSTOM = "custom"


@dataclass
class ConfigMetadata:
    """Метадані конфігурації"""
    name: str
    type: ConfigType
    version: str
    description: str = ""
    author: str = ""
    created_at: str = ""
    modified_at: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ConfigEntry:
    """Запис конфігурації"""
    path: Path
    metadata: ConfigMetadata
    data: Dict[str, Any]
    schema: Optional[ConfigSchema] = None
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)


class ConfigManager:
    """Менеджер конфігурацій"""
    
    def __init__(self, config_directory: Union[str, Path] = "configs"):
        self.config_directory = Path(config_directory)
        self.parser = UniversalConfigParser()
        self.file_utils = FileIOUtils()
        self.entries: Dict[str, ConfigEntry] = {}
        self.schemas: Dict[ConfigType, ConfigSchema] = {}
        
        # Ініціалізувати схеми
        self._initialize_schemas()
        
        # Створити директорію конфігурацій якщо не існує
        self.file_utils.ensure_directory(self.config_directory)
    
    def _initialize_schemas(self) -> None:
        """Ініціалізувати схеми валідації"""
        from config_parser import create_pack_config_schema, create_scene_config_schema
        
        self.schemas[ConfigType.PACK] = create_pack_config_schema()
        self.schemas[ConfigType.SCENE] = create_scene_config_schema()
        
        # Схема для будівель
        buildings_schema = ConfigSchema("buildings_config", "1.0")
        buildings_schema.add_rule(ValidationRule("buildings", required=True, data_type=dict))
        buildings_schema.add_rule(ValidationRule("owners", required=False, data_type=dict))
        self.schemas[ConfigType.BUILDINGS] = buildings_schema
        
        # Схема для юнітів
        units_schema = ConfigSchema("units_config", "1.0")
        units_schema.add_rule(ValidationRule("units", required=True, data_type=dict))
        units_schema.add_rule(ValidationRule("formations", required=False, data_type=dict))
        self.schemas[ConfigType.UNITS] = units_schema
        
        # Схема для ефектів
        effects_schema = ConfigSchema("effects_config", "1.0")
        effects_schema.add_rule(ValidationRule("effects", required=True, data_type=dict))
        self.schemas[ConfigType.EFFECTS] = effects_schema
        
        # Схема для рельєфу
        terrain_schema = ConfigSchema("terrain_config", "1.0")
        terrain_schema.add_rule(ValidationRule("terrain_types", required=True, data_type=dict))
        self.schemas[ConfigType.TERRAIN] = terrain_schema
    
    def register_schema(self, config_type: ConfigType, schema: ConfigSchema) -> None:
        """Зареєструвати схему валідації"""
        self.schemas[config_type] = schema
        LOG.info(f"Зареєстровано схему для типу {config_type.value}")
    
    def load_config(self, file_path: Union[str, Path], 
                   config_type: Optional[ConfigType] = None,
                   auto_detect_type: bool = True) -> ConfigEntry:
        """Завантажити конфігурацію"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigParseError(f"Файл конфігурації не існує: {file_path}")
        
        # Автоматично визначити тип конфігурації
        if auto_detect_type and config_type is None:
            config_type = self._detect_config_type(file_path)
        
        if config_type is None:
            config_type = ConfigType.CUSTOM
        
        # Завантажити дані
        try:
            data = self.parser.load_file(file_path)
        except Exception as e:
            raise ConfigParseError(f"Помилка завантаження конфігурації: {e}")
        
        # Створити метадані
        metadata = self._extract_metadata(data, config_type, file_path)
        
        # Валідувати конфігурацію
        schema = self.schemas.get(config_type)
        is_valid = True
        validation_errors = []
        
        if schema:
            validation_errors = self.parser.validate_config(data, schema)
            is_valid = len(validation_errors) == 0
        
        # Створити запис конфігурації
        entry = ConfigEntry(
            path=file_path,
            metadata=metadata,
            data=data,
            schema=schema,
            is_valid=is_valid,
            validation_errors=validation_errors
        )
        
        # Зберегти в кеші
        config_key = f"{config_type.value}_{file_path.stem}"
        self.entries[config_key] = entry
        
        LOG.info(f"Завантажено конфігурацію: {file_path} (тип: {config_type.value})")
        
        return entry
    
    def save_config(self, entry: ConfigEntry, 
                   output_path: Optional[Union[str, Path]] = None,
                   format_type: Optional[ConfigFormat] = None) -> Path:
        """Зберегти конфігурацію"""
        if output_path is None:
            output_path = entry.path
        else:
            output_path = Path(output_path)
        
        # Валідувати перед збереженням
        if entry.schema and not entry.is_valid:
            LOG.warning(f"Збереження невалідної конфігурації: {entry.path}")
        
        # Додати метадані до даних
        data_with_metadata = entry.data.copy()
        data_with_metadata["_metadata"] = {
            "name": entry.metadata.name,
            "type": entry.metadata.type.value,
            "version": entry.metadata.version,
            "description": entry.metadata.description,
            "author": entry.metadata.author,
            "created_at": entry.metadata.created_at,
            "modified_at": entry.metadata.modified_at,
            "tags": entry.metadata.tags,
            "dependencies": entry.metadata.dependencies
        }
        
        # Зберегти файл
        self.parser.save_file(data_with_metadata, output_path, format_type)
        
        # Оновити запис
        entry.path = output_path
        self.entries[f"{entry.metadata.type.value}_{output_path.stem}"] = entry
        
        LOG.info(f"Збережено конфігурацію: {output_path}")
        
        return output_path
    
    def get_config(self, config_key: str) -> Optional[ConfigEntry]:
        """Отримати конфігурацію за ключем"""
        return self.entries.get(config_key)
    
    def list_configs(self, config_type: Optional[ConfigType] = None) -> List[ConfigEntry]:
        """Список всіх конфігурацій"""
        if config_type is None:
            return list(self.entries.values())
        
        return [entry for entry in self.entries.values() 
                if entry.metadata.type == config_type]
    
    def validate_config(self, entry: ConfigEntry) -> bool:
        """Валідувати конфігурацію"""
        if not entry.schema:
            LOG.warning(f"Немає схеми для валідації: {entry.path}")
            return True
        
        validation_errors = self.parser.validate_config(entry.data, entry.schema)
        entry.validation_errors = validation_errors
        entry.is_valid = len(validation_errors) == 0
        
        if not entry.is_valid:
            LOG.warning(f"Конфігурація невалідна: {entry.path}")
            for error in validation_errors:
                LOG.warning(f"  - {error}")
        
        return entry.is_valid
    
    def merge_configs(self, base_entry: ConfigEntry, 
                     override_entry: ConfigEntry) -> ConfigEntry:
        """Об'єднати дві конфігурації"""
        merged_data = self.parser.merge_configs(base_entry.data, override_entry.data)
        
        # Створити новий запис
        merged_metadata = ConfigMetadata(
            name=f"{base_entry.metadata.name}_merged",
            type=base_entry.metadata.type,
            version=base_entry.metadata.version,
            description=f"Merged: {base_entry.metadata.name} + {override_entry.metadata.name}",
            author=base_entry.metadata.author,
            created_at=base_entry.metadata.created_at,
            modified_at=base_entry.metadata.modified_at,
            tags=list(set(base_entry.metadata.tags + override_entry.metadata.tags)),
            dependencies=list(set(base_entry.metadata.dependencies + override_entry.metadata.dependencies))
        )
        
        merged_entry = ConfigEntry(
            path=Path("merged_config"),
            metadata=merged_metadata,
            data=merged_data,
            schema=base_entry.schema
        )
        
        # Валідувати об'єднану конфігурацію
        self.validate_config(merged_entry)
        
        return merged_entry
    
    def convert_config(self, entry: ConfigEntry, 
                      target_format: ConfigFormat) -> ConfigEntry:
        """Конвертувати конфігурацію в інший формат"""
        # Визначити цільовий шлях
        if target_format == ConfigFormat.YAML:
            new_path = entry.path.with_suffix('.yaml')
        elif target_format == ConfigFormat.JSON:
            new_path = entry.path.with_suffix('.json')
        else:
            raise ValueError(f"Непідтримуваний формат: {target_format}")
        
        # Зберегти в новому форматі
        self.parser.save_file(entry.data, new_path, target_format)
        
        # Створити новий запис
        converted_entry = ConfigEntry(
            path=new_path,
            metadata=entry.metadata,
            data=entry.data,
            schema=entry.schema,
            is_valid=entry.is_valid,
            validation_errors=entry.validation_errors.copy()
        )
        
        # Зберегти в кеші
        config_key = f"{entry.metadata.type.value}_{new_path.stem}"
        self.entries[config_key] = converted_entry
        
        LOG.info(f"Конфігурацію конвертовано: {entry.path} -> {new_path}")
        
        return converted_entry
    
    def backup_config(self, entry: ConfigEntry) -> Path:
        """Створити резервну копію конфігурації"""
        backup_path = self.file_utils.backup_file(entry.path)
        
        LOG.info(f"Створено резервну копію: {backup_path}")
        
        return backup_path
    
    def reload_config(self, config_key: str) -> Optional[ConfigEntry]:
        """Перезавантажити конфігурацію"""
        entry = self.entries.get(config_key)
        if not entry:
            return None
        
        try:
            # Завантажити знову
            new_entry = self.load_config(entry.path, entry.metadata.type, False)
            
            # Оновити в кеші
            self.entries[config_key] = new_entry
            
            LOG.info(f"Перезавантажено конфігурацію: {entry.path}")
            
            return new_entry
            
        except Exception as e:
            LOG.error(f"Помилка перезавантаження конфігурації {entry.path}: {e}")
            return None
    
    def _detect_config_type(self, file_path: Path) -> ConfigType:
        """Автоматично визначити тип конфігурації за шляхом та вмістом"""
        # Перевірити за шляхом
        path_str = str(file_path).lower()
        
        if "pack" in path_str:
            return ConfigType.PACK
        elif "scene" in path_str:
            return ConfigType.SCENE
        elif "buildings" in path_str:
            return ConfigType.BUILDINGS
        elif "units" in path_str:
            return ConfigType.UNITS
        elif "effects" in path_str:
            return ConfigType.EFFECTS
        elif "terrain" in path_str:
            return ConfigType.TERRAIN
        
        # Спробувати визначити за вмістом
        try:
            data = self.parser.load_file(file_path)
            
            if "shots" in data and "image_size" in data:
                return ConfigType.PACK
            elif "scene" in data and "units" in data:
                return ConfigType.SCENE
            elif "buildings" in data:
                return ConfigType.BUILDINGS
            elif "units" in data:
                return ConfigType.UNITS
            elif "effects" in data:
                return ConfigType.EFFECTS
            elif "terrain_types" in data:
                return ConfigType.TERRAIN
            
        except Exception:
            pass
        
        return ConfigType.CUSTOM
    
    def _extract_metadata(self, data: Dict[str, Any], 
                         config_type: ConfigType, 
                         file_path: Path) -> ConfigMetadata:
        """Витягти метадані з даних конфігурації"""
        metadata_section = data.get("_metadata", {})
        
        return ConfigMetadata(
            name=metadata_section.get("name", file_path.stem),
            type=config_type,
            version=metadata_section.get("version", "1.0"),
            description=metadata_section.get("description", ""),
            author=metadata_section.get("author", ""),
            created_at=metadata_section.get("created_at", ""),
            modified_at=metadata_section.get("modified_at", ""),
            tags=metadata_section.get("tags", []),
            dependencies=metadata_section.get("dependencies", [])
        )


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення менеджера конфігурацій
    config_manager = ConfigManager("configs")
    
    try:
        # Завантажити існуючі конфігурації
        pack_config = config_manager.load_config("params/pack.yaml")
        print(f"Завантажено pack конфігурацію: {pack_config.metadata.name}")
        print(f"Валідна: {pack_config.is_valid}")
        
        scene_config = config_manager.load_config("scene.yaml")
        print(f"Завантажено scene конфігурацію: {scene_config.metadata.name}")
        print(f"Валідна: {scene_config.is_valid}")
        
        # Список всіх конфігурацій
        all_configs = config_manager.list_configs()
        print(f"Всього конфігурацій: {len(all_configs)}")
        
        # Список конфігурацій певного типу
        pack_configs = config_manager.list_configs(ConfigType.PACK)
        print(f"Pack конфігурацій: {len(pack_configs)}")
        
    except Exception as e:
        print(f"Помилка: {e}")