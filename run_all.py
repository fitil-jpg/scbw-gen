#!/usr/bin/env python3
"""
Головний скрипт для генерації та рендерингу USD сцени
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Запускає команду та виводить результат"""
    print(f"\n=== {description} ===")
    print(f"Команда: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Успішно!")
            if result.stdout:
                print("Вивід:")
                print(result.stdout)
        else:
            print("❌ Помилка!")
            if result.stderr:
                print("Помилка:")
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Виняток: {e}")
        return False

def main():
    print("🎬 USD Scene Generator and Renderer")
    print("=" * 50)
    
    # 1. Генерація сцени
    success = run_command("python3 build_scene.py", "Генерація USD сцени")
    if not success:
        print("❌ Не вдалося згенерувати сцену!")
        return
    
    # 2. Перевірка сцени
    run_command("python3 check_scene.py", "Аналіз згенерованої сцени")
    
    # 3. Перевірка наявності рендер-інструментів
    print("\n=== Перевірка рендер-інструментів ===")
    
    # Перевірка usdrecord
    usdrecord_available = run_command("which usdrecord", "Перевірка usdrecord")
    
    # Перевірка Blender
    blender_available = run_command("which blender", "Перевірка Blender")
    
    # 4. Рендеринг (якщо доступний інструмент)
    if usdrecord_available:
        print("\n=== Рендеринг через usdrecord ===")
        run_command("usdrecord scene.usda output_usdrecord.png --camera /World/Camera --width 800 --height 600", 
                   "Рендеринг через usdrecord")
    elif blender_available:
        print("\n=== Рендеринг через Blender ===")
        run_command("python3 render_with_blender.py", "Рендеринг через Blender")
    else:
        print("\n=== Рендеринг недоступний ===")
        print("Для рендерингу встановіть один з інструментів:")
        print("1. usdrecord (частина повного OpenUSD SDK)")
        print("2. Blender: brew install --cask blender")
        print("3. Houdini (якщо доступний)")
    
    # 5. Показ результатів
    print("\n=== Результати ===")
    if os.path.exists("scene.usda"):
        print("✅ USD сцена згенерована: scene.usda")
        print(f"   Розмір файлу: {os.path.getsize('scene.usda')} байт")
    
    # Перевірка зображень
    image_files = ["output.png", "output_usdrecord.png"]
    for img in image_files:
        if os.path.exists(img):
            print(f"✅ Зображення створено: {img}")
            print(f"   Розмір файлу: {os.path.getsize(img)} байт")
    
    print("\n🎉 Готово!")

if __name__ == "__main__":
    main()