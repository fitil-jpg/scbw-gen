#!/usr/bin/env python3
"""
Тестовий скрипт для системи анімації Blender SCBW Pipeline
Перевіряє основні функції без повного рендерингу
"""

import bpy
import sys
from pathlib import Path
import logging

# Додавання шляху до модулів
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "blender"))

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_keyframe_manager():
    """Тестує менеджер ключових кадрів."""
    print("🧪 Тестування KeyframeManager...")
    
    try:
        from animation_system import KeyframeManager
        
        # Очищення сцени
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Створення тестового об'єкта
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.name = "TestCube"
        
        # Створення менеджера
        keyframe_manager = KeyframeManager()
        
        # Тест анімації позиції
        keyframes = [
            {'frame': 1, 'type': 'location', 'value': (0, 0, 0)},
            {'frame': 30, 'type': 'location', 'value': (5, 0, 0)},
            {'frame': 60, 'type': 'location', 'value': (5, 5, 0)},
            {'frame': 90, 'type': 'location', 'value': (0, 5, 0)},
            {'frame': 120, 'type': 'location', 'value': (0, 0, 0)}
        ]
        keyframe_manager.add_keyframes_sequence(cube, keyframes)
        
        # Тест анімації обертання
        rotation_keyframes = [
            {'frame': 1, 'type': 'rotation', 'value': (0, 0, 0)},
            {'frame': 60, 'type': 'rotation', 'value': (0, 0, 3.14159)},
            {'frame': 120, 'type': 'rotation', 'value': (0, 0, 6.28318)}
        ]
        keyframe_manager.add_keyframes_sequence(cube, rotation_keyframes)
        
        # Тест інтерполяції
        keyframe_manager.set_interpolation(cube, 'BEZIER')
        
        print("✅ KeyframeManager: PASS")
        return True
        
    except Exception as e:
        print(f"❌ KeyframeManager: FAIL - {e}")
        logger.error(f"KeyframeManager test failed: {e}")
        return False


def test_camera_animator():
    """Тестує аніматор камери."""
    print("🧪 Тестування CameraCurveAnimator...")
    
    try:
        from animation_system import CameraCurveAnimator
        from mathutils import Vector
        
        # Очищення сцени
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Створення камери
        bpy.ops.object.camera_add(location=(0, -10, 5))
        camera = bpy.context.active_object
        camera.name = "TestCamera"
        
        # Створення аніматора
        camera_animator = CameraCurveAnimator()
        
        # Тест кругової кривої
        circular_curve = camera_animator.create_circular_camera_path(
            Vector((0, 0, 0)), 10.0, 5.0, "TestCircularPath"
        )
        
        # Тест спіральної кривої
        helical_curve = camera_animator.create_helical_camera_path(
            Vector((0, 0, 0)), 8.0, 2.0, 8.0, 1, "TestHelicalPath"
        )
        
        # Тест кастомної кривої
        custom_points = [
            Vector((-5, -10, 3)),
            Vector((0, -5, 5)),
            Vector((5, 0, 3))
        ]
        custom_curve = camera_animator.create_camera_path(custom_points, "TestCustomPath")
        
        # Тест анімації камери
        camera_animator.animate_camera_along_curve(
            camera, circular_curve, 1, 50, True
        )
        
        print("✅ CameraCurveAnimator: PASS")
        return True
        
    except Exception as e:
        print(f"❌ CameraCurveAnimator: FAIL - {e}")
        logger.error(f"CameraCurveAnimator test failed: {e}")
        return False


def test_sequence_renderer():
    """Тестує рендерер послідовностей."""
    print("🧪 Тестування AnimationSequenceRenderer...")
    
    try:
        from animation_system import AnimationSequenceRenderer
        
        # Створення рендерера
        output_dir = Path("test_renders")
        sequence_renderer = AnimationSequenceRenderer(output_dir)
        
        # Тест налаштування таймлайну
        sequence_renderer.setup_animation_timeline(1, 10, 24)
        
        # Перевірка налаштувань сцени
        scene = bpy.context.scene
        assert scene.frame_start == 1
        assert scene.frame_end == 10
        assert scene.render.fps == 24
        
        print("✅ AnimationSequenceRenderer: PASS")
        return True
        
    except Exception as e:
        print(f"❌ AnimationSequenceRenderer: FAIL - {e}")
        logger.error(f"AnimationSequenceRenderer test failed: {e}")
        return False


def test_animation_examples():
    """Тестує приклади анімації."""
    print("🧪 Тестування AnimationExamples...")
    
    try:
        from animation_examples import AnimationExamples
        
        # Створення прикладів
        examples = AnimationExamples()
        
        # Тест створення шаблонів
        battle_template = examples.create_animation_config_template('battle_sequence')
        construction_template = examples.create_animation_config_template('building_construction')
        cinematic_template = examples.create_animation_config_template('cinematic_shot')
        
        # Перевірка шаблонів
        assert 'name' in battle_template
        assert 'duration' in battle_template
        assert 'camera' in battle_template
        
        assert 'name' in construction_template
        assert 'duration' in construction_template
        assert 'building' in construction_template
        
        assert 'name' in cinematic_template
        assert 'duration' in cinematic_template
        assert 'camera' in cinematic_template
        
        print("✅ AnimationExamples: PASS")
        return True
        
    except Exception as e:
        print(f"❌ AnimationExamples: FAIL - {e}")
        logger.error(f"AnimationExamples test failed: {e}")
        return False


def test_integrated_pipeline():
    """Тестує інтегрований пайплайн."""
    print("🧪 Тестування IntegratedAnimationPipeline...")
    
    try:
        from integrated_animation_pipeline import IntegratedAnimationPipeline
        
        # Створення пайплайну
        pipeline = IntegratedAnimationPipeline()
        
        # Тест завантаження конфігурації
        config = pipeline.config
        assert isinstance(config, dict)
        
        # Тест створення шаблону
        template = pipeline.create_animation_config_template('battle_sequence')
        assert 'name' in template
        assert 'duration' in template
        
        print("✅ IntegratedAnimationPipeline: PASS")
        return True
        
    except Exception as e:
        print(f"❌ IntegratedAnimationPipeline: FAIL - {e}")
        logger.error(f"IntegratedAnimationPipeline test failed: {e}")
        return False


def test_blender_operators():
    """Тестує оператори Blender."""
    print("🧪 Тестування Blender Operators...")
    
    try:
        from animation_system import (
            SCBW_OT_CreateCircularCameraPath,
            SCBW_OT_CreateHelicalCameraPath,
            SCBW_OT_RenderAnimationSequence
        )
        
        # Перевірка існування операторів
        assert hasattr(SCBW_OT_CreateCircularCameraPath, 'bl_idname')
        assert hasattr(SCBW_OT_CreateHelicalCameraPath, 'bl_idname')
        assert hasattr(SCBW_OT_RenderAnimationSequence, 'bl_idname')
        
        # Перевірка властивостей
        assert hasattr(SCBW_OT_CreateCircularCameraPath, 'radius')
        assert hasattr(SCBW_OT_CreateHelicalCameraPath, 'radius')
        
        print("✅ Blender Operators: PASS")
        return True
        
    except Exception as e:
        print(f"❌ Blender Operators: FAIL - {e}")
        logger.error(f"Blender Operators test failed: {e}")
        return False


def run_all_tests():
    """Запускає всі тести."""
    print("🚀 Запуск тестів системи анімації...")
    print("=" * 50)
    
    tests = [
        test_keyframe_manager,
        test_camera_animator,
        test_sequence_renderer,
        test_animation_examples,
        test_integrated_pipeline,
        test_blender_operators
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: EXCEPTION - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результати тестування:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Успішність: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Всі тести пройдено успішно!")
        return True
    else:
        print(f"\n⚠️  {failed} тестів провалено")
        return False


def main():
    """Головна функція тестування."""
    try:
        success = run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Критична помилка: {e}")
        logger.error(f"Critical error in main: {e}")
        return 1


if __name__ == "__main__":
    exit(main())