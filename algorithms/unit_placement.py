#!/usr/bin/env python3
"""
Advanced Unit Placement Algorithms for StarCraft Maps
Розширені алгоритми розміщення юнітів для карт StarCraft

This module provides sophisticated unit placement algorithms including:
- Tactical formation generation
- AI-driven positioning
- Strategic considerations
- Formation optimization
"""

import math
import random
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class FormationType(Enum):
    """Типи формацій юнітів"""
    LINE = "line"
    ARC = "arc"
    WEDGE = "wedge"
    CIRCLE = "circle"
    SQUARE = "square"
    RANDOM = "random"
    TACTICAL = "tactical"


class UnitType(Enum):
    """Типи юнітів"""
    WARRIOR = "warrior"
    ARCHER = "archer"
    MAGE = "mage"
    KNIGHT = "knight"
    DRAGON = "dragon"
    CAVALRY = "cavalry"
    SIEGE = "siege"


@dataclass
class Unit:
    """Одиниця з тактичними характеристиками"""
    unit_type: UnitType
    position: Tuple[float, float]
    health: int
    damage: int
    range: float
    speed: float
    armor: int = 0
    special_abilities: List[str] = None
    
    def __post_init__(self):
        if self.special_abilities is None:
            self.special_abilities = []


@dataclass
class FormationConfig:
    """Конфігурація формації"""
    formation_type: FormationType
    spacing: float
    depth: int = 1
    width: int = None
    facing_direction: float = 0.0  # В радіанах
    center_position: Tuple[float, float] = (0.0, 0.0)


class TacticalAnalyzer:
    """Аналізатор тактичної ситуації"""
    
    def __init__(self, map_width: float, map_height: float):
        self.map_width = map_width
        self.map_height = map_height
        self.terrain_obstacles = set()
        self.chokepoints = []
        self.high_ground = []
        self.resource_nodes = []
    
    def add_terrain_obstacle(self, x: float, y: float, radius: float):
        """Додати перешкоду на місцевості"""
        self.terrain_obstacles.add((x, y, radius))
    
    def add_chokepoint(self, x: float, y: float, width: float):
        """Додати вузький прохід"""
        self.chokepoints.append((x, y, width))
    
    def add_high_ground(self, x: float, y: float, radius: float):
        """Додати високу позицію"""
        self.high_ground.append((x, y, radius))
    
    def is_position_valid(self, x: float, y: float, unit_radius: float = 0.5) -> bool:
        """Перевірити чи позиція валідна для розміщення юніта"""
        # Перевірити межі карти
        if not (0 <= x <= self.map_width and 0 <= y <= self.map_height):
            return False
        
        # Перевірити перешкоди
        for obs_x, obs_y, obs_radius in self.terrain_obstacles:
            distance = math.sqrt((x - obs_x)**2 + (y - obs_y)**2)
            if distance < obs_radius + unit_radius:
                return False
        
        return True
    
    def get_tactical_value(self, x: float, y: float) -> float:
        """Обчислити тактичну цінність позиції"""
        value = 0.0
        
        # Бонус за високу позицію
        for hg_x, hg_y, hg_radius in self.high_ground:
            distance = math.sqrt((x - hg_x)**2 + (y - hg_y)**2)
            if distance <= hg_radius:
                value += 2.0
        
        # Бонус за контроль вузьких проходів
        for cp_x, cp_y, cp_width in self.chokepoints:
            distance = math.sqrt((x - cp_x)**2 + (y - cp_y)**2)
            if distance <= cp_width:
                value += 1.5
        
        # Штраф за відстань від центру карти
        center_x, center_y = self.map_width / 2, self.map_height / 2
        distance_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = math.sqrt(center_x**2 + center_y**2)
        value += (1.0 - distance_from_center / max_distance) * 0.5
        
        return value


class FormationGenerator:
    """Генератор формацій юнітів"""
    
    def __init__(self, tactical_analyzer: TacticalAnalyzer):
        self.tactical_analyzer = tactical_analyzer
    
    def generate_formation(self, 
                          units: List[UnitType], 
                          config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати формацію для списку юнітів"""
        
        if config.formation_type == FormationType.LINE:
            return self._generate_line_formation(units, config)
        elif config.formation_type == FormationType.ARC:
            return self._generate_arc_formation(units, config)
        elif config.formation_type == FormationType.WEDGE:
            return self._generate_wedge_formation(units, config)
        elif config.formation_type == FormationType.CIRCLE:
            return self._generate_circle_formation(units, config)
        elif config.formation_type == FormationType.SQUARE:
            return self._generate_square_formation(units, config)
        elif config.formation_type == FormationType.TACTICAL:
            return self._generate_tactical_formation(units, config)
        else:  # RANDOM
            return self._generate_random_formation(units, config)
    
    def _generate_line_formation(self, 
                                units: List[UnitType], 
                                config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати лінійну формацію"""
        positions = []
        center_x, center_y = config.center_position
        
        # Обчислити кількість рядів
        units_per_row = len(units) // config.depth
        if len(units) % config.depth != 0:
            units_per_row += 1
        
        # Обчислити ширину формації
        total_width = (units_per_row - 1) * config.spacing
        start_x = center_x - total_width / 2
        
        for i, unit_type in enumerate(units):
            row = i // units_per_row
            col = i % units_per_row
            
            x = start_x + col * config.spacing
            y = center_y + row * config.spacing
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _generate_arc_formation(self, 
                               units: List[UnitType], 
                               config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати дугову формацію"""
        positions = []
        center_x, center_y = config.center_position
        
        # Обчислити радіус дуги
        arc_radius = (len(units) - 1) * config.spacing / (2 * math.pi)
        
        for i, unit_type in enumerate(units):
            angle = (i / (len(units) - 1)) * math.pi - math.pi / 2
            x = center_x + arc_radius * math.cos(angle)
            y = center_y + arc_radius * math.sin(angle)
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _generate_wedge_formation(self, 
                                 units: List[UnitType], 
                                 config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати клинову формацію"""
        positions = []
        center_x, center_y = config.center_position
        
        # Розділити юнітів на ряди
        rows = []
        current_row = []
        max_units_in_row = 1
        
        for i, unit_type in enumerate(units):
            current_row.append(unit_type)
            if len(current_row) >= max_units_in_row:
                rows.append(current_row)
                current_row = []
                max_units_in_row += 2  # Кожен наступний ряд на 2 юніти більше
        
        if current_row:
            rows.append(current_row)
        
        # Розмістити юнітів у клин
        for row_idx, row_units in enumerate(rows):
            row_width = len(row_units) * config.spacing
            start_x = center_x - row_width / 2
            y = center_y + row_idx * config.spacing
            
            for col_idx, unit_type in enumerate(row_units):
                x = start_x + col_idx * config.spacing
                
                # Повернути формацію
                if config.facing_direction != 0:
                    x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
                
                positions.append((x, y))
        
        return positions
    
    def _generate_circle_formation(self, 
                                  units: List[UnitType], 
                                  config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати кругову формацію"""
        positions = []
        center_x, center_y = config.center_position
        
        # Обчислити радіус кола
        circle_radius = len(units) * config.spacing / (2 * math.pi)
        
        for i, unit_type in enumerate(units):
            angle = (2 * math.pi * i) / len(units)
            x = center_x + circle_radius * math.cos(angle)
            y = center_y + circle_radius * math.sin(angle)
            
            positions.append((x, y))
        
        return positions
    
    def _generate_square_formation(self, 
                                  units: List[UnitType], 
                                  config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати квадратну формацію"""
        positions = []
        center_x, center_y = config.center_position
        
        # Обчислити розміри квадрата
        side_length = math.ceil(math.sqrt(len(units)))
        total_width = (side_length - 1) * config.spacing
        start_x = center_x - total_width / 2
        start_y = center_y - total_width / 2
        
        for i, unit_type in enumerate(units):
            row = i // side_length
            col = i % side_length
            
            x = start_x + col * config.spacing
            y = start_y + row * config.spacing
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _generate_tactical_formation(self, 
                                    units: List[UnitType], 
                                    config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати тактичну формацію з урахуванням місцевості"""
        positions = []
        
        # Розділити юнітів за типами
        unit_groups = defaultdict(list)
        for i, unit_type in enumerate(units):
            unit_groups[unit_type].append(i)
        
        # Розмістити різні типи юнітів стратегічно
        for unit_type, indices in unit_groups.items():
            if unit_type in [UnitType.ARCHER, UnitType.MAGE]:
                # Дальні бійці - на височині
                group_positions = self._place_ranged_units(indices, config)
            elif unit_type in [UnitType.WARRIOR, UnitType.KNIGHT]:
                # Ближні бійці - на передовій
                group_positions = self._place_melee_units(indices, config)
            elif unit_type == UnitType.DRAGON:
                # Літаючі - в повітрі над формацією
                group_positions = self._place_flying_units(indices, config)
            else:
                # Інші типи - стандартне розміщення
                group_positions = self._place_standard_units(indices, config)
            
            positions.extend(group_positions)
        
        return positions
    
    def _place_ranged_units(self, 
                           indices: List[int], 
                           config: FormationConfig) -> List[Tuple[float, float]]:
        """Розмістити дальніх бійців на височині"""
        positions = []
        
        # Знайти найкращі позиції для дальніх бійців
        best_positions = self._find_best_positions(len(indices), config, prefer_high_ground=True)
        
        for i, pos in enumerate(best_positions):
            if i < len(indices):
                positions.append(pos)
        
        return positions
    
    def _place_melee_units(self, 
                          indices: List[int], 
                          config: FormationConfig) -> List[Tuple[float, float]]:
        """Розмістити ближніх бійців на передовій"""
        positions = []
        
        # Розмістити ближніх бійців перед дальніми
        center_x, center_y = config.center_position
        front_distance = 2.0
        
        for i, idx in enumerate(indices):
            angle = (2 * math.pi * i) / len(indices)
            x = center_x + front_distance * math.cos(angle)
            y = center_y + front_distance * math.sin(angle)
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _place_flying_units(self, 
                           indices: List[int], 
                           config: FormationConfig) -> List[Tuple[float, float]]:
        """Розмістити літаючих юнітів в повітрі"""
        positions = []
        
        # Літаючі юніти розміщуються над формацією
        center_x, center_y = config.center_position
        altitude = 3.0
        
        for i, idx in enumerate(indices):
            angle = (2 * math.pi * i) / len(indices)
            radius = 1.0
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _place_standard_units(self, 
                             indices: List[int], 
                             config: FormationConfig) -> List[Tuple[float, float]]:
        """Стандартне розміщення юнітів"""
        positions = []
        
        # Використати лінійну формацію як базову
        center_x, center_y = config.center_position
        
        for i, idx in enumerate(indices):
            x = center_x + (i - len(indices) / 2) * config.spacing
            y = center_y
            
            # Повернути формацію
            if config.facing_direction != 0:
                x, y = self._rotate_position(x, y, center_x, center_y, config.facing_direction)
            
            positions.append((x, y))
        
        return positions
    
    def _find_best_positions(self, 
                            count: int, 
                            config: FormationConfig, 
                            prefer_high_ground: bool = False) -> List[Tuple[float, float]]:
        """Знайти найкращі позиції для розміщення юнітів"""
        positions = []
        
        # Генерувати кандидатів позицій
        candidates = []
        for _ in range(count * 10):  # Генерувати більше кандидатів
            x = random.uniform(0, self.tactical_analyzer.map_width)
            y = random.uniform(0, self.tactical_analyzer.map_height)
            
            if self.tactical_analyzer.is_position_valid(x, y):
                tactical_value = self.tactical_analyzer.get_tactical_value(x, y)
                if prefer_high_ground:
                    # Додатковий бонус за височину
                    for hg_x, hg_y, hg_radius in self.tactical_analyzer.high_ground:
                        distance = math.sqrt((x - hg_x)**2 + (y - hg_y)**2)
                        if distance <= hg_radius:
                            tactical_value += 1.0
                
                candidates.append((x, y, tactical_value))
        
        # Відсортувати за тактичною цінністю
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Взяти найкращі позиції
        for i in range(min(count, len(candidates))):
            positions.append((candidates[i][0], candidates[i][1]))
        
        return positions
    
    def _generate_random_formation(self, 
                                  units: List[UnitType], 
                                  config: FormationConfig) -> List[Tuple[float, float]]:
        """Згенерувати випадкову формацію"""
        positions = []
        
        for unit_type in units:
            # Генерувати випадкову позицію
            attempts = 0
            while attempts < 100:
                x = random.uniform(0, self.tactical_analyzer.map_width)
                y = random.uniform(0, self.tactical_analyzer.map_height)
                
                if self.tactical_analyzer.is_position_valid(x, y):
                    positions.append((x, y))
                    break
                
                attempts += 1
            
            # Якщо не знайшли валідну позицію, використати центр
            if len(positions) <= len(units) - 1:
                positions.append(config.center_position)
        
        return positions
    
    def _rotate_position(self, 
                        x: float, 
                        y: float, 
                        center_x: float, 
                        center_y: float, 
                        angle: float) -> Tuple[float, float]:
        """Повернути позицію навколо центру"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Перенести в початок координат
        x -= center_x
        y -= center_y
        
        # Повернути
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # Перенести назад
        new_x += center_x
        new_y += center_y
        
        return (new_x, new_y)


class UnitPlacementOptimizer:
    """Оптимізатор розміщення юнітів"""
    
    def __init__(self, tactical_analyzer: TacticalAnalyzer):
        self.tactical_analyzer = tactical_analyzer
    
    def optimize_formation(self, 
                          units: List[UnitType], 
                          initial_positions: List[Tuple[float, float]],
                          iterations: int = 100) -> List[Tuple[float, float]]:
        """Оптимізувати формацію для кращої тактичної позиції"""
        
        best_positions = initial_positions.copy()
        best_score = self._evaluate_formation(units, best_positions)
        
        for _ in range(iterations):
            # Генерувати нову конфігурацію
            new_positions = self._mutate_positions(best_positions)
            
            # Оцінити нову конфігурацію
            new_score = self._evaluate_formation(units, new_positions)
            
            # Якщо краща, прийняти її
            if new_score > best_score:
                best_positions = new_positions
                best_score = new_score
        
        return best_positions
    
    def _evaluate_formation(self, 
                           units: List[UnitType], 
                           positions: List[Tuple[float, float]]) -> float:
        """Оцінити якість формації"""
        score = 0.0
        
        # Оцінити тактичну цінність кожної позиції
        for i, (x, y) in enumerate(positions):
            if i < len(units):
                unit_type = units[i]
                tactical_value = self.tactical_analyzer.get_tactical_value(x, y)
                
                # Бонус за відповідність типу юніта позиції
                if unit_type in [UnitType.ARCHER, UnitType.MAGE]:
                    # Дальні бійці на височині
                    for hg_x, hg_y, hg_radius in self.tactical_analyzer.high_ground:
                        distance = math.sqrt((x - hg_x)**2 + (y - hg_y)**2)
                        if distance <= hg_radius:
                            tactical_value += 1.0
                
                score += tactical_value
        
        # Штраф за перекриття позицій
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if distance < 1.0:  # Мінімальна відстань між юнітами
                    score -= 2.0
        
        return score
    
    def _mutate_positions(self, 
                         positions: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Мутувати позиції для пошуку кращих варіантів"""
        new_positions = positions.copy()
        
        # Випадково змінити деякі позиції
        for i in range(len(new_positions)):
            if random.random() < 0.3:  # 30% шанс мутації
                x, y = new_positions[i]
                
                # Додати випадкове зміщення
                dx = random.uniform(-2.0, 2.0)
                dy = random.uniform(-2.0, 2.0)
                
                new_x = x + dx
                new_y = y + dy
                
                # Перевірити валідність нової позиції
                if self.tactical_analyzer.is_position_valid(new_x, new_y):
                    new_positions[i] = (new_x, new_y)
        
        return new_positions


def create_sample_army() -> List[UnitType]:
    """Створити зразкову армію для тестування"""
    return [
        UnitType.WARRIOR, UnitType.WARRIOR, UnitType.WARRIOR,
        UnitType.ARCHER, UnitType.ARCHER,
        UnitType.MAGE,
        UnitType.KNIGHT, UnitType.KNIGHT,
        UnitType.DRAGON
    ]


def create_sample_tactical_analyzer() -> TacticalAnalyzer:
    """Створити зразковий аналізатор тактичної ситуації"""
    analyzer = TacticalAnalyzer(100.0, 100.0)
    
    # Додати перешкоди
    analyzer.add_terrain_obstacle(30, 30, 5.0)
    analyzer.add_terrain_obstacle(70, 70, 5.0)
    
    # Додати вузькі проходи
    analyzer.add_chokepoint(50, 20, 3.0)
    analyzer.add_chokepoint(50, 80, 3.0)
    
    # Додати височини
    analyzer.add_high_ground(20, 20, 8.0)
    analyzer.add_high_ground(80, 80, 8.0)
    
    return analyzer


if __name__ == "__main__":
    # Приклад використання
    print("Генерація тактичних формацій...")
    
    # Створити аналізатор та генератор
    analyzer = create_sample_tactical_analyzer()
    generator = FormationGenerator(analyzer)
    optimizer = UnitPlacementOptimizer(analyzer)
    
    # Створити зразкову армію
    army = create_sample_army()
    
    # Згенерувати різні типи формацій
    formations = {
        "Line": FormationConfig(FormationType.LINE, 2.0, 1, facing_direction=0.0, center_position=(50, 50)),
        "Arc": FormationConfig(FormationType.ARC, 2.0, 1, facing_direction=0.0, center_position=(50, 50)),
        "Wedge": FormationConfig(FormationType.WEDGE, 2.0, 1, facing_direction=0.0, center_position=(50, 50)),
        "Tactical": FormationConfig(FormationType.TACTICAL, 2.0, 1, facing_direction=0.0, center_position=(50, 50))
    }
    
    for name, config in formations.items():
        print(f"\n{name} формація:")
        positions = generator.generate_formation(army, config)
        
        # Оптимізувати формацію
        optimized_positions = optimizer.optimize_formation(army, positions)
        
        print(f"Позиції юнітів: {len(optimized_positions)}")
        for i, (x, y) in enumerate(optimized_positions):
            if i < len(army):
                print(f"  {army[i].value}: ({x:.1f}, {y:.1f})")
    
    print("\nГенерація формацій завершена!")