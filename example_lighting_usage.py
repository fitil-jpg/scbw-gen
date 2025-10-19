#!/usr/bin/env python3
"""
Приклад використання системи освітлення та HDRI для Blender
Example usage of lighting and HDRI system for Blender
"""

import sys
import os
from pathlib import Path

# Додавання шляху до модулів Blender
blender_dir = Path(__file__).parent / "blender"
sys.path.append(str(blender_dir))

def example_basic_lighting():
    """Приклад базового освітлення"""
    print("=== Приклад базового освітлення ===")
    
    # Імпорт модулів (тільки для демонстрації структури)
    try:
        from lighting_config import LightingConfigManager
        
        # Ініціалізація менеджера конфігурації
        config_manager = LightingConfigManager("configs/lighting")
        
        # Створення конфігурації для бойової сцени
        battle_config = config_manager.create_battle_lighting_config("sunset")
        
        print(f"✅ Конфігурація бойової сцени створена")
        print(f"   - HDRI: {battle_config.hdri.type.value if battle_config.hdri else 'None'}")
        print(f"   - Основних лайтів: {len(battle_config.main_lights)}")
        print(f"   - Додаткових лайтів: {len(battle_config.additional_lights)}")
        
        # Створення конфігурації для студії
        studio_config = config_manager.create_studio_lighting_config("clean")
        
        print(f"✅ Конфігурація студії створена")
        print(f"   - HDRI: {studio_config.hdri.type.value if studio_config.hdri else 'None'}")
        print(f"   - Основних лайтів: {len(studio_config.main_lights)}")
        print(f"   - Додаткових лайтів: {len(studio_config.additional_lights)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def example_configuration_files():
    """Приклад роботи з файлами конфігурації"""
    print("\n=== Приклад роботи з файлами конфігурації ===")
    
    try:
        from lighting_config import LightingConfigManager
        
        config_manager = LightingConfigManager("configs/lighting")
        
        # Список доступних файлів конфігурації
        config_files = [
            "configs/lighting/battle_sunset_lighting.yaml",
            "configs/lighting/night_battle_lighting.yaml",
            "configs/lighting/studio_clean_lighting.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    # Завантаження конфігурації
                    config = config_manager.load_config(config_file)
                    
                    # Валідація
                    errors = config_manager.validate_config(config)
                    
                    if errors:
                        print(f"⚠️ {config_file}: {len(errors)} помилок валідації")
                    else:
                        print(f"✅ {config_file}: валідна конфігурація")
                        print(f"   - HDRI: {config.hdri.type.value if config.hdri else 'None'}")
                        print(f"   - Основних лайтів: {len(config.main_lights)}")
                        print(f"   - Додаткових лайтів: {len(config.additional_lights)}")
                        
                except Exception as e:
                    print(f"❌ {config_file}: помилка завантаження - {e}")
            else:
                print(f"⚠️ {config_file}: файл не знайдено")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def example_custom_configuration():
    """Приклад створення користувацької конфігурації"""
    print("\n=== Приклад створення користувацької конфігурації ===")
    
    try:
        from lighting_config import LightingConfigManager, LightConfig, HDRIConfig, LightingConfig, LightType, HDRIType
        
        config_manager = LightingConfigManager("configs/lighting")
        
        # Створення користувацької конфігурації
        custom_config = LightingConfig(
            hdri=HDRIConfig(
                type=HDRIType.GRADIENT,
                gradient_type="SPHERICAL",
                colors=[[0.2, 0.4, 0.6], [0.8, 0.9, 1.0]],
                strength=1.0
            ),
            main_lights=[
                LightConfig(
                    name="Custom_Key_Light",
                    type=LightType.AREA,
                    position=[5, -5, 8],
                    energy=3.0,
                    color=[1.0, 0.9, 0.8],
                    size=4.0,
                    shape="SQUARE"
                )
            ],
            additional_lights=[
                LightConfig(
                    name="Custom_Fill_Light",
                    type=LightType.AREA,
                    position=[-3, -3, 6],
                    energy=1.5,
                    color=[0.8, 0.9, 1.0],
                    size=6.0,
                    shape="SQUARE"
                ),
                LightConfig(
                    name="Custom_Rim_Light",
                    type=LightType.AREA,
                    position=[0, 5, 4],
                    energy=2.0,
                    color=[1.0, 1.0, 1.0],
                    size=3.0,
                    shape="SQUARE"
                )
            ]
        )
        
        # Валідація конфігурації
        errors = config_manager.validate_config(custom_config)
        
        if errors:
            print(f"❌ Помилки валідації: {errors}")
            return False
        
        # Збереження конфігурації
        config_path = "configs/lighting/custom_lighting.yaml"
        config_manager.save_config(custom_config, config_path)
        
        print(f"✅ Користувацька конфігурація створена та збережена: {config_path}")
        print(f"   - HDRI: {custom_config.hdri.type.value}")
        print(f"   - Основних лайтів: {len(custom_config.main_lights)}")
        print(f"   - Додаткових лайтів: {len(custom_config.additional_lights)}")
        
        # Очищення тестового файлу
        if os.path.exists(config_path):
            os.remove(config_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def example_preset_management():
    """Приклад роботи з пресетами"""
    print("\n=== Приклад роботи з пресетами ===")
    
    try:
        from lighting_config import LightingConfigManager
        
        config_manager = LightingConfigManager("configs/lighting")
        
        # Отримання доступних пресетів
        presets = config_manager.get_available_presets()
        print(f"✅ Доступні пресети: {len(presets)}")
        for preset_name in presets:
            print(f"   - {preset_name}")
        
        # Отримання конкретного пресету
        sunset_preset = config_manager.get_preset("battle_sunset")
        if sunset_preset:
            print(f"✅ Пресет 'battle_sunset' завантажено")
            print(f"   - Основних лайтів: {len(sunset_preset.get('main_lights', []))}")
            print(f"   - Додаткових лайтів: {len(sunset_preset.get('additional_lights', []))}")
        else:
            print("⚠️ Пресет 'battle_sunset' не знайдено")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def example_blender_integration():
    """Приклад інтеграції з Blender (симуляція)"""
    print("\n=== Приклад інтеграції з Blender ===")
    
    print("Для використання в Blender, додайте наступний код:")
    print()
    print("```python")
    print("import bpy")
    print("from lighting_system import LightingSystem")
    print("from hdri_environment import HDRIEnvironment")
    print("from integrated_blender_pipeline import IntegratedBlenderPipeline")
    print()
    print("# Ініціалізація пайплайну")
    print("pipeline = IntegratedBlenderPipeline('assets', 'renders/blender')")
    print()
    print("# Конфігурація шоту з освітленням")
    print("shot_config = {")
    print("    'shot_id': 'battle_sunset_001',")
    print("    'lighting': {")
    print("        'preset': 'battle_sunset'")
    print("    },")
    print("    'render_settings': {")
    print("        'engine': 'CYCLES',")
    print("        'samples': 128,")
    print("        'resolution': [1920, 1080]")
    print("    }")
    print("}")
    print()
    print("# Обробка шоту")
    print("result = pipeline.process_shot('battle_sunset_001', shot_config)")
    print("```")
    print()
    print("Або використовуйте окремі компоненти:")
    print()
    print("```python")
    print("# Система освітлення")
    print("lighting_system = LightingSystem({'output_dir': 'renders/blender'})")
    print("lighting_system.setup_lighting(lighting_config)")
    print()
    print("# HDRI середовище")
    print("hdri_system = HDRIEnvironment({'output_dir': 'renders/blender'})")
    print("hdri_system.setup_hdri_environment(hdri_config)")
    print("```")
    
    return True

def main():
    """Головна функція прикладу"""
    print("🚀 Приклади використання системи освітлення та HDRI")
    print("=" * 60)
    
    # Створення директорій
    os.makedirs("configs/lighting", exist_ok=True)
    os.makedirs("renders/blender", exist_ok=True)
    
    examples = [
        ("Базове освітлення", example_basic_lighting),
        ("Файли конфігурації", example_configuration_files),
        ("Користувацька конфігурація", example_custom_configuration),
        ("Робота з пресетами", example_preset_management),
        ("Інтеграція з Blender", example_blender_integration)
    ]
    
    results = []
    
    for example_name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"Приклад: {example_name}")
        print(f"{'='*60}")
        
        try:
            result = example_func()
            results.append((example_name, result))
        except Exception as e:
            print(f"❌ Критична помилка в прикладі {example_name}: {e}")
            results.append((example_name, False))
    
    # Підсумок
    print(f"\n{'='*60}")
    print("ПІДСУМОК ПРИКЛАДІВ")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for example_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ПРОВАЛЕНО"
        print(f"{example_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nЗагальний результат: {passed} пройдено, {failed} провалено")
    
    if failed == 0:
        print("\n🎉 Всі приклади виконано успішно!")
        print("\n📚 Для детальної документації дивіться LIGHTING_SYSTEM_README.md")
    else:
        print(f"\n⚠️ {failed} прикладів провалено")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)