#!/usr/bin/env python3
"""
MVP Main - Головний файл MVP
Розмір: ~40 рядків
"""

import sys
import os
from pathlib import Path

# Додати поточну директорію до шляху
sys.path.append(str(Path(__file__).parent))

from mvp_scene_generator import MVPSceneGenerator
from mvp_asset_loader import MVPAssetLoader
from mvp_material_system import MVPMaterialSystem

def main():
    """Головна функція MVP"""
    print("🚀 Запуск MVP StarCraft Scene Generator")
    print("=" * 50)
    
    try:
        # Ініціалізація систем
        print("🔧 Ініціалізація систем...")
        scene_generator = MVPSceneGenerator("mvp_scene.yaml")
        asset_loader = MVPAssetLoader("assets")
        material_system = MVPMaterialSystem()
        
        # Завантаження асетів (опціонально)
        print("📦 Завантаження асетів...")
        asset_paths = [
            "assets/textures/terran_metal.png",
            "assets/textures/zerg_organic.png",
            "assets/models/terran_building.obj"
        ]
        
        # Перевірити наявність асетів
        available_assets = [path for path in asset_paths if os.path.exists(path)]
        if available_assets:
            asset_loader.load_asset_stack("main_assets", available_assets)
            print(f"✅ Завантажено {len(available_assets)} асетів")
        else:
            print("ℹ️ Асети не знайдено, використовуємо базові матеріали")
        
        # Генерація сцени
        print("🎬 Генерація сцени...")
        scene_generator.generate_scene()
        
        # Рендеринг
        print("🖼️ Рендеринг...")
        scene_generator.render_scene()
        
        print("✅ MVP завершено успішно!")
        print(f"📁 Результат: renders/blender/mvp_scene.png")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())