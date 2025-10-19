"""
Приклади використання системи анімації для Blender SCBW pipeline
Демонструє різні типи анімації та рендерингу послідовностей
"""

import bpy
from pathlib import Path
from typing import Dict, List, Any
import logging
from mathutils import Vector
import json

# Імпорт системи анімації
from animation_system import (
    KeyframeManager, 
    CameraCurveAnimator, 
    AnimationSequenceRenderer,
    AnimationUI
)

LOG = logging.getLogger(__name__)


class AnimationExamples:
    """Приклади анімації для різних сценаріїв."""
    
    def __init__(self):
        self.keyframe_manager = KeyframeManager()
        self.camera_animator = CameraCurveAnimator()
        self.sequence_renderer = AnimationSequenceRenderer(Path("renders/blender/animation"))
    
    def create_battle_animation(self, shot_id: str) -> Dict[str, Any]:
        """
        Створює анімацію битви з рухом одиниць та камери.
        
        Args:
            shot_id: Ідентифікатор шоту
        
        Returns:
            Конфігурація анімації
        """
        try:
            # Очищення сцени
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            
            # Створення території
            bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
            terrain = bpy.context.active_object
            terrain.name = "BattleTerrain"
            
            # Додавання матеріалу до території
            terrain_mat = bpy.data.materials.new(name="TerrainMaterial")
            terrain_mat.use_nodes = True
            terrain_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.6, 0.2, 1.0)
            terrain.data.materials.append(terrain_mat)
            
            # Створення одиниць
            units = []
            for i in range(5):
                bpy.ops.mesh.primitive_cube_add(location=(i * 2 - 4, -5, 0.5))
                unit = bpy.context.active_object
                unit.name = f"Unit_{i+1}"
                unit.scale = (0.5, 0.5, 1.0)
                
                # Матеріал одиниці
                unit_mat = bpy.data.materials.new(name=f"UnitMaterial_{i+1}")
                unit_mat.use_nodes = True
                unit_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.2, 0.8, 1.0)
                unit.data.materials.append(unit_mat)
                
                units.append(unit)
            
            # Створення камери
            bpy.ops.object.camera_add(location=(0, -15, 8))
            camera = bpy.context.active_object
            camera.name = "BattleCamera"
            camera.rotation_euler = (60, 0, 0)
            
            # Анімація одиниць - рух вперед
            for i, unit in enumerate(units):
                keyframes = [
                    {'frame': 1, 'type': 'location', 'value': Vector((i * 2 - 4, -5, 0.5))},
                    {'frame': 50, 'type': 'location', 'value': Vector((i * 2 - 4, 0, 0.5))},
                    {'frame': 100, 'type': 'location', 'value': Vector((i * 2 - 4, 5, 0.5))}
                ]
                self.keyframe_manager.add_keyframes_sequence(unit, keyframes)
            
            # Анімація камери - круговий рух
            curve = self.camera_animator.create_circular_camera_path(
                Vector((0, 0, 0)), 20.0, 8.0, "BattleCameraPath"
            )
            self.camera_animator.animate_camera_along_curve(
                camera, curve, 1, 100, True
            )
            
            # Налаштування освітлення
            bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
            sun = bpy.context.active_object
            sun.name = "BattleSun"
            sun.data.energy = 3.0
            
            # Налаштування рендерингу
            render_settings = {
                'engine': 'CYCLES',
                'samples': 128,
                'resolution': [1920, 1080],
                'output_format': 'PNG',
                'denoising': True
            }
            
            # Рендеринг анімації
            rendered_files = self.sequence_renderer.render_animation_sequence(
                shot_id, 1, 100, render_settings
            )
            
            # Створення маніфесту
            animation_config = {
                'type': 'battle',
                'units_count': len(units),
                'camera_path': 'circular',
                'duration': 100
            }
            
            manifest = self.sequence_renderer.create_animation_manifest(
                shot_id, rendered_files, animation_config
            )
            
            LOG.info(f"Анімація битви створена: {shot_id}")
            return {
                'shot_id': shot_id,
                'status': 'success',
                'rendered_files': rendered_files,
                'manifest': manifest,
                'animation_config': animation_config
            }
            
        except Exception as e:
            LOG.error(f"Помилка створення анімації битви: {e}")
            return {'shot_id': shot_id, 'status': 'error', 'error': str(e)}
    
    def create_building_construction_animation(self, shot_id: str) -> Dict[str, Any]:
        """
        Створює анімацію будівництва споруди.
        
        Args:
            shot_id: Ідентифікатор шоту
        
        Returns:
            Конфігурація анімації
        """
        try:
            # Очищення сцени
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            
            # Створення території
            bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
            terrain = bpy.context.active_object
            terrain.name = "ConstructionTerrain"
            
            # Створення будівлі
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            building = bpy.context.active_object
            building.name = "CommandCenter"
            
            # Матеріал будівлі
            building_mat = bpy.data.materials.new(name="BuildingMaterial")
            building_mat.use_nodes = True
            building_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.9, 1.0)
            building_mat.node_tree.nodes["Principled BSDF"].inputs[6].default_value = 0.8  # Metallic
            building_mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.2  # Roughness
            building.data.materials.append(building_mat)
            
            # Анімація будівництва - масштабування знизу вгору
            keyframes = [
                {'frame': 1, 'type': 'scale', 'value': Vector((1, 1, 0.1))},
                {'frame': 30, 'type': 'scale', 'value': Vector((1, 1, 0.3))},
                {'frame': 60, 'type': 'scale', 'value': Vector((1, 1, 0.7))},
                {'frame': 90, 'type': 'scale', 'value': Vector((1, 1, 1.0))}
            ]
            self.keyframe_manager.add_keyframes_sequence(building, keyframes)
            
            # Створення камери
            bpy.ops.object.camera_add(location=(0, -8, 4))
            camera = bpy.context.active_object
            camera.name = "ConstructionCamera"
            camera.rotation_euler = (45, 0, 0)
            
            # Анімація камери - спіральний рух
            curve = self.camera_animator.create_helical_camera_path(
                Vector((0, 0, 0)), 12.0, 2.0, 6.0, 1, "ConstructionCameraPath"
            )
            self.camera_animator.animate_camera_along_curve(
                camera, curve, 1, 90, True
            )
            
            # Налаштування освітлення
            bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
            sun = bpy.context.active_object
            sun.name = "ConstructionSun"
            sun.data.energy = 2.5
            
            # Налаштування рендерингу
            render_settings = {
                'engine': 'CYCLES',
                'samples': 256,
                'resolution': [1920, 1080],
                'output_format': 'PNG',
                'denoising': True
            }
            
            # Рендеринг анімації
            rendered_files = self.sequence_renderer.render_animation_sequence(
                shot_id, 1, 90, render_settings
            )
            
            # Створення маніфесту
            animation_config = {
                'type': 'construction',
                'building_type': 'CommandCenter',
                'camera_path': 'helical',
                'duration': 90
            }
            
            manifest = self.sequence_renderer.create_animation_manifest(
                shot_id, rendered_files, animation_config
            )
            
            LOG.info(f"Анімація будівництва створена: {shot_id}")
            return {
                'shot_id': shot_id,
                'status': 'success',
                'rendered_files': rendered_files,
                'manifest': manifest,
                'animation_config': animation_config
            }
            
        except Exception as e:
            LOG.error(f"Помилка створення анімації будівництва: {e}")
            return {'shot_id': shot_id, 'status': 'error', 'error': str(e)}
    
    def create_cinematic_camera_animation(self, shot_id: str) -> Dict[str, Any]:
        """
        Створює кінематографічну анімацію камери.
        
        Args:
            shot_id: Ідентифікатор шоту
        
        Returns:
            Конфігурація анімації
        """
        try:
            # Очищення сцени
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False)
            
            # Створення ландшафту
            bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
            terrain = bpy.context.active_object
            terrain.name = "CinematicTerrain"
            
            # Додавання рельєфу
            bpy.ops.object.modifier_add(type='SUBSURF')
            terrain.modifiers["SubdivisionSurface"].levels = 2
            
            # Створення об'єктів сцени
            objects = []
            for i in range(3):
                bpy.ops.mesh.primitive_cube_add(location=(i * 5 - 5, 0, 1))
                obj = bpy.context.active_object
                obj.name = f"SceneObject_{i+1}"
                obj.scale = (1, 1, 2)
                objects.append(obj)
            
            # Створення камери
            bpy.ops.object.camera_add(location=(0, -20, 10))
            camera = bpy.context.active_object
            camera.name = "CinematicCamera"
            
            # Складний шлях камери
            camera_points = [
                Vector((-15, -20, 8)),   # Початок
                Vector((-10, -15, 12)),  # Підйом
                Vector((0, -10, 15)),    # Центр
                Vector((10, -5, 12)),    # Спуск
                Vector((15, 0, 8))       # Кінець
            ]
            
            curve = self.camera_animator.create_camera_path(
                camera_points, "CinematicCameraPath"
            )
            self.camera_animator.animate_camera_along_curve(
                camera, curve, 1, 120, True
            )
            
            # Анімація FOV камери
            fov_keyframes = [
                {'frame': 1, 'type': 'fov', 'value': 50},
                {'frame': 30, 'type': 'fov', 'value': 35},
                {'frame': 60, 'type': 'fov', 'value': 25},
                {'frame': 90, 'type': 'fov', 'value': 35},
                {'frame': 120, 'type': 'fov', 'value': 50}
            ]
            self.keyframe_manager.add_keyframes_sequence(camera, fov_keyframes)
            
            # Налаштування освітлення
            bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
            sun = bpy.context.active_object
            sun.name = "CinematicSun"
            sun.data.energy = 4.0
            
            # Додаткове освітлення
            bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
            area_light = bpy.context.active_object
            area_light.name = "FillLight"
            area_light.data.energy = 1.0
            area_light.data.color = (0.9, 0.9, 1.0)
            
            # Налаштування рендерингу
            render_settings = {
                'engine': 'CYCLES',
                'samples': 512,
                'resolution': [1920, 1080],
                'output_format': 'PNG',
                'denoising': True
            }
            
            # Рендеринг анімації
            rendered_files = self.sequence_renderer.render_animation_sequence(
                shot_id, 1, 120, render_settings
            )
            
            # Створення маніфесту
            animation_config = {
                'type': 'cinematic',
                'camera_path': 'custom',
                'fov_animation': True,
                'duration': 120
            }
            
            manifest = self.sequence_renderer.create_animation_manifest(
                shot_id, rendered_files, animation_config
            )
            
            LOG.info(f"Кінематографічна анімація створена: {shot_id}")
            return {
                'shot_id': shot_id,
                'status': 'success',
                'rendered_files': rendered_files,
                'manifest': manifest,
                'animation_config': animation_config
            }
            
        except Exception as e:
            LOG.error(f"Помилка створення кінематографічної анімації: {e}")
            return {'shot_id': shot_id, 'status': 'error', 'error': str(e)}
    
    def create_animation_config_template(self, template_name: str) -> Dict[str, Any]:
        """
        Створює шаблон конфігурації анімації.
        
        Args:
            template_name: Назва шаблону
        
        Returns:
            Шаблон конфігурації
        """
        templates = {
            'battle_sequence': {
                'name': 'Battle Sequence',
                'description': 'Анімація битви з рухом одиниць',
                'duration': 100,
                'camera': {
                    'type': 'circular',
                    'radius': 20.0,
                    'height': 8.0
                },
                'units': {
                    'count': 5,
                    'movement': 'forward_advance'
                },
                'render_settings': {
                    'engine': 'CYCLES',
                    'samples': 128,
                    'resolution': [1920, 1080]
                }
            },
            'building_construction': {
                'name': 'Building Construction',
                'description': 'Анімація будівництва споруди',
                'duration': 90,
                'camera': {
                    'type': 'helical',
                    'radius': 12.0,
                    'height_start': 2.0,
                    'height_end': 6.0,
                    'turns': 1
                },
                'building': {
                    'type': 'CommandCenter',
                    'scale_animation': True
                },
                'render_settings': {
                    'engine': 'CYCLES',
                    'samples': 256,
                    'resolution': [1920, 1080]
                }
            },
            'cinematic_shot': {
                'name': 'Cinematic Shot',
                'description': 'Кінематографічна анімація камери',
                'duration': 120,
                'camera': {
                    'type': 'custom_path',
                    'points': [
                        [-15, -20, 8],
                        [-10, -15, 12],
                        [0, -10, 15],
                        [10, -5, 12],
                        [15, 0, 8]
                    ],
                    'fov_animation': True
                },
                'render_settings': {
                    'engine': 'CYCLES',
                    'samples': 512,
                    'resolution': [1920, 1080]
                }
            }
        }
        
        return templates.get(template_name, {})
    
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
                animation_type = shot_config.get('type', 'battle')
                
                LOG.info(f"Створення анімації: {shot_id} ({animation_type})")
                
                if animation_type == 'battle':
                    result = self.create_battle_animation(shot_id)
                elif animation_type == 'construction':
                    result = self.create_building_construction_animation(shot_id)
                elif animation_type == 'cinematic':
                    result = self.create_cinematic_camera_animation(shot_id)
                else:
                    result = {'shot_id': shot_id, 'status': 'error', 'error': f'Невідомий тип анімації: {animation_type}'}
                
                results[shot_id] = result
            
            # Підсумкова статистика
            successful = sum(1 for r in results.values() if r.get('status') == 'success')
            failed = sum(1 for r in results.values() if r.get('status') == 'error')
            
            LOG.info(f"Пакетне створення анімацій завершено: {successful} успішних, {failed} помилок")
            
            return results
            
        except Exception as e:
            LOG.error(f"Помилка пакетного створення анімацій: {e}")
            raise


def create_animation_panel_ui():
    """Створює UI панель для системи анімації."""
    try:
        # Створення панелі в 3D Viewport
        class SCBW_PT_AnimationPanel(bpy.types.Panel):
            bl_label = "SCBW Animation"
            bl_idname = "SCBW_PT_animation_panel"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = "SCBW"
            
            def draw(self, context):
                layout = self.layout
                
                # Заголовок
                box = layout.box()
                box.label(text="Animation System", icon='ANIM')
                
                # Кнопки створення анімацій
                animation_box = box.box()
                animation_box.label(text="Create Animations")
                
                row = animation_box.row()
                row.operator("scbw.create_battle_animation", text="Battle")
                row.operator("scbw.create_construction_animation", text="Construction")
                
                row = animation_box.row()
                row.operator("scbw.create_cinematic_animation", text="Cinematic")
                
                # Налаштування рендерингу
                render_box = box.box()
                render_box.label(text="Render Settings")
                
                row = render_box.row()
                row.prop(context.scene.render, "engine", text="Engine")
                
                if context.scene.render.engine == 'CYCLES':
                    row = render_box.row()
                    row.prop(context.scene.cycles, "samples", text="Samples")
                
                # Кнопка рендерингу
                render_box.operator("scbw.render_animation_sequence", text="Render Animation")
        
        # Реєстрація панелі
        bpy.utils.register_class(SCBW_PT_AnimationPanel)
        
        LOG.info("UI панель анімації створена")
        
    except Exception as e:
        LOG.error(f"Помилка створення UI панелі: {e}")


# Оператори для UI
class SCBW_OT_CreateBattleAnimation(bpy.types.Operator):
    """Створює анімацію битви."""
    bl_idname = "scbw.create_battle_animation"
    bl_label = "Create Battle Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            examples = AnimationExamples()
            result = examples.create_battle_animation("battle_shot_001")
            
            if result['status'] == 'success':
                self.report({'INFO'}, f"Анімація битви створена: {len(result['rendered_files'])} кадрів")
            else:
                self.report({'ERROR'}, f"Помилка створення анімації: {result.get('error', 'Unknown error')}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка: {e}")
            return {'CANCELLED'}


class SCBW_OT_CreateConstructionAnimation(bpy.types.Operator):
    """Створює анімацію будівництва."""
    bl_idname = "scbw.create_construction_animation"
    bl_label = "Create Construction Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            examples = AnimationExamples()
            result = examples.create_building_construction_animation("construction_shot_001")
            
            if result['status'] == 'success':
                self.report({'INFO'}, f"Анімація будівництва створена: {len(result['rendered_files'])} кадрів")
            else:
                self.report({'ERROR'}, f"Помилка створення анімації: {result.get('error', 'Unknown error')}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка: {e}")
            return {'CANCELLED'}


class SCBW_OT_CreateCinematicAnimation(bpy.types.Operator):
    """Створює кінематографічну анімацію."""
    bl_idname = "scbw.create_cinematic_animation"
    bl_label = "Create Cinematic Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            examples = AnimationExamples()
            result = examples.create_cinematic_camera_animation("cinematic_shot_001")
            
            if result['status'] == 'success':
                self.report({'INFO'}, f"Кінематографічна анімація створена: {len(result['rendered_files'])} кадрів")
            else:
                self.report({'ERROR'}, f"Помилка створення анімації: {result.get('error', 'Unknown error')}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Помилка: {e}")
            return {'CANCELLED'}


# Реєстрація операторів
def register_animation_operators():
    """Реєструє оператори анімації."""
    bpy.utils.register_class(SCBW_OT_CreateBattleAnimation)
    bpy.utils.register_class(SCBW_OT_CreateConstructionAnimation)
    bpy.utils.register_class(SCBW_OT_CreateCinematicAnimation)


def unregister_animation_operators():
    """Скасовує реєстрацію операторів анімації."""
    bpy.utils.unregister_class(SCBW_OT_CreateBattleAnimation)
    bpy.utils.unregister_class(SCBW_OT_CreateConstructionAnimation)
    bpy.utils.unregister_class(SCBW_OT_CreateCinematicAnimation)


if __name__ == "__main__":
    # Тестування прикладів анімації
    logging.basicConfig(level=logging.INFO)
    
    examples = AnimationExamples()
    
    # Створення анімації битви
    print("Створення анімації битви...")
    battle_result = examples.create_battle_animation("test_battle_001")
    print(f"Результат: {battle_result['status']}")
    
    # Створення анімації будівництва
    print("Створення анімації будівництва...")
    construction_result = examples.create_building_construction_animation("test_construction_001")
    print(f"Результат: {construction_result['status']}")
    
    # Створення кінематографічної анімації
    print("Створення кінематографічної анімації...")
    cinematic_result = examples.create_cinematic_camera_animation("test_cinematic_001")
    print(f"Результат: {cinematic_result['status']}")
    
    print("Приклади анімації протестовані успішно!")