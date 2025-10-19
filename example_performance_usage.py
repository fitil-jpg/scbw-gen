#!/usr/bin/env python3
"""
Приклад використання розширеного менеджера продуктивності
Example usage of Advanced Performance Manager

Цей скрипт демонструє як використовувати розширений менеджер продуктивності
для оптимізації рендерингу сцен StarCraft.
"""

import sys
import os
from pathlib import Path
import numpy as np
import time
import logging

# Додати шлях до модулів
sys.path.append(str(Path(__file__).parent))

from algorithms.advanced_performance_manager import AdvancedPerformanceManager
from blender.performance_integrated_pipeline import PerformanceIntegratedPipeline

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Базовий приклад використання менеджера продуктивності"""
    
    print("=== Базовий приклад використання менеджера продуктивності ===")
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)
    
    # Створення тестової сцени
    test_scene = np.random.random((512, 512, 3)).astype(np.float32)
    
    # Налаштування рендерингу
    render_settings = {
        'time_budget': 2.0,
        'camera_distance': 150.0,
        'object_complexity': 1.2,
        'camera_speed': 5.0,
        'enable_denoising': True,
        'denoising_algorithm': 'OPTIX',
        'denoising_strength': 1.0
    }
    
    # Налаштування тайлів
    manager.setup_tile_rendering(512, 512, 128)
    
    # Рендеринг з оптимізацією
    print("Рендеринг з оптимізацією продуктивності...")
    start_time = time.time()
    
    result = manager.render_with_optimization(test_scene, render_settings)
    
    render_time = time.time() - start_time
    print(f"Час рендерингу: {render_time:.3f}s")
    
    # Отримання звіту про продуктивність
    report = manager.get_performance_report()
    
    print(f"\nЗвіт про продуктивність:")
    print(f"  Час генерації: {report['current_metrics']['generation_time']:.3f}s")
    print(f"  Використання CPU: {report['current_metrics']['cpu_usage']:.1f}%")
    print(f"  Використання пам'яті: {report['current_metrics']['memory_usage']:.1f}%")
    print(f"  Використання GPU: {report['current_metrics']['gpu_usage']:.1f}%")
    print(f"  Адаптивні семпли: {report['current_metrics']['adaptive_samples']}")
    print(f"  Якість рендерингу: {report['current_metrics']['render_quality']:.2f}")
    print(f"  Оброблено тайлів: {report['current_metrics']['tiles_processed']}")
    
    # Рекомендації
    if 'recommendations' in report and report['recommendations']:
        print(f"\nРекомендації по оптимізації:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    # Очистити ресурси
    manager.cleanup()
    
    print("Базовий приклад завершено!\n")


def example_denoising_comparison():
    """Приклад порівняння алгоритмів денойзу"""
    
    print("=== Порівняння алгоритмів денойзу ===")
    
    # Створення тестового зображення з шумом
    clean_image = np.random.random((256, 256, 3)).astype(np.float32)
    noise = np.random.normal(0, 0.1, clean_image.shape)
    noisy_image = np.clip(clean_image + noise, 0, 1)
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=False)
    
    # Тестування різних алгоритмів денойзу
    algorithms = ['OPTIX', 'OIDN', 'NLM', 'BILATERAL']
    
    for algorithm in algorithms:
        print(f"\nТестування алгоритму: {algorithm}")
        
        start_time = time.time()
        denoised = manager.denoising_manager.denoise_image(
            noisy_image, 
            algorithm=algorithm, 
            strength=1.0
        )
        denoising_time = time.time() - start_time
        
        # Розрахунок метрики якості (PSNR)
        mse = np.mean((clean_image - denoised) ** 2)
        psnr = 20 * np.log10(1.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        print(f"  Час денойзу: {denoising_time:.3f}s")
        print(f"  PSNR: {psnr:.2f} dB")
    
    manager.cleanup()
    print("Порівняння алгоритмів денойзу завершено!\n")


def example_adaptive_sampling():
    """Приклад адаптивного семплування"""
    
    print("=== Адаптивне семплування ===")
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=False, enable_monitoring=False)
    
    # Тестові сцени з різною складністю
    test_scenes = [
        ("Проста сцена", np.random.random((128, 128, 3)).astype(np.float32) * 0.1),
        ("Середня сцена", np.random.random((128, 128, 3)).astype(np.float32) * 0.5),
        ("Складна сцена", np.random.random((128, 128, 3)).astype(np.float32) * 0.9)
    ]
    
    for scene_name, scene_data in test_scenes:
        print(f"\n{scene_name}:")
        
        # Оцінка складності
        complexity = manager._assess_scene_complexity(scene_data)
        print(f"  Складність: {complexity:.2f}")
        
        # Розрахунок адаптивних семплів
        noise_level = manager.adaptive_sampling.estimate_noise_level(scene_data)
        adaptive_samples = manager.adaptive_sampling.calculate_adaptive_samples(
            complexity, noise_level, 1.0
        )
        
        print(f"  Рівень шуму: {noise_level:.2f}")
        print(f"  Адаптивні семпли: {adaptive_samples}")
        
        # Рекомендації по семплуванню
        recommendations = manager.adaptive_sampling.get_sampling_recommendations()
        if 'recommendation' in recommendations:
            print(f"  Рекомендація: {recommendations['recommendation']}")
    
    manager.cleanup()
    print("Тестування адаптивного семплування завершено!\n")


def example_lod_system():
    """Приклад роботи LOD системи"""
    
    print("=== Система LOD (Level of Detail) ===")
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=False, enable_monitoring=False)
    
    # Тестове зображення
    test_image = np.random.random((512, 512, 3)).astype(np.float32)
    
    # Тестування різних рівнів LOD
    distances = [25, 75, 150, 300, 500]
    object_complexities = [0.5, 1.0, 1.5, 2.0]
    
    print("Тестування LOD на різних відстанях та складності:")
    
    for distance in distances:
        for complexity in object_complexities:
            lod_level = manager.lod_system.get_lod_level(distance, complexity, 0.0)
            resolution = manager.lod_system.get_resolution_for_lod(lod_level)
            
            print(f"  Відстань: {distance:3d}, Складність: {complexity:.1f} -> LOD {lod_level}, Роздільність: {resolution[0]}x{resolution[1]}")
    
    # Тестування генерації LOD даних
    print(f"\nТестування генерації LOD даних:")
    
    for lod_level in range(5):
        start_time = time.time()
        lod_data = manager.lod_system.generate_lod_data(test_image, lod_level)
        generation_time = time.time() - start_time
        
        print(f"  LOD {lod_level}: {lod_data.shape} за {generation_time:.3f}s")
    
    # Статистика LOD
    lod_stats = manager.lod_system.get_lod_statistics()
    print(f"\nСтатистика LOD:")
    print(f"  Переключень LOD: {lod_stats['lod_switches']}")
    print(f"  Розмір кешу: {lod_stats['cache_size']}")
    print(f"  Кількість рівнів: {lod_stats['lod_levels']}")
    
    manager.cleanup()
    print("Тестування LOD системи завершено!\n")


def example_performance_monitoring():
    """Приклад моніторингу продуктивності"""
    
    print("=== Моніторинг продуктивності ===")
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)
    
    # Запуск моніторингу
    print("Запуск моніторингу продуктивності...")
    time.sleep(2)  # Дати час для збору метрик
    
    # Отримання поточних метрик
    current_metrics = manager.performance_monitor.get_current_metrics()
    print(f"\nПоточні метрики:")
    for key, value in current_metrics.items():
        print(f"  {key}: {value}")
    
    # Отримання трендів
    trends = manager.performance_monitor.get_performance_trends()
    if trends:
        print(f"\nТренди продуктивності (останні {len(trends['cpu_usage'])} вимірювань):")
        print(f"  CPU: {np.mean(trends['cpu_usage']):.1f}% ± {np.std(trends['cpu_usage']):.1f}%")
        print(f"  Пам'ять: {np.mean(trends['memory_usage']):.1f}% ± {np.std(trends['memory_usage']):.1f}%")
        print(f"  GPU: {np.mean(trends['gpu_usage']):.1f}% ± {np.std(trends['gpu_usage']):.1f}%")
    
    # Рекомендації
    recommendations = manager.performance_monitor.get_performance_recommendations()
    if recommendations:
        print(f"\nРекомендації по оптимізації:")
        for rec in recommendations:
            print(f"  - {rec}")
    
    # Очистити ресурси
    manager.cleanup()
    print("Моніторинг продуктивності завершено!\n")


def example_optimization_recommendations():
    """Приклад отримання рекомендацій по оптимізації"""
    
    print("=== Рекомендації по оптимізації ===")
    
    # Створення менеджера продуктивності
    manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)
    
    # Тестування різних цільових FPS
    target_fps_values = [15, 30, 60, 120]
    
    for target_fps in target_fps_values:
        print(f"\nРекомендації для цільового FPS: {target_fps}")
        
        recommendations = manager.optimize_settings(target_fps)
        
        if recommendations:
            for key, value in recommendations.items():
                print(f"  {key}: {value}")
        else:
            print("  Немає рекомендацій - поточні налаштування оптимальні")
    
    # Очистити ресурси
    manager.cleanup()
    print("Тестування рекомендацій завершено!\n")


def example_integrated_pipeline():
    """Приклад використання інтегрованого пайплайну"""
    
    print("=== Інтегрований пайплайн з Blender ===")
    
    try:
        import bpy
        blender_available = True
    except ImportError:
        blender_available = False
        print("Blender недоступний - пропускаємо тест інтегрованого пайплайну")
        return
    
    if not blender_available:
        return
    
    # Створення інтегрованого пайплайну
    pipeline = PerformanceIntegratedPipeline("renders/example_output")
    
    # Тестові конфігурації рендерингу
    test_configs = [
        {
            'shot_id': 'example_draft',
            'frame': 1,
            'target_fps': 60.0,
            'quality_preset': 'draft',
            'passes': ['beauty', 'depth']
        },
        {
            'shot_id': 'example_balanced',
            'frame': 1,
            'target_fps': 30.0,
            'quality_preset': 'balanced',
            'passes': ['beauty', 'depth', 'normal']
        }
    ]
    
    print("Рендеринг тестових сцен...")
    
    for config in test_configs:
        print(f"\nРендеринг: {config['shot_id']}")
        
        try:
            result = pipeline.render_shot_optimized(
                config['shot_id'],
                config['frame'],
                config['passes'],
                config['target_fps'],
                config['quality_preset']
            )
            
            print(f"  Успішно зрендерено: {len(result['passes'])} пасів")
            print(f"  Час рендерингу: {result['performance_metrics']['generation_time']:.3f}s")
            print(f"  Адаптивні семпли: {result['performance_metrics']['adaptive_samples']}")
            
        except Exception as e:
            print(f"  Помилка рендерингу: {e}")
    
    # Очистити ресурси
    pipeline.cleanup()
    print("Тестування інтегрованого пайплайну завершено!\n")


def main():
    """Головна функція з усіма прикладами"""
    
    print("Демонстрація розширеного менеджера продуктивності")
    print("=" * 60)
    
    try:
        # Базовий приклад
        example_basic_usage()
        
        # Порівняння денойзу
        example_denoising_comparison()
        
        # Адаптивне семплування
        example_adaptive_sampling()
        
        # LOD система
        example_lod_system()
        
        # Моніторинг продуктивності
        example_performance_monitoring()
        
        # Рекомендації по оптимізації
        example_optimization_recommendations()
        
        # Інтегрований пайплайн (якщо Blender доступний)
        example_integrated_pipeline()
        
        print("Всі приклади виконано успішно!")
        
    except Exception as e:
        logger.error(f"Помилка під час виконання прикладів: {e}")
        raise


if __name__ == "__main__":
    main()