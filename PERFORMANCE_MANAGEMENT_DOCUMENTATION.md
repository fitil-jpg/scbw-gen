# Розширений Менеджер Продуктивності
# Advanced Performance Manager Documentation

## Огляд

Розширений менеджер продуктивності - це комплексна система для оптимізації рендерингу 3D сцен StarCraft, яка включає управління GPU/CPU ресурсами, денойз, тайли, адаптивне семплування та LOD (Level of Detail).

## Основні компоненти

### 1. GPU/CPU Управління (GPUManager, CPUManager)

**Функціональність:**
- Автоматичне виявлення доступних GPU
- Балансування навантаження між пристроями
- Моніторинг використання пам'яті та навантаження
- Оптимізація кількості потоків CPU

**Ключові класи:**
- `GPUManager` - управління GPU ресурсами
- `CPUManager` - управління CPU ресурсами
- `DeviceInfo` - інформація про пристрої

**Приклад використання:**
```python
from algorithms.advanced_performance_manager import AdvancedPerformanceManager

# Створення менеджера з GPU підтримкою
manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)

# Отримання доступного GPU
available_gpu = manager.gpu_manager.get_available_gpu()
if available_gpu:
    print(f"Використовуємо GPU: {available_gpu.name}")
```

### 2. Система Денойзу (DenoisingManager)

**Підтримувані алгоритми:**
- **OptiX** - NVIDIA OptiX денойз (найшвидший)
- **OIDN** - Intel Open Image Denoise
- **NLM** - Non-Local Means
- **BILATERAL** - Білатеральний фільтр

**Функціональність:**
- Автоматичний вибір алгоритму
- Кешування результатів
- Адаптивна сила денойзу
- Оцінка рівня шуму

**Приклад використання:**
```python
# Денойз зображення
denoised = manager.denoising_manager.denoise_image(
    noisy_image, 
    algorithm='OPTIX', 
    strength=1.0
)

# Оцінка рівня шуму
noise_level = manager.denoising_manager.estimate_noise_level(image)
```

### 3. Управління Тайлами (TileManager)

**Функціональність:**
- Розділення зображення на тайли
- Пріоритизація обробки
- Оцінка складності тайлів
- Паралельна обробка

**Ключові параметри:**
- `base_tile_size` - базовий розмір тайлу (за замовчуванням 256)
- `overlap` - перекриття між тайлами (за замовчуванням 8)
- `priority` - пріоритет обробки

**Приклад використання:**
```python
# Налаштування тайлів
manager.setup_tile_rendering(1920, 1080, 128)

# Отримання наступного тайлу для обробки
tile = manager.tile_manager.get_next_tile()
if tile:
    # Обробка тайлу
    result = process_tile(tile)
    manager.tile_manager.complete_tile(tile, result)
```

### 4. Адаптивне Семплування (AdaptiveSamplingManager)

**Функціональність:**
- Автоматичний розрахунок кількості семплів
- Адаптація до складності сцени
- Врахування рівня шуму
- Бюджетування часу

**Параметри:**
- `base_samples` - базова кількість семплів (128)
- `min_samples` - мінімальна кількість (32)
- `max_samples` - максимальна кількість (1024)

**Приклад використання:**
```python
# Розрахунок адаптивних семплів
complexity = 0.8  # Складність сцени
noise_level = 0.3  # Рівень шуму
time_budget = 2.0  # Бюджет часу в секундах

adaptive_samples = manager.adaptive_sampling.calculate_adaptive_samples(
    complexity, noise_level, time_budget
)
```

### 5. LOD Система (EnhancedLODSystem)

**Функціональність:**
- Динамічне масштабування якості
- Адаптація до відстані камери
- Врахування складності об'єктів
- Кешування LOD даних

**Рівні LOD:**
- LOD 0: 100% якості (1.0)
- LOD 1: 75% якості (0.75)
- LOD 2: 50% якості (0.5)
- LOD 3: 25% якості (0.25)
- LOD 4: 12.5% якості (0.125)

**Приклад використання:**
```python
# Визначення рівня LOD
distance = 150.0  # Відстань до об'єкта
complexity = 1.2  # Складність об'єкта
camera_speed = 5.0  # Швидкість камери

lod_level = manager.lod_system.get_lod_level(distance, complexity, camera_speed)

# Генерація LOD даних
lod_data = manager.lod_system.generate_lod_data(original_data, lod_level)
```

### 6. Моніторинг Продуктивності (PerformanceMonitor)

**Функціональність:**
- Моніторинг в реальному часі
- Збір метрик продуктивності
- Аналіз трендів
- Рекомендації по оптимізації

**Метрики:**
- Використання CPU/GPU
- Використання пам'яті
- Температура
- Час рендерингу
- Кількість семплів

**Приклад використання:**
```python
# Отримання поточних метрик
current_metrics = manager.performance_monitor.get_current_metrics()
print(f"CPU: {current_metrics['cpu_usage']:.1f}%")
print(f"GPU: {current_metrics['gpu_usage']:.1f}%")

# Отримання рекомендацій
recommendations = manager.performance_monitor.get_performance_recommendations()
for rec in recommendations:
    print(f"- {rec}")
```

## Інтеграція з Blender

### PerformanceIntegratedPipeline

Інтегрований пайплайн автоматично налаштовує Blender для оптимальної продуктивності:

```python
from blender.performance_integrated_pipeline import PerformanceIntegratedPipeline

# Створення пайплайну
pipeline = PerformanceIntegratedPipeline("renders/optimized")

# Рендеринг з оптимізацією
result = pipeline.render_shot_optimized(
    shot_id="test_shot",
    frame=1,
    target_fps=30.0,
    quality_preset="balanced"
)
```

### Пресети якості

- **draft** - швидкий рендеринг, низька якість
- **balanced** - збалансована якість та швидкість
- **high** - висока якість
- **ultra** - максимальна якість

## Конфігурація

### performance_config.yaml

Основні налаштування системи:

```yaml
# GPU/CPU управління
gpu_cpu_management:
  enable_gpu: true
  max_gpu_memory_mb: 8192
  cpu_usage_threshold: 0.80

# Денойз
denoising:
  enable_denoising: true
  default_algorithm: "OPTIX"
  auto_denoise_threshold: 0.3

# Тайли
tiling:
  enable_tiling: true
  base_tile_size: 256
  overlap: 8

# Адаптивне семплування
adaptive_sampling:
  enable_adaptive_sampling: true
  base_samples: 128
  min_samples: 32
  max_samples: 1024
```

## Приклади використання

### Базовий приклад

```python
from algorithms.advanced_performance_manager import AdvancedPerformanceManager
import numpy as np

# Створення менеджера
manager = AdvancedPerformanceManager(enable_gpu=True, enable_monitoring=True)

# Тестова сцена
scene_data = np.random.random((512, 512, 3)).astype(np.float32)

# Налаштування рендерингу
render_settings = {
    'time_budget': 2.0,
    'camera_distance': 150.0,
    'object_complexity': 1.2,
    'enable_denoising': True,
    'denoising_algorithm': 'OPTIX'
}

# Рендеринг з оптимізацією
result = manager.render_with_optimization(scene_data, render_settings)

# Отримання звіту
report = manager.get_performance_report()
print(f"Час рендерингу: {report['current_metrics']['generation_time']:.3f}s")

# Очищення ресурсів
manager.cleanup()
```

### Рендеринг по тайлах

```python
# Налаштування тайлів
manager.setup_tile_rendering(1920, 1080, 128)

# Рендеринг з тайлами
result = manager.render_with_optimization(scene_data, render_settings)

# Перевірка прогресу
progress = manager.tile_manager.get_progress()
print(f"Прогрес: {progress['progress_percentage']:.1f}%")
```

### Адаптивне семплування

```python
# Оцінка складності сцени
complexity = manager._assess_scene_complexity(scene_data)

# Розрахунок адаптивних семплів
noise_level = manager.adaptive_sampling.estimate_noise_level(scene_data)
adaptive_samples = manager.adaptive_sampling.calculate_adaptive_samples(
    complexity, noise_level, 1.0
)

print(f"Складність: {complexity:.2f}")
print(f"Адаптивні семпли: {adaptive_samples}")
```

### LOD система

```python
# Визначення рівня LOD
distance = 200.0
complexity = 1.5
camera_speed = 10.0

lod_level = manager.lod_system.get_lod_level(distance, complexity, camera_speed)
resolution = manager.lod_system.get_resolution_for_lod(lod_level)

print(f"LOD рівень: {lod_level}")
print(f"Роздільність: {resolution[0]}x{resolution[1]}")

# Генерація LOD даних
lod_data = manager.lod_system.generate_lod_data(original_data, lod_level)
```

## Оптимізація продуктивності

### Автоматичні рекомендації

```python
# Отримання рекомендацій
recommendations = manager.optimize_settings(target_fps=30.0)

# Застосування рекомендацій
if 'reduce_samples' in recommendations:
    # Зменшити кількість семплів
    pass

if 'enable_denoising' in recommendations:
    # Увімкнути денойз
    pass
```

### Моніторинг в реальному часі

```python
# Отримання поточних метрик
metrics = manager.performance_monitor.get_current_metrics()
print(f"CPU: {metrics['cpu_usage']:.1f}%")
print(f"Пам'ять: {metrics['memory_usage']:.1f}%")

# Отримання трендів
trends = manager.performance_monitor.get_performance_trends()
print(f"Середнє використання CPU: {np.mean(trends['cpu_usage']):.1f}%")
```

## Налаштування Blender

### Cycles

```python
# Налаштування Cycles з оптимізацією
scene.cycles.samples = 128
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.device = 'GPU'
scene.cycles.tile_size = 128
```

### Eevee

```python
# Налаштування Eevee з оптимізацією
scene.eevee.taa_render_samples = 64
scene.eevee.use_bloom = True
scene.eevee.use_ssr = True
scene.eevee.use_ssao = True
scene.eevee.shadow_cascade_size = '1024'
```

## Бенчмарки

### Запуск бенчмарку

```python
from algorithms.advanced_performance_manager import benchmark_performance_manager

# Запуск бенчмарку
benchmark_performance_manager()
```

### Результати бенчмарку

Типові результати для зображення 512x512:
- **Без оптимізацій**: 2.5s
- **З оптимізаціями**: 1.2s
- **Прискорення**: 2.1x
- **Економія пам'яті**: 30%

## Усунення проблем

### Часті проблеми

1. **Високе використання пам'яті**
   - Увімкнути тайлинг
   - Зменшити розмір тайлів
   - Увімкнути LOD

2. **Повільний рендеринг**
   - Увімкнути денойз
   - Зменшити кількість семплів
   - Використовувати GPU

3. **Низька якість**
   - Збільшити кількість семплів
   - Вимкнути LOD
   - Використовувати високоякісні пресети

### Діагностика

```python
# Отримання звіту про продуктивність
report = manager.get_performance_report()

# Перевірка рекомендацій
if 'recommendations' in report:
    for rec in report['recommendations']:
        print(f"Рекомендація: {rec}")

# Перевірка системних ресурсів
if report['current_metrics']['memory_usage'] > 85:
    print("Попередження: високе використання пам'яті")
```

## API Довідка

### AdvancedPerformanceManager

**Основні методи:**
- `render_with_optimization(scene_data, render_settings)` - рендеринг з оптимізацією
- `get_performance_report()` - отримання звіту про продуктивність
- `optimize_settings(target_fps)` - оптимізація налаштувань
- `cleanup()` - очищення ресурсів

**Параметри конструктора:**
- `enable_gpu` - увімкнути GPU підтримку
- `enable_monitoring` - увімкнути моніторинг

### PerformanceMetrics

**Поля:**
- `generation_time` - час генерації
- `memory_usage` - використання пам'яті
- `gpu_usage` - використання GPU
- `adaptive_samples` - адаптивні семпли
- `render_quality` - якість рендерингу

## Ліцензія

Цей проект розповсюджується під ліцензією MIT. Дивіться файл LICENSE для деталей.

## Підтримка

Для питань та підтримки створюйте issues в репозиторії проекту.