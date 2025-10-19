# MVP StarCraft Scene Generator

Компактна версія генератора сцени StarCraft з модульною архітектурою.

## Розмір коду

- **MVP Core**: ~180 рядків (в межах цілі 160-180)
- **Asset Manager**: ~80 рядків (замість 508)
- **Config Manager**: ~60 рядків (замість 405)
- **Material System**: ~70 рядків
- **Asset Loader**: ~50 рядків
- **Main**: ~40 рядків

**Загальний розмір MVP**: ~480 рядків (замість 17,518)

## Структура

```
mvp_main.py              # Головний файл (40 рядків)
mvp_scene_generator.py   # Генератор сцени (180 рядків)
mvp_asset_manager.py     # Менеджер асетів (80 рядків)
mvp_config_manager.py    # Менеджер конфігурацій (60 рядків)
mvp_material_system.py   # Система матеріалів (70 рядків)
mvp_asset_loader.py      # Завантажувач асетів (50 рядків)
mvp_scene.yaml          # Конфігурація сцени
```

## Використання

### Базове використання
```bash
python mvp_main.py
```

### З Blender
```bash
blender --background --python mvp_main.py
```

## Модульна архітектура

### 1. Asset Manager
- Простий реєстр асетів
- Автоматичне визначення типів
- Сканування директорій

### 2. Config Manager
- Підтримка YAML/JSON
- Кешування конфігурацій
- Об'єднання конфігурацій

### 3. Material System
- Пресети матеріалів
- Кастомні матеріали
- Автоматичне очищення

### 4. Asset Loader
- Модульне завантаження
- Стеки асетів
- Пакети асетів

## Розширення

### Додавання нових матеріалів
```python
material_system = MVPMaterialSystem()
material = material_system.create_custom_material(
    "Custom_Material",
    base_color=(1.0, 0.0, 0.0, 1.0),
    metallic=0.5,
    roughness=0.3
)
```

### Завантаження асетів
```python
asset_loader = MVPAssetLoader()
assets = asset_loader.load_asset_stack(
    "my_assets", 
    ["texture1.png", "model1.obj"]
)
```

### Кастомна конфігурація
```yaml
# custom_scene.yaml
scene:
  name: "My Custom Scene"
buildings:
  My_Building:
    position: [0, 0, 1]
    size: 2.0
    color: [1.0, 0.0, 0.0, 1.0]
```

## Переваги MVP

1. **Компактність**: 480 рядків замість 17,518
2. **Модульність**: Легко розширювати
3. **Простота**: Зрозумілий код
4. **Гнучкість**: Підтримка різних форматів
5. **Продуктивність**: Швидкий запуск

## Міграція з повної версії

1. Замінити `asset_manager.py` на `mvp_asset_manager.py`
2. Замінити `config_manager.py` на `mvp_config_manager.py`
3. Використовувати `mvp_scene_generator.py` замість `create_starcraft_scene.py`
4. Додати `mvp_material_system.py` для матеріалів
5. Використовувати `mvp_main.py` як точку входу

## Майбутні розширення

- Підтримка анімацій
- Розширена система ефектів
- Інтеграція з Houdini
- Пакетний рендеринг
- Веб-інтерфейс