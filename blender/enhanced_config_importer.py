"""
Покращений імпортер конфігурації для Blender
Підтримує YAML та JSON конфігурації з валідацією
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedConfigImporter:
    """Покращений імпортер конфігурації для Blender"""
    
    def __init__(self, config_dir: Union[str, Path] = "assets"):
        self.config_dir = Path(config_dir)
        self.loaded_configs = {}
        self.validation_schema = self._create_validation_schema()
    
    def _create_validation_schema(self) -> Dict[str, Any]:
        """Створює схему валідації для конфігурацій"""
        return {
            "buildings": {
                "required_fields": ["name", "type", "position", "scale"],
                # Дозволяємо імпорт 3D-моделей та інстансинг
                "optional_fields": [
                    "rotation",
                    "materials",
                    "animations",
                    "collision",
                    "model_path",   # шлях до GLTF/GLB/FBX/OBJ
                    "use_instance", # чи створювати інстанси (Collection Instance)
                    "make_real",    # конвертувати інстанс у реальні об'єкти
                    "instances"     # масив додаткових інстансів {position, rotation, scale}
                ]
            },
            "units": {
                "required_fields": ["name", "type", "position"],
                # Дозволяємо імпорт 3D-моделей та інстансинг
                "optional_fields": [
                    "scale",
                    "rotation",
                    "materials",
                    "animations",
                    "health",
                    "armor",
                    "model_path",
                    "use_instance",
                    "make_real",
                    "instances"
                ]
            },
            "terrain": {
                "required_fields": ["type", "heightmap"],
                "optional_fields": ["textures", "materials", "collision", "lighting"]
            },
            "effects": {
                "required_fields": ["name", "type", "position"],
                "optional_fields": ["scale", "duration", "intensity", "particles"]
            }
        }
    
    def load_config(self, config_type: str, config_name: str = None) -> Dict[str, Any]:
        """
        Завантажує конфігурацію з файлу
        
        Args:
            config_type: Тип конфігурації (buildings, units, terrain, effects)
            config_name: Ім'я конкретного конфігураційного файлу (опціонально)
        
        Returns:
            Словник з конфігурацією
        """
        try:
            if config_name:
                config_path = self.config_dir / config_type / f"{config_name}.yaml"
            else:
                config_path = self.config_dir / config_type / f"{config_type}_config.yaml"
            
            if not config_path.exists():
                # Спробуємо JSON якщо YAML не знайдено
                json_path = config_path.with_suffix('.json')
                if json_path.exists():
                    config_path = json_path
                else:
                    raise FileNotFoundError(f"Конфігурація не знайдена: {config_path}")
            
            # Завантаження конфігурації
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix == '.yaml':
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            # Валідація конфігурації
            self._validate_config(config, config_type)
            
            # Збереження в кеші
            cache_key = f"{config_type}_{config_name}" if config_name else config_type
            self.loaded_configs[cache_key] = config
            
            logger.info(f"Конфігурація завантажена: {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Помилка завантаження конфігурації {config_type}: {e}")
            raise
    
    def _validate_config(self, config: Dict[str, Any], config_type: str) -> None:
        """Валідує конфігурацію відповідно до схеми"""
        if config_type not in self.validation_schema:
            logger.warning(f"Невідомий тип конфігурації: {config_type}")
            return
        
        schema = self.validation_schema[config_type]
        
        # Перевірка основних полів
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._validate_item(item, schema)
    
    def _validate_item(self, item: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Валідує окремий елемент конфігурації"""
        required_fields = schema.get("required_fields", [])
        optional_fields = schema.get("optional_fields", [])
        
        # Перевірка обов'язкових полів
        for field in required_fields:
            if field not in item:
                logger.warning(f"Відсутнє обов'язкове поле: {field}")
        
        # Перевірка невідомих полів
        all_fields = set(required_fields + optional_fields)
        for field in item.keys():
            if field not in all_fields:
                logger.warning(f"Невідоме поле: {field}")
    
    def get_shot_config(self, shot_id: str) -> Dict[str, Any]:
        """
        Отримує конфігурацію для конкретного шоту
        
        Args:
            shot_id: Ідентифікатор шоту
        
        Returns:
            Конфігурація шоту
        """
        try:
            # Завантаження основних конфігурацій
            buildings_config = self.load_config("buildings")
            units_config = self.load_config("units")
            terrain_config = self.load_config("terrain")
            effects_config = self.load_config("effects")
            
            # Створення конфігурації шоту
            shot_config = {
                "shot_id": shot_id,
                "buildings": buildings_config.get("buildings", []),
                "units": units_config.get("units", []),
                "terrain": terrain_config,
                "effects": effects_config.get("effects", []),
                "camera": self._get_camera_config(shot_id),
                "lighting": self._get_lighting_config(shot_id),
                "render_settings": self._get_render_settings(shot_id)
            }
            
            return shot_config
            
        except Exception as e:
            logger.error(f"Помилка створення конфігурації шоту {shot_id}: {e}")
            raise
    
    def _get_camera_config(self, shot_id: str) -> Dict[str, Any]:
        """Отримує конфігурацію камери для шоту"""
        return {
            "position": [0, -10, 5],
            "rotation": [60, 0, 0],
            "focal_length": 50,
            "sensor_size": 36,
            "type": "PERSP"
        }
    
    def _get_lighting_config(self, shot_id: str) -> Dict[str, Any]:
        """Отримує конфігурацію освітлення для шоту"""
        return {
            # Новий формат: world HDRI та список лайтів
            "world_hdri": {
                # Вкажіть шлях до HDRI (EXR/HDR). Якщо None або відсутній — буде використано world_background
                "path": None,
                "strength": 1.0,
                # Обертання у градусах XYZ
                "rotation": [0.0, 0.0, 0.0]
            },
            "world_background": {
                # Бекграунд колір як fallback (RGBA або RGB)
                "color": [0.1, 0.15, 0.2, 1.0],
                "strength": 0.3
            },
            # Пресет базового освітлення може бути: "three_point" або None
            "preset": "three_point",
            "preset_settings": {},
            # Явні лайт-джерела (можна доповнити або перекрити пресет)
            "lights": [
                {"type": "SUN", "name": "Sun", "position": [10, 10, 15], "energy": 3.0, "color": [1.0, 0.95, 0.8]},
                {"type": "AREA", "name": "Fill", "position": [-5, -5, 8], "energy": 300.0, "size": 4.0, "color": [0.9, 0.95, 1.0]},
                {"type": "AREA", "name": "Rim", "position": [0, 8, 5], "energy": 500.0, "size": 2.0, "color": [1.0, 0.95, 0.9]}
            ],
            # Зворотна сумісність зі старими ключами (опціонально)
            "sun_light": {
                "position": [10, 10, 10],
                "energy": 3.0,
                "color": [1.0, 0.95, 0.8]
            },
            "ambient_light": {
                "position": [0, 0, 5],
                "energy": 0.3,
                "size": 10.0,
                "color": [0.5, 0.7, 1.0]
            },
            # Поведінка очищення
            "clear_lights": True
        }
    
    def _get_render_settings(self, shot_id: str) -> Dict[str, Any]:
        """Отримує налаштування рендерингу для шоту"""
        return {
            "engine": "CYCLES",  # або "BLENDER_EEVEE"
            "samples": 128,
            "resolution": [1920, 1080],
            "output_format": "PNG",
            "color_management": "Filmic",
            "denoising": True
        }
    
    def save_config(self, config: Dict[str, Any], config_type: str, config_name: str = None) -> None:
        """
        Зберігає конфігурацію у файл
        
        Args:
            config: Конфігурація для збереження
            config_type: Тип конфігурації
            config_name: Ім'я файлу (опціонально)
        """
        try:
            if config_name:
                config_path = self.config_dir / config_type / f"{config_name}.yaml"
            else:
                config_path = self.config_dir / config_type / f"{config_type}_config.yaml"
            
            # Створення директорії якщо не існує
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Збереження у YAML форматі
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Конфігурація збережена: {config_path}")
            
        except Exception as e:
            logger.error(f"Помилка збереження конфігурації: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Очищає кеш завантажених конфігурацій"""
        self.loaded_configs.clear()
        logger.info("Кеш конфігурацій очищено")
    
    def list_available_configs(self) -> Dict[str, List[str]]:
        """Повертає список доступних конфігурацій"""
        configs = {}
        
        for config_type in ["buildings", "units", "terrain", "effects"]:
            config_dir = self.config_dir / config_type
            if config_dir.exists():
                configs[config_type] = [
                    f.stem for f in config_dir.glob("*.yaml") + config_dir.glob("*.json")
                ]
        
        return configs

# Приклад використання
if __name__ == "__main__":
    # Ініціалізація імпортера
    importer = EnhancedConfigImporter("assets")
    
    # Завантаження конфігурації
    try:
        shot_config = importer.get_shot_config("test_shot")
        print("Конфігурація шоту завантажена успішно")
        print(f"Кількість будівель: {len(shot_config['buildings'])}")
        print(f"Кількість юнітів: {len(shot_config['units'])}")
    except Exception as e:
        print(f"Помилка: {e}")
