# Система конфігурацій та файлових операцій I/O

Комплексна система для роботи з конфігураціями (YAML/JSON) та файловими операціями в Python.

## 🚀 Основні можливості

### 📋 Парсинг конфігурацій
- Підтримка YAML та JSON форматів
- Автоматичне визначення формату файлу
- Валідація конфігурацій з детальними повідомленнями про помилки
- Конвертація між форматами
- Об'єднання конфігурацій

### 📁 Файлові операції
- Копіювання, переміщення, видалення файлів
- Створення резервних копій
- Синхронізація директорій
- Пакетні операції з файлами
- Пошук файлів за шаблонами
- Робота з тимчасовими файлами

### ⚙️ Менеджер конфігурацій
- Централізоване управління конфігураціями
- Підтримка різних типів конфігурацій (pack, scene, buildings, units, effects, terrain)
- Кешування та метадані
- Автоматична валідація при завантаженні

### 🎨 Менеджер асетів
- Реєстрація та управління файлами ресурсів
- Автоматичне визначення типів асетів
- Валідація цілісності файлів
- Експорт списків асетів
- Пошук асетів за критеріями

### ✅ Система валідації
- Детальні повідомлення про помилки
- Різні рівні серйозності (критичні, серйозні, середні, низькі)
- Рекомендації для виправлення помилок
- Генерація звітів валідації

## 📦 Встановлення

```bash
pip install pyyaml pillow
```

## 🚀 Швидкий старт

### Базовий парсинг конфігурацій

```python
from config_parser import UniversalConfigParser, ConfigFormat

# Створення парсера
parser = UniversalConfigParser()

# Завантаження YAML конфігурації
config = parser.load_file("config.yaml")

# Збереження в JSON
parser.save_file(config, "config.json", ConfigFormat.JSON)

# Валідація
from config_parser import create_pack_config_schema
schema = create_pack_config_schema()
errors = parser.validate_config(config, schema)
```

### Робота з файлами

```python
from file_io_utils import FileIOUtils

# Створення утиліт
file_utils = FileIOUtils(create_backups=True)

# Копіювання файлу
file_utils.copy_file("source.txt", "destination.txt")

# Пошук файлів
files = file_utils.find_files("assets/", "*.png", recursive=True)

# Синхронізація директорій
result = file_utils.sync_directories("src/", "dest/")
```

### Менеджер конфігурацій

```python
from config_manager import ConfigManager, ConfigType

# Створення менеджера
config_manager = ConfigManager("configs/")

# Завантаження конфігурації
pack_config = config_manager.load_config("pack.yaml", ConfigType.PACK)

# Список всіх конфігурацій
all_configs = config_manager.list_configs()

# Валідація
is_valid = config_manager.validate_config(pack_config)
```

### Менеджер асетів

```python
from asset_manager import AssetManager, AssetType

# Створення менеджера
asset_manager = AssetManager("assets/")

# Сканування директорії
assets = asset_manager.scan_directory("assets/", recursive=True)

# Пошук текстур
textures = asset_manager.find_assets(asset_type=AssetType.TEXTURE)

# Валідація асетів
results = asset_manager.validate_all_assets()
```

### Система валідації

```python
from validation_system import ValidationSystem, ValidationSchema, ValidationRule, ValidationSeverity

# Створення системи валідації
validation_system = ValidationSystem()

# Створення схеми
schema = ValidationSchema("my_schema", "1.0")
schema.add_rule(ValidationRule(
    field_path="name",
    validator=lambda x: isinstance(x, str) and len(x) > 0,
    message="Ім'я повинно бути непустим рядком",
    required=True,
    severity=ValidationSeverity.HIGH
))

# Реєстрація схеми
validation_system.register_schema(schema)

# Валідація
result = validation_system.validate({"name": "Test"}, "my_schema")

# Генерація звіту
report = validation_system.generate_report(result)
print(report)
```

## 📚 Детальна документація

### ConfigParser

`UniversalConfigParser` - основний клас для роботи з конфігураціями.

**Методи:**
- `load_file(path, format_type)` - завантажити конфігурацію
- `save_file(data, path, format_type)` - зберегти конфігурацію
- `validate_config(data, schema)` - валідувати конфігурацію
- `merge_configs(base, override)` - об'єднати конфігурації
- `convert_format(input_path, output_path)` - конвертувати формат

### FileIOUtils

`FileIOUtils` - утиліти для роботи з файлами.

**Методи:**
- `copy_file(src, dst, overwrite)` - копіювати файл
- `move_file(src, dst, overwrite)` - перемістити файл
- `delete_file(path, backup)` - видалити файл
- `find_files(directory, pattern, recursive)` - знайти файли
- `sync_directories(src, dst, delete_extra)` - синхронізувати директорії
- `batch_operation(operations, dry_run)` - пакетні операції

### ConfigManager

`ConfigManager` - менеджер конфігурацій.

**Методи:**
- `load_config(path, config_type, auto_detect_type)` - завантажити конфігурацію
- `save_config(entry, output_path, format_type)` - зберегти конфігурацію
- `list_configs(config_type)` - список конфігурацій
- `validate_config(entry)` - валідувати конфігурацію
- `merge_configs(base_entry, override_entry)` - об'єднати конфігурації

### AssetManager

`AssetManager` - менеджер асетів.

**Методи:**
- `register_asset(file_path, category, auto_detect_type)` - зареєструвати асет
- `find_assets(category, asset_type, name_pattern)` - знайти асети
- `scan_directory(directory, recursive)` - сканувати директорію
- `validate_all_assets()` - валідувати всі асети
- `export_asset_list(output_path, format_type)` - експортувати список

### ValidationSystem

`ValidationSystem` - система валідації.

**Методи:**
- `register_schema(schema)` - зареєструвати схему
- `validate(data, schema_name)` - валідувати дані
- `validate_file(file_path, schema_name)` - валідувати файл
- `generate_report(result, include_suggestions)` - згенерувати звіт

## 🧪 Тестування

Запуск тестів:

```bash
python test_config_system.py
```

Демонстрація всіх можливостей:

```bash
python demo_config_system.py
```

## 📋 Приклади використання

### Створення схеми валідації

```python
from validation_system import ValidationSchema, ValidationRule, ValidationSeverity

schema = ValidationSchema("pack_config", "1.0")

# Обов'язкове поле
schema.add_rule(ValidationRule(
    field_path="seed",
    validator=lambda x: isinstance(x, int) and x >= 0,
    message="Seed повинен бути невід'ємним цілим числом",
    required=True,
    data_type=int,
    severity=ValidationSeverity.HIGH
))

# Поле з діапазоном значень
schema.add_rule(ValidationRule(
    field_path="image_size",
    validator=lambda x: isinstance(x, list) and len(x) == 2,
    message="image_size повинен бути списком з двох елементів",
    required=True,
    data_type=list,
    severity=ValidationSeverity.HIGH
))

# Поле з дозволеними значеннями
schema.add_rule(ValidationRule(
    field_path="shots.*.export.png",
    validator=lambda x: isinstance(x, bool),
    message="png повинен бути булевим значенням",
    required=True,
    data_type=bool,
    severity=ValidationSeverity.MEDIUM
))
```

### Робота з асетами

```python
from asset_manager import AssetManager, AssetType

asset_manager = AssetManager("assets/")

# Сканування всіх асетів
all_assets = asset_manager.scan_directory("assets/", recursive=True)

# Пошук текстур
textures = asset_manager.find_assets(asset_type=AssetType.TEXTURE)

# Пошук за іменем
warrior_assets = asset_manager.find_assets(name_pattern="warrior")

# Валідація
validation_results = asset_manager.validate_all_assets()
print(f"Валідних: {len(validation_results['valid'])}")
print(f"Невалідних: {len(validation_results['invalid'])}")
print(f"Відсутніх: {len(validation_results['missing'])}")
```

### Пакетні операції з файлами

```python
from file_io_utils import FileIOUtils, FileOperation

file_utils = FileIOUtils()

operations = [
    {
        "operation": FileOperation.COPY.value,
        "source": "source/file1.txt",
        "destination": "dest/file1.txt",
        "overwrite": True
    },
    {
        "operation": FileOperation.BACKUP.value,
        "source": "important/config.yaml"
    },
    {
        "operation": FileOperation.DELETE.value,
        "source": "temp/file.txt",
        "backup": True
    }
]

result = file_utils.batch_operation(operations)
print(f"Успішних операцій: {len(result['success'])}")
print(f"Невдалих операцій: {len(result['failed'])}")
```

## 🔧 Налаштування

### Логування

```python
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Створення кастомних валідаторів

```python
def validate_color(value):
    """Валідатор для кольорів RGB"""
    if not isinstance(value, list) or len(value) != 3:
        return ValidationIssue(
            field_path="color",
            message="Колір повинен бути списком з 3 елементів",
            level=ValidationLevel.ERROR,
            severity=ValidationSeverity.HIGH
        )
    
    if not all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in value):
        return ValidationIssue(
            field_path="color",
            message="Кожен компонент кольору повинен бути числом від 0 до 1",
            level=ValidationLevel.ERROR,
            severity=ValidationSeverity.HIGH
        )
    
    return None

# Використання в схемі
schema.add_rule(ValidationRule(
    field_path="color",
    validator=lambda x: True,  # Завжди True, валідація в custom_validator
    message="Невірний колір",
    custom_validator=validate_color
))
```

## 📝 Ліцензія

MIT License

## 🤝 Внесок

Вітаються внески! Будь ласка, створюйте issues та pull requests.

## 📞 Підтримка

Якщо у вас виникли питання або проблеми, створіть issue в репозиторії.