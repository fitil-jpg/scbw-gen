# Blender Pipeline для StarCraft Scene Generation

Цей проект надає повний пайплайн для створення та рендерингу 3D сцен у Blender на основі конфігураційних файлів.

## Основні компоненти

### 1. Enhanced Config Importer (`enhanced_config_importer.py`)
- Імпорт конфігурацій з YAML та JSON файлів
- Валідація конфігурацій відповідно до схеми
- Підтримка кешування та керування конфігураціями
- Автоматичне створення конфігурацій шотів

### 2. Enhanced Geometry Generator (`enhanced_geometry_generator.py`)
- Створення геометрії на основі параметрів шотів
- Підтримка різних типів об'єктів (будівлі, юніти, ефекти, рельєф)
- Система матеріалів з підтримкою PBR
- Анімація об'єктів (позиція, обертання, масштаб)
- Автоматичне налаштування камери та освітлення

### 3. Enhanced Render Pipeline (`enhanced_render_pipeline.py`)
- Підтримка Cycles та Eevee рендер двигунів
- Розширені налаштування якості рендерингу
- Система рендер пасів (beauty, depth, normal, diffuse, glossy)
- Пакетний рендеринг кількох шотів
- Автоматичне створення маніфестів рендерингу

### 4. Integrated Blender Pipeline (`integrated_blender_pipeline.py`)
- Об'єднує всі компоненти в єдину систему
- Повний цикл обробки: імпорт → генерація → рендеринг
- Підтримка шаблонів сцен
- Експорт сцен у різних форматах
- Валідація конфігурацій

## Встановлення та налаштування

### Вимоги
- Blender 3.0+
- Python 3.8+
- PyYAML
- NumPy (включений в Blender)

### Встановлення
1. Клонуйте репозиторій
2. Встановіть залежності:
   ```bash
   pip install PyYAML
   ```
3. Скопіюйте модулі в папку `blender/` вашого проекту

## Використання

### Базове використання

```python
from integrated_blender_pipeline import IntegratedBlenderPipeline

# Ініціалізація пайплайну
pipeline = IntegratedBlenderPipeline("assets", "renders/blender")

# Обробка шоту
result = pipeline.process_shot("my_shot", shot_config)
```

### Використання з командного рядка

```bash
# Рендеринг з шаблону
python run_blender_pipeline.py --shot-id "battle_001" --template "battle_scene_template"

# Рендеринг з конфігураційного файлу
python run_blender_pipeline.py --shot-id "custom_shot" --config "my_config.yaml"

# Пакетний рендеринг
python run_blender_pipeline.py --batch "batch_config.yaml"

# Валідація без рендерингу
python run_blender_pipeline.py --shot-id "test" --validate-only
```

### Структура конфігурації шоту

```yaml
shot_id: "my_shot"
terrain:
  type: "plane"
  size: [20, 20]
  materials:
    - name: "Ground"
      color: [0.3, 0.4, 0.2]
      roughness: 0.8

buildings:
  - name: "Command Center"
    type: "cube"
    position: [0, 0, 0]
    scale: [2, 2, 1.5]
    materials:
      - name: "Metal"
        color: [0.8, 0.8, 0.9]
        metallic: 0.8
        roughness: 0.2

units:
  - name: "Marine"
    type: "soldier"
    position: [3, 0, 0]
    scale: [1, 1, 1]
    materials:
      - name: "Armor"
        color: [0.2, 0.2, 0.3]
        metallic: 0.1
        roughness: 0.8

camera:
  position: [0, -10, 5]
  rotation: [60, 0, 0]
  focal_length: 50

lighting:
  sun_light:
    position: [10, 10, 10]
    energy: 3.0
    color: [1.0, 0.95, 0.8]

render_settings:
  engine: "CYCLES"
  samples: 128
  resolution: [1920, 1080]
  output_format: "PNG"
  denoising: true
```

## Підтримувані типи об'єктів

### Будівлі
- `cube` - Кубічна будівля
- `cylinder` - Циліндрична будівля
- `pyramid` - Пірамідальна будівля

### Юніти
- `soldier` - Солдат з тілом та головою
- `vehicle` - Транспортний засіб
- `aircraft` - Літак

### Ефекти
- `explosion` - Ефект вибуху
- `smoke` - Ефект диму
- `fire` - Ефект вогню

### Рельєф
- `plane` - Плоский рельєф
- `heightmap` - Рельєф на основі висотної карти

## Рендер двигуни

### Cycles
- Підтримка PBR матеріалів
- Денойзинг
- Налаштування якості (samples, bounces)
- Підтримка GPU та CPU

### Eevee
- Реалтайм рендеринг
- Підтримка SSAO, SSR, Bloom
- Налаштування тіней
- Оптимізація для швидкості

## Рендер паси

- `beauty` - Основний рендер
- `depth` - Пас глибини
- `normal` - Пас нормалей
- `diffuse` - Дифузне освітлення
- `glossy` - Дзеркальне освітлення

## Експорт сцен

Підтримуються наступні формати:
- `.blend` - Нативний формат Blender
- `.fbx` - Autodesk FBX
- `.obj` - Wavefront OBJ
- `.usd` - Universal Scene Description

## Приклади

### Створення бойової сцени

```python
# Завантаження шаблону
shot_config = pipeline.create_shot_from_template(
    "battle_scene_template", 
    "battle_001"
)

# Обробка
result = pipeline.process_shot("battle_001", shot_config)
```

### Пакетний рендеринг

```python
shots_config = [
    {"shot_id": "shot_001", "template": "battle_scene_template"},
    {"shot_id": "shot_002", "template": "battle_scene_template"},
    {"shot_id": "shot_003", "template": "battle_scene_template"}
]

results = pipeline.batch_process_shots(shots_config)
```

### Налаштування рендерингу

```python
render_settings = {
    "engine": "CYCLES",
    "samples": 256,
    "resolution": [3840, 2160],
    "output_format": "EXR",
    "denoising": True,
    "max_bounces": 16
}

pipeline.render_pipeline.setup_render_engine("CYCLES", render_settings)
```

## Логування

Всі модулі підтримують детальне логування:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Обмеження

- Потрібен Blender для рендерингу
- Деякі функції можуть не працювати в headless режимі
- Потрібна достатня кількість RAM для складних сцен

## Розвиток

### Додавання нових типів об'єктів

1. Створіть метод `_create_new_type_object()` в `EnhancedGeometryGenerator`
2. Додайте підтримку в `create_object()` метод
3. Оновіть схему валідації в `EnhancedConfigImporter`

### Додавання нових рендер пасів

1. Створіть метод `_create_new_render_pass()` в `EnhancedRenderPipeline`
2. Додайте підтримку в `create_render_passes()` метод
3. Оновіть документацію

## Підтримка

Для питань та проблем створюйте issues в репозиторії проекту.
