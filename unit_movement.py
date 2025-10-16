#!/usr/bin/env python3
"""
Unit Movement System
Система руху юнітів з pathfinding та розміщенням

Інтегрує pathfinding та unit placement для створення повноцінної
системи руху юнітів з урахуванням формацій та колізій.
"""

import math
import time
from typing import List, Tuple, Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum

from pathfinding import Pathfinder, Grid, PathfindingAlgorithm, TerrainPathfinder
from unit_placement import UnitPlacementManager, Unit, FormationType, Formation


class MovementState(Enum):
    """Стани руху юніта"""
    IDLE = "idle"
    MOVING = "moving"
    FORMING = "forming"
    ATTACKING = "attacking"
    STUCK = "stuck"


@dataclass
class MovementCommand:
    """Команда руху для юніта"""
    unit_id: str
    target_position: Tuple[float, float]
    formation_id: Optional[str] = None
    priority: int = 0
    callback: Optional[Callable] = None


class UnitMovementController:
    """Контролер руху юнітів"""
    
    def __init__(self, grid: Grid, placement_manager: UnitPlacementManager):
        self.grid = grid
        self.placement_manager = placement_manager
        self.pathfinder = Pathfinder(grid)
        self.terrain_pathfinder = TerrainPathfinder(grid)
        
        # Стан руху юнітів
        self.unit_states: Dict[str, MovementState] = {}
        self.unit_paths: Dict[str, List[Tuple[float, float]]] = {}
        self.unit_targets: Dict[str, Tuple[float, float]] = {}
        self.movement_commands: List[MovementCommand] = []
        
        # Параметри руху
        self.movement_speed = 1.0
        self.formation_tolerance = 0.5
        self.stuck_threshold = 5.0  # секунд
        self.last_movement_time: Dict[str, float] = {}
    
    def move_unit_to(self, unit_id: str, target_position: Tuple[float, float], 
                    priority: int = 0, callback: Optional[Callable] = None) -> bool:
        """Перемістити юніт до позиції"""
        if unit_id not in self.placement_manager.units:
            return False
        
        unit = self.placement_manager.units[unit_id]
        start_position = unit.position
        
        # Знайти шлях
        path = self.pathfinder.find_path(start_position, target_position, PathfindingAlgorithm.A_STAR)
        
        if not path:
            return False
        
        # Зберегти команду руху
        command = MovementCommand(
            unit_id=unit_id,
            target_position=target_position,
            priority=priority,
            callback=callback
        )
        
        self.movement_commands.append(command)
        self.unit_states[unit_id] = MovementState.MOVING
        self.unit_paths[unit_id] = path
        self.unit_targets[unit_id] = target_position
        self.last_movement_time[unit_id] = time.time()
        
        return True
    
    def move_formation_to(self, formation_id: str, target_center: Tuple[float, float]) -> bool:
        """Перемістити формацію до позиції"""
        if formation_id not in self.placement_manager.formations:
            return False
        
        formation = self.placement_manager.formations[formation_id]
        
        # Перемістити формацію
        self.placement_manager.move_formation(formation_id, target_center)
        
        # Оновити стан всіх юнітів формації
        for unit in formation.units:
            self.unit_states[unit.unit_id] = MovementState.FORMING
            self.unit_paths[unit.unit_id] = []
            self.unit_targets[unit.unit_id] = target_center
        
        return True
    
    def update_movement(self, delta_time: float):
        """Оновити рух всіх юнітів"""
        current_time = time.time()
        
        for unit_id, unit in self.placement_manager.units.items():
            if unit_id not in self.unit_states:
                self.unit_states[unit_id] = MovementState.IDLE
                continue
            
            state = self.unit_states[unit_id]
            
            if state == MovementState.MOVING:
                self._update_unit_movement(unit, delta_time, current_time)
            elif state == MovementState.FORMING:
                self._update_formation_movement(unit, delta_time, current_time)
            elif state == MovementState.STUCK:
                self._handle_stuck_unit(unit, current_time)
    
    def _update_unit_movement(self, unit: Unit, delta_time: float, current_time: float):
        """Оновити рух окремого юніта"""
        if unit.unit_id not in self.unit_paths or not self.unit_paths[unit.unit_id]:
            self.unit_states[unit.unit_id] = MovementState.IDLE
            return
        
        path = self.unit_paths[unit.unit_id]
        current_pos = unit.position
        
        # Знайти найближчу точку на шляху
        closest_point = None
        closest_distance = float('inf')
        closest_index = -1
        
        for i, path_point in enumerate(path):
            distance = math.sqrt(
                (current_pos[0] - path_point[0])**2 + 
                (current_pos[1] - path_point[1])**2
            )
            if distance < closest_distance:
                closest_distance = distance
                closest_point = path_point
                closest_index = i
        
        if closest_point is None:
            self.unit_states[unit.unit_id] = MovementState.IDLE
            return
        
        # Перевірити чи досягли цілі
        if closest_distance < self.formation_tolerance:
            if closest_index >= len(path) - 1:
                # Досягли кінця шляху
                self.unit_states[unit.unit_id] = MovementState.IDLE
                self.unit_paths[unit.unit_id] = []
                
                # Викликати callback якщо є
                command = self._get_command_for_unit(unit.unit_id)
                if command and command.callback:
                    command.callback(unit.unit_id, True)
                
                return
            else:
                # Перейти до наступної точки
                closest_index += 1
        
        # Рухатися до наступної точки
        if closest_index < len(path):
            target_point = path[closest_index]
            self._move_towards(unit, target_point, delta_time)
            
            # Оновити час останнього руху
            self.last_movement_time[unit.unit_id] = current_time
    
    def _update_formation_movement(self, unit: Unit, delta_time: float, current_time: float):
        """Оновити рух юніта в формації"""
        if not unit.formation_id:
            self.unit_states[unit.unit_id] = MovementState.IDLE
            return
        
        formation = self.placement_manager.formations[unit.formation_id]
        target_pos = formation.center
        
        # Перевірити чи в правильній позиції
        distance = math.sqrt(
            (unit.position[0] - target_pos[0])**2 + 
            (unit.position[1] - target_pos[1])**2
        )
        
        if distance < self.formation_tolerance:
            self.unit_states[unit.unit_id] = MovementState.IDLE
        else:
            # Рухатися до позиції формації
            self._move_towards(unit, target_pos, delta_time)
            self.last_movement_time[unit.unit_id] = current_time
    
    def _move_towards(self, unit: Unit, target: Tuple[float, float], delta_time: float):
        """Рухати юніт до цілі"""
        current_pos = unit.position
        
        # Обчислити напрямок
        dx = target[0] - current_pos[0]
        dy = target[1] - current_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.01:  # Вже на місці
            return
        
        # Нормалізувати напрямок
        dx /= distance
        dy /= distance
        
        # Обчислити нову позицію
        move_distance = unit.speed * self.movement_speed * delta_time
        new_x = current_pos[0] + dx * move_distance
        new_y = current_pos[1] + dy * move_distance
        
        # Перевірити колізії
        if not self.placement_manager.collision_detector.check_collision((new_x, new_y), unit.size):
            # Оновити позицію
            unit.position = (new_x, new_y)
            
            # Оновити систему колізій
            self.placement_manager.collision_detector.remove_unit(unit.unit_id)
            self.placement_manager.collision_detector.add_unit(unit)
        else:
            # Спробувати знайти альтернативний шлях
            self._recalculate_path(unit)
    
    def _recalculate_path(self, unit: Unit):
        """Перерахувати шлях для юніта"""
        if unit.unit_id not in self.unit_targets:
            return
        
        target = self.unit_targets[unit.unit_id]
        new_path = self.pathfinder.find_path(unit.position, target, PathfindingAlgorithm.A_STAR)
        
        if new_path:
            self.unit_paths[unit.unit_id] = new_path
        else:
            # Позначити як застряглий
            self.unit_states[unit.unit_id] = MovementState.STUCK
    
    def _handle_stuck_unit(self, unit: Unit, current_time: float):
        """Обробити застряглий юніт"""
        if unit.unit_id not in self.last_movement_time:
            return
        
        stuck_time = current_time - self.last_movement_time[unit.unit_id]
        
        if stuck_time > self.stuck_threshold:
            # Спробувати знайти вільну позицію поблизу
            suggestions = self.placement_manager.get_placement_suggestions(
                unit.position, unit.size, count=3
            )
            
            if suggestions:
                # Перемістити до найближчої вільній позиції
                closest = min(suggestions, key=lambda pos: 
                    math.sqrt((pos[0] - unit.position[0])**2 + (pos[1] - unit.position[1])**2)
                )
                
                unit.position = closest
                self.unit_states[unit.unit_id] = MovementState.IDLE
                self.last_movement_time[unit.unit_id] = current_time
            else:
                # Залишити як застряглий
                pass
    
    def _get_command_for_unit(self, unit_id: str) -> Optional[MovementCommand]:
        """Отримати команду для юніта"""
        for command in self.movement_commands:
            if command.unit_id == unit_id:
                return command
        return None
    
    def stop_unit(self, unit_id: str):
        """Зупинити рух юніта"""
        if unit_id in self.unit_states:
            self.unit_states[unit_id] = MovementState.IDLE
            self.unit_paths[unit_id] = []
            self.unit_targets[unit_id] = None
    
    def stop_formation(self, formation_id: str):
        """Зупинити рух формації"""
        if formation_id in self.placement_manager.formations:
            formation = self.placement_manager.formations[formation_id]
            for unit in formation.units:
                self.stop_unit(unit.unit_id)
    
    def get_unit_state(self, unit_id: str) -> MovementState:
        """Отримати стан юніта"""
        return self.unit_states.get(unit_id, MovementState.IDLE)
    
    def is_unit_moving(self, unit_id: str) -> bool:
        """Перевірити чи рухається юніт"""
        return self.unit_states.get(unit_id, MovementState.IDLE) == MovementState.MOVING
    
    def get_remaining_path(self, unit_id: str) -> List[Tuple[float, float]]:
        """Отримати залишковий шлях юніта"""
        return self.unit_paths.get(unit_id, [])


class FormationController:
    """Контролер формацій з pathfinding"""
    
    def __init__(self, movement_controller: UnitMovementController):
        self.movement_controller = movement_controller
        self.placement_manager = movement_controller.placement_manager
    
    def create_formation_at(self, formation_type: FormationType, center: Tuple[float, float],
                          unit_types: List[str], unit_counts: List[int], army_id: str,
                          spacing: float = 2.0) -> Optional[str]:
        """Створити формацію в позиції"""
        formation_id = f"formation_{len(self.placement_manager.formations)}"
        
        # Створити формацію
        formation = self.placement_manager.create_formation(
            formation_id, formation_type, center, spacing
        )
        
        # Розмістити юнітів
        all_units = []
        for unit_type, count in zip(unit_types, unit_counts):
            units = self.placement_manager.place_units_in_formation(
                formation_id, unit_type, count, army_id
            )
            all_units.extend(units)
        
        return formation_id if all_units else None
    
    def move_formation_with_pathfinding(self, formation_id: str, target_center: Tuple[float, float]):
        """Перемістити формацію з pathfinding"""
        if formation_id not in self.placement_manager.formations:
            return False
        
        formation = self.placement_manager.formations[formation_id]
        current_center = formation.center
        
        # Знайти шлях для центру формації
        path = self.movement_controller.pathfinder.find_path(
            current_center, target_center, PathfindingAlgorithm.A_STAR
        )
        
        if not path:
            return False
        
        # Перемістити формацію по кроках
        for i, path_point in enumerate(path[1:], 1):  # Пропустити першу точку (поточну позицію)
            self.movement_controller.move_formation_to(formation_id, path_point)
        
        return True
    
    def maintain_formation_during_movement(self, formation_id: str):
        """Підтримувати формацію під час руху"""
        if formation_id not in self.placement_manager.formations:
            return
        
        formation = self.placement_manager.formations[formation_id]
        
        # Перевірити чи всі юніти в правильних позиціях
        for unit in formation.units:
            expected_positions = formation.get_formation_positions(len(formation.units))
            unit_index = formation.units.index(unit)
            
            if unit_index < len(expected_positions):
                expected_pos = expected_positions[unit_index]
                distance = math.sqrt(
                    (unit.position[0] - expected_pos[0])**2 + 
                    (unit.position[1] - expected_pos[1])**2
                )
                
                if distance > self.movement_controller.formation_tolerance:
                    # Юніт вийшов з формації, повернути його
                    self.movement_controller.move_unit_to(unit.unit_id, expected_pos)


# Приклад використання
if __name__ == "__main__":
    # Створити сітку та менеджер розміщення
    grid = Grid(50, 50, 1.0)
    placement_manager = UnitPlacementManager()
    
    # Додати перешкоди
    for x in range(20, 30):
        for y in range(20, 30):
            grid.set_obstacle(x, y)
    
    # Створити контролер руху
    movement_controller = UnitMovementController(grid, placement_manager)
    
    # Створити формацію
    formation_controller = FormationController(movement_controller)
    formation_id = formation_controller.create_formation_at(
        FormationType.LINE,
        (10.0, 10.0),
        ["warrior", "archer"],
        [3, 2],
        "army_1"
    )
    
    if formation_id:
        print(f"Створено формацію: {formation_id}")
        
        # Перемістити формацію
        movement_controller.move_formation_to(formation_id, (40.0, 40.0))
        
        # Симуляція руху
        for i in range(100):
            movement_controller.update_movement(0.016)  # 60 FPS
            time.sleep(0.016)
            
            # Перевірити стан
            formation = placement_manager.formations[formation_id]
            print(f"Крок {i}: Центр формації в {formation.center}")
    
    print("Симуляція завершена")