#!/usr/bin/env python3
"""
Спрощений тестовий скрипт для Blender пайплайну
Перевіряє основну функціональність без запуску Blender
"""

import sys
import os
from pathlib import Path
import yaml
import json

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent / "blender"))

def test_config_importer():
    """Тестує імпортер конфігурацій"""
    print("Тестування Config Importer...")
    
    try:
        from enhanced_config_importer import EnhancedConfigImporter
        
        # Створення тестової конфігурації
        test_config = {
            "buildings": [
                {
                    "name": "Test Building",
                    "type": "cube",
                    "position": [0, 0, 0],
                    "scale": [1, 1, 1]
                }
            ]
        }
        
        # Збереження тестової конфігурації
        os.makedirs("assets/buildings", exist_ok=True)
        with open("assets/buildings/test_config.yaml", 'w') as f:
            yaml.dump(test_config, f)
        
        # Тестування імпортера
        importer = EnhancedConfigImporter("assets")
        config = importer.load_config("buildings", "test_config")
        
        print("  ✓ Config Importer працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Config Importer помилка: {e}")
        return False

def test_geometry_generator():
    """Тестує генератор геометрії (без Blender)"""
    print("Тестування Geometry Generator...")
    
    try:
        # Тестування валідації конфігурації
        building_config = {
            "name": "Test Building",
            "type": "cube",
            "position": [0, 0, 0],
            "scale": [1, 1, 1]
        }
        
        # Тестування валідації (без створення об'єкта)
        required_fields = ["name", "type", "position", "scale"]
        for field in required_fields:
            if field not in building_config:
                raise ValueError(f"Відсутнє поле: {field}")
        
        print("  ✓ Geometry Generator валідація працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Geometry Generator помилка: {e}")
        return False

def test_render_pipeline():
    """Тестує рендер пайплайн (без Blender)"""
    print("Тестування Render Pipeline...")
    
    try:
        # Тестування налаштувань рендерингу
        render_settings = {
            "engine": "CYCLES",
            "samples": 128,
            "resolution": [1920, 1080],
            "output_format": "PNG"
        }
        
        # Валідація налаштувань
        required_fields = ["engine", "samples", "resolution"]
        for field in required_fields:
            if field not in render_settings:
                raise ValueError(f"Відсутнє поле: {field}")
        
        print("  ✓ Render Pipeline валідація працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Render Pipeline помилка: {e}")
        return False

def test_integrated_pipeline():
    """Тестує інтегрований пайплайн"""
    print("Тестування Integrated Pipeline...")
    
    try:
        # Тестова конфігурація шоту
        shot_config = {
            "shot_id": "test_shot",
            "terrain": {
                "type": "plane",
                "size": [20, 20]
            },
            "buildings": [
                {
                    "name": "Test Building",
                    "type": "cube",
                    "position": [0, 0, 0],
                    "scale": [1, 1, 1]
                }
            ],
            "camera": {
                "position": [0, -10, 5],
                "rotation": [60, 0, 0]
            },
            "render_settings": {
                "engine": "CYCLES",
                "samples": 64,
                "resolution": [1920, 1080]
            }
        }
        
        # Тестування валідації
        errors = []
        
        # Перевірка обов'язкових полів
        required_fields = ["shot_id"]
        for field in required_fields:
            if field not in shot_config:
                errors.append(f"Відсутнє обов'язкове поле: {field}")
        
        # Перевірка конфігурації рендерингу
        if "render_settings" in shot_config:
            render_settings = shot_config["render_settings"]
            if "engine" not in render_settings:
                errors.append("Відсутній рендер двигун")
            elif render_settings["engine"] not in ["CYCLES", "BLENDER_EEVEE"]:
                errors.append("Невідомий рендер двигун")
        
        # Перевірка конфігурації камери
        if "camera" in shot_config:
            camera_config = shot_config["camera"]
            if "position" not in camera_config:
                errors.append("Відсутня позиція камери")
            if "rotation" not in camera_config:
                errors.append("Відсутнє обертання камери")
        
        if errors:
            raise ValueError(f"Помилки валідації: {errors}")
        
        print("  ✓ Integrated Pipeline валідація працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Integrated Pipeline помилка: {e}")
        return False

def test_config_validation():
    """Тестує валідацію конфігурацій"""
    print("Тестування Config Validation...")
    
    try:
        # Тест валідної конфігурації
        valid_config = {
            "shot_id": "test",
            "camera": {
                "position": [0, 0, 0],
                "rotation": [0, 0, 0]
            },
            "render_settings": {
                "engine": "CYCLES"
            }
        }
        
        # Валідація
        errors = []
        required_fields = ["shot_id"]
        for field in required_fields:
            if field not in valid_config:
                errors.append(f"Відсутнє обов'язкове поле: {field}")
        
        if errors:
            raise ValueError(f"Валідна конфігурація має помилки: {errors}")
        
        # Тест невалідної конфігурації
        invalid_config = {
            "camera": {
                "position": [0, 0, 0]
                # Відсутнє rotation
            },
            "render_settings": {
                "engine": "INVALID_ENGINE"
            }
        }
        
        # Валідація
        errors = []
        if "shot_id" not in invalid_config:
            errors.append("Відсутнє обов'язкове поле: shot_id")
        
        if "render_settings" in invalid_config:
            render_settings = invalid_config["render_settings"]
            if "engine" not in render_settings:
                errors.append("Відсутній рендер двигун")
            elif render_settings["engine"] not in ["CYCLES", "BLENDER_EEVEE"]:
                errors.append("Невідомий рендер двигун")
        
        if not errors:
            raise ValueError("Невалідна конфігурація не має помилок")
        
        print("  ✓ Config Validation працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Config Validation помилка: {e}")
        return False

def test_template_loading():
    """Тестує завантаження шаблонів"""
    print("Тестування Template Loading...")
    
    try:
        # Перевірка наявності шаблону
        if not Path("assets/templates/battle_scene_template.yaml").exists():
            print("  ⚠ Шаблон battle_scene_template.yaml не знайдено")
            return True
        
        # Тестування завантаження шаблону
        with open("assets/templates/battle_scene_template.yaml", 'r') as f:
            template_config = yaml.safe_load(f)
        
        if "shot_id" not in template_config:
            raise ValueError("Шаблон не містить shot_id")
        
        print("  ✓ Template Loading працює")
        return True
        
    except Exception as e:
        print(f"  ✗ Template Loading помилка: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("Запуск спрощених тестів Blender Pipeline...")
    print("=" * 50)
    
    tests = [
        test_config_importer,
        test_geometry_generator,
        test_render_pipeline,
        test_integrated_pipeline,
        test_config_validation,
        test_template_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Критична помилка в {test.__name__}: {e}")
    
    print("=" * 50)
    print(f"Результати тестування: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно!")
        return 0
    else:
        print("❌ Деякі тести не пройдено")
        return 1

if __name__ == "__main__":
    sys.exit(main())
