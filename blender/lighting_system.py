"""
Розширена система освітлення для Blender
Підтримує кілька лайтів, HDRI та різні типи освітлення
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector, Color, Euler
from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class LightingSystem:
    """Розширена система освітлення для Blender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scene = bpy.context.scene
        self.lights = {}
        self.hdri_environments = {}
        
    def setup_lighting(self, lighting_config: Dict[str, Any]) -> None:
        """
        Налаштовує систему освітлення на основі конфігурації
        
        Args:
            lighting_config: Конфігурація освітлення
        """
        try:
            # Очищення існуючих лайтів
            self.clear_lights()
            
            # Налаштування HDRI середовища
            if "hdri" in lighting_config:
                self.setup_hdri_environment(lighting_config["hdri"])
            
            # Налаштування основних лайтів
            if "main_lights" in lighting_config:
                self.setup_main_lights(lighting_config["main_lights"])
            
            # Налаштування додаткових лайтів
            if "additional_lights" in lighting_config:
                self.setup_additional_lights(lighting_config["additional_lights"])
            
            # Налаштування атмосферного освітлення
            if "atmospheric" in lighting_config:
                self.setup_atmospheric_lighting(lighting_config["atmospheric"])
            
            logger.info("Система освітлення налаштована успішно")
            
        except Exception as e:
            logger.error(f"Помилка налаштування освітлення: {e}")
            raise
    
    def clear_lights(self) -> None:
        """Очищає всі лайти зі сцени"""
        for obj in self.scene.objects:
            if obj.type == 'LIGHT':
                bpy.data.objects.remove(obj, do_unlink=True)
        self.lights.clear()
    
    def setup_hdri_environment(self, hdri_config: Dict[str, Any]) -> None:
        """
        Налаштовує HDRI середовище
        
        Args:
            hdri_config: Конфігурація HDRI
        """
        try:
            # Отримання світового шейдера
            world = self.scene.world
            if not world:
                world = bpy.data.worlds.new("World")
                self.scene.world = world
            
            world.use_nodes = True
            nodes = world.node_tree.nodes
            nodes.clear()
            
            # Створення вузлів для HDRI
            background = nodes.new(type='ShaderNodeBackground')
            background.location = (0, 0)
            
            output = nodes.new(type='ShaderNodeOutputWorld')
            output.location = (300, 0)
            
            # Налаштування HDRI
            hdri_type = hdri_config.get("type", "procedural")
            
            if hdri_type == "image" and "image_path" in hdri_config:
                # Завантаження HDRI зображення
                self._setup_hdri_image(nodes, hdri_config)
            elif hdri_type == "procedural":
                # Процедурне HDRI
                self._setup_procedural_hdri(nodes, hdri_config)
            elif hdri_type == "gradient":
                # Градієнтне HDRI
                self._setup_gradient_hdri(nodes, hdri_config)
            
            # Налаштування інтенсивності
            strength = hdri_config.get("strength", 1.0)
            background.inputs['Strength'].default_value = strength
            
            # З'єднання вузлів
            world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
            
            logger.info(f"HDRI середовище налаштовано: {hdri_type}")
            
        except Exception as e:
            logger.error(f"Помилка налаштування HDRI: {e}")
            raise
    
    def _setup_hdri_image(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує HDRI з зображення"""
        # Вузол зображення
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-400, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-200, 0)
        
        env_tex = nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (0, 0)
        
        # Завантаження зображення
        image_path = hdri_config["image_path"]
        if os.path.exists(image_path):
            image = bpy.data.images.load(image_path)
            env_tex.image = image
        
        # Налаштування мапінгу
        mapping.inputs['Rotation'].default_value = hdri_config.get("rotation", (0, 0, 0))
        mapping.inputs['Scale'].default_value = hdri_config.get("scale", (1, 1, 1))
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        world.node_tree.links.new(env_tex.outputs['Color'], background.inputs['Color'])
    
    def _setup_procedural_hdri(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує процедурне HDRI"""
        # Вузол координат
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-400, 0)
        
        # Вузол мапінгу
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-200, 0)
        
        # Вузол неба
        sky_tex = nodes.new(type='ShaderNodeTexSky')
        sky_tex.location = (0, 0)
        
        # Налаштування неба
        sky_tex.sky_type = hdri_config.get("sky_type", "Nishita")
        sky_tex.sun_elevation = hdri_config.get("sun_elevation", 0.5)
        sky_tex.sun_rotation = hdri_config.get("sun_rotation", 0.0)
        sky_tex.sun_size = hdri_config.get("sun_size", 0.02)
        sky_tex.sun_intensity = hdri_config.get("sun_intensity", 1.0)
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], sky_tex.inputs['Vector'])
        world.node_tree.links.new(sky_tex.outputs['Color'], background.inputs['Color'])
    
    def _setup_gradient_hdri(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує градієнтне HDRI"""
        # Вузол координат
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-400, 0)
        
        # Вузол мапінгу
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-200, 0)
        
        # Вузол градієнту
        gradient = nodes.new(type='ShaderNodeTexGradient')
        gradient.location = (0, 0)
        
        # Вузол кольору
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (200, 0)
        
        # Налаштування градієнту
        gradient_type = hdri_config.get("gradient_type", "SPHERICAL")
        gradient.gradient_type = gradient_type
        
        # Налаштування кольорів
        colors = hdri_config.get("colors", [(0.5, 0.7, 1.0), (1.0, 0.8, 0.6)])
        if len(colors) >= 2:
            color_ramp.color_ramp.elements[0].color = (*colors[0], 1.0)
            color_ramp.color_ramp.elements[1].color = (*colors[1], 1.0)
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
        world.node_tree.links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
        world.node_tree.links.new(color_ramp.outputs['Color'], background.inputs['Color'])
    
    def setup_main_lights(self, main_lights_config: List[Dict[str, Any]]) -> None:
        """
        Налаштовує основні лайти
        
        Args:
            main_lights_config: Список конфігурацій основних лайтів
        """
        for i, light_config in enumerate(main_lights_config):
            try:
                light_type = light_config.get("type", "SUN")
                name = light_config.get("name", f"Main_Light_{i}")
                
                # Створення лайта
                light_obj = self._create_light(light_type, name, light_config)
                self.lights[name] = light_obj
                
                logger.info(f"Основний лайт створено: {name} ({light_type})")
                
            except Exception as e:
                logger.error(f"Помилка створення основного лайта {i}: {e}")
                continue
    
    def setup_additional_lights(self, additional_lights_config: List[Dict[str, Any]]) -> None:
        """
        Налаштовує додаткові лайти
        
        Args:
            additional_lights_config: Список конфігурацій додаткових лайтів
        """
        for i, light_config in enumerate(additional_lights_config):
            try:
                light_type = light_config.get("type", "AREA")
                name = light_config.get("name", f"Additional_Light_{i}")
                
                # Створення лайта
                light_obj = self._create_light(light_type, name, light_config)
                self.lights[name] = light_obj
                
                logger.info(f"Додатковий лайт створено: {name} ({light_type})")
                
            except Exception as e:
                logger.error(f"Помилка створення додаткового лайта {i}: {e}")
                continue
    
    def _create_light(self, light_type: str, name: str, config: Dict[str, Any]) -> bpy.types.Object:
        """
        Створює лайт з заданими параметрами
        
        Args:
            light_type: Тип лайта
            name: Назва лайта
            config: Конфігурація лайта
        
        Returns:
            Об'єкт лайта
        """
        # Позиція
        position = config.get("position", [0, 0, 5])
        location = Vector(position)
        
        # Створення лайта
        bpy.ops.object.light_add(type=light_type, location=location)
        light_obj = bpy.context.object
        light_obj.name = name
        
        # Налаштування лайта
        light_data = light_obj.data
        
        # Енергія
        energy = config.get("energy", 1.0)
        light_data.energy = energy
        
        # Колір
        color = config.get("color", [1.0, 1.0, 1.0])
        light_data.color = Color(color)
        
        # Специфічні налаштування для різних типів лайтів
        if light_type == "SUN":
            # Напрямок сонця
            direction = config.get("direction", [0.5, 0.5, -1.0])
            light_obj.rotation_euler = Euler(direction, 'XYZ')
            light_data.angle = config.get("angle", 0.5)
        
        elif light_type == "AREA":
            # Розмір площі
            size = config.get("size", 1.0)
            light_data.size = size
            light_data.shape = config.get("shape", "SQUARE")
        
        elif light_type == "SPOT":
            # Напрямок спота
            direction = config.get("direction", [0, 0, -1])
            light_obj.rotation_euler = Euler(direction, 'XYZ')
            light_data.spot_size = config.get("spot_size", 1.0)
            light_data.spot_blend = config.get("spot_blend", 0.15)
        
        elif light_type == "POINT":
            # Точковий лайт
            light_data.shadow_soft_size = config.get("shadow_soft_size", 0.25)
        
        # Налаштування тіней
        if "shadow" in config:
            shadow_config = config["shadow"]
            light_data.use_shadow = shadow_config.get("enabled", True)
            light_data.shadow_soft_size = shadow_config.get("soft_size", 0.25)
            light_data.contact_shadow_distance = shadow_config.get("contact_distance", 0.0)
        
        return light_obj
    
    def setup_atmospheric_lighting(self, atmospheric_config: Dict[str, Any]) -> None:
        """
        Налаштовує атмосферне освітлення
        
        Args:
            atmospheric_config: Конфігурація атмосферного освітлення
        """
        try:
            # Налаштування туману
            if "fog" in atmospheric_config:
                self._setup_fog(atmospheric_config["fog"])
            
            # Налаштування атмосферної перспективи
            if "atmospheric_perspective" in atmospheric_config:
                self._setup_atmospheric_perspective(atmospheric_config["atmospheric_perspective"])
            
            logger.info("Атмосферне освітлення налаштовано")
            
        except Exception as e:
            logger.error(f"Помилка налаштування атмосферного освітлення: {e}")
            raise
    
    def _setup_fog(self, fog_config: Dict[str, Any]) -> None:
        """Налаштовує туман"""
        # Включення туману в Cycles
        if self.scene.render.engine == 'CYCLES':
            world = self.scene.world
            if world and world.use_nodes:
                nodes = world.node_tree.nodes
                
                # Вузол туману
                volume_scatter = nodes.new(type='ShaderNodeVolumeScatter')
                volume_scatter.location = (0, -200)
                
                # Вузол виводу
                output = nodes.get('World Output')
                if output:
                    world.node_tree.links.new(volume_scatter.outputs['Volume'], output.inputs['Volume'])
    
    def _setup_atmospheric_perspective(self, perspective_config: Dict[str, Any]) -> None:
        """Налаштовує атмосферну перспективу"""
        # Налаштування кольору далеких об'єктів
        pass  # Можна додати логіку для налаштування атмосферної перспективи
    
    def get_light_by_name(self, name: str) -> Optional[bpy.types.Object]:
        """Отримує лайт за назвою"""
        return self.lights.get(name)
    
    def update_light(self, name: str, config: Dict[str, Any]) -> None:
        """
        Оновлює параметри лайта
        
        Args:
            name: Назва лайта
            config: Нова конфігурація
        """
        light_obj = self.get_light_by_name(name)
        if light_obj:
            self._create_light(light_obj.data.type, name, config)
    
    def animate_light(self, name: str, animation_config: Dict[str, Any]) -> None:
        """
        Анімує лайт
        
        Args:
            name: Назва лайта
            animation_config: Конфігурація анімації
        """
        light_obj = self.get_light_by_name(name)
        if not light_obj:
            return
        
        # Анімація позиції
        if "position" in animation_config:
            pos_config = animation_config["position"]
            start_pos = pos_config.get("start", light_obj.location)
            end_pos = pos_config.get("end", start_pos)
            frames = pos_config.get("frames", [1, 100])
            
            # Ключові кадри
            light_obj.location = start_pos
            light_obj.keyframe_insert(data_path="location", frame=frames[0])
            
            light_obj.location = end_pos
            light_obj.keyframe_insert(data_path="location", frame=frames[1])
        
        # Анімація енергії
        if "energy" in animation_config:
            energy_config = animation_config["energy"]
            start_energy = energy_config.get("start", light_obj.data.energy)
            end_energy = energy_config.get("end", start_energy)
            frames = energy_config.get("frames", [1, 100])
            
            # Ключові кадри
            light_obj.data.energy = start_energy
            light_obj.data.keyframe_insert(data_path="energy", frame=frames[0])
            
            light_obj.data.energy = end_energy
            light_obj.data.keyframe_insert(data_path="energy", frame=frames[1])
    
    def create_lighting_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Створює пресет освітлення
        
        Args:
            preset_name: Назва пресету
        
        Returns:
            Конфігурація пресету
        """
        presets = {
            "sunset": {
                "hdri": {
                    "type": "procedural",
                    "sky_type": "Nishita",
                    "sun_elevation": 0.2,
                    "sun_rotation": 0.0,
                    "strength": 1.5
                },
                "main_lights": [
                    {
                        "type": "SUN",
                        "name": "Sunset_Sun",
                        "position": [5, 5, 10],
                        "energy": 3.0,
                        "color": [1.0, 0.6, 0.3],
                        "direction": [0.3, 0.3, -0.9]
                    }
                ],
                "additional_lights": [
                    {
                        "type": "AREA",
                        "name": "Warm_Fill",
                        "position": [-3, -3, 8],
                        "energy": 1.0,
                        "color": [1.0, 0.8, 0.6],
                        "size": 5.0
                    }
                ]
            },
            "night": {
                "hdri": {
                    "type": "procedural",
                    "sky_type": "Nishita",
                    "sun_elevation": -0.5,
                    "sun_rotation": 0.0,
                    "strength": 0.3
                },
                "main_lights": [
                    {
                        "type": "AREA",
                        "name": "Moon_Light",
                        "position": [0, 0, 15],
                        "energy": 2.0,
                        "color": [0.7, 0.8, 1.0],
                        "size": 10.0
                    }
                ],
                "additional_lights": [
                    {
                        "type": "POINT",
                        "name": "Ambient_Light",
                        "position": [0, 0, 5],
                        "energy": 0.5,
                        "color": [0.5, 0.6, 0.8]
                    }
                ]
            },
            "studio": {
                "hdri": {
                    "type": "gradient",
                    "gradient_type": "SPHERICAL",
                    "colors": [(0.8, 0.8, 0.9), (0.2, 0.2, 0.3)],
                    "strength": 1.0
                },
                "main_lights": [
                    {
                        "type": "AREA",
                        "name": "Key_Light",
                        "position": [5, -5, 8],
                        "energy": 5.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 3.0
                    }
                ],
                "additional_lights": [
                    {
                        "type": "AREA",
                        "name": "Fill_Light",
                        "position": [-3, -3, 6],
                        "energy": 2.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 5.0
                    },
                    {
                        "type": "AREA",
                        "name": "Rim_Light",
                        "position": [0, 5, 4],
                        "energy": 3.0,
                        "color": [1.0, 1.0, 1.0],
                        "size": 2.0
                    }
                ]
            }
        }
        
        return presets.get(preset_name, presets["studio"])
    
    def export_lighting_config(self, filepath: str) -> None:
        """
        Експортує поточну конфігурацію освітлення
        
        Args:
            filepath: Шлях до файлу
        """
        import yaml
        
        config = {
            "lights": {},
            "hdri": {}
        }
        
        # Експорт лайтів
        for name, light_obj in self.lights.items():
            light_data = light_obj.data
            config["lights"][name] = {
                "type": light_data.type,
                "position": list(light_obj.location),
                "rotation": list(light_obj.rotation_euler),
                "energy": light_data.energy,
                "color": list(light_data.color)
            }
        
        # Експорт HDRI
        world = self.scene.world
        if world and world.use_nodes:
            config["hdri"] = {
                "strength": world.node_tree.nodes.get("Background").inputs["Strength"].default_value
            }
        
        # Збереження
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Конфігурація освітлення експортована: {filepath}")


# Приклад використання
if __name__ == "__main__":
    # Базова конфігурація
    config = {
        "output_dir": "renders/blender"
    }
    
    # Ініціалізація системи освітлення
    lighting_system = LightingSystem(config)
    
    # Конфігурація освітлення
    lighting_config = {
        "hdri": {
            "type": "procedural",
            "sky_type": "Nishita",
            "sun_elevation": 0.5,
            "strength": 1.0
        },
        "main_lights": [
            {
                "type": "SUN",
                "name": "Main_Sun",
                "position": [5, 5, 10],
                "energy": 3.0,
                "color": [1.0, 0.9, 0.7]
            }
        ],
        "additional_lights": [
            {
                "type": "AREA",
                "name": "Fill_Light",
                "position": [-3, -3, 8],
                "energy": 1.0,
                "color": [0.8, 0.9, 1.0],
                "size": 5.0
            }
        ]
    }
    
    # Налаштування освітлення
    lighting_system.setup_lighting(lighting_config)
    print("Система освітлення налаштована!")