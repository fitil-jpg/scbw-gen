#!/usr/bin/env python3
"""
Performance Optimization for StarCraft Map Scene Generation
Оптимізація продуктивності для генерації сцен карт StarCraft

This module provides performance optimizations including:
- Spatial hashing for fast neighbor searches
- LOD (Level of Detail) system
- Parallel processing
- Caching mechanisms
- Memory optimization
"""

import math
import time
import threading
import multiprocessing
from typing import List, Tuple, Dict, Any, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
from functools import lru_cache


@dataclass
class PerformanceMetrics:
    """Метрики продуктивності"""
    generation_time: float
    memory_usage: float
    cache_hits: int
    cache_misses: int
    parallel_tasks: int


class SpatialHash:
    """Просторове хешування для швидкого пошуку сусідів"""
    
    def __init__(self, cell_size: float = 10.0):
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def _get_cell_key(self, x: float, y: float) -> Tuple[int, int]:
        """Отримати ключ клітинки для координат"""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def add_object(self, obj_id: str, x: float, y: float, data: Any = None):
        """Додати об'єкт до просторового хешу"""
        cell_key = self._get_cell_key(x, y)
        self.grid[cell_key].append({
            'id': obj_id,
            'x': x,
            'y': y,
            'data': data
        })
    
    def get_nearby_objects(self, x: float, y: float, radius: float) -> List[Dict[str, Any]]:
        """Отримати об'єкти поблизу позиції"""
        nearby_objects = []
        
        # Обчислити діапазон клітинок для пошуку
        min_cell_x = int((x - radius) // self.cell_size)
        max_cell_x = int((x + radius) // self.cell_size)
        min_cell_y = int((y - radius) // self.cell_size)
        max_cell_y = int((y + radius) // self.cell_size)
        
        # Перевірити клітинки в діапазоні
        for cell_x in range(min_cell_x, max_cell_x + 1):
            for cell_y in range(min_cell_y, max_cell_y + 1):
                cell_key = (cell_x, cell_y)
                if cell_key in self.grid:
                    for obj in self.grid[cell_key]:
                        # Перевірити точну відстань
                        distance = math.sqrt(
                            (obj['x'] - x)**2 + (obj['y'] - y)**2
                        )
                        if distance <= radius:
                            nearby_objects.append(obj)
        
        return nearby_objects
    
    def clear(self):
        """Очистити хеш"""
        self.grid.clear()


class LODSystem:
    """Система рівнів деталізації"""
    
    def __init__(self, base_resolution: int = 512):
        self.base_resolution = base_resolution
        self.lod_levels = [1.0, 0.5, 0.25, 0.125]  # Рівні деталізації
        self.lod_cache = {}
    
    def get_lod_level(self, distance: float, max_distance: float) -> int:
        """Визначити рівень деталізації на основі відстані"""
        if distance >= max_distance:
            return len(self.lod_levels) - 1
        
        ratio = distance / max_distance
        for i, lod_ratio in enumerate(self.lod_levels):
            if ratio <= lod_ratio:
                return i
        
        return 0
    
    def get_resolution_for_lod(self, lod_level: int) -> int:
        """Отримати роздільну здатність для рівня деталізації"""
        return int(self.base_resolution * self.lod_levels[lod_level])
    
    def generate_lod_data(self, 
                         data: np.ndarray, 
                         lod_level: int) -> np.ndarray:
        """Згенерувати дані для рівня деталізації"""
        if lod_level == 0:
            return data
        
        # Кешування
        cache_key = (id(data), lod_level)
        if cache_key in self.lod_cache:
            return self.lod_cache[cache_key]
        
        # Зменшити роздільну здатність
        scale_factor = self.lod_levels[lod_level]
        new_height = int(data.shape[0] * scale_factor)
        new_width = int(data.shape[1] * scale_factor)
        
        if new_height <= 0 or new_width <= 0:
            return data
        
        # Використати інтерполяцію для зменшення
        from scipy.ndimage import zoom
        try:
            lod_data = zoom(data, scale_factor, order=1)
        except ImportError:
            # Простий метод зменшення якщо scipy недоступний
            lod_data = self._simple_downsample(data, scale_factor)
        
        self.lod_cache[cache_key] = lod_data
        return lod_data
    
    def _simple_downsample(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Простий метод зменшення розміру"""
        new_height = int(data.shape[0] * scale_factor)
        new_width = int(data.shape[1] * scale_factor)
        
        if new_height <= 0 or new_width <= 0:
            return data
        
        # Використати середнє значення для зменшення
        step_y = data.shape[0] // new_height
        step_x = data.shape[1] // new_width
        
        result = np.zeros((new_height, new_width), dtype=data.dtype)
        
        for i in range(new_height):
            for j in range(new_width):
                start_y = i * step_y
                end_y = min((i + 1) * step_y, data.shape[0])
                start_x = j * step_x
                end_x = min((j + 1) * step_x, data.shape[1])
                
                result[i, j] = np.mean(data[start_y:end_y, start_x:end_x])
        
        return result


class CacheManager:
    """Менеджер кешування"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.access_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Отримати значення з кешу"""
        if key in self.cache:
            self.access_times[key] = self.access_count
            self.access_count += 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Встановити значення в кеш"""
        if len(self.cache) >= self.max_size:
            self._evict_least_recently_used()
        
        self.cache[key] = value
        self.access_times[key] = self.access_count
        self.access_count += 1
    
    def _evict_least_recently_used(self):
        """Видалити найменш використовуваний елемент"""
        if not self.cache:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def clear(self):
        """Очистити кеш"""
        self.cache.clear()
        self.access_times.clear()
        self.access_count = 0
    
    def get_stats(self) -> Dict[str, int]:
        """Отримати статистику кешу"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'access_count': self.access_count
        }


class ParallelProcessor:
    """Паралельний обробник"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def process_terrain_chunks(self, 
                              terrain_data: np.ndarray,
                              chunk_size: int = 64) -> np.ndarray:
        """Обробити рельєф паралельно по чанках"""
        
        def process_chunk(chunk_data):
            # Простий приклад обробки чанка
            return chunk_data * 1.1  # Масштабування
        
        # Розділити на чанки
        chunks = []
        for y in range(0, terrain_data.shape[0], chunk_size):
            for x in range(0, terrain_data.shape[1], chunk_size):
                chunk = terrain_data[y:y+chunk_size, x:x+chunk_size]
                chunks.append((y, x, chunk))
        
        # Обробити паралельно
        results = []
        for y, x, chunk in chunks:
            future = self.thread_pool.submit(process_chunk, chunk)
            results.append((y, x, future))
        
        # Зібрати результати
        processed_terrain = terrain_data.copy()
        for y, x, future in results:
            result = future.result()
            processed_terrain[y:y+result.shape[0], x:x+result.shape[1]] = result
        
        return processed_terrain
    
    def process_units_parallel(self, 
                              units: List[Dict[str, Any]],
                              processing_func) -> List[Any]:
        """Обробити юнітів паралельно"""
        
        # Розділити юнітів на групи
        chunk_size = max(1, len(units) // self.max_workers)
        chunks = [units[i:i+chunk_size] for i in range(0, len(units), chunk_size)]
        
        # Обробити паралельно
        futures = []
        for chunk in chunks:
            future = self.thread_pool.submit(processing_func, chunk)
            futures.append(future)
        
        # Зібрати результати
        results = []
        for future in futures:
            results.extend(future.result())
        
        return results
    
    def close(self):
        """Закрити пули потоків"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


class MemoryOptimizer:
    """Оптимізатор пам'яті"""
    
    def __init__(self):
        self.memory_usage = 0
        self.max_memory = 1024 * 1024 * 1024  # 1GB за замовчуванням
    
    def optimize_array(self, array: np.ndarray) -> np.ndarray:
        """Оптимізувати масив для зменшення використання пам'яті"""
        
        # Перевірити тип даних
        if array.dtype == np.float64:
            # Конвертувати в float32 якщо точність дозволяє
            if np.all(np.isfinite(array)) and np.all(np.abs(array) < 3.4e38):
                array = array.astype(np.float32)
        
        # Використати стиснення якщо можливо
        if array.dtype in [np.int32, np.int64]:
            max_val = np.max(array)
            min_val = np.min(array)
            
            if max_val <= 255 and min_val >= 0:
                array = array.astype(np.uint8)
            elif max_val <= 65535 and min_val >= 0:
                array = array.astype(np.uint16)
            elif max_val <= 127 and min_val >= -128:
                array = array.astype(np.int8)
            elif max_val <= 32767 and min_val >= -32768:
                array = array.astype(np.int16)
        
        return array
    
    def get_memory_usage(self) -> float:
        """Отримати поточне використання пам'яті в MB"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def check_memory_limit(self) -> bool:
        """Перевірити чи не перевищено ліміт пам'яті"""
        current_usage = self.get_memory_usage()
        return current_usage < self.max_memory / 1024 / 1024


class PerformanceProfiler:
    """Профілер продуктивності"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, name: str):
        """Почати таймер"""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """Завершити таймер та повернути час"""
        if name not in self.start_times:
            return 0.0
        
        elapsed = time.time() - self.start_times[name]
        self.metrics[name] = elapsed
        del self.start_times[name]
        return elapsed
    
    def get_metrics(self) -> Dict[str, float]:
        """Отримати всі метрики"""
        return self.metrics.copy()
    
    def reset(self):
        """Скинути метрики"""
        self.metrics.clear()
        self.start_times.clear()


class OptimizedTerrainGenerator:
    """Оптимізований генератор рельєфу"""
    
    def __init__(self, width: int, height: int, enable_optimizations: bool = True):
        self.width = width
        self.height = height
        self.enable_optimizations = enable_optimizations
        
        # Ініціалізація оптимізацій
        if enable_optimizations:
            self.spatial_hash = SpatialHash(cell_size=20.0)
            self.lod_system = LODSystem(base_resolution=max(width, height))
            self.cache_manager = CacheManager(max_size=500)
            self.parallel_processor = ParallelProcessor()
            self.memory_optimizer = MemoryOptimizer()
            self.profiler = PerformanceProfiler()
        else:
            self.spatial_hash = None
            self.lod_system = None
            self.cache_manager = None
            self.parallel_processor = None
            self.memory_optimizer = None
            self.profiler = None
    
    def generate_terrain_optimized(self, 
                                  octaves: int = 4,
                                  persistence: float = 0.5,
                                  use_lod: bool = True) -> np.ndarray:
        """Згенерувати рельєф з оптимізаціями"""
        
        if not self.enable_optimizations:
            # Використати стандартну генерацію
            return self._generate_terrain_standard(octaves, persistence)
        
        # Почати профілювання
        if self.profiler:
            self.profiler.start_timer("terrain_generation")
        
        # Перевірити кеш
        cache_key = f"terrain_{self.width}_{self.height}_{octaves}_{persistence}"
        if self.cache_manager:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Генерувати рельєф
        if use_lod and self.lod_system:
            # Генерувати з LOD
            terrain = self._generate_terrain_with_lod(octaves, persistence)
        else:
            # Стандартна генерація
            terrain = self._generate_terrain_standard(octaves, persistence)
        
        # Оптимізувати пам'ять
        if self.memory_optimizer:
            terrain = self.memory_optimizer.optimize_array(terrain)
        
        # Зберегти в кеш
        if self.cache_manager:
            self.cache_manager.set(cache_key, terrain)
        
        # Завершити профілювання
        if self.profiler:
            self.profiler.end_timer("terrain_generation")
        
        return terrain
    
    def _generate_terrain_standard(self, octaves: int, persistence: float) -> np.ndarray:
        """Стандартна генерація рельєфу"""
        # Спрощена реалізація для прикладу
        terrain = np.random.random((self.height, self.width)).astype(np.float32)
        return terrain
    
    def _generate_terrain_with_lod(self, octaves: int, persistence: float) -> np.ndarray:
        """Генерація рельєфу з LOD"""
        # Генерувати на найвищому рівні деталізації
        base_terrain = self._generate_terrain_standard(octaves, persistence)
        
        # Застосувати LOD
        if self.lod_system:
            # Для прикладу використовуємо LOD рівень 0 (повна деталізація)
            terrain = self.lod_system.generate_lod_data(base_terrain, 0)
        else:
            terrain = base_terrain
        
        return terrain
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Отримати метрики продуктивності"""
        if not self.profiler:
            return PerformanceMetrics(0, 0, 0, 0, 0)
        
        metrics = self.profiler.get_metrics()
        generation_time = metrics.get("terrain_generation", 0.0)
        
        memory_usage = 0.0
        if self.memory_optimizer:
            memory_usage = self.memory_optimizer.get_memory_usage()
        
        cache_hits = 0
        cache_misses = 0
        if self.cache_manager:
            stats = self.cache_manager.get_stats()
            cache_hits = stats.get('access_count', 0)
            cache_misses = 0  # Спрощено для прикладу
        
        parallel_tasks = 0
        if self.parallel_processor:
            parallel_tasks = self.parallel_processor.max_workers
        
        return PerformanceMetrics(
            generation_time=generation_time,
            memory_usage=memory_usage,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            parallel_tasks=parallel_tasks
        )
    
    def cleanup(self):
        """Очистити ресурси"""
        if self.parallel_processor:
            self.parallel_processor.close()
        
        if self.cache_manager:
            self.cache_manager.clear()
        
        if self.spatial_hash:
            self.spatial_hash.clear()


def benchmark_terrain_generation():
    """Бенчмарк генерації рельєфу"""
    print("Бенчмарк генерації рельєфу...")
    
    sizes = [128, 256, 512, 1024]
    
    for size in sizes:
        print(f"\nРозмір: {size}x{size}")
        
        # Тест без оптимізацій
        generator_standard = OptimizedTerrainGenerator(size, size, enable_optimizations=False)
        start_time = time.time()
        terrain_standard = generator_standard.generate_terrain_optimized()
        standard_time = time.time() - start_time
        
        # Тест з оптимізаціями
        generator_optimized = OptimizedTerrainGenerator(size, size, enable_optimizations=True)
        start_time = time.time()
        terrain_optimized = generator_optimized.generate_terrain_optimized()
        optimized_time = time.time() - start_time
        
        # Метрики
        metrics = generator_optimized.get_performance_metrics()
        
        print(f"  Стандартний: {standard_time:.3f}s")
        print(f"  Оптимізований: {optimized_time:.3f}s")
        print(f"  Прискорення: {standard_time/optimized_time:.2f}x")
        print(f"  Пам'ять: {metrics.memory_usage:.1f}MB")
        
        generator_optimized.cleanup()


if __name__ == "__main__":
    # Запустити бенчмарк
    benchmark_terrain_generation()
    
    print("\nТестування оптимізацій завершено!")