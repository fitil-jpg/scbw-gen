# Assets Directory
# Директорія активів для USD сцен

Ця директорія містить всі необхідні активи для генерації USD сцен:
- Спрайти юнітів (PNG)
- Спрайти будівель (PNG) 
- Текстури рельєфу (PNG)
- Ефекти та магія (PNG)

## Структура

```
assets/
├── units/           # Юніти
│   ├── units_config.yaml
│   ├── warrior.png
│   ├── archer.png
│   ├── mage.png
│   ├── knight.png
│   └── dragon.png
├── buildings/       # Будівлі
│   ├── buildings_config.yaml
│   ├── castle.png
│   ├── tower.png
│   ├── barracks.png
│   ├── mage_tower.png
│   ├── wall.png
│   └── gate.png
├── terrain/         # Рельєф
│   ├── terrain_config.yaml
│   ├── grass_01.png
│   ├── sand_01.png
│   ├── snow_01.png
│   ├── forest_01.png
│   ├── mountain_01.png
│   ├── water_01.png
│   ├── tree_01.png
│   ├── rock_01.png
│   └── flower_01.png
└── effects/         # Ефекти
    ├── effects_config.yaml
    ├── magic_aura.png
    ├── explosion.png
    ├── heal.png
    ├── shield.png
    ├── fire.png
    ├── ice.png
    ├── dust_particle.png
    ├── smoke_particle.png
    └── sparkle_particle.png
```

## Формати файлів

### PNG спрайти
- Розмір: 32x32 до 128x128 пікселів
- Формат: PNG з прозорістю
- Колірний простір: RGBA
- Оптимізація: Збережено без стиснення для якості

### YAML конфігурації
- Кодування: UTF-8
- Формат: YAML 1.2
- Структура: Ієрархічна з метаданими

## Використання

1. Розмістіть PNG файли в відповідних піддиректоріях
2. Оновіть YAML конфігурації згідно ваших активів
3. Запустіть генератор сцени: `python generate_usd_scene.py --config scene.yaml --out out/scene.usda`

## Примітки

- Всі PNG файли мають бути з прозорістю
- Рекомендований розмір для юнітів: 32x32
- Рекомендований розмір для будівель: 64x64 до 128x128
- Текстури рельєфу можуть бути більшими: 256x256 або 512x512