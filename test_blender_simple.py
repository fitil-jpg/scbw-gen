#!/usr/bin/env python3
"""
Простий тестовий скрипт для Blender
"""
import bpy
import os

def main():
    print("🎬 Тестовий Blender скрипт")
    print("=" * 30)
    
    # Очищення сцени
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Створення простого куба
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "StarCraft_Cube"
    
    # Додавання матеріалу
    mat = bpy.data.materials.new(name="StarCraft_Material")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.3, 0.1, 1.0)  # Зелений колір
    
    cube.data.materials.append(mat)
    
    # Налаштування камери
    bpy.ops.object.camera_add(location=(5, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    
    # Встановлення камери як активної для рендерингу
    bpy.context.scene.camera = camera
    
    # Налаштування освітлення
    bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))
    light = bpy.context.active_object
    light.data.energy = 3
    
    # Налаштування рендерингу
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    bpy.context.scene.render.filepath = "renders/blender/test_scene.png"
    
    # Вимкнення денойзингу
    bpy.context.scene.cycles.use_denoising = False
    
    # Створення директорії
    os.makedirs("renders/blender", exist_ok=True)
    
    # Рендеринг
    print("🖼️ Рендеринг сцени...")
    bpy.ops.render.render(write_still=True)
    
    print("✅ Рендеринг завершено!")
    print(f"📁 Зображення збережено: renders/blender/test_scene.png")

if __name__ == "__main__":
    main()