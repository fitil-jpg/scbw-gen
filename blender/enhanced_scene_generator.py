"""
Покращений генератор сцен з підтримкою матеріалів та текстур
Інтегрується з існуючим StarCraft пайплайном
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Color
from typing import List, Dict, Any, Tuple
import logging
from .material_generator import StarCraftMaterialGenerator

LOG = logging.getLogger(__name__)

class EnhancedStarCraftSceneGenerator:
    """Покращений генератор StarCraft сцен з матеріалами"""
    
    def __init__(self, config):
        self.config = config
        self.scene = bpy.context.scene
        self.material_gen = StarCraftMaterialGenerator()
        
        # Кольори команд
        self.team_colors = {
            "terran": (0.2, 0.4, 0.8),      # Синій
            "protoss": (0.8, 0.2, 0.2),     # Червоний
            "zerg": (0.4, 0.8, 0.2),        # Зелений
            "neutral": (0.5, 0.5, 0.5)      # Сірий
        }
        
    def clear_scene(self):
        """Очищає сцену та матеріали"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Очищення матеріалів
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
        
        # Очищення текстур
        for image in bpy.data.images:
            bpy.data.images.remove(image)
    
    def setup_scene(self, shot_config):
        """Налаштовує сцену з матеріалами"""
        self.clear_scene()
        
        # Налаштування рендерингу
        self.scene.render.resolution_x = self.config.image_size[0]
        self.scene.render.resolution_y = self.config.image_size[1]
        self.scene.render.resolution_percentage = 100
        
        # Налаштування камери
        self._setup_camera()
        
        # Налаштування освітлення
        self._setup_lighting()
        
        # Генерація території з матеріалами
        self._generate_terrain_with_materials(shot_config)
        
        # Генерація юнітів з матеріалами
        self._generate_units_with_materials(shot_config)
        
        # Генерація UI з матеріалами
        self._generate_ui_with_materials(shot_config)
        
        # Генерація ефектів
        self._generate_effects_with_materials(shot_config)
    
    def _setup_camera(self):
        """Налаштовує камеру"""
        bpy.ops.object.camera_add(location=(0, -10, 5))
        camera = bpy.context.object
        camera.name = "SCBW_Camera"
        camera.rotation_euler = (1.1, 0, 0)
        self.scene.camera = camera
    
    def _setup_lighting(self):
        """Налаштовує освітлення"""
        # Основне світло
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.object
        sun.name = "SCBW_Sun"
        sun.data.energy = 3.0
        sun.data.color = (1.0, 0.95, 0.8)  # Тепле світло
        
        # Заповнювальне світло
        bpy.ops.object.light_add(type='AREA', location=(-3, -3, 8))
        fill = bpy.context.object
        fill.name = "SCBW_Fill"
        fill.data.energy = 1.0
        fill.data.size = 5.0
        fill.data.color = (0.7, 0.8, 1.0)  # Холодне світло
    
    def _generate_terrain_with_materials(self, shot_config):
        """Генерує територію з матеріалами"""
        # Створення основної площини
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        terrain = bpy.context.object
        terrain.name = "SCBW_Terrain"
        
        # Визначення типу території
        terrain_type = shot_config.get("terrain_type", "grass")
        
        # Створення матеріалу для території
        terrain_material = self.material_gen.create_terrain_material(terrain_type)
        terrain.data.materials.append(terrain_material)
        
        # Додавання деталей до території
        self._add_terrain_details(terrain, terrain_type)
        
        # UV-розгортання
        self.material_gen.apply_uv_mapping(terrain, "smart")
    
    def _add_terrain_details(self, terrain, terrain_type):
        """Додає деталі до території"""
        if terrain_type == "grass":
            # Додавання каміння
            for i in range(5):
                bpy.ops.mesh.primitive_cube_add(
                    size=0.3,
                    location=(
                        (i - 2) * 2,
                        (i % 2) * 2 - 1,
                        0.15
                    )
                )
                stone = bpy.context.object
                stone.name = f"Terrain_Stone_{i}"
                stone.scale = (1, 1, 0.5)
                
                # Матеріал для каміння
                stone_material = self.material_gen.create_terrain_material("stone")
                stone.data.materials.append(stone_material)
        
        elif terrain_type == "metal":
            # Додавання металевих панелей
            for i in range(3):
                for j in range(3):
                    bpy.ops.mesh.primitive_cube_add(
                        size=0.8,
                        location=(
                            (i - 1) * 2,
                            (j - 1) * 2,
                            0.05
                        )
                    )
                    panel = bpy.context.object
                    panel.name = f"Terrain_Panel_{i}_{j}"
                    panel.scale = (1, 1, 0.1)
    
    def _generate_units_with_materials(self, shot_config):
        """Генерує юнітів з матеріалами"""
        # Ліва команда
        if shot_config.left_cluster:
            self._create_unit_cluster_with_materials(
                shot_config.left_cluster,
                "terran",
                "left"
            )
        
        # Права команда
        if shot_config.right_cluster:
            self._create_unit_cluster_with_materials(
                shot_config.right_cluster,
                "protoss",
                "right"
            )
    
    def _create_unit_cluster_with_materials(self, cluster_config, race, side):
        """Створює кластер юнітів з матеріалами"""
        rect = cluster_config.get("rect", [0.1, 0.5])
        count = cluster_config.get("count", 5)
        size = cluster_config.get("size", [16, 32])
        unit_type = cluster_config.get("unit_type", "marine")
        
        # Конвертація координат
        x_start = (rect[0] - 0.5) * 20
        y_start = (rect[1] - 0.5) * 20
        
        unit_width = size[0] / 100.0
        unit_height = size[1] / 100.0
        
        # Колір команди
        team_color = self.team_colors.get(race, self.team_colors["neutral"])
        
        for i in range(count):
            # Створення юніта
            unit_obj = self._create_unit_geometry(unit_type, unit_width, unit_height)
            unit_obj.location = (
                x_start + (i % 3) * unit_width * 1.5,
                y_start + (i // 3) * unit_height * 1.5,
                unit_height / 2
            )
            unit_obj.name = f"SCBW_Unit_{side}_{i}"
            
            # Створення матеріалу для юніта
            unit_material = self.material_gen.create_unit_material(
                unit_type, 
                team_color,
                metallic=0.2 if race == "terran" else 0.1,
                roughness=0.7 if race == "terran" else 0.8
            )
            unit_obj.data.materials.append(unit_material)
            
            # UV-розгортання
            self.material_gen.apply_uv_mapping(unit_obj, "smart")
    
    def _create_unit_geometry(self, unit_type, width, height):
        """Створює геометрію юніта"""
        if unit_type == "marine":
            # Простий куб для морпіха
            bpy.ops.mesh.primitive_cube_add(size=width)
            unit = bpy.context.object
            unit.scale = (1, 1, height/width)
            
        elif unit_type == "zealot":
            # Більш складний об'єкт для зелота
            bpy.ops.mesh.primitive_cube_add(size=width)
            unit = bpy.context.object
            unit.scale = (1, 1, height/width)
            
            # Додавання "крил"
            bpy.ops.mesh.primitive_cube_add(size=width*0.3)
            wing = bpy.context.object
            wing.location = (width*0.6, 0, height*0.3)
            wing.scale = (0.2, 1, 0.5)
            
            # Об'єднання об'єктів
            bpy.context.view_layer.objects.active = unit
            wing.select_set(True)
            bpy.ops.object.join()
            
        elif unit_type == "zergling":
            # Витягнутий об'єкт для зерглінга
            bpy.ops.mesh.primitive_cube_add(size=width)
            unit = bpy.context.object
            unit.scale = (1.5, 0.7, height/width)
            
        else:
            # Стандартний куб
            bpy.ops.mesh.primitive_cube_add(size=width)
            unit = bpy.context.object
            unit.scale = (1, 1, height/width)
        
        return unit
    
    def _generate_ui_with_materials(self, shot_config):
        """Генерує UI з матеріалами"""
        if not shot_config.hud:
            return
        
        # Основний HUD
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, -9.5, 0))
        hud_plane = bpy.context.object
        hud_plane.name = "SCBW_HUD"
        hud_plane.scale = (10, 1, 1)
        
        # Матеріал для HUD
        hud_material = self.material_gen.create_ui_material("hud")
        hud_plane.data.materials.append(hud_material)
        
        # Кнопки
        self._create_ui_buttons()
        
        # Панель ресурсів
        self._create_resource_panel()
    
    def _create_ui_buttons(self):
        """Створює UI кнопки"""
        button_positions = [
            (-8, -9.5, 0.1),
            (-6, -9.5, 0.1),
            (-4, -9.5, 0.1),
            (-2, -9.5, 0.1)
        ]
        
        for i, pos in enumerate(button_positions):
            bpy.ops.mesh.primitive_cube_add(size=0.3, location=pos)
            button = bpy.context.object
            button.name = f"SCBW_Button_{i}"
            button.scale = (1, 0.3, 0.1)
            
            # Матеріал для кнопки
            button_material = self.material_gen.create_ui_material("button")
            button.data.materials.append(button_material)
    
    def _create_resource_panel(self):
        """Створює панель ресурсів"""
        bpy.ops.mesh.primitive_plane_add(size=1, location=(8, -9.5, 0))
        resource_panel = bpy.context.object
        resource_panel.name = "SCBW_ResourcePanel"
        resource_panel.scale = (2, 1, 1)
        
        # Матеріал для панелі ресурсів
        panel_material = self.material_gen.create_ui_material("panel")
        resource_panel.data.materials.append(panel_material)
    
    def _generate_effects_with_materials(self, shot_config):
        """Генерує спеціальні ефекти з матеріалами"""
        if shot_config.portal:
            self._create_portal_effect(shot_config.portal)
        
        if shot_config.explosion:
            self._create_explosion_effect(shot_config.explosion)
    
    def _create_portal_effect(self, portal_config):
        """Створює ефект порталу"""
        center = portal_config.get("center", [0.5, 0.5])
        radius = portal_config.get("radius", 0.2)
        
        # Конвертація координат
        x_center = (center[0] - 0.5) * 20
        y_center = (center[1] - 0.5) * 20
        world_radius = radius * 20
        
        # Створення порталу
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=world_radius,
            location=(x_center, y_center, 0)
        )
        
        portal = bpy.context.object
        portal.name = "SCBW_Portal"
        
        # Матеріал для порталу
        portal_material = self.material_gen.create_effect_material("portal")
        portal.data.materials.append(portal_material)
        
        # Анімація порталу
        self._animate_portal(portal)
    
    def _create_explosion_effect(self, explosion_config):
        """Створює ефект вибуху"""
        center = explosion_config.get("center", [0.5, 0.5])
        radius = explosion_config.get("radius", 0.1)
        
        # Конвертація координат
        x_center = (center[0] - 0.5) * 20
        y_center = (center[1] - 0.5) * 20
        world_radius = radius * 20
        
        # Створення вибуху
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=world_radius,
            location=(x_center, y_center, 0)
        )
        
        explosion = bpy.context.object
        explosion.name = "SCBW_Explosion"
        
        # Матеріал для вибуху
        explosion_material = self.material_gen.create_effect_material("explosion")
        explosion.data.materials.append(explosion_material)
        
        # Анімація вибуху
        self._animate_explosion(explosion)
    
    def _animate_portal(self, portal):
        """Анімує портал"""
        # Обертання
        portal.rotation_euler = (0, 0, 0)
        portal.keyframe_insert(data_path="rotation_euler", frame=1)
        portal.rotation_euler = (0, 0, math.pi * 2)
        portal.keyframe_insert(data_path="rotation_euler", frame=100)
        
        # Масштабування
        portal.scale = (1, 1, 1)
        portal.keyframe_insert(data_path="scale", frame=1)
        portal.scale = (1.2, 1.2, 1.2)
        portal.keyframe_insert(data_path="scale", frame=50)
        portal.scale = (1, 1, 1)
        portal.keyframe_insert(data_path="scale", frame=100)
    
    def _animate_explosion(self, explosion):
        """Анімує вибух"""
        # Масштабування
        explosion.scale = (0.1, 0.1, 0.1)
        explosion.keyframe_insert(data_path="scale", frame=1)
        explosion.scale = (2, 2, 2)
        explosion.keyframe_insert(data_path="scale", frame=10)
        explosion.scale = (0, 0, 0)
        explosion.keyframe_insert(data_path="scale", frame=20)
    
    def create_advanced_material_setup(self, shot_config):
        """Створює розширену налаштування матеріалів"""
        # Налаштування рендерингу для матеріалів
        if self.scene.render.engine == 'CYCLES':
            cycles = self.scene.cycles
            cycles.samples = 128
            cycles.use_denoising = True
            cycles.max_bounces = 12
            cycles.diffuse_bounces = 4
            cycles.glossy_bounces = 4
        
        # Налаштування кольору
        self.scene.view_settings.view_transform = "Filmic"
        self.scene.view_settings.look = "None"
        self.scene.view_settings.exposure = 0.0
        self.scene.view_settings.gamma = 1.0
        
        # Налаштування композитора
        self.scene.use_nodes = True
        self._setup_compositor_nodes()
    
    def _setup_compositor_nodes(self):
        """Налаштовує вузли композитора"""
        tree = self.scene.node_tree
        tree.nodes.clear()
        
        # Render Layers
        render_layers = tree.nodes.new("CompositorNodeRLayers")
        render_layers.location = (0, 0)
        
        # Color Correction
        color_correction = tree.nodes.new("CompositorNodeColorBalance")
        color_correction.location = (200, 0)
        
        # Output
        output = tree.nodes.new("CompositorNodeOutputFile")
        output.location = (400, 0)
        output.base_path = "//renders/"
        
        # Connections
        tree.links.new(render_layers.outputs["Image"], color_correction.inputs["Color"])
        tree.links.new(color_correction.outputs["Color"], output.inputs["Image"])
    
    def cleanup(self):
        """Очищає ресурси"""
        self.material_gen.clear_material_cache()
        logger.info("Очищення ресурсів завершено")

# Приклад використання
if __name__ == "__main__":
    # Конфігурація шоту
    shot_config = {
        "terrain_type": "grass",
        "left_cluster": {
            "rect": [0.2, 0.5],
            "count": 5,
            "size": [16, 32],
            "unit_type": "marine"
        },
        "right_cluster": {
            "rect": [0.8, 0.5],
            "count": 5,
            "size": [16, 32],
            "unit_type": "zealot"
        },
        "hud": True,
        "portal": {
            "center": [0.5, 0.5],
            "radius": 0.2
        }
    }
    
    # Створення генератора
    config = type('Config', (), {'image_size': [1920, 1080]})()
    generator = EnhancedStarCraftSceneGenerator(config)
    
    # Генерація сцени
    generator.setup_scene(shot_config)
    generator.create_advanced_material_setup(shot_config)
    
    print("Покращена сцена з матеріалами створена!")