#!/usr/bin/env python3
"""
Advanced Terrain Generation Algorithms for StarCraft Maps
Розширені алгоритми генерації рельєфу для карт StarCraft

This module provides sophisticated terrain generation algorithms including:
- Height map generation using Perlin noise
- Multi-layer terrain composition
- Strategic terrain features (chokepoints, resources, etc.)
- Procedural texture blending
"""

import numpy as np
import math
import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TerrainType(Enum):
    """Типи рельєфу"""
    GRASSLAND = "grassland"
    DESERT = "desert"
    SNOW = "snow"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    WATER = "water"
    SWAMP = "swamp"
    VOLCANIC = "volcanic"


@dataclass
class TerrainFeature:
    """Окрема особливість рельєфу"""
    x: float
    y: float
    radius: float
    height: float
    terrain_type: TerrainType
    influence: float = 1.0


class PerlinNoise:
    """Реалізація шуму Перліна для генерації рельєфу"""
    
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Генерувати перестановки
        self.p = list(range(256))
        random.shuffle(self.p)
        self.p += self.p  # Дублювати для простоти
        
    def fade(self, t: float) -> float:
        """Функція затухання для плавності"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, t: float, a: float, b: float) -> float:
        """Лінійна інтерполяція"""
        return a + t * (b - a)
    
    def grad(self, hash_val: int, x: float, y: float) -> float:
        """Обчислити градієнт"""
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y
    
    def noise(self, x: float, y: float) -> float:
        """Генерувати шум Перліна для координат (x, y)"""
        # Знайти куб, що містить точку
        X = int(x) & 255
        Y = int(y) & 255
        
        # Локальні координати
        x -= int(x)
        y -= int(y)
        
        # Обчислити функції затухання
        u = self.fade(x)
        v = self.fade(y)
        
        # Хеші кутів куба
        A = self.p[X] + Y
        AA = self.p[A]
        AB = self.p[A + 1]
        B = self.p[X + 1] + Y
        BA = self.p[B]
        BB = self.p[B + 1]
        
        # Інтерполяція
        return self.lerp(v, 
                        self.lerp(u, self.grad(self.p[AA], x, y),
                                 self.grad(self.p[BA], x - 1, y)),
                        self.lerp(u, self.grad(self.p[AB], x, y - 1),
                                 self.grad(self.p[BB], x - 1, y - 1)))


class TerrainGenerator:
    """Генератор рельєфу з розширеними алгоритмами"""
    
    def __init__(self, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 1000000)
        self.noise = PerlinNoise(self.seed)
        
        # Масиви для зберігання даних рельєфу
        self.height_map = np.zeros((height, width), dtype=np.float32)
        self.terrain_type_map = np.zeros((height, width), dtype=np.int32)
        self.features = []
        
    def generate_height_map(self, 
                          octaves: int = 4,
                          persistence: float = 0.5,
                          lacunarity: float = 2.0,
                          scale: float = 50.0) -> np.ndarray:
        """Генерувати карту висот з використанням фрактального шуму"""
        
        max_value = 0.0
        amplitude = 1.0
        frequency = 1.0
        
        # Обчислити максимальне значення для нормалізації
        for _ in range(octaves):
            max_value += amplitude
            amplitude *= persistence
        
        # Генерувати шум для кожного пікселя
        for y in range(self.height):
            for x in range(self.width):
                value = 0.0
                amplitude = 1.0
                frequency = 1.0
                
                for _ in range(octaves):
                    sample_x = x / scale * frequency
                    sample_y = y / scale * frequency
                    
                    noise_value = self.noise.noise(sample_x, sample_y)
                    value += noise_value * amplitude
                    
                    amplitude *= persistence
                    frequency *= lacunarity
                
                # Нормалізувати значення
                self.height_map[y, x] = value / max_value
        
        return self.height_map
    
    def add_terrain_features(self, features: List[TerrainFeature]):
        """Додати особливості рельєфу (гори, долини, водойми)"""
        self.features.extend(features)
        
        for feature in features:
            self._apply_feature(feature)
    
    def _apply_feature(self, feature: TerrainFeature):
        """Застосувати особливість рельєфу до карти висот"""
        center_x = int(feature.x * self.width)
        center_y = int(feature.y * self.height)
        radius = int(feature.radius * min(self.width, self.height))
        
        # Обчислити область впливу
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance <= radius:
                        # Обчислити силу впливу
                        influence = 1.0 - (distance / radius)
                        influence = math.pow(influence, 2)  # Квадратичне затухання
                        influence *= feature.influence
                        
                        # Застосувати вплив на висоту
                        self.height_map[y, x] += feature.height * influence
                        
                        # Оновити тип рельєфу
                        if influence > 0.5:
                            self.terrain_type_map[y, x] = feature.terrain_type.value
    
    def generate_strategic_features(self, 
                                  chokepoints: int = 3,
                                  resource_nodes: int = 5,
                                  base_locations: int = 2):
        """Генерувати стратегічні особливості карти"""
        
        # Генерувати вузькі проходи (chokepoints)
        for _ in range(chokepoints):
            x = random.uniform(0.2, 0.8)
            y = random.uniform(0.2, 0.8)
            
            # Створити вузький прохід
            feature = TerrainFeature(
                x=x, y=y,
                radius=0.05,
                height=-0.3,  # Нижча висота
                terrain_type=TerrainType.WATER,
                influence=1.0
            )
            self.add_terrain_features([feature])
        
        # Генерувати ресурсні вузли
        for _ in range(resource_nodes):
            x = random.uniform(0.1, 0.9)
            y = random.uniform(0.1, 0.9)
            
            feature = TerrainFeature(
                x=x, y=y,
                radius=0.08,
                height=0.1,
                terrain_type=TerrainType.MOUNTAIN,
                influence=0.8
            )
            self.add_terrain_features([feature])
        
        # Генерувати місця для баз
        for _ in range(base_locations):
            x = random.uniform(0.1, 0.9)
            y = random.uniform(0.1, 0.9)
            
            feature = TerrainFeature(
                x=x, y=y,
                radius=0.15,
                height=0.0,  # Рівна поверхня
                terrain_type=TerrainType.GRASSLAND,
                influence=1.0
            )
            self.add_terrain_features([feature])
    
    def generate_terrain_type_map(self) -> np.ndarray:
        """Генерувати карту типів рельєфу на основі висоти та особливостей"""
        
        for y in range(self.height):
            for x in range(self.width):
                height = self.height_map[y, x]
                
                # Визначити тип рельєфу на основі висоти
                if height < -0.3:
                    terrain_type = TerrainType.WATER
                elif height < -0.1:
                    terrain_type = TerrainType.SWAMP
                elif height < 0.1:
                    terrain_type = TerrainType.GRASSLAND
                elif height < 0.3:
                    terrain_type = TerrainType.FOREST
                elif height < 0.6:
                    terrain_type = TerrainType.MOUNTAIN
                else:
                    terrain_type = TerrainType.VOLCANIC
                
                self.terrain_type_map[y, x] = terrain_type.value
        
        return self.terrain_type_map
    
    def smooth_terrain(self, iterations: int = 2):
        """Згладжувати рельєф для більш природного вигляду"""
        
        for _ in range(iterations):
            new_height_map = self.height_map.copy()
            
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    # Середнє значення з сусідніх пікселів
                    neighbors = [
                        self.height_map[y-1, x-1], self.height_map[y-1, x], self.height_map[y-1, x+1],
                        self.height_map[y, x-1],   self.height_map[y, x],   self.height_map[y, x+1],
                        self.height_map[y+1, x-1], self.height_map[y+1, x], self.height_map[y+1, x+1]
                    ]
                    new_height_map[y, x] = sum(neighbors) / len(neighbors)
            
            self.height_map = new_height_map
    
    def export_height_map(self, filename: str):
        """Експортувати карту висот як зображення"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 10))
        plt.imshow(self.height_map, cmap='terrain', origin='lower')
        plt.colorbar(label='Height')
        plt.title('Generated Height Map')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
    
    def export_terrain_type_map(self, filename: str):
        """Експортувати карту типів рельєфу"""
        import matplotlib.pyplot as plt
        
        terrain_colors = {
            TerrainType.WATER.value: 'blue',
            TerrainType.SWAMP.value: 'darkgreen',
            TerrainType.GRASSLAND.value: 'lightgreen',
            TerrainType.FOREST.value: 'green',
            TerrainType.MOUNTAIN.value: 'brown',
            TerrainType.VOLCANIC.value: 'red'
        }
        
        # Створити кольорову карту
        colored_map = np.zeros((self.height, self.width, 3))
        for y in range(self.height):
            for x in range(self.width):
                terrain_type = self.terrain_type_map[y, x]
                color = terrain_colors.get(terrain_type, 'gray')
                if color == 'blue':
                    colored_map[y, x] = [0, 0, 1]
                elif color == 'darkgreen':
                    colored_map[y, x] = [0, 0.5, 0]
                elif color == 'lightgreen':
                    colored_map[y, x] = [0.5, 1, 0.5]
                elif color == 'green':
                    colored_map[y, x] = [0, 1, 0]
                elif color == 'brown':
                    colored_map[y, x] = [0.6, 0.3, 0.1]
                elif color == 'red':
                    colored_map[y, x] = [1, 0, 0]
                else:
                    colored_map[y, x] = [0.5, 0.5, 0.5]
        
        plt.figure(figsize=(10, 10))
        plt.imshow(colored_map, origin='lower')
        plt.title('Terrain Type Map')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()


def create_sample_terrain(width: int = 512, height: int = 512) -> TerrainGenerator:
    """Створити зразковий рельєф для тестування"""
    
    generator = TerrainGenerator(width, height)
    
    # Генерувати базову карту висот
    generator.generate_height_map(
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        scale=100.0
    )
    
    # Додати стратегічні особливості
    generator.generate_strategic_features(
        chokepoints=4,
        resource_nodes=8,
        base_locations=3
    )
    
    # Згладжувати рельєф
    generator.smooth_terrain(iterations=3)
    
    # Генерувати карту типів рельєфу
    generator.generate_terrain_type_map()
    
    return generator


if __name__ == "__main__":
    # Приклад використання
    print("Генерація зразкового рельєфу...")
    
    terrain = create_sample_terrain(256, 256)
    
    # Експортувати карти
    terrain.export_height_map("height_map.png")
    terrain.export_terrain_type_map("terrain_types.png")
    
    print("Рельєф згенеровано та збережено!")
    print(f"Розмір: {terrain.width}x{terrain.height}")
    print(f"Кількість особливостей: {len(terrain.features)}")