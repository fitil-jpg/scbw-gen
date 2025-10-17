#!/usr/bin/env python3
"""
Integrated Scene Generator for StarCraft Maps
Інтегрований генератор сцен для карт StarCraft

This module demonstrates how to use all the advanced algorithms together
to generate complete StarCraft map scenes with optimal performance.
"""

import time
import random
from typing import List, Tuple, Dict, Any
from pathlib import Path

# Import all algorithm modules
from terrain_generator import TerrainGenerator, TerrainType, create_sample_terrain
from unit_placement import (
    FormationGenerator, TacticalAnalyzer, UnitPlacementOptimizer,
    FormationType, UnitType, FormationConfig, create_sample_army
)
from building_placement import (
    BaseLayoutGenerator, StrategicAnalyzer, BaseLayoutOptimizer,
    BuildingType, create_sample_strategic_analyzer
)
from pathfinding import (
    PathfindingGrid, AStarPathfinder, FormationPathfinder,
    StrategicPathPlanner, create_sample_pathfinding_grid
)
from scene_composition import (
    SceneComposer, CameraType, LightingType, WeatherType,
    create_sample_scene_data
)
from performance_optimizer import (
    OptimizedTerrainGenerator, PerformanceProfiler, PerformanceMetrics
)


class IntegratedSceneGenerator:
    """Інтегрований генератор сцен"""
    
    def __init__(self, 
                 scene_width: float = 100.0, 
                 scene_height: float = 100.0,
                 enable_optimizations: bool = True):
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.enable_optimizations = enable_optimizations
        
        # Ініціалізація компонентів
        self._initialize_components()
        
        # Профілер продуктивності
        self.profiler = PerformanceProfiler()
    
    def _initialize_components(self):
        """Ініціалізувати всі компоненти"""
        
        # Генератор рельєфу
        if self.enable_optimizations:
            self.terrain_generator = OptimizedTerrainGenerator(
                int(self.scene_width), int(self.scene_height), True
            )
        else:
            self.terrain_generator = TerrainGenerator(
                int(self.scene_width), int(self.scene_height)
            )
        
        # Аналізатори
        self.tactical_analyzer = TacticalAnalyzer(self.scene_width, self.scene_height)
        self.strategic_analyzer = create_sample_strategic_analyzer()
        
        # Генератори
        self.formation_generator = FormationGenerator(self.tactical_analyzer)
        self.building_generator = BaseLayoutGenerator(self.strategic_analyzer)
        self.scene_composer = SceneComposer(self.scene_width, self.scene_height)
        
        # Оптимізатори
        self.unit_optimizer = UnitPlacementOptimizer(self.tactical_analyzer)
        self.building_optimizer = BaseLayoutOptimizer(self.strategic_analyzer)
        
        # Пошук шляхів
        self.pathfinding_grid = create_sample_pathfinding_grid()
        self.astar_pathfinder = AStarPathfinder(self.pathfinding_grid)
        self.formation_pathfinder = FormationPathfinder(self.pathfinding_grid)
        self.strategic_planner = StrategicPathPlanner(self.pathfinding_grid)
    
    def generate_complete_scene(self, 
                               scene_type: str = "battle",
                               army_size: int = 20,
                               building_count: int = 8,
                               enable_pathfinding: bool = True) -> Dict[str, Any]:
        """Згенерувати повну сцену"""
        
        print(f"Генерація {scene_type} сцени...")
        self.profiler.start_timer("total_generation")
        
        # 1. Генерація рельєфу
        print("  Генерація рельєфу...")
        self.profiler.start_timer("terrain_generation")
        terrain_data = self._generate_terrain()
        self.profiler.end_timer("terrain_generation")
        
        # 2. Генерація армій
        print("  Генерація армій...")
        self.profiler.start_timer("army_generation")
        armies = self._generate_armies(army_size)
        self.profiler.end_timer("army_generation")
        
        # 3. Генерація будівель
        print("  Генерація будівель...")
        self.profiler.start_timer("building_generation")
        buildings = self._generate_buildings(building_count)
        self.profiler.end_timer("building_generation")
        
        # 4. Пошук шляхів (опціонально)
        paths = {}
        if enable_pathfinding:
            print("  Планування шляхів...")
            self.profiler.start_timer("pathfinding")
            paths = self._generate_paths(armies)
            self.profiler.end_timer("pathfinding")
        
        # 5. Композиція сцени
        print("  Композиція сцени...")
        self.profiler.start_timer("scene_composition")
        scene_config = self._compose_scene(scene_type, armies, buildings)
        self.profiler.end_timer("scene_composition")
        
        # Завершити загальний таймер
        total_time = self.profiler.end_timer("total_generation")
        
        # Зібрати результати
        result = {
            'scene_type': scene_type,
            'terrain': terrain_data,
            'armies': armies,
            'buildings': buildings,
            'paths': paths,
            'scene_config': scene_config,
            'performance_metrics': self._get_performance_metrics(),
            'generation_time': total_time
        }
        
        print(f"Генерація завершена за {total_time:.2f} секунд")
        return result
    
    def _generate_terrain(self) -> Dict[str, Any]:
        """Згенерувати рельєф"""
        
        if self.enable_optimizations:
            # Використати оптимізований генератор
            height_map = self.terrain_generator.generate_terrain_optimized(
                octaves=6,
                persistence=0.5,
                use_lod=True
            )
        else:
            # Використати стандартний генератор
            terrain_gen = create_sample_terrain(
                int(self.scene_width), int(self.scene_height)
            )
            height_map = terrain_gen.height_map
        
        # Додати стратегічні особливості
        self.tactical_analyzer.add_high_ground(20, 20, 15.0)
        self.tactical_analyzer.add_high_ground(80, 80, 15.0)
        self.tactical_analyzer.add_chokepoint(50, 30, 5.0)
        self.tactical_analyzer.add_chokepoint(50, 70, 5.0)
        
        return {
            'height_map': height_map,
            'width': self.scene_width,
            'height': self.scene_height
        }
    
    def _generate_armies(self, army_size: int) -> List[Dict[str, Any]]:
        """Згенерувати армії"""
        
        armies = []
        
        # Армія 1 (синя)
        army1_units = create_sample_army()[:army_size//2]
        army1_config = FormationConfig(
            formation_type=FormationType.TACTICAL,
            spacing=2.0,
            center_position=(30, 30)
        )
        
        army1_positions = self.formation_generator.generate_formation(
            army1_units, army1_config
        )
        
        # Оптимізувати позиції
        optimized_positions = self.unit_optimizer.optimize_formation(
            army1_units, army1_positions, iterations=50
        )
        
        armies.append({
            'id': 'army_1',
            'color': (0.2, 0.4, 0.8),
            'units': army1_units,
            'positions': optimized_positions,
            'center': (30, 30)
        })
        
        # Армія 2 (червона)
        army2_units = create_sample_army()[:army_size//2]
        army2_config = FormationConfig(
            formation_type=FormationType.TACTICAL,
            spacing=2.0,
            center_position=(70, 70)
        )
        
        army2_positions = self.formation_generator.generate_formation(
            army2_units, army2_config
        )
        
        # Оптимізувати позиції
        optimized_positions = self.unit_optimizer.optimize_formation(
            army2_units, army2_positions, iterations=50
        )
        
        armies.append({
            'id': 'army_2',
            'color': (0.8, 0.2, 0.2),
            'units': army2_units,
            'positions': optimized_positions,
            'center': (70, 70)
        })
        
        return armies
    
    def _generate_buildings(self, building_count: int) -> List[Dict[str, Any]]:
        """Згенерувати будівлі"""
        
        buildings = []
        
        # База 1
        base1_layout = self.building_generator.generate_base_layout(
            center_position=(25, 25),
            owner="army_1",
            base_size=20.0
        )
        
        # Оптимізувати макет
        optimized_base1 = self.building_optimizer.optimize_base_layout(
            base1_layout, iterations=30
        )
        
        buildings.append({
            'id': 'base_1',
            'owner': 'army_1',
            'layout': optimized_base1
        })
        
        # База 2
        base2_layout = self.building_generator.generate_base_layout(
            center_position=(75, 75),
            owner="army_2",
            base_size=20.0
        )
        
        # Оптимізувати макет
        optimized_base2 = self.building_optimizer.optimize_base_layout(
            base2_layout, iterations=30
        )
        
        buildings.append({
            'id': 'base_2',
            'owner': 'army_2',
            'layout': optimized_base2
        })
        
        return buildings
    
    def _generate_paths(self, armies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Згенерувати шляхи"""
        
        paths = {}
        
        for army in armies:
            army_id = army['id']
            army_center = army['center']
            
            # Шлях атаки до ворога
            enemy_center = (70, 70) if army_id == 'army_1' else (30, 30)
            
            attack_path = self.strategic_planner.plan_attack_path(
                army_center, enemy_center
            )
            
            # Патрульний шлях
            patrol_points = [
                army_center,
                (army_center[0] + 10, army_center[1]),
                (army_center[0] + 10, army_center[1] + 10),
                (army_center[0], army_center[1] + 10),
                army_center
            ]
            
            patrol_path = self.strategic_planner.plan_patrol_path(
                patrol_points, loop=True
            )
            
            paths[army_id] = {
                'attack_path': attack_path,
                'patrol_path': patrol_path
            }
        
        return paths
    
    def _compose_scene(self, 
                      scene_type: str, 
                      armies: List[Dict[str, Any]], 
                      buildings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Скомпонувати сцену"""
        
        # Підготувати дані для композиції
        important_objects = []
        action_areas = []
        
        # Додати важливі об'єкти
        for army in armies:
            for i, (unit, pos) in enumerate(zip(army['units'], army['positions'])):
                importance = 2.0 if i == 0 else 1.0  # Перший юніт важливіший
                important_objects.append({
                    'position': pos,
                    'importance': importance,
                    'type': 'unit'
                })
        
        # Додати зони дії
        for army in armies:
            action_areas.append({
                'center': army['center'],
                'radius': 15.0,
                'intensity': 2.0
            })
        
        # Скомпонувати сцену
        scene_config = self.scene_composer.compose_scene(
            scene_type=scene_type,
            important_objects=important_objects,
            action_areas=action_areas,
            time_of_day="day",
            weather=WeatherType.CLEAR
        )
        
        return scene_config
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Отримати метрики продуктивності"""
        
        metrics = self.profiler.get_metrics()
        
        if self.enable_optimizations and hasattr(self.terrain_generator, 'get_performance_metrics'):
            terrain_metrics = self.terrain_generator.get_performance_metrics()
            metrics.update({
                'memory_usage_mb': terrain_metrics.memory_usage,
                'cache_hits': terrain_metrics.cache_hits,
                'parallel_tasks': terrain_metrics.parallel_tasks
            })
        
        return metrics
    
    def export_scene(self, 
                    scene_data: Dict[str, Any], 
                    output_dir: str = "generated_scenes"):
        """Експортувати сцену"""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Експортувати рельєф
        terrain = scene_data['terrain']
        if 'height_map' in terrain:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 10))
            plt.imshow(terrain['height_map'], cmap='terrain', origin='lower')
            plt.colorbar(label='Height')
            plt.title('Generated Terrain')
            plt.savefig(output_path / "terrain.png", dpi=150, bbox_inches='tight')
            plt.close()
        
        # Експортувати метрики
        metrics = scene_data['performance_metrics']
        with open(output_path / "metrics.txt", "w") as f:
            f.write("Performance Metrics\n")
            f.write("==================\n\n")
            for key, value in metrics.items():
                f.write(f"{key}: {value}\n")
        
        # Експортувати конфігурацію сцени
        import json
        scene_config = scene_data['scene_config']
        with open(output_path / "scene_config.json", "w") as f:
            # Конвертувати в JSON-сумісний формат
            json_config = {
                'camera': {
                    'position': scene_config['camera'].position,
                    'target': scene_config['camera'].target,
                    'fov': scene_config['camera'].fov,
                    'camera_type': scene_config['camera'].camera_type.value
                },
                'lighting': {
                    'sun_direction': scene_config['lighting'].sun_direction,
                    'sun_intensity': scene_config['lighting'].sun_intensity,
                    'ambient_intensity': scene_config['lighting'].ambient_intensity
                },
                'scene_type': scene_config['scene_type'],
                'time_of_day': scene_config['time_of_day'],
                'weather': scene_config['weather']
            }
            json.dump(json_config, f, indent=2)
        
        print(f"Сцена експортована в {output_path}")
    
    def cleanup(self):
        """Очистити ресурси"""
        if self.enable_optimizations and hasattr(self.terrain_generator, 'cleanup'):
            self.terrain_generator.cleanup()


def main():
    """Головна функція для демонстрації"""
    
    print("=== Інтегрований генератор сцен StarCraft ===\n")
    
    # Створити генератор
    generator = IntegratedSceneGenerator(
        scene_width=100.0,
        scene_height=100.0,
        enable_optimizations=True
    )
    
    try:
        # Генерувати різні типи сцен
        scene_types = ["battle", "peaceful", "dramatic", "cinematic"]
        
        for scene_type in scene_types:
            print(f"\n{'='*50}")
            print(f"Генерація {scene_type.upper()} сцени")
            print(f"{'='*50}")
            
            # Генерувати сцену
            scene_data = generator.generate_complete_scene(
                scene_type=scene_type,
                army_size=16,
                building_count=6,
                enable_pathfinding=True
            )
            
            # Показати метрики
            metrics = scene_data['performance_metrics']
            print(f"\nМетрики продуктивності:")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
            
            # Експортувати сцену
            generator.export_scene(scene_data, f"generated_scenes/{scene_type}")
        
        print(f"\n{'='*50}")
        print("Генерація всіх сцен завершена!")
        print(f"{'='*50}")
        
    finally:
        # Очистити ресурси
        generator.cleanup()


if __name__ == "__main__":
    main()