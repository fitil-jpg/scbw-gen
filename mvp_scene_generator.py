#!/usr/bin/env python3
"""
MVP Scene Generator - Компактна версія генератора сцени
Розмір: ~180 рядків (в межах MVP)
"""

import bpy
import os
import math
import random
from typing import List, Tuple, Dict, Any
from mvp_asset_manager import SimpleAssetManager
from mvp_config_manager import SimpleConfigManager

class MVPSceneGenerator:
    """Компактний генератор сцени для MVP"""
    
    def __init__(self, config_path: str = "scene.yaml"):
        self.asset_manager = SimpleAssetManager()
        self.config_manager = SimpleConfigManager()
        self.config = self.config_manager.load_config(config_path)
        self.scene_objects = []
    
    def clear_scene(self):
        """Очистити сцену"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Очистити матеріали
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    
    def create_terrain(self, size: float = 20.0, color: Tuple[float, float, float, float] = (0.2, 0.4, 0.2, 1.0)):
        """Створити терен"""
        bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
        terrain = bpy.context.active_object
        terrain.name = "Terrain"
        
        # Матеріал терену
        mat = self._create_material("Terrain_Material", color)
        terrain.data.materials.append(mat)
        
        self.scene_objects.append(terrain)
        return terrain
    
    def create_building(self, position: Tuple[float, float, float], 
                       size: float, color: Tuple[float, float, float, float], 
                       name: str) -> bpy.types.Object:
        """Створити будівлю"""
        bpy.ops.mesh.primitive_cube_add(size=size, location=position)
        building = bpy.context.active_object
        building.name = name
        
        # Матеріал будівлі
        mat = self._create_material(f"{name}_Material", color)
        building.data.materials.append(mat)
        
        self.scene_objects.append(building)
        return building
    
    def create_unit(self, position: Tuple[float, float, float], 
                   size: float, color: Tuple[float, float, float, float], 
                   name: str) -> bpy.types.Object:
        """Створити юніт"""
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=position)
        unit = bpy.context.active_object
        unit.name = name
        
        # Матеріал юніта
        mat = self._create_material(f"{name}_Material", color)
        unit.data.materials.append(mat)
        
        self.scene_objects.append(unit)
        return unit
    
    def create_effect(self, position: Tuple[float, float, float], 
                     radius: float, color: Tuple[float, float, float, float], 
                     name: str) -> bpy.types.Object:
        """Створити ефект"""
        bpy.ops.mesh.primitive_torus_add(
            major_radius=radius, 
            minor_radius=radius*0.1, 
            location=position
        )
        effect = bpy.context.active_object
        effect.name = name
        
        # Матеріал з емісією
        mat = self._create_emissive_material(f"{name}_Material", color)
        effect.data.materials.append(mat)
        
        self.scene_objects.append(effect)
        return effect
    
    def setup_camera(self, position: Tuple[float, float, float] = (8, -8, 6),
                    rotation: Tuple[float, float, float] = (1.1, 0, 0.785)):
        """Налаштувати камеру"""
        bpy.ops.object.camera_add(location=position)
        camera = bpy.context.active_object
        camera.rotation_euler = rotation
        bpy.context.scene.camera = camera
        return camera
    
    def setup_lighting(self, sun_energy: float = 3.0, area_energy: float = 5.0):
        """Налаштувати освітлення"""
        # Основне світло
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.data.energy = sun_energy
        
        # Додаткове світло
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
        area_light = bpy.context.active_object
        area_light.data.energy = area_energy
        area_light.data.color = (0.5, 0.8, 1.0)
        
        return sun, area_light
    
    def setup_render(self, resolution: Tuple[int, int] = (1280, 720), 
                    samples: int = 256, output_path: str = "renders/blender/mvp_scene.png"):
        """Налаштувати рендеринг"""
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]
        bpy.context.scene.render.filepath = output_path
        bpy.context.scene.cycles.use_denoising = False
        bpy.context.scene.cycles.samples = samples
        
        # Створити директорію
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    def generate_scene(self):
        """Згенерувати сцену"""
        print("🎬 Генерація MVP сцени...")
        
        # Очистити сцену
        self.clear_scene()
        
        # Створити терен
        terrain = self.create_terrain()
        
        # Налаштувати камеру та освітлення
        camera = self.setup_camera()
        sun, area_light = self.setup_lighting()
        
        # Створити об'єкти з конфігурації
        self._create_objects_from_config()
        
        # Налаштувати рендеринг
        self.setup_render()
        
        print(f"✅ Сцена створена! Об'єктів: {len(self.scene_objects)}")
    
    def render_scene(self):
        """Рендерити сцену"""
        print("🖼️ Рендеринг сцени...")
        bpy.ops.render.render(write_still=True)
        print("✅ Рендеринг завершено!")
    
    def _create_material(self, name: str, color: Tuple[float, float, float, float]) -> bpy.types.Material:
        """Створити матеріал"""
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        return mat
    
    def _create_emissive_material(self, name: str, color: Tuple[float, float, float, float]) -> bpy.types.Material:
        """Створити емісивний матеріал"""
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
        mat.node_tree.nodes["Principled BSDF"].inputs[17].default_value = color  # Emission Color
        mat.node_tree.nodes["Principled BSDF"].inputs[18].default_value = 2.0    # Emission Strength
        return mat
    
    def _create_objects_from_config(self):
        """Створити об'єкти з конфігурації"""
        # Будівлі
        buildings_config = self.config.get("buildings", {})
        for building_name, building_data in buildings_config.items():
            position = tuple(building_data.get("position", [0, 0, 1]))
            size = building_data.get("size", 1.5)
            color = tuple(building_data.get("color", [0.2, 0.4, 0.8, 1.0]))
            
            self.create_building(position, size, color, building_name)
        
        # Юніти
        units_config = self.config.get("units", {})
        for unit_name, unit_data in units_config.items():
            position = tuple(unit_data.get("position", [0, 0, 0.5]))
            size = unit_data.get("size", 0.3)
            color = tuple(unit_data.get("color", [0.3, 0.5, 0.9, 1.0]))
            
            self.create_unit(position, size, color, unit_name)
        
        # Ефекти
        effects_config = self.config.get("effects", {})
        for effect_name, effect_data in effects_config.items():
            position = tuple(effect_data.get("position", [0, 0, 1]))
            radius = effect_data.get("radius", 1.5)
            color = tuple(effect_data.get("color", [0.5, 0.8, 1.0, 1.0]))
            
            self.create_effect(position, radius, color, effect_name)

def main():
    """Головна функція"""
    generator = MVPSceneGenerator()
    generator.generate_scene()
    generator.render_scene()

if __name__ == "__main__":
    main()