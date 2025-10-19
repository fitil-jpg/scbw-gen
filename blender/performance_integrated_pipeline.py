#!/usr/bin/env python3
"""
Інтегрований пайплайн рендерингу з розширеним управлінням продуктивністю
Performance-Integrated Render Pipeline with Advanced Performance Management

Цей модуль інтегрує розширений менеджер продуктивності з існуючим Blender пайплайном,
забезпечуючи оптимальне використання GPU/CPU ресурсів, денойз, тайли, адаптивне семплування та LOD.
"""

import bpy
import bpy_extras
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import mathutils
from mathutils import Vector, Color
import numpy as np
import time
import json

# Імпорт розширеного менеджера продуктивності
import sys
sys.path.append(str(Path(__file__).parent.parent))
from algorithms.advanced_performance_manager import (
    AdvancedPerformanceManager, 
    PerformanceMetrics,
    DeviceInfo,
    TileInfo
)

LOG = logging.getLogger(__name__)


class PerformanceIntegratedRenderPass:
    """Рендер пас з інтегрованим управлінням продуктивністю"""
    
    def __init__(self, name: str, output_path: Path, performance_manager: AdvancedPerformanceManager):
        self.name = name
        self.output_path = output_path
        self.performance_manager = performance_manager
        self.render_settings = {}
        self.quality_settings = {}
    
    def setup_performance_optimized_render(self, scene: bpy.types.Scene, 
                                         target_fps: float = 30.0) -> Dict[str, Any]:
        """Налаштувати рендеринг з оптимізацією продуктивності"""
        
        # Отримати рекомендації по оптимізації
        optimization_recs = self.performance_manager.optimize_settings(target_fps)
        
        # Налаштувати рендер двигун
        engine = self._get_optimal_render_engine(optimization_recs)
        self._setup_render_engine(scene, engine, optimization_recs)
        
        # Налаштувати адаптивне семплування
        self._setup_adaptive_sampling(scene, optimization_recs)
        
        # Налаштувати денойз
        self._setup_denoising(scene, optimization_recs)
        
        # Налаштувати LOD
        self._setup_lod_settings(scene, optimization_recs)
        
        # Налаштувати тайли
        self._setup_tiling(scene, optimization_recs)
        
        return optimization_recs
    
    def _get_optimal_render_engine(self, optimization_recs: Dict[str, Any]) -> str:
        """Визначити оптимальний рендер двигун"""
        
        # Перевірити доступність GPU
        if self.performance_manager.gpu_manager and self.performance_manager.gpu_manager.gpus:
            gpu_available = any(gpu.is_available for gpu in self.performance_manager.gpu_manager.gpus)
        else:
            gpu_available = False
        
        # Рекомендації по двигуну
        if gpu_available and not optimization_recs.get('reduce_samples', False):
            return 'CYCLES'  # GPU-прискорений
        else:
            return 'BLENDER_EEVEE'  # Швидший для CPU
    
    def _setup_render_engine(self, scene: bpy.types.Scene, engine: str, 
                           optimization_recs: Dict[str, Any]):
        """Налаштувати рендер двигун"""
        
        scene.render.engine = engine
        
        if engine == 'CYCLES':
            self._setup_cycles_optimized(scene, optimization_recs)
        elif engine == 'BLENDER_EEVEE':
            self._setup_eevee_optimized(scene, optimization_recs)
    
    def _setup_cycles_optimized(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати Cycles з оптимізацією"""
        
        cycles = scene.cycles
        
        # Адаптивні семпли
        base_samples = optimization_recs.get('base_samples', 128)
        cycles.samples = base_samples
        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.01
        cycles.adaptive_min_samples = max(0, base_samples // 4)
        
        # Денойз
        if optimization_recs.get('enable_denoising', True):
            cycles.use_denoising = True
            cycles.denoiser = 'OPTIX' if bpy.app.version >= (3, 0, 0) else 'NLM'
            cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        
        # Налаштування якості
        cycles.max_bounces = 8 if optimization_recs.get('reduce_samples', False) else 12
        cycles.diffuse_bounces = 3 if optimization_recs.get('reduce_samples', False) else 4
        cycles.glossy_bounces = 3 if optimization_recs.get('reduce_samples', False) else 4
        cycles.transmission_bounces = 8 if optimization_recs.get('reduce_samples', False) else 12
        cycles.volume_bounces = 1 if optimization_recs.get('reduce_samples', False) else 2
        
        # Налаштування пристрою
        if self.performance_manager.gpu_manager and self.performance_manager.gpu_manager.gpus:
            cycles.device = 'GPU'
            # Налаштувати конкретний GPU якщо доступно
            available_gpu = self.performance_manager.gpu_manager.get_available_gpu()
            if available_gpu:
                cycles.device = 'GPU'
        else:
            cycles.device = 'CPU'
        
        # Налаштування тайлів
        if optimization_recs.get('enable_tiling', False):
            cycles.tile_size = optimization_recs.get('tile_size', 128)
        else:
            cycles.tile_size = 256
    
    def _setup_eevee_optimized(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати Eevee з оптимізацією"""
        
        eevee = scene.eevee
        
        # Налаштування семплів
        base_samples = optimization_recs.get('base_samples', 64)
        eevee.taa_render_samples = min(base_samples, 128)  # Eevee має обмеження
        eevee.taa_samples = min(base_samples // 4, 32)
        
        # Налаштування якості
        if optimization_recs.get('reduce_samples', False):
            eevee.use_bloom = False
            eevee.use_ssr = False
            eevee.use_ssao = False
            eevee.shadow_cascade_size = '512'
            eevee.shadow_cascade_count = 2
        else:
            eevee.use_bloom = True
            eevee.use_ssr = True
            eevee.use_ssao = True
            eevee.shadow_cascade_size = '1024'
            eevee.shadow_cascade_count = 4
        
        # Налаштування тіней
        eevee.use_soft_shadows = not optimization_recs.get('reduce_samples', False)
        
        # Налаштування кольору
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'None'
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
    
    def _setup_adaptive_sampling(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати адаптивне семплування"""
        
        if scene.render.engine == 'CYCLES':
            cycles = scene.cycles
            cycles.use_adaptive_sampling = True
            cycles.adaptive_threshold = 0.01
            cycles.adaptive_min_samples = max(0, cycles.samples // 4)
    
    def _setup_denoising(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати денойз"""
        
        if scene.render.engine == 'CYCLES' and optimization_recs.get('enable_denoising', True):
            cycles = scene.cycles
            cycles.use_denoising = True
            
            # Вибір алгоритму денойзу
            denoising_algorithm = optimization_recs.get('denoising_algorithm', 'OPTIX')
            if denoising_algorithm == 'OPTIX' and bpy.app.version >= (3, 0, 0):
                cycles.denoiser = 'OPTIX'
            else:
                cycles.denoiser = 'NLM'
            
            cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    
    def _setup_lod_settings(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати LOD"""
        
        if optimization_recs.get('enable_lod', False):
            # Налаштувати LOD для об'єктів сцени
            for obj in scene.objects:
                if obj.type == 'MESH':
                    # Додати модифікатор LOD якщо потрібно
                    if 'LOD' not in obj.modifiers:
                        lod_modifier = obj.modifiers.new(name='LOD', type='DECIMATE')
                        lod_modifier.decimate_type = 'COLLAPSE'
                        lod_modifier.ratio = 0.8  # Зменшити на 20%
    
    def _setup_tiling(self, scene: bpy.types.Scene, optimization_recs: Dict[str, Any]):
        """Налаштувати тайлинг"""
        
        if optimization_recs.get('enable_tiling', False):
            if scene.render.engine == 'CYCLES':
                cycles = scene.cycles
                cycles.tile_size = optimization_recs.get('tile_size', 128)
            
            # Налаштувати рендеринг по тайлах
            resolution = scene.render.resolution_x, scene.render.resolution_y
            tile_size = optimization_recs.get('tile_size', 128)
            self.performance_manager.setup_tile_rendering(resolution[0], resolution[1], tile_size)


class PerformanceIntegratedMultiPassRenderer:
    """Мульти-пас рендерер з інтегрованим управлінням продуктивністю"""
    
    def __init__(self, output_directory: Path, performance_manager: AdvancedPerformanceManager):
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.performance_manager = performance_manager
        
        # Стандартні паси з оптимізацією
        self.default_passes = [
            'beauty', 'mask_units', 'mask_buildings', 'mask_terrain',
            'depth', 'normal', 'ao', 'emission'
        ]
    
    def create_performance_optimized_passes(self, shot_id: str, frame: int = 1,
                                          custom_passes: Optional[List[str]] = None,
                                          target_fps: float = 30.0) -> List[PerformanceIntegratedRenderPass]:
        """Створити оптимізовані рендер паси"""
        
        passes = []
        passes_to_create = custom_passes or self.default_passes
        
        for pass_name in passes_to_create:
            if pass_name == 'beauty':
                beauty_path = self.output_directory / f"{shot_id}_beauty_{frame:04d}.png"
                pass_obj = PerformanceIntegratedRenderPass("beauty", beauty_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'mask_units':
                mask_path = self.output_directory / f"{shot_id}_mask_units_{frame:04d}.png"
                pass_obj = PerformanceIntegratedRenderPass("mask_units", mask_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'mask_buildings':
                mask_path = self.output_directory / f"{shot_id}_mask_buildings_{frame:04d}.png"
                pass_obj = PerformanceIntegratedRenderPass("mask_buildings", mask_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'mask_terrain':
                mask_path = self.output_directory / f"{shot_id}_mask_terrain_{frame:04d}.png"
                pass_obj = PerformanceIntegratedRenderPass("mask_terrain", mask_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'depth':
                depth_path = self.output_directory / f"{shot_id}_depth_{frame:04d}.exr"
                pass_obj = PerformanceIntegratedRenderPass("depth", depth_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'normal':
                normal_path = self.output_directory / f"{shot_id}_normal_{frame:04d}.exr"
                pass_obj = PerformanceIntegratedRenderPass("normal", normal_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'ao':
                ao_path = self.output_directory / f"{shot_id}_ao_{frame:04d}.exr"
                pass_obj = PerformanceIntegratedRenderPass("ao", ao_path, self.performance_manager)
                passes.append(pass_obj)
            
            elif pass_name == 'emission':
                emission_path = self.output_directory / f"{shot_id}_emission_{frame:04d}.exr"
                pass_obj = PerformanceIntegratedRenderPass("emission", emission_path, self.performance_manager)
                passes.append(pass_obj)
        
        return passes
    
    def render_performance_optimized_passes(self, shot_id: str, frame: int = 1,
                                          custom_passes: Optional[List[str]] = None,
                                          target_fps: float = 30.0) -> Dict[str, Path]:
        """Рендерити оптимізовані паси"""
        
        passes = self.create_performance_optimized_passes(shot_id, frame, custom_passes, target_fps)
        rendered_paths = {}
        
        for pass_obj in passes:
            LOG.info(f"Рендеринг пасу з оптимізацією: {pass_obj.name}")
            
            # Налаштувати рендеринг з оптимізацією
            optimization_recs = pass_obj.setup_performance_optimized_render(bpy.context.scene, target_fps)
            
            # Налаштувати специфічні параметри пасу
            self._setup_pass_specific_settings(pass_obj, bpy.context.scene)
            
            # Встановити шлях виводу
            bpy.context.scene.render.filepath = str(pass_obj.output_path.parent / pass_obj.output_path.stem)
            
            # Рендеринг з моніторингом продуктивності
            start_time = time.time()
            bpy.ops.render.render(write_still=True)
            render_time = time.time() - start_time
            
            # Оновити метрики продуктивності
            self._update_performance_metrics(pass_obj.name, render_time, optimization_recs)
            
            rendered_paths[pass_obj.name] = pass_obj.output_path
        
        return rendered_paths
    
    def _setup_pass_specific_settings(self, pass_obj: PerformanceIntegratedRenderPass, scene: bpy.types.Scene):
        """Налаштувати специфічні параметри пасу"""
        
        if pass_obj.name == 'beauty':
            # Красивий пас - повна якість
            pass
        
        elif pass_obj.name.startswith('mask_'):
            # Маски - швидкий рендеринг
            scene.cycles.samples = 1
            scene.cycles.use_denoising = False
            scene.cycles.use_adaptive_sampling = False
        
        elif pass_obj.name == 'depth':
            # Глибина - середня якість
            scene.cycles.samples = 64
            scene.cycles.use_denoising = False
        
        elif pass_obj.name in ['normal', 'ao', 'emission']:
            # Допоміжні паси - середня якість
            scene.cycles.samples = 128
            scene.cycles.use_denoising = False
    
    def _update_performance_metrics(self, pass_name: str, render_time: float, 
                                  optimization_recs: Dict[str, Any]):
        """Оновити метрики продуктивності"""
        
        # Оновити метрики в менеджері продуктивності
        self.performance_manager.current_metrics.generation_time = render_time
        self.performance_manager.current_metrics.adaptive_samples = optimization_recs.get('base_samples', 128)
        
        # Зберегти в історію
        self.performance_manager.performance_history.append(self.performance_manager.current_metrics)


class PerformanceIntegratedPipeline:
    """Головний клас інтегрованого пайплайну з управлінням продуктивністю"""
    
    def __init__(self, output_directory: str = "renders/performance_optimized"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Ініціалізація менеджера продуктивності
        self.performance_manager = AdvancedPerformanceManager(
            enable_gpu=True, 
            enable_monitoring=True
        )
        
        # Ініціалізація рендерера
        self.renderer = PerformanceIntegratedMultiPassRenderer(
            self.output_directory, 
            self.performance_manager
        )
        
        LOG.info("Інтегрований пайплайн з управлінням продуктивністю ініціалізовано")
    
    def render_shot_optimized(self, shot_id: str, frame: int = 1,
                            custom_passes: Optional[List[str]] = None,
                            target_fps: float = 30.0,
                            quality_preset: str = 'balanced') -> Dict[str, Any]:
        """Рендерити шот з оптимізацією продуктивності"""
        
        LOG.info(f"Рендеринг шоту {shot_id} з оптимізацією (FPS: {target_fps}, Quality: {quality_preset})")
        
        # Налаштувати якість на основі пресету
        quality_settings = self._get_quality_preset(quality_preset)
        
        # Рендерити паси
        rendered_paths = self.renderer.render_performance_optimized_passes(
            shot_id, frame, custom_passes, target_fps
        )
        
        # Отримати звіт про продуктивність
        performance_report = self.performance_manager.get_performance_report()
        
        # Створити маніфест рендерингу
        manifest = self._create_performance_manifest(shot_id, frame, rendered_paths, performance_report)
        
        # Зберегти маніфест
        manifest_path = self.output_directory / shot_id / "performance_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        LOG.info(f"Рендеринг завершено: {len(rendered_paths)} пасів")
        return manifest
    
    def _get_quality_preset(self, preset: str) -> Dict[str, Any]:
        """Отримати налаштування якості для пресету"""
        
        presets = {
            'draft': {
                'base_samples': 32,
                'enable_denoising': False,
                'enable_tiling': True,
                'tile_size': 64,
                'enable_lod': True,
                'reduce_samples': True
            },
            'balanced': {
                'base_samples': 128,
                'enable_denoising': True,
                'enable_tiling': True,
                'tile_size': 128,
                'enable_lod': True,
                'reduce_samples': False
            },
            'high': {
                'base_samples': 256,
                'enable_denoising': True,
                'enable_tiling': False,
                'tile_size': 256,
                'enable_lod': False,
                'reduce_samples': False
            },
            'ultra': {
                'base_samples': 512,
                'enable_denoising': True,
                'enable_tiling': False,
                'tile_size': 512,
                'enable_lod': False,
                'reduce_samples': False
            }
        }
        
        return presets.get(preset, presets['balanced'])
    
    def _create_performance_manifest(self, shot_id: str, frame: int, 
                                   rendered_paths: Dict[str, Path],
                                   performance_report: Dict[str, Any]) -> Dict[str, Any]:
        """Створити маніфест з метриками продуктивності"""
        
        manifest = {
            'shot_id': shot_id,
            'frame': frame,
            'render_timestamp': time.time(),
            'render_engine': bpy.context.scene.render.engine,
            'resolution': [
                bpy.context.scene.render.resolution_x,
                bpy.context.scene.render.resolution_y
            ],
            'performance_metrics': performance_report['current_metrics'],
            'system_info': performance_report['system_info'],
            'recommendations': performance_report.get('recommendations', []),
            'sampling_recommendations': performance_report.get('sampling_recommendations', {}),
            'lod_statistics': performance_report.get('lod_statistics', {}),
            'passes': {}
        }
        
        # Додати інформацію про паси
        for pass_name, path in rendered_paths.items():
            manifest['passes'][pass_name] = {
                'path': str(path),
                'format': path.suffix[1:].upper(),
                'size_bytes': path.stat().st_size if path.exists() else 0
            }
        
        return manifest
    
    def batch_render_optimized(self, shots_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Пакетний рендеринг з оптимізацією"""
        
        LOG.info(f"Пакетний рендеринг {len(shots_config)} шотів з оптимізацією")
        
        results = {}
        total_start_time = time.time()
        
        for i, shot_config in enumerate(shots_config):
            shot_id = shot_config.get('shot_id', f'shot_{i}')
            frame = shot_config.get('frame', 1)
            target_fps = shot_config.get('target_fps', 30.0)
            quality_preset = shot_config.get('quality_preset', 'balanced')
            custom_passes = shot_config.get('passes', None)
            
            LOG.info(f"Рендеринг шоту {i+1}/{len(shots_config)}: {shot_id}")
            
            try:
                result = self.render_shot_optimized(
                    shot_id, frame, custom_passes, target_fps, quality_preset
                )
                results[shot_id] = result
                
            except Exception as e:
                LOG.error(f"Помилка рендерингу шоту {shot_id}: {e}")
                results[shot_id] = {'error': str(e)}
        
        total_time = time.time() - total_start_time
        
        # Створити загальний звіт
        batch_report = {
            'total_shots': len(shots_config),
            'successful_shots': len([r for r in results.values() if 'error' not in r]),
            'failed_shots': len([r for r in results.values() if 'error' in r]),
            'total_time': total_time,
            'average_time_per_shot': total_time / len(shots_config),
            'results': results
        }
        
        # Зберегти загальний звіт
        batch_report_path = self.output_directory / "batch_render_report.json"
        with open(batch_report_path, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False)
        
        LOG.info(f"Пакетний рендеринг завершено за {total_time:.2f}s")
        return batch_report
    
    def get_performance_recommendations(self) -> List[str]:
        """Отримати рекомендації по оптимізації продуктивності"""
        
        return self.performance_manager.performance_monitor.get_performance_recommendations()
    
    def optimize_for_target_fps(self, target_fps: float) -> Dict[str, Any]:
        """Оптимізувати налаштування для досягнення цільового FPS"""
        
        return self.performance_manager.optimize_settings(target_fps)
    
    def cleanup(self):
        """Очистити ресурси"""
        
        self.performance_manager.cleanup()
        LOG.info("Ресурси інтегрованого пайплайну очищено")


def create_performance_optimized_scene():
    """Створити сцену з оптимізацією продуктивності"""
    
    # Очистити сцену
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Створити базову сцену
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "SCBW_Test_Cube"
    
    # Додати матеріал
    mat = bpy.data.materials.new(name="SCBW_Test_Material")
    mat.use_nodes = True
    cube.data.materials.append(mat)
    
    # Додати освітлення
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.name = "SCBW_Sun_Light"
    sun.data.energy = 3.0
    
    # Налаштувати камеру
    bpy.ops.object.camera_add(location=(5, -5, 5))
    camera = bpy.context.active_object
    camera.name = "SCBW_Camera"
    camera.rotation_euler = (mathutils.radians(60), 0, mathutils.radians(45))
    
    # Встановити активну камеру
    bpy.context.scene.camera = camera
    
    # Налаштувати рендеринг
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    LOG.info("Тестова сцена створена з оптимізацією продуктивності")


def benchmark_performance_integrated_pipeline():
    """Бенчмарк інтегрованого пайплайну"""
    
    print("Бенчмарк інтегрованого пайплайну з управлінням продуктивністю...")
    
    # Створити тестову сцену
    create_performance_optimized_scene()
    
    # Ініціалізація пайплайну
    pipeline = PerformanceIntegratedPipeline("renders/performance_benchmark")
    
    # Тестові конфігурації
    test_configs = [
        {
            'shot_id': 'test_draft',
            'frame': 1,
            'target_fps': 60.0,
            'quality_preset': 'draft',
            'passes': ['beauty', 'depth']
        },
        {
            'shot_id': 'test_balanced',
            'frame': 1,
            'target_fps': 30.0,
            'quality_preset': 'balanced',
            'passes': ['beauty', 'depth', 'normal']
        },
        {
            'shot_id': 'test_high',
            'frame': 1,
            'target_fps': 15.0,
            'quality_preset': 'high',
            'passes': ['beauty', 'depth', 'normal', 'ao']
        }
    ]
    
    # Пакетний рендеринг
    results = pipeline.batch_render_optimized(test_configs)
    
    # Вивести результати
    print(f"\nРезультати бенчмарку:")
    print(f"  Загальний час: {results['total_time']:.2f}s")
    print(f"  Успішних шотів: {results['successful_shots']}")
    print(f"  Невдалих шотів: {results['failed_shots']}")
    print(f"  Середній час на шот: {results['average_time_per_shot']:.2f}s")
    
    # Рекомендації
    recommendations = pipeline.get_performance_recommendations()
    if recommendations:
        print(f"\nРекомендації по оптимізації:")
        for rec in recommendations:
            print(f"  - {rec}")
    
    # Очистити ресурси
    pipeline.cleanup()
    
    print("\nБенчмарк завершено!")


if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Запустити бенчмарк
    benchmark_performance_integrated_pipeline()