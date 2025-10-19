# Система анімації Blender SCBW Pipeline

Повнофункціональна система анімації для створення кінематографічних послідовностей у стилі StarCraft: Brood War.

## 🎬 Основні можливості

### Ключові кадри (Keyframes)
- **Позиція** - анімація руху об'єктів
- **Обертання** - анімація поворотів
- **Масштаб** - анімація зміни розміру
- **FOV камери** - анімація поля зору
- **Енергія світла** - анімація освітлення

### Криві камери (Camera Curves)
- **Кругові криві** - обліт навколо об'єкта
- **Спіральні криві** - підйом/спуск з обертанням
- **Кастомні криві** - довільні шляхи Безьє
- **Автоматичне наведення** - камера дивиться вздовж кривої

### Рендеринг послідовностей
- **Підтримка Cycles та Eevee**
- **Мульти-пас рендеринг**
- **Пакетне створення**
- **Експорт у різні формати**

## 📁 Структура файлів

```
blender/
├── animation_system.py          # Основна система анімації
├── animation_examples.py        # Приклади використання
├── integrated_animation_pipeline.py  # Інтегрований пайплайн
└── advanced_render_pipeline.py  # Розширений рендеринг

assets/animations/
└── animations_config.yaml      # Конфігурація анімацій

demo_animation_system.py         # Демонстраційний скрипт
```

## 🚀 Швидкий старт

### 1. Базове використання

```python
from animation_system import KeyframeManager, CameraCurveAnimator

# Створення менеджера ключових кадрів
keyframe_manager = KeyframeManager()

# Анімація об'єкта
keyframes = [
    {'frame': 1, 'type': 'location', 'value': (0, 0, 0)},
    {'frame': 30, 'type': 'location', 'value': (5, 5, 5)},
    {'frame': 60, 'type': 'location', 'value': (0, 0, 0)}
]
keyframe_manager.add_keyframes_sequence(obj, keyframes)
```

### 2. Анімація камери по кривій

```python
from animation_system import CameraCurveAnimator

camera_animator = CameraCurveAnimator()

# Кругова крива
curve = camera_animator.create_circular_camera_path(
    center=Vector((0, 0, 0)),
    radius=15.0,
    height=8.0
)

# Анімація камери
camera_animator.animate_camera_along_curve(
    camera, curve, start_frame=1, end_frame=100, follow_curve=True
)
```

### 3. Рендеринг послідовності

```python
from animation_system import AnimationSequenceRenderer

renderer = AnimationSequenceRenderer(Path("renders/animation"))

# Налаштування рендерингу
render_settings = {
    'engine': 'CYCLES',
    'samples': 128,
    'resolution': [1920, 1080],
    'output_format': 'PNG'
}

# Рендеринг
rendered_files = renderer.render_animation_sequence(
    "my_shot", 1, 100, render_settings
)
```

## 🎯 Шаблони анімацій

### Battle Sequence
Анімація битви з рухом одиниць та круговою камерою:

```yaml
battle_sequence:
  duration: 100
  camera:
    type: "circular"
    radius: 20.0
    height: 8.0
  units:
    count: 5
    movement: "forward_advance"
```

### Building Construction
Анімація будівництва з масштабуванням та спіральною камерою:

```yaml
building_construction:
  duration: 90
  camera:
    type: "helical"
    radius: 12.0
    height_start: 2.0
    height_end: 6.0
    turns: 1
  building:
    scale_animation: true
```

### Cinematic Shot
Кінематографічна анімація зі складним шляхом камери:

```yaml
cinematic_shot:
  duration: 120
  camera:
    type: "custom_path"
    points:
      - [-15, -20, 8]
      - [-10, -15, 12]
      - [0, -10, 15]
      - [10, -5, 12]
      - [15, 0, 8]
    fov_animation: true
```

## 🛠️ Розширені можливості

### Інтегрований пайплайн

```python
from integrated_animation_pipeline import IntegratedAnimationPipeline

pipeline = IntegratedAnimationPipeline()

# Створення з шаблону
result = pipeline.create_shot_from_template(
    "battle_sequence",
    "my_shot_001",
    custom_settings={
        'units': {'count': 10},
        'camera': {'radius': 25.0}
    }
)
```

### Пакетне створення

```python
batch_config = [
    {
        'shot_id': 'battle_001',
        'template': 'battle_sequence',
        'custom_settings': {'units': {'count': 8}}
    },
    {
        'shot_id': 'construction_001',
        'template': 'building_construction',
        'custom_settings': {'building': {'type': 'Factory'}}
    }
]

results = pipeline.batch_create_animations(batch_config)
```

### Експорт анімацій

```python
# Експорт у різні формати
export_path = pipeline.export_animation("my_shot", "blend")
export_path = pipeline.export_animation("my_shot", "fbx")
export_path = pipeline.export_animation("my_shot", "usd")
```

## 🎨 Налаштування рендерингу

### Якість рендерингу

```yaml
render_qualities:
  preview:
    samples: 32
    resolution: [640, 360]
  
  high:
    samples: 256
    resolution: [1920, 1080]
  
  cinematic:
    samples: 1024
    resolution: [3840, 2160]
```

### Мульти-пас рендеринг

```python
# Налаштування пасів
passes_config = [
    {'type': 'beauty', 'name': 'beauty'},
    {'type': 'depth', 'name': 'depth'},
    {'type': 'normal', 'name': 'normal'},
    {'type': 'diffuse', 'name': 'diffuse'},
    {'type': 'glossy', 'name': 'glossy'}
]

renderer.create_render_passes("my_shot", passes_config)
```

## 🎬 Типи анімації

### 1. Keyframe Animation
- **BEZIER** - плавні криві (за замовчуванням)
- **LINEAR** - лінійна інтерполяція
- **CONSTANT** - постійні значення
- **BACK** - ефект відкату
- **BOUNCE** - ефект підстрибування
- **ELASTIC** - еластичний ефект

### 2. Camera Paths
- **Circular** - круговий обліт
- **Helical** - спіральний підйом/спуск
- **Custom** - довільний шлях Безьє

### 3. Object Animation
- **Location** - рух по простору
- **Rotation** - обертання
- **Scale** - зміна розміру
- **Material** - зміна властивостей матеріалу

## 📊 Моніторинг та логування

```python
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Логування процесу анімації
logger.info("Створення анімації...")
logger.info(f"Рендеринг завершено: {len(rendered_files)} кадрів")
```

## 🔧 Конфігурація

### Глобальні налаштування

```yaml
global_settings:
  fps: 24
  frame_start: 1
  frame_end: 100
  interpolation: "BEZIER"
  render_engine: "CYCLES"
  output_format: "PNG"
  resolution: [1920, 1080]
```

### Налаштування камери

```yaml
camera_settings:
  default_fov: 50
  min_fov: 10
  max_fov: 180
  movement_smoothing: true
  auto_focus: true
```

### Налаштування освітлення

```yaml
lighting_settings:
  sun_light:
    default_energy: 3.0
    default_color: [1.0, 0.95, 0.8]
  area_light:
    default_energy: 1.0
    size: 1.0
```

## 🚀 Демонстрація

Запустіть демонстраційний скрипт:

```bash
python demo_animation_system.py
```

Це створить:
- Анімацію ключовими кадрами
- Криві камери (кругові, спіральні, кастомні)
- Рендеринг послідовностей
- Приклади різних типів анімацій
- Інтегрований пайплайн

## 📈 Продуктивність

### Оптимізація рендерингу
- **Adaptive Sampling** - адаптивна вибірка
- **Denoising** - шумоподавлення
- **Tile Size** - розмір тайлів
- **Memory Management** - управління пам'яттю

### Пакетна обробка
- **Parallel Rendering** - паралельний рендеринг
- **Queue Management** - управління чергою
- **Progress Tracking** - відстеження прогресу

## 🎯 Приклади використання

### Створення анімації битви

```python
from animation_examples import AnimationExamples

examples = AnimationExamples()
result = examples.create_battle_animation("battle_001")
```

### Створення анімації будівництва

```python
result = examples.create_building_construction_animation("construction_001")
```

### Створення кінематографічної анімації

```python
result = examples.create_cinematic_camera_animation("cinematic_001")
```

## 🔍 Відладка

### Перевірка анімації
```python
# Перевірка ключових кадрів
if obj.animation_data and obj.animation_data.action:
    for fcurve in obj.animation_data.action.fcurves:
        print(f"FCurve: {fcurve.data_path}")
        print(f"Keyframes: {len(fcurve.keyframe_points)}")
```

### Логування помилок
```python
try:
    # Код анімації
    pass
except Exception as e:
    logger.error(f"Помилка анімації: {e}")
```

## 📚 Додаткові ресурси

- [Blender Python API](https://docs.blender.org/api/current/)
- [Animation Nodes](https://github.com/JacquesLucke/animation_nodes)
- [Blender Compositing](https://docs.blender.org/manual/en/latest/compositing/)

## 🤝 Внесок у розробку

1. Fork репозиторій
2. Створіть feature branch
3. Внесіть зміни
4. Створіть Pull Request

## 📄 Ліцензія

Цей проект ліцензовано під MIT License.

---

**Система анімації Blender SCBW Pipeline** - потужний інструмент для створення кінематографічних послідовностей у стилі StarCraft: Brood War. 🎬✨