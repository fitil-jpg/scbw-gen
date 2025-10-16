#!/usr/bin/env python3
"""
USD Scene Generator
Генератор USD сцен з юнітами та будівлями

Використання:
    python generate_usd_scene.py --config scene.yaml --out out/scene.usda
"""

import argparse
import yaml
import os
import sys
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any

try:
    from pxr import Usd, UsdGeom, UsdLux, Gf, Sdf, UsdShade
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("Warning: USD Python bindings not available. Install with: pip install usd-core")


class USDSceneGenerator:
    """Генератор USD сцен з юнітами та будівлями"""
    
    def __init__(self, config_path: str, output_path: str):
        self.config_path = config_path
        self.output_path = output_path
        self.config = self.load_config()
        self.stage = None
        self.assets_path = Path("assets")
        
    def load_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію з YAML файлу"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_stage(self):
        """Створити USD stage"""
        if not USD_AVAILABLE:
            raise RuntimeError("USD Python bindings not available")
            
        self.stage = Usd.Stage.CreateNew(self.output_path)
        
        # Додати метадані
        self.stage.SetMetadata("upAxis", "Y")
        self.stage.SetMetadata("metersPerUnit", 1.0)
        
    def setup_lighting(self):
        """Налаштувати освітлення сцени"""
        scene_config = self.config.get('scene', {})
        lighting = scene_config.get('lighting', {})
        
        # Додати сонце
        sun_angle = lighting.get('sun_angle', [45, 30])
        sun_intensity = lighting.get('sun_intensity', 1.0)
        
        # Конвертувати кути в радіани
        azimuth = math.radians(sun_angle[0])
        elevation = math.radians(sun_angle[1])
        
        # Обчислити напрямок сонця
        sun_direction = Gf.Vec3f(
            math.cos(elevation) * math.sin(azimuth),
            math.sin(elevation),
            math.cos(elevation) * math.cos(azimuth)
        )
        
        # Створити directional light (сонце)
        sun_light = UsdLux.DirectionalLight.Define(self.stage, "/World/Sun")
        sun_light.CreateIntensityAttr(sun_intensity)
        sun_light.CreateDirectionAttr(sun_direction)
        sun_light.CreateColorAttr(Gf.Vec3f(1.0, 0.95, 0.8))
        
        # Додати ambient light
        ambient = lighting.get('ambient', 0.3)
        ambient_light = UsdLux.DomeLight.Define(self.stage, "/World/Ambient")
        ambient_light.CreateIntensityAttr(ambient)
        ambient_light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    def create_terrain(self):
        """Створити рельєф місцевості"""
        scene_config = self.config.get('scene', {})
        terrain = scene_config.get('terrain', {})
        
        terrain_type = terrain.get('type', 'grassland')
        height_variation = terrain.get('height_variation', 0.2)
        texture_path = terrain.get('texture', 'terrain/grass_01.png')
        
        # Створити площину для рельєфу
        plane = UsdGeom.Plane.Define(self.stage, "/World/Terrain")
        plane.CreateSizeAttr(100.0)  # Розмір площини
        
        # Додати матеріал
        material = UsdShade.Material.Define(self.stage, "/World/Terrain/Material")
        shader = UsdShade.Shader.Define(self.stage, "/World/Terrain/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Налаштувати кольори залежно від типу рельєфу
        if terrain_type == 'grassland':
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.2, 0.6, 0.2))
        elif terrain_type == 'desert':
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.8, 0.6, 0.3))
        elif terrain_type == 'snow':
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(0.9, 0.9, 0.9))
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        # Прив'язати матеріал до площини
        UsdShade.MaterialBindingAPI(plane).Bind(material)
    
    def create_unit(self, unit_type: str, position: Tuple[float, float], army_color: List[float], 
                   scale: float = 1.0) -> str:
        """Створити юніт в сцені"""
        unit_path = f"/World/Units/{unit_type}_{len(self.stage.Traverse())}"
        
        # Створити куб як базову форму юніта
        cube = UsdGeom.Cube.Define(self.stage, unit_path)
        cube.CreateSizeAttr(1.0 * scale)
        
        # Позиціонувати юніта
        cube.AddTranslateOp().Set(Gf.Vec3f(position[0], 0.5 * scale, position[1]))
        
        # Додати матеріал з кольором армії
        material = UsdShade.Material.Define(self.stage, f"{unit_path}/Material")
        shader = UsdShade.Shader.Define(self.stage, f"{unit_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*army_color))
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(cube).Bind(material)
        
        return unit_path
    
    def create_units(self):
        """Створити всіх юнітів згідно конфігурації"""
        units_config = self.config.get('units', {})
        
        for army_name, army_config in units_config.items():
            army_color = army_config.get('color', [0.5, 0.5, 0.5])
            spawn_area = army_config.get('spawn_area', [0, 0, 10, 10])
            
            for unit_config in army_config.get('units', []):
                unit_type = unit_config['type']
                count = unit_config['count']
                formation = unit_config.get('formation', 'random')
                spacing = unit_config.get('spacing', 2.0)
                
                # Генерувати позиції для юнітів
                positions = self.generate_unit_positions(
                    spawn_area, count, formation, spacing
                )
                
                # Створити юнітів
                for i, pos in enumerate(positions):
                    scale = self.get_unit_scale(unit_type)
                    self.create_unit(unit_type, pos, army_color, scale)
    
    def generate_unit_positions(self, spawn_area: List[float], count: int, 
                              formation: str, spacing: float) -> List[Tuple[float, float]]:
        """Генерувати позиції для юнітів згідно формації"""
        x1, y1, x2, y2 = spawn_area
        positions = []
        
        if formation == 'line':
            # Лінійна формація
            for i in range(count):
                x = x1 + (x2 - x1) * i / max(1, count - 1)
                y = (y1 + y2) / 2
                positions.append((x, y))
                
        elif formation == 'arc':
            # Дугова формація
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            radius = min(x2 - x1, y2 - y1) / 3
            
            for i in range(count):
                angle = math.pi * i / max(1, count - 1)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((x, y))
                
        elif formation == 'back':
            # Формація ззаду
            for i in range(count):
                x = x1 + (x2 - x1) * i / max(1, count - 1)
                y = y1 + spacing * i
                positions.append((x, y))
                
        else:  # random
            # Випадкове розміщення
            for _ in range(count):
                x = random.uniform(x1, x2)
                y = random.uniform(y1, y2)
                positions.append((x, y))
        
        return positions
    
    def get_unit_scale(self, unit_type: str) -> float:
        """Отримати масштаб для типу юніта"""
        scales = {
            'warrior': 1.0,
            'archer': 0.8,
            'mage': 0.9,
            'knight': 1.2,
            'dragon': 2.0
        }
        return scales.get(unit_type, 1.0)
    
    def create_buildings(self):
        """Створити будівлі згідно конфігурації"""
        buildings_config = self.config.get('buildings', [])
        
        for i, building in enumerate(buildings_config):
            building_type = building['type']
            position = building['position']
            rotation = building.get('rotation', 0)
            scale = building.get('scale', 1.0)
            owner = building.get('owner', 'neutral')
            
            building_path = f"/World/Buildings/{building_type}_{i}"
            
            # Створити будівлю як куб
            cube = UsdGeom.Cube.Define(self.stage, building_path)
            cube.CreateSizeAttr(2.0 * scale)
            
            # Позиціонувати та повернути
            cube.AddTranslateOp().Set(Gf.Vec3f(position[0], 1.0 * scale, position[1]))
            cube.AddRotateYOp().Set(rotation)
            
            # Додати матеріал
            material = UsdShade.Material.Define(self.stage, f"{building_path}/Material")
            shader = UsdShade.Shader.Define(self.stage, f"{building_path}/Material/Shader")
            shader.CreateIdAttr("UsdPreviewSurface")
            
            # Кольори залежно від власника
            if owner == 'army_1':
                color = Gf.Vec3f(0.2, 0.4, 0.8)
            elif owner == 'army_2':
                color = Gf.Vec3f(0.8, 0.2, 0.2)
            else:
                color = Gf.Vec3f(0.5, 0.5, 0.5)
            
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(color)
            material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
            UsdShade.MaterialBindingAPI(cube).Bind(material)
    
    def create_effects(self):
        """Створити ефекти та магію"""
        effects_config = self.config.get('effects', [])
        
        for i, effect in enumerate(effects_config):
            effect_type = effect['type']
            position = effect['position']
            radius = effect.get('radius', 5.0)
            color = effect.get('color', [1.0, 0.0, 1.0])
            intensity = effect.get('intensity', 0.7)
            
            effect_path = f"/World/Effects/{effect_type}_{i}"
            
            if effect_type == 'magic_aura':
                # Створити сферу для магічної аури
                sphere = UsdGeom.Sphere.Define(self.stage, effect_path)
                sphere.CreateRadiusAttr(radius)
                sphere.AddTranslateOp().Set(Gf.Vec3f(position[0], 2.0, position[1]))
                
                # Додати матеріал з прозорістю
                material = UsdShade.Material.Define(self.stage, f"{effect_path}/Material")
                shader = UsdShade.Shader.Define(self.stage, f"{effect_path}/Material/Shader")
                shader.CreateIdAttr("UsdPreviewSurface")
                shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
                shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(intensity)
                
                material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
                UsdShade.MaterialBindingAPI(sphere).Bind(material)
    
    def setup_camera(self):
        """Налаштувати камеру"""
        camera_config = self.config.get('camera', {})
        position = camera_config.get('position', [50, 50, 80])
        target = camera_config.get('target', [50, 50, 0])
        fov = camera_config.get('fov', 60)
        
        camera = UsdGeom.Camera.Define(self.stage, "/World/Camera")
        camera.CreateFocalLengthAttr(50.0)  # Приблизний FOV
        camera.AddTranslateOp().Set(Gf.Vec3f(*position))
        
        # Направити камеру на ціль
        look_at = Gf.Vec3f(*target) - Gf.Vec3f(*position)
        look_at.Normalize()
        
        # Простий поворот камери (можна покращити)
        camera.AddRotateYOp().Set(math.degrees(math.atan2(look_at[0], look_at[2])))
    
    def generate_scene(self):
        """Згенерувати повну сцену"""
        print(f"Генерація USD сцени з конфігурації: {self.config_path}")
        
        if not USD_AVAILABLE:
            print("Error: USD Python bindings not available")
            return False
        
        # Створити директорію виводу
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Створити stage
        self.create_stage()
        
        # Налаштувати сцену
        self.setup_lighting()
        self.create_terrain()
        self.create_units()
        self.create_buildings()
        self.create_effects()
        self.setup_camera()
        
        # Зберегти сцену
        self.stage.Save()
        
        print(f"Сцена збережена: {self.output_path}")
        return True


def main():
    parser = argparse.ArgumentParser(description='USD Scene Generator')
    parser.add_argument('--config', required=True, help='Path to scene configuration YAML file')
    parser.add_argument('--out', required=True, help='Output USD file path')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    generator = USDSceneGenerator(args.config, args.out)
    success = generator.generate_scene()
    
    if success:
        print("Scene generation completed successfully!")
    else:
        print("Scene generation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()