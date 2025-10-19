#!/usr/bin/env python3
"""
MVP Material System Test - Версія без Blender для тестування
"""

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

class MVPMaterialSystemTest:
    """Компактна система матеріалів для MVP (без Blender)"""
    
    def __init__(self):
        self.materials: Dict[str, Dict[str, Any]] = {}
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
                       custom_props: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Створити матеріал"""
        if name in self.materials:
            return self.materials[name]
        
        material_data = {"name": name}
        
        # Використати пресет або створити з нуля
        if preset_name and preset_name in self.presets:
            preset = self.presets[preset_name]
            material_data.update({
                "base_color": preset.base_color,
                "metallic": preset.metallic,
                "roughness": preset.roughness,
                "emission_color": preset.emission_color,
                "emission_strength": preset.emission_strength
            })
        elif custom_props:
            material_data.update(custom_props)
        
        self.materials[name] = material_data
        return material_data
    
    def create_custom_material(self, name: str, base_color: Tuple[float, float, float, float],
                              metallic: float = 0.0, roughness: float = 0.5,
                              emission_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
                              emission_strength: float = 0.0) -> Dict[str, Any]:
        """Створити кастомний матеріал"""
        custom_props = {
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength
        }
        return self.create_material(name, custom_props=custom_props)
    
    def get_material(self, name: str) -> Optional[Dict[str, Any]]:
        """Отримати матеріал за ім'ям"""
        return self.materials.get(name)
    
    def list_materials(self) -> list:
        """Список створених матеріалів"""
        return list(self.materials.keys())