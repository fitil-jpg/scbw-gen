#!/usr/bin/env python3
"""
Test USD Scene Generator
Тест генератора USD сцен без USD залежностей
"""

import os
import yaml
from pathlib import Path


def test_config_loading():
    """Тест завантаження конфігурації"""
    print("Тестування завантаження конфігурації...")
    
    if not os.path.exists("scene.yaml"):
        print("❌ Файл scene.yaml не знайдено")
        return False
    
    try:
        with open("scene.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Перевірити основні секції
        required_sections = ['scene', 'units', 'buildings']
        for section in required_sections:
            if section not in config:
                print(f"❌ Відсутня секція: {section}")
                return False
        
        print("✅ Конфігурація завантажена успішно")
        print(f"   - Сцена: {config['scene']['name']}")
        print(f"   - Армій: {len(config['units'])}")
        print(f"   - Будівель: {len(config['buildings'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка завантаження конфігурації: {e}")
        return False


def test_assets_structure():
    """Тест структури активів"""
    print("\nТестування структури активів...")
    
    assets_path = Path("assets")
    if not assets_path.exists():
        print("❌ Директорія assets не знайдена")
        return False
    
    # Перевірити піддиректорії
    required_dirs = ['units', 'buildings', 'terrain', 'effects']
    for dir_name in required_dirs:
        dir_path = assets_path / dir_name
        if not dir_path.exists():
            print(f"❌ Відсутня директорія: {dir_name}")
            return False
    
    # Перевірити конфігураційні файли
    config_files = [
        'units/units_config.yaml',
        'buildings/buildings_config.yaml', 
        'terrain/terrain_config.yaml',
        'effects/effects_config.yaml'
    ]
    
    for config_file in config_files:
        file_path = assets_path / config_file
        if not file_path.exists():
            print(f"❌ Відсутній конфігураційний файл: {config_file}")
            return False
        
        # Перевірити валідність YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Помилка в YAML файлі {config_file}: {e}")
            return False
    
    print("✅ Структура активів валідна")
    return True


def test_generator_import():
    """Тест імпорту генератора"""
    print("\nТестування імпорту генератора...")
    
    try:
        from generate_usd_scene import USDSceneGenerator
        print("✅ USDSceneGenerator імпортовано успішно")
        
        # Спробувати створити екземпляр
        generator = USDSceneGenerator("scene.yaml", "out/test.usda")
        print("✅ Екземпляр USDSceneGenerator створено")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка імпорту генератора: {e}")
        return False


def test_utils_import():
    """Тест імпорту утиліт"""
    print("\nТестування імпорту утиліт...")
    
    try:
        from usd_utils import (
            USDUnitManager, 
            USDBuildingManager, 
            USDTerrainManager, 
            USDEffectManager,
            USDSceneUtils
        )
        print("✅ Всі утиліти імпортовано успішно")
        return True
        
    except Exception as e:
        print(f"❌ Помилка імпорту утиліт: {e}")
        return False


def test_yaml_parsing():
    """Тест парсингу YAML конфігурацій"""
    print("\nТестування парсингу YAML...")
    
    config_files = [
        "scene.yaml",
        "assets/units/units_config.yaml",
        "assets/buildings/buildings_config.yaml",
        "assets/terrain/terrain_config.yaml", 
        "assets/effects/effects_config.yaml"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"❌ Файл не знайдено: {config_file}")
            return False
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ {config_file} - OK")
        except Exception as e:
            print(f"❌ {config_file} - Помилка: {e}")
            return False
    
    return True


def main():
    """Головна функція тестування"""
    print("=== Тестування USD Scene Generator ===\n")
    
    tests = [
        test_config_loading,
        test_assets_structure,
        test_generator_import,
        test_utils_import,
        test_yaml_parsing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Результат: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно!")
        print("\nДля повної роботи встановіть USD залежності:")
        print("pip install usd-core pyyaml numpy Pillow")
    else:
        print("❌ Деякі тести не пройдено")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)