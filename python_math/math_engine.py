#!/usr/bin/env python3
"""
Python математичний движок для 3D геометрії
Сумісний з USD генератором сцен
"""

import math
import random
from typing import List, Tuple, Union
from dataclasses import dataclass

# Константи
PI = math.pi
TWO_PI = 2.0 * PI
HALF_PI = PI / 2.0
DEG_TO_RAD = PI / 180.0
RAD_TO_DEG = 180.0 / PI
EPSILON = 1e-6

@dataclass
class Vec2:
    """2D вектор"""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vec2':
        return Vec2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vec2':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vec2':
        return Vec2(self.x / scalar, self.y / scalar)
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y
    
    def normalized(self) -> 'Vec2':
        length = self.length()
        if length > 0:
            return Vec2(self.x / length, self.y / length)
        return Vec2(0, 0)
    
    def dot(self, other: 'Vec2') -> float:
        return self.x * other.x + self.y * other.y
    
    def distance(self, other: 'Vec2') -> float:
        return (self - other).length()
    
    def lerp(self, other: 'Vec2', t: float) -> 'Vec2':
        return self + (other - self) * t
    
    @staticmethod
    def zero() -> 'Vec2':
        return Vec2(0, 0)
    
    @staticmethod
    def one() -> 'Vec2':
        return Vec2(1, 1)
    
    def __str__(self) -> str:
        return f"Vec2({self.x}, {self.y})"

@dataclass
class Vec3:
    """3D вектор"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vec3':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def normalized(self) -> 'Vec3':
        length = self.length()
        if length > 0:
            return Vec3(self.x / length, self.y / length, self.z / length)
        return Vec3(0, 0, 0)
    
    def dot(self, other: 'Vec3') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vec3') -> 'Vec3':
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def distance(self, other: 'Vec3') -> float:
        return (self - other).length()
    
    def lerp(self, other: 'Vec3', t: float) -> 'Vec3':
        return self + (other - self) * t
    
    @staticmethod
    def zero() -> 'Vec3':
        return Vec3(0, 0, 0)
    
    @staticmethod
    def one() -> 'Vec3':
        return Vec3(1, 1, 1)
    
    @staticmethod
    def up() -> 'Vec3':
        return Vec3(0, 1, 0)
    
    @staticmethod
    def down() -> 'Vec3':
        return Vec3(0, -1, 0)
    
    @staticmethod
    def left() -> 'Vec3':
        return Vec3(-1, 0, 0)
    
    @staticmethod
    def right() -> 'Vec3':
        return Vec3(1, 0, 0)
    
    @staticmethod
    def forward() -> 'Vec3':
        return Vec3(0, 0, 1)
    
    @staticmethod
    def back() -> 'Vec3':
        return Vec3(0, 0, -1)
    
    def __str__(self) -> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

@dataclass
class Transform:
    """3D трансформація"""
    position: Vec3 = None
    rotation: Vec3 = None  # Euler angles in radians
    scale: Vec3 = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = Vec3(0, 0, 0)
        if self.rotation is None:
            self.rotation = Vec3(0, 0, 0)
        if self.scale is None:
            self.scale = Vec3(1, 1, 1)
    
    def get_forward(self) -> Vec3:
        """Отримати напрямок вперед"""
        # Простий розрахунок для Y-повороту
        yaw = self.rotation.y
        return Vec3(math.sin(yaw), 0, math.cos(yaw))
    
    def get_right(self) -> Vec3:
        """Отримати напрямок вправо"""
        forward = self.get_forward()
        return forward.cross(Vec3.up())
    
    def get_up(self) -> Vec3:
        """Отримати напрямок вгору"""
        right = self.get_right()
        forward = self.get_forward()
        return right.cross(forward)
    
    def look_at(self, target: Vec3, up: Vec3 = Vec3.up()) -> None:
        """Направити на ціль"""
        direction = (target - self.position).normalized()
        
        # Обчислити кути повороту
        yaw = math.atan2(direction.x, direction.z)
        pitch = math.asin(-direction.y)
        
        self.rotation = Vec3(pitch, yaw, 0)
    
    def transform_point(self, point: Vec3) -> Vec3:
        """Трансформувати точку"""
        # Простий розрахунок трансформації
        # В реальній реалізації використовували б матриці
        return point + self.position
    
    def distance_to(self, other: 'Transform') -> float:
        """Відстань до іншої трансформації"""
        return self.position.distance(other.position)
    
    def __str__(self) -> str:
        return f"Transform(pos={self.position}, rot={self.rotation}, scale={self.scale})"

class FormationGenerator:
    """Генератор формацій юнітів"""
    
    @staticmethod
    def create_line_formation(start: Vec3, end: Vec3, count: int) -> List[Vec3]:
        """Створити лінійну формацію"""
        if count <= 0:
            return []
        
        if count == 1:
            return [start]
        
        direction = (end - start) / (count - 1)
        positions = []
        
        for i in range(count):
            position = start + direction * i
            positions.append(position)
        
        return positions
    
    @staticmethod
    def create_arc_formation(center: Vec3, radius: float, start_angle: float, 
                           end_angle: float, count: int) -> List[Vec3]:
        """Створити дугову формацію"""
        if count <= 0:
            return []
        
        if count == 1:
            return [center]
        
        angle_step = (end_angle - start_angle) / (count - 1)
        positions = []
        
        for i in range(count):
            angle = start_angle + angle_step * i
            offset = Vec3(
                radius * math.cos(angle),
                0,
                radius * math.sin(angle)
            )
            positions.append(center + offset)
        
        return positions
    
    @staticmethod
    def create_circle_formation(center: Vec3, radius: float, count: int) -> List[Vec3]:
        """Створити кругову формацію"""
        return FormationGenerator.create_arc_formation(center, radius, 0, TWO_PI, count)
    
    @staticmethod
    def create_grid_formation(center: Vec3, rows: int, cols: int, spacing: float) -> List[Vec3]:
        """Створити сіткову формацію"""
        if rows <= 0 or cols <= 0:
            return []
        
        start = center - Vec3(
            (cols - 1) * spacing * 0.5,
            0,
            (rows - 1) * spacing * 0.5
        )
        
        positions = []
        for row in range(rows):
            for col in range(cols):
                position = start + Vec3(col * spacing, 0, row * spacing)
                positions.append(position)
        
        return positions
    
    @staticmethod
    def create_random_formation(bounds_min: Vec3, bounds_max: Vec3, count: int) -> List[Vec3]:
        """Створити випадкову формацію"""
        if count <= 0:
            return []
        
        size = bounds_max - bounds_min
        positions = []
        
        for _ in range(count):
            position = Vec3(
                bounds_min.x + random.random() * size.x,
                bounds_min.y + random.random() * size.y,
                bounds_min.z + random.random() * size.z
            )
            positions.append(position)
        
        return positions

class Camera:
    """3D камера"""
    
    def __init__(self, position: Vec3 = Vec3(0, 0, 0), target: Vec3 = Vec3(0, 0, 0)):
        self.position = position
        self.target = target
        self.up = Vec3.up()
        self.fov = 60.0  # degrees
        self.aspect = 16.0 / 9.0
        self.near = 0.1
        self.far = 1000.0
    
    def look_at(self, target: Vec3, up: Vec3 = Vec3.up()) -> None:
        """Направити камеру на ціль"""
        self.target = target
        self.up = up
    
    def get_forward(self) -> Vec3:
        """Отримати напрямок вперед"""
        return (self.target - self.position).normalized()
    
    def get_right(self) -> Vec3:
        """Отримати напрямок вправо"""
        forward = self.get_forward()
        return forward.cross(self.up).normalized()
    
    def get_up(self) -> Vec3:
        """Отримати напрямок вгору"""
        right = self.get_right()
        forward = self.get_forward()
        return right.cross(forward).normalized()
    
    def move_forward(self, distance: float) -> None:
        """Рух вперед"""
        self.position += self.get_forward() * distance
    
    def move_right(self, distance: float) -> None:
        """Рух вправо"""
        self.position += self.get_right() * distance
    
    def move_up(self, distance: float) -> None:
        """Рух вгору"""
        self.position += self.get_up() * distance
    
    def rotate_around_target(self, angle_x: float, angle_y: float) -> None:
        """Поворот навколо цілі"""
        # Простий поворот навколо цілі
        direction = self.position - self.target
        distance = direction.length()
        
        # Поворот по Y (yaw)
        yaw = math.atan2(direction.x, direction.z) + angle_y
        # Поворот по X (pitch)
        pitch = math.asin(direction.y / distance) + angle_x
        pitch = max(-HALF_PI + 0.1, min(HALF_PI - 0.1, pitch))
        
        # Обчислити нову позицію
        new_direction = Vec3(
            distance * math.cos(pitch) * math.sin(yaw),
            distance * math.sin(pitch),
            distance * math.cos(pitch) * math.cos(yaw)
        )
        
        self.position = self.target + new_direction

class GeometryUtils:
    """Утиліти для геометрії"""
    
    @staticmethod
    def distance_point_to_point(a: Vec3, b: Vec3) -> float:
        """Відстань між двома точками"""
        return a.distance(b)
    
    @staticmethod
    def distance_point_to_line(point: Vec3, line_start: Vec3, line_end: Vec3) -> float:
        """Відстань від точки до лінії"""
        line = line_end - line_start
        line_length = line.length()
        
        if line_length < EPSILON:
            return point.distance(line_start)
        
        line_dir = line / line_length
        point_to_start = point - line_start
        t = point_to_start.dot(line_dir)
        t = max(0.0, min(1.0, t))
        
        closest_point = line_start + line_dir * t
        return point.distance(closest_point)
    
    @staticmethod
    def is_point_in_sphere(point: Vec3, center: Vec3, radius: float) -> bool:
        """Перевірити чи точка в сфері"""
        return point.distance(center) <= radius
    
    @staticmethod
    def is_point_in_aabb(point: Vec3, min_point: Vec3, max_point: Vec3) -> bool:
        """Перевірити чи точка в AABB"""
        return (min_point.x <= point.x <= max_point.x and
                min_point.y <= point.y <= max_point.y and
                min_point.z <= point.z <= max_point.z)

# Утилітарні функції
def degrees_to_radians(degrees: float) -> float:
    """Конвертувати градуси в радіани"""
    return degrees * DEG_TO_RAD

def radians_to_degrees(radians: float) -> float:
    """Конвертувати радіани в градуси"""
    return radians * RAD_TO_DEG

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Обмежити значення"""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """Лінійна інтерполяція"""
    return a + (b - a) * t

def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Плавна інтерполяція"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def random_direction() -> Vec3:
    """Випадковий напрямок"""
    theta = random.random() * TWO_PI
    phi = random.random() * PI
    return Vec3(
        math.sin(phi) * math.cos(theta),
        math.cos(phi),
        math.sin(phi) * math.sin(theta)
    )

def random_point_in_sphere(radius: float) -> Vec3:
    """Випадкова точка в сфері"""
    return random_direction() * (random.random() * radius)

# Приклад використання
if __name__ == "__main__":
    print("Python Math Engine Test")
    print("======================")
    
    # Тест векторів
    v1 = Vec3(1, 2, 3)
    v2 = Vec3(4, 5, 6)
    print(f"Vec3 addition: {v1} + {v2} = {v1 + v2}")
    print(f"Dot product: {v1} · {v2} = {v1.dot(v2)}")
    print(f"Cross product: {v1} × {v2} = {v1.cross(v2)}")
    
    # Тест формацій
    line = FormationGenerator.create_line_formation(
        Vec3(0, 0, 0), Vec3(20, 0, 0), 5
    )
    print(f"\nLine formation: {line}")
    
    circle = FormationGenerator.create_circle_formation(
        Vec3(0, 0, 0), 10, 8
    )
    print(f"Circle formation: {circle}")
    
    # Тест камери
    camera = Camera(Vec3(0, 5, 10), Vec3(0, 0, 0))
    print(f"\nCamera position: {camera.position}")
    print(f"Camera forward: {camera.get_forward()}")
    
    print("\nMath engine test completed!")