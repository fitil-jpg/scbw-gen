"""
Система конфігурації освітлення для Blender
Підтримує YAML конфігурації, пресети та валідацію
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class LightType(Enum):
    """Типи лайтів"""
    SUN = "SUN"
    AREA = "AREA"
    SPOT = "SPOT"
    POINT = "POINT"


class HDRIType(Enum):
    """Типи HDRI"""
    IMAGE = "image"
    PROCEDURAL = "procedural"
    GRADIENT = "gradient"
    PRESET = "preset"


@dataclass
class LightConfig:
    """Конфігурація лайта"""
    name: str
    type: LightType
    position: List[float]
    rotation: Optional[List[float]] = None
    energy: float = 1.0
    color: List[float] = None
    size: Optional[float] = None
    shape: Optional[str] = None
    angle: Optional[float] = None
    spot_size: Optional[float] = None
    spot_blend: Optional[float] = None
    shadow_soft_size: Optional[float] = None
    shadow_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.color is None:
            self.color = [1.0, 1.0, 1.0]
        if self.rotation is None:
            self.rotation = [0.0, 0.0, 0.0]


@dataclass
class HDRIConfig:
    """Конфігурація HDRI"""
    type: HDRIType
    strength: float = 1.0
    image_path: Optional[str] = None
    rotation: Optional[List[float]] = None
    scale: Optional[List[float]] = None
    sky_type: Optional[str] = None
    sun_elevation: Optional[float] = None
    sun_rotation: Optional[float] = None
    sun_size: Optional[float] = None
    sun_intensity: Optional[float] = None
    turbidity: Optional[float] = None
    ground_albedo: Optional[float] = None
    gradient_type: Optional[str] = None
    colors: Optional[List[List[float]]] = None
    preset_name: Optional[str] = None
    
    def __post_init__(self):
        if self.rotation is None:
            self.rotation = [0.0, 0.0, 0.0]
        if self.scale is None:
            self.scale = [1.0, 1.0, 1.0]


@dataclass
class AtmosphericConfig:
    """Конфігурація атмосферних ефектів"""
    fog: Optional[Dict[str, Any]] = None
    atmospheric_perspective: Optional[Dict[str, Any]] = None
    volume_absorption: Optional[Dict[str, Any]] = None


@dataclass
class LightingConfig:
    """Повна конфігурація освітлення"""
    hdri: Optional[HDRIConfig] = None
    main_lights: List[LightConfig] = None
    additional_lights: List[LightConfig] = None
    atmospheric: Optional[AtmosphericConfig] = None
    animation: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.main_lights is None:
            self.main_lights = []
        if self.additional_lights is None:
            self.additional_lights = []


class LightingConfigManager:
    """Менеджер конфігурації освітлення"""
    
    def __init__(self, config_dir: str = "configs/lighting"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.presets = {}
        self._load_default_presets()
    
    def _load_default_presets(self) -> None:
        """Завантажує стандартні пресети"""
        self.presets = {
            "battle_sunset": {
                "hdri": {
                    "type": "preset",
                    "preset_name": "sunset",
                    "strength": 1.2
                },
                "main_lights": [
                    {
                        "name": "Battle_Sun",
                        "type": "SUN",
                        "position": [5, 5, 10],
                        "energy": 3.0,
                        "color": [1.0, 0.6, 0.3],
                        "rotation": [0.3, 0.3, -0.9]
                    }
                ],
                "additional_lights": [
                    {
                        "name": "Warm_Fill",
                        "type": "AREA",
                        "position": [-3, -3, 8],
                        "energy": 1.0,
                        "color": [1.0, 0.8, 0.6],
                        "size": 5.0
                    },
                    {
                        "name": "Rim_Light",
                        "type": "AREA",
                        "position": [0, 5, 4],
                        "energy": 2.0,
                        "color": [1.0, 0.9, 0.7],
                        "size": 3.0
                    }
                ],
                "atmospheric": {
                    "fog": {
                        "density": 0.05,
                        "anisotropy": 0.0
                    }
                }
            },
            "night_battle": {
                "hdri": {
                    "type": "preset",
                    "preset_name": "night",
                    "strength": 0.8
                },
                "main_lights": [
                    {
                        "name": "Moon_Light",
                        "type": "AREA",
                        "position": [0, 0, 15],
                        "energy": 2.0,
                        "color": [0.7, 0.8, 1.0],
                        "size": 10.0
                    }
                ],
                "additional_lights": [
                    {
                        "name": "Ambient_Light",
                        "type": "POINT",
                        "position": [0, 0, 5],
                        "energy": 0.5,
                        "color": [0.5, 0.6, 0.8]
                    },
                    {
                        "name": "Fire_Light",
                        "type": "POINT",
                        "position": [2, 2, 1],
                        "energy": 1.5,
                        "color": [1.0, 0.4, 0.1]
                    }
                ]
            },
            "studio_clean": {
                "hdri": {
                    "type": "preset",
                    "preset_name": "studio_white",
                    "strength": 1.0
                },
                "main_lights": [
                    {
                        "name": "Key_Light",
                        "type": "AREA",
                        "position": [5, -5, 8],
                        "energy": 5.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 3.0
                    }
                ],
                "additional_lights": [
                    {
                        "name": "Fill_Light",
                        "type": "AREA",
                        "position": [-3, -3, 6],
                        "energy": 2.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 5.0
                    },
                    {
                        "name": "Rim_Light",
                        "type": "AREA",
                        "position": [0, 5, 4],
                        "energy": 3.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 2.0
                    }
                ]
            },
            "dramatic": {
                "hdri": {
                    "type": "gradient",
                    "gradient_type": "SPHERICAL",
                    "colors": [[0.1, 0.1, 0.2], [0.3, 0.2, 0.4]],
                    "strength": 0.8
                },
                "main_lights": [
                    {
                        "name": "Dramatic_Key",
                        "type": "SPOT",
                        "position": [8, -8, 12],
                        "energy": 8.0,
                        "color": [1.0, 0.9, 0.7],
                        "rotation": [0.2, 0.2, -0.5],
                        "spot_size": 0.8,
                        "spot_blend": 0.3
                    }
                ],
                "additional_lights": [
                    {
                        "name": "Back_Light",
                        "type": "AREA",
                        "position": [-5, 5, 6],
                        "energy": 2.0,
                        "color": [0.8, 0.9, 1.0],
                        "size": 4.0
                    }
                ],
                "atmospheric": {
                    "fog": {
                        "density": 0.1,
                        "anisotropy": 0.2
                    }
                }
            }
        }
    
    def load_config(self, config_path: Union[str, Path]) -> LightingConfig:
        """
        Завантажує конфігурацію з файлу
        
        Args:
            config_path: Шлях до файлу конфігурації
        
        Returns:
            Конфігурація освітлення
        """
        try:
            config_path = Path(config_path)
            
            if not config_path.exists():
                raise FileNotFoundError(f"Файл конфігурації не знайдено: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    raise ValueError(f"Непідтримуваний формат файлу: {config_path.suffix}")
            
            # Валідація та конвертація
            lighting_config = self._convert_to_lighting_config(config_data)
            
            logger.info(f"Конфігурація завантажена: {config_path}")
            return lighting_config
            
        except Exception as e:
            logger.error(f"Помилка завантаження конфігурації: {e}")
            raise
    
    def save_config(self, config: LightingConfig, config_path: Union[str, Path], format: str = "yaml") -> None:
        """
        Зберігає конфігурацію у файл
        
        Args:
            config: Конфігурація освітлення
            config_path: Шлях до файлу
            format: Формат файлу (yaml або json)
        """
        try:
            config_path = Path(config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Конвертація в словник
            config_dict = self._convert_to_dict(config)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, indent=2)
                elif format.lower() == "json":
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Непідтримуваний формат: {format}")
            
            logger.info(f"Конфігурація збережена: {config_path}")
            
        except Exception as e:
            logger.error(f"Помилка збереження конфігурації: {e}")
            raise
    
    def _convert_to_lighting_config(self, data: Dict[str, Any]) -> LightingConfig:
        """Конвертує словник в LightingConfig"""
        config = LightingConfig()
        
        # HDRI конфігурація
        if "hdri" in data:
            hdri_data = data["hdri"]
            config.hdri = HDRIConfig(
                type=HDRIType(hdri_data.get("type", "procedural")),
                strength=hdri_data.get("strength", 1.0),
                image_path=hdri_data.get("image_path"),
                rotation=hdri_data.get("rotation"),
                scale=hdri_data.get("scale"),
                sky_type=hdri_data.get("sky_type"),
                sun_elevation=hdri_data.get("sun_elevation"),
                sun_rotation=hdri_data.get("sun_rotation"),
                sun_size=hdri_data.get("sun_size"),
                sun_intensity=hdri_data.get("sun_intensity"),
                turbidity=hdri_data.get("turbidity"),
                ground_albedo=hdri_data.get("ground_albedo"),
                gradient_type=hdri_data.get("gradient_type"),
                colors=hdri_data.get("colors"),
                preset_name=hdri_data.get("preset_name")
            )
        
        # Основні лайти
        if "main_lights" in data:
            config.main_lights = []
            for light_data in data["main_lights"]:
                light_config = LightConfig(
                    name=light_data["name"],
                    type=LightType(light_data["type"]),
                    position=light_data["position"],
                    rotation=light_data.get("rotation"),
                    energy=light_data.get("energy", 1.0),
                    color=light_data.get("color"),
                    size=light_data.get("size"),
                    shape=light_data.get("shape"),
                    angle=light_data.get("angle"),
                    spot_size=light_data.get("spot_size"),
                    spot_blend=light_data.get("spot_blend"),
                    shadow_soft_size=light_data.get("shadow_soft_size"),
                    shadow_config=light_data.get("shadow")
                )
                config.main_lights.append(light_config)
        
        # Додаткові лайти
        if "additional_lights" in data:
            config.additional_lights = []
            for light_data in data["additional_lights"]:
                light_config = LightConfig(
                    name=light_data["name"],
                    type=LightType(light_data["type"]),
                    position=light_data["position"],
                    rotation=light_data.get("rotation"),
                    energy=light_data.get("energy", 1.0),
                    color=light_data.get("color"),
                    size=light_data.get("size"),
                    shape=light_data.get("shape"),
                    angle=light_data.get("angle"),
                    spot_size=light_data.get("spot_size"),
                    spot_blend=light_data.get("spot_blend"),
                    shadow_soft_size=light_data.get("shadow_soft_size"),
                    shadow_config=light_data.get("shadow")
                )
                config.additional_lights.append(light_config)
        
        # Атмосферні ефекти
        if "atmospheric" in data:
            atmospheric_data = data["atmospheric"]
            config.atmospheric = AtmosphericConfig(
                fog=atmospheric_data.get("fog"),
                atmospheric_perspective=atmospheric_data.get("atmospheric_perspective"),
                volume_absorption=atmospheric_data.get("volume_absorption")
            )
        
        # Анімація
        if "animation" in data:
            config.animation = data["animation"]
        
        return config
    
    def _convert_to_dict(self, config: LightingConfig) -> Dict[str, Any]:
        """Конвертує LightingConfig в словник"""
        config_dict = {}
        
        # HDRI
        if config.hdri:
            hdri_dict = asdict(config.hdri)
            # Конвертація enum в строку
            hdri_dict["type"] = hdri_dict["type"].value if hasattr(hdri_dict["type"], 'value') else hdri_dict["type"]
            config_dict["hdri"] = hdri_dict
        
        # Основні лайти
        if config.main_lights:
            config_dict["main_lights"] = []
            for light in config.main_lights:
                light_dict = asdict(light)
                light_dict["type"] = light_dict["type"].value if hasattr(light_dict["type"], 'value') else light_dict["type"]
                config_dict["main_lights"].append(light_dict)
        
        # Додаткові лайти
        if config.additional_lights:
            config_dict["additional_lights"] = []
            for light in config.additional_lights:
                light_dict = asdict(light)
                light_dict["type"] = light_dict["type"].value if hasattr(light_dict["type"], 'value') else light_dict["type"]
                config_dict["additional_lights"].append(light_dict)
        
        # Атмосферні ефекти
        if config.atmospheric:
            config_dict["atmospheric"] = asdict(config.atmospheric)
        
        # Анімація
        if config.animation:
            config_dict["animation"] = config.animation
        
        return config_dict
    
    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Отримує пресет за назвою
        
        Args:
            preset_name: Назва пресету
        
        Returns:
            Конфігурація пресету
        """
        return self.presets.get(preset_name, {})
    
    def create_preset(self, name: str, config: LightingConfig) -> None:
        """
        Створює новий пресет
        
        Args:
            name: Назва пресету
            config: Конфігурація
        """
        self.presets[name] = self._convert_to_dict(config)
        logger.info(f"Пресет створено: {name}")
    
    def save_presets(self, filepath: Union[str, Path]) -> None:
        """
        Зберігає всі пресети у файл
        
        Args:
            filepath: Шлях до файлу
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(self.presets, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Пресети збережено: {filepath}")
            
        except Exception as e:
            logger.error(f"Помилка збереження пресетів: {e}")
            raise
    
    def load_presets(self, filepath: Union[str, Path]) -> None:
        """
        Завантажує пресети з файлу
        
        Args:
            filepath: Шлях до файлу
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.warning(f"Файл пресетів не знайдено: {filepath}")
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                presets_data = yaml.safe_load(f)
            
            if presets_data:
                self.presets.update(presets_data)
            
            logger.info(f"Пресети завантажено: {filepath}")
            
        except Exception as e:
            logger.error(f"Помилка завантаження пресетів: {e}")
            raise
    
    def validate_config(self, config: LightingConfig) -> List[str]:
        """
        Валідує конфігурацію
        
        Args:
            config: Конфігурація для валідації
        
        Returns:
            Список помилок валідації
        """
        errors = []
        
        # Валідація HDRI
        if config.hdri:
            if config.hdri.type == HDRIType.IMAGE and not config.hdri.image_path:
                errors.append("HDRI зображення не вказано для типу 'image'")
            
            if config.hdri.type == HDRIType.PRESET and not config.hdri.preset_name:
                errors.append("Назва пресету не вказана для типу 'preset'")
        
        # Валідація лайтів
        all_lights = config.main_lights + config.additional_lights
        light_names = [light.name for light in all_lights]
        
        if len(light_names) != len(set(light_names)):
            errors.append("Дублювання назв лайтів")
        
        for light in all_lights:
            if not light.name:
                errors.append("Назва лайта не може бути порожньою")
            
            if len(light.position) != 3:
                errors.append(f"Позиція лайта '{light.name}' повинна мати 3 координати")
            
            if light.color and len(light.color) != 3:
                errors.append(f"Колір лайта '{light.name}' повинен мати 3 компоненти")
        
        return errors
    
    def create_battle_lighting_config(self, battle_type: str = "sunset") -> LightingConfig:
        """
        Створює конфігурацію освітлення для бойової сцени
        
        Args:
            battle_type: Тип битви (sunset, night, dawn, etc.)
        
        Returns:
            Конфігурація освітлення
        """
        preset_data = self.get_preset(f"battle_{battle_type}")
        if not preset_data:
            # Використання стандартної конфігурації
            preset_data = self.get_preset("battle_sunset")
        
        return self._convert_to_lighting_config(preset_data)
    
    def create_studio_lighting_config(self, studio_type: str = "clean") -> LightingConfig:
        """
        Створює конфігурацію освітлення для студії
        
        Args:
            studio_type: Тип студії (clean, warm, cool, etc.)
        
        Returns:
            Конфігурація освітлення
        """
        preset_data = self.get_preset(f"studio_{studio_type}")
        if not preset_data:
            # Використання стандартної конфігурації
            preset_data = self.get_preset("studio_clean")
        
        return self._convert_to_lighting_config(preset_data)
    
    def get_available_presets(self) -> List[str]:
        """Повертає список доступних пресетів освітлення"""
        return list(self.presets.keys())


# Приклад використання
if __name__ == "__main__":
    # Ініціалізація менеджера конфігурації
    config_manager = LightingConfigManager("configs/lighting")
    
    # Створення конфігурації для бойової сцени
    battle_config = config_manager.create_battle_lighting_config("sunset")
    
    # Збереження конфігурації
    config_manager.save_config(battle_config, "configs/lighting/battle_sunset.yaml")
    
    # Завантаження конфігурації
    loaded_config = config_manager.load_config("configs/lighting/battle_sunset.yaml")
    
    # Валідація конфігурації
    errors = config_manager.validate_config(loaded_config)
    if errors:
        print("Помилки валідації:", errors)
    else:
        print("Конфігурація валідна!")
    
    print("Система конфігурації освітлення готова!")