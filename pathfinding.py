#!/usr/bin/env python3
"""
Pathfinding System
Система пошуку шляхів для юнітів

Реалізує алгоритми A*, Dijkstra, BFS для пошуку оптимальних шляхів
з урахуванням перешкод та рельєфу місцевості.
"""

import math
import heapq
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from enum import Enum


class PathfindingAlgorithm(Enum):
    """Алгоритми пошуку шляхів"""
    A_STAR = "a_star"
    DIJKSTRA = "dijkstra"
    BFS = "bfs"


@dataclass
class Node:
    """Вузол сітки для pathfinding"""
    x: int
    y: int
    g_cost: float = float('inf')  # Вартість від початку
    h_cost: float = 0.0           # Евристична вартість до цілі
    f_cost: float = float('inf')  # Загальна вартість (g + h)
    parent: Optional['Node'] = None
    walkable: bool = True
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))


class Grid:
    """Сітка для pathfinding"""
    
    def __init__(self, width: int, height: int, cell_size: float = 1.0):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.nodes: Dict[Tuple[int, int], Node] = {}
        self.obstacles: Set[Tuple[int, int]] = set()
        
        # Ініціалізувати всі вузли
        for x in range(width):
            for y in range(height):
                self.nodes[(x, y)] = Node(x, y)
    
    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Отримати вузол за координатами"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.nodes.get((x, y))
        return None
    
    def set_obstacle(self, x: int, y: int, is_obstacle: bool = True):
        """Встановити перешкоду в точці"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if is_obstacle:
                self.obstacles.add((x, y))
                self.nodes[(x, y)].walkable = False
            else:
                self.obstacles.discard((x, y))
                self.nodes[(x, y)].walkable = True
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Перевірити чи можна пройти через точку"""
        node = self.get_node(x, y)
        return node is not None and node.walkable
    
    def get_neighbors(self, node: Node, allow_diagonal: bool = True) -> List[Node]:
        """Отримати сусідні вузли"""
        neighbors = []
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0)  # Прямі напрямки
        ]
        
        if allow_diagonal:
            directions.extend([
                (1, 1), (1, -1), (-1, 1), (-1, -1)  # Діагональні напрямки
            ])
        
        for dx, dy in directions:
            new_x, new_y = node.x + dx, node.y + dy
            neighbor = self.get_node(new_x, new_y)
            if neighbor and neighbor.walkable:
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


class Pathfinder:
    """Основний клас для пошуку шляхів"""
    
    def __init__(self, grid: Grid):
        self.grid = grid
    
    def find_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                  algorithm: PathfindingAlgorithm = PathfindingAlgorithm.A_STAR) -> List[Tuple[float, float]]:
        """Знайти шлях між двома точками"""
        # Конвертувати в сіткові координати
        start_grid = self.grid.world_to_grid(start[0], start[1])
        end_grid = self.grid.world_to_grid(end[0], end[1])
        
        start_node = self.grid.get_node(start_grid[0], start_grid[1])
        end_node = self.grid.get_node(end_grid[0], end_grid[1])
        
        if not start_node or not end_node:
            return []
        
        if not start_node.walkable or not end_node.walkable:
            return []
        
        # Вибрати алгоритм
        if algorithm == PathfindingAlgorithm.A_STAR:
            path_nodes = self._a_star(start_node, end_node)
        elif algorithm == PathfindingAlgorithm.DIJKSTRA:
            path_nodes = self._dijkstra(start_node, end_node)
        elif algorithm == PathfindingAlgorithm.BFS:
            path_nodes = self._bfs(start_node, end_node)
        else:
            return []
        
        # Конвертувати назад в світові координати
        world_path = []
        for node in path_nodes:
            world_pos = self.grid.grid_to_world(node.x, node.y)
            world_path.append(world_pos)
        
        return world_path
    
    def _a_star(self, start: Node, end: Node) -> List[Node]:
        """Алгоритм A*"""
        open_set = []
        closed_set = set()
        
        # Скинути всі вузли
        for node in self.grid.nodes.values():
            node.g_cost = float('inf')
            node.h_cost = 0.0
            node.f_cost = float('inf')
            node.parent = None
        
        start.g_cost = 0
        start.h_cost = self._heuristic(start, end)
        start.f_cost = start.g_cost + start.h_cost
        
        heapq.heappush(open_set, start)
        
        while open_set:
            current = heapq.heappop(open_set)
            
            if current == end:
                return self._reconstruct_path(current)
            
            closed_set.add((current.x, current.y))
            
            for neighbor in self.grid.get_neighbors(current):
                if (neighbor.x, neighbor.y) in closed_set:
                    continue
                
                tentative_g = current.g_cost + self._get_distance(current, neighbor)
                
                if tentative_g < neighbor.g_cost:
                    neighbor.parent = current
                    neighbor.g_cost = tentative_g
                    neighbor.h_cost = self._heuristic(neighbor, end)
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)
        
        return []  # Шлях не знайдено
    
    def _dijkstra(self, start: Node, end: Node) -> List[Node]:
        """Алгоритм Дейкстри"""
        distances = {}
        previous = {}
        unvisited = set()
        
        # Ініціалізація
        for node in self.grid.nodes.values():
            distances[(node.x, node.y)] = float('inf')
            previous[(node.x, node.y)] = None
            unvisited.add((node.x, node.y))
        
        distances[(start.x, start.y)] = 0
        
        while unvisited:
            # Знайти вузол з найменшою відстанню
            current_pos = min(unvisited, key=lambda pos: distances[pos])
            current = self.grid.get_node(current_pos[0], current_pos[1])
            
            if current == end:
                return self._reconstruct_path_dijkstra(previous, end)
            
            unvisited.remove(current_pos)
            
            for neighbor in self.grid.get_neighbors(current):
                neighbor_pos = (neighbor.x, neighbor.y)
                if neighbor_pos not in unvisited:
                    continue
                
                alt = distances[current_pos] + self._get_distance(current, neighbor)
                if alt < distances[neighbor_pos]:
                    distances[neighbor_pos] = alt
                    previous[neighbor_pos] = current
        
        return []  # Шлях не знайдено
    
    def _bfs(self, start: Node, end: Node) -> List[Node]:
        """Алгоритм пошуку в ширину"""
        queue = [start]
        visited = set()
        parent = {}
        
        visited.add((start.x, start.y))
        
        while queue:
            current = queue.pop(0)
            
            if current == end:
                return self._reconstruct_path_bfs(parent, start, end)
            
            for neighbor in self.grid.get_neighbors(current, allow_diagonal=False):
                neighbor_pos = (neighbor.x, neighbor.y)
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    parent[neighbor_pos] = current
                    queue.append(neighbor)
        
        return []  # Шлях не знайдено
    
    def _heuristic(self, node1: Node, node2: Node) -> float:
        """Евристична функція для A* (манхеттенська відстань)"""
        return abs(node1.x - node2.x) + abs(node1.y - node2.y)
    
    def _get_distance(self, node1: Node, node2: Node) -> float:
        """Обчислити відстань між вузлами"""
        dx = abs(node1.x - node2.x)
        dy = abs(node1.y - node2.y)
        
        if dx == 1 and dy == 1:  # Діагональний рух
            return math.sqrt(2)
        else:  # Прямий рух
            return 1.0
    
    def _reconstruct_path(self, end: Node) -> List[Node]:
        """Відновити шлях для A*"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = current.parent
        
        path.reverse()
        return path
    
    def _reconstruct_path_dijkstra(self, previous: Dict, end: Node) -> List[Node]:
        """Відновити шлях для Дейкстри"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = previous.get((current.x, current.y))
        
        path.reverse()
        return path
    
    def _reconstruct_path_bfs(self, parent: Dict, start: Node, end: Node) -> List[Node]:
        """Відновити шлях для BFS"""
        path = []
        current = end
        
        while current != start:
            path.append(current)
            current = parent.get((current.x, current.y))
            if current is None:
                return []
        
        path.append(start)
        path.reverse()
        return path


class TerrainPathfinder:
    """Pathfinder з урахуванням рельєфу місцевості"""
    
    def __init__(self, grid: Grid, terrain_data: Dict = None):
        self.grid = grid
        self.terrain_data = terrain_data or {}
        self.pathfinder = Pathfinder(grid)
    
    def set_terrain_cost(self, terrain_type: str, cost_multiplier: float):
        """Встановити коефіцієнт вартості для типу рельєфу"""
        self.terrain_data[terrain_type] = cost_multiplier
    
    def find_path_with_terrain(self, start: Tuple[float, float], end: Tuple[float, float],
                              terrain_type: str = "grassland") -> List[Tuple[float, float]]:
        """Знайти шлях з урахуванням рельєфу"""
        # Отримати коефіцієнт вартості для рельєфу
        cost_multiplier = self.terrain_data.get(terrain_type, 1.0)
        
        # Тимчасово змінити вартості переміщення
        original_distances = {}
        
        # Застосувати коефіцієнт до всіх вузлів
        for node in self.grid.nodes.values():
            if node.walkable:
                # Зберігаємо оригінальні відстані
                original_distances[(node.x, node.y)] = node.g_cost
                # Застосовуємо коефіцієнт рельєфу
                node.g_cost *= cost_multiplier
        
        # Знайти шлях
        path = self.pathfinder.find_path(start, end)
        
        # Відновити оригінальні відстані
        for node in self.grid.nodes.values():
            if (node.x, node.y) in original_distances:
                node.g_cost = original_distances[(node.x, node.y)]
        
        return path


class PathfindingVisualizer:
    """Візуалізатор для pathfinding"""
    
    def __init__(self, grid: Grid):
        self.grid = grid
    
    def visualize_path(self, path: List[Tuple[float, float]], 
                      obstacles: List[Tuple[float, float]] = None) -> str:
        """Створити ASCII візуалізацію шляху"""
        if not path:
            return "Шлях не знайдено"
        
        # Створити сітку для візуалізації
        vis_grid = [['.' for _ in range(self.grid.width)] for _ in range(self.grid.height)]
        
        # Позначити перешкоди
        for obs_x, obs_y in obstacles or []:
            grid_x, grid_y = self.grid.world_to_grid(obs_x, obs_y)
            if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                vis_grid[grid_y][grid_x] = '#'
        
        # Позначити шлях
        for i, (world_x, world_y) in enumerate(path):
            grid_x, grid_y = self.grid.world_to_grid(world_x, world_y)
            if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                if i == 0:
                    vis_grid[grid_y][grid_x] = 'S'  # Початок
                elif i == len(path) - 1:
                    vis_grid[grid_y][grid_x] = 'E'  # Кінець
                else:
                    vis_grid[grid_y][grid_x] = '*'  # Шлях
        
        # Створити рядок для виводу
        result = []
        for row in reversed(vis_grid):  # Перевернути для правильного відображення
            result.append(''.join(row))
        
        return '\n'.join(result)


# Приклад використання
if __name__ == "__main__":
    # Створити сітку 10x10
    grid = Grid(10, 10, 1.0)
    
    # Додати перешкоди
    grid.set_obstacle(3, 3)
    grid.set_obstacle(3, 4)
    grid.set_obstacle(3, 5)
    grid.set_obstacle(4, 3)
    grid.set_obstacle(5, 3)
    
    # Створити pathfinder
    pathfinder = Pathfinder(grid)
    
    # Знайти шлях
    start = (1.0, 1.0)
    end = (8.0, 8.0)
    
    path = pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
    
    print(f"Шлях від {start} до {end}:")
    print(f"Кількість кроків: {len(path)}")
    
    # Візуалізувати
    visualizer = PathfindingVisualizer(grid)
    obstacles = [(3.0, 3.0), (3.0, 4.0), (3.0, 5.0), (4.0, 3.0), (5.0, 3.0)]
    print("\nВізуалізація:")
    print(visualizer.visualize_path(path, obstacles))