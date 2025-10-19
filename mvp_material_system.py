#!/usr/bin/env python3
"""
MVP Material System - Компактна система матеріалів
Розмір: ~70 рядків
"""

import bpy
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class MaterialPreset:
    """Пресет матеріалу"""
    name: str
    base_color: Tuple[float, float, float, float]
    metallic: float = 0.0
    roughness: float = 0.5
    emission_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    emission_strength: float = 0.0

class MVPMaterialSystem:
    """Компактна система матеріалів для MVP"""
    
    def __init__(self):
        self.materials: Dict[str, bpy.types.Material] = {}
        self.presets = self._create_presets()
    
    def _create_presets(self) -> Dict[str, MaterialPreset]:
        """Створити пресети матеріалів"""
        return {
            "terran_metal": MaterialPreset(
                "Terran_Metal", (0.2, 0.4, 0.8, 1.0), 
                metallic=0.8, roughness=0.3
            ),
            "zerg_organic": MaterialPreset(
                "Zerg_Organic", (0.6, 0.2, 0.6, 1.0), 
                metallic=0.1, roughness=0.7
            ),
            "protoss_energy": MaterialPreset(
                "Protoss_Energy", (0.8, 0.9, 1.0, 1.0), 
                metallic=0.9, roughness=0.1,
                emission_color=(0.8, 0.9, 1.0, 1.0), emission_strength=2.0
            ),
            "terrain_grass": MaterialPreset(
                "Terrain_Grass", (0.2, 0.4, 0.2, 1.0), 
                metallic=0.0, roughness=0.8
            ),
            "portal_effect": MaterialPreset(
                "Portal_Effect", (0.5, 0.8, 1.0, 1.0), 
                metallic=0.0, roughness=0.0,
                emission_color=(0.5, 0.8, 1.0, 1.0), emission_strength=3.0
            )
        }
    
    def create_material(self, name: str, preset_name: Optional[str] = None, 
                       custom_props: Optional[Dict[str, Any]] = None) -> bpy.types.Material:
        """Створити матеріал"""
        if name in self.materials:
            return self.materials[name]
        
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        
        # Використати пресет або створити з нуля
        if preset_name and preset_name in self.presets:
            preset = self.presets[preset_name]
            self._apply_preset(mat, preset)
        elif custom_props:
            self._apply_custom_props(mat, custom_props)
        
        self.materials[name] = mat
        return mat
    
    def create_custom_material(self, name: str, base_color: Tuple[float, float, float, float],
                              metallic: float = 0.0, roughness: float = 0.5,
                              emission_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
                              emission_strength: float = 0.0) -> bpy.types.Material:
        """Створити кастомний матеріал"""
        custom_props = {
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength
        }
        return self.create_material(name, custom_props=custom_props)
    
    def _apply_preset(self, material: bpy.types.Material, preset: MaterialPreset):
        """Застосувати пресет до матеріалу"""
        bsdf = material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = preset.base_color
        bsdf.inputs[4].default_value = preset.metallic
        bsdf.inputs[7].default_value = preset.roughness
        bsdf.inputs[17].default_value = preset.emission_color
        bsdf.inputs[18].default_value = preset.emission_strength
    
    def _apply_custom_props(self, material: bpy.types.Material, props: Dict[str, Any]):
        """Застосувати кастомні властивості"""
        bsdf = material.node_tree.nodes["Principled BSDF"]
        
        if "base_color" in props:
            bsdf.inputs[0].default_value = props["base_color"]
        if "metallic" in props:
            bsdf.inputs[4].default_value = props["metallic"]
        if "roughness" in props:
            bsdf.inputs[7].default_value = props["roughness"]
        if "emission_color" in props:
            bsdf.inputs[17].default_value = props["emission_color"]
        if "emission_strength" in props:
            bsdf.inputs[18].default_value = props["emission_strength"]
    
    def get_material(self, name: str) -> Optional[bpy.types.Material]:
        """Отримати матеріал за ім'ям"""
        return self.materials.get(name)
    
    def list_materials(self) -> list:
        """Список створених матеріалів"""
        return list(self.materials.keys())
    
    def cleanup_unused(self):
        """Очистити невикористані матеріали"""
        for material in bpy.data.materials:
            if material.users == 0:
                bpy.data.materials.remove(material)