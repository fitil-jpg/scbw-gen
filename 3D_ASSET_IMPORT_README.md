# 3D Asset Import System with Instancing

Система імпорту 3D асетів з підтримкою інстансингу для GLTF/FBX/OBJ файлів.

## Огляд

Ця система надає повнофункціональний імпорт 3D моделей з підтримкою інстансингу, що дозволяє ефективно використовувати одну модель для створення багатьох інстансів у сцені. Система інтегрована з існуючим Asset Manager та підтримує експорт в USD формат.

## Основні можливості

### Підтримувані формати
- **GLTF/GLB** - сучасний формат для 3D сцен
- **FBX** - популярний формат для 3D моделей
- **OBJ** - простий формат для геометрії
- **USD/USDA/USDC** - формат Pixar USD
- **DAE** - формат Collada
- **BLEND** - формат Blender

### Система інстансингу
- Створення тисяч інстансів з однієї моделі
- Ефективне управління пам'яттю
- Підтримка LOD (Level of Detail)
- Фрустум та оклюзійне відсіювання
- Батчова обробка інстансів

### Інтеграція
- Повна інтеграція з Asset Manager
- Підтримка конфігураційних файлів
- Експорт в USD з інстансингом
- Валідація асетів

## Структура файлів

```
assets/
├── 3d_assets/
│   ├── config.yaml              # Конфігурація 3D асетів
│   ├── models/                  # 3D моделі
│   │   ├── castle.gltf
│   │   ├── tower.obj
│   │   ├── warrior.glb
│   │   └── ...
│   ├── textures/                # Текстури
│   ├── materials/               # Матеріали
│   ├── animations/              # Анімації
│   └── instances/               # Конфігурації інстансів
└── ...

src/
├── asset_3d_importer.py         # Основний імпортер
├── integrated_3d_scene_generator.py  # Інтегрований генератор
├── example_3d_asset_import.py   # Приклади використання
└── integrated_scene_config.yaml # Конфігурація сцени
```

## Швидкий старт

### 1. Базовий імпорт моделі

```python
from asset_3d_importer import Asset3DImporter

# Створити імпортер
importer = Asset3DImporter("assets")

# Імпортувати модель
model = importer.import_model("assets/3d_assets/models/castle.gltf")
print(f"Імпортовано: {model.name} ({model.format.value})")
```

### 2. Створення інстансів

```python
# Створити інстанс
instance_id = importer.create_instance(
    model_key="gltf_castle",
    position=(0, 0, 0),
    rotation=(0, 45, 0),
    scale=(1.2, 1.2, 1.2),
    metadata={"type": "main_castle"}
)

print(f"Створено інстанс: {instance_id}")
```

### 3. Експорт в USD

```python
# Експорт з інстансингом
importer.export_to_usd("output/scene.usda", use_instancing=True)

# Експорт без інстансингу
importer.export_to_usd("output/scene_no_instancing.usda", use_instancing=False)
```

### 4. Створення інстансів з конфігурації

```yaml
# instances_config.yaml
instances:
  - model: "gltf_castle"
    position: [0, 0, 0]
    rotation: [0, 0, 0]
    scale: [1, 1, 1]
    metadata:
      type: "main_castle"
      
  - model: "obj_tower"
    position: [10, 0, 0]
    rotation: [0, 45, 0]
    scale: [1.2, 1.2, 1.2]
    metadata:
      type: "defense_tower"
```

```python
# Створити інстанси з конфігурації
instance_ids = importer.create_instances_from_config("instances_config.yaml")
```

## Детальне використання

### Asset3DImporter

Основний клас для роботи з 3D асетами.

#### Методи імпорту

```python
# Імпорт моделі
model = importer.import_model(file_path, auto_register=True)

# Сканування директорії
models = importer.scan_directory("assets/3d_assets/models", recursive=True)
```

#### Управління інстансами

```python
# Створення інстансу
instance_id = importer.create_instance(
    model_key="gltf_model",
    position=(x, y, z),
    rotation=(rx, ry, rz),
    scale=(sx, sy, sz),
    material_overrides={"color": [1, 0, 0]},
    metadata={"custom": "data"}
)

# Отримання інстансу
instance = importer.get_instance(instance_id)

# Видалення інстансу
importer.remove_instance(instance_id)

# Очищення всіх інстансів
importer.clear_instances()
```

#### Експорт

```python
# Експорт в USD
importer.export_to_usd("output.usda", use_instancing=True)

# Експорт конфігурації інстансів
importer.export_instances_config("instances.yaml")
```

### Integrated3DSceneGenerator

Інтегрований генератор сцен з підтримкою 3D асетів.

```python
from integrated_3d_scene_generator import Integrated3DSceneGenerator

# Створити генератор
generator = Integrated3DSceneGenerator("assets", "integrated_scene_config.yaml")

# Згенерувати повну сцену
generator.generate_complete_scene("output/scene.usda")
```

## Конфігурація

### Конфігурація 3D асетів (assets/3d_assets/config.yaml)

```yaml
# Налаштування інстансингу
instancing:
  max_instances_per_model: 1000
  enable_lod: true
  lod_distances: [10.0, 50.0, 100.0]
  culling_distance: 200.0
  batch_size: 100
  enable_frustum_culling: true
  enable_occlusion_culling: false

# Шляхи до асетів
asset_paths:
  models: "3d_assets/models"
  textures: "3d_assets/textures"
  materials: "3d_assets/materials"
  animations: "3d_assets/animations"

# Налаштування імпорту
import_settings:
  auto_scale: true
  normalize_scale: 1.0
  merge_materials: true
  generate_tangents: true
  optimize_meshes: true
```

### Конфігурація сцени (integrated_scene_config.yaml)

```yaml
scene:
  name: "3D Battle Scene"
  terrain:
    type: "grassland"
    size: 200.0
  lighting:
    sun_angle: [45, 30]
    sun_intensity: 1.0

3d_assets:
  import_models: true
  use_instancing: true
  model_placement:
    strategy: "random"
    density: 0.1
    spacing: 5.0

buildings:
  enabled: true
  use_3d_models: true
  instancing_enabled: true
  count: 12

units:
  enabled: true
  use_3d_models: true
  instancing_enabled: true
  total_count: 60
```

## Приклади використання

### 1. Базовий приклад

```python
#!/usr/bin/env python3
from asset_3d_importer import Asset3DImporter

# Створити імпортер
importer = Asset3DImporter("assets")

# Імпортувати модель
model = importer.import_model("castle.gltf")

# Створити кілька інстансів
for i in range(10):
    instance_id = importer.create_instance(
        model_key=f"gltf_{model.name}",
        position=(i * 5, 0, 0),
        rotation=(0, i * 36, 0),
        scale=(1, 1, 1)
    )
    print(f"Створено інстанс: {instance_id}")

# Експортувати сцену
importer.export_to_usd("output/castle_scene.usda")
```

### 2. Приклад з конфігурацією

```python
#!/usr/bin/env python3
from integrated_3d_scene_generator import Integrated3DSceneGenerator

# Створити генератор з конфігурацією
generator = Integrated3DSceneGenerator(
    assets_root="assets",
    config_path="integrated_scene_config.yaml"
)

# Згенерувати сцену
generator.generate_complete_scene("output/battle_scene.usda")
```

### 3. Приклад управління інстансами

```python
#!/usr/bin/env python3
from asset_3d_importer import Asset3DImporter

importer = Asset3DImporter("assets")

# Імпортувати моделі
importer.import_model("warrior.glb")
importer.import_model("archer.glb")

# Створити армію воїнів
warrior_instances = []
for i in range(20):
    instance_id = importer.create_instance(
        model_key="glb_warrior",
        position=(i * 2, 0, 0),
        metadata={"unit_type": "warrior", "squad": "alpha"}
    )
    warrior_instances.append(instance_id)

# Створити армію лучників
archer_instances = []
for i in range(15):
    instance_id = importer.create_instance(
        model_key="glb_archer",
        position=(i * 2, 0, 10),
        metadata={"unit_type": "archer", "squad": "beta"}
    )
    archer_instances.append(instance_id)

# Експортувати армію
importer.export_to_usd("output/army.usda", use_instancing=True)

# Показати статистику
print(f"Воїнів: {len(warrior_instances)}")
print(f"Лучників: {len(archer_instances)}")
print(f"Всього інстансів: {len(importer.instances)}")
```

## Продуктивність

### Оптимізації інстансингу

1. **Батчова обробка** - інстанси обробляються групами
2. **LOD система** - різні рівні деталізації залежно від відстані
3. **Відсіювання** - фрустум та оклюзійне відсіювання
4. **Кешування** - збереження оброблених моделей

### Рекомендації

- Використовуйте інстансинг для повторюваних об'єктів
- Налаштуйте LOD для великих сцен
- Обмежте кількість інстансів на модель (за замовчуванням 1000)
- Використовуйте батчову обробку для створення багатьох інстансів

## Валідація

Система включає валідацію:

- Перевірка цілісності файлів
- Валідація геометрії
- Перевірка матеріалів та текстур
- Валідація інстансів
- Перевірка UV координат

## Логування

Система надає детальне логування:

- Прогрес імпорту
- Метрики продуктивності
- Використання пам'яті
- Попередження та помилки

## Залежності

- `pxr` - USD Python bindings
- `PyYAML` - для роботи з YAML файлами
- `PIL` - для роботи з зображеннями
- `pathlib` - для роботи з шляхами

## Встановлення

```bash
# Встановити залежності
pip install usd-core PyYAML Pillow

# Клонувати репозиторій
git clone <repository_url>
cd 3d-asset-import

# Запустити приклад
python example_3d_asset_import.py
```

## Ліцензія

Цей проект розповсюджується під ліцензією MIT. Дивіться файл LICENSE для деталей.

## Підтримка

Для питань та підтримки створюйте issues в репозиторії проекту.