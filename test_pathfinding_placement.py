#!/usr/bin/env python3
"""
Test Suite for Pathfinding and Unit Placement
Тестовий набір для систем pathfinding та розміщення юнітів
"""

import unittest
import math
import time
from pathfinding import Grid, Pathfinder, PathfindingAlgorithm, TerrainPathfinder
from unit_placement import UnitPlacementManager, FormationType, Unit
from unit_movement import UnitMovementController, FormationController


class TestPathfinding(unittest.TestCase):
    """Тести для pathfinding системи"""
    
    def setUp(self):
        """Налаштування перед кожним тестом"""
        self.grid = Grid(10, 10, 1.0)
        self.pathfinder = Pathfinder(self.grid)
    
    def test_basic_pathfinding(self):
        """Тест базового pathfinding"""
        # Простий шлях без перешкод
        start = (1.0, 1.0)
        end = (8.0, 8.0)
        
        path = self.pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
        
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)
    
    def test_obstacle_avoidance(self):
        """Тест обходу перешкод"""
        # Додати перешкоди
        self.grid.set_obstacle(4, 4)
        self.grid.set_obstacle(4, 5)
        self.grid.set_obstacle(5, 4)
        self.grid.set_obstacle(5, 5)
        
        start = (2.0, 2.0)
        end = (7.0, 7.0)
        
        path = self.pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
        
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        
        # Перевірити що шлях не проходить через перешкоди
        for point in path:
            grid_x, grid_y = self.grid.world_to_grid(point[0], point[1])
            self.assertFalse(self.grid.is_walkable(grid_x, grid_y) == False)
    
    def test_no_path_scenario(self):
        """Тест сценарію без шляху"""
        # Створити стіну
        for x in range(3, 7):
            for y in range(3, 7):
                self.grid.set_obstacle(x, y)
        
        start = (1.0, 1.0)
        end = (8.0, 8.0)
        
        path = self.pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
        
        # Шлях не повинен існувати
        self.assertEqual(len(path), 0)
    
    def test_different_algorithms(self):
        """Тест різних алгоритмів"""
        start = (1.0, 1.0)
        end = (8.0, 8.0)
        
        # A*
        path_a_star = self.pathfinder.find_path(start, end, PathfindingAlgorithm.A_STAR)
        self.assertIsNotNone(path_a_star)
        
        # Dijkstra
        path_dijkstra = self.pathfinder.find_path(start, end, PathfindingAlgorithm.DIJKSTRA)
        self.assertIsNotNone(path_dijkstra)
        
        # BFS
        path_bfs = self.pathfinder.find_path(start, end, PathfindingAlgorithm.BFS)
        self.assertIsNotNone(path_bfs)
        
        # Всі шляхи повинні мати однакову початкову та кінцеву точки
        self.assertEqual(path_a_star[0], path_dijkstra[0])
        self.assertEqual(path_a_star[-1], path_dijkstra[-1])
        self.assertEqual(path_a_star[0], path_bfs[0])
        self.assertEqual(path_a_star[-1], path_bfs[-1])


class TestUnitPlacement(unittest.TestCase):
    """Тести для системи розміщення юнітів"""
    
    def setUp(self):
        """Налаштування перед кожним тестом"""
        self.placement_manager = UnitPlacementManager()
    
    def test_unit_creation(self):
        """Тест створення юніта"""
        unit = self.placement_manager.create_unit(
            "warrior", (10.0, 10.0), "army_1"
        )
        
        self.assertIsNotNone(unit)
        self.assertEqual(unit.unit_type, "warrior")
        self.assertEqual(unit.position, (10.0, 10.0))
        self.assertEqual(unit.army_id, "army_1")
        self.assertIn(unit.unit_id, self.placement_manager.units)
    
    def test_collision_detection(self):
        """Тест детекції колізій"""
        # Створити перший юніт
        unit1 = self.placement_manager.create_unit(
            "warrior", (10.0, 10.0), "army_1"
        )
        self.assertIsNotNone(unit1)
        
        # Спробувати створити другий юніт в тій же позиції
        unit2 = self.placement_manager.create_unit(
            "warrior", (10.0, 10.0), "army_1"
        )
        
        # Другий юніт не повинен бути створений або повинен бути зміщений
        if unit2:
            self.assertNotEqual(unit2.position, (10.0, 10.0))
    
    def test_formation_creation(self):
        """Тест створення формації"""
        formation = self.placement_manager.create_formation(
            "test_formation",
            FormationType.LINE,
            (10.0, 10.0),
            spacing=2.0
        )
        
        self.assertIsNotNone(formation)
        self.assertEqual(formation.formation_type, FormationType.LINE)
        self.assertEqual(formation.center, (10.0, 10.0))
        self.assertEqual(formation.spacing, 2.0)
    
    def test_formation_positions(self):
        """Тест генерації позицій формації"""
        formation = self.placement_manager.create_formation(
            "test_formation",
            FormationType.LINE,
            (10.0, 10.0),
            spacing=2.0
        )
        
        positions = formation.get_formation_positions(3)
        
        self.assertEqual(len(positions), 3)
        
        # Перевірити що позиції розташовані лінійно
        for i, pos in enumerate(positions):
            expected_x = 10.0 + (i - 1) * 2.0  # Центр + зміщення
            self.assertAlmostEqual(pos[0], expected_x, places=1)
            self.assertAlmostEqual(pos[1], 10.0, places=1)
    
    def test_formation_placement(self):
        """Тест розміщення юнітів у формації"""
        formation = self.placement_manager.create_formation(
            "test_formation",
            FormationType.LINE,
            (10.0, 10.0),
            spacing=2.0
        )
        
        units = self.placement_manager.place_units_in_formation(
            "test_formation",
            "warrior",
            3,
            "army_1"
        )
        
        self.assertEqual(len(units), 3)
        
        # Перевірити що всі юніти належать до формації
        for unit in units:
            self.assertEqual(unit.formation_id, "test_formation")
            self.assertEqual(unit.army_id, "army_1")
    
    def test_formation_movement(self):
        """Тест переміщення формації"""
        formation = self.placement_manager.create_formation(
            "test_formation",
            FormationType.LINE,
            (10.0, 10.0),
            spacing=2.0
        )
        
        # Розмістити юнітів
        units = self.placement_manager.place_units_in_formation(
            "test_formation",
            "warrior",
            2,
            "army_1"
        )
        
        # Перемістити формацію
        self.placement_manager.move_formation("test_formation", (20.0, 20.0))
        
        # Перевірити що центр формації змінився
        self.assertEqual(formation.center, (20.0, 20.0))
        
        # Перевірити що юніти також перемістилися
        for unit in units:
            # Юніти повинні бути близько до нового центру
            distance = math.sqrt(
                (unit.position[0] - 20.0)**2 + (unit.position[1] - 20.0)**2
            )
            self.assertLess(distance, 5.0)  # Допустима похибка


class TestUnitMovement(unittest.TestCase):
    """Тести для системи руху юнітів"""
    
    def setUp(self):
        """Налаштування перед кожним тестом"""
        self.grid = Grid(20, 20, 1.0)
        self.placement_manager = UnitPlacementManager()
        self.movement_controller = UnitMovementController(self.grid, self.placement_manager)
    
    def test_unit_movement(self):
        """Тест руху юніта"""
        # Створити юніт
        unit = self.placement_manager.create_unit(
            "warrior", (5.0, 5.0), "army_1"
        )
        
        # Перемістити юніта
        success = self.movement_controller.move_unit_to(unit.unit_id, (15.0, 15.0))
        
        self.assertTrue(success)
        self.assertEqual(self.movement_controller.get_unit_state(unit.unit_id).value, "moving")
    
    def test_formation_movement(self):
        """Тест руху формації"""
        # Створити формацію
        formation = self.placement_manager.create_formation(
            "test_formation",
            FormationType.LINE,
            (5.0, 5.0),
            spacing=2.0
        )
        
        # Розмістити юнітів
        units = self.placement_manager.place_units_in_formation(
            "test_formation",
            "warrior",
            2,
            "army_1"
        )
        
        # Перемістити формацію
        success = self.movement_controller.move_formation_to("test_formation", (15.0, 15.0))
        
        self.assertTrue(success)
        
        # Перевірити що центр формації змінився
        self.assertEqual(formation.center, (15.0, 15.0))
    
    def test_movement_update(self):
        """Тест оновлення руху"""
        # Створити юніт
        unit = self.placement_manager.create_unit(
            "warrior", (5.0, 5.0), "army_1"
        )
        
        # Почати рух
        self.movement_controller.move_unit_to(unit.unit_id, (15.0, 15.0))
        
        # Симулювати кілька кроків оновлення
        for _ in range(10):
            self.movement_controller.update_movement(0.016)  # 60 FPS
        
        # Юніт повинен рухатися
        self.assertTrue(self.movement_controller.is_unit_moving(unit.unit_id))
    
    def test_obstacle_avoidance_movement(self):
        """Тест обходу перешкод під час руху"""
        # Додати перешкоди
        for x in range(8, 12):
            for y in range(8, 12):
                self.grid.set_obstacle(x, y)
        
        # Створити юніт
        unit = self.placement_manager.create_unit(
            "warrior", (5.0, 5.0), "army_1"
        )
        
        # Перемістити через перешкоди
        success = self.movement_controller.move_unit_to(unit.unit_id, (15.0, 15.0))
        
        self.assertTrue(success)
        
        # Симулювати рух
        for _ in range(50):
            self.movement_controller.update_movement(0.016)
        
        # Юніт повинен досягти цілі або бути близько до неї
        final_distance = math.sqrt(
            (unit.position[0] - 15.0)**2 + (unit.position[1] - 15.0)**2
        )
        self.assertLess(final_distance, 2.0)  # Допустима похибка


class TestIntegration(unittest.TestCase):
    """Інтеграційні тести"""
    
    def test_full_scenario(self):
        """Тест повного сценарію"""
        # Створити сітку з перешкодами
        grid = Grid(30, 30, 1.0)
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
        
        self.assertIsNotNone(army1_formation)
        self.assertIsNotNone(army2_formation)
        
        # Перемістити армії назустріч одна одній
        movement_controller.move_formation_to(army1_formation, (15.0, 15.0))
        movement_controller.move_formation_to(army2_formation, (15.0, 15.0))
        
        # Симулювати битву
        for _ in range(100):
            movement_controller.update_movement(0.016)
            formation_controller.maintain_formation_during_movement(army1_formation)
            formation_controller.maintain_formation_during_movement(army2_formation)
        
        # Перевірити що армії наблизилися
        army1_center = placement_manager.formations[army1_formation].center
        army2_center = placement_manager.formations[army2_formation].center
        
        distance = math.sqrt(
            (army1_center[0] - army2_center[0])**2 + 
            (army1_center[1] - army2_center[1])**2
        )
        
        self.assertLess(distance, 10.0)  # Армії повинні наблизитися


def run_performance_tests():
    """Запустити тести продуктивності"""
    print("=== Тести продуктивності ===")
    
    # Тест pathfinding на великій сітці
    print("Тест pathfinding на сітці 100x100...")
    start_time = time.time()
    
    grid = Grid(100, 100, 1.0)
    pathfinder = Pathfinder(grid)
    
    # Додати випадкові перешкоди
    import random
    for _ in range(1000):
        x = random.randint(0, 99)
        y = random.randint(0, 99)
        grid.set_obstacle(x, y)
    
    # Знайти шлях
    path = pathfinder.find_path((1.0, 1.0), (99.0, 99.0), PathfindingAlgorithm.A_STAR)
    
    end_time = time.time()
    print(f"Час виконання: {end_time - start_time:.3f} секунд")
    print(f"Довжина шляху: {len(path)} кроків")
    
    # Тест розміщення багатьох юнітів
    print("\nТест розміщення 1000 юнітів...")
    start_time = time.time()
    
    placement_manager = UnitPlacementManager()
    units_created = 0
    
    for i in range(1000):
        x = random.uniform(0, 50)
        y = random.uniform(0, 50)
        unit = placement_manager.create_unit("warrior", (x, y), "army_1")
        if unit:
            units_created += 1
    
    end_time = time.time()
    print(f"Час виконання: {end_time - start_time:.3f} секунд")
    print(f"Юнітів створено: {units_created}")


if __name__ == "__main__":
    # Запустити unit тести
    print("=== Unit тести ===")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Запустити тести продуктивності
    print("\n")
    run_performance_tests()