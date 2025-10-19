import bpy
import yaml
import sys

print("=== Тест YAML в Blender ===")
print(f"Python версия: {sys.version}")
print(f"PyYAML версия: {yaml.__version__}")

# Тестовые данные
test_data = {
    'scene': {
        'name': 'Test Scene',
        'objects': ['Cube', 'Sphere', 'Light'],
        'settings': {
            'resolution': [1920, 1080],
            'samples': 64
        }
    }
}

# Сохраняем в YAML
yaml_content = yaml.dump(test_data, default_flow_style=False)
print("\nYAML контент:")
print(yaml_content)

# Загружаем обратно
loaded_data = yaml.safe_load(yaml_content)
print("\nЗагруженные данные:")
print(loaded_data)

print("\n✅ YAML работает корректно в Blender!")
