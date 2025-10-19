"""
Генератор матеріалів для StarCraft Brood War сцен
Підтримує процедурні матеріали, текстури та UV-розгортання
"""

import bpy
import bmesh
import os
import math
from mathutils import Vector, Color
from typing import Dict, Any, List, Optional, Tuple
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StarCraftMaterialGenerator:
    """Генератор матеріалів для StarCraft сцен"""
    
    def __init__(self, texture_path: str = "assets/textures"):
        self.texture_path = texture_path
        self.material_cache = {}
        
    def create_unit_material(self, unit_type: str, team_color: Tuple[float, float, float], 
                           metallic: float = 0.1, roughness: float = 0.8) -> bpy.types.Material:
        """
        Створює матеріал для юніта StarCraft
        
        Args:
            unit_type: Тип юніта (marine, zealot, zergling, etc.)
            team_color: Колір команди (R, G, B)
            metallic: Металічність (0-1)
            roughness: Шорсткість (0-1)
        
        Returns:
            Створений матеріал
        """
        material_name = f"SC_{unit_type}_Material"
        
        if material_name in self.material_cache:
            return self.material_cache[material_name]
        
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Team color
        team_color_node = nodes.new(type='ShaderNodeRGB')
        team_color_node.outputs[0].default_value = (*team_color, 1.0)
        team_color_node.location = (-600, 200)
        
        # Noise for detail variation
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 20.0
        noise.inputs['Detail'].default_value = 5.0
        noise.inputs['Roughness'].default_value = 0.5
        noise.location = (-600, 0)
        
        # Mix team color with noise
        mix_color = nodes.new(type='ShaderNodeMix')
        mix_color.inputs['Fac'].default_value = 0.3
        mix_color.location = (-400, 100)
        
        # Metallic value
        metallic_value = nodes.new(type='ShaderNodeValue')
        metallic_value.outputs[0].default_value = metallic
        metallic_value.location = (-600, -200)
        
        # Roughness value
        roughness_value = nodes.new(type='ShaderNodeValue')
        roughness_value.outputs[0].default_value = roughness
        roughness_value.location = (-600, -400)
        
        # Emission for glowing parts (optional)
        emission_value = nodes.new(type='ShaderNodeValue')
        emission_value.outputs[0].default_value = 0.0
        emission_value.location = (-600, -600)
        
        # Mix emission with base color
        mix_emission = nodes.new(type='ShaderNodeMix')
        mix_emission.inputs['Fac'].default_value = 0.0
        mix_emission.location = (-200, 0)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Connections
        material.node_tree.links.new(team_color_node.outputs['Color'], mix_color.inputs['Color1'])
        material.node_tree.links.new(noise.outputs['Color'], mix_color.inputs['Color2'])
        material.node_tree.links.new(mix_color.outputs['Color'], mix_emission.inputs['Color1'])
        material.node_tree.links.new(emission_value.outputs['Value'], mix_emission.inputs['Fac'])
        material.node_tree.links.new(mix_emission.outputs['Color'], bsdf.inputs['Base Color'])
        material.node_tree.links.new(metallic_value.outputs['Value'], bsdf.inputs['Metallic'])
        material.node_tree.links.new(roughness_value.outputs['Value'], bsdf.inputs['Roughness'])
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        self.material_cache[material_name] = material
        logger.info(f"Створено матеріал для юніта: {unit_type}")
        return material
    
    def create_terrain_material(self, terrain_type: str = "grass") -> bpy.types.Material:
        """
        Створює матеріал для території
        
        Args:
            terrain_type: Тип території (grass, dirt, stone, metal)
        
        Returns:
            Створений матеріал
        """
        material_name = f"Terrain_{terrain_type}_Material"
        
        if material_name in self.material_cache:
            return self.material_cache[material_name]
        
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Terrain color based on type
        terrain_colors = {
            "grass": (0.2, 0.6, 0.2, 1.0),
            "dirt": (0.4, 0.3, 0.2, 1.0),
            "stone": (0.5, 0.5, 0.5, 1.0),
            "metal": (0.3, 0.3, 0.4, 1.0),
            "sand": (0.8, 0.7, 0.5, 1.0)
        }
        
        base_color = terrain_colors.get(terrain_type, (0.3, 0.3, 0.3, 1.0))
        
        # Base color
        color_node = nodes.new(type='ShaderNodeRGB')
        color_node.outputs[0].default_value = base_color
        color_node.location = (-600, 200)
        
        # Noise for variation
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 10.0
        noise.inputs['Detail'].default_value = 10.0
        noise.inputs['Roughness'].default_value = 0.5
        noise.location = (-600, 0)
        
        # Mix base color with noise
        mix = nodes.new(type='ShaderNodeMix')
        mix.inputs['Fac'].default_value = 0.2
        mix.location = (-400, 100)
        
        # Roughness based on terrain type
        roughness_values = {
            "grass": 0.9,
            "dirt": 0.8,
            "stone": 0.7,
            "metal": 0.3,
            "sand": 0.6
        }
        
        roughness_value = nodes.new(type='ShaderNodeValue')
        roughness_value.outputs[0].default_value = roughness_values.get(terrain_type, 0.8)
        roughness_value.location = (-600, -200)
        
        # Metallic based on terrain type
        metallic_values = {
            "grass": 0.0,
            "dirt": 0.0,
            "stone": 0.1,
            "metal": 0.8,
            "sand": 0.0
        }
        
        metallic_value = nodes.new(type='ShaderNodeValue')
        metallic_value.outputs[0].default_value = metallic_values.get(terrain_type, 0.0)
        metallic_value.location = (-600, -400)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Connections
        material.node_tree.links.new(color_node.outputs['Color'], mix.inputs['Color1'])
        material.node_tree.links.new(noise.outputs['Color'], mix.inputs['Color2'])
        material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
        material.node_tree.links.new(roughness_value.outputs['Value'], bsdf.inputs['Roughness'])
        material.node_tree.links.new(metallic_value.outputs['Value'], bsdf.inputs['Metallic'])
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        self.material_cache[material_name] = material
        logger.info(f"Створено матеріал для території: {terrain_type}")
        return material
    
    def create_ui_material(self, ui_type: str = "hud") -> bpy.types.Material:
        """
        Створює матеріал для UI елементів
        
        Args:
            ui_type: Тип UI (hud, button, panel)
        
        Returns:
            Створений матеріал
        """
        material_name = f"UI_{ui_type}_Material"
        
        if material_name in self.material_cache:
            return self.material_cache[material_name]
        
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        # Emission shader for UI
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        
        # UI color
        ui_colors = {
            "hud": (0.1, 0.1, 0.1, 1.0),
            "button": (0.2, 0.2, 0.4, 1.0),
            "panel": (0.05, 0.05, 0.05, 1.0)
        }
        
        ui_color = ui_colors.get(ui_type, (0.1, 0.1, 0.1, 1.0))
        
        color_node = nodes.new(type='ShaderNodeRGB')
        color_node.outputs[0].default_value = ui_color
        color_node.location = (-200, 0)
        
        # Strength
        strength_value = nodes.new(type='ShaderNodeValue')
        strength_value.outputs[0].default_value = 1.0
        strength_value.location = (-200, -200)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Connections
        material.node_tree.links.new(color_node.outputs['Color'], emission.inputs['Color'])
        material.node_tree.links.new(strength_value.outputs['Value'], emission.inputs['Strength'])
        material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        self.material_cache[material_name] = material
        logger.info(f"Створено UI матеріал: {ui_type}")
        return material
    
    def create_effect_material(self, effect_type: str = "portal") -> bpy.types.Material:
        """
        Створює матеріал для спеціальних ефектів
        
        Args:
            effect_type: Тип ефекту (portal, explosion, shield)
        
        Returns:
            Створений матеріал
        """
        material_name = f"Effect_{effect_type}_Material"
        
        if material_name in self.material_cache:
            return self.material_cache[material_name]
        
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        if effect_type == "portal":
            # Portal effect with animated noise
            emission = nodes.new(type='ShaderNodeEmission')
            emission.location = (0, 0)
            
            # Animated noise
            noise = nodes.new(type='ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 5.0
            noise.inputs['Detail'].default_value = 15.0
            noise.location = (-400, 0)
            
            # Time for animation
            time = nodes.new(type='ShaderNodeTexCoord')
            time.location = (-600, 0)
            
            # Mapping for animation
            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-500, 0)
            
            # Portal color
            portal_color = nodes.new(type='ShaderNodeRGB')
            portal_color.outputs[0].default_value = (0.0, 0.8, 1.0, 1.0)
            portal_color.location = (-400, 200)
            
            # Mix color with noise
            mix = nodes.new(type='ShaderNodeMix')
            mix.inputs['Fac'].default_value = 0.5
            mix.location = (-200, 100)
            
            # Strength
            strength_value = nodes.new(type='ShaderNodeValue')
            strength_value.outputs[0].default_value = 2.0
            strength_value.location = (-200, -200)
            
            # Output
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (200, 0)
            
            # Connections
            material.node_tree.links.new(time.outputs['Generated'], mapping.inputs['Vector'])
            material.node_tree.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
            material.node_tree.links.new(portal_color.outputs['Color'], mix.inputs['Color1'])
            material.node_tree.links.new(noise.outputs['Color'], mix.inputs['Color2'])
            material.node_tree.links.new(mix.outputs['Color'], emission.inputs['Color'])
            material.node_tree.links.new(strength_value.outputs['Value'], emission.inputs['Strength'])
            material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
            
        elif effect_type == "explosion":
            # Explosion effect
            emission = nodes.new(type='ShaderNodeEmission')
            emission.location = (0, 0)
            
            # Fire color gradient
            color_ramp = nodes.new(type='ShaderNodeValToRGB')
            color_ramp.color_ramp.elements[0].color = (1.0, 0.0, 0.0, 1.0)  # Red
            color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 0.0, 1.0)  # Yellow
            color_ramp.location = (-200, 0)
            
            # Noise for fire pattern
            noise = nodes.new(type='ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 10.0
            noise.inputs['Detail'].default_value = 20.0
            noise.location = (-400, 0)
            
            # Output
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (200, 0)
            
            # Connections
            material.node_tree.links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
            material.node_tree.links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
            material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        self.material_cache[material_name] = material
        logger.info(f"Створено матеріал ефекту: {effect_type}")
        return material
    
    def apply_uv_mapping(self, obj: bpy.types.Object, mapping_type: str = "smart") -> None:
        """
        Застосовує UV-розгортання до об'єкта
        
        Args:
            obj: Об'єкт для UV-розгортання
            mapping_type: Тип розгортання (smart, cube, cylinder, sphere)
        """
        if obj.type != 'MESH':
            logger.warning(f"Об'єкт {obj.name} не є мешем")
            return
        
        # Select object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Enter Edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')
        
        if mapping_type == "smart":
            bpy.ops.uv.smart_project(
                angle_limit=math.radians(66),
                island_margin=0.001,
                area_weight=0.0,
                correct_aspect=True
            )
        elif mapping_type == "cube":
            bpy.ops.uv.cube_project(
                cube_size=1.0,
                correct_aspect=True,
                clip_to_bounds=False,
                scale_to_bounds=True
            )
        elif mapping_type == "cylinder":
            bpy.ops.uv.cylinder_project(
                direction='ALIGN_TO_OBJECT',
                align='POLAR_ZX',
                radius=1.0,
                correct_aspect=True
            )
        elif mapping_type == "sphere":
            bpy.ops.uv.sphere_project(
                direction='ALIGN_TO_OBJECT',
                align='POLAR_ZX',
                correct_aspect=True
            )
        
        # Pack UV islands
        bpy.ops.uv.pack_islands(margin=0.001)
        
        # Return to Object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        logger.info(f"Застосовано UV-розгортання {mapping_type} до {obj.name}")
    
    def create_pbr_material(self, texture_paths: Dict[str, str], material_name: str) -> bpy.types.Material:
        """
        Створює PBR матеріал з текстурними картами
        
        Args:
            texture_paths: Словник з шляхами до текстур
            material_name: Назва матеріалу
        
        Returns:
            Створений PBR матеріал
        """
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Albedo texture
        if "albedo" in texture_paths and os.path.exists(texture_paths["albedo"]):
            albedo_tex = nodes.new(type='ShaderNodeTexImage')
            albedo_tex.image = bpy.data.images.load(texture_paths["albedo"])
            albedo_tex.location = (-600, 200)
            material.node_tree.links.new(albedo_tex.outputs['Color'], bsdf.inputs['Base Color'])
        
        # Normal map
        if "normal" in texture_paths and os.path.exists(texture_paths["normal"]):
            normal_tex = nodes.new(type='ShaderNodeTexImage')
            normal_tex.image = bpy.data.images.load(texture_paths["normal"])
            normal_tex.location = (-600, 0)
            
            normal_map = nodes.new(type='ShaderNodeNormalMap')
            normal_map.location = (-400, 0)
            
            material.node_tree.links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
            material.node_tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        
        # Roughness map
        if "roughness" in texture_paths and os.path.exists(texture_paths["roughness"]):
            roughness_tex = nodes.new(type='ShaderNodeTexImage')
            roughness_tex.image = bpy.data.images.load(texture_paths["roughness"])
            roughness_tex.location = (-600, -200)
            material.node_tree.links.new(roughness_tex.outputs['Color'], bsdf.inputs['Roughness'])
        
        # Metallic map
        if "metallic" in texture_paths and os.path.exists(texture_paths["metallic"]):
            metallic_tex = nodes.new(type='ShaderNodeTexImage')
            metallic_tex.image = bpy.data.images.load(texture_paths["metallic"])
            metallic_tex.location = (-600, -400)
            material.node_tree.links.new(metallic_tex.outputs['Color'], bsdf.inputs['Metallic'])
        
        # Emission map
        if "emission" in texture_paths and os.path.exists(texture_paths["emission"]):
            emission_tex = nodes.new(type='ShaderNodeTexImage')
            emission_tex.image = bpy.data.images.load(texture_paths["emission"])
            emission_tex.location = (-600, -600)
            material.node_tree.links.new(emission_tex.outputs['Color'], bsdf.inputs['Emission Color'])
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        logger.info(f"Створено PBR матеріал: {material_name}")
        return material
    
    def clear_material_cache(self) -> None:
        """Очищає кеш матеріалів"""
        for material in self.material_cache.values():
            if material.users == 0:
                bpy.data.materials.remove(material)
        self.material_cache.clear()
        logger.info("Кеш матеріалів очищено")

# Приклад використання
if __name__ == "__main__":
    # Ініціалізація генератора матеріалів
    material_gen = StarCraftMaterialGenerator()
    
    # Створення матеріалів для різних типів об'єктів
    marine_material = material_gen.create_unit_material("marine", (0.2, 0.4, 0.8))
    zealot_material = material_gen.create_unit_material("zealot", (0.8, 0.2, 0.2))
    zergling_material = material_gen.create_unit_material("zergling", (0.4, 0.8, 0.2))
    
    # Матеріали для території
    grass_material = material_gen.create_terrain_material("grass")
    dirt_material = material_gen.create_terrain_material("dirt")
    metal_material = material_gen.create_terrain_material("metal")
    
    # UI матеріали
    hud_material = material_gen.create_ui_material("hud")
    button_material = material_gen.create_ui_material("button")
    
    # Ефекти
    portal_material = material_gen.create_effect_material("portal")
    explosion_material = material_gen.create_effect_material("explosion")
    
    print("Матеріали створено успішно!")