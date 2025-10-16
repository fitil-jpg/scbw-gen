# USD Scene Generator
# Генератор USD сцен з юнітами та будівлями

USD+Python headless рішення для генерації 3D сцен з юнітами, будівлями та ефектами.

## Особливості

- ✅ **Headless генерація** - без GUI, тільки Python + USD
- ✅ **Конфігурація через YAML** - легке налаштування сцен
- ✅ **Підтримка спрайтів** - PNG текстури для юнітів та будівель
- ✅ **Формації юнітів** - лінійні, дугові, випадкові розміщення
- ✅ **Система власності** - різні армії з кольорами
- ✅ **Ефекти та магія** - візуальні ефекти для сцени
- ✅ **Модульна архітектура** - окремі менеджери для різних типів об'єктів

## Встановлення

```bash
# Встановити залежності
pip install -r requirements.txt

# Або вручну
pip install usd-core pyyaml numpy Pillow
```

## Швидкий старт

```bash
# Згенерувати сцену з конфігурації
python generate_usd_scene.py --config scene.yaml --out out/scene.usda

# Запустити приклади
python example_usage.py
```

## Структура проекту

```
├── generate_usd_scene.py    # Основний генератор
├── usd_utils.py            # USD утиліти
├── scene.yaml              # Конфігурація сцени
├── example_usage.py        # Приклади використання
├── assets/                 # Активі (спрайти, текстури)
│   ├── units/             # Юніти
│   ├── buildings/         # Будівлі
│   ├── terrain/           # Рельєф
│   └── effects/           # Ефекти
└── out/                   # Згенеровані USD файли
```

## Конфігурація сцени

### scene.yaml

```yaml
scene:
  name: "Battle Scene"
  size: [100, 100]
  terrain:
    type: "grassland"
    height_variation: 0.2
    texture: "terrain/grass_01.png"
  
  lighting:
    sun_angle: [45, 30]
    ambient: 0.3
    sun_intensity: 1.0

units:
  army_1:
    color: [0.2, 0.4, 0.8]
    spawn_area: [10, 10, 30, 30]
    units:
      - type: "warrior"
        count: 15
        formation: "line"
        spacing: 2.0
      - type: "archer" 
        count: 10
        formation: "arc"
        spacing: 1.5

buildings:
  - type: "castle"
    position: [50, 50]
    rotation: 0
    scale: 1.0
    owner: "neutral"

effects:
  - type: "magic_aura"
    position: [50, 50]
    radius: 10
    color: [1.0, 0.0, 1.0]
    intensity: 0.7
```

## Формати активів

### PNG спрайти
- **Юніти**: 32x32 пікселів
- **Будівлі**: 64x64 до 128x128 пікселів  
- **Текстури рельєфу**: 256x256 або 512x512 пікселів
- **Ефекти**: 32x32 до 64x64 пікселів

### YAML конфігурації
- Кодування: UTF-8
- Формат: YAML 1.2
- Структура: Ієрархічна з метаданими

## API

### USDSceneGenerator

```python
from generate_usd_scene import USDSceneGenerator

# Створити генератор
generator = USDSceneGenerator("scene.yaml", "out/scene.usda")

# Згенерувати сцену
success = generator.generate_scene()
```

### USD утиліти

```python
from usd_utils import USDUnitManager, USDBuildingManager

# Створити менеджери
unit_manager = USDUnitManager(stage)
building_manager = USDBuildingManager(stage)

# Створити юніта
unit_path = unit_manager.create_unit_sprite("warrior", (10, 10), [0.2, 0.4, 0.8])

# Створити будівлю
building_path = building_manager.create_building("castle", (50, 50), "neutral")
```

## Типи юнітів

- **warrior** - Воїн (1.0x масштаб)
- **archer** - Лучник (0.8x масштаб)
- **mage** - Маг (0.9x масштаб)
- **knight** - Лицар (1.2x масштаб)
- **dragon** - Дракон (2.0x масштаб)

## Формації юнітів

- **line** - Лінійна формація
- **arc** - Дугова формація
- **back** - Формація ззаду
- **random** - Випадкове розміщення

## Типи будівель

- **castle** - Замок (2.0x масштаб)
- **tower** - Вежа (1.0x масштаб)
- **barracks** - Казарми (1.2x масштаб)
- **mage_tower** - Вежа магів (1.1x масштаб)
- **wall** - Стіна (0.8x масштаб)
- **gate** - Ворота (1.0x масштаб)

## Типи рельєфу

- **grassland** - Зелені луки
- **desert** - Пустеля
- **snow** - Сніжна місцевість
- **forest** - Ліс
- **mountain** - Гори
- **water** - Водна поверхня

## Ефекти

- **magic_aura** - Магічна аура
- **explosion** - Вибух
- **heal** - Лікування
- **shield** - Захисний щит
- **fire** - Вогонь
- **ice** - Лід

## Переглядачі USD

Для перегляду згенерованих USD файлів:

- **USD Composer** (безкоштовний)
- **Blender** з USD плагіном
- **Houdini**
- **Omniverse Create/View**
- **Maya** з USD плагіном

## Приклади

```bash
# Базовий приклад
python generate_usd_scene.py --config scene.yaml --out out/scene.usda

# Запустити всі приклади
python example_usage.py

# Створити кастомну сцену
python -c "
from usd_utils import *
from pxr import Usd
stage = Usd.Stage.CreateNew('custom.usda')
unit_manager = USDUnitManager(stage)
unit_manager.create_unit_sprite('warrior', (0, 0), [1, 0, 0])
stage.Save()
"
```

## Розширення

### Додати новий тип юніта

1. Додати PNG спрайт в `assets/units/`
2. Оновити `assets/units/units_config.yaml`
3. Використовувати в `scene.yaml`

### Додати новий тип будівлі

1. Додати PNG спрайт в `assets/buildings/`
2. Оновити `assets/buildings/buildings_config.yaml`
3. Використовувати в `scene.yaml`

### Додати новий ефект

1. Додати PNG спрайт в `assets/effects/`
2. Оновити `assets/effects/effects_config.yaml`
3. Використовувати в `scene.yaml`

## Ліцензія

Дивіться LICENSE файл для деталей.