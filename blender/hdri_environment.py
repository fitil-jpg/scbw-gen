"""
Система HDRI середовища для Blender
Підтримує різні типи HDRI, пресети та налаштування
"""

import bpy
import os
import mathutils
from mathutils import Vector, Color
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class HDRIEnvironment:
    """Система HDRI середовища для Blender"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scene = bpy.context.scene
        self.hdri_presets = {}
        self.current_hdri = None
        
        # Завантаження пресетів
        self._load_hdri_presets()
    
    def _load_hdri_presets(self) -> None:
        """Завантажує пресети HDRI"""
        self.hdri_presets = {
            "sunset": {
                "type": "procedural",
                "sky_type": "Nishita",
                "sun_elevation": 0.2,
                "sun_rotation": 0.0,
                "sun_size": 0.02,
                "sun_intensity": 1.5,
                "strength": 1.2,
                "turbidity": 2.2,
                "ground_albedo": 0.3,
                "description": "Захід сонця з теплим освітленням"
            },
            "sunrise": {
                "type": "procedural",
                "sky_type": "Nishita",
                "sun_elevation": 0.1,
                "sun_rotation": 0.0,
                "sun_size": 0.02,
                "sun_intensity": 1.8,
                "strength": 1.5,
                "turbidity": 1.8,
                "ground_albedo": 0.2,
                "description": "Схід сонця з яскравим освітленням"
            },
            "midday": {
                "type": "procedural",
                "sky_type": "Nishita",
                "sun_elevation": 0.8,
                "sun_rotation": 0.0,
                "sun_size": 0.02,
                "sun_intensity": 1.0,
                "strength": 1.0,
                "turbidity": 2.0,
                "ground_albedo": 0.4,
                "description": "Полудень з ясним небом"
            },
            "overcast": {
                "type": "procedural",
                "sky_type": "Nishita",
                "sun_elevation": 0.3,
                "sun_rotation": 0.0,
                "sun_size": 0.1,
                "sun_intensity": 0.3,
                "strength": 0.8,
                "turbidity": 5.0,
                "ground_albedo": 0.3,
                "description": "Хмарний день з м'яким освітленням"
            },
            "night": {
                "type": "procedural",
                "sky_type": "Nishita",
                "sun_elevation": -0.5,
                "sun_rotation": 0.0,
                "sun_size": 0.02,
                "sun_intensity": 0.1,
                "strength": 0.3,
                "turbidity": 1.0,
                "ground_albedo": 0.1,
                "description": "Нічне небо з місячним освітленням"
            },
            "studio_white": {
                "type": "gradient",
                "gradient_type": "SPHERICAL",
                "colors": [(0.9, 0.9, 0.95), (0.7, 0.7, 0.8)],
                "strength": 1.0,
                "description": "Студійне біле освітлення"
            },
            "studio_warm": {
                "type": "gradient",
                "gradient_type": "SPHERICAL",
                "colors": [(1.0, 0.95, 0.8), (0.8, 0.7, 0.6)],
                "strength": 1.0,
                "description": "Студійне тепле освітлення"
            },
            "studio_cool": {
                "type": "gradient",
                "gradient_type": "SPHERICAL",
                "colors": [(0.8, 0.9, 1.0), (0.6, 0.7, 0.8)],
                "strength": 1.0,
                "description": "Студійне холодне освітлення"
            },
            "space": {
                "type": "gradient",
                "gradient_type": "SPHERICAL",
                "colors": [(0.1, 0.1, 0.2), (0.0, 0.0, 0.1)],
                "strength": 0.5,
                "description": "Космічне середовище"
            },
            "underwater": {
                "type": "gradient",
                "gradient_type": "SPHERICAL",
                "colors": [(0.2, 0.4, 0.6), (0.1, 0.2, 0.4)],
                "strength": 0.8,
                "description": "Підводне середовище"
            }
        }
    
    def setup_hdri_environment(self, hdri_config: Dict[str, Any]) -> None:
        """
        Налаштовує HDRI середовище
        
        Args:
            hdri_config: Конфігурація HDRI
        """
        try:
            # Отримання або створення світового шейдера
            world = self.scene.world
            if not world:
                world = bpy.data.worlds.new("World")
                self.scene.world = world
            
            world.use_nodes = True
            nodes = world.node_tree.nodes
            nodes.clear()
            
            # Створення основних вузлів
            background = nodes.new(type='ShaderNodeBackground')
            background.location = (0, 0)
            
            output = nodes.new(type='ShaderNodeOutputWorld')
            output.location = (300, 0)
            
            # Налаштування HDRI на основі типу
            hdri_type = hdri_config.get("type", "procedural")
            
            if hdri_type == "image":
                self._setup_image_hdri(nodes, hdri_config)
            elif hdri_type == "procedural":
                self._setup_procedural_hdri(nodes, hdri_config)
            elif hdri_type == "gradient":
                self._setup_gradient_hdri(nodes, hdri_config)
            elif hdri_type == "preset":
                preset_name = hdri_config.get("preset_name", "midday")
                preset_config = self.get_preset(preset_name)
                self._apply_preset_config(nodes, preset_config)
            else:
                logger.warning(f"Невідомий тип HDRI: {hdri_type}")
                return
            
            # Налаштування інтенсивності
            strength = hdri_config.get("strength", 1.0)
            background.inputs['Strength'].default_value = strength
            
            # З'єднання вузлів
            world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
            
            # Збереження поточної конфігурації
            self.current_hdri = hdri_config
            
            logger.info(f"HDRI середовище налаштовано: {hdri_type}")
            
        except Exception as e:
            logger.error(f"Помилка налаштування HDRI: {e}")
            raise
    
    def _setup_image_hdri(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує HDRI з зображення"""
        # Вузол координат
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        # Вузол мапінгу
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        
        # Вузол зображення
        env_tex = nodes.new(type='ShaderNodeTexEnvironment')
        env_tex.location = (-200, 0)
        
        # Завантаження зображення
        image_path = hdri_config.get("image_path", "")
        if image_path and os.path.exists(image_path):
            try:
                image = bpy.data.images.load(image_path)
                env_tex.image = image
                logger.info(f"HDRI зображення завантажено: {image_path}")
            except Exception as e:
                logger.error(f"Помилка завантаження HDRI зображення: {e}")
        else:
            logger.warning(f"HDRI зображення не знайдено: {image_path}")
        
        # Налаштування мапінгу
        rotation = hdri_config.get("rotation", [0, 0, 0])
        mapping.inputs['Rotation'].default_value = rotation
        
        scale = hdri_config.get("scale", [1, 1, 1])
        mapping.inputs['Scale'].default_value = scale
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        world.node_tree.links.new(env_tex.outputs['Color'], background.inputs['Color'])
    
    def _setup_procedural_hdri(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує процедурне HDRI"""
        # Вузол координат
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        # Вузол мапінгу
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        
        # Вузол неба
        sky_tex = nodes.new(type='ShaderNodeTexSky')
        sky_tex.location = (-200, 0)
        
        # Налаштування неба
        sky_tex.sky_type = hdri_config.get("sky_type", "Nishita")
        sky_tex.sun_elevation = hdri_config.get("sun_elevation", 0.5)
        sky_tex.sun_rotation = hdri_config.get("sun_rotation", 0.0)
        sky_tex.sun_size = hdri_config.get("sun_size", 0.02)
        sky_tex.sun_intensity = hdri_config.get("sun_intensity", 1.0)
        sky_tex.turbidity = hdri_config.get("turbidity", 2.0)
        sky_tex.ground_albedo = hdri_config.get("ground_albedo", 0.3)
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], sky_tex.inputs['Vector'])
        world.node_tree.links.new(sky_tex.outputs['Color'], background.inputs['Color'])
    
    def _setup_gradient_hdri(self, nodes, hdri_config: Dict[str, Any]) -> None:
        """Налаштовує градієнтне HDRI"""
        # Вузол координат
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        # Вузол мапінгу
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        
        # Вузол градієнту
        gradient = nodes.new(type='ShaderNodeTexGradient')
        gradient.location = (-200, 0)
        
        # Вузол кольору
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (0, 0)
        
        # Налаштування градієнту
        gradient_type = hdri_config.get("gradient_type", "SPHERICAL")
        gradient.gradient_type = gradient_type
        
        # Налаштування кольорів
        colors = hdri_config.get("colors", [(0.5, 0.7, 1.0), (1.0, 0.8, 0.6)])
        if len(colors) >= 2:
            color_ramp.color_ramp.elements[0].color = (*colors[0], 1.0)
            color_ramp.color_ramp.elements[1].color = (*colors[1], 1.0)
        
        # Додавання проміжних кольорів
        if len(colors) > 2:
            for i, color in enumerate(colors[2:], 2):
                if i < len(color_ramp.color_ramp.elements):
                    color_ramp.color_ramp.elements[i].color = (*color, 1.0)
                else:
                    # Додавання нового елемента
                    new_element = color_ramp.color_ramp.elements.new(i / (len(colors) - 1))
                    new_element.color = (*color, 1.0)
        
        # З'єднання вузлів
        world.node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        world.node_tree.links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
        world.node_tree.links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
        world.node_tree.links.new(color_ramp.outputs['Color'], background.inputs['Color'])
    
    def _apply_preset_config(self, nodes, preset_config: Dict[str, Any]) -> None:
        """Застосовує конфігурацію пресету"""
        hdri_type = preset_config.get("type", "procedural")
        
        if hdri_type == "procedural":
            self._setup_procedural_hdri(nodes, preset_config)
        elif hdri_type == "gradient":
            self._setup_gradient_hdri(nodes, preset_config)
    
    def get_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Отримує пресет за назвою
        
        Args:
            preset_name: Назва пресету
        
        Returns:
            Конфігурація пресету
        """
        return self.hdri_presets.get(preset_name, self.hdri_presets["midday"])
    
    def get_available_presets(self) -> List[str]:
        """Отримує список доступних пресетів"""
        return list(self.hdri_presets.keys())
    
    def create_custom_preset(self, name: str, config: Dict[str, Any]) -> None:
        """
        Створює користувацький пресет
        
        Args:
            name: Назва пресету
            config: Конфігурація пресету
        """
        self.hdri_presets[name] = config
        logger.info(f"Користувацький пресет створено: {name}")
    
    def animate_hdri(self, animation_config: Dict[str, Any]) -> None:
        """
        Анімує HDRI середовище
        
        Args:
            animation_config: Конфігурація анімації
        """
        try:
            world = self.scene.world
            if not world or not world.use_nodes:
                return
            
            nodes = world.node_tree.nodes
            
            # Анімація сонця (для процедурного HDRI)
            sky_tex = nodes.get("Sky Texture")
            if sky_tex and sky_tex.type == 'TEX_SKY':
                if "sun_elevation" in animation_config:
                    elevation_config = animation_config["sun_elevation"]
                    start_elevation = elevation_config.get("start", sky_tex.sun_elevation)
                    end_elevation = elevation_config.get("end", start_elevation)
                    frames = elevation_config.get("frames", [1, 100])
                    
                    # Ключові кадри
                    sky_tex.sun_elevation = start_elevation
                    sky_tex.keyframe_insert(data_path="sun_elevation", frame=frames[0])
                    
                    sky_tex.sun_elevation = end_elevation
                    sky_tex.keyframe_insert(data_path="sun_elevation", frame=frames[1])
                
                if "sun_rotation" in animation_config:
                    rotation_config = animation_config["sun_rotation"]
                    start_rotation = rotation_config.get("start", sky_tex.sun_rotation)
                    end_rotation = rotation_config.get("end", start_rotation)
                    frames = rotation_config.get("frames", [1, 100])
                    
                    # Ключові кадри
                    sky_tex.sun_rotation = start_rotation
                    sky_tex.keyframe_insert(data_path="sun_rotation", frame=frames[0])
                    
                    sky_tex.sun_rotation = end_rotation
                    sky_tex.keyframe_insert(data_path="sun_rotation", frame=frames[1])
            
            # Анімація інтенсивності
            background = nodes.get("Background")
            if background and "strength" in animation_config:
                strength_config = animation_config["strength"]
                start_strength = strength_config.get("start", background.inputs['Strength'].default_value)
                end_strength = strength_config.get("end", start_strength)
                frames = strength_config.get("frames", [1, 100])
                
                # Ключові кадри
                background.inputs['Strength'].default_value = start_strength
                background.inputs['Strength'].keyframe_insert(data_path="default_value", frame=frames[0])
                
                background.inputs['Strength'].default_value = end_strength
                background.inputs['Strength'].keyframe_insert(data_path="default_value", frame=frames[1])
            
            logger.info("HDRI анімація налаштована")
            
        except Exception as e:
            logger.error(f"Помилка анімації HDRI: {e}")
            raise
    
    def add_volumetric_effects(self, effects_config: Dict[str, Any]) -> None:
        """
        Додає об'ємні ефекти до HDRI
        
        Args:
            effects_config: Конфігурація ефектів
        """
        try:
            world = self.scene.world
            if not world or not world.use_nodes:
                return
            
            nodes = world.node_tree.nodes
            output = nodes.get("World Output")
            if not output:
                return
            
            # Туман
            if effects_config.get("fog", False):
                fog_config = effects_config["fog"]
                
                volume_scatter = nodes.new(type='ShaderNodeVolumeScatter')
                volume_scatter.location = (0, -200)
                
                # Налаштування туману
                volume_scatter.inputs['Density'].default_value = fog_config.get("density", 0.1)
                volume_scatter.inputs['Anisotropy'].default_value = fog_config.get("anisotropy", 0.0)
                
                # З'єднання
                world.node_tree.links.new(volume_scatter.outputs['Volume'], output.inputs['Volume'])
            
            # Об'ємне поглинання
            if effects_config.get("volume_absorption", False):
                absorption_config = effects_config["volume_absorption"]
                
                volume_absorption = nodes.new(type='ShaderNodeVolumeAbsorption')
                volume_absorption.location = (0, -400)
                
                # Налаштування поглинання
                volume_absorption.inputs['Density'].default_value = absorption_config.get("density", 0.1)
                
                # З'єднання
                world.node_tree.links.new(volume_absorption.outputs['Volume'], output.inputs['Volume'])
            
            logger.info("Об'ємні ефекти додано до HDRI")
            
        except Exception as e:
            logger.error(f"Помилка додавання об'ємних ефектів: {e}")
            raise
    
    def export_hdri_config(self, filepath: str) -> None:
        """
        Експортує поточну конфігурацію HDRI
        
        Args:
            filepath: Шлях до файлу
        """
        try:
            config = {
                "current_hdri": self.current_hdri,
                "presets": self.hdri_presets
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Конфігурація HDRI експортована: {filepath}")
            
        except Exception as e:
            logger.error(f"Помилка експорту HDRI: {e}")
            raise
    
    def import_hdri_config(self, filepath: str) -> None:
        """
        Імпортує конфігурацію HDRI
        
        Args:
            filepath: Шлях до файлу
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Завантаження пресетів
            if "presets" in config:
                self.hdri_presets.update(config["presets"])
            
            # Застосування поточної конфігурації
            if "current_hdri" in config and config["current_hdri"]:
                self.setup_hdri_environment(config["current_hdri"])
            
            logger.info(f"Конфігурація HDRI імпортована: {filepath}")
            
        except Exception as e:
            logger.error(f"Помилка імпорту HDRI: {e}")
            raise


# Приклад використання
if __name__ == "__main__":
    # Базова конфігурація
    config = {
        "output_dir": "renders/blender"
    }
    
    # Ініціалізація системи HDRI
    hdri_system = HDRIEnvironment(config)
    
    # Використання пресету
    hdri_config = {
        "type": "preset",
        "preset_name": "sunset"
    }
    
    # Налаштування HDRI
    hdri_system.setup_hdri_environment(hdri_config)
    print("HDRI середовище налаштовано!")
    
    # Додавання об'ємних ефектів
    effects_config = {
        "fog": {
            "density": 0.05,
            "anisotropy": 0.0
        }
    }
    
    hdri_system.add_volumetric_effects(effects_config)
    print("Об'ємні ефекти додано!")