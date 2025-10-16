#!/usr/bin/env python3
"""
Intelligent Building Placement Algorithms for StarCraft Maps
Розумні алгоритми розміщення будівель для карт StarCraft

This module provides sophisticated building placement algorithms including:
- Strategic positioning based on game mechanics
- Resource optimization
- Defensive positioning
- Base layout optimization
"""

import math
import random
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class BuildingType(Enum):
    """Типи будівель"""
    CASTLE = "castle"
    TOWER = "tower"
    BARRACKS = "barracks"
    MAGE_TOWER = "mage_tower"
    WALL = "wall"
    GATE = "gate"
    RESOURCE_DEPOT = "resource_depot"
    WORKSHOP = "workshop"
    TEMPLE = "temple"


class ResourceType(Enum):
    """Типи ресурсів"""
    GOLD = "gold"
    WOOD = "wood"
    STONE = "stone"
    MANA = "mana"


@dataclass
class Building:
    """Будівля з характеристиками"""
    building_type: BuildingType
    position: Tuple[float, float]
    size: Tuple[float, float]
    health: int
    cost: int
    range: float = 0.0
    production: List[str] = None
    owner: str = "neutral"
    
    def __post_init__(self):
        if self.production is None:
            self.production = []


@dataclass
class ResourceNode:
    """Вузол ресурсів"""
    resource_type: ResourceType
    position: Tuple[float, float]
    amount: int
    radius: float = 2.0


@dataclass
class BaseLayout:
    """Макет бази"""
    center_position: Tuple[float, float]
    buildings: List[Building]
    resource_nodes: List[ResourceNode]
    walls: List[Building]
    gates: List[Building]


class StrategicAnalyzer:
    """Аналізатор стратегічних позицій"""
    
    def __init__(self, map_width: float, map_height: float):
        self.map_width = map_width
        self.map_height = map_height
        self.terrain_obstacles = set()
        self.resource_nodes = []
        self.enemy_positions = []
        self.chokepoints = []
        self.high_ground = []
    
    def add_terrain_obstacle(self, x: float, y: float, radius: float):
        """Додати перешкоду на місцевості"""
        self.terrain_obstacles.add((x, y, radius))
    
    def add_resource_node(self, resource: ResourceNode):
        """Додати вузол ресурсів"""
        self.resource_nodes.append(resource)
    
    def add_enemy_position(self, x: float, y: float, threat_level: float = 1.0):
        """Додати позицію ворога"""
        self.enemy_positions.append((x, y, threat_level))
    
    def add_chokepoint(self, x: float, y: float, width: float):
        """Додати вузький прохід"""
        self.chokepoints.append((x, y, width))
    
    def add_high_ground(self, x: float, y: float, radius: float):
        """Додати високу позицію"""
        self.high_ground.append((x, y, radius))
    
    def is_position_valid(self, x: float, y: float, building_size: Tuple[float, float]) -> bool:
        """Перевірити чи позиція валідна для будівлі"""
        width, height = building_size
        
        # Перевірити межі карти
        if not (width/2 <= x <= self.map_width - width/2 and 
                height/2 <= y <= self.map_height - height/2):
            return False
        
        # Перевірити перешкоди
        for obs_x, obs_y, obs_radius in self.terrain_obstacles:
            distance = math.sqrt((x - obs_x)**2 + (y - obs_y)**2)
            if distance < obs_radius + max(width, height) / 2:
                return False
        
        return True
    
    def get_strategic_value(self, x: float, y: float, building_type: BuildingType) -> float:
        """Обчислити стратегічну цінність позиції для будівлі"""
        value = 0.0
        
        # Бонус за близькість до ресурсів
        for resource in self.resource_nodes:
            distance = math.sqrt((x - resource.position[0])**2 + (y - resource.position[1])**2)
            if distance <= resource.radius * 2:
                value += 2.0 / (1 + distance)
        
        # Бонус за високу позицію для оборонних будівель
        if building_type in [BuildingType.TOWER, BuildingType.CASTLE, BuildingType.MAGE_TOWER]:
            for hg_x, hg_y, hg_radius in self.high_ground:
                distance = math.sqrt((x - hg_x)**2 + (y - hg_y)**2)
                if distance <= hg_radius:
                    value += 3.0
        
        # Бонус за контроль вузьких проходів
        if building_type in [BuildingType.TOWER, BuildingType.WALL, BuildingType.GATE]:
            for cp_x, cp_y, cp_width in self.chokepoints:
                distance = math.sqrt((x - cp_x)**2 + (y - cp_y)**2)
                if distance <= cp_width:
                    value += 2.5
        
        # Штраф за близькість до ворогів
        for enemy_x, enemy_y, threat_level in self.enemy_positions:
            distance = math.sqrt((x - enemy_x)**2 + (y - enemy_y)**2)
            if distance < 20.0:  # Близько до ворога
                value -= threat_level * (20.0 - distance) / 20.0
        
        return value
    
    def get_resource_accessibility(self, x: float, y: float) -> float:
        """Обчислити доступність ресурсів з позиції"""
        accessibility = 0.0
        
        for resource in self.resource_nodes:
            distance = math.sqrt((x - resource.position[0])**2 + (y - resource.position[1])**2)
            if distance <= resource.radius * 3:
                accessibility += resource.amount / (1 + distance)
        
        return accessibility


class BaseLayoutGenerator:
    """Генератор макетів баз"""
    
    def __init__(self, strategic_analyzer: StrategicAnalyzer):
        self.analyzer = strategic_analyzer
    
    def generate_base_layout(self, 
                           center_position: Tuple[float, float],
                           owner: str = "player",
                           base_size: float = 30.0) -> BaseLayout:
        """Згенерувати макет бази"""
        
        buildings = []
        walls = []
        gates = []
        
        # Знайти найкращі позиції для різних типів будівель
        building_positions = self._find_optimal_building_positions(center_position, base_size)
        
        # Розмістити головну будівлю (замок)
        castle_pos = self._find_best_position_for_building(
            center_position, BuildingType.CASTLE, building_positions
        )
        if castle_pos:
            castle = Building(
                building_type=BuildingType.CASTLE,
                position=castle_pos,
                size=(8.0, 8.0),
                health=500,
                cost=500,
                owner=owner
            )
            buildings.append(castle)
        
        # Розмістити оборонні вежі
        tower_positions = self._find_tower_positions(center_position, base_size)
        for i, pos in enumerate(tower_positions[:4]):  # Максимум 4 вежі
            tower = Building(
                building_type=BuildingType.TOWER,
                position=pos,
                size=(4.0, 4.0),
                health=200,
                cost=150,
                range=8.0,
                owner=owner
            )
            buildings.append(tower)
        
        # Розмістити виробничі будівлі
        production_buildings = [
            (BuildingType.BARRACKS, 2),
            (BuildingType.MAGE_TOWER, 1),
            (BuildingType.WORKSHOP, 1)
        ]
        
        for building_type, count in production_buildings:
            for _ in range(count):
                pos = self._find_best_position_for_building(
                    center_position, building_type, building_positions
                )
                if pos:
                    building = self._create_building(building_type, pos, owner)
                    buildings.append(building)
        
        # Розмістити ресурсні депо біля вузлів ресурсів
        depot_positions = self._find_resource_depot_positions(center_position)
        for pos in depot_positions[:3]:  # Максимум 3 депо
            depot = Building(
                building_type=BuildingType.RESOURCE_DEPOT,
                position=pos,
                size=(3.0, 3.0),
                health=100,
                cost=50,
                owner=owner
            )
            buildings.append(depot)
        
        # Збудувати стіни навколо бази
        wall_positions = self._generate_wall_positions(center_position, base_size)
        for pos in wall_positions:
            wall = Building(
                building_type=BuildingType.WALL,
                position=pos,
                size=(2.0, 2.0),
                health=100,
                cost=50,
                owner=owner
            )
            walls.append(wall)
        
        # Розмістити ворота
        gate_positions = self._find_gate_positions(center_position, base_size)
        for pos in gate_positions[:2]:  # Максимум 2 ворота
            gate = Building(
                building_type=BuildingType.GATE,
                position=pos,
                size=(3.0, 3.0),
                health=150,
                cost=75,
                owner=owner
            )
            gates.append(gate)
        
        return BaseLayout(
            center_position=center_position,
            buildings=buildings,
            resource_nodes=self.analyzer.resource_nodes,
            walls=walls,
            gates=gates
        )
    
    def _find_optimal_building_positions(self, 
                                       center: Tuple[float, float], 
                                       radius: float) -> List[Tuple[float, float]]:
        """Знайти оптимальні позиції для будівель"""
        positions = []
        center_x, center_y = center
        
        # Генерувати кандидатів позицій в радіусі бази
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            if self.analyzer.is_position_valid(x, y, (4.0, 4.0)):
                positions.append((x, y))
        
        return positions
    
    def _find_best_position_for_building(self, 
                                       center: Tuple[float, float],
                                       building_type: BuildingType,
                                       candidates: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """Знайти найкращу позицію для конкретної будівлі"""
        if not candidates:
            return None
        
        best_position = None
        best_score = -float('inf')
        
        for x, y in candidates:
            if self.analyzer.is_position_valid(x, y, self._get_building_size(building_type)):
                score = self.analyzer.get_strategic_value(x, y, building_type)
                
                if score > best_score:
                    best_score = score
                    best_position = (x, y)
        
        return best_position
    
    def _find_tower_positions(self, 
                            center: Tuple[float, float], 
                            radius: float) -> List[Tuple[float, float]]:
        """Знайти позиції для оборонних веж"""
        positions = []
        center_x, center_y = center
        
        # Розмістити вежі по периметру бази
        for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
            x = center_x + radius * 0.8 * math.cos(angle)
            y = center_y + radius * 0.8 * math.sin(angle)
            
            if self.analyzer.is_position_valid(x, y, (4.0, 4.0)):
                positions.append((x, y))
        
        # Додати додаткові вежі в стратегічних точках
        for _ in range(4):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(radius * 0.6, radius * 0.9)
            
            x = center_x + distance * math.cos(angle)
            y = center_y + distance * math.sin(angle)
            
            if self.analyzer.is_position_valid(x, y, (4.0, 4.0)):
                score = self.analyzer.get_strategic_value(x, y, BuildingType.TOWER)
                if score > 1.0:  # Тільки якщо стратегічно цінна
                    positions.append((x, y))
        
        return positions
    
    def _find_resource_depot_positions(self, 
                                     center: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Знайти позиції для ресурсних депо"""
        positions = []
        
        for resource in self.analyzer.resource_nodes:
            # Розмістити депо поруч з ресурсом
            resource_x, resource_y = resource.position
            
            for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                x = resource_x + resource.radius * 1.5 * math.cos(angle)
                y = resource_y + resource.radius * 1.5 * math.sin(angle)
                
                if self.analyzer.is_position_valid(x, y, (3.0, 3.0)):
                    positions.append((x, y))
        
        return positions
    
    def _generate_wall_positions(self, 
                               center: Tuple[float, float], 
                               radius: float) -> List[Tuple[float, float]]:
        """Згенерувати позиції для стін"""
        positions = []
        center_x, center_y = center
        
        # Створити стіни по периметру
        wall_segments = int(radius * 2)  # Кількість сегментів стіни
        
        for i in range(wall_segments):
            angle = (2 * math.pi * i) / wall_segments
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            if self.analyzer.is_position_valid(x, y, (2.0, 2.0)):
                positions.append((x, y))
        
        return positions
    
    def _find_gate_positions(self, 
                           center: Tuple[float, float], 
                           radius: float) -> List[Tuple[float, float]]:
        """Знайти позиції для воріт"""
        positions = []
        center_x, center_y = center
        
        # Розмістити ворота в найближчих точках до ресурсів
        for resource in self.analyzer.resource_nodes:
            resource_x, resource_y = resource.position
            
            # Обчислити напрямок до ресурсу
            dx = resource_x - center_x
            dy = resource_y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Нормалізувати напрямок
                dx /= distance
                dy /= distance
                
                # Розмістити ворота в цьому напрямку
                x = center_x + radius * dx
                y = center_y + radius * dy
                
                if self.analyzer.is_position_valid(x, y, (3.0, 3.0)):
                    positions.append((x, y))
        
        return positions
    
    def _create_building(self, 
                        building_type: BuildingType, 
                        position: Tuple[float, float], 
                        owner: str) -> Building:
        """Створити будівлю з базовими характеристиками"""
        
        building_configs = {
            BuildingType.BARRACKS: {
                'size': (6.0, 6.0),
                'health': 300,
                'cost': 200,
                'production': ['warrior', 'archer']
            },
            BuildingType.MAGE_TOWER: {
                'size': (5.0, 5.0),
                'health': 250,
                'cost': 300,
                'production': ['mage']
            },
            BuildingType.WORKSHOP: {
                'size': (5.0, 5.0),
                'health': 200,
                'cost': 150,
                'production': ['knight', 'cavalry']
            }
        }
        
        config = building_configs.get(building_type, {
            'size': (4.0, 4.0),
            'health': 100,
            'cost': 100,
            'production': []
        })
        
        return Building(
            building_type=building_type,
            position=position,
            size=config['size'],
            health=config['health'],
            cost=config['cost'],
            production=config['production'],
            owner=owner
        )
    
    def _get_building_size(self, building_type: BuildingType) -> Tuple[float, float]:
        """Отримати розмір будівлі за типом"""
        sizes = {
            BuildingType.CASTLE: (8.0, 8.0),
            BuildingType.TOWER: (4.0, 4.0),
            BuildingType.BARRACKS: (6.0, 6.0),
            BuildingType.MAGE_TOWER: (5.0, 5.0),
            BuildingType.WALL: (2.0, 2.0),
            BuildingType.GATE: (3.0, 3.0),
            BuildingType.RESOURCE_DEPOT: (3.0, 3.0),
            BuildingType.WORKSHOP: (5.0, 5.0),
            BuildingType.TEMPLE: (6.0, 6.0)
        }
        return sizes.get(building_type, (4.0, 4.0))


class BaseLayoutOptimizer:
    """Оптимізатор макетів баз"""
    
    def __init__(self, strategic_analyzer: StrategicAnalyzer):
        self.analyzer = strategic_analyzer
    
    def optimize_base_layout(self, 
                           base_layout: BaseLayout,
                           iterations: int = 50) -> BaseLayout:
        """Оптимізувати макет бази"""
        
        best_layout = base_layout
        best_score = self._evaluate_base_layout(base_layout)
        
        for _ in range(iterations):
            # Створити варіацію макету
            new_layout = self._mutate_base_layout(base_layout)
            
            # Оцінити новий макет
            new_score = self._evaluate_base_layout(new_layout)
            
            # Якщо кращий, прийняти його
            if new_score > best_score:
                best_layout = new_layout
                best_score = new_score
        
        return best_layout
    
    def _evaluate_base_layout(self, base_layout: BaseLayout) -> float:
        """Оцінити якість макету бази"""
        score = 0.0
        
        # Оцінити розміщення будівель
        for building in base_layout.buildings:
            strategic_value = self.analyzer.get_strategic_value(
                building.position[0], building.position[1], building.building_type
            )
            score += strategic_value
        
        # Бонус за захищеність бази
        defense_score = self._calculate_defense_score(base_layout)
        score += defense_score
        
        # Бонус за доступність ресурсів
        resource_score = self._calculate_resource_score(base_layout)
        score += resource_score
        
        # Штраф за перекриття будівель
        overlap_penalty = self._calculate_overlap_penalty(base_layout)
        score -= overlap_penalty
        
        return score
    
    def _calculate_defense_score(self, base_layout: BaseLayout) -> float:
        """Обчислити оцінку захищеності бази"""
        score = 0.0
        
        # Бонус за кількість оборонних будівель
        tower_count = sum(1 for b in base_layout.buildings if b.building_type == BuildingType.TOWER)
        score += tower_count * 2.0
        
        # Бонус за наявність стін
        wall_count = len(base_layout.walls)
        score += wall_count * 0.5
        
        # Бонус за ворота
        gate_count = len(base_layout.gates)
        score += gate_count * 1.0
        
        return score
    
    def _calculate_resource_score(self, base_layout: BaseLayout) -> float:
        """Обчислити оцінку доступу до ресурсів"""
        score = 0.0
        
        for building in base_layout.buildings:
            if building.building_type == BuildingType.RESOURCE_DEPOT:
                accessibility = self.analyzer.get_resource_accessibility(
                    building.position[0], building.position[1]
                )
                score += accessibility
        
        return score
    
    def _calculate_overlap_penalty(self, base_layout: BaseLayout) -> float:
        """Обчислити штраф за перекриття будівель"""
        penalty = 0.0
        all_buildings = base_layout.buildings + base_layout.walls + base_layout.gates
        
        for i in range(len(all_buildings)):
            for j in range(i + 1, len(all_buildings)):
                building1 = all_buildings[i]
                building2 = all_buildings[j]
                
                # Обчислити відстань між центрами
                distance = math.sqrt(
                    (building1.position[0] - building2.position[0])**2 +
                    (building1.position[1] - building2.position[1])**2
                )
                
                # Мінімальна відстань між будівлями
                min_distance = max(
                    building1.size[0] + building2.size[0],
                    building1.size[1] + building2.size[1]
                ) / 2
                
                if distance < min_distance:
                    penalty += (min_distance - distance) * 2.0
        
        return penalty
    
    def _mutate_base_layout(self, base_layout: BaseLayout) -> BaseLayout:
        """Мутувати макет бази для пошуку кращих варіантів"""
        new_layout = BaseLayout(
            center_position=base_layout.center_position,
            buildings=base_layout.buildings.copy(),
            resource_nodes=base_layout.resource_nodes,
            walls=base_layout.walls.copy(),
            gates=base_layout.gates.copy()
        )
        
        # Випадково перемістити деякі будівлі
        for building in new_layout.buildings:
            if random.random() < 0.1:  # 10% шанс мутації
                # Генерувати нову позицію
                center_x, center_y = base_layout.center_position
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(5.0, 25.0)
                
                new_x = center_x + distance * math.cos(angle)
                new_y = center_y + distance * math.sin(angle)
                
                if self.analyzer.is_position_valid(new_x, new_y, building.size):
                    building.position = (new_x, new_y)
        
        return new_layout


def create_sample_strategic_analyzer() -> StrategicAnalyzer:
    """Створити зразковий аналізатор стратегічної ситуації"""
    analyzer = StrategicAnalyzer(100.0, 100.0)
    
    # Додати перешкоди
    analyzer.add_terrain_obstacle(20, 20, 8.0)
    analyzer.add_terrain_obstacle(80, 80, 8.0)
    
    # Додати ресурси
    analyzer.add_resource_node(ResourceNode(ResourceType.GOLD, (30, 30), 1000))
    analyzer.add_resource_node(ResourceNode(ResourceType.WOOD, (70, 30), 800))
    analyzer.add_resource_node(ResourceNode(ResourceType.STONE, (50, 70), 600))
    
    # Додати ворогів
    analyzer.add_enemy_position(90, 90, 1.5)
    analyzer.add_enemy_position(10, 10, 1.0)
    
    # Додати вузькі проходи
    analyzer.add_chokepoint(50, 20, 4.0)
    analyzer.add_chokepoint(50, 80, 4.0)
    
    # Додати височини
    analyzer.add_high_ground(25, 25, 10.0)
    analyzer.add_high_ground(75, 75, 10.0)
    
    return analyzer


if __name__ == "__main__":
    # Приклад використання
    print("Генерація розумних макетів баз...")
    
    # Створити аналізатор та генератор
    analyzer = create_sample_strategic_analyzer()
    generator = BaseLayoutGenerator(analyzer)
    optimizer = BaseLayoutOptimizer(analyzer)
    
    # Згенерувати макет бази
    base_layout = generator.generate_base_layout(
        center_position=(50, 50),
        owner="player",
        base_size=25.0
    )
    
    # Оптимізувати макет
    optimized_layout = optimizer.optimize_base_layout(base_layout)
    
    print(f"\nЗгенеровано макет бази:")
    print(f"Центр: {optimized_layout.center_position}")
    print(f"Будівлі: {len(optimized_layout.buildings)}")
    print(f"Стіни: {len(optimized_layout.walls)}")
    print(f"Ворота: {len(optimized_layout.gates)}")
    
    print(f"\nДеталі будівель:")
    for building in optimized_layout.buildings:
        print(f"  {building.building_type.value}: {building.position} (HP: {building.health})")
    
    print("\nГенерація макетів завершена!")