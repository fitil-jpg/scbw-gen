"""
Система анімації для Blender SCBW pipeline
Підтримує ключові кадри, криві камери та рендеринг послідовностей
"""

import bpy
import bmesh
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import mathutils
from mathutils import Vector, Euler, Quaternion
import json
import numpy as np

LOG = logging.getLogger(__name__)


class KeyframeManager:
    """Менеджер ключових кадрів для об'єктів та камери."""
    
    def __init__(self):
        self.keyframe_types = {
            'location': 'location',
            'rotation': 'rotation_euler',
            'scale': 'scale',
            'fov': 'lens',
            'energy': 'energy'
        }
    
    def add_keyframe(self, obj: bpy.types.Object, frame: int, 
                    keyframe_type: str, value: Optional[Any] = None) -> None:
        """
        Додає ключовий кадр до об'єкта.
        
        Args:
            obj: Об'єкт Blender
            frame: Номер кадру
            keyframe_type: Тип ключового кадру (location, rotation, scale, fov, energy)
            value: Значення (опціонально, якщо не вказано - використовується поточне)
        """
        try:
            # Встановлення поточного кадру
            bpy.context.scene.frame_set(frame)
            
            # Встановлення значення якщо вказано
            if value is not None:
                if keyframe_type == 'location':
                    obj.location = value
                elif keyframe_type == 'rotation':
                    obj.rotation_euler = value
                elif keyframe_type == 'scale':
                    obj.scale = value
                elif keyframe_type == 'fov' and obj.type == 'CAMERA':
                    obj.data.lens = value
                elif keyframe_type == 'energy' and obj.type == 'LIGHT':
                    obj.data.energy = value
            
            # Додавання ключового кадру
            if keyframe_type in self.keyframe_types:
                data_path = self.keyframe_types[keyframe_type]
                obj.keyframe_insert(data_path=data_path, frame=frame)
                LOG.info(f"Додано ключовий кадр {keyframe_type} для {obj.name} на кадрі {frame}")
            
        except Exception as e:
            LOG.error(f"Помилка додавання ключового кадру: {e}")
            raise
    
    def add_keyframes_sequence(self, obj: bpy.types.Object, 
                              keyframes: List[Dict[str, Any]]) -> None:
        """
        Додає послідовність ключових кадрів.
        
        Args:
            obj: Об'єкт Blender
            keyframes: Список словників з ключовими кадрами
        """
        try:
            for keyframe in keyframes:
                frame = keyframe.get('frame', 1)
                keyframe_type = keyframe.get('type', 'location')
                value = keyframe.get('value')
                
                self.add_keyframe(obj, frame, keyframe_type, value)
            
            LOG.info(f"Додано {len(keyframes)} ключових кадрів для {obj.name}")
            
        except Exception as e:
            LOG.error(f"Помилка додавання послідовності ключових кадрів: {e}")
            raise
    
    def set_interpolation(self, obj: bpy.types.Object, 
                         interpolation_type: str = 'BEZIER') -> None:
        """
        Встановлює тип інтерполяції для ключових кадрів.
        
        Args:
            obj: Об'єкт Blender
            interpolation_type: Тип інтерполяції (BEZIER, LINEAR, CONSTANT, etc.)
        """
        try:
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        keyframe.interpolation = interpolation_type
            
            LOG.info(f"Встановлено інтерполяцію {interpolation_type} для {obj.name}")
            
        except Exception as e:
            LOG.error(f"Помилка встановлення інтерполяції: {e}")
            raise


class CameraCurveAnimator:
    """Аніматор камери з підтримкою кривих Безьє."""
    
    def __init__(self):
        self.keyframe_manager = KeyframeManager()
    
    def create_camera_path(self, points: List[Vector], 
                          curve_name: str = "CameraPath") -> bpy.types.Curve:
        """
        Створює криву шляху для камери.
        
        Args:
            points: Список точок для кривої
            curve_name: Назва кривої
        
        Returns:
            Створена крива
        """
        try:
            # Створення кривої
            curve_data = bpy.data.curves.new(name=curve_name, type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.resolution_u = 64
            
            # Створення сплайну
            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(len(points) - 1)
            
            # Встановлення точок
            for i, point in enumerate(points):
                spline.bezier_points[i].co = point
                spline.bezier_points[i].handle_left_type = 'AUTO'
                spline.bezier_points[i].handle_right_type = 'AUTO'
            
            # Створення об'єкта кривої
            curve_obj = bpy.data.objects.new(curve_name, curve_data)
            bpy.context.collection.objects.link(curve_obj)
            
            LOG.info(f"Створено криву камери: {curve_name} з {len(points)} точками")
            return curve_data
            
        except Exception as e:
            LOG.error(f"Помилка створення кривої камери: {e}")
            raise
    
    def animate_camera_along_curve(self, camera: bpy.types.Object, 
                                 curve: bpy.types.Curve, 
                                 start_frame: int = 1, 
                                 end_frame: int = 100,
                                 follow_curve: bool = True) -> None:
        """
        Анімує камеру вздовж кривої.
        
        Args:
            camera: Об'єкт камери
            curve: Крива шляху
            start_frame: Початковий кадр
            end_frame: Кінцевий кадр
            follow_curve: Чи повинна камера дивитися вздовж кривої
        """
        try:
            # Додавання модифікатора Follow Path
            if follow_curve:
                follow_path = camera.modifiers.new(name="FollowPath", type='FOLLOW_PATH')
                follow_path.target = bpy.data.objects[curve.name]
                follow_path.use_curve_follow = True
                follow_path.forward_axis = 'FORWARD_X'
                follow_path.up_axis = 'UP_Z'
            
            # Анімація offset
            if camera.animation_data is None:
                camera.animation_data_create()
            
            # Ключові кадри для offset
            camera.modifiers["FollowPath"].keyframe_insert(
                data_path="offset_factor", 
                frame=start_frame
            )
            camera.modifiers["FollowPath"].offset_factor = 0.0
            
            camera.modifiers["FollowPath"].keyframe_insert(
                data_path="offset_factor", 
                frame=end_frame
            )
            camera.modifiers["FollowPath"].offset_factor = 1.0
            
            # Встановлення інтерполяції
            if camera.animation_data and camera.animation_data.action:
                for fcurve in camera.animation_data.action.fcurves:
                    if "offset_factor" in fcurve.data_path:
                        for keyframe in fcurve.keyframe_points:
                            keyframe.interpolation = 'BEZIER'
            
            LOG.info(f"Камера анімована вздовж кривої {curve.name} з кадру {start_frame} до {end_frame}")
            
        except Exception as e:
            LOG.error(f"Помилка анімації камери вздовж кривої: {e}")
            raise
    
    def create_circular_camera_path(self, center: Vector, radius: float, 
                                   height: float = 5.0, 
                                   curve_name: str = "CircularCameraPath") -> bpy.types.Curve:
        """
        Створює кругову криву для камери.
        
        Args:
            center: Центр кола
            radius: Радіус кола
            height: Висота камери
            curve_name: Назва кривої
        
        Returns:
            Створена крива
        """
        try:
            # Генерація точок кола
            num_points = 16
            points = []
            
            for i in range(num_points):
                angle = (2 * np.pi * i) / num_points
                x = center.x + radius * np.cos(angle)
                y = center.y + radius * np.sin(angle)
                z = center.z + height
                points.append(Vector((x, y, z)))
            
            return self.create_camera_path(points, curve_name)
            
        except Exception as e:
            LOG.error(f"Помилка створення кругової кривої: {e}")
            raise
    
    def create_helical_camera_path(self, center: Vector, radius: float, 
                                  height_start: float, height_end: float,
                                  turns: int = 2,
                                  curve_name: str = "HelicalCameraPath") -> bpy.types.Curve:
        """
        Створює спіральну криву для камери.
        
        Args:
            center: Центр спіралі
            radius: Радіус спіралі
            height_start: Початкова висота
            height_end: Кінцева висота
            turns: Кількість витків
            curve_name: Назва кривої
        
        Returns:
            Створена крива
        """
        try:
            # Генерація точок спіралі
            num_points = 64
            points = []
            
            for i in range(num_points):
                t = i / (num_points - 1)
                angle = 2 * np.pi * turns * t
                x = center.x + radius * np.cos(angle)
                y = center.y + radius * np.sin(angle)
                z = center.z + height_start + (height_end - height_start) * t
                points.append(Vector((x, y, z)))
            
            return self.create_camera_path(points, curve_name)
            
        except Exception as e:
            LOG.error(f"Помилка створення спіральної кривої: {e}")
            raise


class AnimationSequenceRenderer:
    """Рендерер анімаційних послідовностей."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.keyframe_manager = KeyframeManager()
        self.camera_animator = CameraCurveAnimator()
    
    def setup_animation_timeline(self, start_frame: int = 1, 
                                end_frame: int = 100, 
                                fps: int = 24) -> None:
        """
        Налаштовує таймлайн анімації.
        
        Args:
            start_frame: Початковий кадр
            end_frame: Кінцевий кадр
            fps: Кадрів на секунду
        """
        try:
            scene = bpy.context.scene
            scene.frame_start = start_frame
            scene.frame_end = end_frame
            scene.render.fps = fps
            scene.render.fps_base = 1.0
            
            LOG.info(f"Таймлайн налаштовано: {start_frame}-{end_frame} кадрів, {fps} FPS")
            
        except Exception as e:
            LOG.error(f"Помилка налаштування таймлайну: {e}")
            raise
    
    def create_camera_animation(self, camera: bpy.types.Object, 
                              animation_config: Dict[str, Any]) -> None:
        """
        Створює анімацію камери на основі конфігурації.
        
        Args:
            camera: Об'єкт камери
            animation_config: Конфігурація анімації
        """
        try:
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
            
            LOG.info(f"Анімація камери створена: {animation_type}")
            
        except Exception as e:
            LOG.error(f"Помилка створення анімації камери: {e}")
            raise
    
    def create_object_animation(self, obj: bpy.types.Object, 
                              animation_config: Dict[str, Any]) -> None:
        """
        Створює анімацію об'єкта.
        
        Args:
            obj: Об'єкт для анімації
            animation_config: Конфігурація анімації
        """
        try:
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
            
            LOG.info(f"Анімація об'єкта {obj.name} створена")
            
        except Exception as e:
            LOG.error(f"Помилка створення анімації об'єкта: {e}")
            raise
    
    def render_animation_sequence(self, shot_id: str, 
                                start_frame: int = 1, 
                                end_frame: int = 100,
                                render_settings: Optional[Dict[str, Any]] = None) -> List[Path]:
        """
        Рендерить анімаційну послідовність.
        
        Args:
            shot_id: Ідентифікатор шоту
            start_frame: Початковий кадр
            end_frame: Кінцевий кадр
            render_settings: Налаштування рендерингу
        
        Returns:
            Список шляхів до зрендерених кадрів
        """
        try:
            scene = bpy.context.scene
            
            # Налаштування таймлайну
            self.setup_animation_timeline(start_frame, end_frame)
            
            # Налаштування рендерингу
            if render_settings:
                self._apply_render_settings(render_settings)
            
            # Налаштування виводу
            output_path = self.output_directory / shot_id / "animation"
            scene.render.filepath = str(output_path)
            
            # Рендеринг анімації
            bpy.ops.render.render(animation=True)
            
            # Отримання списку файлів
            rendered_files = []
            for frame in range(start_frame, end_frame + 1):
                frame_file = Path(f"{output_path}{frame:04d}{scene.render.file_extension}")
                if frame_file.exists():
                    rendered_files.append(frame_file)
            
            LOG.info(f"Анімаційна послідовність зрендерена: {len(rendered_files)} кадрів")
            return rendered_files
            
        except Exception as e:
            LOG.error(f"Помилка рендерингу анімаційної послідовності: {e}")
            raise
    
    def _apply_render_settings(self, settings: Dict[str, Any]) -> None:
        """Застосовує налаштування рендерингу."""
        try:
            scene = bpy.context.scene
            
            # Роздільність
            if 'resolution' in settings:
                resolution = settings['resolution']
                scene.render.resolution_x = resolution[0]
                scene.render.resolution_y = resolution[1]
            
            # Формат виводу
            if 'output_format' in settings:
                output_format = settings['output_format']
                if output_format == 'PNG':
                    scene.render.image_settings.file_format = 'PNG'
                    scene.render.image_settings.color_mode = 'RGBA'
                elif output_format == 'JPEG':
                    scene.render.image_settings.file_format = 'JPEG'
                    scene.render.image_settings.color_mode = 'RGB'
                elif output_format == 'EXR':
                    scene.render.image_settings.file_format = 'OPEN_EXR'
                    scene.render.image_settings.color_mode = 'RGBA'
            
            # Рендер двигун
            if 'engine' in settings:
                scene.render.engine = settings['engine']
                
                if settings['engine'] == 'CYCLES':
                    cycles = scene.cycles
                    cycles.samples = settings.get('samples', 128)
                    cycles.use_denoising = settings.get('denoising', True)
                elif settings['engine'] == 'BLENDER_EEVEE':
                    eevee = scene.eevee
                    eevee.taa_render_samples = settings.get('samples', 64)
            
        except Exception as e:
            LOG.error(f"Помилка застосування налаштувань рендерингу: {e}")
            raise
    
    def create_animation_manifest(self, shot_id: str, 
                                rendered_files: List[Path],
                                animation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Створює маніфест анімації.
        
        Args:
            shot_id: Ідентифікатор шоту
            rendered_files: Список зрендерених файлів
            animation_config: Конфігурація анімації
        
        Returns:
            Маніфест анімації
        """
        try:
            scene = bpy.context.scene
            
            manifest = {
                'shot_id': shot_id,
                'animation_type': 'sequence',
                'frame_range': [scene.frame_start, scene.frame_end],
                'fps': scene.render.fps,
                'total_frames': len(rendered_files),
                'render_engine': scene.render.engine,
                'resolution': [scene.render.resolution_x, scene.render.resolution_y],
                'output_format': scene.render.image_settings.file_format,
                'files': [str(f) for f in rendered_files],
                'animation_config': animation_config,
                'created_at': bpy.context.scene.frame_current
            }
            
            # Збереження маніфесту
            manifest_path = self.output_directory / shot_id / "animation_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            LOG.info(f"Маніфест анімації створено: {manifest_path}")
            return manifest
            
        except Exception as e:
            LOG.error(f"Помилка створення маніфесту анімації: {e}")
            raise


class AnimationUI:
    """Інтерфейс для налаштування анімації."""
    
    def __init__(self):
        self.sequence_renderer = None
    
    def create_animation_panel(self, layout, context):
        """Створює панель налаштувань анімації."""
        try:
            box = layout.box()
            box.label(text="SCBW Animation System")
            
            # Налаштування таймлайну
            timeline_box = box.box()
            timeline_box.label(text="Timeline Settings")
            
            row = timeline_box.row()
            row.prop(context.scene, "frame_start", text="Start Frame")
            row.prop(context.scene, "frame_end", text="End Frame")
            
            row = timeline_box.row()
            row.prop(context.scene.render, "fps", text="FPS")
            
            # Налаштування камери
            camera_box = box.box()
            camera_box.label(text="Camera Animation")
            
            row = camera_box.row()
            row.operator("scbw.create_circular_camera_path", text="Circular Path")
            row.operator("scbw.create_helical_camera_path", text="Helical Path")
            
            # Налаштування рендерингу
            render_box = box.box()
            render_box.label(text="Render Settings")
            
            row = render_box.row()
            row.prop(context.scene.render, "engine", text="Engine")
            
            if context.scene.render.engine == 'CYCLES':
                row = render_box.row()
                row.prop(context.scene.cycles, "samples", text="Samples")
            
            # Кнопки рендерингу
            render_box.operator("scbw.render_animation_sequence", text="Render Animation")
            
        except Exception as e:
            LOG.error(f"Помилка створення панелі анімації: {e}")


# Оператори Blender
class SCBW_OT_CreateCircularCameraPath(bpy.types.Operator):
    """Створює кругову криву для камери."""
    bl_idname = "scbw.create_circular_camera_path"
    bl_label = "Create Circular Camera Path"
    bl_options = {'REGISTER', 'UNDO'}
    
    radius: bpy.props.FloatProperty(
        name="Radius",
        description="Радіус кругової кривої",
        default=10.0,
        min=1.0,
        max=100.0
    )
    
    height: bpy.props.FloatProperty(
        name="Height",
        description="Висота камери",
        default=5.0,
        min=0.0,
        max=50.0
    )
    
    def execute(self, context):
        try:
            camera_animator = CameraCurveAnimator()
            center = Vector((0, 0, 0))
            
            curve = camera_animator.create_circular_camera_path(
                center, self.radius, self.height
            )
            
            self.report({'INFO'}, f"Створено кругову криву з радіусом {self.radius}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка створення кругової кривої: {e}")
            return {'CANCELLED'}


class SCBW_OT_CreateHelicalCameraPath(bpy.types.Operator):
    """Створює спіральну криву для камери."""
    bl_idname = "scbw.create_helical_camera_path"
    bl_label = "Create Helical Camera Path"
    bl_options = {'REGISTER', 'UNDO'}
    
    radius: bpy.props.FloatProperty(
        name="Radius",
        description="Радіус спіралі",
        default=10.0,
        min=1.0,
        max=100.0
    )
    
    height_start: bpy.props.FloatProperty(
        name="Start Height",
        description="Початкова висота",
        default=0.0,
        min=0.0,
        max=50.0
    )
    
    height_end: bpy.props.FloatProperty(
        name="End Height",
        description="Кінцева висота",
        default=20.0,
        min=0.0,
        max=100.0
    )
    
    turns: bpy.props.IntProperty(
        name="Turns",
        description="Кількість витків",
        default=2,
        min=1,
        max=10
    )
    
    def execute(self, context):
        try:
            camera_animator = CameraCurveAnimator()
            center = Vector((0, 0, 0))
            
            curve = camera_animator.create_helical_camera_path(
                center, self.radius, self.height_start, 
                self.height_end, self.turns
            )
            
            self.report({'INFO'}, f"Створено спіральну криву з {self.turns} витками")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка створення спіральної кривої: {e}")
            return {'CANCELLED'}


class SCBW_OT_RenderAnimationSequence(bpy.types.Operator):
    """Рендерить анімаційну послідовність."""
    bl_idname = "scbw.render_animation_sequence"
    bl_label = "Render Animation Sequence"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            output_dir = Path("renders/blender/animation")
            sequence_renderer = AnimationSequenceRenderer(output_dir)
            
            # Рендеринг поточної сцени
            rendered_files = sequence_renderer.render_animation_sequence(
                "current_scene",
                context.scene.frame_start,
                context.scene.frame_end
            )
            
            self.report({'INFO'}, f"Зрендерено {len(rendered_files)} кадрів")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка рендерингу: {e}")
            return {'CANCELLED'}


# Реєстрація класів
classes = [
    SCBW_OT_CreateCircularCameraPath,
    SCBW_OT_CreateHelicalCameraPath,
    SCBW_OT_RenderAnimationSequence
]


def register():
    """Реєструє класи в Blender."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Скасовує реєстрацію класів."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    # Тестування системи анімації
    logging.basicConfig(level=logging.INFO)
    
    # Створення тестової сцени
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"
    
    # Створення камери
    bpy.ops.object.camera_add(location=(0, -10, 5))
    camera = bpy.context.active_object
    
    # Тестування ключових кадрів
    keyframe_manager = KeyframeManager()
    
    # Анімація куба
    keyframes = [
        {'frame': 1, 'type': 'location', 'value': Vector((0, 0, 0))},
        {'frame': 50, 'type': 'location', 'value': Vector((5, 5, 5))},
        {'frame': 100, 'type': 'location', 'value': Vector((0, 0, 0))}
    ]
    keyframe_manager.add_keyframes_sequence(cube, keyframes)
    
    # Тестування кругової кривої камери
    camera_animator = CameraCurveAnimator()
    curve = camera_animator.create_circular_camera_path(
        Vector((0, 0, 0)), 15.0, 8.0
    )
    
    # Анімація камери вздовж кривої
    camera_animator.animate_camera_along_curve(
        camera, curve, 1, 100, True
    )
    
    print("Система анімації протестована успішно!")