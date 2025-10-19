#!/usr/bin/env python3
"""
MVP Test - Тестування MVP без Blender
"""

import os
import sys
from pathlib import Path

# Додати поточну директорію до шляху
sys.path.append(str(Path(__file__).parent))

from mvp_asset_manager import SimpleAssetManager
from mvp_config_manager import SimpleConfigManager
from mvp_asset_loader import MVPAssetLoader
from mvp_material_system_test import MVPMaterialSystemTest as MVPMaterialSystem

def test_asset_manager():
    """Тестування Asset Manager"""
    print("🧪 Тестування Asset Manager...")
    
    asset_manager = SimpleAssetManager("test_assets")
    
    # Створити тестові файли
    test_dir = Path("test_assets")
    test_dir.mkdir(exist_ok=True)
    
    # Створити тестові файли
    (test_dir / "texture1.png").touch()
    (test_dir / "model1.obj").touch()
    (test_dir / "sound1.wav").touch()
    
    # Сканувати директорію
    assets = asset_manager.scan_directory()
    print(f"✅ Знайдено асетів: {len(assets)}")
    
    # Перевірити типи
    for asset in assets:
        print(f"  - {asset.name}: {asset.asset_type} ({asset.size} bytes)")
    
    return len(assets) == 3

def test_config_manager():
    """Тестування Config Manager"""
    print("🧪 Тестування Config Manager...")
    
    config_manager = SimpleConfigManager("test_configs")
    
    # Створити тестову конфігурацію
    test_config = {
        "scene": {
            "name": "Test Scene",
            "version": "1.0"
        },
        "buildings": {
            "Test_Building": {
                "position": [0, 0, 1],
                "size": 1.0,
                "color": [1.0, 0.0, 0.0, 1.0]
            }
        }
    }
    
    # Зберегти конфігурацію
    config_path = config_manager.save_config(test_config, "test_config.yaml")
    print(f"✅ Збережено конфігурацію: {config_path}")
    
    # Завантажити конфігурацію
    loaded_config = config_manager.load_config("test_config.yaml")
    print(f"✅ Завантажено конфігурацію: {loaded_config['scene']['name']}")
    
    return loaded_config["scene"]["name"] == "Test Scene"

def test_asset_loader():
    """Тестування Asset Loader"""
    print("🧪 Тестування Asset Loader...")
    
    asset_loader = MVPAssetLoader("test_assets")
    
    # Створити тестові файли
    test_dir = Path("test_assets")
    test_dir.mkdir(exist_ok=True)
    
    (test_dir / "texture1.png").touch()
    (test_dir / "model1.obj").touch()
    
    # Завантажити стек асетів
    assets = asset_loader.load_asset_stack("test_stack", [
        "test_assets/texture1.png",
        "test_assets/model1.obj"
    ])
    
    print(f"✅ Завантажено стек асетів: {len(assets)}")
    
    # Перевірити, що асети завантажені
    if len(assets) == 0:
        print("⚠️ Асети не завантажені в стек")
        return False
    
    # Створити пакет асетів
    pack = asset_loader.create_asset_pack("test_pack", {
        "texture1": "test_assets/texture1.png",
        "model1": "test_assets/model1.obj"
    })
    
    print(f"✅ Створено пакет: {pack['name']} ({pack['total_size']} bytes)")
    
    return len(assets) == 2

def test_material_system():
    """Тестування Material System"""
    print("🧪 Тестування Material System...")
    
    material_system = MVPMaterialSystem()
    
    # Перевірити пресети
    presets = material_system.presets
    print(f"✅ Доступно пресетів: {len(presets)}")
    
    for name, preset in presets.items():
        print(f"  - {name}: {preset.name}")
    
    # Створити кастомний матеріал
    custom_mat = material_system.create_custom_material(
        "Test_Material",
        base_color=(1.0, 0.0, 0.0, 1.0),
        metallic=0.5,
        roughness=0.3
    )
    
    print(f"✅ Створено кастомний матеріал: {custom_mat['name']}")
    
    return len(presets) >= 5

def main():
    """Головна функція тестування"""
    print("🚀 Тестування MVP StarCraft Scene Generator")
    print("=" * 50)
    
    tests = [
        ("Asset Manager", test_asset_manager),
        ("Config Manager", test_config_manager),
        ("Asset Loader", test_asset_loader),
        ("Material System", test_material_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: ПРОЙДЕНО")
                passed += 1
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕНО")
        except Exception as e:
            print(f"❌ {test_name}: ПОМИЛКА - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результати: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно!")
        return 0
    else:
        print("⚠️ Деякі тести не пройдено")
        return 1

if __name__ == "__main__":
    exit(main())