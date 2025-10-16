#!/usr/bin/env python3
"""
Тест математичного движка
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_math'))

from math_engine import *

def test_vectors():
    print("=== Testing Vectors ===")
    
    # Vec2 tests
    v2a = Vec2(1, 2)
    v2b = Vec2(3, 4)
    v2c = v2a + v2b
    print(f"Vec2 addition: {v2a} + {v2b} = {v2c}")
    
    # Vec3 tests
    v3a = Vec3(1, 2, 3)
    v3b = Vec3(4, 5, 6)
    v3c = v3a + v3b
    print(f"Vec3 addition: {v3a} + {v3b} = {v3c}")
    
    # Dot product
    dot = v3a.dot(v3b)
    print(f"Dot product: {v3a} · {v3b} = {dot}")
    
    # Cross product
    cross = v3a.cross(v3b)
    print(f"Cross product: {v3a} × {v3b} = {cross}")
    
    # Length and normalization
    length = v3a.length()
    normalized = v3a.normalized()
    print(f"Length of {v3a} = {length}")
    print(f"Normalized: {normalized}")
    
    print()

def test_transforms():
    print("=== Testing Transforms ===")
    
    transform = Transform()
    transform.position = Vec3(5, 10, 15)
    transform.rotation = Vec3(0, degrees_to_radians(45), 0)
    transform.scale = Vec3(2, 2, 2)
    
    print(f"Transform position: {transform.position}")
    print(f"Transform rotation: {transform.rotation}")
    print(f"Transform scale: {transform.scale}")
    
    point = Vec3(1, 0, 0)
    transformed = transform.transform_point(point)
    print(f"Point {point} transformed = {transformed}")
    
    forward = transform.get_forward()
    print(f"Forward direction: {forward}")
    
    print()

def test_formations():
    print("=== Testing Formations ===")
    
    # Line formation
    line = FormationGenerator.create_line_formation(
        Vec3(0, 0, 0), Vec3(20, 0, 0), 6
    )
    print(f"Line formation (6 units):")
    for i, pos in enumerate(line):
        print(f"  Unit {i}: {pos}")
    
    # Arc formation
    arc = FormationGenerator.create_arc_formation(
        Vec3(0, 0, 0), 10, 0, PI, 5
    )
    print(f"\nArc formation (5 units, 180 degrees):")
    for i, pos in enumerate(arc):
        print(f"  Unit {i}: {pos}")
    
    # Circle formation
    circle = FormationGenerator.create_circle_formation(
        Vec3(0, 0, 0), 8, 8
    )
    print(f"\nCircle formation (8 units):")
    for i, pos in enumerate(circle):
        print(f"  Unit {i}: {pos}")
    
    # Grid formation
    grid = FormationGenerator.create_grid_formation(
        Vec3(0, 0, 0), 3, 4, 2.0
    )
    print(f"\nGrid formation (3x4, spacing 2):")
    for i, pos in enumerate(grid):
        print(f"  Unit {i}: {pos}")
    
    print()

def test_camera():
    print("=== Testing Camera ===")
    
    camera = Camera(Vec3(0, 5, 10), Vec3(0, 0, 0))
    print(f"Camera position: {camera.position}")
    print(f"Camera target: {camera.target}")
    print(f"Camera forward: {camera.get_forward()}")
    print(f"Camera right: {camera.get_right()}")
    print(f"Camera up: {camera.get_up()}")
    
    # Test movement
    camera.move_forward(5)
    print(f"After moving forward 5: {camera.position}")
    
    camera.move_right(3)
    print(f"After moving right 3: {camera.position}")
    
    # Test rotation
    camera.rotate_around_target(0.1, 0.2)
    print(f"After rotation: {camera.position}")
    
    print()

def test_geometry():
    print("=== Testing Geometry ===")
    
    # Distance tests
    distance = GeometryUtils.distance_point_to_point(Vec3(0, 0, 0), Vec3(3, 4, 0))
    print(f"Distance between points: {distance}")
    
    # Point in sphere test
    in_sphere = GeometryUtils.is_point_in_sphere(Vec3(2, 0, 0), Vec3(0, 0, 0), 5)
    print(f"Point (2,0,0) in sphere (center=0,0,0, radius=5): {in_sphere}")
    
    # Point in AABB test
    in_aabb = GeometryUtils.is_point_in_aabb(Vec3(0.5, 0.5, 0.5), Vec3(0, 0, 0), Vec3(1, 1, 1))
    print(f"Point (0.5,0.5,0.5) in AABB (0,0,0) to (1,1,1): {in_aabb}")
    
    print()

def test_utilities():
    print("=== Testing Utilities ===")
    
    # Angle conversion
    degrees = 90
    radians = degrees_to_radians(degrees)
    back_to_degrees = radians_to_degrees(radians)
    print(f"Degrees to radians: {degrees}° = {radians} rad = {back_to_degrees}°")
    
    # Clamping
    value = 15.5
    clamped = clamp(value, 0, 10)
    print(f"Clamp {value} to [0, 10]: {clamped}")
    
    # Lerp
    lerped = lerp(0, 10, 0.3)
    print(f"Lerp from 0 to 10 at t=0.3: {lerped}")
    
    # Smoothstep
    smooth = smoothstep(0, 10, 5)
    print(f"Smoothstep at 5 in [0, 10]: {smooth}")
    
    # Random direction
    random_dir = random_direction()
    print(f"Random direction: {random_dir}")
    print(f"Random direction length: {random_dir.length()}")
    
    print()

def test_scene_generation():
    print("=== Testing Scene Generation ===")
    
    # Створити тестову конфігурацію
    config = {
        'scene': {
            'name': 'Test Scene',
            'size': [100, 100],
            'terrain': {
                'type': 'grassland',
                'height_variation': 0.2
            },
            'lighting': {
                'sun_angle': [45, 30],
                'ambient': 0.3,
                'sun_intensity': 1.0
            }
        },
        'units': {
            'army_1': {
                'color': [0.2, 0.4, 0.8],
                'spawn_area': [10, 10, 30, 30],
                'units': [
                    {'type': 'warrior', 'count': 5, 'formation': 'line', 'spacing': 2.0},
                    {'type': 'archer', 'count': 3, 'formation': 'arc', 'spacing': 1.5}
                ]
            },
            'army_2': {
                'color': [0.8, 0.2, 0.2],
                'spawn_area': [60, 60, 80, 80],
                'units': [
                    {'type': 'warrior', 'count': 4, 'formation': 'circle', 'spacing': 2.0},
                    {'type': 'mage', 'count': 2, 'formation': 'grid', 'spacing': 3.0}
                ]
            }
        },
        'camera': {
            'position': [50, 50, 80],
            'target': [50, 50, 0],
            'fov': 60
        }
    }
    
    # Тестувати генерацію позицій для різних формацій
    print("Testing formation generation for different unit types:")
    
    for army_name, army_config in config['units'].items():
        print(f"\n{army_name}:")
        spawn_area = army_config['spawn_area']
        
        for unit_config in army_config['units']:
            unit_type = unit_config['type']
            count = unit_config['count']
            formation = unit_config['formation']
            spacing = unit_config['spacing']
            
            # Генерувати позиції
            positions = generate_unit_positions(spawn_area, count, formation, spacing)
            
            print(f"  {unit_type} ({count} units, {formation}):")
            for i, pos in enumerate(positions):
                print(f"    Unit {i}: ({pos[0]:.2f}, {pos[1]:.2f})")
    
    print()

def generate_unit_positions(spawn_area, count, formation, spacing):
    """Генерувати позиції для юнітів згідно формації"""
    x1, y1, x2, y2 = spawn_area
    positions = []
    
    # Конвертуємо в 3D координати для математичного движка
    start_3d = Vec3(x1, 0, y1)
    end_3d = Vec3(x2, 0, y2)
    center_3d = Vec3((x1 + x2) / 2, 0, (y1 + y2) / 2)
    radius = min(x2 - x1, y2 - y1) / 3
    
    if formation == 'line':
        line_positions = FormationGenerator.create_line_formation(start_3d, end_3d, count)
        positions = [(pos.x, pos.z) for pos in line_positions]
    elif formation == 'arc':
        arc_positions = FormationGenerator.create_arc_formation(
            center_3d, radius, 0, PI, count
        )
        positions = [(pos.x, pos.z) for pos in arc_positions]
    elif formation == 'circle':
        circle_positions = FormationGenerator.create_circle_formation(
            center_3d, radius, count
        )
        positions = [(pos.x, pos.z) for pos in circle_positions]
    elif formation == 'grid':
        rows = int(math.sqrt(count))
        cols = (count + rows - 1) // rows
        grid_positions = FormationGenerator.create_grid_formation(
            center_3d, rows, cols, spacing
        )
        positions = [(pos.x, pos.z) for pos in grid_positions[:count]]
    else:  # random
        min_3d = Vec3(x1, 0, y1)
        max_3d = Vec3(x2, 0, y2)
        random_positions = FormationGenerator.create_random_formation(
            min_3d, max_3d, count
        )
        positions = [(pos.x, pos.z) for pos in random_positions]
    
    return positions

def main():
    print("Math Engine Test Suite")
    print("=====================")
    print()
    
    test_vectors()
    test_transforms()
    test_formations()
    test_camera()
    test_geometry()
    test_utilities()
    test_scene_generation()
    
    print("All tests completed!")

if __name__ == "__main__":
    main()