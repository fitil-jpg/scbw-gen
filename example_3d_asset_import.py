#!/usr/bin/env python3
"""
Example: 3D Asset Import with Instancing
Приклад використання імпорту 3D асетів з інстансингом
"""

import os
import sys
import logging
import random
import math
from pathlib import Path
from typing import List, Tuple

# Додати поточну директорію до шляху для імпорту
sys.path.append(str(Path(__file__).parent))

from asset_3d_importer import Asset3DImporter, ModelFormat, ModelInstance
from asset_manager import AssetManager, AssetType
from config_manager import ConfigManager

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOG = logging.getLogger(__name__)


def create_sample_3d_models():
    """Створити зразкові 3D моделі для тестування"""
    models_dir = Path("assets/3d_assets/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Створити зразкові файли моделей (заглушки)
    sample_models = [
        "castle.gltf",
        "tower.obj", 
        "barracks.fbx",
        "warrior.glb",
        "archer.usd",
        "mage.dae"
    ]
    
    for model_file in sample_models:
        model_path = models_dir / model_file
        if not model_path.exists():
            # Створити заглушку файлу
            with open(model_path, 'w') as f:
                f.write(f"# Placeholder {model_file}\n")
            LOG.info(f"Створено зразкову модель: {model_path}")


def example_basic_import():
    """Приклад базового імпорту 3D моделей"""
    LOG.info("=== Приклад базового імпорту 3D моделей ===")
    
    # Створити зразкові моделі
    create_sample_3d_models()
    
    # Створити імпортер
    importer = Asset3DImporter("assets")
    
    # Імпортувати моделі
    models_dir = Path("assets/3d_assets/models")
    imported_models = []
    
    for model_file in models_dir.glob("*"):
        if model_file.suffix.lower() in ['.gltf', '.glb', '.obj', '.fbx', '.usd', '.dae']:
            try:
                model = importer.import_model(model_file)
                imported_models.append(model)
                LOG.info(f"Імпортовано: {model.name} ({model.format.value})")
            except Exception as e:
                LOG.error(f"Помилка імпорту {model_file}: {e}")
    
    LOG.info(f"Всього імпортовано моделей: {len(imported_models)}")
    return importer, imported_models


def example_instancing():
    """Приклад створення інстансів"""
    LOG.info("=== Приклад створення інстансів ===")
    
    importer, models = example_basic_import()
    
    if not models:
        LOG.warning("Немає моделей для створення інстансів")
        return importer
    
    # Створити інстанси для кожної моделі
    instance_count = 0
    
    for model in models:
        model_key = f"{model.format.value}_{model.name}"
        
        # Створити кілька інстансів для кожної моделі
        for i in range(random.randint(2, 5)):
            position = (
                random.uniform(-50, 50),
                random.uniform(0, 10),
                random.uniform(-50, 50)
            )
            rotation = (
                random.uniform(0, 360),
                random.uniform(0, 360),
                random.uniform(0, 360)
            )
            scale = (
                random.uniform(0.5, 2.0),
                random.uniform(0.5, 2.0),
                random.uniform(0.5, 2.0)
            )
            
            try:
                instance_id = importer.create_instance(
                    model_key=model_key,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    metadata={
                        "created_by": "example_script",
                        "instance_number": i,
                        "model_type": model.format.value
                    }
                )
                instance_count += 1
                LOG.info(f"Створено інстанс: {instance_id}")
                
            except Exception as e:
                LOG.error(f"Помилка створення інстансу: {e}")
    
    LOG.info(f"Всього створено інстансів: {instance_count}")
    return importer


def example_instances_from_config():
    """Приклад створення інстансів з конфігурації"""
    LOG.info("=== Приклад створення інстансів з конфігурації ===")
    
    # Створити конфігурацію інстансів
    instances_config = {
        'instances': [
            {
                'model': 'gltf_castle',
                'position': [0, 0, 0],
                'rotation': [0, 0, 0],
                'scale': [1, 1, 1],
                'metadata': {'type': 'main_castle'}
            },
            {
                'model': 'obj_tower',
                'position': [10, 0, 0],
                'rotation': [0, 45, 0],
                'scale': [1.2, 1.2, 1.2],
                'metadata': {'type': 'defense_tower'}
            },
            {
                'model': 'fbx_barracks',
                'position': [-10, 0, 0],
                'rotation': [0, -45, 0],
                'scale': [0.8, 0.8, 0.8],
                'metadata': {'type': 'training_facility'}
            },
            {
                'model': 'glb_warrior',
                'position': [5, 0, 5],
                'rotation': [0, 90, 0],
                'scale': [1, 1, 1],
                'metadata': {'type': 'guard_unit'}
            },
            {
                'model': 'glb_warrior',
                'position': [-5, 0, 5],
                'rotation': [0, -90, 0],
                'scale': [1, 1, 1],
                'metadata': {'type': 'guard_unit'}
            }
        ]
    }
    
    # Зберегти конфігурацію
    config_path = Path("assets/3d_assets/instances_config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import yaml
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(instances_config, f, default_flow_style=False, allow_unicode=True)
    
    # Створити імпортер та імпортувати моделі
    importer = Asset3DImporter("assets")
    create_sample_3d_models()
    
    # Імпортувати необхідні моделі
    model_files = [
        "assets/3d_assets/models/castle.gltf",
        "assets/3d_assets/models/tower.obj",
        "assets/3d_assets/models/barracks.fbx",
        "assets/3d_assets/models/warrior.glb"
    ]
    
    for model_file in model_files:
        if Path(model_file).exists():
            try:
                model = importer.import_model(model_file)
                LOG.info(f"Імпортовано для конфігурації: {model.name}")
            except Exception as e:
                LOG.error(f"Помилка імпорту {model_file}: {e}")
    
    # Створити інстанси з конфігурації
    try:
        instance_ids = importer.create_instances_from_config(config_path)
        LOG.info(f"Створено {len(instance_ids)} інстансів з конфігурації")
        
        for instance_id in instance_ids:
            instance = importer.get_instance(instance_id)
            if instance:
                LOG.info(f"  - {instance_id}: {instance.position}")
        
    except Exception as e:
        LOG.error(f"Помилка створення інстансів з конфігурації: {e}")
    
    return importer


def example_usd_export():
    """Приклад експорту в USD з інстансингом"""
    LOG.info("=== Приклад експорту в USD ===")
    
    # Створити інстанси
    importer = example_instancing()
    
    if not importer.models:
        LOG.warning("Немає моделей для експорту")
        return
    
    # Експорт з інстансингом
    try:
        output_path = "output/3d_scene_with_instancing.usda"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        importer.export_to_usd(output_path, use_instancing=True)
        LOG.info(f"Експортовано сцену з інстансингом: {output_path}")
        
    except Exception as e:
        LOG.error(f"Помилка експорту USD: {e}")
    
    # Експорт без інстансингу
    try:
        output_path = "output/3d_scene_without_instancing.usda"
        importer.export_to_usd(output_path, use_instancing=False)
        LOG.info(f"Експортовано сцену без інстансингу: {output_path}")
        
    except Exception as e:
        LOG.error(f"Помилка експорту USD без інстансингу: {e}")


def example_instances_management():
    """Приклад управління інстансами"""
    LOG.info("=== Приклад управління інстансами ===")
    
    importer = example_instancing()
    
    # Показати статистику
    LOG.info(f"Всього моделей: {len(importer.models)}")
    LOG.info(f"Всього інстансів: {len(importer.instances)}")
    
    # Показати інстанси по моделях
    for model_key, model in importer.models.items():
        LOG.info(f"Модель {model_key}: {len(model.instances)} інстансів")
    
    # Видалити деякі інстанси
    instances_to_remove = list(importer.instances.keys())[:2]
    for instance_id in instances_to_remove:
        if importer.remove_instance(instance_id):
            LOG.info(f"Видалено інстанс: {instance_id}")
    
    # Очистити інстанси для однієї моделі
    if importer.models:
        first_model_key = list(importer.models.keys())[0]
        removed_count = importer.clear_instances(first_model_key)
        LOG.info(f"Очищено {removed_count} інстансів для моделі {first_model_key}")
    
    # Експорт конфігурації інстансів
    try:
        config_path = "output/instances_export.yaml"
        importer.export_instances_config(config_path)
        LOG.info(f"Експортовано конфігурацію інстансів: {config_path}")
        
    except Exception as e:
        LOG.error(f"Помилка експорту конфігурації: {e}")


def example_performance_test():
    """Приклад тестування продуктивності інстансингу"""
    LOG.info("=== Приклад тестування продуктивності ===")
    
    import time
    
    # Створити імпортер
    importer = Asset3DImporter("assets")
    create_sample_3d_models()
    
    # Імпортувати одну модель
    model_file = Path("assets/3d_assets/models/castle.gltf")
    if model_file.exists():
        model = importer.import_model(model_file)
        model_key = f"{model.format.value}_{model.name}"
        
        # Тест створення багатьох інстансів
        instance_count = 100
        start_time = time.time()
        
        for i in range(instance_count):
            position = (i * 2, 0, 0)
            rotation = (0, i * 3.6, 0)  # Повний оберт
            scale = (1, 1, 1)
            
            try:
                importer.create_instance(model_key, position, rotation, scale)
            except Exception as e:
                LOG.error(f"Помилка створення інстансу {i}: {e}")
                break
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        LOG.info(f"Створено {instance_count} інстансів за {creation_time:.3f} секунд")
        LOG.info(f"Швидкість: {instance_count/creation_time:.1f} інстансів/сек")
        
        # Тест експорту
        start_time = time.time()
        try:
            importer.export_to_usd("output/performance_test.usda", use_instancing=True)
            end_time = time.time()
            export_time = end_time - start_time
            LOG.info(f"Експорт зайняв {export_time:.3f} секунд")
        except Exception as e:
            LOG.error(f"Помилка експорту: {e}")


def main():
    """Головна функція з прикладами"""
    LOG.info("Запуск прикладів 3D Asset Import з інстансингом")
    
    try:
        # Базовий імпорт
        example_basic_import()
        
        # Створення інстансів
        example_instancing()
        
        # Інстанси з конфігурації
        example_instances_from_config()
        
        # Експорт в USD
        example_usd_export()
        
        # Управління інстансами
        example_instances_management()
        
        # Тест продуктивності
        example_performance_test()
        
        LOG.info("Всі приклади виконано успішно!")
        
    except Exception as e:
        LOG.error(f"Помилка виконання прикладів: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())