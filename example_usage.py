#!/usr/bin/env python3
"""
Example Usage of USD Scene Generator
Приклад використання генератора USD сцен
"""

import os
import sys
from pathlib import Path

# Додати поточну директорію до шляху Python
sys.path.insert(0, str(Path(__file__).parent))

from generate_usd_scene import USDSceneGenerator
from usd_utils import USDUnitManager, USDBuildingManager, USDTerrainManager, USDEffectManager


def create_example_scene():
    """Створити приклад сцени"""
    print("Створення прикладу USD сцени...")
    
    # Створити директорію виводу
    os.makedirs("out", exist_ok=True)
    
    # Генерувати сцену з конфігурації
    generator = USDSceneGenerator("scene.yaml", "out/example_scene.usda")
    success = generator.generate_scene()
    
    if success:
        print("✅ Приклад сцени створено: out/example_scene.usda")
    else:
        print("❌ Помилка створення сцени")
    
    return success


def create_custom_scene():
    """Створити кастомну сцену з використанням утиліт"""
    print("Створення кастомної USD сцени...")
    
    try:
        from pxr import Usd, UsdGeom, Gf
        USD_AVAILABLE = True
    except ImportError:
        print("❌ USD Python bindings не доступні")
        return False
    
    # Створити новий stage
    stage = Usd.Stage.CreateNew("out/custom_scene.usda")
    stage.SetMetadata("upAxis", "Y")
    stage.SetMetadata("metersPerUnit", 1.0)
    
    # Створити менеджери
    unit_manager = USDUnitManager(stage)
    building_manager = USDBuildingManager(stage)
    terrain_manager = USDTerrainManager(stage)
    effect_manager = USDEffectManager(stage)
    
    # Створити рельєф
    terrain_manager.create_terrain("grassland", 100.0, 0.2)
    
    # Створити юнітів
    blue_army_positions = [(10, 10), (12, 10), (14, 10), (16, 10)]
    for pos in blue_army_positions:
        unit_manager.create_unit_sprite("warrior", pos, [0.2, 0.4, 0.8], 1.0)
    
    red_army_positions = [(80, 80), (82, 80), (84, 80), (86, 80)]
    for pos in red_army_positions:
        unit_manager.create_unit_sprite("archer", pos, [0.8, 0.2, 0.2], 0.8)
    
    # Створити будівлі
    building_manager.create_building("castle", (50, 50), "neutral", 0, 1.0)
    building_manager.create_building("tower", (20, 20), "army_1", 45, 0.8)
    building_manager.create_building("tower", (80, 80), "army_2", -45, 0.8)
    
    # Створити ефекти
    effect_manager.create_effect("magic_aura", (50, 50), 10.0, [1.0, 0.0, 1.0], 0.7)
    effect_manager.create_effect("fire", (30, 30), 3.0, [1.0, 0.3, 0.0], 0.8)
    
    # Зберегти сцену
    stage.Save()
    print("✅ Кастомна сцена створена: out/custom_scene.usda")
    
    return True


def main():
    """Головна функція"""
    print("=== USD Scene Generator Example ===")
    print()
    
    # Перевірити наявність конфігурації
    if not os.path.exists("scene.yaml"):
        print("❌ Файл scene.yaml не знайдено")
        return
    
    # Створити приклад сцени
    print("1. Створення прикладу сцени з конфігурації...")
    success1 = create_example_scene()
    
    print()
    
    # Створити кастомну сцену
    print("2. Створення кастомної сцени...")
    success2 = create_custom_scene()
    
    print()
    
    if success1 and success2:
        print("🎉 Всі приклади створено успішно!")
        print("Файли збережено в директорії out/")
        print()
        print("Для перегляду USD файлів використовуйте:")
        print("- USD Composer (безкоштовний)")
        print("- Blender з USD плагіном")
        print("- Houdini")
        print("- Omniverse Create/View")
    else:
        print("❌ Деякі приклади не вдалося створити")


if __name__ == "__main__":
    main()