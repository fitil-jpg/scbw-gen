#!/usr/bin/env python3
"""
Pathfinding Integration for StarCraft Map Scenes
Інтеграція алгоритмів пошуку шляху для сцен карт StarCraft

This module provides pathfinding algorithms including:
- A* pathfinding with terrain considerations
- Formation movement
- Strategic path planning
- Dynamic obstacle avoidance
"""

import math
import heapq
import random
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class TerrainType(Enum):
    """Типи рельєфу для пошуку шляху"""
    GRASS = "grass"
    WATER = "water"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    SWAMP = "swamp"
    ROAD = "road"


@dataclass
class Node:
    """Вузол для пошуку шляху"""
    x: int
    y: int
    g_cost: float = 0.0
    h_cost: float = 0.0
    f_cost: float = 0.0
    parent: Optional['Node'] = None
    terrain_type: TerrainType = TerrainType.GRASS
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


class PathfindingGrid:
    """Сітка для пошуку шляху"""
    
    def __init__(self, width: int, height: int, cell_size: float = 1.0):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = {}
        self.obstacles = set()
        self.terrain_costs = {
            TerrainType.GRASS: 1.0,
            TerrainType.WATER: 2.0,
            TerrainType.MOUNTAIN: 3.0,
            TerrainType.FOREST: 1.5,
            TerrainType.SWAMP: 2.5,
            TerrainType.ROAD: 0.5
        }
    
    def add_obstacle(self, x: int, y: int):
        """Додати перешкоду"""
        self.obstacles.add((x, y))
    
    def set_terrain_type(self, x: int, y: int, terrain_type: TerrainType):
        """Встановити тип рельєфу для клітинки"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[(x, y)] = terrain_type
    
    def get_terrain_cost(self, x: int, y: int) -> float:
        """Отримати вартість проходження клітинки"""
        if (x, y) in self.obstacles:
            return float('inf')
        
        terrain_type = self.grid.get((x, y), TerrainType.GRASS)
        return self.terrain_costs.get(terrain_type, 1.0)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Перевірити чи позиція валідна"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                (x, y) not in self.obstacles)
    
    def get_neighbors(self, node: Node) -> List[Node]:
        """Отримати сусідні вузли"""
        neighbors = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dx, dy in directions:
            new_x = node.x + dx
            new_y = node.y + dy
            
            if self.is_valid_position(new_x, new_y):
                neighbor = Node(
                    x=new_x,
                    y=new_y,
                    terrain_type=self.grid.get((new_x, new_y), TerrainType.GRASS)
                )
                neighbors.append(neighbor)
        
        return neighbors
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Конвертувати світові координати в сіткові"""
        grid_x = int(world_x / self.cell_size)
        grid_y = int(world_y / self.cell_size)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Конвертувати сіткові координати в світові"""
        world_x = grid_x * self.cell_size + self.cell_size / 2
        world_y = grid_y * self.cell_size + self.cell_size / 2
        return world_x, world_y


class AStarPathfinder:
    """A* алгоритм пошуку шляху"""
    
    def __init__(self, grid: PathfindingGrid):
        self.grid = grid
    
    def find_path(self, 
                  start: Tuple[float, float], 
                  goal: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Знайти шлях від початку до цілі"""
        
        # Конвертувати в сіткові координати
        start_grid = self.grid.world_to_grid(start[0], start[1])
        goal_grid = self.grid.world_to_grid(goal[0], goal[1])
        
        # Створити початковий та цільовий вузли
        start_node = Node(x=start_grid[0], y=start_grid[1])
        goal_node = Node(x=goal_grid[0], y=goal_grid[1])
        
        # Відкритий та закритий списки
        open_list = []
        closed_set = set()
        
        # Додати початковий вузол
        start_node.g_cost = 0
        start_node.h_cost = self._heuristic(start_node, goal_node)
        start_node.f_cost = start_node.g_cost + start_node.h_cost
        
        heapq.heappush(open_list, start_node)
        
        while open_list:
            # Взяти вузол з найменшою f_cost
            current_node = heapq.heappop(open_list)
            
            # Перевірити чи досягли цілі
            if current_node == goal_node:
                return self._reconstruct_path(current_node)
            
            # Додати в закритий список
            closed_set.add((current_node.x, current_node.y))
            
            # Перевірити сусідів
            for neighbor in self.grid.get_neighbors(current_node):
                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                
                # Обчислити вартість до сусіда
                tentative_g_cost = current_node.g_cost + self._get_distance(current_node, neighbor)
                
                # Перевірити чи знайшли кращий шлях
                if neighbor not in open_list or tentative_g_cost < neighbor.g_cost:
                    neighbor.g_cost = tentative_g_cost
                    neighbor.h_cost = self._heuristic(neighbor, goal_node)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    neighbor.parent = current_node
                    
                    if neighbor not in open_list:
                        heapq.heappush(open_list, neighbor)
        
        # Шлях не знайдено
        return []
    
    def _heuristic(self, node: Node, goal: Node) -> float:
        """Евристична функція (відстань манхеттен)"""
        return abs(node.x - goal.x) + abs(node.y - goal.y)
    
    def _get_distance(self, node1: Node, node2: Node) -> float:
        """Обчислити відстань між вузлами"""
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        
        # Діагональна відстань
        if dx == 1 and dy == 1:
            return math.sqrt(2) * self.grid.get_terrain_cost(node2.x, node2.y)
        else:
            return self.grid.get_terrain_cost(node2.x, node2.y)
    
    def _reconstruct_path(self, goal_node: Node) -> List[Tuple[float, float]]:
        """Відновити шлях від цілі до початку"""
        path = []
        current = goal_node
        
        while current is not None:
            world_pos = self.grid.grid_to_world(current.x, current.y)
            path.append(world_pos)
            current = current.parent
        
        path.reverse()
        return path


class FormationPathfinder:
    """Пошук шляху для формацій юнітів"""
    
    def __init__(self, grid: PathfindingGrid):
        self.grid = grid
        self.astar = AStarPathfinder(grid)
    
    def find_formation_path(self, 
                           formation_center: Tuple[float, float],
                           formation_positions: List[Tuple[float, float]],
                           goal: Tuple[float, float]) -> List[List[Tuple[float, float]]]:
        """Знайти шляхи для всіх юнітів у формації"""
        
        # Знайти шлях для центру формації
        center_path = self.astar.find_path(formation_center, goal)
        
        if not center_path:
            return []
        
        # Обчислити зміщення для кожного юніта
        unit_offsets = []
        for pos in formation_positions:
            offset_x = pos[0] - formation_center[0]
            offset_y = pos[1] - formation_center[1]
            unit_offsets.append((offset_x, offset_y))
        
        # Створити шляхи для кожного юніта
        unit_paths = []
        for i, offset in enumerate(unit_offsets):
            unit_path = []
            for center_point in center_path:
                unit_x = center_point[0] + offset[0]
                unit_y = center_point[1] + offset[1]
                unit_path.append((unit_x, unit_y))
            unit_paths.append(unit_path)
        
        return unit_paths
    
    def smooth_formation_path(self, 
                            unit_paths: List[List[Tuple[float, float]]],
                            smoothing_factor: float = 0.5) -> List[List[Tuple[float, float]]]:
        """Згладжувати шляхи формації"""
        smoothed_paths = []
        
        for unit_path in unit_paths:
            if len(unit_path) < 3:
                smoothed_paths.append(unit_path)
                continue
            
            smoothed_path = [unit_path[0]]  # Початкова точка
            
            for i in range(1, len(unit_path) - 1):
                # Згладжування з використанням середнього значення
                prev_point = unit_path[i - 1]
                curr_point = unit_path[i]
                next_point = unit_path[i + 1]
                
                smooth_x = (prev_point[0] + curr_point[0] + next_point[0]) / 3
                smooth_y = (prev_point[1] + curr_point[1] + next_point[1]) / 3
                
                # Застосувати коефіцієнт згладжування
                final_x = curr_point[0] + smoothing_factor * (smooth_x - curr_point[0])
                final_y = curr_point[1] + smoothing_factor * (smooth_y - curr_point[1])
                
                smoothed_path.append((final_x, final_y))
            
            smoothed_path.append(unit_path[-1])  # Кінцева точка
            smoothed_paths.append(smoothed_path)
        
        return smoothed_paths


class StrategicPathPlanner:
    """Стратегічний планувальник шляхів"""
    
    def __init__(self, grid: PathfindingGrid):
        self.grid = grid
        self.astar = AStarPathfinder(grid)
        self.formation_pathfinder = FormationPathfinder(grid)
    
    def plan_attack_path(self, 
                        start: Tuple[float, float],
                        enemy_base: Tuple[float, float],
                        waypoints: List[Tuple[float, float]] = None) -> List[Tuple[float, float]]:
        """Спланувати шлях атаки"""
        
        if not waypoints:
            waypoints = self._generate_attack_waypoints(start, enemy_base)
        
        # Об'єднати всі точки в один шлях
        full_path = [start]
        
        for waypoint in waypoints:
            path_segment = self.astar.find_path(full_path[-1], waypoint)
            if path_segment:
                full_path.extend(path_segment[1:])  # Пропустити першу точку (дублікат)
        
        # Додати шлях до цілі
        final_path = self.astar.find_path(full_path[-1], enemy_base)
        if final_path:
            full_path.extend(final_path[1:])
        
        return full_path
    
    def plan_retreat_path(self, 
                         current_pos: Tuple[float, float],
                         safe_zone: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Спланувати шлях відступу"""
        
        # Знайти найкоротший шлях до безпечної зони
        return self.astar.find_path(current_pos, safe_zone)
    
    def plan_patrol_path(self, 
                        patrol_points: List[Tuple[float, float]],
                        loop: bool = True) -> List[Tuple[float, float]]:
        """Спланувати патрульний шлях"""
        
        if len(patrol_points) < 2:
            return patrol_points
        
        full_path = []
        
        # Створити шлях між точками патрулювання
        for i in range(len(patrol_points)):
            current_point = patrol_points[i]
            next_point = patrol_points[(i + 1) % len(patrol_points)]
            
            path_segment = self.astar.find_path(current_point, next_point)
            if path_segment:
                full_path.extend(path_segment)
        
        # Якщо не потрібно зациклювати, повернути як є
        if not loop:
            return full_path
        
        # Додати шлях назад до початку
        if full_path and full_path[0] != full_path[-1]:
            return_path = self.astar.find_path(full_path[-1], full_path[0])
            if return_path:
                full_path.extend(return_path[1:])
        
        return full_path
    
    def _generate_attack_waypoints(self, 
                                  start: Tuple[float, float],
                                  target: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Згенерувати проміжні точки для атаки"""
        waypoints = []
        
        # Знайти височини на шляху
        high_ground_points = self._find_high_ground_points(start, target)
        waypoints.extend(high_ground_points)
        
        # Знайти вузькі проходи для контролю
        chokepoint_positions = self._find_chokepoint_positions(start, target)
        waypoints.extend(chokepoint_positions)
        
        # Сортувати за відстанню від початку
        waypoints.sort(key=lambda wp: math.sqrt((wp[0] - start[0])**2 + (wp[1] - start[1])**2))
        
        return waypoints
    
    def _find_high_ground_points(self, 
                                start: Tuple[float, float],
                                target: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Знайти височини на шляху"""
        # Спрощена реалізація - в реальності потрібно аналізувати карту висот
        waypoints = []
        
        # Додати кілька випадкових точок на шляху
        for _ in range(2):
            t = random.uniform(0.2, 0.8)
            x = start[0] + t * (target[0] - start[0])
            y = start[1] + t * (target[1] - start[1])
            waypoints.append((x, y))
        
        return waypoints
    
    def _find_chokepoint_positions(self, 
                                  start: Tuple[float, float],
                                  target: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Знайти позиції вузьких проходів"""
        # Спрощена реалізація
        waypoints = []
        
        # Додати точку посередині шляху
        mid_x = (start[0] + target[0]) / 2
        mid_y = (start[1] + target[1]) / 2
        waypoints.append((mid_x, mid_y))
        
        return waypoints


class DynamicObstacleAvoidance:
    """Уникнення динамічних перешкод"""
    
    def __init__(self, grid: PathfindingGrid):
        self.grid = grid
        self.astar = AStarPathfinder(grid)
        self.dynamic_obstacles = {}
    
    def add_dynamic_obstacle(self, 
                           obstacle_id: str, 
                           position: Tuple[float, float],
                           radius: float,
                           duration: float = 5.0):
        """Додати динамічну перешкоду"""
        self.dynamic_obstacles[obstacle_id] = {
            'position': position,
            'radius': radius,
            'duration': duration,
            'start_time': 0.0  # Буде встановлено при використанні
        }
    
    def update_dynamic_obstacles(self, current_time: float):
        """Оновити динамічні перешкоди"""
        obstacles_to_remove = []
        
        for obstacle_id, obstacle in self.dynamic_obstacles.items():
            if current_time - obstacle['start_time'] > obstacle['duration']:
                obstacles_to_remove.append(obstacle_id)
        
        for obstacle_id in obstacles_to_remove:
            del self.dynamic_obstacles[obstacle_id]
    
    def find_path_with_avoidance(self, 
                                start: Tuple[float, float],
                                goal: Tuple[float, float],
                                current_time: float = 0.0) -> List[Tuple[float, float]]:
        """Знайти шлях з уникненням динамічних перешкод"""
        
        # Оновити динамічні перешкоди
        self.update_dynamic_obstacles(current_time)
        
        # Додати динамічні перешкоди до сітки
        temp_obstacles = set()
        for obstacle in self.dynamic_obstacles.values():
            pos = obstacle['position']
            radius = obstacle['radius']
            
            # Додати перешкоду як кілька клітинок
            grid_pos = self.grid.world_to_grid(pos[0], pos[1])
            for dx in range(-int(radius), int(radius) + 1):
                for dy in range(-int(radius), int(radius) + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        temp_obstacles.add((grid_pos[0] + dx, grid_pos[1] + dy))
        
        # Тимчасово додати перешкоди до сітки
        original_obstacles = self.grid.obstacles.copy()
        self.grid.obstacles.update(temp_obstacles)
        
        # Знайти шлях
        path = self.astar.find_path(start, goal)
        
        # Відновити оригінальні перешкоди
        self.grid.obstacles = original_obstacles
        
        return path


def create_sample_pathfinding_grid() -> PathfindingGrid:
    """Створити зразкову сітку для пошуку шляху"""
    grid = PathfindingGrid(50, 50, cell_size=2.0)
    
    # Додати перешкоди
    for x in range(10, 15):
        for y in range(10, 15):
            grid.add_obstacle(x, y)
    
    for x in range(35, 40):
        for y in range(35, 40):
            grid.add_obstacle(x, y)
    
    # Додати різні типи рельєфу
    for x in range(20, 30):
        for y in range(20, 30):
            grid.set_terrain_type(x, y, TerrainType.FOREST)
    
    for x in range(5, 10):
        for y in range(5, 10):
            grid.set_terrain_type(x, y, TerrainType.WATER)
    
    return grid


if __name__ == "__main__":
    # Приклад використання
    print("Тестування алгоритмів пошуку шляху...")
    
    # Створити сітку
    grid = create_sample_pathfinding_grid()
    
    # Тестувати A* пошук
    astar = AStarPathfinder(grid)
    start = (5.0, 5.0)
    goal = (45.0, 45.0)
    
    path = astar.find_path(start, goal)
    print(f"A* шлях від {start} до {goal}: {len(path)} точок")
    
    # Тестувати формаційний пошук
    formation_pathfinder = FormationPathfinder(grid)
    formation_center = (10.0, 10.0)
    formation_positions = [
        (9.0, 9.0), (11.0, 9.0), (9.0, 11.0), (11.0, 11.0)
    ]
    
    formation_paths = formation_pathfinder.find_formation_path(
        formation_center, formation_positions, goal
    )
    print(f"Шляхи формації: {len(formation_paths)} юнітів")
    
    # Тестувати стратегічне планування
    strategic_planner = StrategicPathPlanner(grid)
    attack_path = strategic_planner.plan_attack_path(start, goal)
    print(f"Шлях атаки: {len(attack_path)} точок")
    
    # Тестувати уникнення перешкод
    avoidance = DynamicObstacleAvoidance(grid)
    avoidance.add_dynamic_obstacle("temp_obstacle", (25.0, 25.0), 3.0, 10.0)
    
    avoidance_path = avoidance.find_path_with_avoidance(start, goal)
    print(f"Шлях з уникненням: {len(avoidance_path)} точок")
    
    print("Тестування завершено!")