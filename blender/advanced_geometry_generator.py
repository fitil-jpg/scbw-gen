"""Розширений генератор геометрії для Blender SCBW pipeline."""

from __future__ import annotations

import bmesh
import bpy
import bpy_extras
import mathutils
from mathutils import Vector, Color, Euler
from typing import List, Dict, Any, Tuple, Optional
import logging
import random
import math

LOG = logging.getLogger(__name__)


class AdvancedGeometryGenerator:
    """Розширений генератор геометрії з детальними моделями та ефектами."""
    
    def __init__(self, config_importer):
        self.config_importer = config_importer
        self.scene = bpy.context.scene
        self.materials_cache = {}
        
    def clear_scene(self):
        """Очищає сцену від всіх об'єктів."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Очищення матеріалів
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
        
        # Очищення текстур
        for texture in bpy.data.textures:
            bpy.data.textures.remove(texture)
        
        # Очищення мешів
        for mesh in bpy.data.meshes:
            bpy.data.meshes.remove(mesh)
    
    def setup_advanced_scene(self, shot_config: Dict[str, Any]):
        """Налаштовує розширену сцену з детальною геометрією."""
        self.clear_scene()
        
        # Налаштування рендерингу
        self._setup_render_settings()
        
        # Налаштування камери
        self._setup_advanced_camera(shot_config)
        
        # Налаштування освітлення
        self._setup_advanced_lighting(shot_config)
        
        # Генерація території
        self._generate_advanced_terrain(shot_config)
        
        # Генерація будівель
        self._generate_buildings(shot_config)
        
        # Генерація юнітів
        self._generate_advanced_units(shot_config)
        
        # Генерація ефектів
        self._generate_effects(shot_config)
        
        # Генерація UI
        self._generate_advanced_ui(shot_config)
    
    def _setup_render_settings(self):
        """Налаштовує параметри рендерингу."""
        self.scene.render.resolution_x = self.config_importer.config_data.get('image_size', [1280, 720])[0]
        self.scene.render.resolution_y = self.config_importer.config_data.get('image_size', [1280, 720])[1]
        self.scene.render.resolution_percentage = 100
        
        # Налаштування Cycles
        self.scene.render.engine = 'CYCLES'
        self.scene.cycles.samples = 256
        self.scene.cycles.use_denoising = True
        self.scene.cycles.denoiser = 'OPTIX' if bpy.app.version >= (3, 0, 0) else 'NLM'
        
        # Налаштування Eevee
        self.scene.render.engine = 'BLENDER_EEVEE'
        self.scene.eevee.use_bloom = True
        self.scene.eevee.use_ssr = True
        self.scene.eevee.use_ssr_refraction = True
        self.scene.eevee.use_soft_shadows = True
    
    def _setup_advanced_camera(self, shot_config: Dict[str, Any]):
        """Налаштовує камеру з динамічними параметрами."""
        # Створення камери
        bpy.ops.object.camera_add(location=(0, -15, 8))
        camera = bpy.context.object
        camera.name = "SCBW_Advanced_Camera"
        
        # Налаштування камери
        camera.data.lens = 50  # Фокусна відстань
        camera.data.sensor_width = 32  # Розмір сенсора
        
        # Динамічне позиціонування на основі шоту
        portal = shot_config.get('portal', {})
        if portal:
            center = portal.get('center', [0.5, 0.5])
            # Позиціонування камери відносно порталу
            camera.location.x = (center[0] - 0.5) * 20
            camera.location.y = (center[1] - 0.5) * 20 - 15
            camera.location.z = 8 + portal.get('radius', 0.2) * 10
        
        # Налаштування обертання
        camera.rotation_euler = Euler((1.1, 0, 0), 'XYZ')
        
        # Встановлення як активна камера
        self.scene.camera = camera
    
    def _setup_advanced_lighting(self, shot_config: Dict[str, Any]):
        """Налаштовує розширене освітлення."""
        # Основне освітлення (сонце)
        bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
        sun = bpy.context.object
        sun.name = "SCBW_Sun"
        sun.data.energy = 5.0
        sun.data.color = (1.0, 0.95, 0.8)  # Теплий колір
        
        # Заповнювальне освітлення
        bpy.ops.object.light_add(type='AREA', location=(-5, -5, 10))
        fill = bpy.context.object
        fill.name = "SCBW_Fill_Light"
        fill.data.energy = 2.0
        fill.data.size = 8.0
        fill.data.color = (0.8, 0.9, 1.0)  # Холодний колір
        
        # Rim lighting
        bpy.ops.object.light_add(type='AREA', location=(0, 15, 5))
        rim = bpy.context.object
        rim.name = "SCBW_Rim_Light"
        rim.data.energy = 3.0
        rim.data.size = 5.0
        rim.data.color = (1.0, 0.8, 0.6)  # Помаранчевий
        
        # Атмосферне освітлення
        world = bpy.context.scene.world
        if not world:
            world = bpy.data.worlds.new("SCBW_World")
            bpy.context.scene.world = world
        
        world.use_nodes = True
        world_nodes = world.node_tree.nodes
        world_nodes.clear()
        
        # Background shader
        bg = world_nodes.new(type='ShaderNodeBackground')
        bg.inputs['Color'].default_value = (0.1, 0.15, 0.2, 1.0)  # Темно-синій
        bg.inputs['Strength'].default_value = 0.3
        
        output = world_nodes.new(type='ShaderNodeOutputWorld')
        world.node_tree.links.new(bg.outputs['Background'], output.inputs['Surface'])
    
    def _generate_advanced_terrain(self, shot_config: Dict[str, Any]):
        """Генерує детальну територію з рельєфом."""
        # Основна територія
        bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
        terrain = bpy.context.object
        terrain.name = "SCBW_Advanced_Terrain"
        
        # Додавання рельєфу через модифікатори
        terrain.modifiers.new(name="Subdivision", type='SUBSURF')
        terrain.modifiers["Subdivision"].levels = 2
        
        # Noise модифікатор для рельєфу
        noise_mod = terrain.modifiers.new(name="Noise", type='DISPLACE')
        noise_texture = bpy.data.textures.new(name="Terrain_Noise", type='NOISE')
        noise_texture.noise_scale = 0.5
        noise_mod.texture = noise_texture
        noise_mod.strength = 0.5
        
        # Матеріал території
        terrain_mat = self._create_terrain_material(shot_config)
        terrain.data.materials.append(terrain_mat)
        
        # Додавання деталей території
        self._add_terrain_details(terrain, shot_config)
    
    def _create_terrain_material(self, shot_config: Dict[str, Any]) -> bpy.types.Material:
        """Створює матеріал для території."""
        mat = bpy.data.materials.new(name="Advanced_Terrain_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # ColorRamp для варіації кольору
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 0)
        
        # Noise texture для варіації
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 2.0
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # З'єднання вузлів
        mat.node_tree.links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        mat.node_tree.links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Налаштування кольорів на основі палітри
        palette = self.config_importer.get_palette_colors(shot_config)
        if palette:
            color_ramp.color_ramp.elements[0].color = (*palette[0], 1.0)
            color_ramp.color_ramp.elements[1].color = (*palette[1], 1.0)
        
        return mat
    
    def _add_terrain_details(self, terrain: bpy.types.Object, shot_config: Dict[str, Any]):
        """Додає деталі до території (каміння, рослини)."""
        # Випадкове розміщення каміння
        for i in range(20):
            x = random.uniform(-10, 10)
            y = random.uniform(-10, 10)
            z = random.uniform(0, 0.5)
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=random.uniform(0.2, 0.8),
                location=(x, y, z)
            )
            rock = bpy.context.object
            rock.name = f"SCBW_Rock_{i}"
            
            # Матеріал для каміння
            rock_mat = bpy.data.materials.new(name=f"Rock_Material_{i}")
            rock_mat.use_nodes = True
            rock.data.materials.append(rock_mat)
            
            # Простий матеріал
            nodes = rock_mat.node_tree.nodes
            nodes.clear()
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
            output = nodes.new(type='ShaderNodeOutputMaterial')
            rock_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    def _generate_buildings(self, shot_config: Dict[str, Any]):
        """Генерує будівлі на основі конфігурації."""
        buildings = shot_config.get('buildings', [])
        
        for building_data in buildings:
            building_type = building_data.get('type', 'command_center')
            position = building_data.get('position', [0.5, 0.5])
            owner = building_data.get('owner', 'left')
            
            # Отримання конфігурації будівлі
            building_config = self.config_importer.get_building_config(building_type)
            if not building_config:
                LOG.warning(f"Конфігурація будівлі {building_type} не знайдена")
                continue
            
            # Створення будівлі
            self._create_building(building_type, building_config, position, owner, shot_config)
    
    def _create_building(self, building_type: str, config: Dict[str, Any], 
                        position: List[float], owner: str, shot_config: Dict[str, Any]):
        """Створює конкретну будівлю."""
        # Конвертація позиції в світові координати
        x = (position[0] - 0.5) * 20
        y = (position[1] - 0.5) * 20
        z = 0
        
        # Розміри будівлі
        size = config.get('size', [64, 64])
        scale = config.get('scale', 1.0)
        
        # Створення базової геометрії
        if building_type in ['command_center', 'hatchery', 'nexus']:
            # Головні будівлі - більші та складніші
            bpy.ops.mesh.primitive_cube_add(
                size=2,
                location=(x, y, z + 1)
            )
            building = bpy.context.object
            building.scale = (scale * 1.5, scale * 1.5, scale)
        else:
            # Звичайні будівлі
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x, y, z + 0.5)
            )
            building = bpy.context.object
            building.scale = (scale, scale, scale * 0.8)
        
        building.name = f"SCBW_Building_{building_type}_{owner}"
        
        # Додавання деталей
        self._add_building_details(building, building_type, config)
        
        # Створення матеріалу
        building_mat = self._create_building_material(building_type, config, owner, shot_config)
        building.data.materials.append(building_mat)
    
    def _add_building_details(self, building: bpy.types.Object, building_type: str, config: Dict[str, Any]):
        """Додає деталі до будівлі."""
        # Додавання модифікаторів для деталізації
        building.modifiers.new(name="Bevel", type='BEVEL')
        building.modifiers["Bevel"].width = 0.1
        building.modifiers["Bevel"].segments = 2
        
        # Додавання вікон для великих будівель
        if building_type in ['command_center', 'hatchery', 'nexus']:
            # Створення вікон через boolean операції
            bpy.ops.mesh.primitive_cube_add(
                size=0.3,
                location=(building.location.x, building.location.y, building.location.z + 0.5)
            )
            window = bpy.context.object
            window.name = f"Window_{building.name}"
            
            # Boolean модифікатор
            bool_mod = building.modifiers.new(name="Window_Boolean", type='BOOLEAN')
            bool_mod.object = window
            bool_mod.operation = 'DIFFERENCE'
    
    def _create_building_material(self, building_type: str, config: Dict[str, Any], 
                                 owner: str, shot_config: Dict[str, Any]) -> bpy.types.Material:
        """Створює матеріал для будівлі."""
        mat = bpy.data.materials.new(name=f"Building_Material_{building_type}_{owner}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # З'єднання
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Налаштування кольору на основі власника
        palette = self.config_importer.get_palette_colors(shot_config)
        if palette and len(palette) > 1:
            if owner == 'left':
                color = palette[1] if len(palette) > 1 else palette[0]
            else:
                color = palette[2] if len(palette) > 2 else palette[1]
            
            bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        
        # Налаштування металевості для технологічних будівель
        if building_type in ['command_center', 'barracks', 'factory']:
            bsdf.inputs['Metallic'].default_value = 0.8
            bsdf.inputs['Roughness'].default_value = 0.3
        else:
            bsdf.inputs['Metallic'].default_value = 0.2
            bsdf.inputs['Roughness'].default_value = 0.7
        
        return mat
    
    def _generate_advanced_units(self, shot_config: Dict[str, Any]):
        """Генерує детальні юніти з різними типами."""
        # Лівий кластер
        if 'left_cluster' in shot_config:
            self._create_advanced_unit_cluster(
                shot_config['left_cluster'],
                'left',
                shot_config
            )
        
        # Правий кластер
        if 'right_cluster' in shot_config:
            self._create_advanced_unit_cluster(
                shot_config['right_cluster'],
                'right',
                shot_config
            )
    
    def _create_advanced_unit_cluster(self, cluster_config: Dict[str, Any], 
                                    side: str, shot_config: Dict[str, Any]):
        """Створює кластер детальних юнітів."""
        rect = cluster_config.get('rect', [0.1, 0.5])
        count = cluster_config.get('count', 5)
        size = cluster_config.get('size', [16, 32])
        unit_types = cluster_config.get('unit_types', ['marine'])
        
        # Конвертація координат
        x_start = (rect[0] - 0.5) * 20
        y_start = (rect[1] - 0.5) * 20
        
        unit_width = size[0] / 100.0
        unit_height = size[1] / 100.0
        
        for i in range(count):
            unit_type = unit_types[i % len(unit_types)]
            unit_config = self.config_importer.get_unit_config(unit_type)
            
            # Позиція юніта
            x = x_start + (i % 3) * unit_width * 1.5
            y = y_start + (i // 3) * unit_height * 1.5
            z = unit_height / 2
            
            # Створення юніта
            self._create_advanced_unit(unit_type, unit_config, (x, y, z), side, i, shot_config)
    
    def _create_advanced_unit(self, unit_type: str, config: Dict[str, Any], 
                            position: Tuple[float, float, float], side: str, 
                            index: int, shot_config: Dict[str, Any]):
        """Створює детальний юніт."""
        x, y, z = position
        
        # Створення геометрії на основі типу юніта
        if unit_type in ['marine', 'firebat', 'medic']:
            # Людські юніти - антропоморфна форма
            self._create_humanoid_unit(unit_type, (x, y, z), side, index, shot_config)
        elif unit_type in ['zergling', 'hydralisk', 'mutalisk']:
            # Зерг юніти - більш органічні форми
            self._create_zerg_unit(unit_type, (x, y, z), side, index, shot_config)
        elif unit_type in ['zealot', 'dragoon', 'high_templar']:
            # Протосс юніти - технологічні форми
            self._create_protoss_unit(unit_type, (x, y, z), side, index, shot_config)
        else:
            # За замовчуванням - простий куб
            self._create_default_unit(unit_type, (x, y, z), side, index, shot_config)
    
    def _create_humanoid_unit(self, unit_type: str, position: Tuple[float, float, float], 
                            side: str, index: int, shot_config: Dict[str, Any]):
        """Створює людський юніт."""
        x, y, z = position
        
        # Тіло
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=(x, y, z))
        body = bpy.context.object
        body.name = f"SCBW_Unit_{unit_type}_{side}_{index}_body"
        body.scale = (0.8, 0.4, 1.2)
        
        # Голова
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, y, z + 0.6))
        head = bpy.context.object
        head.name = f"SCBW_Unit_{unit_type}_{side}_{index}_head"
        
        # Зброя
        if unit_type == 'marine':
            bpy.ops.mesh.primitive_cube_add(size=0.1, location=(x + 0.3, y, z + 0.3))
            weapon = bpy.context.object
            weapon.name = f"SCBW_Unit_{unit_type}_{side}_{index}_weapon"
            weapon.scale = (2.0, 0.1, 0.1)
        
        # Матеріал
        self._create_unit_material(unit_type, side, shot_config)
    
    def _create_zerg_unit(self, unit_type: str, position: Tuple[float, float, float], 
                         side: str, index: int, shot_config: Dict[str, Any]):
        """Створює зерг юніт."""
        x, y, z = position
        
        # Органічна форма
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(x, y, z))
        body = bpy.context.object
        body.name = f"SCBW_Unit_{unit_type}_{side}_{index}_body"
        body.scale = (1.2, 0.8, 0.6)
        
        # Додавання модифікаторів для органічної форми
        body.modifiers.new(name="Subdivision", type='SUBSURF')
        body.modifiers["Subdivision"].levels = 1
        
        # Матеріал
        self._create_unit_material(unit_type, side, shot_config)
    
    def _create_protoss_unit(self, unit_type: str, position: Tuple[float, float, float], 
                           side: str, index: int, shot_config: Dict[str, Any]):
        """Створює протосс юніт."""
        x, y, z = position
        
        # Технологічна форма
        bpy.ops.mesh.primitive_cube_add(size=0.4, location=(x, y, z))
        body = bpy.context.object
        body.name = f"SCBW_Unit_{unit_type}_{side}_{index}_body"
        body.scale = (1.0, 0.6, 1.5)
        
        # Додавання bevel для технологічного вигляду
        body.modifiers.new(name="Bevel", type='BEVEL')
        body.modifiers["Bevel"].width = 0.05
        body.modifiers["Bevel"].segments = 3
        
        # Матеріал
        self._create_unit_material(unit_type, side, shot_config)
    
    def _create_default_unit(self, unit_type: str, position: Tuple[float, float, float], 
                           side: str, index: int, shot_config: Dict[str, Any]):
        """Створює юніт за замовчуванням."""
        x, y, z = position
        
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=(x, y, z))
        unit = bpy.context.object
        unit.name = f"SCBW_Unit_{unit_type}_{side}_{index}"
        
        # Матеріал
        self._create_unit_material(unit_type, side, shot_config)
    
    def _create_unit_material(self, unit_type: str, side: str, shot_config: Dict[str, Any]):
        """Створює матеріал для юніта."""
        mat = bpy.data.materials.new(name=f"Unit_Material_{unit_type}_{side}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # З'єднання
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Налаштування кольору
        palette = self.config_importer.get_palette_colors(shot_config)
        if palette:
            if side == 'left':
                color = palette[1] if len(palette) > 1 else palette[0]
            else:
                color = palette[2] if len(palette) > 2 else palette[1]
            
            bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        
        # Налаштування матеріалу на основі типу
        if unit_type in ['marine', 'firebat', 'medic']:
            bsdf.inputs['Metallic'].default_value = 0.3
            bsdf.inputs['Roughness'].default_value = 0.6
        elif unit_type in ['zergling', 'hydralisk', 'mutalisk']:
            bsdf.inputs['Metallic'].default_value = 0.1
            bsdf.inputs['Roughness'].default_value = 0.8
        elif unit_type in ['zealot', 'dragoon', 'high_templar']:
            bsdf.inputs['Metallic'].default_value = 0.9
            bsdf.inputs['Roughness'].default_value = 0.2
            bsdf.inputs['Emission'].default_value = (0.1, 0.2, 0.5, 1.0)
    
    def _generate_effects(self, shot_config: Dict[str, Any]):
        """Генерує спеціальні ефекти."""
        # Портал
        if 'portal' in shot_config:
            self._create_advanced_portal(shot_config['portal'], shot_config)
        
        # Ефекти зброї
        self._create_weapon_effects(shot_config)
    
    def _create_advanced_portal(self, portal_config: Dict[str, Any], shot_config: Dict[str, Any]):
        """Створює розширений портал з ефектами."""
        center = portal_config.get('center', [0.5, 0.5])
        radius = portal_config.get('radius', 0.2)
        
        x_center = (center[0] - 0.5) * 20
        y_center = (center[1] - 0.5) * 20
        world_radius = radius * 20
        
        # Основа порталу
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=world_radius,
            location=(x_center, y_center, 0)
        )
        portal = bpy.context.object
        portal.name = "SCBW_Advanced_Portal"
        
        # Матеріал порталу
        portal_mat = bpy.data.materials.new(name="Advanced_Portal_Material")
        portal_mat.use_nodes = True
        portal.data.materials.append(portal_mat)
        
        # Налаштування шейдера
        nodes = portal_mat.node_tree.nodes
        nodes.clear()
        
        # Emission для світіння
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0)
        emission.inputs['Strength'].default_value = 3.0
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        portal_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Додавання анімації
        portal.animation_data_create()
        portal.keyframe_insert(data_path="rotation_euler", frame=1)
        portal.rotation_euler = (0, 0, 0)
        portal.keyframe_insert(data_path="rotation_euler", frame=100)
        portal.rotation_euler = (0, 0, math.radians(360))
    
    def _create_weapon_effects(self, shot_config: Dict[str, Any]):
        """Створює ефекти зброї та вибухів."""
        # Випадкові ефекти вибухів
        for i in range(5):
            x = random.uniform(-8, 8)
            y = random.uniform(-8, 8)
            z = random.uniform(0, 2)
            
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=random.uniform(0.5, 1.5),
                location=(x, y, z)
            )
            explosion = bpy.context.object
            explosion.name = f"SCBW_Explosion_{i}"
            
            # Матеріал вибуху
            explosion_mat = bpy.data.materials.new(name=f"Explosion_Material_{i}")
            explosion_mat.use_nodes = True
            explosion.data.materials.append(explosion_mat)
            
            # Emission для вибуху
            nodes = explosion_mat.node_tree.nodes
            nodes.clear()
            emission = nodes.new(type='ShaderNodeEmission')
            emission.inputs['Color'].default_value = (1.0, 0.3, 0.0, 1.0)
            emission.inputs['Strength'].default_value = 2.0
            output = nodes.new(type='ShaderNodeOutputMaterial')
            explosion_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    def _generate_advanced_ui(self, shot_config: Dict[str, Any]):
        """Генерує розширений UI."""
        if 'hud' not in shot_config:
            return
        
        # Основа UI
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, -12, 0))
        ui_plane = bpy.context.object
        ui_plane.name = "SCBW_Advanced_UI"
        ui_plane.scale = (15, 1, 1)
        
        # Матеріал UI
        ui_mat = bpy.data.materials.new(name="Advanced_UI_Material")
        ui_mat.use_nodes = True
        ui_plane.data.materials.append(ui_mat)
        
        # Налаштування шейдера
        nodes = ui_mat.node_tree.nodes
        nodes.clear()
        
        # Emission для UI
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        emission.inputs['Strength'].default_value = 1.0
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        ui_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Додавання UI елементів
        self._add_ui_elements(shot_config['hud'])
    
    def _add_ui_elements(self, hud_config: Dict[str, Any]):
        """Додає елементи UI."""
        # Лівий бік UI
        if 'left' in hud_config:
            self._create_ui_panel(hud_config['left'], 'left', (-6, -12, 0.1))
        
        # Правий бік UI
        if 'right' in hud_config:
            self._create_ui_panel(hud_config['right'], 'right', (6, -12, 0.1))
    
    def _create_ui_panel(self, panel_data: Dict[str, Any], side: str, position: Tuple[float, float, float]):
        """Створює панель UI."""
        x, y, z = position
        
        # Панель
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, z))
        panel = bpy.context.object
        panel.name = f"SCBW_UI_Panel_{side}"
        panel.scale = (3, 0.8, 1)
        
        # Матеріал панелі
        panel_mat = bpy.data.materials.new(name=f"UI_Panel_Material_{side}")
        panel_mat.use_nodes = True
        panel.data.materials.append(panel_mat)
        
        # Налаштування
        nodes = panel_mat.node_tree.nodes
        nodes.clear()
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = (0.1, 0.1, 0.2, 1.0)
        output = nodes.new(type='ShaderNodeOutputMaterial')
        panel_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])


if __name__ == "__main__":
    # Тестування генератора геометрії
    logging.basicConfig(level=logging.INFO)
    
    # Створення тестової конфігурації
    from advanced_config_importer import AdvancedConfigImporter
    
    importer = AdvancedConfigImporter("sample_config.yaml")
    config = importer.load_config()
    assets = importer.load_asset_configs()
    
    # Тестування генератора
    generator = AdvancedGeometryGenerator(importer)
    shot_config = importer.get_shot_config('demo_shot_001')
    
    if shot_config:
        generator.setup_advanced_scene(shot_config)
        print("Розширена сцена створена успішно!")
    else:
        print("Шот не знайдено!")