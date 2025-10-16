#!/usr/bin/env python3
"""
USD Utilities
Утиліти для роботи з USD сценами, юнітами та будівлями
"""

import os
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

try:
    from pxr import Usd, UsdGeom, UsdLux, Gf, Sdf, UsdShade, UsdPhysics
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    # Створити заглушки для тестування
    class Usd:
        class Stage:
            pass
    class UsdGeom:
        class Plane:
            pass
        class Cube:
            pass
        class Sphere:
            pass
        class Camera:
            pass
    class UsdLux:
        class DirectionalLight:
            pass
        class DomeLight:
            pass
    class Gf:
        class Vec3f:
            pass
    class Sdf:
        class ValueTypeNames:
            pass
    class UsdShade:
        class Material:
            pass
        class Shader:
            pass
        class MaterialBindingAPI:
            pass


class USDUnitManager:
    """Менеджер для роботи з юнітами в USD"""
    
    def __init__(self, stage: Usd.Stage, assets_path: str = "assets"):
        self.stage = stage
        self.assets_path = Path(assets_path)
        self.units_config = self.load_units_config()
        
    def load_units_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію юнітів"""
        config_path = self.assets_path / "units" / "units_config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def create_unit_sprite(self, unit_type: str, position: Tuple[float, float], 
                          army_color: List[float], scale: float = 1.0) -> str:
        """Створити юніт зі спрайтом"""
        unit_config = self.units_config.get('units', {}).get(unit_type, {})
        sprite_path = unit_config.get('sprite', f"{unit_type}.png")
        unit_scale = unit_config.get('scale', 1.0) * scale
        
        unit_path = f"/World/Units/{unit_type}_{random.randint(1000, 9999)}"
        
        # Створити площину для спрайта
        plane = UsdGeom.Plane.Define(self.stage, unit_path)
        plane.CreateSizeAttr(2.0 * unit_scale)
        plane.AddTranslateOp().Set(Gf.Vec3f(position[0], 1.0 * unit_scale, position[1]))
        
        # Додати матеріал з текстурою
        material = UsdShade.Material.Define(self.stage, f"{unit_path}/Material")
        shader = UsdShade.Shader.Define(self.stage, f"{unit_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Встановити кольори
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*army_color))
        
        # Додати текстуру якщо файл існує
        sprite_file = self.assets_path / "units" / sprite_path
        if sprite_file.exists():
            texture = UsdShade.Shader.Define(self.stage, f"{unit_path}/Material/Texture")
            texture.CreateIdAttr("UsdUVTexture")
            texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(str(sprite_file))
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
                texture.ConnectableAPI(), "rgb"
            )
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(plane).Bind(material)
        
        # Додати метадані юніта
        plane.GetPrim().SetMetadata("unit_type", unit_type)
        plane.GetPrim().SetMetadata("health", unit_config.get('health', 100))
        plane.GetPrim().SetMetadata("damage", unit_config.get('damage', 25))
        plane.GetPrim().SetMetadata("speed", unit_config.get('speed', 1.0))
        
        return unit_path
    
    def create_unit_formation(self, unit_type: str, positions: List[Tuple[float, float]], 
                            army_color: List[float], scale: float = 1.0) -> List[str]:
        """Створити формацію юнітів"""
        unit_paths = []
        for pos in positions:
            unit_path = self.create_unit_sprite(unit_type, pos, army_color, scale)
            unit_paths.append(unit_path)
        return unit_paths


class USDBuildingManager:
    """Менеджер для роботи з будівлями в USD"""
    
    def __init__(self, stage: Usd.Stage, assets_path: str = "assets"):
        self.stage = stage
        self.assets_path = Path(assets_path)
        self.buildings_config = self.load_buildings_config()
        
    def load_buildings_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію будівель"""
        config_path = self.assets_path / "buildings" / "buildings_config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def create_building(self, building_type: str, position: Tuple[float, float], 
                       owner: str = "neutral", rotation: float = 0, 
                       scale: float = 1.0) -> str:
        """Створити будівлю"""
        building_config = self.buildings_config.get('buildings', {}).get(building_type, {})
        sprite_path = building_config.get('sprite', f"{building_type}.png")
        building_scale = building_config.get('scale', 1.0) * scale
        
        building_path = f"/World/Buildings/{building_type}_{random.randint(1000, 9999)}"
        
        # Створити куб як основу будівлі
        cube = UsdGeom.Cube.Define(self.stage, building_path)
        cube.CreateSizeAttr(2.0 * building_scale)
        cube.AddTranslateOp().Set(Gf.Vec3f(position[0], 1.0 * building_scale, position[1]))
        cube.AddRotateYOp().Set(rotation)
        
        # Додати матеріал
        material = UsdShade.Material.Define(self.stage, f"{building_path}/Material")
        shader = UsdShade.Shader.Define(self.stage, f"{building_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Кольори залежно від власника
        owners = self.buildings_config.get('owners', {})
        owner_config = owners.get(owner, {})
        color = owner_config.get('color', [0.5, 0.5, 0.5])
        
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        
        # Додати текстуру якщо файл існує
        sprite_file = self.assets_path / "buildings" / sprite_path
        if sprite_file.exists():
            texture = UsdShade.Shader.Define(self.stage, f"{building_path}/Material/Texture")
            texture.CreateIdAttr("UsdUVTexture")
            texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(str(sprite_file))
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
                texture.ConnectableAPI(), "rgb"
            )
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(cube).Bind(material)
        
        # Додати метадані будівлі
        cube.GetPrim().SetMetadata("building_type", building_type)
        cube.GetPrim().SetMetadata("health", building_config.get('health', 200))
        cube.GetPrim().SetMetadata("owner", owner)
        
        return building_path


class USDTerrainManager:
    """Менеджер для роботи з рельєфом в USD"""
    
    def __init__(self, stage: Usd.Stage, assets_path: str = "assets"):
        self.stage = stage
        self.assets_path = Path(assets_path)
        self.terrain_config = self.load_terrain_config()
        
    def load_terrain_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію рельєфу"""
        config_path = self.assets_path / "terrain" / "terrain_config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def create_terrain(self, terrain_type: str = "grassland", 
                      size: float = 100.0, height_variation: float = 0.2) -> str:
        """Створити рельєф місцевості"""
        terrain_types = self.terrain_config.get('terrain_types', {})
        terrain_data = terrain_types.get(terrain_type, {})
        
        texture_path = terrain_data.get('texture', f"{terrain_type}_01.png")
        color = terrain_data.get('color', [0.2, 0.6, 0.2])
        
        terrain_path = "/World/Terrain"
        
        # Створити площину для рельєфу
        plane = UsdGeom.Plane.Define(self.stage, terrain_path)
        plane.CreateSizeAttr(size)
        
        # Додати матеріал
        material = UsdShade.Material.Define(self.stage, f"{terrain_path}/Material")
        shader = UsdShade.Shader.Define(self.stage, f"{terrain_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Встановити базовий колір
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        
        # Додати текстуру якщо файл існує
        texture_file = self.assets_path / "terrain" / texture_path
        if texture_file.exists():
            texture = UsdShade.Shader.Define(self.stage, f"{terrain_path}/Material/Texture")
            texture.CreateIdAttr("UsdUVTexture")
            texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(str(texture_file))
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
                texture.ConnectableAPI(), "rgb"
            )
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(plane).Bind(material)
        
        return terrain_path


class USDEffectManager:
    """Менеджер для роботи з ефектами в USD"""
    
    def __init__(self, stage: Usd.Stage, assets_path: str = "assets"):
        self.stage = stage
        self.assets_path = Path(assets_path)
        self.effects_config = self.load_effects_config()
        
    def load_effects_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію ефектів"""
        config_path = self.assets_path / "effects" / "effects_config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def create_effect(self, effect_type: str, position: Tuple[float, float], 
                     radius: float = 5.0, color: List[float] = [1.0, 0.0, 1.0], 
                     intensity: float = 0.7) -> str:
        """Створити ефект"""
        effects = self.effects_config.get('effects', {})
        effect_data = effects.get(effect_type, {})
        
        sprite_path = effect_data.get('sprite', f"{effect_type}.png")
        effect_scale = effect_data.get('scale', 1.0)
        duration = effect_data.get('duration', 5.0)
        
        effect_path = f"/World/Effects/{effect_type}_{random.randint(1000, 9999)}"
        
        # Створити сферу для ефекту
        sphere = UsdGeom.Sphere.Define(self.stage, effect_path)
        sphere.CreateRadiusAttr(radius * effect_scale)
        sphere.AddTranslateOp().Set(Gf.Vec3f(position[0], 2.0, position[1]))
        
        # Додати матеріал з прозорістю
        material = UsdShade.Material.Define(self.stage, f"{effect_path}/Material")
        shader = UsdShade.Shader.Define(self.stage, f"{effect_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(intensity)
        
        # Додати текстуру якщо файл існує
        sprite_file = self.assets_path / "effects" / sprite_path
        if sprite_file.exists():
            texture = UsdShade.Shader.Define(self.stage, f"{effect_path}/Material/Texture")
            texture.CreateIdAttr("UsdUVTexture")
            texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(str(sprite_file))
            shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
                texture.ConnectableAPI(), "rgb"
            )
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(sphere).Bind(material)
        
        # Додати метадані ефекту
        sphere.GetPrim().SetMetadata("effect_type", effect_type)
        sphere.GetPrim().SetMetadata("duration", duration)
        sphere.GetPrim().SetMetadata("animated", effect_data.get('animated', False))
        
        return effect_path


class USDSceneUtils:
    """Утиліти для роботи з USD сценами"""
    
    @staticmethod
    def create_camera(stage: Usd.Stage, position: Tuple[float, float, float], 
                     target: Tuple[float, float, float], fov: float = 60.0) -> str:
        """Створити камеру"""
        camera = UsdGeom.Camera.Define(stage, "/World/Camera")
        camera.CreateFocalLengthAttr(50.0)  # Приблизний FOV
        camera.AddTranslateOp().Set(Gf.Vec3f(*position))
        
        # Направити камеру на ціль
        look_at = Gf.Vec3f(*target) - Gf.Vec3f(*position)
        look_at.Normalize()
        
        # Простий поворот камери
        camera.AddRotateYOp().Set(math.degrees(math.atan2(look_at[0], look_at[2])))
        
        return "/World/Camera"
    
    @staticmethod
    def setup_lighting(stage: Usd.Stage, sun_angle: Tuple[float, float] = (45, 30), 
                      sun_intensity: float = 1.0, ambient: float = 0.3) -> None:
        """Налаштувати освітлення сцени"""
        # Сонце
        azimuth, elevation = sun_angle
        azimuth_rad = math.radians(azimuth)
        elevation_rad = math.radians(elevation)
        
        sun_direction = Gf.Vec3f(
            math.cos(elevation_rad) * math.sin(azimuth_rad),
            math.sin(elevation_rad),
            math.cos(elevation_rad) * math.cos(azimuth_rad)
        )
        
        sun_light = UsdLux.DirectionalLight.Define(stage, "/World/Sun")
        sun_light.CreateIntensityAttr(sun_intensity)
        sun_light.CreateDirectionAttr(sun_direction)
        sun_light.CreateColorAttr(Gf.Vec3f(1.0, 0.95, 0.8))
        
        # Ambient light
        ambient_light = UsdLux.DomeLight.Define(stage, "/World/Ambient")
        ambient_light.CreateIntensityAttr(ambient)
        ambient_light.CreateColorAttr(Gf.Vec3f(1.0, 1.0, 1.0))
    
    @staticmethod
    def generate_positions_in_area(area: List[float], count: int, 
                                 formation: str = "random", spacing: float = 2.0) -> List[Tuple[float, float]]:
        """Генерувати позиції в області згідно формації"""
        x1, y1, x2, y2 = area
        positions = []
        
        if formation == "line":
            for i in range(count):
                x = x1 + (x2 - x1) * i / max(1, count - 1)
                y = (y1 + y2) / 2
                positions.append((x, y))
                
        elif formation == "arc":
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            radius = min(x2 - x1, y2 - y1) / 3
            
            for i in range(count):
                angle = math.pi * i / max(1, count - 1)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions.append((x, y))
                
        elif formation == "back":
            for i in range(count):
                x = x1 + (x2 - x1) * i / max(1, count - 1)
                y = y1 + spacing * i
                positions.append((x, y))
                
        else:  # random
            for _ in range(count):
                x = random.uniform(x1, x2)
                y = random.uniform(y1, y2)
                positions.append((x, y))
        
        return positions