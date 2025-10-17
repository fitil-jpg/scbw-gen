#!/usr/bin/env python3
"""
Enhanced Scene Composition Algorithms for StarCraft Maps
Розширені алгоритми композиції сцен для карт StarCraft

This module provides sophisticated scene composition algorithms including:
- Rule-based camera positioning
- Dynamic lighting setup
- Atmospheric effects
- Compositional balance
"""

import math
import random
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class CameraType(Enum):
    """Типи камер"""
    OVERVIEW = "overview"
    TACTICAL = "tactical"
    CINEMATIC = "cinematic"
    FOLLOW = "follow"
    ORBIT = "orbit"


class LightingType(Enum):
    """Типи освітлення"""
    SUNLIGHT = "sunlight"
    MOONLIGHT = "moonlight"
    BATTLE = "battle"
    DRAMATIC = "dramatic"
    AMBIENT = "ambient"


class WeatherType(Enum):
    """Типи погоди"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    FOGGY = "foggy"
    STORMY = "stormy"


@dataclass
class CameraConfig:
    """Конфігурація камери"""
    position: Tuple[float, float, float]
    target: Tuple[float, float, float]
    fov: float
    near_clip: float = 0.1
    far_clip: float = 1000.0
    camera_type: CameraType = CameraType.OVERVIEW


@dataclass
class LightingConfig:
    """Конфігурація освітлення"""
    sun_direction: Tuple[float, float, float]
    sun_intensity: float
    ambient_intensity: float
    sun_color: Tuple[float, float, float] = (1.0, 0.95, 0.8)
    ambient_color: Tuple[float, float, float] = (0.3, 0.3, 0.4)


@dataclass
class AtmosphericConfig:
    """Конфігурація атмосфери"""
    fog_density: float
    fog_color: Tuple[float, float, float]
    wind_direction: Tuple[float, float]
    wind_strength: float
    weather_type: WeatherType = WeatherType.CLEAR


class CompositionAnalyzer:
    """Аналізатор композиції сцени"""
    
    def __init__(self, scene_width: float, scene_height: float):
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.important_objects = []
        self.action_areas = []
        self.visual_weights = {}
    
    def add_important_object(self, 
                           position: Tuple[float, float], 
                           importance: float = 1.0,
                           object_type: str = "unit"):
        """Додати важливий об'єкт"""
        self.important_objects.append({
            'position': position,
            'importance': importance,
            'type': object_type
        })
    
    def add_action_area(self, 
                       center: Tuple[float, float], 
                       radius: float,
                       intensity: float = 1.0):
        """Додати зону дії"""
        self.action_areas.append({
            'center': center,
            'radius': radius,
            'intensity': intensity
        })
    
    def calculate_visual_center(self) -> Tuple[float, float]:
        """Обчислити візуальний центр сцени"""
        if not self.important_objects:
            return (self.scene_width / 2, self.scene_height / 2)
        
        total_weight = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        
        for obj in self.important_objects:
            weight = obj['importance']
            total_weight += weight
            weighted_x += obj['position'][0] * weight
            weighted_y += obj['position'][1] * weight
        
        if total_weight > 0:
            return (weighted_x / total_weight, weighted_y / total_weight)
        else:
            return (self.scene_width / 2, self.scene_height / 2)
    
    def calculate_action_center(self) -> Tuple[float, float]:
        """Обчислити центр дії"""
        if not self.action_areas:
            return self.calculate_visual_center()
        
        total_intensity = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        
        for area in self.action_areas:
            intensity = area['intensity']
            total_intensity += intensity
            weighted_x += area['center'][0] * intensity
            weighted_y += area['center'][1] * intensity
        
        if total_intensity > 0:
            return (weighted_x / total_intensity, weighted_y / total_intensity)
        else:
            return self.calculate_visual_center()
    
    def get_rule_of_thirds_points(self) -> List[Tuple[float, float]]:
        """Отримати точки правила третин"""
        points = []
        
        # Вертикальні лінії
        x1 = self.scene_width / 3
        x2 = 2 * self.scene_width / 3
        
        # Горизонтальні лінії
        y1 = self.scene_height / 3
        y2 = 2 * self.scene_height / 3
        
        # Точки перетину
        points.extend([
            (x1, y1), (x2, y1),
            (x1, y2), (x2, y2)
        ])
        
        return points
    
    def find_best_camera_positions(self, 
                                 camera_type: CameraType,
                                 count: int = 5) -> List[Tuple[float, float, float]]:
        """Знайти найкращі позиції камери"""
        positions = []
        
        if camera_type == CameraType.OVERVIEW:
            positions = self._find_overview_positions(count)
        elif camera_type == CameraType.TACTICAL:
            positions = self._find_tactical_positions(count)
        elif camera_type == CameraType.CINEMATIC:
            positions = self._find_cinematic_positions(count)
        elif camera_type == CameraType.FOLLOW:
            positions = self._find_follow_positions(count)
        elif camera_type == CameraType.ORBIT:
            positions = self._find_orbit_positions(count)
        
        return positions
    
    def _find_overview_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """Знайти позиції для оглядової камери"""
        positions = []
        center = self.calculate_visual_center()
        
        # Висота для огляду
        height = max(self.scene_width, self.scene_height) * 0.8
        
        # Розмістити камери навколо центру
        for i in range(count):
            angle = (2 * math.pi * i) / count
            distance = max(self.scene_width, self.scene_height) * 0.6
            
            x = center[0] + distance * math.cos(angle)
            y = center[1] + distance * math.sin(angle)
            z = height
            
            positions.append((x, y, z))
        
        return positions
    
    def _find_tactical_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """Знайти позиції для тактичної камери"""
        positions = []
        action_center = self.calculate_action_center()
        
        # Нижча висота для тактичного огляду
        height = max(self.scene_width, self.scene_height) * 0.4
        
        # Розмістити камери ближче до дії
        for i in range(count):
            angle = (2 * math.pi * i) / count
            distance = max(self.scene_width, self.scene_height) * 0.3
            
            x = action_center[0] + distance * math.cos(angle)
            y = action_center[1] + distance * math.sin(angle)
            z = height
            
            positions.append((x, y, z))
        
        return positions
    
    def _find_cinematic_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """Знайти позиції для кінематографічної камери"""
        positions = []
        
        # Використати правило третин
        rule_of_thirds = self.get_rule_of_thirds_points()
        
        for point in rule_of_thirds[:count]:
            # Розмістити камеру на висоті з кутом огляду
            height = max(self.scene_width, self.scene_height) * 0.6
            x = point[0]
            y = point[1] - 20  # Трохи відступити
            z = height
            
            positions.append((x, y, z))
        
        return positions
    
    def _find_follow_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """Знайти позиції для камери слідування"""
        positions = []
        
        # Слідувати за найважливішими об'єктами
        sorted_objects = sorted(self.important_objects, 
                              key=lambda x: x['importance'], reverse=True)
        
        for i, obj in enumerate(sorted_objects[:count]):
            pos = obj['position']
            x = pos[0] + random.uniform(-5, 5)
            y = pos[1] + random.uniform(-5, 5)
            z = 10 + random.uniform(-2, 2)
            
            positions.append((x, y, z))
        
        return positions
    
    def _find_orbit_positions(self, count: int) -> List[Tuple[float, float, float]]:
        """Знайти позиції для орбітальної камери"""
        positions = []
        center = self.calculate_visual_center()
        
        # Орбітальні позиції навколо центру
        radius = max(self.scene_width, self.scene_height) * 0.5
        height = max(self.scene_width, self.scene_height) * 0.3
        
        for i in range(count):
            angle = (2 * math.pi * i) / count
            elevation = random.uniform(0.2, 0.8)  # Випадкова висота
            
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            z = height * elevation
            
            positions.append((x, y, z))
        
        return positions


class LightingDesigner:
    """Дизайнер освітлення"""
    
    def __init__(self, scene_width: float, scene_height: float):
        self.scene_width = scene_width
        self.scene_height = scene_height
    
    def design_lighting(self, 
                       scene_type: str,
                       time_of_day: str = "day",
                       weather: WeatherType = WeatherType.CLEAR) -> LightingConfig:
        """Спроектувати освітлення для сцени"""
        
        if scene_type == "battle":
            return self._design_battle_lighting(time_of_day, weather)
        elif scene_type == "peaceful":
            return self._design_peaceful_lighting(time_of_day, weather)
        elif scene_type == "dramatic":
            return self._design_dramatic_lighting(time_of_day, weather)
        elif scene_type == "mysterious":
            return self._design_mysterious_lighting(time_of_day, weather)
        else:
            return self._design_default_lighting(time_of_day, weather)
    
    def _design_battle_lighting(self, 
                               time_of_day: str, 
                               weather: WeatherType) -> LightingConfig:
        """Спроектувати освітлення для битви"""
        
        if time_of_day == "dawn":
            sun_direction = (0.7, 0.3, 0.5)
            sun_intensity = 0.8
            sun_color = (1.0, 0.6, 0.3)
            ambient_intensity = 0.4
        elif time_of_day == "dusk":
            sun_direction = (-0.7, 0.3, 0.5)
            sun_intensity = 0.6
            sun_color = (1.0, 0.4, 0.2)
            ambient_intensity = 0.3
        elif time_of_day == "night":
            sun_direction = (0.0, 0.0, 1.0)  # Місяць
            sun_intensity = 0.3
            sun_color = (0.7, 0.8, 1.0)
            ambient_intensity = 0.2
        else:  # day
            sun_direction = (0.3, 0.7, 0.5)
            sun_intensity = 1.2
            sun_color = (1.0, 0.95, 0.8)
            ambient_intensity = 0.5
        
        # Модифікувати залежно від погоди
        if weather == WeatherType.CLOUDY:
            sun_intensity *= 0.7
            ambient_intensity *= 0.8
        elif weather == WeatherType.RAINY:
            sun_intensity *= 0.5
            ambient_intensity *= 0.6
        elif weather == WeatherType.FOGGY:
            sun_intensity *= 0.4
            ambient_intensity *= 0.9
        elif weather == WeatherType.STORMY:
            sun_intensity *= 0.3
            ambient_intensity *= 0.4
        
        return LightingConfig(
            sun_direction=sun_direction,
            sun_intensity=sun_intensity,
            ambient_intensity=ambient_intensity,
            sun_color=sun_color,
            ambient_color=(0.2, 0.2, 0.3)
        )
    
    def _design_peaceful_lighting(self, 
                                 time_of_day: str, 
                                 weather: WeatherType) -> LightingConfig:
        """Спроектувати мирне освітлення"""
        
        if time_of_day == "dawn":
            sun_direction = (0.5, 0.5, 0.5)
            sun_intensity = 0.6
            sun_color = (1.0, 0.8, 0.6)
            ambient_intensity = 0.6
        elif time_of_day == "dusk":
            sun_direction = (-0.5, 0.5, 0.5)
            sun_intensity = 0.5
            sun_color = (1.0, 0.7, 0.5)
            ambient_intensity = 0.5
        else:  # day
            sun_direction = (0.2, 0.8, 0.4)
            sun_intensity = 1.0
            sun_color = (1.0, 1.0, 0.9)
            ambient_intensity = 0.7
        
        return LightingConfig(
            sun_direction=sun_direction,
            sun_intensity=sun_intensity,
            ambient_intensity=ambient_intensity,
            sun_color=sun_color,
            ambient_color=(0.4, 0.4, 0.5)
        )
    
    def _design_dramatic_lighting(self, 
                                 time_of_day: str, 
                                 weather: WeatherType) -> LightingConfig:
        """Спроектувати драматичне освітлення"""
        
        # Резкі контрасти та темні тіні
        sun_direction = (0.8, 0.2, 0.3)
        sun_intensity = 1.5
        sun_color = (1.0, 0.9, 0.7)
        ambient_intensity = 0.2
        ambient_color = (0.1, 0.1, 0.2)
        
        return LightingConfig(
            sun_direction=sun_direction,
            sun_intensity=sun_intensity,
            ambient_intensity=ambient_intensity,
            sun_color=sun_color,
            ambient_color=ambient_color
        )
    
    def _design_mysterious_lighting(self, 
                                   time_of_day: str, 
                                   weather: WeatherType) -> LightingConfig:
        """Спроектувати містичне освітлення"""
        
        # М'яке, розсіяне освітлення
        sun_direction = (0.3, 0.3, 0.7)
        sun_intensity = 0.4
        sun_color = (0.8, 0.9, 1.0)
        ambient_intensity = 0.6
        ambient_color = (0.3, 0.3, 0.5)
        
        return LightingConfig(
            sun_direction=sun_direction,
            sun_intensity=sun_intensity,
            ambient_intensity=ambient_intensity,
            sun_color=sun_color,
            ambient_color=ambient_color
        )
    
    def _design_default_lighting(self, 
                                time_of_day: str, 
                                weather: WeatherType) -> LightingConfig:
        """Спроектувати стандартне освітлення"""
        
        sun_direction = (0.3, 0.7, 0.5)
        sun_intensity = 1.0
        sun_color = (1.0, 0.95, 0.8)
        ambient_intensity = 0.4
        ambient_color = (0.3, 0.3, 0.4)
        
        return LightingConfig(
            sun_direction=sun_direction,
            sun_intensity=sun_intensity,
            ambient_intensity=ambient_intensity,
            sun_color=sun_color,
            ambient_color=ambient_color
        )


class AtmosphericDesigner:
    """Дизайнер атмосфери"""
    
    def __init__(self, scene_width: float, scene_height: float):
        self.scene_width = scene_width
        self.scene_height = scene_height
    
    def design_atmosphere(self, 
                         scene_type: str,
                         weather: WeatherType = WeatherType.CLEAR,
                         intensity: float = 1.0) -> AtmosphericConfig:
        """Спроектувати атмосферу для сцени"""
        
        if weather == WeatherType.CLEAR:
            return self._design_clear_atmosphere(scene_type, intensity)
        elif weather == WeatherType.CLOUDY:
            return self._design_cloudy_atmosphere(scene_type, intensity)
        elif weather == WeatherType.RAINY:
            return self._design_rainy_atmosphere(scene_type, intensity)
        elif weather == WeatherType.FOGGY:
            return self._design_foggy_atmosphere(scene_type, intensity)
        elif weather == WeatherType.STORMY:
            return self._design_stormy_atmosphere(scene_type, intensity)
        else:
            return self._design_default_atmosphere(scene_type, intensity)
    
    def _design_clear_atmosphere(self, 
                                scene_type: str, 
                                intensity: float) -> AtmosphericConfig:
        """Спроектувати ясну атмосферу"""
        
        fog_density = 0.01 * intensity
        fog_color = (0.8, 0.9, 1.0)
        wind_direction = (0.1, 0.1)
        wind_strength = 0.2 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.CLEAR
        )
    
    def _design_cloudy_atmosphere(self, 
                                 scene_type: str, 
                                 intensity: float) -> AtmosphericConfig:
        """Спроектувати хмарну атмосферу"""
        
        fog_density = 0.05 * intensity
        fog_color = (0.6, 0.7, 0.8)
        wind_direction = (0.3, 0.2)
        wind_strength = 0.4 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.CLOUDY
        )
    
    def _design_rainy_atmosphere(self, 
                                scene_type: str, 
                                intensity: float) -> AtmosphericConfig:
        """Спроектувати дощову атмосферу"""
        
        fog_density = 0.1 * intensity
        fog_color = (0.4, 0.5, 0.6)
        wind_direction = (0.5, 0.3)
        wind_strength = 0.8 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.RAINY
        )
    
    def _design_foggy_atmosphere(self, 
                                scene_type: str, 
                                intensity: float) -> AtmosphericConfig:
        """Спроектувати туманну атмосферу"""
        
        fog_density = 0.3 * intensity
        fog_color = (0.7, 0.7, 0.8)
        wind_direction = (0.1, 0.1)
        wind_strength = 0.1 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.FOGGY
        )
    
    def _design_stormy_atmosphere(self, 
                                 scene_type: str, 
                                 intensity: float) -> AtmosphericConfig:
        """Спроектувати штормову атмосферу"""
        
        fog_density = 0.2 * intensity
        fog_color = (0.3, 0.3, 0.4)
        wind_direction = (0.8, 0.6)
        wind_strength = 1.2 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.STORMY
        )
    
    def _design_default_atmosphere(self, 
                                  scene_type: str, 
                                  intensity: float) -> AtmosphericConfig:
        """Спроектувати стандартну атмосферу"""
        
        fog_density = 0.02 * intensity
        fog_color = (0.8, 0.8, 0.9)
        wind_direction = (0.2, 0.2)
        wind_strength = 0.3 * intensity
        
        return AtmosphericConfig(
            fog_density=fog_density,
            fog_color=fog_color,
            wind_direction=wind_direction,
            wind_strength=wind_strength,
            weather_type=WeatherType.CLEAR
        )


class SceneComposer:
    """Композитор сцен"""
    
    def __init__(self, scene_width: float, scene_height: float):
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.composition_analyzer = CompositionAnalyzer(scene_width, scene_height)
        self.lighting_designer = LightingDesigner(scene_width, scene_height)
        self.atmospheric_designer = AtmosphericDesigner(scene_width, scene_height)
    
    def compose_scene(self, 
                     scene_type: str,
                     important_objects: List[Dict[str, Any]],
                     action_areas: List[Dict[str, Any]],
                     time_of_day: str = "day",
                     weather: WeatherType = WeatherType.CLEAR) -> Dict[str, Any]:
        """Скомпонувати повну сцену"""
        
        # Додати важливі об'єкти та зони дії
        for obj in important_objects:
            self.composition_analyzer.add_important_object(
                obj['position'], obj.get('importance', 1.0), obj.get('type', 'unit')
            )
        
        for area in action_areas:
            self.composition_analyzer.add_action_area(
                area['center'], area['radius'], area.get('intensity', 1.0)
            )
        
        # Визначити тип камери на основі сцени
        camera_type = self._determine_camera_type(scene_type)
        
        # Знайти позиції камери
        camera_positions = self.composition_analyzer.find_best_camera_positions(
            camera_type, count=3
        )
        
        # Вибрати найкращу позицію камери
        best_camera_pos = self._select_best_camera_position(
            camera_positions, scene_type
        )
        
        # Спроектувати освітлення
        lighting_config = self.lighting_designer.design_lighting(
            scene_type, time_of_day, weather
        )
        
        # Спроектувати атмосферу
        atmospheric_config = self.atmospheric_designer.design_atmosphere(
            scene_type, weather
        )
        
        # Створити конфігурацію камери
        camera_config = self._create_camera_config(
            best_camera_pos, camera_type
        )
        
        return {
            'camera': camera_config,
            'lighting': lighting_config,
            'atmosphere': atmospheric_config,
            'scene_type': scene_type,
            'time_of_day': time_of_day,
            'weather': weather.value
        }
    
    def _determine_camera_type(self, scene_type: str) -> CameraType:
        """Визначити тип камери на основі типу сцени"""
        
        if scene_type == "battle":
            return CameraType.TACTICAL
        elif scene_type == "cinematic":
            return CameraType.CINEMATIC
        elif scene_type == "overview":
            return CameraType.OVERVIEW
        elif scene_type == "follow":
            return CameraType.FOLLOW
        else:
            return CameraType.OVERVIEW
    
    def _select_best_camera_position(self, 
                                   positions: List[Tuple[float, float, float]],
                                   scene_type: str) -> Tuple[float, float, float]:
        """Вибрати найкращу позицію камери"""
        
        if not positions:
            # Стандартна позиція
            return (self.scene_width / 2, self.scene_height / 2, 50.0)
        
        # Простий вибір - перша позиція
        # В реальності можна додати більш складну логіку
        return positions[0]
    
    def _create_camera_config(self, 
                            position: Tuple[float, float, float],
                            camera_type: CameraType) -> CameraConfig:
        """Створити конфігурацію камери"""
        
        # Обчислити ціль камери
        target = self.composition_analyzer.calculate_visual_center()
        target = (target[0], target[1], 0.0)  # Додати z-координату
        
        # Визначити FOV залежно від типу камери
        fov_map = {
            CameraType.OVERVIEW: 60.0,
            CameraType.TACTICAL: 45.0,
            CameraType.CINEMATIC: 35.0,
            CameraType.FOLLOW: 50.0,
            CameraType.ORBIT: 40.0
        }
        
        fov = fov_map.get(camera_type, 50.0)
        
        return CameraConfig(
            position=position,
            target=target,
            fov=fov,
            camera_type=camera_type
        )


def create_sample_scene_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Створити зразкові дані сцени"""
    
    # Важливі об'єкти
    important_objects = [
        {'position': (30, 30), 'importance': 2.0, 'type': 'hero'},
        {'position': (70, 70), 'importance': 1.5, 'type': 'enemy_commander'},
        {'position': (50, 50), 'importance': 1.0, 'type': 'battle_center'},
        {'position': (20, 80), 'importance': 0.8, 'type': 'resource'},
        {'position': (80, 20), 'importance': 0.8, 'type': 'resource'}
    ]
    
    # Зони дії
    action_areas = [
        {'center': (40, 40), 'radius': 15.0, 'intensity': 2.0},
        {'center': (60, 60), 'radius': 12.0, 'intensity': 1.5},
        {'center': (25, 75), 'radius': 8.0, 'intensity': 1.0}
    ]
    
    return important_objects, action_areas


if __name__ == "__main__":
    # Приклад використання
    print("Тестування алгоритмів композиції сцен...")
    
    # Створити композитор
    composer = SceneComposer(100.0, 100.0)
    
    # Створити зразкові дані
    important_objects, action_areas = create_sample_scene_data()
    
    # Скомпонувати різні типи сцен
    scene_types = ["battle", "peaceful", "dramatic", "cinematic"]
    weather_types = [WeatherType.CLEAR, WeatherType.CLOUDY, WeatherType.RAINY]
    
    for scene_type in scene_types:
        print(f"\n{scene_type.upper()} сцена:")
        
        for weather in weather_types:
            scene_config = composer.compose_scene(
                scene_type=scene_type,
                important_objects=important_objects,
                action_areas=action_areas,
                time_of_day="day",
                weather=weather
            )
            
            print(f"  {weather.value}: Камера {scene_config['camera'].camera_type.value}, "
                  f"FOV {scene_config['camera'].fov:.1f}, "
                  f"Освітлення {scene_config['lighting'].sun_intensity:.2f}")
    
    print("\nТестування композиції завершено!")