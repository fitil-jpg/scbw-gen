#!/usr/bin/env python3
"""
Розширений менеджер продуктивності для StarCraft Map Scene Generation
Advanced Performance Manager for GPU/CPU, Denoising, Tiles, Adaptive Sampling, LOD

Цей модуль надає комплексну систему управління продуктивністю включаючи:
- Управління ресурсами GPU/CPU з балансуванням навантаження
- Розширені системи денойзу (OptiX, OIDN, NLM)
- Інтелектуальне управління тайлами для оптимального використання пам'яті
- Адаптивне семплування на основі складності сцени
- Покращена система LOD з динамічним масштабуванням якості
- Моніторинг продуктивності в реальному часі
"""

import math
import time
import threading
import multiprocessing
import psutil
import GPUtil
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import lru_cache
import json
import logging
from pathlib import Path
import subprocess
import platform

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Розширені метрики продуктивності"""
    generation_time: float = 0.0
    memory_usage: float = 0.0
    gpu_memory_usage: float = 0.0
    cpu_usage: float = 0.0
    gpu_usage: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_tasks: int = 0
    tiles_processed: int = 0
    denoising_time: float = 0.0
    lod_switches: int = 0
    adaptive_samples: int = 0
    render_quality: float = 1.0


@dataclass
class DeviceInfo:
    """Інформація про пристрій (GPU/CPU)"""
    device_id: int
    device_type: str  # 'GPU' or 'CPU'
    name: str
    memory_total: float  # MB
    memory_used: float = 0.0
    memory_free: float = 0.0
    utilization: float = 0.0
    temperature: float = 0.0
    power_usage: float = 0.0
    is_available: bool = True


@dataclass
class TileInfo:
    """Інформація про тайл для рендерингу"""
    tile_id: str
    x: int
    y: int
    width: int
    height: int
    priority: int = 0
    complexity: float = 1.0
    samples: int = 128
    device_id: int = 0
    status: str = 'pending'  # pending, processing, completed, failed
    start_time: float = 0.0
    end_time: float = 0.0


class GPUManager:
    """Менеджер GPU ресурсів"""
    
    def __init__(self):
        self.gpus = []
        self.gpu_queue = []
        self.lock = threading.Lock()
        self._initialize_gpus()
    
    def _initialize_gpus(self):
        """Ініціалізація доступних GPU"""
        try:
            gpu_list = GPUtil.getGPUs()
            for i, gpu in enumerate(gpu_list):
                device_info = DeviceInfo(
                    device_id=i,
                    device_type='GPU',
                    name=gpu.name,
                    memory_total=gpu.memoryTotal,
                    memory_used=gpu.memoryUsed,
                    memory_free=gpu.memoryFree,
                    utilization=gpu.load * 100,
                    temperature=gpu.temperature,
                    is_available=True
                )
                self.gpus.append(device_info)
                logger.info(f"GPU {i} ініціалізовано: {gpu.name}")
        except Exception as e:
            logger.warning(f"Не вдалося ініціалізувати GPU: {e}")
    
    def get_available_gpu(self) -> Optional[DeviceInfo]:
        """Отримати доступний GPU з найменшим навантаженням"""
        with self.lock:
            available_gpus = [gpu for gpu in self.gpus if gpu.is_available and gpu.memory_free > 100]
            if not available_gpus:
                return None
            
            # Сортувати за використанням пам'яті та навантаженням
            available_gpus.sort(key=lambda gpu: (gpu.memory_used / gpu.memory_total, gpu.utilization))
            return available_gpus[0]
    
    def update_gpu_status(self):
        """Оновити статус GPU"""
        try:
            gpu_list = GPUtil.getGPUs()
            for i, gpu in enumerate(gpu_list):
                if i < len(self.gpus):
                    self.gpus[i].memory_used = gpu.memoryUsed
                    self.gpus[i].memory_free = gpu.memoryFree
                    self.gpus[i].utilization = gpu.load * 100
                    self.gpus[i].temperature = gpu.temperature
        except Exception as e:
            logger.warning(f"Помилка оновлення статусу GPU: {e}")
    
    def allocate_gpu_memory(self, device_id: int, memory_mb: float) -> bool:
        """Виділити пам'ять на GPU"""
        with self.lock:
            if device_id < len(self.gpus):
                gpu = self.gpus[device_id]
                if gpu.memory_free >= memory_mb:
                    gpu.memory_used += memory_mb
                    gpu.memory_free -= memory_mb
                    return True
        return False
    
    def release_gpu_memory(self, device_id: int, memory_mb: float):
        """Звільнити пам'ять на GPU"""
        with self.lock:
            if device_id < len(self.gpus):
                gpu = self.gpus[device_id]
                gpu.memory_used = max(0, gpu.memory_used - memory_mb)
                gpu.memory_free = min(gpu.memory_total, gpu.memory_free + memory_mb)


class CPUManager:
    """Менеджер CPU ресурсів"""
    
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.cpu_usage_history = deque(maxlen=60)  # 60 секунд історії
        self.thread_pools = {}
        self.lock = threading.Lock()
    
    def get_cpu_usage(self) -> float:
        """Отримати поточне використання CPU"""
        return psutil.cpu_percent(interval=1)
    
    def get_optimal_thread_count(self) -> int:
        """Отримати оптимальну кількість потоків"""
        cpu_usage = self.get_cpu_usage()
        self.cpu_usage_history.append(cpu_usage)
        
        # Якщо CPU навантажений більше 80%, зменшити кількість потоків
        if cpu_usage > 80:
            return max(1, self.cpu_count // 2)
        elif cpu_usage > 60:
            return max(2, self.cpu_count * 3 // 4)
        else:
            return self.cpu_count
    
    def create_thread_pool(self, pool_id: str, max_workers: int = None) -> ThreadPoolExecutor:
        """Створити пул потоків"""
        if max_workers is None:
            max_workers = self.get_optimal_thread_count()
        
        with self.lock:
            if pool_id in self.thread_pools:
                self.thread_pools[pool_id].shutdown(wait=False)
            
            self.thread_pools[pool_id] = ThreadPoolExecutor(max_workers=max_workers)
            return self.thread_pools[pool_id]
    
    def cleanup_thread_pools(self):
        """Очистити всі пули потоків"""
        with self.lock:
            for pool in self.thread_pools.values():
                pool.shutdown(wait=True)
            self.thread_pools.clear()


class DenoisingManager:
    """Менеджер денойзу з підтримкою різних алгоритмів"""
    
    def __init__(self):
        self.denoisers = {
            'OPTIX': self._optix_denoise,
            'OIDN': self._oidn_denoise,
            'NLM': self._nlm_denoise,
            'BILATERAL': self._bilateral_denoise
        }
        self.denoising_cache = {}
        self.cache_size = 100
    
    def denoise_image(self, image: np.ndarray, 
                     algorithm: str = 'OPTIX',
                     strength: float = 1.0,
                     **kwargs) -> np.ndarray:
        """Денойз зображення вибраним алгоритмом"""
        
        # Перевірити кеш
        cache_key = self._get_cache_key(image, algorithm, strength, kwargs)
        if cache_key in self.denoising_cache:
            return self.denoising_cache[cache_key]
        
        # Виконати денойз
        if algorithm in self.denoisers:
            start_time = time.time()
            denoised = self.denoisers[algorithm](image, strength, **kwargs)
            denoising_time = time.time() - start_time
            
            # Зберегти в кеш
            self._cache_result(cache_key, denoised)
            
            logger.info(f"Денойз завершено за {denoising_time:.3f}s алгоритмом {algorithm}")
            return denoised
        else:
            logger.warning(f"Невідомий алгоритм денойзу: {algorithm}")
            return image
    
    def _optix_denoise(self, image: np.ndarray, strength: float, **kwargs) -> np.ndarray:
        """OptiX денойз (симуляція)"""
        # Спрощена реалізація - в реальності використовувати OptiX API
        if len(image.shape) == 3:
            # Кольорове зображення
            denoised = self._gaussian_blur(image, strength * 2)
        else:
            # Сіре зображення
            denoised = self._gaussian_blur(image, strength * 1.5)
        
        return denoised.astype(image.dtype)
    
    def _oidn_denoise(self, image: np.ndarray, strength: float, **kwargs) -> np.ndarray:
        """OIDN денойз (симуляція)"""
        # Спрощена реалізація - в реальності використовувати OIDN
        denoised = self._bilateral_filter(image, strength)
        return denoised.astype(image.dtype)
    
    def _nlm_denoise(self, image: np.ndarray, strength: float, **kwargs) -> np.ndarray:
        """Non-Local Means денойз"""
        # Спрощена реалізація NLM
        h = kwargs.get('h', 10.0 * strength)
        template_window_size = kwargs.get('template_window_size', 7)
        search_window_size = kwargs.get('search_window_size', 21)
        
        if len(image.shape) == 3:
            denoised = np.zeros_like(image)
            for c in range(image.shape[2]):
                denoised[:, :, c] = self._nlm_2d(image[:, :, c], h, template_window_size, search_window_size)
        else:
            denoised = self._nlm_2d(image, h, template_window_size, search_window_size)
        
        return denoised.astype(image.dtype)
    
    def _bilateral_denoise(self, image: np.ndarray, strength: float, **kwargs) -> np.ndarray:
        """Білатеральний фільтр"""
        return self._bilateral_filter(image, strength)
    
    def _gaussian_blur(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """Гаусів блюр"""
        from scipy.ndimage import gaussian_filter
        try:
            return gaussian_filter(image, sigma=sigma)
        except ImportError:
            # Простий блюр якщо scipy недоступний
            return self._simple_blur(image, int(sigma * 3))
    
    def _bilateral_filter(self, image: np.ndarray, strength: float) -> np.ndarray:
        """Білатеральний фільтр (спрощена реалізація)"""
        # Спрощена реалізація - в реальності використовувати OpenCV або scikit-image
        return self._gaussian_blur(image, strength)
    
    def _nlm_2d(self, image: np.ndarray, h: float, template_size: int, search_size: int) -> np.ndarray:
        """2D Non-Local Means (спрощена реалізація)"""
        # Спрощена реалізація NLM
        return self._gaussian_blur(image, h / 10)
    
    def _simple_blur(self, image: np.ndarray, kernel_size: int) -> np.ndarray:
        """Простий блюр"""
        if kernel_size <= 1:
            return image
        
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
        
        if len(image.shape) == 3:
            result = np.zeros_like(image)
            for c in range(image.shape[2]):
                result[:, :, c] = self._convolve2d(image[:, :, c], kernel)
            return result
        else:
            return self._convolve2d(image, kernel)
    
    def _convolve2d(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """2D згортка"""
        from scipy.signal import convolve2d
        try:
            return convolve2d(image, kernel, mode='same')
        except ImportError:
            # Проста реалізація згортки
            return self._naive_convolve2d(image, kernel)
    
    def _naive_convolve2d(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Наївна реалізація 2D згортки"""
        h, w = image.shape
        kh, kw = kernel.shape
        result = np.zeros_like(image)
        
        for i in range(h):
            for j in range(w):
                for ki in range(kh):
                    for kj in range(kw):
                        ii = i + ki - kh // 2
                        jj = j + kj - kw // 2
                        if 0 <= ii < h and 0 <= jj < w:
                            result[i, j] += image[ii, jj] * kernel[ki, kj]
        
        return result
    
    def _get_cache_key(self, image: np.ndarray, algorithm: str, strength: float, kwargs: dict) -> str:
        """Отримати ключ кешу"""
        return f"{id(image)}_{algorithm}_{strength}_{hash(str(sorted(kwargs.items())))}"
    
    def _cache_result(self, cache_key: str, result: np.ndarray):
        """Зберегти результат в кеш"""
        if len(self.denoising_cache) >= self.cache_size:
            # Видалити найстаріший елемент
            oldest_key = next(iter(self.denoising_cache))
            del self.denoising_cache[oldest_key]
        
        self.denoising_cache[cache_key] = result


class TileManager:
    """Менеджер тайлів для оптимального рендерингу"""
    
    def __init__(self, image_width: int, image_height: int, 
                 base_tile_size: int = 256, overlap: int = 8):
        self.image_width = image_width
        self.image_height = image_height
        self.base_tile_size = base_tile_size
        self.overlap = overlap
        self.tiles = []
        self.tile_queue = []
        self.completed_tiles = []
        self.lock = threading.Lock()
        self._generate_tiles()
    
    def _generate_tiles(self):
        """Генерувати тайли для зображення"""
        self.tiles = []
        tile_id = 0
        
        for y in range(0, self.image_height, self.base_tile_size):
            for x in range(0, self.image_width, self.base_tile_size):
                # Розрахунок розмірів тайлу з перекриттям
                tile_width = min(self.base_tile_size, self.image_width - x)
                tile_height = min(self.base_tile_size, self.image_height - y)
                
                # Додати перекриття
                if x > 0:
                    x -= self.overlap
                    tile_width += self.overlap
                if y > 0:
                    y -= self.overlap
                    tile_height += self.overlap
                
                # Обмежити розміри
                tile_width = min(tile_width, self.image_width)
                tile_height = min(tile_height, self.image_height)
                
                tile = TileInfo(
                    tile_id=f"tile_{tile_id}",
                    x=x,
                    y=y,
                    width=tile_width,
                    height=tile_height,
                    priority=0
                )
                
                self.tiles.append(tile)
                tile_id += 1
        
        # Ініціалізувати чергу
        self.tile_queue = self.tiles.copy()
        logger.info(f"Створено {len(self.tiles)} тайлів для зображення {self.image_width}x{self.image_height}")
    
    def get_next_tile(self) -> Optional[TileInfo]:
        """Отримати наступний тайл для обробки"""
        with self.lock:
            if not self.tile_queue:
                return None
            
            # Сортувати за пріоритетом
            self.tile_queue.sort(key=lambda t: t.priority, reverse=True)
            tile = self.tile_queue.pop(0)
            tile.status = 'processing'
            tile.start_time = time.time()
            return tile
    
    def complete_tile(self, tile: TileInfo, result: np.ndarray):
        """Завершити обробку тайлу"""
        with self.lock:
            tile.status = 'completed'
            tile.end_time = time.time()
            tile.processing_time = tile.end_time - tile.start_time
            self.completed_tiles.append((tile, result))
            logger.info(f"Тайл {tile.tile_id} завершено за {tile.processing_time:.3f}s")
    
    def set_tile_priority(self, tile_id: str, priority: int):
        """Встановити пріоритет тайлу"""
        with self.lock:
            for tile in self.tile_queue:
                if tile.tile_id == tile_id:
                    tile.priority = priority
                    break
    
    def get_tile_complexity(self, tile: TileInfo, image_data: np.ndarray) -> float:
        """Розрахувати складність тайлу"""
        if tile.x >= image_data.shape[1] or tile.y >= image_data.shape[0]:
            return 1.0
        
        # Витягти дані тайлу
        end_x = min(tile.x + tile.width, image_data.shape[1])
        end_y = min(tile.y + tile.height, image_data.shape[0])
        
        if len(image_data.shape) == 3:
            tile_data = image_data[tile.y:end_y, tile.x:end_x, :]
        else:
            tile_data = image_data[tile.y:end_y, tile.x:end_x]
        
        # Розрахувати складність на основі варіації пікселів
        if len(tile_data.shape) == 3:
            # Кольорове зображення
            gray = np.mean(tile_data, axis=2)
        else:
            gray = tile_data
        
        # Стандартне відхилення як міра складності
        complexity = np.std(gray) / 255.0
        
        # Нормалізувати до діапазону [0.1, 2.0]
        complexity = max(0.1, min(2.0, complexity * 2))
        
        return complexity
    
    def get_progress(self) -> Dict[str, Any]:
        """Отримати прогрес обробки тайлів"""
        with self.lock:
            total_tiles = len(self.tiles)
            completed_tiles = len(self.completed_tiles)
            processing_tiles = sum(1 for tile in self.tiles if tile.status == 'processing')
            pending_tiles = len(self.tile_queue)
            
            return {
                'total_tiles': total_tiles,
                'completed_tiles': completed_tiles,
                'processing_tiles': processing_tiles,
                'pending_tiles': pending_tiles,
                'progress_percentage': (completed_tiles / total_tiles) * 100 if total_tiles > 0 else 0
            }


class AdaptiveSamplingManager:
    """Менеджер адаптивного семплування"""
    
    def __init__(self, base_samples: int = 128, max_samples: int = 1024, min_samples: int = 32):
        self.base_samples = base_samples
        self.max_samples = max_samples
        self.min_samples = min_samples
        self.sampling_history = deque(maxlen=100)
        self.complexity_thresholds = [0.3, 0.6, 0.8]  # Пороги складності
        self.sample_multipliers = [0.5, 1.0, 1.5, 2.0]  # Множники семплів
    
    def calculate_adaptive_samples(self, complexity: float, 
                                 noise_level: float = 0.0,
                                 time_budget: float = 1.0) -> int:
        """Розрахувати адаптивну кількість семплів"""
        
        # Базові семпли на основі складності
        if complexity < self.complexity_thresholds[0]:
            base_multiplier = self.sample_multipliers[0]  # 0.5
        elif complexity < self.complexity_thresholds[1]:
            base_multiplier = self.sample_multipliers[1]  # 1.0
        elif complexity < self.complexity_thresholds[2]:
            base_multiplier = self.sample_multipliers[2]  # 1.5
        else:
            base_multiplier = self.sample_multipliers[3]  # 2.0
        
        # Корекція на основі рівня шуму
        noise_multiplier = 1.0 + noise_level * 0.5
        
        # Корекція на основі бюджету часу
        time_multiplier = min(2.0, max(0.5, time_budget))
        
        # Розрахунок фінальних семплів
        adaptive_samples = int(self.base_samples * base_multiplier * noise_multiplier * time_multiplier)
        
        # Обмежити діапазон
        adaptive_samples = max(self.min_samples, min(self.max_samples, adaptive_samples))
        
        # Зберегти в історію
        self.sampling_history.append({
            'complexity': complexity,
            'noise_level': noise_level,
            'samples': adaptive_samples,
            'timestamp': time.time()
        })
        
        return adaptive_samples
    
    def estimate_noise_level(self, image: np.ndarray) -> float:
        """Оцінити рівень шуму в зображенні"""
        if len(image.shape) == 3:
            # Кольорове зображення - використати яскравість
            gray = np.mean(image, axis=2)
        else:
            gray = image
        
        # Розрахувати локальну варіацію як міру шуму
        from scipy.ndimage import uniform_filter
        try:
            local_mean = uniform_filter(gray, size=3)
            local_variance = uniform_filter(gray**2, size=3) - local_mean**2
            noise_level = np.sqrt(np.mean(local_variance)) / 255.0
        except ImportError:
            # Простий метод якщо scipy недоступний
            noise_level = np.std(gray) / 255.0
        
        return min(1.0, noise_level)
    
    def get_sampling_recommendations(self) -> Dict[str, Any]:
        """Отримати рекомендації по семплуванню"""
        if not self.sampling_history:
            return {'recommendation': 'insufficient_data'}
        
        recent_samples = list(self.sampling_history)[-10:]  # Останні 10 записів
        
        avg_complexity = np.mean([s['complexity'] for s in recent_samples])
        avg_samples = np.mean([s['samples'] for s in recent_samples])
        avg_noise = np.mean([s['noise_level'] for s in recent_samples])
        
        # Рекомендації
        if avg_complexity > 0.8 and avg_samples < self.max_samples * 0.8:
            recommendation = 'increase_samples'
        elif avg_complexity < 0.3 and avg_samples > self.min_samples * 2:
            recommendation = 'decrease_samples'
        elif avg_noise > 0.5:
            recommendation = 'enable_denoising'
        else:
            recommendation = 'optimal'
        
        return {
            'recommendation': recommendation,
            'avg_complexity': avg_complexity,
            'avg_samples': avg_samples,
            'avg_noise': avg_noise,
            'suggested_samples': self.calculate_adaptive_samples(avg_complexity, avg_noise)
        }


class EnhancedLODSystem:
    """Покращена система LOD з динамічним масштабуванням"""
    
    def __init__(self, base_resolution: int = 512, max_lod_levels: int = 5):
        self.base_resolution = base_resolution
        self.max_lod_levels = max_lod_levels
        self.lod_levels = [1.0, 0.75, 0.5, 0.25, 0.125][:max_lod_levels]
        self.lod_cache = {}
        self.lod_switches = 0
        self.distance_thresholds = [50, 100, 200, 400]  # Пороги відстані для LOD
    
    def get_lod_level(self, distance: float, object_complexity: float = 1.0, 
                     camera_speed: float = 0.0) -> int:
        """Визначити рівень LOD на основі відстані та складності"""
        
        # Базовий LOD на основі відстані
        base_lod = 0
        for i, threshold in enumerate(self.distance_thresholds):
            if distance > threshold:
                base_lod = i + 1
            else:
                break
        
        # Корекція на основі складності об'єкта
        if object_complexity > 1.5:
            base_lod = max(0, base_lod - 1)  # Вищий рівень деталізації
        elif object_complexity < 0.5:
            base_lod = min(len(self.lod_levels) - 1, base_lod + 1)  # Нижчий рівень
        
        # Корекція на основі швидкості камери
        if camera_speed > 10.0:  # Швидкий рух
            base_lod = min(len(self.lod_levels) - 1, base_lod + 1)
        
        # Обмежити діапазон
        lod_level = max(0, min(len(self.lod_levels) - 1, base_lod))
        
        # Відстежити переключення LOD
        if hasattr(self, '_last_lod_level') and self._last_lod_level != lod_level:
            self.lod_switches += 1
        
        self._last_lod_level = lod_level
        return lod_level
    
    def get_resolution_for_lod(self, lod_level: int) -> Tuple[int, int]:
        """Отримати роздільну здатність для рівня LOD"""
        scale = self.lod_levels[lod_level]
        width = int(self.base_resolution * scale)
        height = int(self.base_resolution * scale)
        return width, height
    
    def generate_lod_data(self, data: np.ndarray, lod_level: int, 
                         method: str = 'bilinear') -> np.ndarray:
        """Згенерувати дані для рівня LOD"""
        
        if lod_level == 0:
            return data
        
        # Кешування
        cache_key = (id(data), lod_level, method)
        if cache_key in self.lod_cache:
            return self.lod_cache[cache_key]
        
        scale_factor = self.lod_levels[lod_level]
        
        if method == 'bilinear':
            lod_data = self._bilinear_downsample(data, scale_factor)
        elif method == 'nearest':
            lod_data = self._nearest_downsample(data, scale_factor)
        elif method == 'gaussian':
            lod_data = self._gaussian_downsample(data, scale_factor)
        else:
            lod_data = self._bilinear_downsample(data, scale_factor)
        
        # Зберегти в кеш
        self.lod_cache[cache_key] = lod_data
        return lod_data
    
    def _bilinear_downsample(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Білінійне зменшення"""
        from scipy.ndimage import zoom
        try:
            return zoom(data, scale_factor, order=1)
        except ImportError:
            return self._simple_downsample(data, scale_factor)
    
    def _nearest_downsample(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Найближчий сусід"""
        from scipy.ndimage import zoom
        try:
            return zoom(data, scale_factor, order=0)
        except ImportError:
            return self._simple_downsample(data, scale_factor)
    
    def _gaussian_downsample(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Гаусове зменшення з антиаліасингом"""
        from scipy.ndimage import gaussian_filter, zoom
        try:
            # Спочатку згладити, потім зменшити
            sigma = (1.0 / scale_factor - 1.0) / 2.0
            if sigma > 0:
                data = gaussian_filter(data, sigma=sigma)
            return zoom(data, scale_factor, order=1)
        except ImportError:
            return self._simple_downsample(data, scale_factor)
    
    def _simple_downsample(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Простий метод зменшення"""
        new_height = int(data.shape[0] * scale_factor)
        new_width = int(data.shape[1] * scale_factor)
        
        if new_height <= 0 or new_width <= 0:
            return data
        
        step_y = data.shape[0] / new_height
        step_x = data.shape[1] / new_width
        
        result = np.zeros((new_height, new_width) + data.shape[2:], dtype=data.dtype)
        
        for i in range(new_height):
            for j in range(new_width):
                start_y = int(i * step_y)
                end_y = int((i + 1) * step_y)
                start_x = int(j * step_x)
                end_x = int((j + 1) * step_x)
                
                if len(data.shape) == 3:
                    result[i, j] = np.mean(data[start_y:end_y, start_x:end_x], axis=(0, 1))
                else:
                    result[i, j] = np.mean(data[start_y:end_y, start_x:end_x])
        
        return result
    
    def get_lod_statistics(self) -> Dict[str, Any]:
        """Отримати статистику LOD"""
        return {
            'lod_switches': self.lod_switches,
            'cache_size': len(self.lod_cache),
            'lod_levels': len(self.lod_levels),
            'distance_thresholds': self.distance_thresholds
        }


class PerformanceMonitor:
    """Монітор продуктивності в реальному часі"""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.metrics_history = deque(maxlen=300)  # 5 хвилин історії
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Почати моніторинг"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Моніторинг продуктивності запущено")
    
    def stop_monitoring(self):
        """Зупинити моніторинг"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Моніторинг продуктивності зупинено")
    
    def _monitor_loop(self):
        """Цикл моніторингу"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                with self.lock:
                    self.metrics_history.append(metrics)
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Помилка моніторингу: {e}")
                time.sleep(self.update_interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Зібрати поточні метрики"""
        return {
            'timestamp': time.time(),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'gpu_usage': self._get_gpu_usage(),
            'gpu_memory': self._get_gpu_memory(),
            'temperature': self._get_temperature()
        }
    
    def _get_gpu_usage(self) -> float:
        """Отримати використання GPU"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except:
            pass
        return 0.0
    
    def _get_gpu_memory(self) -> float:
        """Отримати використання пам'яті GPU"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].memoryUtil * 100
        except:
            pass
        return 0.0
    
    def _get_temperature(self) -> float:
        """Отримати температуру"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].temperature
        except:
            pass
        return 0.0
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Отримати поточні метрики"""
        with self.lock:
            if self.metrics_history:
                return self.metrics_history[-1]
            return {}
    
    def get_performance_trends(self) -> Dict[str, List[float]]:
        """Отримати тренди продуктивності"""
        with self.lock:
            if not self.metrics_history:
                return {}
            
            trends = {
                'cpu_usage': [m['cpu_usage'] for m in self.metrics_history],
                'memory_usage': [m['memory_usage'] for m in self.metrics_history],
                'gpu_usage': [m['gpu_usage'] for m in self.metrics_history],
                'gpu_memory': [m['gpu_memory'] for m in self.metrics_history],
                'temperature': [m['temperature'] for m in self.metrics_history]
            }
            
            return trends
    
    def get_performance_recommendations(self) -> List[str]:
        """Отримати рекомендації по оптимізації"""
        recommendations = []
        
        with self.lock:
            if not self.metrics_history:
                return recommendations
            
            recent_metrics = list(self.metrics_history)[-10:]  # Останні 10 записів
            
            # Аналіз CPU
            avg_cpu = np.mean([m['cpu_usage'] for m in recent_metrics])
            if avg_cpu > 90:
                recommendations.append("CPU перевантажений - зменшити кількість потоків")
            elif avg_cpu < 30:
                recommendations.append("CPU недооптимізований - можна збільшити навантаження")
            
            # Аналіз пам'яті
            avg_memory = np.mean([m['memory_usage'] for m in recent_metrics])
            if avg_memory > 85:
                recommendations.append("Недостатньо RAM - оптимізувати використання пам'яті")
            
            # Аналіз GPU
            avg_gpu = np.mean([m['gpu_usage'] for m in recent_metrics])
            if avg_gpu > 95:
                recommendations.append("GPU перевантажений - зменшити якість рендерингу")
            elif avg_gpu < 20:
                recommendations.append("GPU недооптимізований - можна збільшити якість")
            
            # Аналіз температури
            avg_temp = np.mean([m['temperature'] for m in recent_metrics])
            if avg_temp > 80:
                recommendations.append("Висока температура - перевірити охолодження")
        
        return recommendations


class AdvancedPerformanceManager:
    """Головний клас розширеного менеджера продуктивності"""
    
    def __init__(self, enable_gpu: bool = True, enable_monitoring: bool = True):
        self.enable_gpu = enable_gpu
        self.enable_monitoring = enable_monitoring
        
        # Ініціалізація компонентів
        self.gpu_manager = GPUManager() if enable_gpu else None
        self.cpu_manager = CPUManager()
        self.denoising_manager = DenoisingManager()
        self.tile_manager = None
        self.adaptive_sampling = AdaptiveSamplingManager()
        self.lod_system = EnhancedLODSystem()
        self.performance_monitor = PerformanceMonitor() if enable_monitoring else None
        
        # Метрики
        self.current_metrics = PerformanceMetrics()
        self.performance_history = []
        
        # Запуск моніторингу
        if self.performance_monitor:
            self.performance_monitor.start_monitoring()
        
        logger.info("Розширений менеджер продуктивності ініціалізовано")
    
    def setup_tile_rendering(self, image_width: int, image_height: int, 
                           tile_size: int = 256) -> None:
        """Налаштувати рендеринг по тайлах"""
        self.tile_manager = TileManager(image_width, image_height, tile_size)
        logger.info(f"Рендеринг по тайлах налаштовано: {image_width}x{image_height}, тайли {tile_size}x{tile_size}")
    
    def render_with_optimization(self, scene_data: np.ndarray, 
                               render_settings: Dict[str, Any]) -> np.ndarray:
        """Рендеринг з оптимізацією продуктивності"""
        
        start_time = time.time()
        
        # Оцінка складності сцени
        complexity = self._assess_scene_complexity(scene_data)
        
        # Розрахунок адаптивних семплів
        noise_level = self.adaptive_sampling.estimate_noise_level(scene_data)
        time_budget = render_settings.get('time_budget', 1.0)
        adaptive_samples = self.adaptive_sampling.calculate_adaptive_samples(
            complexity, noise_level, time_budget
        )
        
        # Налаштування LOD
        distance = render_settings.get('camera_distance', 100.0)
        object_complexity = render_settings.get('object_complexity', 1.0)
        camera_speed = render_settings.get('camera_speed', 0.0)
        
        lod_level = self.lod_system.get_lod_level(distance, object_complexity, camera_speed)
        
        # Рендеринг з LOD
        if lod_level > 0:
            scene_data = self.lod_system.generate_lod_data(scene_data, lod_level)
        
        # Рендеринг по тайлах якщо налаштовано
        if self.tile_manager:
            result = self._render_with_tiles(scene_data, adaptive_samples, render_settings)
        else:
            result = self._render_standard(scene_data, adaptive_samples, render_settings)
        
        # Денойз якщо потрібно
        if render_settings.get('enable_denoising', True):
            denoising_algorithm = render_settings.get('denoising_algorithm', 'OPTIX')
            denoising_strength = render_settings.get('denoising_strength', 1.0)
            
            result = self.denoising_manager.denoise_image(
                result, denoising_algorithm, denoising_strength
            )
        
        # Оновлення метрик
        self._update_metrics(start_time, complexity, adaptive_samples, lod_level)
        
        return result
    
    def _assess_scene_complexity(self, scene_data: np.ndarray) -> float:
        """Оцінити складність сцени"""
        if len(scene_data.shape) == 3:
            gray = np.mean(scene_data, axis=2)
        else:
            gray = scene_data
        
        # Розрахунок варіації як міра складності
        complexity = np.std(gray) / 255.0
        
        # Нормалізувати до діапазону [0.1, 2.0]
        complexity = max(0.1, min(2.0, complexity * 2))
        
        return complexity
    
    def _render_with_tiles(self, scene_data: np.ndarray, samples: int, 
                          render_settings: Dict[str, Any]) -> np.ndarray:
        """Рендеринг з використанням тайлів"""
        
        if not self.tile_manager:
            return self._render_standard(scene_data, samples, render_settings)
        
        # Створити результуюче зображення
        result = np.zeros_like(scene_data)
        
        # Обробка тайлів
        while True:
            tile = self.tile_manager.get_next_tile()
            if tile is None:
                break
            
            # Розрахувати складність тайлу
            tile_complexity = self.tile_manager.get_tile_complexity(tile, scene_data)
            tile.samples = self.adaptive_sampling.calculate_adaptive_samples(
                tile_complexity, 0.0, 1.0
            )
            
            # Рендеринг тайлу
            tile_result = self._render_tile(scene_data, tile, render_settings)
            
            # Зберегти результат
            end_y = min(tile.y + tile.height, result.shape[0])
            end_x = min(tile.x + tile.width, result.shape[1])
            
            if len(result.shape) == 3:
                result[tile.y:end_y, tile.x:end_x, :] = tile_result
            else:
                result[tile.y:end_y, tile.x:end_x] = tile_result
            
            # Завершити тайл
            self.tile_manager.complete_tile(tile, tile_result)
        
        return result
    
    def _render_tile(self, scene_data: np.ndarray, tile: TileInfo, 
                    render_settings: Dict[str, Any]) -> np.ndarray:
        """Рендеринг окремого тайлу"""
        
        # Витягти дані тайлу
        end_y = min(tile.y + tile.height, scene_data.shape[0])
        end_x = min(tile.x + tile.width, scene_data.shape[1])
        
        if len(scene_data.shape) == 3:
            tile_data = scene_data[tile.y:end_y, tile.x:end_x, :]
        else:
            tile_data = scene_data[tile.y:end_y, tile.x:end_x]
        
        # Простий рендеринг тайлу (заглушка)
        # В реальній реалізації тут буде виклик рендер двигуна
        tile_result = tile_data.copy()
        
        # Додати шум для симуляції рендерингу
        noise = np.random.normal(0, 0.01, tile_result.shape)
        tile_result = np.clip(tile_result + noise, 0, 1)
        
        return tile_result
    
    def _render_standard(self, scene_data: np.ndarray, samples: int, 
                        render_settings: Dict[str, Any]) -> np.ndarray:
        """Стандартний рендеринг без тайлів"""
        
        # Простий рендеринг (заглушка)
        result = scene_data.copy()
        
        # Додати шум для симуляції рендерингу
        noise = np.random.normal(0, 0.01, result.shape)
        result = np.clip(result + noise, 0, 1)
        
        return result
    
    def _update_metrics(self, start_time: float, complexity: float, 
                       samples: int, lod_level: int):
        """Оновити метрики продуктивності"""
        
        generation_time = time.time() - start_time
        
        # Оновити поточні метрики
        self.current_metrics.generation_time = generation_time
        self.current_metrics.adaptive_samples = samples
        self.current_metrics.render_quality = 1.0 / (lod_level + 1)
        
        # Оновити використання ресурсів
        if self.performance_monitor:
            current_metrics = self.performance_monitor.get_current_metrics()
            self.current_metrics.cpu_usage = current_metrics.get('cpu_usage', 0.0)
            self.current_metrics.memory_usage = current_metrics.get('memory_usage', 0.0)
            self.current_metrics.gpu_usage = current_metrics.get('gpu_usage', 0.0)
            self.current_metrics.gpu_memory_usage = current_metrics.get('gpu_memory', 0.0)
        
        # Оновити статистику LOD
        lod_stats = self.lod_system.get_lod_statistics()
        self.current_metrics.lod_switches = lod_stats['lod_switches']
        
        # Оновити статистику тайлів
        if self.tile_manager:
            tile_progress = self.tile_manager.get_progress()
            self.current_metrics.tiles_processed = tile_progress['completed_tiles']
        
        # Зберегти в історію
        self.performance_history.append(self.current_metrics)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Отримати звіт про продуктивність"""
        
        report = {
            'current_metrics': {
                'generation_time': self.current_metrics.generation_time,
                'memory_usage': self.current_metrics.memory_usage,
                'gpu_memory_usage': self.current_metrics.gpu_memory_usage,
                'cpu_usage': self.current_metrics.cpu_usage,
                'gpu_usage': self.current_metrics.gpu_usage,
                'adaptive_samples': self.current_metrics.adaptive_samples,
                'render_quality': self.current_metrics.render_quality,
                'tiles_processed': self.current_metrics.tiles_processed,
                'lod_switches': self.current_metrics.lod_switches
            },
            'system_info': {
                'gpu_available': self.gpu_manager is not None and len(self.gpu_manager.gpus) > 0,
                'cpu_cores': self.cpu_manager.cpu_count,
                'monitoring_enabled': self.performance_monitor is not None
            }
        }
        
        # Додати рекомендації
        if self.performance_monitor:
            recommendations = self.performance_monitor.get_performance_recommendations()
            report['recommendations'] = recommendations
        
        # Додати статистику адаптивного семплування
        sampling_recs = self.adaptive_sampling.get_sampling_recommendations()
        report['sampling_recommendations'] = sampling_recs
        
        # Додати статистику LOD
        lod_stats = self.lod_system.get_lod_statistics()
        report['lod_statistics'] = lod_stats
        
        return report
    
    def optimize_settings(self, target_fps: float = 30.0) -> Dict[str, Any]:
        """Оптимізувати налаштування для досягнення цільового FPS"""
        
        recommendations = {}
        
        # Аналіз поточних метрик
        if self.performance_monitor:
            current_metrics = self.performance_monitor.get_current_metrics()
            
            # Оптимізація CPU
            cpu_usage = current_metrics.get('cpu_usage', 0.0)
            if cpu_usage > 80:
                recommendations['cpu_threads'] = max(1, self.cpu_manager.cpu_count // 2)
            elif cpu_usage < 30:
                recommendations['cpu_threads'] = self.cpu_manager.cpu_count
            
            # Оптимізація GPU
            gpu_usage = current_metrics.get('gpu_usage', 0.0)
            if gpu_usage > 90:
                recommendations['enable_denoising'] = True
                recommendations['denoising_strength'] = 1.5
                recommendations['reduce_samples'] = True
            
            # Оптимізація пам'яті
            memory_usage = current_metrics.get('memory_usage', 0.0)
            if memory_usage > 85:
                recommendations['enable_tiling'] = True
                recommendations['tile_size'] = 128
                recommendations['enable_lod'] = True
        
        # Рекомендації по семплуванню
        sampling_recs = self.adaptive_sampling.get_sampling_recommendations()
        if sampling_recs['recommendation'] == 'increase_samples':
            recommendations['base_samples'] = min(1024, self.adaptive_sampling.base_samples * 2)
        elif sampling_recs['recommendation'] == 'decrease_samples':
            recommendations['base_samples'] = max(32, self.adaptive_sampling.base_samples // 2)
        
        return recommendations
    
    def cleanup(self):
        """Очистити ресурси"""
        
        # Зупинити моніторинг
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()
        
        # Очистити CPU менеджер
        self.cpu_manager.cleanup_thread_pools()
        
        # Очистити кеші
        self.denoising_manager.denoising_cache.clear()
        self.lod_system.lod_cache.clear()
        
        logger.info("Ресурси очищено")


def benchmark_performance_manager():
    """Бенчмарк менеджера продуктивності"""
    
    print("Бенчмарк розширеного менеджера продуктивності...")
    
    # Тестові дані
    test_scene = np.random.random((512, 512, 3)).astype(np.float32)
    
    # Налаштування рендерингу
    render_settings = {
        'time_budget': 1.0,
        'camera_distance': 100.0,
        'object_complexity': 1.0,
        'camera_speed': 0.0,
        'enable_denoising': True,
        'denoising_algorithm': 'OPTIX',
        'denoising_strength': 1.0
    }
    
    # Тест з оптимізаціями
    manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)
    manager.setup_tile_rendering(512, 512, 128)
    
    start_time = time.time()
    result = manager.render_with_optimization(test_scene, render_settings)
    total_time = time.time() - start_time
    
    # Звіт
    report = manager.get_performance_report()
    print(f"\nРезультати бенчмарку:")
    print(f"  Час рендерингу: {total_time:.3f}s")
    print(f"  Адаптивні семпли: {report['current_metrics']['adaptive_samples']}")
    print(f"  Якість рендерингу: {report['current_metrics']['render_quality']:.2f}")
    print(f"  Оброблено тайлів: {report['current_metrics']['tiles_processed']}")
    print(f"  Переключень LOD: {report['current_metrics']['lod_switches']}")
    
    if 'recommendations' in report:
        print(f"\nРекомендації:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    # Очистити ресурси
    manager.cleanup()
    
    print("\nБенчмарк завершено!")


if __name__ == "__main__":
    # Запустити бенчмарк
    benchmark_performance_manager()