# USD Scene Generator - Готовий до використання! 🎉

Повнофункціональний USD+Python headless генератор сцен з юнітами та будівлями.

## ✅ Що вже готово

- **`generate_usd_scene.py`** - основний генератор сцен
- **`usd_utils.py`** - утиліти для роботи з USD
- **`scene.yaml`** - конфігурація сцени
- **`assets/`** - структура активів з конфігураціями
- **`example_usage.py`** - приклади використання
- **`test_generator.py`** - тести (всі пройдено ✅)

## 🚀 Швидкий старт

```bash
# 1. Встановити залежності
pip install usd-core pyyaml numpy Pillow

# 2. Згенерувати сцену
python generate_usd_scene.py --config scene.yaml --out out/scene.usda

# 3. Запустити приклади
python example_usage.py

# 4. Запустити тести
python test_generator.py
```

## 📁 Структура проекту

```
├── generate_usd_scene.py      # 🎯 Основний генератор
├── usd_utils.py              # 🔧 USD утиліти
├── scene.yaml                # ⚙️ Конфігурація сцени
├── example_usage.py          # 📚 Приклади
├── test_generator.py         # 🧪 Тести
├── assets/                   # 🎨 Активі
│   ├── units/               # 👥 Юніти (PNG + YAML)
│   ├── buildings/           # 🏰 Будівлі (PNG + YAML)
│   ├── terrain/             # 🌍 Рельєф (PNG + YAML)
│   └── effects/             # ✨ Ефекти (PNG + YAML)
└── out/                     # 📤 Згенеровані USD файли
```

## 🎮 Що можна генерувати

### Юніти (5 типів)
- **warrior** - Воїн (32x32 PNG)
- **archer** - Лучник (28x28 PNG)  
- **mage** - Маг (30x30 PNG)
- **knight** - Лицар (36x36 PNG)
- **dragon** - Дракон (64x64 PNG)

### Будівлі (6 типів)
- **castle** - Замок (128x128 PNG)
- **tower** - Вежа (64x64 PNG)
- **barracks** - Казарми (80x80 PNG)
- **mage_tower** - Вежа магів (72x72 PNG)
- **wall** - Стіна (32x32 PNG)
- **gate** - Ворота (48x48 PNG)

### Рельєф (6 типів)
- **grassland** - Зелені луки
- **desert** - Пустеля
- **snow** - Сніжна місцевість
- **forest** - Ліс
- **mountain** - Гори
- **water** - Водна поверхня

### Ефекти (6 типів)
- **magic_aura** - Магічна аура
- **explosion** - Вибух
- **heal** - Лікування
- **shield** - Захисний щит
- **fire** - Вогонь
- **ice** - Лід

## 🎯 Формації юнітів

- **line** - Лінійна формація
- **arc** - Дугова формація  
- **back** - Формація ззаду
- **random** - Випадкове розміщення

## 📝 Приклад конфігурації

```yaml
scene:
  name: "Battle Scene"
  size: [100, 100]
  terrain:
    type: "grassland"
    texture: "terrain/grass_01.png"

units:
  army_1:
    color: [0.2, 0.4, 0.8]  # Сині
    spawn_area: [10, 10, 30, 30]
    units:
      - type: "warrior"
        count: 15
        formation: "line"
      - type: "archer"
        count: 10
        formation: "arc"

buildings:
  - type: "castle"
    position: [50, 50]
    owner: "neutral"

effects:
  - type: "magic_aura"
    position: [50, 50]
    radius: 10
```

## 🔧 API використання

```python
from generate_usd_scene import USDSceneGenerator

# Простий спосіб
generator = USDSceneGenerator("scene.yaml", "out/scene.usda")
generator.generate_scene()

# Розширений спосіб
from usd_utils import USDUnitManager, USDBuildingManager

unit_manager = USDUnitManager(stage)
unit_manager.create_unit_sprite("warrior", (10, 10), [0.2, 0.4, 0.8])

building_manager = USDBuildingManager(stage)
building_manager.create_building("castle", (50, 50), "neutral")
```

## 🎨 Формати активів

### PNG спрайти
- **Розміри**: 32x32 до 128x128 пікселів
- **Формат**: PNG з прозорістю (RGBA)
- **Розташування**: `assets/{type}/{name}.png`

### YAML конфігурації
- **Кодування**: UTF-8
- **Структура**: Ієрархічна з метаданими
- **Розташування**: `assets/{type}/{type}_config.yaml`

## 👀 Переглядачі USD

Для перегляду згенерованих файлів:

- **USD Composer** (безкоштовний) ⭐
- **Blender** з USD плагіном
- **Houdini**
- **Omniverse Create/View**
- **Maya** з USD плагіном

## 🧪 Тестування

```bash
# Запустити всі тести
python test_generator.py

# Результат: 5/5 тестів пройдено ✅
```

## 📦 Встановлення USD

```bash
# Основний пакет
pip install usd-core

# Додаткові залежності
pip install pyyaml numpy Pillow

# Або все одразу
pip install -r requirements.txt
```

## 🎯 Готово до використання!

1. ✅ Код написано
2. ✅ Структура створена  
3. ✅ Конфігурації готові
4. ✅ Тести пройдено
5. ✅ Документація написана

**Просто встановіть USD залежності та запускайте!** 🚀

## 📞 Підтримка

- Всі файли готові до використання
- Тести показують, що все працює
- Документація детальна
- Приклади включені

**Генеруйте сцени з юнітами та будівлями в USD!** 🎮✨