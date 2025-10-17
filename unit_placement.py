#!/usr/bin/env python3
"""
Unit Placement System
Система розміщення юнітів з колізіями та формаціями

Забезпечує правильне розміщення юнітів з урахуванням колізій,
формацій та обмежень місцевості.
"""

import math
import random
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum
import yaml


class FormationType(Enum):
    """Типи формацій юнітів"""
    LINE = "line"
    ARC = "arc"
    SQUARE = "square"
    WEDGE = "wedge"
    CIRCLE = "circle"
    RANDOM = "random"
    CUSTOM = "custom"


@dataclass
class Unit:
    """Клас юніта"""
    unit_id: str
    unit_type: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    health: int
    damage: int
    speed: float
    cost: int
    army_id: str
    formation_id: Optional[str] = None
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Отримати межі юніта (x1, y1, x2, y2)"""
        half_width = self.size[0] / 2
        half_height = self.size[1] / 2
        return (
            self.position[0] - half_width,
            self.position[1] - half_height,
            self.position[0] + half_width,
            self.position[1] + half_height
        )


@dataclass
class Formation:
    """Клас формації юнітів"""
    formation_id: str
    formation_type: FormationType
    center: Tuple[float, float]
    spacing: float
    units: List[Unit]
    rotation: float = 0.0
    
    def get_formation_positions(self, unit_count: int) -> List[Tuple[float, float]]:
        """Отримати позиції для формації"""
        if self.formation_type == FormationType.LINE:
            return self._line_formation(unit_count)
        elif self.formation_type == FormationType.ARC:
            return self._arc_formation(unit_count)
        elif self.formation_type == FormationType.SQUARE:
            return self._square_formation(unit_count)
        elif self.formation_type == FormationType.WEDGE:
            return self._wedge_formation(unit_count)
        elif self.formation_type == FormationType.CIRCLE:
            return self._circle_formation(unit_count)
        elif self.formation_type == FormationType.RANDOM:
            return self._random_formation(unit_count)
        else:
            return []
    
    def _line_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Лінійна формація"""
        positions = []
        start_x = self.center[0] - (unit_count - 1) * self.spacing / 2
        
        for i in range(unit_count):
            x = start_x + i * self.spacing
            y = self.center[1]
            positions.append(self._rotate_point((x, y), self.center, self.rotation))
        
        return positions
    
    def _arc_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Дугова формація"""
        positions = []
        radius = self.spacing * unit_count / math.pi
        
        for i in range(unit_count):
            angle = math.pi * i / max(1, unit_count - 1)
            x = self.center[0] + radius * math.cos(angle)
            y = self.center[1] + radius * math.sin(angle)
            positions.append(self._rotate_point((x, y), self.center, self.rotation))
        
        return positions
    
    def _square_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Квадратна формація"""
        positions = []
        side_length = int(math.ceil(math.sqrt(unit_count)))
        
        for i in range(unit_count):
            row = i // side_length
            col = i % side_length
            x = self.center[0] + (col - side_length // 2) * self.spacing
            y = self.center[1] + (row - side_length // 2) * self.spacing
            positions.append(self._rotate_point((x, y), self.center, self.rotation))
        
        return positions
    
    def _wedge_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Клинова формація"""
        positions = []
        rows = int(math.ceil(math.sqrt(unit_count)))
        
        for i in range(unit_count):
            row = i // rows
            col = i % rows
            x = self.center[0] + (col - row) * self.spacing / 2
            y = self.center[1] + row * self.spacing
            positions.append(self._rotate_point((x, y), self.center, self.rotation))
        
        return positions
    
    def _circle_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Кругова формація"""
        positions = []
        radius = self.spacing * unit_count / (2 * math.pi)
        
        for i in range(unit_count):
            angle = 2 * math.pi * i / unit_count
            x = self.center[0] + radius * math.cos(angle)
            y = self.center[1] + radius * math.sin(angle)
            positions.append(self._rotate_point((x, y), self.center, self.rotation))
        
        return positions
    
    def _random_formation(self, unit_count: int) -> List[Tuple[float, float]]:
        """Випадкова формація"""
        positions = []
        spread = self.spacing * unit_count / 2
        
        for _ in range(unit_count):
            x = self.center[0] + random.uniform(-spread, spread)
            y = self.center[1] + random.uniform(-spread, spread)
            positions.append((x, y))
        
        return positions
    
    def _rotate_point(self, point: Tuple[float, float], center: Tuple[float, float], 
                     angle: float) -> Tuple[float, float]:
        """Повернути точку навколо центру"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Перенести в початок координат
        x = point[0] - center[0]
        y = point[1] - center[1]
        
        # Повернути
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # Перенести назад
        return (new_x + center[0], new_y + center[1])


class CollisionDetector:
    """Детектор колізій для юнітів"""
    
    def __init__(self):
        self.occupied_positions: Set[Tuple[float, float]] = set()
        self.unit_bounds: Dict[str, Tuple[float, float, float, float]] = {}
    
    def add_unit(self, unit: Unit):
        """Додати юніт до системи колізій"""
        bounds = unit.get_bounds()
        self.unit_bounds[unit.unit_id] = bounds
        
        # Додати всі точки в межах юніта
        x1, y1, x2, y2 = bounds
        for x in range(int(x1), int(x2) + 1):
            for y in range(int(y1), int(y2) + 1):
                self.occupied_positions.add((x, y))
    
    def remove_unit(self, unit_id: str):
        """Видалити юніт з системи колізій"""
        if unit_id in self.unit_bounds:
            bounds = self.unit_bounds[unit_id]
            x1, y1, x2, y2 = bounds
            
            # Видалити всі точки в межах юніта
            for x in range(int(x1), int(x2) + 1):
                for y in range(int(y1), int(y2) + 1):
                    self.occupied_positions.discard((x, y))
            
            del self.unit_bounds[unit_id]
    
    def check_collision(self, position: Tuple[float, float], size: Tuple[float, float]) -> bool:
        """Перевірити колізію в позиції"""
        half_width = size[0] / 2
        half_height = size[1] / 2
        bounds = (
            position[0] - half_width,
            position[1] - half_height,
            position[0] + half_width,
            position[1] + half_height
        )
        
        x1, y1, x2, y2 = bounds
        for x in range(int(x1), int(x2) + 1):
            for y in range(int(y1), int(y2) + 1):
                if (x, y) in self.occupied_positions:
                    return True
        
        return False
    
    def find_valid_position(self, center: Tuple[float, float], size: Tuple[float, float], 
                          max_attempts: int = 100) -> Optional[Tuple[float, float]]:
        """Знайти вільну позицію поблизу центру"""
        for _ in range(max_attempts):
            # Генерувати випадкову позицію в радіусі
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, 5.0)  # Максимальна відстань
            
            x = center[0] + distance * math.cos(angle)
            y = center[1] + distance * math.sin(angle)
            
            if not self.check_collision((x, y), size):
                return (x, y)
        
        return None


class UnitPlacementManager:
    """Менеджер розміщення юнітів"""
    
    def __init__(self, units_config_path: str = "assets/units/units_config.yaml"):
        self.units_config = self.load_units_config(units_config_path)
        self.units: Dict[str, Unit] = {}
        self.formations: Dict[str, Formation] = {}
        self.collision_detector = CollisionDetector()
        self.next_unit_id = 1
    
    def load_units_config(self, config_path: str) -> Dict:
        """Завантажити конфігурацію юнітів"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def create_unit(self, unit_type: str, position: Tuple[float, float], 
                   army_id: str, formation_id: Optional[str] = None) -> Optional[Unit]:
        """Створити юніт"""
        unit_config = self.units_config.get('units', {}).get(unit_type, {})
        if not unit_config:
            return None
        
        # Отримати параметри юніта
        size = tuple(unit_config.get('size', [32, 32]))
        health = unit_config.get('health', 100)
        damage = unit_config.get('damage', 25)
        speed = unit_config.get('speed', 1.0)
        cost = unit_config.get('cost', 50)
        
        # Перевірити колізії
        if self.collision_detector.check_collision(position, size):
            # Спробувати знайти вільну позицію
            new_position = self.collision_detector.find_valid_position(position, size)
            if new_position is None:
                return None
            position = new_position
        
        # Створити юніт
        unit_id = f"unit_{self.next_unit_id}"
        self.next_unit_id += 1
        
        unit = Unit(
            unit_id=unit_id,
            unit_type=unit_type,
            position=position,
            size=size,
            health=health,
            damage=damage,
            speed=speed,
            cost=cost,
            army_id=army_id,
            formation_id=formation_id
        )
        
        # Додати до системи
        self.units[unit_id] = unit
        self.collision_detector.add_unit(unit)
        
        return unit
    
    def create_formation(self, formation_id: str, formation_type: FormationType,
                       center: Tuple[float, float], spacing: float = 2.0,
                       rotation: float = 0.0) -> Formation:
        """Створити формацію"""
        formation = Formation(
            formation_id=formation_id,
            formation_type=formation_type,
            center=center,
            spacing=spacing,
            units=[],
            rotation=rotation
        )
        
        self.formations[formation_id] = formation
        return formation
    
    def place_units_in_formation(self, formation_id: str, unit_type: str, 
                                unit_count: int, army_id: str) -> List[Unit]:
        """Розмістити юнітів у формації"""
        if formation_id not in self.formations:
            return []
        
        formation = self.formations[formation_id]
        positions = formation.get_formation_positions(unit_count)
        
        placed_units = []
        for i, position in enumerate(positions):
            unit = self.create_unit(unit_type, position, army_id, formation_id)
            if unit:
                placed_units.append(unit)
                formation.units.append(unit)
        
        return placed_units
    
    def move_formation(self, formation_id: str, new_center: Tuple[float, float]):
        """Перемістити всю формацію"""
        if formation_id not in self.formations:
            return
        
        formation = self.formations[formation_id]
        old_center = formation.center
        offset_x = new_center[0] - old_center[0]
        offset_y = new_center[1] - old_center[1]
        
        # Оновити центр формації
        formation.center = new_center
        
        # Перемістити всіх юнітів
        for unit in formation.units:
            new_position = (unit.position[0] + offset_x, unit.position[1] + offset_y)
            
            # Видалити з системи колізій
            self.collision_detector.remove_unit(unit.unit_id)
            
            # Перевірити нову позицію
            if not self.collision_detector.check_collision(new_position, unit.size):
                unit.position = new_position
                self.collision_detector.add_unit(unit)
            else:
                # Знайти альтернативну позицію
                alt_position = self.collision_detector.find_valid_position(new_position, unit.size)
                if alt_position:
                    unit.position = alt_position
                    self.collision_detector.add_unit(unit)
    
    def remove_unit(self, unit_id: str) -> bool:
        """Видалити юніт"""
        if unit_id not in self.units:
            return False
        
        unit = self.units[unit_id]
        
        # Видалити з формації
        if unit.formation_id and unit.formation_id in self.formations:
            formation = self.formations[unit.formation_id]
            if unit in formation.units:
                formation.units.remove(unit)
        
        # Видалити з системи колізій
        self.collision_detector.remove_unit(unit_id)
        
        # Видалити з менеджера
        del self.units[unit_id]
        
        return True
    
    def get_units_in_area(self, area: Tuple[float, float, float, float]) -> List[Unit]:
        """Отримати юнітів в області"""
        x1, y1, x2, y2 = area
        units_in_area = []
        
        for unit in self.units.values():
            unit_x, unit_y = unit.position
            if x1 <= unit_x <= x2 and y1 <= unit_y <= y2:
                units_in_area.append(unit)
        
        return units_in_area
    
    def get_units_by_army(self, army_id: str) -> List[Unit]:
        """Отримати юнітів армії"""
        return [unit for unit in self.units.values() if unit.army_id == army_id]
    
    def get_formation_units(self, formation_id: str) -> List[Unit]:
        """Отримати юнітів формації"""
        if formation_id in self.formations:
            return self.formations[formation_id].units
        return []
    
    def validate_placement(self, position: Tuple[float, float], size: Tuple[float, float]) -> bool:
        """Перевірити чи можна розмістити юніт в позиції"""
        return not self.collision_detector.check_collision(position, size)
    
    def get_placement_suggestions(self, center: Tuple[float, float], size: Tuple[float, float],
                                 count: int = 5) -> List[Tuple[float, float]]:
        """Отримати пропозиції для розміщення"""
        suggestions = []
        
        for _ in range(count):
            suggestion = self.collision_detector.find_valid_position(center, size)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions


# Приклад використання
if __name__ == "__main__":
    # Створити менеджер розміщення
    manager = UnitPlacementManager()
    
    # Створити формацію
    formation = manager.create_formation(
        "army1_formation",
        FormationType.LINE,
        (10.0, 10.0),
        spacing=2.0
    )
    
    # Розмістити юнітів
    units = manager.place_units_in_formation(
        "army1_formation",
        "warrior",
        5,
        "army_1"
    )
    
    print(f"Розміщено {len(units)} юнітів")
    
    # Перемістити формацію
    manager.move_formation("army1_formation", (20.0, 20.0))
    
    # Отримати юнітів армії
    army_units = manager.get_units_by_army("army_1")
    print(f"Юнітів в армії 1: {len(army_units)}")
    
    # Перевірити розміщення
    valid = manager.validate_placement((15.0, 15.0), (32, 32))
    print(f"Позиція (15, 15) вільна: {valid}")