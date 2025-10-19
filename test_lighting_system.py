#!/usr/bin/env python3
"""
Тест системи освітлення та HDRI для Blender
Test script for lighting and HDRI system
"""

import sys
import os
from pathlib import Path
import logging

# Додавання шляху до модулів Blender
blender_dir = Path(__file__).parent / "blender"
sys.path.append(str(blender_dir))

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_lighting_config_manager():
    """Тестує менеджер конфігурації освітлення"""
    try:
        from lighting_config import LightingConfigManager, LightingConfig
        
        logger.info("Тестування менеджера конфігурації освітлення...")
        
        # Ініціалізація менеджера
        config_manager = LightingConfigManager("configs/lighting")
        
        # Тест створення конфігурації для бойової сцени
        battle_config = config_manager.create_battle_lighting_config("sunset")
        logger.info(f"Конфігурація бойової сцени створена: {len(battle_config.main_lights)} основних лайтів")
        
        # Тест створення конфігурації для студії
        studio_config = config_manager.create_studio_lighting_config("clean")
        logger.info(f"Конфігурація студії створена: {len(studio_config.main_lights)} основних лайтів")
        
        # Тест валідації конфігурації
        errors = config_manager.validate_config(battle_config)
        if errors:
            logger.warning(f"Помилки валідації: {errors}")
        else:
            logger.info("Конфігурація валідна")
        
        # Тест збереження та завантаження
        config_path = "configs/lighting/test_config.yaml"
        config_manager.save_config(battle_config, config_path)
        loaded_config = config_manager.load_config(config_path)
        logger.info("Конфігурація збережена та завантажена успішно")
        
        # Очищення тестового файлу
        os.remove(config_path)
        
        logger.info("✅ Менеджер конфігурації освітлення працює правильно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування менеджера конфігурації: {e}")
        return False

def test_hdri_environment():
    """Тестує систему HDRI середовища"""
    try:
        from hdri_environment import HDRIEnvironment
        
        logger.info("Тестування системи HDRI середовища...")
        
        # Ініціалізація системи HDRI
        hdri_system = HDRIEnvironment({"output_dir": "renders/blender"})
        
        # Тест отримання доступних пресетів
        presets = hdri_system.get_available_presets()
        logger.info(f"Доступні HDRI пресети: {len(presets)}")
        
        # Тест створення користувацького пресету
        custom_preset = {
            "type": "gradient",
            "gradient_type": "SPHERICAL",
            "colors": [[0.2, 0.4, 0.6], [0.8, 0.9, 1.0]],
            "strength": 1.0,
            "description": "Тестовий градієнт"
        }
        hdri_system.create_custom_preset("test_gradient", custom_preset)
        logger.info("Користувацький пресет створено")
        
        # Тест експорту конфігурації
        export_path = "configs/lighting/test_hdri_config.json"
        hdri_system.export_hdri_config(export_path)
        logger.info("Конфігурація HDRI експортована")
        
        # Очищення тестового файлу
        if os.path.exists(export_path):
            os.remove(export_path)
        
        logger.info("✅ Система HDRI середовища працює правильно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування системи HDRI: {e}")
        return False

def test_lighting_system():
    """Тестує систему освітлення"""
    try:
        from lighting_system import LightingSystem
        
        logger.info("Тестування системи освітлення...")
        
        # Ініціалізація системи освітлення
        lighting_system = LightingSystem({"output_dir": "renders/blender"})
        
        # Тест створення пресету освітлення
        sunset_preset = lighting_system.create_lighting_preset("sunset")
        logger.info(f"Пресет освітлення створено: {len(sunset_preset['main_lights'])} основних лайтів")
        
        # Тест експорту конфігурації
        export_path = "configs/lighting/test_lighting_config.yaml"
        lighting_system.export_lighting_config(export_path)
        logger.info("Конфігурація освітлення експортована")
        
        # Очищення тестового файлу
        if os.path.exists(export_path):
            os.remove(export_path)
        
        logger.info("✅ Система освітлення працює правильно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування системи освітлення: {e}")
        return False

def test_integrated_pipeline():
    """Тестує інтегрований пайплайн з новою системою освітлення"""
    try:
        from integrated_blender_pipeline import IntegratedBlenderPipeline
        
        logger.info("Тестування інтегрованого пайплайну...")
        
        # Ініціалізація пайплайну
        pipeline = IntegratedBlenderPipeline("assets", "renders/blender")
        
        # Тест створення пресету освітлення
        test_lighting_config = {
            "hdri": {
                "type": "preset",
                "preset_name": "sunset",
                "strength": 1.0
            },
            "main_lights": [
                {
                    "name": "Test_Sun",
                    "type": "SUN",
                    "position": [5, 5, 10],
                    "energy": 2.0,
                    "color": [1.0, 0.8, 0.6]
                }
            ],
            "additional_lights": [
                {
                    "name": "Test_Fill",
                    "type": "AREA",
                    "position": [-3, -3, 8],
                    "energy": 1.0,
                    "color": [0.8, 0.9, 1.0],
                    "size": 3.0
                }
            ]
        }
        
        pipeline.create_lighting_preset("test_preset", test_lighting_config)
        logger.info("Пресет освітлення створено через пайплайн")
        
        # Тест отримання доступних пресетів
        presets = pipeline.get_available_lighting_presets()
        logger.info(f"Доступні пресети освітлення: {len(presets)}")
        
        # Тест отримання інформації про освітлення
        lighting_info = pipeline.get_lighting_info()
        logger.info(f"Інформація про освітлення: {len(lighting_info.get('lights', {}))} лайтів")
        
        logger.info("✅ Інтегрований пайплайн працює правильно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування інтегрованого пайплайну: {e}")
        return False

def test_configuration_files():
    """Тестує файли конфігурації"""
    try:
        logger.info("Тестування файлів конфігурації...")
        
        config_files = [
            "configs/lighting/battle_sunset_lighting.yaml",
            "configs/lighting/night_battle_lighting.yaml",
            "configs/lighting/studio_clean_lighting.yaml"
        ]
        
        from lighting_config import LightingConfigManager
        
        config_manager = LightingConfigManager("configs/lighting")
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    config = config_manager.load_config(config_file)
                    errors = config_manager.validate_config(config)
                    if errors:
                        logger.warning(f"Помилки валідації {config_file}: {errors}")
                    else:
                        logger.info(f"✅ {config_file} - валідна конфігурація")
                except Exception as e:
                    logger.error(f"❌ Помилка завантаження {config_file}: {e}")
            else:
                logger.warning(f"⚠️ Файл не знайдено: {config_file}")
        
        logger.info("✅ Тестування файлів конфігурації завершено")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка тестування файлів конфігурації: {e}")
        return False

def main():
    """Головна функція тестування"""
    logger.info("🚀 Початок тестування системи освітлення та HDRI")
    
    # Створення директорій для тестів
    os.makedirs("configs/lighting", exist_ok=True)
    os.makedirs("renders/blender", exist_ok=True)
    
    tests = [
        ("Менеджер конфігурації освітлення", test_lighting_config_manager),
        ("Система HDRI середовища", test_hdri_environment),
        ("Система освітлення", test_lighting_system),
        ("Інтегрований пайплайн", test_integrated_pipeline),
        ("Файли конфігурації", test_configuration_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Тестування: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Критична помилка в тесті {test_name}: {e}")
            results.append((test_name, False))
    
    # Підсумок результатів
    logger.info(f"\n{'='*50}")
    logger.info("ПІДСУМОК ТЕСТУВАННЯ")
    logger.info(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ПРОВАЛЕНО"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info(f"\nЗагальний результат: {passed} пройдено, {failed} провалено")
    
    if failed == 0:
        logger.info("🎉 Всі тести пройдено успішно!")
        return True
    else:
        logger.error(f"⚠️ {failed} тестів провалено")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)