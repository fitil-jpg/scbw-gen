#!/usr/bin/env python3
"""
Скрипт для установки PyYAML в Blender Python.

Этот скрипт автоматически находит установку Blender и устанавливает PyYAML
в его встроенный Python интерпретатор.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import tempfile
import urllib.request
import zipfile


def find_blender_executable():
    """Находит исполняемый файл Blender в системе."""
    possible_paths = []
    
    # Определяем возможные пути в зависимости от ОС
    if platform.system() == "Linux":
        possible_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender",
            "/opt/blender/blender",
            "/home/*/blender*/blender",
            "/home/*/Blender*/blender",
        ]
    elif platform.system() == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/usr/local/bin/blender",
            "/opt/homebrew/bin/blender",
        ]
    elif platform.system() == "Windows":
        possible_paths = [
            "C:\\Program Files\\Blender Foundation\\Blender *\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender *\\blender.exe",
        ]
    
    # Ищем Blender в стандартных путях
    for path_pattern in possible_paths:
        if "*" in path_pattern:
            # Используем glob для поиска с wildcards
            import glob
            matches = glob.glob(os.path.expanduser(path_pattern))
            for match in matches:
                if os.path.isfile(match) and os.access(match, os.X_OK):
                    return match
        else:
            if os.path.isfile(path_pattern) and os.access(path_pattern, os.X_OK):
                return path_pattern
    
    # Пробуем найти через which/where
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["where", "blender"], capture_output=True, text=True)
        else:
            result = subprocess.run(["which", "blender"], capture_output=True, text=True)
        
        if result.returncode == 0:
            blender_path = result.stdout.strip().split('\n')[0]
            if os.path.isfile(blender_path) and os.access(blender_path, os.X_OK):
                return blender_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None


def get_blender_python_path(blender_executable):
    """Получает путь к Python интерпретатору Blender."""
    try:
        # Запускаем Blender с командой для получения пути к Python
        cmd = [blender_executable, "--background", "--python-expr", "import sys; print(sys.executable)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Извлекаем путь к Python из вывода (может быть несколько строк)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line and os.path.isfile(line) and 'python' in line.lower():
                    return line
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Ошибка при получении пути к Python Blender: {e}")
    
    # Fallback: пытаемся угадать путь
    blender_dir = os.path.dirname(blender_executable)
    possible_python_paths = [
        os.path.join(blender_dir, "python", "bin", "python"),
        os.path.join(blender_dir, "python", "python"),
        os.path.join(blender_dir, "..", "python", "bin", "python"),
        os.path.join(blender_dir, "..", "python", "python"),
    ]
    
    for python_path in possible_python_paths:
        if os.path.isfile(python_path):
            return python_path
    
    return None


def check_yaml_installed(python_executable):
    """Проверяет, установлен ли PyYAML в Python Blender."""
    try:
        cmd = [python_executable, "-c", "import yaml; print('PyYAML version:', yaml.__version__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_yaml_via_pip(python_executable):
    """Устанавливает PyYAML через pip."""
    print("Установка PyYAML через pip...")
    
    try:
        # Обновляем pip
        subprocess.run([python_executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Устанавливаем PyYAML
        subprocess.run([python_executable, "-m", "pip", "install", "PyYAML>=6.0"], 
                      check=True, capture_output=True)
        
        print("✅ PyYAML успешно установлен через pip")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки через pip: {e}")
        return False


def install_yaml_manually(python_executable):
    """Устанавливает PyYAML вручную, скачивая и компилируя."""
    print("Установка PyYAML вручную...")
    
    try:
        # Создаем временную директорию
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Скачиваем PyYAML
            yaml_url = "https://github.com/yaml/pyyaml/archive/refs/tags/6.0.1.zip"
            yaml_zip = temp_path / "pyyaml.zip"
            
            print("Скачивание PyYAML...")
            urllib.request.urlretrieve(yaml_url, yaml_zip)
            
            # Распаковываем
            with zipfile.ZipFile(yaml_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Находим директорию с исходниками
            yaml_dir = temp_path / "pyyaml-6.0.1"
            
            # Устанавливаем
            print("Компиляция и установка PyYAML...")
            subprocess.run([python_executable, "setup.py", "install"], 
                          cwd=yaml_dir, check=True, capture_output=True)
            
        print("✅ PyYAML успешно установлен вручную")
        return True
    except Exception as e:
        print(f"❌ Ошибка ручной установки: {e}")
        return False


def create_yaml_test_script():
    """Создает тестовый скрипт для проверки YAML в Blender."""
    test_script = """import bpy
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
print("\\nYAML контент:")
print(yaml_content)

# Загружаем обратно
loaded_data = yaml.safe_load(yaml_content)
print("\\nЗагруженные данные:")
print(loaded_data)

print("\\n✅ YAML работает корректно в Blender!")
"""
    
    with open("test_yaml_in_blender.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("Создан тестовый скрипт: test_yaml_in_blender.py")


def main():
    """Главная функция установки."""
    print("🎨 Установка PyYAML для Blender Python")
    print("=" * 50)
    
    # 1. Находим Blender
    print("Поиск Blender...")
    blender_executable = find_blender_executable()
    
    if not blender_executable:
        print("❌ Blender не найден в системе")
        print("\nВозможные решения:")
        print("1. Установите Blender:")
        if platform.system() == "Linux":
            print("   sudo apt install blender  # Ubuntu/Debian")
            print("   sudo dnf install blender  # Fedora")
            print("   sudo pacman -S blender    # Arch Linux")
        elif platform.system() == "Darwin":
            print("   brew install --cask blender  # macOS")
        elif platform.system() == "Windows":
            print("   Скачайте с https://www.blender.org/download/")
        print("2. Убедитесь, что Blender добавлен в PATH")
        return False
    
    print(f"✅ Найден Blender: {blender_executable}")
    
    # 2. Находим Python Blender
    print("Поиск Python интерпретатора Blender...")
    python_executable = get_blender_python_path(blender_executable)
    
    if not python_executable:
        print("❌ Не удалось найти Python интерпретатор Blender")
        return False
    
    print(f"✅ Найден Python: {python_executable}")
    
    # 3. Проверяем, установлен ли уже YAML
    print("Проверка установки PyYAML...")
    if check_yaml_installed(python_executable):
        print("✅ PyYAML уже установлен!")
        create_yaml_test_script()
        return True
    
    print("⚠ PyYAML не установлен, начинаем установку...")
    
    # 4. Пытаемся установить через pip
    if install_yaml_via_pip(python_executable):
        if check_yaml_installed(python_executable):
            print("✅ PyYAML успешно установлен через pip!")
            create_yaml_test_script()
            return True
    
    # 5. Если pip не сработал, пробуем ручную установку
    print("Попытка ручной установки...")
    if install_yaml_manually(python_executable):
        if check_yaml_installed(python_executable):
            print("✅ PyYAML успешно установлен вручную!")
            create_yaml_test_script()
            return True
    
    print("❌ Не удалось установить PyYAML")
    print("\nАльтернативные решения:")
    print("1. Установите PyYAML в системный Python и скопируйте модули")
    print("2. Используйте conda для управления пакетами Blender")
    print("3. Скомпилируйте PyYAML из исходников")
    
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)