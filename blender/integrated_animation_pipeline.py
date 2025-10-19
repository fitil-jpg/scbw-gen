"""
Інтегрований пайплайн анімації для Blender SCBW
Об'єднує всі компоненти системи анімації та рендерингу послідовностей
"""

import bpy
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import yaml
import json
from mathutils import Vector, Euler

# Додавання поточної директорії до шляху
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Імпорт компонентів системи анімації
from animation_system import (
    KeyframeManager,
    CameraCurveAnimator,
    AnimationSequenceRenderer,
    AnimationUI
)
from animation_examples import AnimationExamples

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedAnimationPipeline:
    """Інтегрований пайплайн анімації."""
    
    def __init__(self, config_dir: str = "assets/animations", 
                 output_dir: str = "renders/blender/animation"):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ініціалізація компонентів
        self.keyframe_manager = KeyframeManager()
        self.camera_animator = CameraCurveAnimator()
        self.sequence_renderer = AnimationSequenceRenderer(self.output_dir)
        self.animation_examples = AnimationExamples()
        
        # Завантаження конфігурації
        self.config = self.load_animation_config()
        
        logger.info("Інтегрований пайплайн анімації ініціалізовано")
    
    def load_animation_config(self) -> Dict[str, Any]:
        """Завантажує конфігурацію анімації."""
        try:
            config_path = self.config_dir / "animations_config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Конфігурація анімації завантажена: {config_path}")
                return config
            else:
                logger.warning(f"Файл конфігурації не знайдено: {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Помилка завантаження конфігурації: {e}")
            return {}
    
    def create_shot_from_template(self, template_name: str, shot_id: str,
                                custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Створює шот анімації на основі шаблону.
        
        Args:
            template_name: Назва шаблону
            shot_id: Ідентифікатор шоту
            custom_settings: Додаткові налаштування
        
        Returns:
            Результат створення шоту
        """
        try:
            # Отримання шаблону
            templates = self.config.get('animation_templates', {})
            template = templates.get(template_name, {})
            
            if not template:
                raise ValueError(f"Шаблон не знайдено: {template_name}")
            
            # Об'єднання шаблону з додатковими налаштуваннями
            shot_config = template.copy()
            shot_config['shot_id'] = shot_id
            
            if custom_settings:
                self._merge_settings(shot_config, custom_settings)
            
            # Створення анімації на основі типу
            animation_type = shot_config.get('name', '').lower()
            
            if 'battle' in animation_type:
                result = self.animation_examples.create_battle_animation(shot_id)
            elif 'construction' in animation_type:
                result = self.animation_examples.create_building_construction_animation(shot_id)
            elif 'cinematic' in animation_type:
                result = self.animation_examples.create_cinematic_camera_animation(shot_id)
            else:
                # Створення кастомної анімації
                result = self._create_custom_animation(shot_id, shot_config)
            
            # Збереження конфігурації шоту
            self._save_shot_config(shot_id, shot_config)
            
            logger.info(f"Шот створено з шаблону: {template_name} -> {shot_id}")
            return result
            
        except Exception as e:
            logger.error(f"Помилка створення шоту з шаблону: {e}")
            return {'shot_id': shot_id, 'status': 'error', 'error': str(e)}
    
    def _merge_settings(self, base_config: Dict[str, Any], 
                       custom_settings: Dict[str, Any]) -> None:
        """Об'єднує налаштування рекурсивно."""
        for key, value in custom_settings.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_settings(base_config[key], value)
            else:
                base_config[key] = value
    
    def _create_custom_animation(self, shot_id: str, 
                               shot_config: Dict[str, Any]) -> Dict[str, Any]:
        """Створює кастомну анімацію на основі конфігурації."""
        try:
            # Очищення сцени
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            
            # Створення території
            terrain_config = shot_config.get('terrain', {})
            if terrain_config:
                self._create_terrain(terrain_config)
            
            # Створення об'єктів
            objects_config = shot_config.get('objects', {})
            if objects_config:
                self._create_objects(objects_config)
            
            # Створення камери
            camera_config = shot_config.get('camera', {})
            if camera_config:
                camera = self._create_camera(camera_config)
                
                # Анімація камери
                if 'animation' in camera_config:
                    self._animate_camera(camera, camera_config['animation'])
            
            # Створення освітлення
            lighting_config = shot_config.get('lighting', {})
            if lighting_config:
                self._create_lighting(lighting_config)
            
            # Налаштування рендерингу
            render_settings = shot_config.get('render_settings', {})
            if not render_settings:
                render_settings = self.config.get('global_settings', {})
            
            # Рендеринг анімації
            duration = shot_config.get('duration', 100)
            rendered_files = self.sequence_renderer.render_animation_sequence(
                shot_id, 1, duration, render_settings
            )
            
            # Створення маніфесту
            manifest = self.sequence_renderer.create_animation_manifest(
                shot_id, rendered_files, shot_config
            )
            
            return {
                'shot_id': shot_id,
                'status': 'success',
                'rendered_files': rendered_files,
                'manifest': manifest,
                'animation_config': shot_config
            }
            
        except Exception as e:
            logger.error(f"Помилка створення кастомної анімації: {e}")
            return {'shot_id': shot_id, 'status': 'error', 'error': str(e)}
    
    def _create_terrain(self, terrain_config: Dict[str, Any]) -> None:
        """Створює територію."""
        terrain_type = terrain_config.get('type', 'plane')
        size = terrain_config.get('size', [20, 20])
        
        if terrain_type == 'plane':
            bpy.ops.mesh.primitive_plane_add(size=max(size), location=(0, 0, 0))
            terrain = bpy.context.active_object
            terrain.name = "Terrain"
            
            # Матеріал території
            material_config = terrain_config.get('material', {})
            if material_config:
                self._create_material(terrain, material_config)
    
    def _create_objects(self, objects_config: Dict[str, Any]) -> List[bpy.types.Object]:
        """Створює об'єкти сцени."""
        objects = []
        
        for obj_config in objects_config:
            obj_type = obj_config.get('type', 'cube')
            position = obj_config.get('position', [0, 0, 0])
            scale = obj_config.get('scale', [1, 1, 1])
            name = obj_config.get('name', 'Object')
            
            if obj_type == 'cube':
                bpy.ops.mesh.primitive_cube_add(location=position)
            elif obj_type == 'sphere':
                bpy.ops.mesh.primitive_uv_sphere_add(location=position)
            elif obj_type == 'cylinder':
                bpy.ops.mesh.primitive_cylinder_add(location=position)
            
            obj = bpy.context.active_object
            obj.name = name
            obj.scale = scale
            
            # Матеріал об'єкта
            material_config = obj_config.get('material', {})
            if material_config:
                self._create_material(obj, material_config)
            
            # Анімація об'єкта
            animation_config = obj_config.get('animation', {})
            if animation_config:
                self._animate_object(obj, animation_config)
            
            objects.append(obj)
        
        return objects
    
    def _create_camera(self, camera_config: Dict[str, Any]) -> bpy.types.Object:
        """Створює камеру."""
        position = camera_config.get('position', [0, -10, 5])
        rotation = camera_config.get('rotation', [60, 0, 0])
        focal_length = camera_config.get('focal_length', 50)
        
        bpy.ops.object.camera_add(location=position)
        camera = bpy.context.active_object
        camera.name = "Camera"
        camera.rotation_euler = rotation
        camera.data.lens = focal_length
        
        return camera
    
    def _create_lighting(self, lighting_config: Dict[str, Any]) -> None:
        """Створює освітлення."""
        # Сонячне світло
        sun_config = lighting_config.get('sun_light', {})
        if sun_config:
            position = sun_config.get('position', [10, 10, 10])
            energy = sun_config.get('energy', 3.0)
            color = sun_config.get('color', [1.0, 0.95, 0.8])
            
            bpy.ops.object.light_add(type='SUN', location=position)
            sun = bpy.context.active_object
            sun.name = "Sun"
            sun.data.energy = energy
            sun.data.color = color
        
        # Додаткове освітлення
        additional_lights = lighting_config.get('additional_lights', [])
        for light_config in additional_lights:
            light_type = light_config.get('type', 'AREA')
            position = light_config.get('position', [0, 0, 5])
            energy = light_config.get('energy', 1.0)
            color = light_config.get('color', [1.0, 1.0, 1.0])
            
            bpy.ops.object.light_add(type=light_type, location=position)
            light = bpy.context.active_object
            light.name = light_config.get('name', 'Light')
            light.data.energy = energy
            light.data.color = color
    
    def _create_material(self, obj: bpy.types.Object, material_config: Dict[str, Any]) -> None:
        """Створює матеріал для об'єкта."""
        name = material_config.get('name', 'Material')
        color = material_config.get('color', [0.8, 0.8, 0.8])
        metallic = material_config.get('metallic', 0.0)
        roughness = material_config.get('roughness', 0.5)
        
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        
        # Налаштування Principled BSDF
        principled = material.node_tree.nodes["Principled BSDF"]
        principled.inputs[0].default_value = (*color, 1.0)  # Base Color
        principled.inputs[6].default_value = metallic  # Metallic
        principled.inputs[7].default_value = roughness  # Roughness
        
        obj.data.materials.append(material)
    
    def _animate_object(self, obj: bpy.types.Object, animation_config: Dict[str, Any]) -> None:
        """Анімує об'єкт."""
        # Анімація позиції
        if 'location' in animation_config:
            location_keyframes = animation_config['location']
            self.keyframe_manager.add_keyframes_sequence(obj, location_keyframes)
        
        # Анімація обертання
        if 'rotation' in animation_config:
            rotation_keyframes = animation_config['rotation']
            self.keyframe_manager.add_keyframes_sequence(obj, rotation_keyframes)
        
        # Анімація масштабу
        if 'scale' in animation_config:
            scale_keyframes = animation_config['scale']
            self.keyframe_manager.add_keyframes_sequence(obj, scale_keyframes)
        
        # Встановлення інтерполяції
        interpolation = animation_config.get('interpolation', 'BEZIER')
        self.keyframe_manager.set_interpolation(obj, interpolation)
    
    def _animate_camera(self, camera: bpy.types.Object, animation_config: Dict[str, Any]) -> None:
        """Анімує камеру."""
        animation_type = animation_config.get('type', 'keyframes')
        
        if animation_type == 'keyframes':
            # Анімація ключовими кадрами
            keyframes = animation_config.get('keyframes', [])
            self.keyframe_manager.add_keyframes_sequence(camera, keyframes)
            
        elif animation_type == 'curve':
            # Анімація по кривій
            curve_config = animation_config.get('curve', {})
            curve_type = curve_config.get('type', 'custom')
            
            if curve_type == 'circular':
                center = Vector(curve_config.get('center', [0, 0, 0]))
                radius = curve_config.get('radius', 10.0)
                height = curve_config.get('height', 5.0)
                
                curve = self.camera_animator.create_circular_camera_path(
                    center, radius, height
                )
                
            elif curve_type == 'helical':
                center = Vector(curve_config.get('center', [0, 0, 0]))
                radius = curve_config.get('radius', 10.0)
                height_start = curve_config.get('height_start', 0.0)
                height_end = curve_config.get('height_end', 10.0)
                turns = curve_config.get('turns', 2)
                
                curve = self.camera_animator.create_helical_camera_path(
                    center, radius, height_start, height_end, turns
                )
            
            elif curve_type == 'custom':
                points = [Vector(p) for p in curve_config.get('points', [])]
                curve = self.camera_animator.create_camera_path(points)
            
            # Анімація камери вздовж кривої
            start_frame = animation_config.get('start_frame', 1)
            end_frame = animation_config.get('end_frame', 100)
            follow_curve = animation_config.get('follow_curve', True)
            
            self.camera_animator.animate_camera_along_curve(
                camera, curve, start_frame, end_frame, follow_curve
            )
    
    def _save_shot_config(self, shot_id: str, shot_config: Dict[str, Any]) -> None:
        """Зберігає конфігурацію шоту."""
        try:
            shots_dir = self.output_dir / "configs"
            shots_dir.mkdir(parents=True, exist_ok=True)
            
            config_path = shots_dir / f"{shot_id}.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(shot_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Конфігурація шоту збережена: {config_path}")
            
        except Exception as e:
            logger.error(f"Помилка збереження конфігурації шоту: {e}")
    
    def batch_create_animations(self, shots_config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Створює кілька анімацій пакетно.
        
        Args:
            shots_config: Список конфігурацій шотів
        
        Returns:
            Результати створення анімацій
        """
        try:
            results = {}
            
            for shot_config in shots_config:
                shot_id = shot_config.get('shot_id', 'unknown')
                template_name = shot_config.get('template', 'battle_sequence')
                custom_settings = shot_config.get('custom_settings', {})
                
                logger.info(f"Створення анімації: {shot_id} (шаблон: {template_name})")
                
                result = self.create_shot_from_template(
                    template_name, shot_id, custom_settings
                )
                
                results[shot_id] = result
            
            # Підсумкова статистика
            successful = sum(1 for r in results.values() if r.get('status') == 'success')
            failed = sum(1 for r in results.values() if r.get('status') == 'error')
            
            logger.info(f"Пакетне створення анімацій завершено: {successful} успішних, {failed} помилок")
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка пакетного створення анімацій: {e}")
            raise
    
    def export_animation(self, shot_id: str, export_format: str = "blend") -> Path:
        """
        Експортує анімацію у різних форматах.
        
        Args:
            shot_id: Ідентифікатор шоту
            export_format: Формат експорту
        
        Returns:
            Шлях до експортованого файлу
        """
        try:
            export_dir = self.output_dir / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            if export_format == "blend":
                export_path = export_dir / f"{shot_id}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(export_path))
                
            elif export_format == "fbx":
                export_path = export_dir / f"{shot_id}.fbx"
                bpy.ops.export_scene.fbx(filepath=str(export_path))
                
            elif export_format == "obj":
                export_path = export_dir / f"{shot_id}.obj"
                bpy.ops.export_scene.obj(filepath=str(export_path))
                
            elif export_format == "usd":
                export_path = export_dir / f"{shot_id}.usd"
                bpy.ops.wm.usd_export(filepath=str(export_path))
                
            else:
                raise ValueError(f"Непідтримуваний формат експорту: {export_format}")
            
            logger.info(f"Анімація експортована: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Помилка експорту анімації: {e}")
            raise
    
    def get_animation_info(self, shot_id: str) -> Dict[str, Any]:
        """Повертає інформацію про анімацію."""
        try:
            # Завантаження конфігурації шоту
            config_path = self.output_dir / "configs" / f"{shot_id}.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    shot_config = yaml.safe_load(f)
            else:
                shot_config = {}
            
            # Інформація про сцену
            scene = bpy.context.scene
            scene_info = {
                'objects_count': len(scene.objects),
                'materials_count': len(bpy.data.materials),
                'lights_count': len([obj for obj in scene.objects if obj.type == 'LIGHT']),
                'cameras_count': len([obj for obj in scene.objects if obj.type == 'CAMERA']),
                'render_engine': scene.render.engine,
                'resolution': [scene.render.resolution_x, scene.render.resolution_y],
                'frame_range': [scene.frame_start, scene.frame_end],
                'fps': scene.render.fps
            }
            
            # Інформація про анімацію
            animation_info = {
                'shot_id': shot_id,
                'scene_info': scene_info,
                'config': shot_config,
                'output_directory': str(self.output_dir / shot_id)
            }
            
            return animation_info
            
        except Exception as e:
            logger.error(f"Помилка отримання інформації про анімацію: {e}")
            return {}


# Приклад використання
if __name__ == "__main__":
    # Ініціалізація пайплайну
    pipeline = IntegratedAnimationPipeline()
    
    # Приклад створення анімації з шаблону
    print("Створення анімації битви...")
    battle_result = pipeline.create_shot_from_template(
        "battle_sequence", 
        "test_battle_001",
        {
            'units': {'count': 10},
            'camera': {'radius': 30.0, 'height': 12.0},
            'render_settings': {'samples': 256}
        }
    )
    print(f"Результат: {battle_result['status']}")
    
    # Приклад пакетного створення
    print("Пакетне створення анімацій...")
    batch_config = [
        {
            'shot_id': 'batch_001',
            'template': 'battle_sequence',
            'custom_settings': {'units': {'count': 5}}
        },
        {
            'shot_id': 'batch_002',
            'template': 'building_construction',
            'custom_settings': {'building': {'type': 'Factory'}}
        },
        {
            'shot_id': 'batch_003',
            'template': 'cinematic_shot',
            'custom_settings': {'camera': {'radius': 25.0}}
        }
    ]
    
    batch_results = pipeline.batch_create_animations(batch_config)
    print(f"Пакетне створення завершено: {len(batch_results)} шотів")
    
    # Експорт анімації
    print("Експорт анімації...")
    export_path = pipeline.export_animation("test_battle_001", "blend")
    print(f"Анімація експортована: {export_path}")
    
    print("Інтегрований пайплайн анімації протестовано успішно!")