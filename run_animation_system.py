#!/usr/bin/env python3
"""
Скрипт запуску системи анімації Blender SCBW Pipeline
Надає інтерактивний інтерфейс для створення анімацій
"""

import bpy
import sys
from pathlib import Path
import logging

# Додавання шляху до модулів
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "blender"))

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show_menu():
    """Показує головне меню."""
    print("\n" + "=" * 60)
    print("🎬 СИСТЕМА АНІМАЦІЇ BLENDER SCBW PIPELINE")
    print("=" * 60)
    print("1. Створити анімацію битви")
    print("2. Створити анімацію будівництва")
    print("3. Створити кінематографічну анімацію")
    print("4. Створити кастомну анімацію")
    print("5. Пакетне створення анімацій")
    print("6. Тестування системи")
    print("7. Демонстрація можливостей")
    print("8. Налаштування")
    print("9. Вихід")
    print("=" * 60)


def create_battle_animation():
    """Створює анімацію битви."""
    print("\n⚔️  Створення анімації битви...")
    
    try:
        from animation_examples import AnimationExamples
        
        examples = AnimationExamples()
        result = examples.create_battle_animation("battle_shot_001")
        
        if result['status'] == 'success':
            print(f"✅ Анімація битви створена: {len(result['rendered_files'])} кадрів")
            print(f"📁 Файли збережено в: {result['rendered_files'][0].parent}")
        else:
            print(f"❌ Помилка створення анімації: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        logger.error(f"Error creating battle animation: {e}")


def create_construction_animation():
    """Створює анімацію будівництва."""
    print("\n🏗️  Створення анімації будівництва...")
    
    try:
        from animation_examples import AnimationExamples
        
        examples = AnimationExamples()
        result = examples.create_building_construction_animation("construction_shot_001")
        
        if result['status'] == 'success':
            print(f"✅ Анімація будівництва створена: {len(result['rendered_files'])} кадрів")
            print(f"📁 Файли збережено в: {result['rendered_files'][0].parent}")
        else:
            print(f"❌ Помилка створення анімації: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        logger.error(f"Error creating construction animation: {e}")


def create_cinematic_animation():
    """Створює кінематографічну анімацію."""
    print("\n🎭 Створення кінематографічної анімації...")
    
    try:
        from animation_examples import AnimationExamples
        
        examples = AnimationExamples()
        result = examples.create_cinematic_camera_animation("cinematic_shot_001")
        
        if result['status'] == 'success':
            print(f"✅ Кінематографічна анімація створена: {len(result['rendered_files'])} кадрів")
            print(f"📁 Файли збережено в: {result['rendered_files'][0].parent}")
        else:
            print(f"❌ Помилка створення анімації: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        logger.error(f"Error creating cinematic animation: {e}")


def create_custom_animation():
    """Створює кастомну анімацію."""
    print("\n🎨 Створення кастомної анімації...")
    
    try:
        from integrated_animation_pipeline import IntegratedAnimationPipeline
        
        pipeline = IntegratedAnimationPipeline()
        
        # Запит параметрів від користувача
        print("\nДоступні шаблони:")
        print("1. battle_sequence - Анімація битви")
        print("2. building_construction - Анімація будівництва")
        print("3. cinematic_shot - Кінематографічна анімація")
        
        template_choice = input("Виберіть шаблон (1-3): ").strip()
        
        templates = {
            '1': 'battle_sequence',
            '2': 'building_construction',
            '3': 'cinematic_shot'
        }
        
        template = templates.get(template_choice, 'battle_sequence')
        shot_id = input("Введіть ID шоту: ").strip() or "custom_shot_001"
        
        # Додаткові налаштування
        print("\nДодаткові налаштування (натисніть Enter для пропуску):")
        units_count = input("Кількість одиниць (для битви): ").strip()
        camera_radius = input("Радіус камери: ").strip()
        samples = input("Кількість семплів рендерингу: ").strip()
        
        custom_settings = {}
        if units_count:
            custom_settings['units'] = {'count': int(units_count)}
        if camera_radius:
            custom_settings['camera'] = {'radius': float(camera_radius)}
        if samples:
            custom_settings['render_settings'] = {'samples': int(samples)}
        
        # Створення анімації
        result = pipeline.create_shot_from_template(template, shot_id, custom_settings)
        
        if result['status'] == 'success':
            print(f"✅ Кастомна анімація створена: {len(result['rendered_files'])} кадрів")
            print(f"📁 Файли збережено в: {result['rendered_files'][0].parent}")
        else:
            print(f"❌ Помилка створення анімації: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        logger.error(f"Error creating custom animation: {e}")


def batch_create_animations():
    """Створює кілька анімацій пакетно."""
    print("\n📦 Пакетне створення анімацій...")
    
    try:
        from integrated_animation_pipeline import IntegratedAnimationPipeline
        
        pipeline = IntegratedAnimationPipeline()
        
        # Конфігурація для пакетного створення
        batch_config = [
            {
                'shot_id': 'batch_battle_001',
                'template': 'battle_sequence',
                'custom_settings': {'units': {'count': 5}}
            },
            {
                'shot_id': 'batch_construction_001',
                'template': 'building_construction',
                'custom_settings': {'building': {'type': 'Factory'}}
            },
            {
                'shot_id': 'batch_cinematic_001',
                'template': 'cinematic_shot',
                'custom_settings': {'camera': {'radius': 20.0}}
            }
        ]
        
        print("Створення анімацій...")
        results = pipeline.batch_create_animations(batch_config)
        
        successful = sum(1 for r in results.values() if r.get('status') == 'success')
        failed = sum(1 for r in results.values() if r.get('status') == 'error')
        
        print(f"✅ Пакетне створення завершено:")
        print(f"   Успішних: {successful}")
        print(f"   Провалених: {failed}")
        
        for shot_id, result in results.items():
            if result['status'] == 'success':
                print(f"   ✅ {shot_id}: {len(result['rendered_files'])} кадрів")
            else:
                print(f"   ❌ {shot_id}: {result.get('error')}")
                
    except Exception as e:
        print(f"❌ Помилка: {e}")
        logger.error(f"Error in batch creation: {e}")


def run_tests():
    """Запускає тести системи."""
    print("\n🧪 Запуск тестів системи...")
    
    try:
        # Імпорт тестового модуля
        sys.path.append(str(current_dir))
        from test_animation_system import run_all_tests
        
        success = run_all_tests()
        
        if success:
            print("\n🎉 Всі тести пройдено успішно!")
        else:
            print("\n⚠️  Деякі тести провалено")
            
    except Exception as e:
        print(f"❌ Помилка запуску тестів: {e}")
        logger.error(f"Error running tests: {e}")


def run_demo():
    """Запускає демонстрацію можливостей."""
    print("\n🎬 Запуск демонстрації можливостей...")
    
    try:
        # Імпорт демонстраційного модуля
        sys.path.append(str(current_dir))
        from demo_animation_system import main as demo_main
        
        demo_main()
        
    except Exception as e:
        print(f"❌ Помилка запуску демонстрації: {e}")
        logger.error(f"Error running demo: {e}")


def show_settings():
    """Показує налаштування системи."""
    print("\n⚙️  Налаштування системи...")
    
    try:
        from integrated_animation_pipeline import IntegratedAnimationPipeline
        
        pipeline = IntegratedAnimationPipeline()
        
        # Показ поточної конфігурації
        config = pipeline.config
        global_settings = config.get('global_settings', {})
        
        print("\nПоточні налаштування:")
        print(f"  FPS: {global_settings.get('fps', 24)}")
        print(f"  Роздільність: {global_settings.get('resolution', [1920, 1080])}")
        print(f"  Рендер двигун: {global_settings.get('render_engine', 'CYCLES')}")
        print(f"  Формат виводу: {global_settings.get('output_format', 'PNG')}")
        
        # Показ доступних шаблонів
        templates = config.get('animation_templates', {})
        print(f"\nДоступні шаблони анімацій: {len(templates)}")
        for name, template in templates.items():
            print(f"  - {name}: {template.get('name', 'Без назви')}")
        
        # Показ якостей рендерингу
        qualities = config.get('render_qualities', {})
        print(f"\nДоступні якості рендерингу: {len(qualities)}")
        for name, quality in qualities.items():
            samples = quality.get('samples', 'N/A')
            resolution = quality.get('resolution', 'N/A')
            print(f"  - {name}: {samples} семплів, {resolution} роздільність")
            
    except Exception as e:
        print(f"❌ Помилка завантаження налаштувань: {e}")
        logger.error(f"Error loading settings: {e}")


def main():
    """Головна функція програми."""
    print("🚀 Запуск системи анімації Blender SCBW Pipeline...")
    
    while True:
        try:
            show_menu()
            choice = input("\nВиберіть опцію (1-9): ").strip()
            
            if choice == '1':
                create_battle_animation()
            elif choice == '2':
                create_construction_animation()
            elif choice == '3':
                create_cinematic_animation()
            elif choice == '4':
                create_custom_animation()
            elif choice == '5':
                batch_create_animations()
            elif choice == '6':
                run_tests()
            elif choice == '7':
                run_demo()
            elif choice == '8':
                show_settings()
            elif choice == '9':
                print("\n👋 До побачення!")
                break
            else:
                print("\n❌ Невірний вибір. Спробуйте ще раз.")
            
            input("\nНатисніть Enter для продовження...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Програма перервана користувачем. До побачення!")
            break
        except Exception as e:
            print(f"\n❌ Критична помилка: {e}")
            logger.error(f"Critical error in main loop: {e}")
            input("Натисніть Enter для продовження...")


if __name__ == "__main__":
    main()