"""
Покращений генератор геометрії для Blender
Створює геометрію на основі параметрів шотів з підтримкою анімації
"""

import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Matrix
from typing import Dict, Any, List, Optional, Tuple
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGeometryGenerator:
    """Покращений генератор геометрії для Blender"""
    
    def __init__(self):
        self.created_objects = []
        self.material_cache = {}
        self.animation_cache = {}
    
    def clear_scene(self) -> None:
        """Очищає сцену від всіх об'єктів"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        self.created_objects.clear()
        logger.info("Сцена очищена")
    
    def create_building(self, building_config: Dict[str, Any]) -> bpy.types.Object:
        """
        Створює будівлю на основі конфігурації
        
        Args:
            building_config: Конфігурація будівлі
        
        Returns:
            Створений об'єкт будівлі
        """
        try:
            name = building_config.get("name", "Building")
            building_type = building_config.get("type", "cube")
            position = building_config.get("position", [0, 0, 0])
            scale = building_config.get("scale", [1, 1, 1])
            rotation = building_config.get("rotation", [0, 0, 0])
            
            # Створення базової геометрії
            if building_type == "cube":
                obj = self._create_cube_building(name, scale)
            elif building_type == "cylinder":
                obj = self._create_cylinder_building(name, scale)
            elif building_type == "pyramid":
                obj = self._create_pyramid_building(name, scale)
            else:
                obj = self._create_cube_building(name, scale)
            
            # Позиціонування
            obj.location = Vector(position)
            obj.rotation_euler = [math.radians(r) for r in rotation]
            
            # Застосування матеріалів
            if "materials" in building_config:
                self._apply_materials(obj, building_config["materials"])
            
            # Додавання анімації
            if "animations" in building_config:
                self._add_animations(obj, building_config["animations"])
            
            self.created_objects.append(obj)
            logger.info(f"Будівлю створено: {name}")
            return obj
            
        except Exception as e:
            logger.error(f"Помилка створення будівлі {name}: {e}")
            raise
    
    def _create_cube_building(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює кубічну будівлю"""
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def _create_cylinder_building(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює циліндричну будівлю"""
        bpy.ops.mesh.primitive_cylinder_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def _create_pyramid_building(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює пірамідальну будівлю"""
        bpy.ops.mesh.primitive_cone_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def create_unit(self, unit_config: Dict[str, Any]) -> bpy.types.Object:
        """
        Створює юніт на основі конфігурації
        
        Args:
            unit_config: Конфігурація юніта
        
        Returns:
            Створений об'єкт юніта
        """
        try:
            name = unit_config.get("name", "Unit")
            unit_type = unit_config.get("type", "soldier")
            position = unit_config.get("position", [0, 0, 0])
            scale = unit_config.get("scale", [1, 1, 1])
            rotation = unit_config.get("rotation", [0, 0, 0])
            
            # Створення базової геометрії
            if unit_type == "soldier":
                obj = self._create_soldier_unit(name, scale)
            elif unit_type == "vehicle":
                obj = self._create_vehicle_unit(name, scale)
            elif unit_type == "aircraft":
                obj = self._create_aircraft_unit(name, scale)
            else:
                obj = self._create_soldier_unit(name, scale)
            
            # Позиціонування
            obj.location = Vector(position)
            obj.rotation_euler = [math.radians(r) for r in rotation]
            
            # Застосування матеріалів
            if "materials" in unit_config:
                self._apply_materials(obj, unit_config["materials"])
            
            # Додавання анімації
            if "animations" in unit_config:
                self._add_animations(obj, unit_config["animations"])
            
            self.created_objects.append(obj)
            logger.info(f"Юніт створено: {name}")
            return obj
            
        except Exception as e:
            logger.error(f"Помилка створення юніта {name}: {e}")
            raise
    
    def _create_soldier_unit(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює солдата"""
        # Тіло
        bpy.ops.mesh.primitive_cube_add()
        body = bpy.context.active_object
        body.name = f"{name}_body"
        body.scale = Vector([0.3, 0.2, 0.8]) * Vector(scale)
        
        # Голова
        bpy.ops.mesh.primitive_uv_sphere_add()
        head = bpy.context.active_object
        head.name = f"{name}_head"
        head.location = Vector([0, 0, 0.6]) * Vector(scale)
        head.scale = Vector([0.2, 0.2, 0.2]) * Vector(scale)
        
        # Об'єднання в один об'єкт
        bpy.context.view_layer.objects.active = body
        head.select_set(True)
        bpy.ops.object.join()
        
        body.name = name
        return body
    
    def _create_vehicle_unit(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює транспортний засіб"""
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector([1.5, 0.8, 0.6]) * Vector(scale)
        return obj
    
    def _create_aircraft_unit(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює літак"""
        bpy.ops.mesh.primitive_cone_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector([0.5, 2.0, 0.3]) * Vector(scale)
        return obj
    
    def create_terrain(self, terrain_config: Dict[str, Any]) -> bpy.types.Object:
        """
        Створює рельєф на основі конфігурації
        
        Args:
            terrain_config: Конфігурація рельєфу
        
        Returns:
            Створений об'єкт рельєфу
        """
        try:
            terrain_type = terrain_config.get("type", "plane")
            size = terrain_config.get("size", [20, 20])
            
            if terrain_type == "plane":
                obj = self._create_plane_terrain(size)
            elif terrain_type == "heightmap":
                obj = self._create_heightmap_terrain(terrain_config)
            else:
                obj = self._create_plane_terrain(size)
            
            # Застосування матеріалів
            if "materials" in terrain_config:
                self._apply_materials(obj, terrain_config["materials"])
            
            self.created_objects.append(obj)
            logger.info(f"Рельєф створено: {terrain_type}")
            return obj
            
        except Exception as e:
            logger.error(f"Помилка створення рельєфу: {e}")
            raise
    
    def _create_plane_terrain(self, size: List[float]) -> bpy.types.Object:
        """Створює плоский рельєф"""
        bpy.ops.mesh.primitive_plane_add()
        obj = bpy.context.active_object
        obj.name = "Terrain"
        obj.scale = Vector([size[0]/2, size[1]/2, 1])
        return obj
    
    def _create_heightmap_terrain(self, terrain_config: Dict[str, Any]) -> bpy.types.Object:
        """Створює рельєф на основі висотної карти"""
        # Поки що створюємо простий плоский рельєф
        # Тут можна додати логіку для завантаження heightmap
        return self._create_plane_terrain([20, 20])
    
    def create_effect(self, effect_config: Dict[str, Any]) -> bpy.types.Object:
        """
        Створює ефект на основі конфігурації
        
        Args:
            effect_config: Конфігурація ефекту
        
        Returns:
            Створений об'єкт ефекту
        """
        try:
            name = effect_config.get("name", "Effect")
            effect_type = effect_config.get("type", "explosion")
            position = effect_config.get("position", [0, 0, 0])
            scale = effect_config.get("scale", [1, 1, 1])
            
            # Створення базової геометрії
            if effect_type == "explosion":
                obj = self._create_explosion_effect(name, scale)
            elif effect_type == "smoke":
                obj = self._create_smoke_effect(name, scale)
            elif effect_type == "fire":
                obj = self._create_fire_effect(name, scale)
            else:
                obj = self._create_explosion_effect(name, scale)
            
            # Позиціонування
            obj.location = Vector(position)
            
            # Додавання анімації
            if "animations" in effect_config:
                self._add_animations(obj, effect_config["animations"])
            
            self.created_objects.append(obj)
            logger.info(f"Ефект створено: {name}")
            return obj
            
        except Exception as e:
            logger.error(f"Помилка створення ефекту {name}: {e}")
            raise
    
    def _create_explosion_effect(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює ефект вибуху"""
        bpy.ops.mesh.primitive_uv_sphere_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def _create_smoke_effect(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює ефект диму"""
        bpy.ops.mesh.primitive_cone_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def _create_fire_effect(self, name: str, scale: List[float]) -> bpy.types.Object:
        """Створює ефект вогню"""
        bpy.ops.mesh.primitive_cone_add()
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = Vector(scale)
        return obj
    
    def _apply_materials(self, obj: bpy.types.Object, materials_config: List[Dict[str, Any]]) -> None:
        """Застосовує матеріали до об'єкта"""
        try:
            for i, material_config in enumerate(materials_config):
                material_name = material_config.get("name", f"Material_{i}")
                color = material_config.get("color", [1, 1, 1])
                metallic = material_config.get("metallic", 0.0)
                roughness = material_config.get("roughness", 0.5)
                
                # Створення або отримання матеріалу
                if material_name in self.material_cache:
                    material = self.material_cache[material_name]
                else:
                    material = bpy.data.materials.new(name=material_name)
                    material.use_nodes = True
                    self.material_cache[material_name] = material
                
                # Налаштування матеріалу
                if material.use_nodes:
                    bsdf = material.node_tree.nodes.get("Principled BSDF")
                    if bsdf:
                        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
                        bsdf.inputs["Metallic"].default_value = metallic
                        bsdf.inputs["Roughness"].default_value = roughness
                
                # Призначення матеріалу
                if obj.data.materials:
                    obj.data.materials[i] = material
                else:
                    obj.data.materials.append(material)
                
        except Exception as e:
            logger.error(f"Помилка застосування матеріалів: {e}")
    
    def _add_animations(self, obj: bpy.types.Object, animations_config: List[Dict[str, Any]]) -> None:
        """Додає анімацію до об'єкта"""
        try:
            for animation in animations_config:
                animation_type = animation.get("type", "rotation")
                duration = animation.get("duration", 1.0)
                keyframes = animation.get("keyframes", [])
                
                if animation_type == "rotation":
                    self._add_rotation_animation(obj, keyframes, duration)
                elif animation_type == "position":
                    self._add_position_animation(obj, keyframes, duration)
                elif animation_type == "scale":
                    self._add_scale_animation(obj, keyframes, duration)
                
        except Exception as e:
            logger.error(f"Помилка додавання анімації: {e}")
    
    def _add_rotation_animation(self, obj: bpy.types.Object, keyframes: List[Dict], duration: float) -> None:
        """Додає анімацію обертання"""
        obj.animation_data_create()
        action = bpy.data.actions.new(f"{obj.name}_rotation")
        obj.animation_data.action = action
        
        for keyframe in keyframes:
            frame = int(keyframe.get("frame", 0) * duration)
            rotation = keyframe.get("rotation", [0, 0, 0])
            
            obj.rotation_euler = [math.radians(r) for r in rotation]
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    def _add_position_animation(self, obj: bpy.types.Object, keyframes: List[Dict], duration: float) -> None:
        """Додає анімацію позиції"""
        obj.animation_data_create()
        action = bpy.data.actions.new(f"{obj.name}_position")
        obj.animation_data.action = action
        
        for keyframe in keyframes:
            frame = int(keyframe.get("frame", 0) * duration)
            position = keyframe.get("position", [0, 0, 0])
            
            obj.location = Vector(position)
            obj.keyframe_insert(data_path="location", frame=frame)
    
    def _add_scale_animation(self, obj: bpy.types.Object, keyframes: List[Dict], duration: float) -> None:
        """Додає анімацію масштабу"""
        obj.animation_data_create()
        action = bpy.data.actions.new(f"{obj.name}_scale")
        obj.animation_data.action = action
        
        for keyframe in keyframes:
            frame = int(keyframe.get("frame", 0) * duration)
            scale = keyframe.get("scale", [1, 1, 1])
            
            obj.scale = Vector(scale)
            obj.keyframe_insert(data_path="scale", frame=frame)
    
    def setup_camera(self, camera_config: Dict[str, Any]) -> bpy.types.Object:
        """Налаштовує камеру"""
        try:
            position = camera_config.get("position", [0, -10, 5])
            rotation = camera_config.get("rotation", [60, 0, 0])
            focal_length = camera_config.get("focal_length", 50)
            sensor_size = camera_config.get("sensor_size", 36)
            
            # Створення камери
            bpy.ops.object.camera_add()
            camera = bpy.context.active_object
            camera.name = "Camera"
            
            # Позиціонування
            camera.location = Vector(position)
            camera.rotation_euler = [math.radians(r) for r in rotation]
            
            # Налаштування камери
            camera.data.lens = focal_length
            camera.data.sensor_width = sensor_size
            
            # Встановлення як активна камера
            bpy.context.scene.camera = camera
            
            logger.info("Камера налаштована")
            return camera
            
        except Exception as e:
            logger.error(f"Помилка налаштування камери: {e}")
            raise
    
    def setup_lighting(self, lighting_config: Dict[str, Any]) -> None:
        """Налаштовує освітлення: кілька лайтів і world HDRI.

        Підтримує:
        - lighting.preset: "three_point" для швидкого сетапу кей/філ/рім
        - lighting.lights: список лайтів із типами SUN/AREA/POINT/SPOT
        - lighting.world_hdri: { path, strength, rotation }
        - lighting.world_background: { color, strength } як fallback

        Сумісність назад: підтримуються "sun_light" і "ambient_light".
        """
        try:
            scene = bpy.context.scene

            # Опційно почистити існуючі джерела світла (за замовчуванням True)
            if lighting_config.get("clear_lights", True):
                for obj in list(scene.objects):
                    if obj.type == 'LIGHT':
                        bpy.data.objects.remove(obj, do_unlink=True)

            # Налаштування World та HDRI/бекграунду
            self._setup_world_environment(lighting_config)

            # Обробка пресетів освітлення
            preset = lighting_config.get("preset")
            if preset == "three_point":
                self._create_three_point_lighting(lighting_config.get("preset_settings", {}))

            # Явний список лайтів
            for light_cfg in lighting_config.get("lights", []):
                self._create_light_from_config(light_cfg)

            # Сумісність назад з наявними ключами
            if "sun_light" in lighting_config:
                sun_cfg = lighting_config["sun_light"]
                self._create_light_from_config({
                    "type": "SUN",
                    "name": sun_cfg.get("name", "Sun"),
                    "position": sun_cfg.get("position", [10, 10, 10]),
                    "energy": sun_cfg.get("energy", 3.0),
                    "color": sun_cfg.get("color", [1.0, 0.95, 0.8])
                })

            if "ambient_light" in lighting_config:
                amb_cfg = lighting_config["ambient_light"]
                self._create_light_from_config({
                    "type": "AREA",
                    "name": amb_cfg.get("name", "Ambient"),
                    "position": amb_cfg.get("position", [0, 0, 5]),
                    "energy": amb_cfg.get("energy", 0.3),
                    "color": amb_cfg.get("color", [0.5, 0.7, 1.0]),
                    "size": amb_cfg.get("size", 10.0)
                })

            logger.info("Освітлення налаштовано")

        except Exception as e:
            logger.error(f"Помилка налаштування освітлення: {e}")
            raise

    def _setup_world_environment(self, lighting_config: Dict[str, Any]) -> None:
        """Створює вузли World для HDRI або бекграунду."""
        scene = bpy.context.scene
        world = scene.world or bpy.data.worlds.new("World")
        scene.world = world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Почистити існуючі вузли, щоб уникнути дублювання
        nodes.clear()

        # Спроба налаштувати HDRI
        hdri_cfg = lighting_config.get("world_hdri")
        if hdri_cfg and hdri_cfg.get("path"):
            try:
                env_tex = nodes.new(type='ShaderNodeTexEnvironment')
                env_tex.image = bpy.data.images.load(hdri_cfg["path"], check_existing=True)

                mapping = nodes.new(type='ShaderNodeMapping')
                texcoord = nodes.new(type='ShaderNodeTexCoord')
                background = nodes.new(type='ShaderNodeBackground')
                world_output = nodes.new(type='ShaderNodeOutputWorld')

                # Strength
                background.inputs['Strength'].default_value = float(hdri_cfg.get("strength", 1.0))

                # Rotation (в градусах)
                rotation = hdri_cfg.get("rotation", [0.0, 0.0, 0.0])
                mapping.inputs['Rotation'].default_value[0] = math.radians(rotation[0])
                mapping.inputs['Rotation'].default_value[1] = math.radians(rotation[1])
                mapping.inputs['Rotation'].default_value[2] = math.radians(rotation[2])

                # Лінки
                links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
                links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
                links.new(env_tex.outputs['Color'], background.inputs['Color'])
                links.new(background.outputs['Background'], world_output.inputs['Surface'])

                return
            except Exception as e:
                logger.warning(f"Не вдалося завантажити HDRI: {e}. Використовую бекграунд колір.")

        # Fallback: суцільний бекграунд
        bg_cfg = lighting_config.get("world_background", {})
        background = nodes.new(type='ShaderNodeBackground')
        world_output = nodes.new(type='ShaderNodeOutputWorld')
        color = bg_cfg.get("color", [0.1, 0.15, 0.2, 1.0])
        strength = float(bg_cfg.get("strength", 0.3))
        background.inputs['Color'].default_value = (*color[:3], color[3] if len(color) > 3 else 1.0)
        background.inputs['Strength'].default_value = strength
        links.new(background.outputs['Background'], world_output.inputs['Surface'])

    def _create_three_point_lighting(self, preset_settings: Dict[str, Any]) -> None:
        """Створює базовий three-point lighting сетап (key, fill, rim)."""
        # Key
        self._create_light_from_config({
            "type": "AREA",
            "name": "Key_Light",
            "position": preset_settings.get("key_position", [5.0, -5.0, 5.0]),
            "energy": preset_settings.get("key_energy", 800.0),
            "color": preset_settings.get("key_color", [1.0, 1.0, 1.0]),
            "size": preset_settings.get("key_size", 3.0)
        })

        # Fill
        self._create_light_from_config({
            "type": "AREA",
            "name": "Fill_Light",
            "position": preset_settings.get("fill_position", [-5.0, -2.5, 3.0]),
            "energy": preset_settings.get("fill_energy", 300.0),
            "color": preset_settings.get("fill_color", [0.9, 0.95, 1.0]),
            "size": preset_settings.get("fill_size", 4.0)
        })

        # Rim
        self._create_light_from_config({
            "type": "AREA",
            "name": "Rim_Light",
            "position": preset_settings.get("rim_position", [0.0, 5.0, 3.0]),
            "energy": preset_settings.get("rim_energy", 500.0),
            "color": preset_settings.get("rim_color", [1.0, 0.95, 0.9]),
            "size": preset_settings.get("rim_size", 2.0)
        })

    def _create_light_from_config(self, light_cfg: Dict[str, Any]) -> None:
        """Створює лайт певного типу на основі конфігурації."""
        light_type = light_cfg.get("type", "SUN").upper()
        name = light_cfg.get("name", f"Light_{light_type}")
        position = Vector(light_cfg.get("position", [0.0, 0.0, 5.0]))
        rotation = light_cfg.get("rotation")  # очікуємо градуси [x, y, z]
        energy = float(light_cfg.get("energy", 10.0))
        color = light_cfg.get("color", [1.0, 1.0, 1.0])

        bpy.ops.object.light_add(type=light_type)
        light_obj = bpy.context.active_object
        light_obj.name = name
        light_obj.location = position

        if rotation is not None:
            light_obj.rotation_euler = [math.radians(r) for r in rotation]

        data = light_obj.data
        data.energy = energy
        data.color = color

        # Додаткові параметри для різних типів
        if light_type == 'AREA':
            size = float(light_cfg.get("size", 1.0))
            data.size = size
            shape = light_cfg.get("shape")
            if shape in {"SQUARE", "RECTANGLE", "DISK", "ELLIPSE"}:
                data.shape = shape
            size_x = light_cfg.get("size_x")
            size_y = light_cfg.get("size_y")
            if size_x:
                data.size_x = float(size_x)
            if size_y:
                data.size_y = float(size_y)
        elif light_type == 'SPOT':
            data.spot_size = float(light_cfg.get("spot_size", math.radians(45.0)))
            data.spot_blend = float(light_cfg.get("spot_blend", 0.15))
        # POINT і SUN не потребують додаткових налаштувань за замовчуванням
    
    def generate_scene_from_config(self, shot_config: Dict[str, Any]) -> None:
        """Генерує всю сцену на основі конфігурації шоту"""
        try:
            # Очищення сцени
            self.clear_scene()
            
            # Створення рельєфу
            if "terrain" in shot_config:
                self.create_terrain(shot_config["terrain"])
            
            # Створення будівель
            for building_config in shot_config.get("buildings", []):
                self.create_building(building_config)
            
            # Створення юнітів
            for unit_config in shot_config.get("units", []):
                self.create_unit(unit_config)
            
            # Створення ефектів
            for effect_config in shot_config.get("effects", []):
                self.create_effect(effect_config)
            
            # Налаштування камери
            if "camera" in shot_config:
                self.setup_camera(shot_config["camera"])
            
            # Налаштування освітлення
            if "lighting" in shot_config:
                self.setup_lighting(shot_config["lighting"])
            
            logger.info("Сцена згенерована успішно")
            
        except Exception as e:
            logger.error(f"Помилка генерації сцени: {e}")
            raise

# Приклад використання
if __name__ == "__main__":
    # Ініціалізація генератора
    generator = EnhancedGeometryGenerator()
    
    # Приклад конфігурації шоту
    shot_config = {
        "terrain": {
            "type": "plane",
            "size": [20, 20]
        },
        "buildings": [
            {
                "name": "Command Center",
                "type": "cube",
                "position": [0, 0, 0],
                "scale": [2, 2, 1.5]
            }
        ],
        "units": [
            {
                "name": "Marine",
                "type": "soldier",
                "position": [3, 0, 0],
                "scale": [1, 1, 1]
            }
        ],
        "camera": {
            "position": [0, -10, 5],
            "rotation": [60, 0, 0]
        }
    }
    
    # Генерація сцени
    generator.generate_scene_from_config(shot_config)
    print("Сцена згенерована успішно")
