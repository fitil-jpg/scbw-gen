# YAML в Blender Python - Краткое руководство

## ✅ Статус установки

PyYAML уже установлен и работает в вашем Blender Python! Версия: 6.0.2

## 🚀 Быстрый старт

### 1. Проверка установки

```bash
# Запустите тест
blender --background --python test_yaml_in_blender.py
```

### 2. Использование в вашем проекте

Ваш проект уже настроен для работы с YAML! Вот как использовать:

```python
# В любом Blender скрипте
import bpy
import yaml
from pathlib import Path

# Загрузка конфигурации
def load_scene_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Сохранение конфигурации
def save_scene_config(config_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
```

### 3. Примеры из вашего проекта

#### Загрузка конфигурации сцены:
```python
from blender.config import load_pack_config
from pathlib import Path

# Загружаем конфигурацию
config = load_pack_config(Path('params/pack.yaml'))
print(f"Загружено {len(config.shots)} шотов")
```

#### Работа с ассетами:
```python
from blender.advanced_config_importer import AdvancedConfigImporter

# Загружаем расширенную конфигурацию
importer = AdvancedConfigImporter('scene_config.yaml')
config = importer.load_config()
assets = importer.load_asset_configs()
```

## 📁 Структура YAML файлов в проекте

```
assets/
├── buildings/buildings_config.yaml    # Конфигурация зданий
├── units/units_config.yaml           # Конфигурация юнитов
├── effects/effects_config.yaml       # Конфигурация эффектов
└── terrain/terrain_config.yaml       # Конфигурация местности

params/
└── pack.yaml                         # Основная конфигурация сцены
```

## 🔧 Доступные скрипты установки

1. **`install_yaml_for_blender.py`** - Универсальный скрипт для всех платформ
2. **`install_yaml_blender_linux.sh`** - Специализированный скрипт для Linux
3. **`test_yaml_in_blender.py`** - Тестовый скрипт (создается автоматически)

## 🧪 Тестирование

```bash
# Тест YAML в Blender
blender --background --python test_yaml_in_blender.py

# Тест конфигурации проекта
python3 -c "from blender.config import load_pack_config; from pathlib import Path; config = load_pack_config(Path('params/pack.yaml')); print('✅ Конфигурация работает!')"

# Запуск примера использования
python3 blender/example_usage.py
```

## 📚 Дополнительная документация

- **`YAML_INSTALLATION_GUIDE.md`** - Подробное руководство по установке
- **`blender/example_usage.py`** - Примеры использования в Blender
- **`blender/config.py`** - Модуль конфигурации с поддержкой YAML

## 🎯 Готовые примеры

### Создание простой сцены из YAML:

```python
import bpy
import yaml

# Загружаем конфигурацию
with open('scene_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Создаем объекты согласно конфигурации
for obj_data in config['objects']:
    if obj_data['type'] == 'cube':
        bpy.ops.mesh.primitive_cube_add(location=obj_data['position'])
    elif obj_data['type'] == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(location=obj_data['position'])
```

### Сохранение настроек сцены:

```python
import bpy
import yaml

# Собираем данные сцены
scene_data = {
    'scene_name': bpy.context.scene.name,
    'objects': [
        {
            'name': obj.name,
            'type': obj.type,
            'location': list(obj.location)
        }
        for obj in bpy.context.scene.objects
    ],
    'camera': {
        'location': list(bpy.context.scene.camera.location),
        'rotation': list(bpy.context.scene.camera.rotation_euler)
    }
}

# Сохраняем в YAML
with open('exported_scene.yaml', 'w') as f:
    yaml.dump(scene_data, f, default_flow_style=False)
```

## ⚡ Готово к использованию!

YAML полностью интегрирован в ваш Blender проект. Вы можете:

- ✅ Загружать конфигурации сцен из YAML файлов
- ✅ Сохранять настройки Blender в YAML формате
- ✅ Использовать все существующие модули конфигурации
- ✅ Создавать сложные сцены на основе YAML описаний

Начните с изучения файла `blender/example_usage.py` для практических примеров!