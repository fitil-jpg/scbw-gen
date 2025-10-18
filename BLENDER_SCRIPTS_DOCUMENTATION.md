# Blender Скрипти для SCBW Pipeline - Документація

## Огляд

Цей проект містить розширені Blender скрипти для створення StarCraft: Brood War сцен з автоматизованим імпортом конфігурації, генерацією геометрії та рендерингом через Cycles/Eevee.

## Структура проекту

```
blender/
├── advanced_config_importer.py      # Розширений імпортер конфігурації
├── advanced_geometry_generator.py   # Генератор детальної геометрії
├── advanced_render_pipeline.py      # Покращений рендер пайплайн
├── example_usage.py                 # Приклади використання
├── test_advanced_pipeline.py        # Тести
├── scene_generator.py               # Базовий генератор сцен
├── render_pipeline.py               # Базовий рендер пайплайн
├── generate_passes.py               # CLI для генерації пасів
└── startup_script.py                # Скрипт запуску
```

## Основні компоненти

### 1. AdvancedConfigImporter

**Призначення**: Імпорт та валідація конфігурацій з YAML/JSON файлів.

**Ключові функції**:
- Завантаження основних конфігурацій
- Завантаження конфігурацій асетів (будівлі, юніти, ефекти)
- Валідація структури конфігурації
- Підтримка попередньо визначених палітр кольорів
- Експорт зведень конфігурації

**Приклад використання**:
```python
from blender.advanced_config_importer import AdvancedConfigImporter

# Завантаження конфігурації
importer = AdvancedConfigImporter("config.yaml")
config = importer.load_config()
assets = importer.load_asset_configs()

# Отримання шоту
shot = importer.get_shot_config("shot_001")
colors = importer.get_palette_colors(shot)
```

### 2. AdvancedGeometryGenerator

**Призначення**: Створення детальної геометрії на основі параметрів шотів.

**Ключові функції**:
- Генерація території з рельєфом та деталями
- Створення будівель різних типів
- Генерація юнітів з різними расами (Terran, Zerg, Protoss)
- Створення спеціальних ефектів (портали, вибухи)
- Розширений UI з HUD елементами

**Приклад використання**:
```python
from blender.advanced_geometry_generator import AdvancedGeometryGenerator

# Створення генератора
generator = AdvancedGeometryGenerator(importer)

# Генерація сцени
generator.setup_advanced_scene(shot_config)
```

### 3. AdvancedRenderPipeline

**Призначення**: Покращений рендеринг з підтримкою Cycles та Eevee.

**Ключові функції**:
- Мульти-пас рендеринг (beauty, mask, depth, normal, AO, emission)
- Спеціалізовані рендерери для Cycles та Eevee
- Налаштування якості рендерингу
- Композитор для мульти-площинного EXR
- Автоматичне створення маніфестів

**Приклад використання**:
```python
from blender.advanced_render_pipeline import CyclesRenderer, EeveeRenderer

# Cycles рендеринг
cycles_renderer = CyclesRenderer(output_dir)
paths = cycles_renderer.render_cycles_passes("shot_001", 1, "high")

# Eevee рендеринг
eevee_renderer = EeveeRenderer(output_dir)
paths = eevee_renderer.render_eevee_passes("shot_001", 1)
```

## Формат конфігурації

### Основна конфігурація (YAML/JSON)

```yaml
seed: 1337
image_size: [1920, 1080]
shots:
  - id: shot_001
    palette: ArmyColors  # або [[0.1,0.2,0.3], [0.4,0.5,0.6]]
    portal:
      center: [0.5, 0.5]
      radius: 0.2
      falloff: 0.25
    left_cluster:
      rect: [0.1, 0.4]
      count: 8
      size: [20, 40]
      unit_types: ['marine', 'firebat']
    right_cluster:
      rect: [0.6, 0.6]
      count: 6
      size: [18, 36]
      unit_types: ['zergling', 'hydralisk']
    buildings:
      - type: command_center
        position: [0.2, 0.2]
        owner: left
    hud:
      left:
        Race: Terran
        M: 2500
        G: 1200
        Supply: [65, 85]
        APM: 200
    export:
      png: true
      exr16: true
      exr32: false
```

### Конфігурація асетів

**Будівлі** (`assets/buildings/buildings_config.yaml`):
```yaml
buildings:
  command_center:
    sprite: "command_center.png"
    size: [128, 128]
    scale: 2.0
    health: 500
    cost: 500
  barracks:
    sprite: "barracks.png"
    size: [80, 80]
    scale: 1.2
    health: 300
    cost: 200
```

**Юніти** (`assets/units/units_config.yaml`):
```yaml
units:
  marine:
    sprite: "marine.png"
    size: [32, 32]
    health: 40
    damage: 6
    speed: 1.5
  zergling:
    sprite: "zergling.png"
    size: [24, 24]
    health: 35
    damage: 5
    speed: 2.0
```

## Попередньо визначені палітри

- `ArmyColors`: Синя, червона, зелена армії
- `TerranColors`: Металічні кольори
- `ZergColors`: Органічні зелені тони
- `ProtossColors`: Золотий, блакитний, фіолетовий

## Рендер паси

### Доступні паси

1. **beauty** - Основний красивий пас
2. **mask_units** - Маска юнітів
3. **mask_buildings** - Маска будівель
4. **mask_terrain** - Маска території
5. **depth** - Пас глибини
6. **normal** - Пас нормалей
7. **ao** - Ambient Occlusion
8. **emission** - Пас емісії

### Якість рендерингу

**Cycles**:
- `low`: 64 семпли, базові налаштування
- `medium`: 256 семплів, середня якість
- `high`: 512 семплів, висока якість
- `ultra`: 1024 семпли, максимальна якість

**Eevee**:
- Оптимізовані налаштування для швидкого рендерингу
- Підтримка bloom, SSR, soft shadows
- Volumetric lighting та motion blur

## Використання

### Базове використання

```python
from blender.advanced_config_importer import AdvancedConfigImporter
from blender.advanced_geometry_generator import AdvancedGeometryGenerator
from blender.advanced_render_pipeline import CyclesRenderer

# 1. Завантаження конфігурації
importer = AdvancedConfigImporter("config.yaml")
config = importer.load_config()
assets = importer.load_asset_configs()

# 2. Генерація геометрії
generator = AdvancedGeometryGenerator(importer)
shot = importer.get_shot_config("shot_001")
generator.setup_advanced_scene(shot)

# 3. Рендеринг
renderer = CyclesRenderer(Path("output"))
paths = renderer.render_cycles_passes("shot_001", 1, "high")
```

### CLI використання

```bash
# Запуск через Blender
blender --background --python blender/startup_script.py -- \
  --config params/pack.yaml \
  --shot shot_001 \
  --output renders/blender

# Прямий запуск
python blender/generate_passes.py \
  --config config.yaml \
  --shot shot_001 \
  --output renders
```

### Пакетна обробка

```python
# Обробка кількох шотів
for shot in config['shots']:
    generator.setup_advanced_scene(shot)
    paths = renderer.render_cycles_passes(shot['id'], 1, 'medium')
```

## Тестування

```bash
# Запуск тестів
python blender/test_advanced_pipeline.py

# Запуск прикладів
python blender/example_usage.py
```

## Вимоги

- Blender 3.0+ з Python API
- Python 3.7+
- PyYAML для YAML конфігурацій
- Pillow для обробки зображень
- OpenEXR для мульти-площинного EXR

## Встановлення

1. Клонуйте репозиторій
2. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```
3. Налаштуйте Blender для використання скриптів

## Оцінка складності

### Кількість рядків коду

| Компонент | Рядків коду | Складність |
|-----------|-------------|------------|
| AdvancedConfigImporter | ~200 | Середня |
| AdvancedGeometryGenerator | ~400 | Висока |
| AdvancedRenderPipeline | ~350 | Висока |
| Приклади та тести | ~300 | Низька |
| **Загалом** | **~1250** | **Середня-Висока** |

### Час розробки

- **Базовий функціонал**: 2-3 дні
- **Розширена геометрія**: 3-4 дні
- **Покращений рендеринг**: 2-3 дні
- **Тестування та документація**: 1-2 дні
- **Загалом**: 8-12 днів

### Складність завдання

**Середня-Висока** - завдання вимагає:
- Глибокого розуміння Blender API
- Знань 3D геометрії та матеріалів
- Досвіду з рендерингом та композитингом
- Розуміння ігрових асетів та стилістики

### Переваги

✅ **Модульна архітектура** - легко розширювати
✅ **Підтримка різних форматів** - YAML/JSON
✅ **Гнучка конфігурація** - багато параметрів
✅ **Висока якість рендерингу** - Cycles/Eevee
✅ **Автоматизація** - мінімум ручної роботи
✅ **Тестування** - покриття тестами

### Обмеження

⚠️ **Залежність від Blender** - потребує встановленого Blender
⚠️ **Складність налаштування** - багато параметрів
⚠️ **Час рендерингу** - висока якість = довгий час
⚠️ **Пам'ять** - великі сцени потребують багато RAM

## Розвиток

### Можливі покращення

1. **Анімація** - додати підтримку анімації юнітів
2. **Частинки** - ефекти частинок для вибухів
3. **Процедурна геометрія** - більше варіацій моделей
4. **Оптимізація** - покращення швидкості рендерингу
5. **UI** - графічний інтерфейс для налаштування

### Інтеграція

- **Houdini** - експорт в Houdini формати
- **Maya** - підтримка Maya
- **Unreal Engine** - експорт для UE
- **Unity** - експорт для Unity

## Підтримка

Для питань та проблем створюйте issues в репозиторії або звертайтесь до команди розробки.

---

**Версія**: 1.0.0  
**Останнє оновлення**: 2024  
**Автор**: Blender SCBW Pipeline Team