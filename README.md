# USD Scene Generator and Renderer

Цей проект демонструє генерацію USD сцени та її рендеринг з використанням OpenUSD та Storm рендер-делегата.

## Файли проекту

- `build_scene.py` - Генератор USD сцени
- `scene.usda` - Згенерована USD сцена
- `check_scene.py` - Скрипт для аналізу сцени
- `render_scene.py` - Скрипт для рендерингу (потребує повний OpenUSD)

## Встановлення залежностей

```bash
pip3 install usd-core
```

## Генерація сцени

```bash
python3 build_scene.py
```

Це створить файл `scene.usda` з простою 3D сценою, що містить:
- Куб в центрі координат
- Дальнє світло з налаштованим поворотом
- Камеру з позицією та орієнтацією

## Перевірка сцени

```bash
python3 check_scene.py
```

Це покаже детальну інформацію про всі примітиви в сцені.

## Рендеринг

Для рендерингу USD сцен рекомендується використовувати:

### Варіант 1: usdrecord (якщо доступний)
```bash
usdrecord scene.usda output.png --camera /World/Camera --width 800 --height 600
```

### Варіант 2: Blender
```bash
# Встановлення Blender
brew install --cask blender

# Відкрити сцену в Blender
blender --background --python -c "
import bpy
bpy.ops.wm.usd_import(filepath='scene.usda')
bpy.ops.render.render(write_still=True, filepath='output.png')
"
```

### Варіант 3: Houdini (якщо доступний)
```bash
# Відкрити сцену в Houdini
houdini scene.usda
```

## Структура сцени

Сцена містить:
- **World** - кореневий контейнер
- **Cube** - куб розміром 2x2x2 в центрі
- **Light** - дальнє світло з поворотом (-45°, 45°, 0°)
- **Camera** - камера в позиції (5, 5, 5) з поворотом (-30°, -45°, 0°)

## Примітки

- Storm рендер-делегат є частиною повного OpenUSD SDK
- `usd-core` Python пакет містить тільки базові функції USD
- Для повного рендерингу потрібен повний OpenUSD SDK або сумісний 3D додаток