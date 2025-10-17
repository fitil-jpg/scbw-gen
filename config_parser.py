#!/usr/bin/env python3
"""
Universal Configuration Parser
Універсальний парсер конфігурацій для YAML/JSON файлів з валідацією
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml

LOG = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Підтримувані формати конфігурацій"""
    YAML = "yaml"
    JSON = "json"
    AUTO = "auto"


@dataclass
class ValidationRule:
    """Правило валідації для поля конфігурації"""
    field_path: str
    required: bool = False
    data_type: Optional[Type] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable[[Any], bool]] = None
    error_message: Optional[str] = None


@dataclass
class ConfigSchema:
    """Схема валідації конфігурації"""
    name: str
    version: str = "1.0"
    rules: List[ValidationRule] = field(default_factory=list)
    
    def add_rule(self, rule: ValidationRule) -> 'ConfigSchema':
        """Додати правило валідації"""
        self.rules.append(rule)
        return self


class ConfigValidationError(Exception):
    """Помилка валідації конфігурації"""
    
    def __init__(self, message: str, field_path: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.field_path = field_path
        self.details = details or {}


class ConfigParseError(Exception):
    """Помилка парсингу конфігурації"""
    pass


class UniversalConfigParser:
    """Універсальний парсер конфігурацій з підтримкою YAML/JSON"""
    
    def __init__(self, auto_detect_format: bool = True):
        self.auto_detect_format = auto_detect_format
        self.supported_extensions = {'.yaml', '.yml', '.json'}
    
    def detect_format(self, file_path: Path) -> ConfigFormat:
        """Автоматично визначити формат файлу"""
        if not self.auto_detect_format:
            return ConfigFormat.AUTO
            
        suffix = file_path.suffix.lower()
        if suffix in {'.yaml', '.yml'}:
            return ConfigFormat.YAML
        elif suffix == '.json':
            return ConfigFormat.JSON
        else:
            raise ConfigParseError(f"Непідтримуваний формат файлу: {suffix}")
    
    def load_file(self, file_path: Union[str, Path], 
                  format_type: ConfigFormat = ConfigFormat.AUTO) -> Dict[str, Any]:
        """Завантажити конфігурацію з файлу"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigParseError(f"Файл не знайдено: {file_path}")
        
        if format_type == ConfigFormat.AUTO:
            format_type = self.detect_format(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if format_type == ConfigFormat.YAML:
                data = yaml.safe_load(content)
            elif format_type == ConfigFormat.JSON:
                data = json.loads(content)
            else:
                raise ConfigParseError(f"Непідтримуваний формат: {format_type}")
            
            if not isinstance(data, dict):
                raise ConfigParseError("Конфігурація повинна бути словником (dict)")
            
            return data
            
        except yaml.YAMLError as e:
            raise ConfigParseError(f"Помилка парсингу YAML: {e}")
        except json.JSONDecodeError as e:
            raise ConfigParseError(f"Помилка парсингу JSON: {e}")
        except Exception as e:
            raise ConfigParseError(f"Неочікувана помилка при завантаженні файлу: {e}")
    
    def save_file(self, data: Dict[str, Any], file_path: Union[str, Path], 
                  format_type: ConfigFormat = ConfigFormat.AUTO) -> None:
        """Зберегти конфігурацію у файл"""
        file_path = Path(file_path)
        
        if format_type == ConfigFormat.AUTO:
            format_type = self.detect_format(file_path)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type == ConfigFormat.YAML:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif format_type == ConfigFormat.JSON:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    raise ConfigParseError(f"Непідтримуваний формат: {format_type}")
                    
        except Exception as e:
            raise ConfigParseError(f"Помилка збереження файлу: {e}")
    
    def validate_config(self, data: Dict[str, Any], schema: ConfigSchema) -> List[str]:
        """Валідувати конфігурацію згідно схеми"""
        errors = []
        
        for rule in schema.rules:
            try:
                self._validate_field(data, rule)
            except ConfigValidationError as e:
                errors.append(f"{rule.field_path}: {e}")
        
        return errors
    
    def _validate_field(self, data: Dict[str, Any], rule: ValidationRule) -> None:
        """Валідувати окреме поле"""
        field_value = self._get_nested_value(data, rule.field_path)
        
        # Перевірка обов'язковості
        if rule.required and field_value is None:
            raise ConfigValidationError(
                rule.error_message or f"Поле '{rule.field_path}' є обов'язковим",
                rule.field_path
            )
        
        if field_value is None:
            return  # Необов'язкове поле може бути None
        
        # Перевірка типу даних
        if rule.data_type and not isinstance(field_value, rule.data_type):
            raise ConfigValidationError(
                rule.error_message or f"Поле '{rule.field_path}' повинно бути типу {rule.data_type.__name__}",
                rule.field_path
            )
        
        # Перевірка числових значень
        if isinstance(field_value, (int, float)):
            if rule.min_value is not None and field_value < rule.min_value:
                raise ConfigValidationError(
                    rule.error_message or f"Поле '{rule.field_path}' повинно бути >= {rule.min_value}",
                    rule.field_path
                )
            if rule.max_value is not None and field_value > rule.max_value:
                raise ConfigValidationError(
                    rule.error_message or f"Поле '{rule.field_path}' повинно бути <= {rule.max_value}",
                    rule.field_path
                )
        
        # Перевірка дозволених значень
        if rule.allowed_values and field_value not in rule.allowed_values:
            raise ConfigValidationError(
                rule.error_message or f"Поле '{rule.field_path}' повинно бути одним з: {rule.allowed_values}",
                rule.field_path
            )
        
        # Кастомна валідація
        if rule.custom_validator and not rule.custom_validator(field_value):
            raise ConfigValidationError(
                rule.error_message or f"Поле '{rule.field_path}' не пройшло кастомну валідацію",
                rule.field_path
            )
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Отримати значення з вкладеної структури за шляхом (наприклад, 'shots.0.id')"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        
        return current
    
    def merge_configs(self, base_config: Dict[str, Any], 
                     override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Об'єднати дві конфігурації (override має пріоритет)"""
        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def convert_format(self, input_path: Union[str, Path], 
                      output_path: Union[str, Path]) -> None:
        """Конвертувати конфігурацію з одного формату в інший"""
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # Завантажити з вихідного формату
        input_format = self.detect_format(input_path)
        data = self.load_file(input_path, input_format)
        
        # Зберегти в цільовому форматі
        output_format = self.detect_format(output_path)
        self.save_file(data, output_path, output_format)
        
        LOG.info(f"Конфігурацію конвертовано з {input_format.value} в {output_format.value}")


# Попередньо визначені схеми для поширених типів конфігурацій
def create_pack_config_schema() -> ConfigSchema:
    """Створити схему для pack конфігурацій"""
    schema = ConfigSchema("pack_config", "1.0")
    
    schema.add_rule(ValidationRule("seed", required=True, data_type=int, min_value=0))
    schema.add_rule(ValidationRule("image_size", required=True, data_type=list))
    schema.add_rule(ValidationRule("shots", required=True, data_type=list))
    
    # Валідація shots
    schema.add_rule(ValidationRule("shots.*.id", required=True, data_type=str))
    schema.add_rule(ValidationRule("shots.*.palette", required=True))
    schema.add_rule(ValidationRule("shots.*.portal", required=True, data_type=dict))
    schema.add_rule(ValidationRule("shots.*.export", required=True, data_type=dict))
    
    return schema


def create_scene_config_schema() -> ConfigSchema:
    """Створити схему для scene конфігурацій"""
    schema = ConfigSchema("scene_config", "1.0")
    
    schema.add_rule(ValidationRule("scene", required=True, data_type=dict))
    schema.add_rule(ValidationRule("scene.name", required=True, data_type=str))
    schema.add_rule(ValidationRule("scene.size", required=True, data_type=list))
    
    # Валідація units
    schema.add_rule(ValidationRule("units", required=False, data_type=dict))
    schema.add_rule(ValidationRule("buildings", required=False, data_type=list))
    schema.add_rule(ValidationRule("effects", required=False, data_type=list))
    
    return schema


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення парсера
    parser = UniversalConfigParser()
    
    # Приклад завантаження та валідації
    try:
        # Завантажити конфігурацію
        config_data = parser.load_file("params/pack.yaml")
        print("Конфігурацію успішно завантажено")
        
        # Валідувати конфігурацію
        schema = create_pack_config_schema()
        errors = parser.validate_config(config_data, schema)
        
        if errors:
            print("Помилки валідації:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Конфігурація валідна")
            
    except Exception as e:
        print(f"Помилка: {e}")