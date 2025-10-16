#!/bin/bash
# Скрипт для встановлення Blender на macOS

echo "🎨 Встановлення Blender для рендерингу USD сцен..."

# Перевірка операційної системи
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Виявлено macOS"
    
    # Перевірка наявності Homebrew
    if command -v brew &> /dev/null; then
        echo "✅ Homebrew знайдено"
        echo "📦 Встановлення Blender..."
        brew install --cask blender
        
        if [ $? -eq 0 ]; then
            echo "✅ Blender успішно встановлено!"
            echo "📍 Blender встановлено в /Applications/Blender.app"
            echo ""
            echo "Тепер ви можете запустити рендеринг:"
            echo "python3 render_with_blender.py"
        else
            echo "❌ Помилка встановлення Blender"
            exit 1
        fi
    else
        echo "❌ Homebrew не знайдено"
        echo "Встановіть Homebrew спочатку:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
else
    echo "❌ Цей скрипт призначений для macOS"
    echo "Для Linux встановіть Blender через пакетний менеджер:"
    echo "sudo apt install blender  # Ubuntu/Debian"
    echo "sudo dnf install blender  # Fedora"
    echo "sudo pacman -S blender    # Arch Linux"
    exit 1
fi