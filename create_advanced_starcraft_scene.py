#!/usr/bin/env python3
"""
Створення розширеної StarCraft сцени з використанням конфігурації
"""
import bpy
import os
import math
import random
import yaml

def load_config():
    """Завантаження конфігурації"""
    with open('params/pack.yaml', 'r') as f:
        return yaml.safe_load(f)

def clear_scene():
    """Очищення сцени"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Очищення матеріалів
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_terrain_with_palette(palette):
    """Створення терену з палітрою кольорів"""
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.name = "Terrain"
    
    # Використання палітри кольорів
    if isinstance(palette, list) and len(palette) >= 3:
        base_color = palette[1]  # Використовуємо середній колір
    else:
        base_color = [0.2, 0.4, 0.2]  # За замовчуванням
    
    mat = bpy.data.materials.new(name="Terrain_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*base_color, 1.0)
    terrain.data.materials.append(mat)
    
    return terrain

def create_unit_cluster(center, count, size_range, color, name_prefix):
    """Створення кластера юнітів"""
    units = []
    for i in range(count):
        # Випадкове розташування в межах кластера
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, 2)
        x = center[0] + distance * math.cos(angle)
        y = center[1] + distance * math.sin(angle)
        
        size = random.uniform(size_range[0], size_range[1])
        
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=(x, y, 0.5))
        unit = bpy.context.active_object
        unit.name = f"{name_prefix}_Unit_{i+1}"
        
        # Матеріал
        mat = bpy.data.materials.new(name=f"{unit.name}_Material")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*color, 1.0)
        unit.data.materials.append(mat)
        
        units.append(unit)
    
    return units

def create_portal_effect_advanced(center, radius, falloff, invert=False):
    """Створення розширеного портального ефекту"""
    # Основний портал
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius, 
        minor_radius=radius*0.1, 
        location=center
    )
    portal = bpy.context.active_object
    portal.name = "Portal"
    
    # Матеріал з емісією
    mat = bpy.data.materials.new(name="Portal_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[17].default_value = (0.5, 0.8, 1.0)  # Синій емісія
    mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 3.0  # Сила емісії
    portal.data.materials.append(mat)
    
    # Додаткові ефекти
    for i in range(3):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius + (i+1) * 0.3, 
            minor_radius=radius*0.05, 
            location=center
        )
        ring = bpy.context.active_object
        ring.name = f"Portal_Ring_{i+1}"
        
        # Прозорий матеріал
        ring_mat = bpy.data.materials.new(name=f"Portal_Ring_{i+1}_Material")
        ring_mat.use_nodes = True
        ring_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.6, 1.0, 0.3)
        ring_mat.blend_method = 'BLEND'
        ring.data.materials.append(ring_mat)
    
    return portal

def create_hud_advanced(left_info, right_info):
    """Створення розширеного HUD"""
    # Лівий HUD
    bpy.ops.mesh.primitive_plane_add(size=3, location=(-7, -4, 2))
    left_hud = bpy.context.active_object
    left_hud.name = "Left_HUD"
    
    # Правий HUD
    bpy.ops.mesh.primitive_plane_add(size=3, location=(7, -4, 2))
    right_hud = bpy.context.active_object
    right_hud.name = "Right_HUD"
    
    # Матеріали для HUD
    for hud, info in [(left_hud, left_info), (right_hud, right_info)]:
        mat = bpy.data.materials.new(name=f"{hud.name}_Material")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.05, 0.05, 0.9)
        mat.blend_method = 'BLEND'
        hud.data.materials.append(mat)
        
        # Додавання текстури з інформацією (симуляція)
        print(f"{hud.name}: {info}")

def setup_camera_advanced():
    """Розширене налаштування камери"""
    bpy.ops.object.camera_add(location=(10, -10, 8))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.0, 0, 0.785)
    bpy.context.scene.camera = camera
    return camera

def setup_lighting_advanced():
    """Розширене налаштування освітлення"""
    # Основне світло
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 4
    
    # Додаткове освітлення для порталу
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 4))
    area_light = bpy.context.active_object
    area_light.data.energy = 8
    area_light.data.color = (0.5, 0.8, 1.0)
    area_light.data.size = 2
    
    # Заповнювальне світло
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 3))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 2
    fill_light.data.color = (1.0, 0.9, 0.8)
    fill_light.data.size = 3
    
    return sun, area_light, fill_light

def main():
    print("🎬 Створення розширеної StarCraft сцени")
    print("=" * 50)
    
    # Завантаження конфігурації
    config = load_config()
    shot_config = config['shots'][0]  # Використовуємо перший шот
    
    print(f"📋 Конфігурація шоту: {shot_config['id']}")
    print(f"🎨 Палітра: {shot_config['palette']}")
    print(f"🌀 Портальний ефект: {shot_config['portal']}")
    
    # Очищення сцени
    clear_scene()
    
    # Створення терену з палітрою
    print("🌍 Створення терену з палітрою...")
    terrain = create_terrain_with_palette(shot_config['palette'])
    
    # Налаштування камери
    print("📷 Налаштування камери...")
    camera = setup_camera_advanced()
    
    # Налаштування освітлення
    print("💡 Налаштування освітлення...")
    sun, area_light, fill_light = setup_lighting_advanced()
    
    # Створення кластерів юнітів
    print("⚔️ Створення кластерів юнітів...")
    
    # Лівий кластер (Terran)
    left_center = (shot_config['left_cluster']['rect'][0] * 20 - 10, 
                   shot_config['left_cluster']['rect'][1] * 20 - 10,
                   0.5)  # Додаємо Z координату
    left_units = create_unit_cluster(
        left_center,
        shot_config['left_cluster']['count'],
        shot_config['left_cluster']['size'],
        [0.3, 0.5, 0.9],  # Синій колір для Terran
        "Terran"
    )
    
    # Правий кластер (Zerg)
    right_center = (shot_config['right_cluster']['rect'][0] * 20 - 10, 
                    shot_config['right_cluster']['rect'][1] * 20 - 10,
                    0.5)  # Додаємо Z координату
    right_units = create_unit_cluster(
        right_center,
        shot_config['right_cluster']['count'],
        shot_config['right_cluster']['size'],
        [0.7, 0.3, 0.7],  # Фіолетовий колір для Zerg
        "Zerg"
    )
    
    # Створення портального ефекту
    print("🌀 Створення портального ефекту...")
    portal_center = (shot_config['portal']['center'][0] * 20 - 10, 
                     shot_config['portal']['center'][1] * 20 - 10,
                     1)  # Додаємо Z координату
    portal = create_portal_effect_advanced(
        portal_center,
        shot_config['portal']['radius'] * 10,
        shot_config['portal']['falloff'],
        shot_config['portal']['invert']
    )
    
    # Створення HUD
    print("🖥️ Створення HUD...")
    create_hud_advanced(shot_config['hud']['left'], shot_config['hud']['right'])
    
    # Налаштування рендерингу
    print("⚙️ Налаштування рендерингу...")
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = config['image_size'][0]
    bpy.context.scene.render.resolution_y = config['image_size'][1]
    bpy.context.scene.render.filepath = "renders/blender/advanced_starcraft_scene.png"
    bpy.context.scene.cycles.use_denoising = False
    bpy.context.scene.cycles.samples = 128  # Зменшуємо для швидкості
    
    # Створення директорії
    os.makedirs("renders/blender", exist_ok=True)
    
    # Рендеринг
    print("🖼️ Рендеринг сцени...")
    bpy.ops.render.render(write_still=True)
    
    print("✅ Розширена StarCraft сцена створена успішно!")
    print(f"📁 Зображення збережено: renders/blender/advanced_starcraft_scene.png")
    print(f"⚔️ Лівий кластер (Terran): {len(left_units)} юнітів")
    print(f"⚔️ Правий кластер (Zerg): {len(right_units)} юнітів")
    print(f"🌀 Портальний ефект: створено")
    print(f"🖥️ HUD: налаштовано")

if __name__ == "__main__":
    main()