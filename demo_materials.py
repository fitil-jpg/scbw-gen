#!/usr/bin/env python3
"""
Демонстраційний скрипт для роботи з матеріалами, текстурами та UV-розгортанням
Показує всі можливості створення матеріалів для StarCraft сцен
"""

import bpy
import os
import sys
from pathlib import Path

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent))

from blender.material_generator import StarCraftMaterialGenerator
from blender.enhanced_scene_generator import EnhancedStarCraftSceneGenerator

def clear_scene():
    """Очищає сцену"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Очищення матеріалів
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Очищення текстур
    for image in bpy.data.images:
        bpy.data.images.remove(image)

def create_demo_scene():
    """Створює демонстраційну сцену з різними матеріалами"""
    print("Створення демонстраційної сцени...")
    
    # Очищення сцени
    clear_scene()
    
    # Ініціалізація генератора матеріалів
    material_gen = StarCraftMaterialGenerator()
    
    # Створення різних типів матеріалів
    print("Створення матеріалів...")
    
    # 1. Матеріали для юнітів
    marine_material = material_gen.create_unit_material("marine", (0.2, 0.4, 0.8), 0.2, 0.7)
    zealot_material = material_gen.create_unit_material("zealot", (0.8, 0.2, 0.2), 0.1, 0.8)
    zergling_material = material_gen.create_unit_material("zergling", (0.4, 0.8, 0.2), 0.05, 0.9)
    
    # 2. Матеріали для території
    grass_material = material_gen.create_terrain_material("grass")
    dirt_material = material_gen.create_terrain_material("dirt")
    stone_material = material_gen.create_terrain_material("stone")
    metal_material = material_gen.create_terrain_material("metal")
    
    # 3. UI матеріали
    hud_material = material_gen.create_ui_material("hud")
    button_material = material_gen.create_ui_material("button")
    panel_material = material_gen.create_ui_material("panel")
    
    # 4. Матеріали ефектів
    portal_material = material_gen.create_effect_material("portal")
    explosion_material = material_gen.create_effect_material("explosion")
    
    # Створення демонстраційних об'єктів
    print("Створення демонстраційних об'єктів...")
    
    # Юніти
    create_demo_units(material_gen)
    
    # Територія
    create_demo_terrain(material_gen)
    
    # UI елементи
    create_demo_ui(material_gen)
    
    # Ефекти
    create_demo_effects(material_gen)
    
    # Налаштування сцени
    setup_demo_scene()
    
    print("Демонстраційна сцена створена успішно!")

def create_demo_units(material_gen):
    """Створює демонстраційні юніти"""
    # Морпіхи (Terran)
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-5 + i*2, 0, 0.5))
        marine = bpy.context.object
        marine.name = f"Demo_Marine_{i}"
        marine.scale = (1, 1, 1.5)
        
        marine_material = material_gen.create_unit_material("marine", (0.2, 0.4, 0.8), 0.2, 0.7)
        marine.data.materials.append(marine_material)
        material_gen.apply_uv_mapping(marine, "smart")
    
    # Зелоти (Protoss)
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(5 + i*2, 0, 0.5))
        zealot = bpy.context.object
        zealot.name = f"Demo_Zealot_{i}"
        zealot.scale = (1, 1, 1.5)
        
        zealot_material = material_gen.create_unit_material("zealot", (0.8, 0.2, 0.2), 0.1, 0.8)
        zealot.data.materials.append(zealot_material)
        material_gen.apply_uv_mapping(zealot, "smart")
    
    # Зерглінги (Zerg)
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5 + i*2, 0.5))
        zergling = bpy.context.object
        zergling.name = f"Demo_Zergling_{i}"
        zergling.scale = (1.5, 0.7, 1.2)
        
        zergling_material = material_gen.create_unit_material("zergling", (0.4, 0.8, 0.2), 0.05, 0.9)
        zergling.data.materials.append(zergling_material)
        material_gen.apply_uv_mapping(zergling, "smart")

def create_demo_terrain(material_gen):
    """Створює демонстраційну територію"""
    # Основний терен
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    terrain = bpy.context.object
    terrain.name = "Demo_Terrain"
    
    grass_material = material_gen.create_terrain_material("grass")
    terrain.data.materials.append(grass_material)
    material_gen.apply_uv_mapping(terrain, "smart")
    
    # Різні типи території
    terrain_types = [
        ("dirt", (-8, -8, 0.1)),
        ("stone", (8, -8, 0.1)),
        ("metal", (-8, 8, 0.1)),
        ("sand", (8, 8, 0.1))
    ]
    
    for terrain_type, location in terrain_types:
        bpy.ops.mesh.primitive_plane_add(size=4, location=location)
        terrain_patch = bpy.context.object
        terrain_patch.name = f"Demo_Terrain_{terrain_type}"
        
        terrain_material = material_gen.create_terrain_material(terrain_type)
        terrain_patch.data.materials.append(terrain_material)
        material_gen.apply_uv_mapping(terrain_patch, "smart")

def create_demo_ui(material_gen):
    """Створює демонстраційні UI елементи"""
    # HUD
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, -9, 0))
    hud = bpy.context.object
    hud.name = "Demo_HUD"
    hud.scale = (10, 1, 1)
    
    hud_material = material_gen.create_ui_material("hud")
    hud.data.materials.append(hud_material)
    
    # Кнопки
    button_positions = [
        (-8, -9, 0.1),
        (-6, -9, 0.1),
        (-4, -9, 0.1),
        (-2, -9, 0.1)
    ]
    
    for i, pos in enumerate(button_positions):
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=pos)
        button = bpy.context.object
        button.name = f"Demo_Button_{i}"
        button.scale = (1, 0.3, 0.1)
        
        button_material = material_gen.create_ui_material("button")
        button.data.materials.append(button_material)
    
    # Панель ресурсів
    bpy.ops.mesh.primitive_plane_add(size=1, location=(8, -9, 0))
    panel = bpy.context.object
    panel.name = "Demo_ResourcePanel"
    panel.scale = (2, 1, 1)
    
    panel_material = material_gen.create_ui_material("panel")
    panel.data.materials.append(panel_material)

def create_demo_effects(material_gen):
    """Створює демонстраційні ефекти"""
    # Портали
    portal_positions = [(-10, 0, 0), (10, 0, 0)]
    
    for i, pos in enumerate(portal_positions):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=pos)
        portal = bpy.context.object
        portal.name = f"Demo_Portal_{i}"
        
        portal_material = material_gen.create_effect_material("portal")
        portal.data.materials.append(portal_material)
        
        # Анімація порталу
        portal.rotation_euler = (0, 0, 0)
        portal.keyframe_insert(data_path="rotation_euler", frame=1)
        portal.rotation_euler = (0, 0, 3.14159 * 2)
        portal.keyframe_insert(data_path="rotation_euler", frame=100)
    
    # Вибухи
    explosion_positions = [(0, -10, 0), (0, 10, 0)]
    
    for i, pos in enumerate(explosion_positions):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=pos)
        explosion = bpy.context.object
        explosion.name = f"Demo_Explosion_{i}"
        
        explosion_material = material_gen.create_effect_material("explosion")
        explosion.data.materials.append(explosion_material)
        
        # Анімація вибуху
        explosion.scale = (0.1, 0.1, 0.1)
        explosion.keyframe_insert(data_path="scale", frame=1)
        explosion.scale = (2, 2, 2)
        explosion.keyframe_insert(data_path="scale", frame=10)
        explosion.scale = (0, 0, 0)
        explosion.keyframe_insert(data_path="scale", frame=20)

def setup_demo_scene():
    """Налаштовує демонстраційну сцену"""
    # Камера
    bpy.ops.object.camera_add(location=(0, -15, 8))
    camera = bpy.context.object
    camera.name = "Demo_Camera"
    camera.rotation_euler = (1.1, 0, 0)
    bpy.context.scene.camera = camera
    
    # Освітлення
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.object
    sun.name = "Demo_Sun"
    sun.data.energy = 3.0
    
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 8))
    fill = bpy.context.object
    fill.name = "Demo_Fill"
    fill.data.energy = 1.0
    fill.data.size = 5.0
    
    # Налаштування рендерингу
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 50  # Швидший рендеринг для демо
    
    # Налаштування Cycles
    if scene.render.engine == 'CYCLES':
        cycles = scene.cycles
        cycles.samples = 64
        cycles.use_denoising = True
        cycles.max_bounces = 8
    
    # Налаштування кольору
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

def create_procedural_materials_demo():
    """Створює демонстрацію процедурних матеріалів"""
    print("Створення демонстрації процедурних матеріалів...")
    
    material_gen = StarCraftMaterialGenerator()
    
    # Створення різних процедурних матеріалів
    procedural_materials = [
        ("Noise_Material", lambda: create_noise_material()),
        ("Voronoi_Material", lambda: create_voronoi_material()),
        ("Wave_Material", lambda: create_wave_material()),
        ("Layered_Material", lambda: create_layered_material())
    ]
    
    for i, (name, create_func) in enumerate(procedural_materials):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i*3, 15, 0.5))
        cube = bpy.context.object
        cube.name = f"Demo_{name}"
        
        material = create_func()
        cube.data.materials.append(material)
        material_gen.apply_uv_mapping(cube, "smart")

def create_noise_material():
    """Створює матеріал на основі шуму"""
    material = bpy.data.materials.new(name="Demo_Noise_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Noise texture
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 15.0
    noise.inputs['Roughness'].default_value = 0.5
    noise.location = (-400, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(noise.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material

def create_voronoi_material():
    """Створює матеріал на основі діаграми Вороного"""
    material = bpy.data.materials.new(name="Demo_Voronoi_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Voronoi texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 10.0
    voronoi.inputs['Randomness'].default_value = 1.0
    voronoi.location = (-400, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(voronoi.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material

def create_wave_material():
    """Створює матеріал з хвилями"""
    material = bpy.data.materials.new(name="Demo_Wave_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Wave texture
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 5.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value = 2.0
    wave.location = (-400, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(wave.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material

def create_layered_material():
    """Створює складний матеріал з кількома шарами"""
    material = bpy.data.materials.new(name="Demo_Layered_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Noise 1
    noise1 = nodes.new(type='ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 10.0
    noise1.inputs['Detail'].default_value = 5.0
    noise1.location = (-600, 200)
    
    # Noise 2
    noise2 = nodes.new(type='ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 50.0
    noise2.inputs['Detail'].default_value = 10.0
    noise2.location = (-600, 0)
    
    # Mix node
    mix = nodes.new(type='ShaderNodeMix')
    mix.inputs['Fac'].default_value = 0.5
    mix.location = (-400, 100)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(noise1.outputs['Color'], mix.inputs['Color1'])
    material.node_tree.links.new(noise2.outputs['Color'], mix.inputs['Color2'])
    material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material

def render_demo():
    """Рендерить демонстраційну сцену"""
    print("Рендеринг демонстраційної сцени...")
    
    # Налаштування виводу
    output_path = "/workspace/renders/demo_materials"
    os.makedirs(output_path, exist_ok=True)
    
    bpy.context.scene.render.filepath = f"{output_path}/demo_materials"
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    
    # Рендеринг
    bpy.ops.render.render(write_still=True)
    
    print(f"Демонстраційна сцена зрендерена: {output_path}/demo_materials.png")

def main():
    """Головна функція"""
    print("=== Демонстрація матеріалів, текстур та UV-розгортання ===")
    
    # Створення демонстраційної сцени
    create_demo_scene()
    
    # Демонстрація процедурних матеріалів
    create_procedural_materials_demo()
    
    # Рендеринг
    render_demo()
    
    print("Демонстрація завершена!")

if __name__ == "__main__":
    main()