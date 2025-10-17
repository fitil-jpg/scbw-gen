#!/usr/bin/env python3
"""
Visualization Tools for Pathfinding and Unit Placement
Інструменти візуалізації для pathfinding та розміщення юнітів
"""

import math
import random
from typing import List, Tuple, Optional, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

from pathfinding import Grid, Pathfinder, PathfindingAlgorithm
from unit_placement import UnitPlacementManager, FormationType, Unit
from unit_movement import UnitMovementController, FormationController


class PathfindingVisualizer:
    """Візуалізатор для pathfinding"""
    
    def __init__(self, grid: Grid, figsize: Tuple[int, int] = (10, 10)):
        self.grid = grid
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_xlim(0, grid.width)
        self.ax.set_ylim(0, grid.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
    
    def visualize_grid(self, obstacles: List[Tuple[int, int]] = None):
        """Візуалізувати сітку з перешкодами"""
        # Очистити графік
        self.ax.clear()
        self.ax.set_xlim(0, self.grid.width)
        self.ax.set_ylim(0, self.grid.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Відобразити перешкоди
        if obstacles:
            for x, y in obstacles:
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                       edgecolor='black', facecolor='red', alpha=0.7)
                self.ax.add_patch(rect)
        else:
            # Відобразити всі перешкоди з сітки
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    if not self.grid.is_walkable(x, y):
                        rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                               edgecolor='black', facecolor='red', alpha=0.7)
                        self.ax.add_patch(rect)
    
    def visualize_path(self, path: List[Tuple[float, float]], 
                      start: Tuple[float, float] = None, 
                      end: Tuple[float, float] = None,
                      color: str = 'blue', linewidth: int = 2):
        """Візуалізувати шлях"""
        if not path:
            return
        
        # Відобразити шлях
        path_x = [point[0] for point in path]
        path_y = [point[1] for point in path]
        self.ax.plot(path_x, path_y, color=color, linewidth=linewidth, alpha=0.8)
        
        # Відобразити точки шляху
        self.ax.scatter(path_x, path_y, color=color, s=20, alpha=0.6)
        
        # Відобразити початок та кінець
        if start:
            self.ax.scatter([start[0]], [start[1]], color='green', s=100, marker='o', 
                          label='Початок', edgecolor='black', linewidth=2)
        
        if end:
            self.ax.scatter([end[0]], [end[1]], color='red', s=100, marker='s', 
                          label='Кінець', edgecolor='black', linewidth=2)
    
    def visualize_multiple_paths(self, paths: Dict[str, List[Tuple[float, float]]], 
                               colors: List[str] = None):
        """Візуалізувати кілька шляхів"""
        if colors is None:
            colors = ['blue', 'green', 'orange', 'purple', 'brown']
        
        color_idx = 0
        for name, path in paths.items():
            color = colors[color_idx % len(colors)]
            self.visualize_path(path, color=color)
            color_idx += 1
    
    def save_plot(self, filename: str, dpi: int = 300):
        """Зберегти графік"""
        self.ax.legend()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Графік збережено: {filename}")
    
    def show(self):
        """Показати графік"""
        self.ax.legend()
        plt.show()


class UnitPlacementVisualizer:
    """Візуалізатор для розміщення юнітів"""
    
    def __init__(self, placement_manager: UnitPlacementManager, 
                 figsize: Tuple[int, int] = (12, 8)):
        self.placement_manager = placement_manager
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_xlim(0, 50)  # За замовчуванням
        self.ax.set_ylim(0, 50)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
    
    def visualize_units(self, army_colors: Dict[str, str] = None):
        """Візуалізувати всіх юнітів"""
        if army_colors is None:
            army_colors = {
                'army_1': 'blue',
                'army_2': 'red',
                'army_3': 'green',
                'neutral': 'gray'
            }
        
        # Очистити графік
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)
        
        # Відобразити юнітів
        for unit in self.placement_manager.units.values():
            color = army_colors.get(unit.army_id, 'gray')
            
            # Створити прямокутник для юніта
            width, height = unit.size
            rect = patches.Rectangle(
                (unit.position[0] - width/2, unit.position[1] - height/2),
                width, height,
                linewidth=1, edgecolor='black', facecolor=color, alpha=0.7
            )
            self.ax.add_patch(rect)
            
            # Додати підпис
            self.ax.text(unit.position[0], unit.position[1], unit.unit_type[0].upper(),
                        ha='center', va='center', fontsize=8, fontweight='bold')
    
    def visualize_formations(self, formation_colors: Dict[str, str] = None):
        """Візуалізувати формації"""
        if formation_colors is None:
            formation_colors = {
                'formation_0': 'blue',
                'formation_1': 'red',
                'formation_2': 'green'
            }
        
        color_idx = 0
        for formation_id, formation in self.placement_manager.formations.items():
            color = formation_colors.get(formation_id, f'C{color_idx % 10}')
            
            # Відобразити центр формації
            center = formation.center
            self.ax.scatter([center[0]], [center[1]], color=color, s=100, 
                          marker='x', linewidth=3, label=f'Центр {formation_id}')
            
            # Відобразити юнітів формації
            for unit in formation.units:
                rect = patches.Rectangle(
                    (unit.position[0] - unit.size[0]/2, unit.position[1] - unit.size[1]/2),
                    unit.size[0], unit.size[1],
                    linewidth=1, edgecolor=color, facecolor=color, alpha=0.5
                )
                self.ax.add_patch(rect)
            
            color_idx += 1
    
    def visualize_collision_detection(self):
        """Візуалізувати систему колізій"""
        # Відобразити зайняті позиції
        for pos in self.placement_manager.collision_detector.occupied_positions:
            rect = patches.Rectangle(pos, 1, 1, linewidth=0.5, 
                                   edgecolor='red', facecolor='red', alpha=0.3)
            self.ax.add_patch(rect)
    
    def save_plot(self, filename: str, dpi: int = 300):
        """Зберегти графік"""
        self.ax.legend()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Графік збережено: {filename}")
    
    def show(self):
        """Показати графік"""
        self.ax.legend()
        plt.show()


class MovementVisualizer:
    """Візуалізатор для руху юнітів"""
    
    def __init__(self, movement_controller: UnitMovementController, 
                 figsize: Tuple[int, int] = (12, 8)):
        self.movement_controller = movement_controller
        self.placement_manager = movement_controller.placement_manager
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(0, 50)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Дані для анімації
        self.unit_positions_history = []
        self.formation_centers_history = []
    
    def visualize_current_state(self):
        """Візуалізувати поточний стан"""
        self.ax.clear()
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(0, 50)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Відобразити юнітів
        for unit in self.placement_manager.units.values():
            state = self.movement_controller.get_unit_state(unit.unit_id)
            
            # Кольори залежно від стану
            if state.value == 'moving':
                color = 'blue'
                alpha = 0.8
            elif state.value == 'forming':
                color = 'green'
                alpha = 0.8
            elif state.value == 'stuck':
                color = 'red'
                alpha = 0.8
            else:
                color = 'gray'
                alpha = 0.5
            
            rect = patches.Rectangle(
                (unit.position[0] - unit.size[0]/2, unit.position[1] - unit.size[1]/2),
                unit.size[0], unit.size[1],
                linewidth=1, edgecolor='black', facecolor=color, alpha=alpha
            )
            self.ax.add_patch(rect)
            
            # Додати стрілку напрямку руху
            if state.value == 'moving' and unit.unit_id in self.movement_controller.unit_paths:
                path = self.movement_controller.unit_paths[unit.unit_id]
                if len(path) > 1:
                    # Знайти наступну точку
                    current_pos = unit.position
                    next_point = None
                    min_dist = float('inf')
                    
                    for point in path:
                        dist = math.sqrt((point[0] - current_pos[0])**2 + (point[1] - current_pos[1])**2)
                        if dist < min_dist and dist > 0.1:
                            min_dist = dist
                            next_point = point
                    
                    if next_point:
                        dx = next_point[0] - current_pos[0]
                        dy = next_point[1] - current_pos[1]
                        self.ax.arrow(current_pos[0], current_pos[1], dx*0.5, dy*0.5,
                                    head_width=0.5, head_length=0.3, fc='blue', ec='blue')
        
        # Відобразити формації
        for formation in self.placement_manager.formations.values():
            center = formation.center
            self.ax.scatter([center[0]], [center[1]], color='red', s=100, 
                          marker='x', linewidth=3, label=f'Центр формації')
    
    def create_animation(self, duration: float = 10.0, fps: int = 30):
        """Створити анімацію руху"""
        frames = int(duration * fps)
        
        def animate(frame):
            # Оновити рух
            self.movement_controller.update_movement(1.0 / fps)
            
            # Зберегти позиції
            unit_positions = {}
            for unit in self.placement_manager.units.values():
                unit_positions[unit.unit_id] = unit.position
            self.unit_positions_history.append(unit_positions)
            
            # Зберегти центри формацій
            formation_centers = {}
            for formation_id, formation in self.placement_manager.formations.items():
                formation_centers[formation_id] = formation.center
            self.formation_centers_history.append(formation_centers)
            
            # Візуалізувати поточний стан
            self.visualize_current_state()
            
            return []
        
        anim = FuncAnimation(self.fig, animate, frames=frames, interval=1000/fps, 
                           blit=False, repeat=True)
        return anim
    
    def save_animation(self, filename: str, duration: float = 10.0, fps: int = 30):
        """Зберегти анімацію"""
        anim = self.create_animation(duration, fps)
        anim.save(filename, writer='pillow', fps=fps)
        print(f"Анімація збережена: {filename}")
    
    def show(self):
        """Показати графік"""
        self.ax.legend()
        plt.show()


def create_demo_scenario():
    """Створити демонстраційний сценарій"""
    # Створити сітку з перешкодами
    grid = Grid(30, 30, 1.0)
    
    # Додати перешкоди
    for x in range(10, 20):
        for y in range(10, 20):
            grid.set_obstacle(x, y)
    
    # Створити менеджери
    placement_manager = UnitPlacementManager()
    movement_controller = UnitMovementController(grid, placement_manager)
    formation_controller = FormationController(movement_controller)
    
    # Створити дві армії
    army1_formation = formation_controller.create_formation_at(
        FormationType.LINE, (5.0, 5.0), ["warrior", "archer"], [3, 2], "army_1"
    )
    
    army2_formation = formation_controller.create_formation_at(
        FormationType.ARC, (25.0, 25.0), ["warrior", "mage"], [2, 1], "army_2"
    )
    
    return grid, placement_manager, movement_controller, formation_controller


def demo_pathfinding():
    """Демонстрація pathfinding"""
    print("=== Демонстрація Pathfinding ===")
    
    # Створити сітку
    grid = Grid(20, 20, 1.0)
    
    # Додати перешкоди
    obstacles = []
    for x in range(8, 12):
        for y in range(8, 12):
            grid.set_obstacle(x, y)
            obstacles.append((x, y))
    
    # Створити pathfinder
    pathfinder = Pathfinder(grid)
    
    # Знайти шлях
    start = (2.0, 2.0)
    end = (18.0, 18.0)
    
    path = pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
    
    # Візуалізувати
    visualizer = PathfindingVisualizer(grid)
    visualizer.visualize_grid(obstacles)
    visualizer.visualize_path(path, start, end)
    visualizer.save_plot("pathfinding_demo.png")
    visualizer.show()
    
    print(f"Шлях знайдено: {len(path)} кроків")


def demo_unit_placement():
    """Демонстрація розміщення юнітів"""
    print("=== Демонстрація розміщення юнітів ===")
    
    # Створити менеджер
    placement_manager = UnitPlacementManager()
    
    # Створити формації
    formation1 = placement_manager.create_formation(
        "army1_line", FormationType.LINE, (10.0, 10.0), spacing=2.0
    )
    
    formation2 = placement_manager.create_formation(
        "army2_arc", FormationType.ARC, (30.0, 30.0), spacing=3.0
    )
    
    # Розмістити юнітів
    placement_manager.place_units_in_formation(
        "army1_line", "warrior", 5, "army_1"
    )
    
    placement_manager.place_units_in_formation(
        "army2_arc", "archer", 4, "army_2"
    )
    
    # Візуалізувати
    visualizer = UnitPlacementVisualizer(placement_manager)
    visualizer.visualize_units()
    visualizer.visualize_formations()
    visualizer.save_plot("unit_placement_demo.png")
    visualizer.show()
    
    print(f"Створено {len(placement_manager.units)} юнітів")


def demo_movement():
    """Демонстрація руху юнітів"""
    print("=== Демонстрація руху юнітів ===")
    
    # Створити сценарій
    grid, placement_manager, movement_controller, formation_controller = create_demo_scenario()
    
    # Перемістити армії
    army1_formation = list(placement_manager.formations.keys())[0]
    army2_formation = list(placement_manager.formations.keys())[1]
    
    movement_controller.move_formation_to(army1_formation, (15.0, 15.0))
    movement_controller.move_formation_to(army2_formation, (15.0, 15.0))
    
    # Візуалізувати
    visualizer = MovementVisualizer(movement_controller)
    visualizer.visualize_current_state()
    visualizer.save_plot("movement_demo.png")
    visualizer.show()
    
    print("Демонстрація руху завершена")


if __name__ == "__main__":
    # Запустити демонстрації
    try:
        demo_pathfinding()
        print()
        demo_unit_placement()
        print()
        demo_movement()
    except ImportError:
        print("Matplotlib не встановлено. Встановіть: pip install matplotlib")
    except Exception as e:
        print(f"Помилка: {e}")