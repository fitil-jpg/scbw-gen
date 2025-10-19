# Система освітлення та HDRI для Blender

## Огляд

Ця система надає розширені можливості освітлення для Blender, включаючи:

- **Множинні типи лайтів**: SUN, AREA, SPOT, POINT
- **HDRI середовища**: процедурні, градієнтні, зображення та пресети
- **Конфігурація YAML**: гнучка система налаштувань
- **Анімація освітлення**: динамічні ефекти
- **Атмосферні ефекти**: туман, об'ємні ефекти
- **Пресети**: готові конфігурації для різних сценаріїв

## Структура файлів

```
blender/
├── lighting_system.py          # Основна система освітлення
├── hdri_environment.py         # Система HDRI середовища
├── lighting_config.py          # Менеджер конфігурації
└── integrated_blender_pipeline.py  # Інтегрований пайплайн

configs/lighting/
├── battle_sunset_lighting.yaml    # Бойова сцена на заході сонця
├── night_battle_lighting.yaml     # Нічна бойова сцена
└── studio_clean_lighting.yaml     # Чиста студійна сцена
```

## Основні компоненти

### 1. LightingSystem

Основна система освітлення з підтримкою різних типів лайтів.

```python
from lighting_system import LightingSystem

# Ініціалізація
lighting_system = LightingSystem({"output_dir": "renders/blender"})

# Налаштування освітлення
lighting_config = {
    "hdri": {
        "type": "preset",
        "preset_name": "sunset",
        "strength": 1.2
    },
    "main_lights": [
        {
            "name": "Main_Sun",
            "type": "SUN",
            "position": [5, 5, 10],
            "energy": 3.0,
            "color": [1.0, 0.6, 0.3]
        }
    ],
    "additional_lights": [
        {
            "name": "Fill_Light",
            "type": "AREA",
            "position": [-3, -3, 8],
            "energy": 1.0,
            "color": [0.8, 0.9, 1.0],
            "size": 5.0
        }
    ]
}

lighting_system.setup_lighting(lighting_config)
```

### 2. HDRIEnvironment

Система HDRI середовища з різними пресетами.

```python
from hdri_environment import HDRIEnvironment

# Ініціалізація
hdri_system = HDRIEnvironment({"output_dir": "renders/blender"})

# Використання пресету
hdri_config = {
    "type": "preset",
    "preset_name": "sunset"
}

hdri_system.setup_hdri_environment(hdri_config)

# Додавання об'ємних ефектів
effects_config = {
    "fog": {
        "density": 0.05,
        "anisotropy": 0.0
    }
}

hdri_system.add_volumetric_effects(effects_config)
```

### 3. LightingConfigManager

Менеджер конфігурації з підтримкою YAML.

```python
from lighting_config import LightingConfigManager

# Ініціалізація
config_manager = LightingConfigManager("configs/lighting")

# Завантаження конфігурації
config = config_manager.load_config("battle_sunset_lighting.yaml")

# Створення пресету
battle_config = config_manager.create_battle_lighting_config("sunset")

# Валідація
errors = config_manager.validate_config(config)
```

## Типи лайтів

### SUN (Сонце)
```yaml
- name: "Main_Sun"
  type: "SUN"
  position: [5, 5, 10]
  energy: 3.0
  color: [1.0, 0.6, 0.3]
  angle: 0.5
  shadow:
    enabled: true
    soft_size: 0.25
```

### AREA (Площевий)
```yaml
- name: "Fill_Light"
  type: "AREA"
  position: [-3, -3, 8]
  energy: 1.0
  color: [0.8, 0.9, 1.0]
  size: 5.0
  shape: "SQUARE"
  shadow:
    enabled: true
    soft_size: 0.5
```

### SPOT (Прожектор)
```yaml
- name: "Spot_Light"
  type: "SPOT"
  position: [0, 5, 3]
  rotation: [0.2, 0, 0]
  energy: 2.5
  color: [1.0, 0.6, 0.2]
  spot_size: 0.8
  spot_blend: 0.3
  shadow:
    enabled: true
    soft_size: 0.2
```

### POINT (Точковий)
```yaml
- name: "Point_Light"
  type: "POINT"
  position: [2, 2, 1]
  energy: 1.5
  color: [1.0, 0.4, 0.1]
  shadow_soft_size: 0.2
  shadow:
    enabled: true
    soft_size: 0.3
```

## Типи HDRI

### 1. Процедурне HDRI
```yaml
hdri:
  type: "procedural"
  sky_type: "Nishita"
  sun_elevation: 0.5
  sun_rotation: 0.0
  sun_size: 0.02
  sun_intensity: 1.0
  turbidity: 2.0
  ground_albedo: 0.3
  strength: 1.0
```

### 2. Градієнтне HDRI
```yaml
hdri:
  type: "gradient"
  gradient_type: "SPHERICAL"
  colors: [[0.5, 0.7, 1.0], [1.0, 0.8, 0.6]]
  strength: 1.0
```

### 3. HDRI з зображення
```yaml
hdri:
  type: "image"
  image_path: "path/to/hdri.hdr"
  rotation: [0, 0, 0]
  scale: [1, 1, 1]
  strength: 1.0
```

### 4. Пресет HDRI
```yaml
hdri:
  type: "preset"
  preset_name: "sunset"
  strength: 1.2
```

## Доступні пресети HDRI

- **sunset** - Захід сонця з теплим освітленням
- **sunrise** - Схід сонця з яскравим освітленням
- **midday** - Полудень з ясним небом
- **overcast** - Хмарний день з м'яким освітленням
- **night** - Нічне небо з місячним освітленням
- **studio_white** - Студійне біле освітлення
- **studio_warm** - Студійне тепле освітлення
- **studio_cool** - Студійне холодне освітлення
- **space** - Космічне середовище
- **underwater** - Підводне середовище

## Атмосферні ефекти

### Туман
```yaml
atmospheric:
  fog:
    density: 0.05
    anisotropy: 0.0
```

### Об'ємне поглинання
```yaml
atmospheric:
  volume_absorption:
    density: 0.02
    color: [0.1, 0.1, 0.2]
```

### Атмосферна перспектива
```yaml
atmospheric:
  atmospheric_perspective:
    enabled: true
    distance: 50.0
    color: [0.8, 0.7, 0.6]
```

## Анімація освітлення

### Анімація лайтів
```yaml
animation:
  lights:
    Main_Sun:
      position:
        start: [5, 5, 10]
        end: [3, 3, 8]
        frames: [1, 100]
      energy:
        start: 3.0
        end: 1.5
        frames: [1, 100]
```

### Анімація HDRI
```yaml
animation:
  hdri:
    strength:
      start: 1.2
      end: 0.8
      frames: [1, 100]
    sun_elevation:
      start: 0.5
      end: 0.2
      frames: [1, 100]
```

## Використання в інтегрованому пайплайні

```python
from integrated_blender_pipeline import IntegratedBlenderPipeline

# Ініціалізація пайплайну
pipeline = IntegratedBlenderPipeline("assets", "renders/blender")

# Конфігурація шоту з освітленням
shot_config = {
    "shot_id": "battle_sunset_001",
    "lighting": {
        "preset": "battle_sunset"
    },
    "render_settings": {
        "engine": "CYCLES",
        "samples": 128,
        "resolution": [1920, 1080]
    }
}

# Обробка шоту
result = pipeline.process_shot("battle_sunset_001", shot_config)
```

## Приклади конфігурацій

### Бойова сцена на заході сонця
```yaml
hdri:
  type: "preset"
  preset_name: "sunset"
  strength: 1.2

main_lights:
  - name: "Battle_Sun"
    type: "SUN"
    position: [5, 5, 10]
    energy: 3.0
    color: [1.0, 0.6, 0.3]

additional_lights:
  - name: "Warm_Fill"
    type: "AREA"
    position: [-3, -3, 8]
    energy: 1.0
    color: [1.0, 0.8, 0.6]
    size: 5.0

atmospheric:
  fog:
    density: 0.05
    anisotropy: 0.0
```

### Нічна бойова сцена
```yaml
hdri:
  type: "preset"
  preset_name: "night"
  strength: 0.8

main_lights:
  - name: "Moon_Light"
    type: "AREA"
    position: [0, 0, 15]
    energy: 2.0
    color: [0.7, 0.8, 1.0]
    size: 10.0

additional_lights:
  - name: "Fire_Light"
    type: "POINT"
    position: [2, 2, 1]
    energy: 1.5
    color: [1.0, 0.4, 0.1]
```

### Чиста студійна сцена
```yaml
hdri:
  type: "preset"
  preset_name: "studio_white"
  strength: 1.0

main_lights:
  - name: "Key_Light"
    type: "AREA"
    position: [5, -5, 8]
    energy: 5.0
    color: [1.0, 1.0, 1.0]
    size: 3.0

additional_lights:
  - name: "Fill_Light"
    type: "AREA"
    position: [-3, -3, 6]
    energy: 2.0
    color: [1.0, 1.0, 1.0]
    size: 5.0
```

## Валідація конфігурації

Система автоматично валідує конфігурації:

```python
# Валідація конфігурації
errors = config_manager.validate_config(config)
if errors:
    print(f"Помилки валідації: {errors}")
else:
    print("Конфігурація валідна")
```

## Експорт та імпорт

### Експорт конфігурації
```python
# Експорт поточної конфігурації
pipeline.export_lighting_config("battle_sunset_001", "configs/lighting/exported.yaml")
```

### Імпорт конфігурації
```python
# Завантаження конфігурації
config = config_manager.load_config("configs/lighting/battle_sunset_lighting.yaml")
```

## Розширення системи

### Створення користувацького пресету
```python
# Створення пресету освітлення
custom_config = {
    "hdri": {
        "type": "gradient",
        "gradient_type": "SPHERICAL",
        "colors": [[0.2, 0.4, 0.6], [0.8, 0.9, 1.0]],
        "strength": 1.0
    },
    "main_lights": [
        {
            "name": "Custom_Light",
            "type": "AREA",
            "position": [0, 0, 10],
            "energy": 2.0,
            "color": [1.0, 1.0, 1.0],
            "size": 5.0
        }
    ]
}

pipeline.create_lighting_preset("custom_preset", custom_config)
```

### Створення користувацького HDRI пресету
```python
# Створення HDRI пресету
custom_hdri = {
    "type": "gradient",
    "gradient_type": "SPHERICAL",
    "colors": [[0.1, 0.1, 0.2], [0.3, 0.2, 0.4]],
    "strength": 0.8,
    "description": "Користувацький космічний HDRI"
}

hdri_system.create_custom_preset("custom_space", custom_hdri)
```

## Підтримка

Для отримання допомоги або повідомлення про помилки:

1. Перевірте логи Blender
2. Валідуйте конфігурацію
3. Переконайтеся, що всі залежності встановлені
4. Перевірте шляхи до файлів

## Ліцензія

Ця система розроблена для проекту StarCraft Battle Scene Generator та доступна під тією ж ліцензією.