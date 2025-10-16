#!/usr/bin/env python3
"""
Configuration System Demo
Демонстрація системи конфігурацій та файлових операцій
"""

import logging
from pathlib import Path
import tempfile
import shutil

from config_parser import UniversalConfigParser, ConfigFormat, create_pack_config_schema
from file_io_utils import FileIOUtils
from config_manager import ConfigManager, ConfigType
from asset_manager import AssetManager, AssetType
from validation_system import ValidationSystem, ValidationSchema, ValidationRule, ValidationLevel, ValidationSeverity

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOG = logging.getLogger(__name__)


def demo_config_parser():
    """Демонстрація парсера конфігурацій"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦІЯ ПАРСЕРА КОНФІГУРАЦІЙ")
    print("="*60)
    
    parser = UniversalConfigParser()
    
    # Створити тестові дані
    test_data = {
        "seed": 1337,
        "image_size": [1280, 720],
        "shots": [
            {
                "id": "shot_1001",
                "palette": [[0.07, 0.13, 0.09], [0.12, 0.2, 0.14]],
                "portal": {"center": [0.5, 0.5], "radius": 0.18},
                "export": {"png": True, "exr16": True}
            },
            {
                "id": "shot_1002", 
                "palette": "ArmyColors",
                "portal": {"center": [0.52, 0.48], "radius": 0.21},
                "export": {"png": True, "exr16": False}
            }
        ]
    }
    
    # Зберегти в різних форматах
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        yaml_file = temp_path / "test.yaml"
        json_file = temp_path / "test.json"
        
        # Зберегти YAML
        parser.save_file(test_data, yaml_file, ConfigFormat.YAML)
        print(f"✅ Збережено YAML: {yaml_file}")
        
        # Зберегти JSON
        parser.save_file(test_data, json_file, ConfigFormat.JSON)
        print(f"✅ Збережено JSON: {json_file}")
        
        # Завантажити назад
        loaded_yaml = parser.load_file(yaml_file)
        loaded_json = parser.load_file(json_file)
        
        print(f"✅ Завантажено YAML: {len(loaded_yaml['shots'])} shots")
        print(f"✅ Завантажено JSON: {len(loaded_json['shots'])} shots")
        
        # Валідація
        schema = create_pack_config_schema()
        yaml_errors = parser.validate_config(loaded_yaml, schema)
        json_errors = parser.validate_config(loaded_json, schema)
        
        print(f"✅ Валідація YAML: {len(yaml_errors)} помилок")
        print(f"✅ Валідація JSON: {len(json_errors)} помилок")
        
        # Конвертація
        converted_file = temp_path / "converted.json"
        parser.convert_format(yaml_file, converted_file)
        print(f"✅ Конвертовано YAML -> JSON: {converted_file}")


def demo_file_io_utils():
    """Демонстрація файлових утиліт"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦІЯ ФАЙЛОВИХ УТИЛІТ")
    print("="*60)
    
    file_utils = FileIOUtils(create_backups=True)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Створити тестові файли
        test_files = []
        for i in range(3):
            test_file = temp_path / f"test_{i}.txt"
            test_file.write_text(f"Test content {i}")
            test_files.append(test_file)
        
        print(f"✅ Створено {len(test_files)} тестових файлів")
        
        # Створити піддиректорію
        subdir = temp_path / "subdir"
        file_utils.ensure_directory(subdir)
        print(f"✅ Створено директорію: {subdir}")
        
        # Копіювати файли
        for i, src_file in enumerate(test_files):
            dst_file = subdir / f"copy_{i}.txt"
            file_utils.copy_file(src_file, dst_file)
        
        print(f"✅ Скопійовано {len(test_files)} файлів в піддиректорію")
        
        # Знайти файли
        all_files = file_utils.find_files(temp_path, "*.txt")
        print(f"✅ Знайдено {len(all_files)} .txt файлів")
        
        # Отримати інформацію про файли
        for file_path in all_files[:2]:  # Показати тільки перші 2
            file_info = file_utils.get_file_info(file_path)
            if file_info:
                print(f"   📄 {file_path.name}: {file_info.size} байт, хеш: {file_info.checksum[:8]}...")
        
        # Синхронізація директорій
        sync_dest = temp_path / "sync_dest"
        file_utils.ensure_directory(sync_dest)
        
        sync_result = file_utils.sync_directories(temp_path / "subdir", sync_dest)
        print(f"✅ Синхронізація: {len(sync_result['copied'])} скопійовано, {len(sync_result['updated'])} оновлено")
        
        # Пакетні операції
        operations = [
            {"operation": "copy", "source": str(test_files[0]), "destination": str(sync_dest / "batch_copy.txt")},
            {"operation": "backup", "source": str(test_files[1])},
        ]
        
        batch_result = file_utils.batch_operation(operations)
        print(f"✅ Пакетні операції: {len(batch_result['success'])} успішних, {len(batch_result['failed'])} невдалих")


def demo_config_manager():
    """Демонстрація менеджера конфігурацій"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦІЯ МЕНЕДЖЕРА КОНФІГУРАЦІЙ")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        
        # Створити тестові конфігурації
        pack_config_data = {
            "seed": 1337,
            "image_size": [1280, 720],
            "shots": [
                {
                    "id": "demo_shot",
                    "palette": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                    "portal": {"center": [0.5, 0.5], "radius": 0.2},
                    "export": {"png": True, "exr16": True}
                }
            ]
        }
        
        scene_config_data = {
            "scene": {
                "name": "Demo Scene",
                "size": [100, 100],
                "terrain": {"type": "grassland", "height_variation": 0.2}
            },
            "units": {
                "army_1": {
                    "color": [0.2, 0.4, 0.8],
                    "spawn_area": [10, 10, 30, 30],
                    "units": [{"type": "warrior", "count": 10}]
                }
            }
        }
        
        # Зберегти конфігурації
        pack_file = Path(temp_dir) / "pack.yaml"
        scene_file = Path(temp_dir) / "scene.yaml"
        
        with open(pack_file, 'w') as f:
            import yaml
            yaml.dump(pack_config_data, f)
        
        with open(scene_file, 'w') as f:
            yaml.dump(scene_config_data, f)
        
        print(f"✅ Створено тестові конфігурації")
        
        # Завантажити конфігурації
        pack_entry = config_manager.load_config(pack_file, ConfigType.PACK)
        scene_entry = config_manager.load_config(scene_file, ConfigType.SCENE)
        
        print(f"✅ Завантажено pack конфігурацію: {pack_entry.metadata.name}")
        print(f"   Валідна: {pack_entry.is_valid}")
        print(f"   Помилок: {len(pack_entry.validation_errors)}")
        
        print(f"✅ Завантажено scene конфігурацію: {scene_entry.metadata.name}")
        print(f"   Валідна: {scene_entry.is_valid}")
        print(f"   Помилок: {len(scene_entry.validation_errors)}")
        
        # Список конфігурацій
        all_configs = config_manager.list_configs()
        pack_configs = config_manager.list_configs(ConfigType.PACK)
        
        print(f"✅ Всього конфігурацій: {len(all_configs)}")
        print(f"✅ Pack конфігурацій: {len(pack_configs)}")
        
        # Об'єднання конфігурацій
        merged_entry = config_manager.merge_configs(pack_entry, scene_entry)
        print(f"✅ Об'єднано конфігурації: {merged_entry.metadata.name}")
        
        # Конвертація
        json_file = Path(temp_dir) / "pack.json"
        converted_entry = config_manager.convert_config(pack_entry, ConfigFormat.JSON)
        print(f"✅ Конвертовано в JSON: {converted_entry.path}")


def demo_asset_manager():
    """Демонстрація менеджера асетів"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦІЯ МЕНЕДЖЕРА АСЕТІВ")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        asset_manager = AssetManager(temp_dir)
        
        # Створити тестові асети
        test_assets = []
        
        # Текстові файли (дані)
        for i in range(3):
            data_file = Path(temp_dir) / "data" / f"data_{i}.txt"
            data_file.parent.mkdir(exist_ok=True)
            data_file.write_text(f"Data content {i}")
            test_assets.append(data_file)
        
        # JSON файли (конфігурації)
        for i in range(2):
            config_file = Path(temp_dir) / "data" / f"config_{i}.json"
            config_data = {"id": f"config_{i}", "value": i * 10}
            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f)
            test_assets.append(config_file)
        
        print(f"✅ Створено {len(test_assets)} тестових асетів")
        
        # Сканувати директорію
        found_assets = asset_manager.scan_directory(temp_dir, recursive=True)
        print(f"✅ Знайдено {len(found_assets)} асетів при скануванні")
        
        # Зареєструвати асети вручну
        for asset_file in test_assets:
            try:
                asset_info = asset_manager.register_asset(asset_file, "data")
                print(f"   📄 {asset_info.name}: {asset_info.asset_type.value}, {asset_info.size} байт")
            except Exception as e:
                print(f"   ❌ Помилка реєстрації {asset_file}: {e}")
        
        # Пошук асетів
        data_assets = asset_manager.find_assets(asset_type=AssetType.DATA)
        print(f"✅ Знайдено {len(data_assets)} асетів типу DATA")
        
        # Валідація асетів
        validation_results = asset_manager.validate_all_assets()
        print(f"✅ Валідація: {len(validation_results['valid'])} валідних, {len(validation_results['invalid'])} невалідних")
        
        # Експорт списку асетів
        export_file = Path(temp_dir) / "asset_list.json"
        asset_manager.export_asset_list(export_file, "json")
        print(f"✅ Експортовано список асетів: {export_file}")


def demo_validation_system():
    """Демонстрація системи валідації"""
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦІЯ СИСТЕМИ ВАЛІДАЦІЇ")
    print("="*60)
    
    validation_system = ValidationSystem()
    
    # Створити схему валідації
    schema = ValidationSchema("demo_schema", "1.0")
    
    # Додати правила валідації
    schema.add_rule(ValidationRule(
        field_path="name",
        validator=lambda x: isinstance(x, str) and len(x) > 0,
        message="Ім'я повинно бути непустим рядком",
        required=True,
        data_type=str,
        severity=ValidationSeverity.HIGH
    ))
    
    schema.add_rule(ValidationRule(
        field_path="age",
        validator=lambda x: isinstance(x, int) and 0 <= x <= 150,
        message="Вік повинен бути числом від 0 до 150",
        required=True,
        data_type=int,
        min_value=0,
        max_value=150,
        severity=ValidationSeverity.MEDIUM
    ))
    
    schema.add_rule(ValidationRule(
        field_path="email",
        validator=lambda x: isinstance(x, str) and "@" in x and "." in x,
        message="Email повинен бути валідним",
        required=False,
        data_type=str,
        severity=ValidationSeverity.LOW
    ))
    
    # Зареєструвати схему
    validation_system.register_schema(schema)
    
    # Тестові дані
    test_cases = [
        {
            "name": "Валідна конфігурація",
            "data": {"name": "John Doe", "age": 30, "email": "john@example.com"}
        },
        {
            "name": "Відсутнє обов'язкове поле",
            "data": {"age": 30, "email": "john@example.com"}
        },
        {
            "name": "Невірний тип даних",
            "data": {"name": "John Doe", "age": "thirty", "email": "john@example.com"}
        },
        {
            "name": "Значення поза діапазоном",
            "data": {"name": "John Doe", "age": 200, "email": "john@example.com"}
        },
        {
            "name": "Невірний email",
            "data": {"name": "John Doe", "age": 30, "email": "invalid-email"}
        }
    ]
    
    # Валідувати кожен тестовий випадок
    for test_case in test_cases:
        print(f"\n📋 {test_case['name']}:")
        result = validation_system.validate(test_case['data'], "demo_schema")
        
        if result.is_valid:
            print("   ✅ Валідна")
        else:
            print(f"   ❌ Невалідна ({len(result.errors)} помилок, {len(result.warnings)} попереджень)")
            
            for issue in result.issues[:3]:  # Показати тільки перші 3 проблеми
                severity_icon = "🔴" if issue.severity == ValidationSeverity.HIGH else "🟡" if issue.severity == ValidationSeverity.MEDIUM else "🔵"
                print(f"      {severity_icon} {issue.field_path}: {issue.message}")
                if issue.suggestion:
                    print(f"         💡 {issue.suggestion}")
    
    # Згенерувати детальний звіт для останнього тестового випадку
    print(f"\n📊 ДЕТАЛЬНИЙ ЗВІТ ВАЛІДАЦІЇ:")
    print("-" * 40)
    last_result = validation_system.validate(test_cases[-1]['data'], "demo_schema")
    report = validation_system.generate_report(last_result, include_suggestions=True)
    print(report)


def main():
    """Головна функція демонстрації"""
    print("🚀 ДЕМОНСТРАЦІЯ СИСТЕМИ КОНФІГУРАЦІЙ ТА ФАЙЛОВИХ ОПЕРАЦІЙ")
    print("=" * 80)
    
    try:
        # Демонстрація всіх компонентів
        demo_config_parser()
        demo_file_io_utils()
        demo_config_manager()
        demo_asset_manager()
        demo_validation_system()
        
        print("\n" + "="*80)
        print("✅ ВСІ ДЕМОНСТРАЦІЇ ЗАВЕРШЕНО УСПІШНО!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПІД ЧАС ДЕМОНСТРАЦІЇ: {e}")
        LOG.exception("Деталі помилки:")


if __name__ == "__main__":
    main()