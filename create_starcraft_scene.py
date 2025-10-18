#!/usr/bin/env python3
"""
Створення StarCraft сцени з використанням Blender
"""
import bpy
import os
import math
import random

def clear_scene():
    """Очищення сцени"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Очищення матеріалів
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_terrain():
    """Створення терену"""
    # Створення великої площини для терену
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.name = "Terrain"
    
    # Додавання матеріалу для терену
    mat = bpy.data.materials.new(name="Terrain_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.4, 0.2, 1.0)  # Темно-зелений
    terrain.data.materials.append(mat)
    
    return terrain

def create_building(position, size, color, name):
    """Створення будівлі"""
    bpy.ops.mesh.primitive_cube_add(size=size, location=position)
    building = bpy.context.active_object
    building.name = name
    
    # Додавання матеріалу
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    building.data.materials.append(mat)
    
    return building

def create_unit(position, size, color, name):
    """Створення юніта"""
    bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=position)
    unit = bpy.context.active_object
    unit.name = name
    
    # Додавання матеріалу
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    unit.data.materials.append(mat)
    
    return unit

def create_portal_effect(center, radius):
    """Створення портального ефекту"""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius, 
        minor_radius=radius*0.1, 
        location=center
    )
    portal = bpy.context.active_object
    portal.name = "Portal"
    
    # Додавання матеріалу з емісією
    mat = bpy.data.materials.new(name="Portal_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[17].default_value = (0.5, 0.8, 1.0)  # Синій емісія
    mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 2.0  # Сила емісії
    portal.data.materials.append(mat)
    
    return portal

def setup_camera():
    """Налаштування камери"""
    bpy.ops.object.camera_add(location=(8, -8, 6))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    bpy.context.scene.camera = camera
    return camera

def setup_lighting():
    """Налаштування освітлення"""
    # Основне світло
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3
    
    # Додаткове світло для порталу
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
    area_light = bpy.context.active_object
    area_light.data.energy = 5
    area_light.data.color = (0.5, 0.8, 1.0)  # Синій колір
    
    return sun, area_light

def create_hud_elements():
    """Створення HUD елементів (простих площин)"""
    # Лівий HUD
    bpy.ops.mesh.primitive_plane_add(size=2, location=(-6, -3, 2))
    left_hud = bpy.context.active_object
    left_hud.name = "Left_HUD"
    left_hud.rotation_euler = (0, 0, 0)
    
    # Правий HUD
    bpy.ops.mesh.primitive_plane_add(size=2, location=(6, -3, 2))
    right_hud = bpy.context.active_object
    right_hud.name = "Right_HUD"
    right_hud.rotation_euler = (0, 0, 0)
    
    # Матеріали для HUD
    for hud in [left_hud, right_hud]:
        mat = bpy.data.materials.new(name=f"{hud.name}_Material")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.1, 0.1, 0.8)  # Темний напівпрозорий
        hud.data.materials.append(mat)

def main():
    print("🎬 Створення StarCraft сцени")
    print("=" * 40)
    
    # Очищення сцени
    clear_scene()
    
    # Створення терену
    print("🌍 Створення терену...")
    terrain = create_terrain()
    
    # Налаштування камери
    print("📷 Налаштування камери...")
    camera = setup_camera()
    
    # Налаштування освітлення
    print("💡 Налаштування освітлення...")
    sun, area_light = setup_lighting()
    
    # Створення будівель
    print("🏗️ Створення будівель...")
    buildings = []
    
    # Terran будівлі (сині)
    terran_positions = [(-4, 2, 1), (-2, 3, 1), (-6, 1, 1)]
    for i, pos in enumerate(terran_positions):
        building = create_building(
            pos, 
            1.5, 
            (0.2, 0.4, 0.8, 1.0), 
            f"Terran_Building_{i+1}"
        )
        buildings.append(building)
    
    # Zerg будівлі (фіолетові)
    zerg_positions = [(4, -2, 1), (6, -1, 1), (2, -3, 1)]
    for i, pos in enumerate(zerg_positions):
        building = create_building(
            pos, 
            1.2, 
            (0.6, 0.2, 0.6, 1.0), 
            f"Zerg_Building_{i+1}"
        )
        buildings.append(building)
    
    # Створення юнітів
    print("⚔️ Створення юнітів...")
    units = []
    
    # Terran юніти (сині)
    for i in range(8):
        x = random.uniform(-5, -1)
        y = random.uniform(0, 4)
        unit = create_unit(
            (x, y, 0.5), 
            0.3, 
            (0.3, 0.5, 0.9, 1.0), 
            f"Terran_Unit_{i+1}"
        )
        units.append(unit)
    
    # Zerg юніти (фіолетові)
    for i in range(6):
        x = random.uniform(1, 5)
        y = random.uniform(-4, 0)
        unit = create_unit(
            (x, y, 0.5), 
            0.25, 
            (0.7, 0.3, 0.7, 1.0), 
            f"Zerg_Unit_{i+1}"
        )
        units.append(unit)
    
    # Створення портального ефекту
    print("🌀 Створення портального ефекту...")
    portal = create_portal_effect((0, 0, 1), 1.5)
    
    # Створення HUD елементів
    print("🖥️ Створення HUD елементів...")
    create_hud_elements()
    
    # Налаштування рендерингу
    print("⚙️ Налаштування рендерингу...")
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.filepath = "renders/blender/starcraft_scene.png"
    bpy.context.scene.cycles.use_denoising = False
    bpy.context.scene.cycles.samples = 256  # Зменшуємо для швидкості
    
    # Створення директорії
    os.makedirs("renders/blender", exist_ok=True)
    
    # Рендеринг
    print("🖼️ Рендеринг сцени...")
    bpy.ops.render.render(write_still=True)
    
    print("✅ StarCraft сцена створена успішно!")
    print(f"📁 Зображення збережено: renders/blender/starcraft_scene.png")
    print(f"🏗️ Створено будівель: {len(buildings)}")
    print(f"⚔️ Створено юнітів: {len(units)}")
    print(f"🌀 Портальний ефект: 1")

if __name__ == "__main__":
    main()