"""Приклади використання Blender SCBW pipeline."""

from __future__ import annotations

import sys
from pathlib import Path
import logging

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent.parent))

from blender.advanced_config_importer import AdvancedConfigImporter, create_sample_config
from blender.advanced_geometry_generator import AdvancedGeometryGenerator
from blender.advanced_render_pipeline import AdvancedMultiPassRenderer, EeveeRenderer, CyclesRenderer

LOG = logging.getLogger(__name__)


def example_basic_usage():
    """Базовий приклад використання pipeline."""
    print("=== Базовий приклад використання ===")
    
    # 1. Створення прикладу конфігурації
    config_path = Path("example_config.yaml")
    create_sample_config(config_path)
    print(f"✓ Створено приклад конфігурації: {config_path}")
    
    # 2. Завантаження конфігурації
    importer = AdvancedConfigImporter(config_path)
    config = importer.load_config()
    assets = importer.load_asset_configs()
    print(f"✓ Завантажено конфігурацію з {len(config.get('shots', []))} шотами")
    
    # 3. Валідація конфігурації
    errors = importer.validate_config()
    if errors:
        print("⚠ Помилки в конфігурації:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Конфігурація валідна")
    
    # 4. Отримання шоту
    shot_config = importer.get_shot_config('demo_shot_001')
    if shot_config:
        print(f"✓ Знайдено шот: {shot_config['id']}")
        print(f"  - Палітра: {shot_config.get('palette', 'N/A')}")
        print(f"  - Лівий кластер: {shot_config.get('left_cluster', {}).get('count', 0)} юнітів")
        print(f"  - Правий кластер: {shot_config.get('right_cluster', {}).get('count', 0)} юнітів")
    else:
        print("✗ Шот не знайдено")
        return
    
    # 5. Експорт зведення
    summary_path = Path("config_summary.json")
    importer.export_config_summary(summary_path)
    print(f"✓ Зведення експортовано: {summary_path}")
    
    return importer, shot_config


def example_geometry_generation(importer, shot_config):
    """Приклад генерації геометрії."""
    print("\n=== Генерація геометрії ===")
    
    try:
        # Імпорт Blender API
        import bpy
        
        # Створення генератора геометрії
        generator = AdvancedGeometryGenerator(importer)
        print("✓ Генератор геометрії створено")
        
        # Генерація сцени
        generator.setup_advanced_scene(shot_config)
        print("✓ Розширена сцена створена")
        
        # Перевірка створених об'єктів
        scene_objects = [obj.name for obj in bpy.context.scene.objects]
        print(f"✓ Створено {len(scene_objects)} об'єктів у сцені")
        
        # Групування об'єктів за типом
        units = [obj for obj in scene_objects if 'Unit' in obj]
        buildings = [obj for obj in scene_objects if 'Building' in obj]
        terrain = [obj for obj in scene_objects if 'Terrain' in obj]
        
        print(f"  - Юніти: {len(units)}")
        print(f"  - Будівлі: {len(buildings)}")
        print(f"  - Територія: {len(terrain)}")
        
        return generator
        
    except ImportError:
        print("⚠ Blender API недоступний - пропускаємо генерацію геометрії")
        return None


def example_rendering(generator, shot_config):
    """Приклад рендерингу."""
    print("\n=== Рендеринг ===")
    
    try:
        import bpy
        
        # Налаштування виводу
        output_dir = Path("example_renders")
        output_dir.mkdir(exist_ok=True)
        
        # Тестування Eevee рендерера
        print("Тестування Eevee рендерера...")
        eevee_renderer = EeveeRenderer(output_dir)
        print("✓ Eevee рендерер створено")
        
        # Тестування Cycles рендерера
        print("Тестування Cycles рендерера...")
        cycles_renderer = CyclesRenderer(output_dir)
        print("✓ Cycles рендерер створено")
        
        # Розширений мульти-пас рендерер
        advanced_renderer = AdvancedMultiPassRenderer(output_dir)
        print("✓ Розширений рендерер створено")
        
        # Створення пасів
        passes = advanced_renderer.create_advanced_passes("demo_shot_001", 1)
        print(f"✓ Створено {len(passes)} рендер пасів")
        
        for pass_obj in passes:
            print(f"  - {pass_obj.name}: {pass_obj.output_path}")
        
        return advanced_renderer
        
    except ImportError:
        print("⚠ Blender API недоступний - пропускаємо рендеринг")
        return None


def example_custom_configuration():
    """Приклад створення власної конфігурації."""
    print("\n=== Власна конфігурація ===")
    
    # Створення кастомної конфігурації
    custom_config = {
        'seed': 42,
        'image_size': [1920, 1080],
        'shots': [
            {
                'id': 'custom_battle_001',
                'palette': 'ProtossColors',
                'portal': {
                    'center': [0.3, 0.7],
                    'radius': 0.15,
                    'falloff': 0.3,
                    'invert': False
                },
                'left_cluster': {
                    'rect': [0.05, 0.3],
                    'count': 12,
                    'size': [22, 44],
                    'unit_types': ['zealot', 'dragoon', 'high_templar']
                },
                'right_cluster': {
                    'rect': [0.7, 0.6],
                    'count': 15,
                    'size': [18, 36],
                    'unit_types': ['zergling', 'hydralisk', 'mutalisk']
                },
                'buildings': [
                    {
                        'type': 'nexus',
                        'position': [0.15, 0.15],
                        'owner': 'left'
                    },
                    {
                        'type': 'hatchery',
                        'position': [0.85, 0.85],
                        'owner': 'right'
                    },
                    {
                        'type': 'pylon',
                        'position': [0.2, 0.2],
                        'owner': 'left'
                    }
                ],
                'hud': {
                    'left': {
                        'Race': 'Protoss',
                        'M': 3000,
                        'G': 1500,
                        'Supply': [80, 100],
                        'APM': 180
                    },
                    'right': {
                        'Race': 'Zerg',
                        'M': 2800,
                        'G': 1200,
                        'Supply': [90, 110],
                        'APM': 280
                    }
                },
                'export': {
                    'png': True,
                    'exr16': True,
                    'exr32': True
                }
            }
        ]
    }
    
    # Збереження конфігурації
    import yaml
    custom_config_path = Path("custom_config.yaml")
    with open(custom_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(custom_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✓ Власна конфігурація створена: {custom_config_path}")
    
    # Завантаження та валідація
    importer = AdvancedConfigImporter(custom_config_path)
    config = importer.load_config()
    errors = importer.validate_config()
    
    if errors:
        print("⚠ Помилки в власній конфігурації:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Власна конфігурація валідна")
    
    return importer


def example_batch_processing():
    """Приклад пакетної обробки."""
    print("\n=== Пакетна обробка ===")
    
    # Створення кількох шотів
    batch_config = {
        'seed': 123,
        'image_size': [1280, 720],
        'shots': []
    }
    
    # Генерація 5 різних шотів
    for i in range(5):
        shot = {
            'id': f'batch_shot_{i+1:03d}',
            'palette': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
            'left_cluster': {
                'rect': [0.1, 0.4 + i * 0.1],
                'count': 5 + i * 2,
                'size': [16, 32]
            },
            'right_cluster': {
                'rect': [0.6, 0.5 + i * 0.05],
                'count': 3 + i,
                'size': [18, 36]
            },
            'export': {
                'png': True,
                'exr16': i % 2 == 0
            }
        }
        batch_config['shots'].append(shot)
    
    # Збереження пакетної конфігурації
    import yaml
    batch_path = Path("batch_config.yaml")
    with open(batch_path, 'w', encoding='utf-8') as f:
        yaml.dump(batch_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✓ Пакетна конфігурація створена: {batch_path}")
    print(f"  - Кількість шотів: {len(batch_config['shots'])}")
    
    # Завантаження та обробка
    importer = AdvancedConfigImporter(batch_path)
    config = importer.load_config()
    
    print("✓ Пакетна конфігурація завантажена")
    
    # Симуляція обробки кожного шоту
    for shot in config['shots']:
        print(f"  - Обробка шоту: {shot['id']}")
        print(f"    Лівий кластер: {shot['left_cluster']['count']} юнітів")
        print(f"    Правий кластер: {shot['right_cluster']['count']} юнітів")
    
    return importer


def example_error_handling():
    """Приклад обробки помилок."""
    print("\n=== Обробка помилок ===")
    
    # Тестування неіснуючого файлу
    try:
        importer = AdvancedConfigImporter("nonexistent.yaml")
        config = importer.load_config()
    except FileNotFoundError as e:
        print(f"✓ Правильно оброблено помилку файлу: {e}")
    
    # Тестування невалідної конфігурації
    invalid_config = {
        'shots': [
            {
                'id': 'invalid_shot',
                # Відсутні обов'язкові поля
            }
        ]
    }
    
    import yaml
    invalid_path = Path("invalid_config.yaml")
    with open(invalid_path, 'w', encoding='utf-8') as f:
        yaml.dump(invalid_config, f, default_flow_style=False, allow_unicode=True)
    
    try:
        importer = AdvancedConfigImporter(invalid_path)
        config = importer.load_config()
        errors = importer.validate_config()
        
        if errors:
            print("✓ Валідація виявила помилки:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("⚠ Валідація не виявила помилок (неочікувано)")
            
    except Exception as e:
        print(f"✓ Оброблено неочікувану помилку: {e}")
    
    # Очищення
    if invalid_path.exists():
        invalid_path.unlink()


def main():
    """Головна функція з усіма прикладами."""
    print("🚀 Приклади використання Blender SCBW Pipeline")
    print("=" * 50)
    
    # Налаштування логування
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    
    try:
        # 1. Базовий приклад
        importer, shot_config = example_basic_usage()
        
        # 2. Генерація геометрії
        generator = example_geometry_generation(importer, shot_config)
        
        # 3. Рендеринг
        renderer = example_rendering(generator, shot_config)
        
        # 4. Власна конфігурація
        custom_importer = example_custom_configuration()
        
        # 5. Пакетна обробка
        batch_importer = example_batch_processing()
        
        # 6. Обробка помилок
        example_error_handling()
        
        print("\n" + "=" * 50)
        print("✅ Всі приклади виконано успішно!")
        print("\nСтворені файли:")
        print("  - example_config.yaml")
        print("  - config_summary.json")
        print("  - custom_config.yaml")
        print("  - batch_config.yaml")
        print("  - example_renders/ (директорія)")
        
    except Exception as e:
        print(f"\n❌ Помилка під час виконання прикладів: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()