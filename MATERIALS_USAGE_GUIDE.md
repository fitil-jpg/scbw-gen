# Керівництво з використання матеріалів та текстур

## Огляд

Цей проект містить повний набір інструментів для роботи з матеріалами, текстурами та UV-розгортанням у Blender для створення StarCraft Brood War сцен.

## Структура проекту

```
blender/
├── material_generator.py          # Генератор матеріалів
├── enhanced_scene_generator.py    # Покращений генератор сцен
├── enhanced_render_pipeline.py    # Рендер пайплайн
└── scene_generator.py             # Базовий генератор сцен

demo_materials.py                  # Демонстраційний скрипт
MATERIALS_AND_TEXTURES_GUIDE.md    # Детальний гід
MATERIALS_USAGE_GUIDE.md           # Цей файл
```

## Швидкий старт

### 1. Запуск демонстрації

```bash
# Запуск демонстраційного скрипта
blender --background --python demo_materials.py
```

### 2. Використання в існуючому коді

```python
from blender.material_generator import StarCraftMaterialGenerator
from blender.enhanced_scene_generator import EnhancedStarCraftSceneGenerator

# Створення генератора матеріалів
material_gen = StarCraftMaterialGenerator()

# Створення матеріалу для юніта
marine_material = material_gen.create_unit_material(
    unit_type="marine",
    team_color=(0.2, 0.4, 0.8),
    metallic=0.2,
    roughness=0.7
)

# Застосування матеріалу до об'єкта
obj.data.materials.append(marine_material)
```

## Основні компоненти

### 1. StarCraftMaterialGenerator

Головний клас для створення матеріалів.

#### Методи:

- `create_unit_material(unit_type, team_color, metallic, roughness)` - матеріали для юнітів
- `create_terrain_material(terrain_type)` - матеріали для території
- `create_ui_material(ui_type)` - матеріали для UI
- `create_effect_material(effect_type)` - матеріали для ефектів
- `create_pbr_material(texture_paths, material_name)` - PBR матеріали з текстур
- `apply_uv_mapping(obj, mapping_type)` - UV-розгортання

#### Приклад використання:

```python
# Створення матеріалу для території
grass_material = material_gen.create_terrain_material("grass")

# Створення PBR матеріалу
texture_paths = {
    "albedo": "textures/terrain_albedo.png",
    "normal": "textures/terrain_normal.png",
    "roughness": "textures/terrain_roughness.png",
    "metallic": "textures/terrain_metallic.png"
}
pbr_material = material_gen.create_pbr_material(texture_paths, "Terrain_PBR")

# UV-розгортання
material_gen.apply_uv_mapping(obj, "smart")
```

### 2. EnhancedStarCraftSceneGenerator

Покращений генератор сцен з підтримкою матеріалів.

#### Основні функції:

- Автоматичне створення матеріалів для всіх об'єктів
- Підтримка різних рас (Terran, Protoss, Zerg)
- Створення UI елементів з матеріалами
- Генерація спеціальних ефектів

#### Приклад використання:

```python
# Конфігурація шоту
shot_config = {
    "terrain_type": "grass",
    "left_cluster": {
        "rect": [0.2, 0.5],
        "count": 5,
        "size": [16, 32],
        "unit_type": "marine"
    },
    "right_cluster": {
        "rect": [0.8, 0.5],
        "count": 5,
        "size": [16, 32],
        "unit_type": "zealot"
    },
    "hud": True,
    "portal": {
        "center": [0.5, 0.5],
        "radius": 0.2
    }
}

# Створення генератора
config = type('Config', (), {'image_size': [1920, 1080]})()
generator = EnhancedStarCraftSceneGenerator(config)

# Генерація сцени
generator.setup_scene(shot_config)
```

## Типи матеріалів

### 1. Матеріали юнітів

Підтримувані типи:
- `marine` - морпіхи (Terran)
- `zealot` - зелоти (Protoss)
- `zergling` - зерглінги (Zerg)

Кольори команд:
- Terran: (0.2, 0.4, 0.8) - синій
- Protoss: (0.8, 0.2, 0.2) - червоний
- Zerg: (0.4, 0.8, 0.2) - зелений

### 2. Матеріали території

Підтримувані типи:
- `grass` - трава
- `dirt` - земля
- `stone` - камінь
- `metal` - метал
- `sand` - пісок

### 3. UI матеріали

Підтримувані типи:
- `hud` - основний HUD
- `button` - кнопки
- `panel` - панелі

### 4. Матеріали ефектів

Підтримувані типи:
- `portal` - портали
- `explosion` - вибухи
- `shield` - щити

## UV-розгортання

### Підтримувані типи:

- `smart` - розумне розгортання (за замовчуванням)
- `cube` - кубічна проекція
- `cylinder` - циліндрична проекція
- `sphere` - сферична проекція

### Приклад:

```python
# Розумне UV-розгортання
material_gen.apply_uv_mapping(obj, "smart")

# Кубічна проекція
material_gen.apply_uv_mapping(obj, "cube")
```

## Процедурні матеріали

### Створення власних процедурних матеріалів:

```python
def create_custom_material():
    material = bpy.data.materials.new(name="Custom_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Ваші ноди тут
    # ...
    
    return material
```

### Доступні процедурні текстури:

- Noise (шум)
- Voronoi (діаграма Вороного)
- Wave (хвилі)
- Brick (цегла)
- Checker (шахівниця)
- Magic (магічна)

## PBR матеріали

### Структура текстурних карт:

```
textures/
├── material_albedo.png      # Основний колір
├── material_normal.png      # Карта нормалей
├── material_roughness.png   # Карта шорсткості
├── material_metallic.png    # Карта металевості
└── material_emission.png    # Карта емісії
```

### Використання:

```python
texture_paths = {
    "albedo": "textures/terrain_albedo.png",
    "normal": "textures/terrain_normal.png",
    "roughness": "textures/terrain_roughness.png",
    "metallic": "textures/terrain_metallic.png"
}

pbr_material = material_gen.create_pbr_material(texture_paths, "Terrain_PBR")
```

## Анімація матеріалів

### Анімація параметрів:

```python
# Анімація кольору
color_node = nodes.get("RGB")
color_node.outputs[0].default_value = (1.0, 0.0, 0.0, 1.0)
color_node.outputs[0].keyframe_insert(data_path="default_value", frame=1)
color_node.outputs[0].default_value = (0.0, 1.0, 0.0, 1.0)
color_node.outputs[0].keyframe_insert(data_path="default_value", frame=100)

# Анімація шкали текстури
mapping_node = nodes.get("Mapping")
mapping_node.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
mapping_node.inputs["Scale"].keyframe_insert(data_path="default_value", frame=1)
mapping_node.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
mapping_node.inputs["Scale"].keyframe_insert(data_path="default_value", frame=100)
```

## Оптимізація

### Поради для кращої продуктивності:

1. **Використовуйте кеш матеріалів**:
```python
# Матеріали автоматично кешуються
material_gen.clear_material_cache()  # Очищення кешу
```

2. **Оптимізуйте UV-розгортання**:
```python
# Використовуйте відповідний тип розгортання
material_gen.apply_uv_mapping(obj, "smart")  # Для складних об'єктів
material_gen.apply_uv_mapping(obj, "cube")   # Для простих об'єктів
```

3. **Налаштуйте рендеринг**:
```python
# Для швидкого попереднього перегляду
cycles.samples = 32
cycles.use_denoising = True

# Для фінального рендерингу
cycles.samples = 128
cycles.max_bounces = 12
```

## Приклади використання

### 1. Створення простої сцени

```python
from blender.material_generator import StarCraftMaterialGenerator

# Ініціалізація
material_gen = StarCraftMaterialGenerator()

# Створення матеріалів
terrain_material = material_gen.create_terrain_material("grass")
marine_material = material_gen.create_unit_material("marine", (0.2, 0.4, 0.8))

# Створення об'єктів
bpy.ops.mesh.primitive_plane_add(size=20)
terrain = bpy.context.object
terrain.data.materials.append(terrain_material)

bpy.ops.mesh.primitive_cube_add(size=1)
marine = bpy.context.object
marine.data.materials.append(marine_material)

# UV-розгортання
material_gen.apply_uv_mapping(terrain, "smart")
material_gen.apply_uv_mapping(marine, "smart")
```

### 2. Створення складного PBR матеріалу

```python
# Підготовка текстур
texture_paths = {
    "albedo": "textures/metal_albedo.png",
    "normal": "textures/metal_normal.png",
    "roughness": "textures/metal_roughness.png",
    "metallic": "textures/metal_metallic.png"
}

# Створення PBR матеріалу
pbr_material = material_gen.create_pbr_material(texture_paths, "Metal_PBR")

# Застосування до об'єкта
obj.data.materials.append(pbr_material)
```

### 3. Створення анімованого ефекту

```python
# Створення матеріалу ефекту
portal_material = material_gen.create_effect_material("portal")

# Створення об'єкта
bpy.ops.mesh.primitive_uv_sphere_add(radius=1)
portal = bpy.context.object
portal.data.materials.append(portal_material)

# Анімація
portal.rotation_euler = (0, 0, 0)
portal.keyframe_insert(data_path="rotation_euler", frame=1)
portal.rotation_euler = (0, 0, 3.14159 * 2)
portal.keyframe_insert(data_path="rotation_euler", frame=100)
```

## Налагодження

### Поширені проблеми:

1. **Матеріал не застосовується**:
   - Перевірте, чи об'єкт має меш
   - Переконайтеся, що матеріал створено правильно

2. **Текстури не завантажуються**:
   - Перевірте шляхи до файлів
   - Переконайтеся, що файли існують

3. **UV-розгортання не працює**:
   - Перевірте, чи об'єкт в режимі редагування
   - Спробуйте інший тип розгортання

### Логування:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Логи будуть показувати процес створення матеріалів
```

## Розширення функціональності

### Додавання нових типів матеріалів:

```python
def create_custom_unit_material(self, unit_type, team_color):
    # Ваша реалізація
    pass

# Додавання до класу
StarCraftMaterialGenerator.create_custom_unit_material = create_custom_unit_material
```

### Додавання нових типів UV-розгортання:

```python
def custom_uv_mapping(self, obj):
    # Ваша реалізація
    pass

# Додавання до класу
StarCraftMaterialGenerator.custom_uv_mapping = custom_uv_mapping
```

## Висновок

Цей набір інструментів надає повну підтримку для створення матеріалів, текстур та UV-розгортання в Blender для StarCraft Brood War сцен. Використовуйте їх як основу для створення власних матеріалів та ефектів.

Для додаткової інформації дивіться `MATERIALS_AND_TEXTURES_GUIDE.md`.