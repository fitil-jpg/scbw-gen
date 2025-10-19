# Установка PyYAML в Blender Python

Это руководство описывает различные способы установки библиотеки PyYAML для использования в Blender Python.

## 🚀 Быстрая установка

### Автоматическая установка (рекомендуется)

```bash
# Для Linux
chmod +x install_yaml_blender_linux.sh
./install_yaml_blender_linux.sh

# Для всех платформ
python3 install_yaml_for_blender.py
```

## 📋 Ручная установка

### 1. Linux (Ubuntu/Debian)

```bash
# Установка через системный пакетный менеджер
sudo apt update
sudo apt install python3-yaml

# Или через pip в Blender Python
/usr/bin/blender --background --python-expr "import subprocess; subprocess.run(['pip', 'install', 'PyYAML'])"
```

### 2. Linux (Fedora)

```bash
# Установка через dnf
sudo dnf install python3-PyYAML

# Или через pip
/usr/bin/blender --background --python-expr "import subprocess; subprocess.run(['pip', 'install', 'PyYAML'])"
```

### 3. Linux (Arch Linux)

```bash
# Установка через pacman
sudo pacman -S python-yaml

# Или через pip
/usr/bin/blender --background --python-expr "import subprocess; subprocess.run(['pip', 'install', 'PyYAML'])"
```

### 4. macOS

```bash
# Установка через Homebrew
brew install pyyaml

# Или через pip в Blender
/Applications/Blender.app/Contents/MacOS/Blender --background --python-expr "import subprocess; subprocess.run(['pip', 'install', 'PyYAML'])"
```

### 5. Windows

```cmd
# Через pip в Blender Python
"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --background --python-expr "import subprocess; subprocess.run(['pip', 'install', 'PyYAML'])"
```

## 🔧 Альтернативные методы

### Метод 1: Копирование системного YAML

Если у вас уже установлен PyYAML в системном Python, можно скопировать его в Blender:

```bash
# Находим системный YAML
python3 -c "import yaml; print(yaml.__file__)"

# Находим site-packages Blender
/usr/bin/blender --background --python-expr "import site; print(site.getsitepackages()[0])"

# Копируем YAML (замените пути на ваши)
sudo cp -r /usr/lib/python3/dist-packages/yaml /path/to/blender/python/lib/python3.x/site-packages/
```

### Метод 2: Использование conda

```bash
# Установка Blender через conda
conda install -c conda-forge blender

# Установка PyYAML
conda install -c conda-forge pyyaml
```

### Метод 3: Ручная компиляция

```bash
# Скачиваем исходники PyYAML
wget https://github.com/yaml/pyyaml/archive/refs/tags/6.0.1.zip
unzip 6.0.1.zip
cd pyyaml-6.0.1

# Компилируем и устанавливаем
/usr/bin/blender --background --python-expr "import subprocess; subprocess.run(['python', 'setup.py', 'install'], cwd='$(pwd)')"
```

## 🧪 Проверка установки

После установки создайте тестовый скрипт:

```python
# test_yaml.py
import bpy
import yaml

print("Тестирование YAML в Blender...")

# Тестовые данные
data = {
    'scene': {
        'name': 'Test Scene',
        'objects': ['Cube', 'Sphere'],
        'settings': {
            'resolution': [1920, 1080]
        }
    }
}

# Сохраняем в YAML
yaml_content = yaml.dump(data, default_flow_style=False)
print("YAML контент:")
print(yaml_content)

# Загружаем обратно
loaded_data = yaml.safe_load(yaml_content)
print("Загруженные данные:")
print(loaded_data)

print("✅ YAML работает!")
```

Запустите тест:

```bash
blender --background --python test_yaml.py
```

## 🐛 Решение проблем

### Проблема: "No module named 'yaml'"

**Решение:**
1. Убедитесь, что PyYAML установлен в правильный Python интерпретатор
2. Проверьте, что Blender использует тот же Python, где установлен PyYAML
3. Попробуйте переустановить PyYAML

### Проблема: "Permission denied" при установке

**Решение:**
```bash
# Используйте --user флаг
/usr/bin/blender --background --python-expr "import subprocess; subprocess.run(['pip', 'install', '--user', 'PyYAML'])"
```

### Проблема: Blender не найден

**Решение:**
1. Убедитесь, что Blender установлен и добавлен в PATH
2. Используйте полный путь к исполняемому файлу Blender
3. Проверьте права доступа к файлу

### Проблема: Конфликт версий Python

**Решение:**
1. Используйте виртуальное окружение
2. Установите Blender через conda
3. Используйте AppImage версию Blender

## 📚 Использование в проекте

После успешной установки PyYAML, вы можете использовать его в ваших Blender скриптах:

```python
import bpy
import yaml
from pathlib import Path

# Загрузка конфигурации
def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Сохранение конфигурации
def save_config(config_data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

# Пример использования
config = load_config('scene_config.yaml')
print(f"Загружено {len(config.get('shots', []))} шотов")
```

## 🔗 Полезные ссылки

- [Официальная документация PyYAML](https://pyyaml.org/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Репозиторий PyYAML на GitHub](https://github.com/yaml/pyyaml)

## 📝 Примечания

- PyYAML версии 6.0+ рекомендуется для совместимости с современными версиями Python
- Некоторые дистрибутивы Linux могут иметь устаревшие версии PyYAML в репозиториях
- При использовании AppImage версии Blender, PyYAML нужно устанавливать в виртуальное окружение
- Для продакшн использования рекомендуется зафиксировать версию PyYAML в requirements.txt