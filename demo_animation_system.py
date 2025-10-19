#!/usr/bin/env python3
"""
Демонстраційний скрипт системи анімації для Blender SCBW pipeline
Показує всі можливості: ключові кадри, криві камери, рендеринг послідовностей
"""

import bpy
import sys
from pathlib import Path
import logging

# Додавання шляху до модулів
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "blender"))

# Імпорт системи анімації
from animation_system import (
    KeyframeManager,
    CameraCurveAnimator,
    AnimationSequenceRenderer
)
from animation_examples import AnimationExamples
from integrated_animation_pipeline import IntegratedAnimationPipeline

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_keyframe_animation():
    """Демонстрація анімації ключовими кадрами."""
    print("\n=== Демонстрація анімації ключовими кадрами ===")
    
    # Очищення сцени
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Створення куба
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "AnimatedCube"
    
    # Створення менеджера ключових кадрів
    keyframe_manager = KeyframeManager()
    
    # Анімація позиції
    position_keyframes = [
        {'frame': 1, 'type': 'location', 'value': (0, 0, 0)},
        {'frame': 30, 'type': 'location', 'value': (5, 0, 0)},
        {'frame': 60, 'type': 'location', 'value': (5, 5, 0)},
        {'frame': 90, 'type': 'location', 'value': (0, 5, 0)},
        {'frame': 120, 'type': 'location', 'value': (0, 0, 0)}
    ]
    keyframe_manager.add_keyframes_sequence(cube, position_keyframes)
    
    # Анімація обертання
    rotation_keyframes = [
        {'frame': 1, 'type': 'rotation', 'value': (0, 0, 0)},
        {'frame': 60, 'type': 'rotation', 'value': (0, 0, 3.14159)},
        {'frame': 120, 'type': 'rotation', 'value': (0, 0, 6.28318)}
    ]
    keyframe_manager.add_keyframes_sequence(cube, rotation_keyframes)
    
    # Анімація масштабу
    scale_keyframes = [
        {'frame': 1, 'type': 'scale', 'value': (1, 1, 1)},
        {'frame': 30, 'type': 'scale', 'value': (1.5, 1.5, 1.5)},
        {'frame': 60, 'type': 'scale', 'value': (1, 1, 1)},
        {'frame': 90, 'type': 'scale', 'value': (0.5, 0.5, 0.5)},
        {'frame': 120, 'type': 'scale', 'value': (1, 1, 1)}
    ]
    keyframe_manager.add_keyframes_sequence(cube, scale_keyframes)
    
    # Встановлення інтерполяції
    keyframe_manager.set_interpolation(cube, 'BEZIER')
    
    print("✓ Анімація ключовими кадрами створена")
    print("  - Позиція: квадратний рух")
    print("  - Обертання: повний оберт")
    print("  - Масштаб: пульсація")


def demo_camera_curves():
    """Демонстрація анімації камери по кривим."""
    print("\n=== Демонстрація анімації камери по кривим ===")
    
    # Створення аніматора камери
    camera_animator = CameraCurveAnimator()
    
    # Створення камери
    bpy.ops.object.camera_add(location=(0, -10, 5))
    camera = bpy.context.active_object
    camera.name = "CurveCamera"
    
    # 1. Кругова крива
    print("Створення кругової кривої камери...")
    circular_curve = camera_animator.create_circular_camera_path(
        Vector((0, 0, 0)), 15.0, 8.0, "CircularPath"
    )
    camera_animator.animate_camera_along_curve(
        camera, circular_curve, 1, 100, True
    )
    print("✓ Кругова крива створена")
    
    # 2. Спіральна крива
    print("Створення спіральної кривої камери...")
    helical_curve = camera_animator.create_helical_camera_path(
        Vector((0, 0, 0)), 12.0, 2.0, 10.0, 2, "HelicalPath"
    )
    print("✓ Спіральна крива створена")
    
    # 3. Кастомна крива
    print("Створення кастомної кривої камери...")
    custom_points = [
        Vector((-10, -15, 5)),
        Vector((-5, -10, 8)),
        Vector((0, -5, 10)),
        Vector((5, 0, 8)),
        Vector((10, 5, 5))
    ]
    custom_curve = camera_animator.create_camera_path(custom_points, "CustomPath")
    print("✓ Кастомна крива створена")


def demo_sequence_rendering():
    """Демонстрація рендерингу послідовностей."""
    print("\n=== Демонстрація рендерингу послідовностей ===")
    
    # Створення рендерера послідовностей
    output_dir = Path("renders/blender/demo")
    sequence_renderer = AnimationSequenceRenderer(output_dir)
    
    # Налаштування таймлайну
    sequence_renderer.setup_animation_timeline(1, 50, 24)
    print("✓ Таймлайн налаштовано: 1-50 кадрів, 24 FPS")
    
    # Налаштування рендерингу
    render_settings = {
        'engine': 'CYCLES',
        'samples': 64,  # Швидкий рендеринг для демо
        'resolution': [1280, 720],
        'output_format': 'PNG',
        'denoising': True
    }
    
    # Рендеринг анімації
    print("Рендеринг анімації...")
    rendered_files = sequence_renderer.render_animation_sequence(
        "demo_sequence", 1, 50, render_settings
    )
    print(f"✓ Рендеринг завершено: {len(rendered_files)} кадрів")
    
    # Створення маніфесту
    animation_config = {
        'type': 'demo',
        'duration': 50,
        'camera_path': 'mixed'
    }
    manifest = sequence_renderer.create_animation_manifest(
        "demo_sequence", rendered_files, animation_config
    )
    print("✓ Маніфест анімації створено")


def demo_animation_examples():
    """Демонстрація прикладів анімації."""
    print("\n=== Демонстрація прикладів анімації ===")
    
    examples = AnimationExamples()
    
    # 1. Анімація битви
    print("Створення анімації битви...")
    battle_result = examples.create_battle_animation("demo_battle")
    if battle_result['status'] == 'success':
        print(f"✓ Анімація битви: {len(battle_result['rendered_files'])} кадрів")
    else:
        print(f"✗ Помилка анімації битви: {battle_result.get('error')}")
    
    # 2. Анімація будівництва
    print("Створення анімації будівництва...")
    construction_result = examples.create_building_construction_animation("demo_construction")
    if construction_result['status'] == 'success':
        print(f"✓ Анімація будівництва: {len(construction_result['rendered_files'])} кадрів")
    else:
        print(f"✗ Помилка анімації будівництва: {construction_result.get('error')}")
    
    # 3. Кінематографічна анімація
    print("Створення кінематографічної анімації...")
    cinematic_result = examples.create_cinematic_camera_animation("demo_cinematic")
    if cinematic_result['status'] == 'success':
        print(f"✓ Кінематографічна анімація: {len(cinematic_result['rendered_files'])} кадрів")
    else:
        print(f"✗ Помилка кінематографічної анімації: {cinematic_result.get('error')}")


def demo_integrated_pipeline():
    """Демонстрація інтегрованого пайплайну."""
    print("\n=== Демонстрація інтегрованого пайплайну ===")
    
    # Ініціалізація пайплайну
    pipeline = IntegratedAnimationPipeline()
    
    # Створення анімації з шаблону
    print("Створення анімації з шаблону...")
    shot_result = pipeline.create_shot_from_template(
        "battle_sequence",
        "demo_integrated_001",
        {
            'units': {'count': 3},
            'camera': {'radius': 15.0, 'height': 6.0},
            'render_settings': {'samples': 32}  # Швидкий рендеринг
        }
    )
    
    if shot_result['status'] == 'success':
        print(f"✓ Інтегрована анімація: {len(shot_result['rendered_files'])} кадрів")
    else:
        print(f"✗ Помилка інтегрованої анімації: {shot_result.get('error')}")
    
    # Пакетне створення
    print("Пакетне створення анімацій...")
    batch_config = [
        {
            'shot_id': 'batch_demo_001',
            'template': 'battle_sequence',
            'custom_settings': {'units': {'count': 2}}
        },
        {
            'shot_id': 'batch_demo_002',
            'template': 'building_construction',
            'custom_settings': {'building': {'type': 'Factory'}}
        }
    ]
    
    batch_results = pipeline.batch_create_animations(batch_config)
    successful = sum(1 for r in batch_results.values() if r.get('status') == 'success')
    print(f"✓ Пакетне створення: {successful}/{len(batch_results)} успішних")
    
    # Експорт
    print("Експорт анімації...")
    try:
        export_path = pipeline.export_animation("demo_integrated_001", "blend")
        print(f"✓ Анімація експортована: {export_path}")
    except Exception as e:
        print(f"✗ Помилка експорту: {e}")


def demo_advanced_features():
    """Демонстрація розширених можливостей."""
    print("\n=== Демонстрація розширених можливостей ===")
    
    # Очищення сцени
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Створення складної сцени
    print("Створення складної сцени...")
    
    # Територія
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    terrain = bpy.context.active_object
    terrain.name = "AdvancedTerrain"
    
    # Об'єкти з різними анімаціями
    objects = []
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(location=(i * 3 - 6, 0, 0.5))
        obj = bpy.context.active_object
        obj.name = f"AdvancedObject_{i+1}"
        obj.scale = (0.8, 0.8, 1.0)
        objects.append(obj)
    
    # Створення менеджера ключових кадрів
    keyframe_manager = KeyframeManager()
    
    # Різні типи анімації для кожного об'єкта
    animation_types = [
        'bounce', 'elastic', 'back', 'circular', 'cubic'
    ]
    
    for i, obj in enumerate(objects):
        animation_type = animation_types[i % len(animation_types)]
        
        # Анімація позиції з різними інтерполяціями
        keyframes = [
            {'frame': 1, 'type': 'location', 'value': (i * 3 - 6, 0, 0.5)},
            {'frame': 30, 'type': 'location', 'value': (i * 3 - 6, 5, 2.0)},
            {'frame': 60, 'type': 'location', 'value': (i * 3 - 6, -5, 2.0)},
            {'frame': 90, 'type': 'location', 'value': (i * 3 - 6, 0, 0.5)}
        ]
        keyframe_manager.add_keyframes_sequence(obj, keyframes)
        keyframe_manager.set_interpolation(obj, animation_type.upper())
    
    # Створення камери зі складним шляхом
    camera_animator = CameraCurveAnimator()
    
    # Складний шлях камери
    camera_points = [
        Vector((-15, -20, 8)),
        Vector((-10, -15, 12)),
        Vector((0, -10, 15)),
        Vector((10, -5, 12)),
        Vector((15, 0, 8)),
        Vector((10, 5, 6)),
        Vector((0, 10, 4)),
        Vector((-10, 5, 6)),
        Vector((-15, 0, 8))
    ]
    
    bpy.ops.object.camera_add(location=camera_points[0])
    camera = bpy.context.active_object
    camera.name = "AdvancedCamera"
    
    curve = camera_animator.create_camera_path(camera_points, "AdvancedCameraPath")
    camera_animator.animate_camera_along_curve(camera, curve, 1, 120, True)
    
    # Анімація FOV камери
    fov_keyframes = [
        {'frame': 1, 'type': 'fov', 'value': 50},
        {'frame': 30, 'type': 'fov', 'value': 35},
        {'frame': 60, 'type': 'fov', 'value': 25},
        {'frame': 90, 'type': 'fov', 'value': 35},
        {'frame': 120, 'type': 'fov', 'value': 50}
    ]
    keyframe_manager.add_keyframes_sequence(camera, fov_keyframes)
    
    # Налаштування освітлення
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.active_object
    sun.name = "AdvancedSun"
    sun.data.energy = 4.0
    
    # Додаткове освітлення
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    area_light = bpy.context.active_object
    area_light.name = "AdvancedFillLight"
    area_light.data.energy = 1.5
    area_light.data.color = (0.9, 0.9, 1.0)
    
    print("✓ Складна сцена створена")
    print("  - 5 об'єктів з різними анімаціями")
    print("  - Складний шлях камери")
    print("  - Анімація FOV")
    print("  - Множинне освітлення")


def main():
    """Головна функція демонстрації."""
    print("🎬 Демонстрація системи анімації Blender SCBW Pipeline")
    print("=" * 60)
    
    try:
        # Демонстрація основних компонентів
        demo_keyframe_animation()
        demo_camera_curves()
        demo_sequence_rendering()
        
        # Демонстрація прикладів
        demo_animation_examples()
        
        # Демонстрація інтегрованого пайплайну
        demo_integrated_pipeline()
        
        # Демонстрація розширених можливостей
        demo_advanced_features()
        
        print("\n" + "=" * 60)
        print("✅ Всі демонстрації завершено успішно!")
        print("\nСтворені файли:")
        print("- renders/blender/demo/ - демонстраційні рендери")
        print("- renders/blender/animation/ - анімаційні послідовності")
        print("- assets/animations/ - конфігурації анімацій")
        
        print("\nМожливості системи:")
        print("✓ Анімація ключовими кадрами")
        print("✓ Криві камери (кругові, спіральні, кастомні)")
        print("✓ Рендеринг послідовностей")
        print("✓ Шаблони анімацій")
        print("✓ Пакетне створення")
        print("✓ Експорт у різні формати")
        print("✓ Розширені налаштування рендерингу")
        
    except Exception as e:
        print(f"\n❌ Помилка демонстрації: {e}")
        logger.error(f"Помилка демонстрації: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())