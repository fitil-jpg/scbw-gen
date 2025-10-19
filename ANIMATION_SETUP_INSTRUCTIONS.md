# Інструкції з налаштування системи анімації

## 🎬 Система анімації Blender SCBW Pipeline

Повнофункціональна система для створення кінематографічних анімацій у стилі StarCraft: Brood War.

## 📋 Що було створено

### Основні компоненти
1. **`animation_system.py`** - Основна система анімації
   - KeyframeManager - управління ключовими кадрами
   - CameraCurveAnimator - анімація камери по кривим
   - AnimationSequenceRenderer - рендеринг послідовностей
   - Blender оператори для UI

2. **`animation_examples.py`** - Приклади використання
   - Анімація битви
   - Анімація будівництва
   - Кінематографічна анімація
   - UI панелі

3. **`integrated_animation_pipeline.py`** - Інтегрований пайплайн
   - Об'єднання всіх компонентів
   - Робота з шаблонами
   - Пакетне створення
   - Експорт анімацій

4. **`animations_config.yaml`** - Конфігурація
   - Шаблони анімацій
   - Налаштування рендерингу
   - Якості рендерингу
   - Параметри камери та освітлення

### Демонстраційні скрипти
5. **`demo_animation_system.py`** - Повна демонстрація
6. **`test_animation_system.py`** - Тестування компонентів
7. **`run_animation_system.py`** - Інтерактивний запуск

## 🚀 Швидкий старт

### 1. Запуск через Blender
```bash
# В Blender Python Console або Text Editor
exec(open("blender/animation_system.py").read())
```

### 2. Запуск демонстрації
```bash
python demo_animation_system.py
```

### 3. Запуск тестів
```bash
python test_animation_system.py
```

### 4. Інтерактивний режим
```bash
python run_animation_system.py
```

## 🎯 Основні можливості

### Ключові кадри
- ✅ Позиція об'єктів
- ✅ Обертання
- ✅ Масштабування
- ✅ FOV камери
- ✅ Енергія світла
- ✅ Різні типи інтерполяції

### Криві камери
- ✅ Кругові криві (обліт)
- ✅ Спіральні криві (підйом/спуск)
- ✅ Кастомні криві Безьє
- ✅ Автоматичне наведення

### Рендеринг
- ✅ Cycles та Eevee
- ✅ Мульти-пас рендеринг
- ✅ Різні якості
- ✅ Пакетна обробка
- ✅ Експорт у різні формати

## 📁 Структура файлів

```
workspace/
├── blender/
│   ├── animation_system.py          # Основна система
│   ├── animation_examples.py        # Приклади
│   ├── integrated_animation_pipeline.py  # Інтегрований пайплайн
│   └── advanced_render_pipeline.py  # Рендеринг
├── assets/animations/
│   └── animations_config.yaml       # Конфігурація
├── demo_animation_system.py         # Демонстрація
├── test_animation_system.py         # Тести
├── run_animation_system.py          # Запуск
└── renders/blender/animation/       # Результати
```

## 🎬 Приклади використання

### Створення анімації битви
```python
from animation_examples import AnimationExamples

examples = AnimationExamples()
result = examples.create_battle_animation("battle_001")
```

### Створення з шаблону
```python
from integrated_animation_pipeline import IntegratedAnimationPipeline

pipeline = IntegratedAnimationPipeline()
result = pipeline.create_shot_from_template(
    "battle_sequence", 
    "my_shot",
    {'units': {'count': 10}}
)
```

### Анімація камери
```python
from animation_system import CameraCurveAnimator

animator = CameraCurveAnimator()
curve = animator.create_circular_camera_path(
    center=Vector((0, 0, 0)),
    radius=15.0,
    height=8.0
)
animator.animate_camera_along_curve(camera, curve, 1, 100, True)
```

## ⚙️ Налаштування

### Конфігурація в YAML
```yaml
global_settings:
  fps: 24
  resolution: [1920, 1080]
  render_engine: "CYCLES"
  output_format: "PNG"

animation_templates:
  battle_sequence:
    duration: 100
    camera:
      type: "circular"
      radius: 20.0
```

### Якості рендерингу
- **preview** - 32 семпли, 640x360
- **low** - 64 семпли, 1280x720
- **medium** - 128 семплів, 1920x1080
- **high** - 256 семплів, 1920x1080
- **cinematic** - 1024 семпли, 3840x2160

## 🧪 Тестування

### Запуск тестів
```bash
python test_animation_system.py
```

### Тестування компонентів
- ✅ KeyframeManager
- ✅ CameraCurveAnimator
- ✅ AnimationSequenceRenderer
- ✅ AnimationExamples
- ✅ IntegratedAnimationPipeline
- ✅ Blender Operators

## 🎨 UI в Blender

### Панель анімації
- Розташування: 3D Viewport > N-panel > SCBW
- Кнопки створення анімацій
- Налаштування рендерингу
- Кнопки рендерингу

### Оператори
- `scbw.create_circular_camera_path`
- `scbw.create_helical_camera_path`
- `scbw.render_animation_sequence`
- `scbw.create_battle_animation`
- `scbw.create_construction_animation`
- `scbw.create_cinematic_animation`

## 📊 Моніторинг

### Логування
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Маніфести
- Автоматичне створення маніфестів
- JSON формат
- Метадані анімації
- Шляхи до файлів

## 🔧 Розширення

### Додавання нових типів анімації
1. Створіть новий клас в `animation_examples.py`
2. Додайте шаблон в `animations_config.yaml`
3. Зареєструйте в `integrated_animation_pipeline.py`

### Додавання нових типів кривих
1. Розширте `CameraCurveAnimator`
2. Додайте новий метод створення кривої
3. Оновіть конфігурацію

## 🐛 Відладка

### Типові проблеми
1. **Помилки імпорту** - перевірте шляхи до модулів
2. **Помилки рендерингу** - перевірте налаштування Blender
3. **Помилки анімації** - перевірте ключові кадри

### Логи
```python
# Увімкнення детального логування
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Продуктивність

### Оптимізація
- Використовуйте preview якість для тестування
- Налаштуйте tile size для Cycles
- Увімкніть denoising
- Використовуйте adaptive sampling

### Пакетна обробка
- Створюйте кілька анімацій одночасно
- Використовуйте різні якості рендерингу
- Експортуйте в різні формати

## 🎉 Готово!

Система анімації повністю налаштована та готова до використання. 

### Наступні кроки:
1. Запустіть `python demo_animation_system.py` для ознайомлення
2. Спробуйте `python run_animation_system.py` для інтерактивного режиму
3. Створіть власні анімації використовуючи шаблони
4. Налаштуйте конфігурацію під свої потреби

**Успішного створення анімацій! 🎬✨**