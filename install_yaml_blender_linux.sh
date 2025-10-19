#!/bin/bash
# Скрипт для установки PyYAML в Blender Python на Linux

set -e

echo "🐧 Установка PyYAML для Blender Python на Linux"
echo "================================================"

# Функция для поиска Blender
find_blender() {
    local blender_paths=(
        "/usr/bin/blender"
        "/usr/local/bin/blender"
        "/snap/bin/blender"
        "/opt/blender/blender"
        "/home/*/blender*/blender"
        "/home/*/Blender*/blender"
    )
    
    for path in "${blender_paths[@]}"; do
        if [[ "$path" == *"*"* ]]; then
            # Используем glob для поиска с wildcards
            for match in $path; do
                if [[ -f "$match" && -x "$match" ]]; then
                    echo "$match"
                    return 0
                fi
            done
        else
            if [[ -f "$path" && -x "$path" ]]; then
                echo "$path"
                return 0
            fi
        fi
    done
    
    # Пробуем which
    if command -v blender >/dev/null 2>&1; then
        command -v blender
        return 0
    fi
    
    return 1
}

# Функция для получения пути к Python Blender
get_blender_python() {
    local blender_exe="$1"
    
    # Пробуем получить через Blender
    local python_path
    python_path=$(blender --background --python-expr "import sys; print(sys.executable)" 2>/dev/null | tail -1)
    
    if [[ -n "$python_path" && -f "$python_path" ]]; then
        echo "$python_path"
        return 0
    fi
    
    # Fallback: угадываем путь
    local blender_dir
    blender_dir=$(dirname "$blender_exe")
    
    local possible_paths=(
        "$blender_dir/python/bin/python"
        "$blender_dir/python/python"
        "$blender_dir/../python/bin/python"
        "$blender_dir/../python/python"
        "/usr/lib/blender/python/bin/python"
        "/usr/local/lib/blender/python/bin/python"
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -f "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Функция для проверки установки YAML
check_yaml() {
    local python_exe="$1"
    
    if "$python_exe" -c "import yaml; print('PyYAML version:', yaml.__version__)" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Функция для установки через pip
install_via_pip() {
    local python_exe="$1"
    
    echo "📦 Установка PyYAML через pip..."
    
    # Обновляем pip
    "$python_exe" -m pip install --upgrade pip --quiet
    
    # Устанавливаем PyYAML
    "$python_exe" -m pip install "PyYAML>=6.0" --quiet
    
    return $?
}

# Функция для установки через системный пакетный менеджер
install_via_package_manager() {
    echo "📦 Попытка установки через системный пакетный менеджер..."
    
    # Определяем дистрибутив
    if command -v apt >/dev/null 2>&1; then
        # Ubuntu/Debian
        echo "Обнаружен apt, устанавливаем python3-yaml..."
        sudo apt update
        sudo apt install -y python3-yaml
        return $?
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora
        echo "Обнаружен dnf, устанавливаем python3-PyYAML..."
        sudo dnf install -y python3-PyYAML
        return $?
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        echo "Обнаружен pacman, устанавливаем python-yaml..."
        sudo pacman -S --noconfirm python-yaml
        return $?
    elif command -v zypper >/dev/null 2>&1; then
        # openSUSE
        echo "Обнаружен zypper, устанавливаем python3-PyYAML..."
        sudo zypper install -y python3-PyYAML
        return $?
    else
        echo "❌ Неизвестный пакетный менеджер"
        return 1
    fi
}

# Функция для копирования системного YAML в Blender
copy_system_yaml() {
    local python_exe="$1"
    
    echo "📋 Копирование системного YAML в Blender..."
    
    # Находим системный YAML
    local system_yaml
    system_yaml=$(python3 -c "import yaml; print(yaml.__file__)" 2>/dev/null || echo "")
    
    if [[ -z "$system_yaml" ]]; then
        echo "❌ Системный YAML не найден"
        return 1
    fi
    
    # Находим директорию site-packages Blender
    local blender_site_packages
    blender_site_packages=$("$python_exe" -c "import site; print(site.getsitepackages()[0])" 2>/dev/null)
    
    if [[ -z "$blender_site_packages" ]]; then
        echo "❌ Не удалось найти site-packages Blender"
        return 1
    fi
    
    # Копируем YAML
    sudo cp -r "$(dirname "$system_yaml")" "$blender_site_packages/"
    
    return $?
}

# Функция для создания тестового скрипта
create_test_script() {
    cat > test_yaml_blender.py << 'EOF'
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
EOF
    
    echo "✅ Создан тестовый скрипт: test_yaml_blender.py"
}

# Основная логика
main() {
    # 1. Находим Blender
    echo "🔍 Поиск Blender..."
    BLENDER_EXE=$(find_blender)
    
    if [[ -z "$BLENDER_EXE" ]]; then
        echo "❌ Blender не найден в системе"
        echo ""
        echo "Установите Blender:"
        echo "  Ubuntu/Debian: sudo apt install blender"
        echo "  Fedora:        sudo dnf install blender"
        echo "  Arch Linux:    sudo pacman -S blender"
        echo "  Snap:          sudo snap install blender"
        exit 1
    fi
    
    echo "✅ Найден Blender: $BLENDER_EXE"
    
    # 2. Находим Python Blender
    echo "🔍 Поиск Python интерпретатора Blender..."
    BLENDER_PYTHON=$(get_blender_python "$BLENDER_EXE")
    
    if [[ -z "$BLENDER_PYTHON" ]]; then
        echo "❌ Не удалось найти Python интерпретатор Blender"
        exit 1
    fi
    
    echo "✅ Найден Python: $BLENDER_PYTHON"
    
    # 3. Проверяем, установлен ли уже YAML
    echo "🔍 Проверка установки PyYAML..."
    if check_yaml "$BLENDER_PYTHON"; then
        echo "✅ PyYAML уже установлен!"
        create_test_script
        exit 0
    fi
    
    echo "⚠ PyYAML не установлен, начинаем установку..."
    
    # 4. Пытаемся установить через pip
    if install_via_pip "$BLENDER_PYTHON"; then
        if check_yaml "$BLENDER_PYTHON"; then
            echo "✅ PyYAML успешно установлен через pip!"
            create_test_script
            exit 0
        fi
    fi
    
    # 5. Пытаемся установить через системный пакетный менеджер
    if install_via_package_manager; then
        if check_yaml "$BLENDER_PYTHON"; then
            echo "✅ PyYAML установлен через системный пакетный менеджер!"
            create_test_script
            exit 0
        fi
    fi
    
    # 6. Пытаемся скопировать системный YAML
    if copy_system_yaml "$BLENDER_PYTHON"; then
        if check_yaml "$BLENDER_PYTHON"; then
            echo "✅ PyYAML скопирован из системной установки!"
            create_test_script
            exit 0
        fi
    fi
    
    echo "❌ Не удалось установить PyYAML"
    echo ""
    echo "Альтернативные решения:"
    echo "1. Установите Blender через conda: conda install -c conda-forge blender"
    echo "2. Используйте AppImage версию Blender с собственным Python"
    echo "3. Скомпилируйте PyYAML из исходников"
    
    exit 1
}

# Запускаем основную функцию
main "$@"