#!/bin/bash

# Скрипт для запуску тестів матеріалів

echo "=== Запуск тестів матеріалів ==="

# Перевірка наявності Blender
if ! command -v blender &> /dev/null; then
    echo "Помилка: Blender не знайдено. Встановіть Blender або додайте його до PATH."
    exit 1
fi

# Запуск тестів
echo "Запуск тестів..."
blender --background --python test_materials.py

# Перевірка результату
if [ $? -eq 0 ]; then
    echo "✅ Всі тести пройшли успішно!"
else
    echo "❌ Деякі тести не пройшли"
    exit 1
fi