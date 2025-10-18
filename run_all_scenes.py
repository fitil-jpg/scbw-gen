#!/usr/bin/env python3
"""
Скрипт для запуску всіх StarCraft сцен
"""
import subprocess
import sys
import os
import time

def run_scene(script_name, description):
    """Запуск сцени з вимірюванням часу"""
    print(f"\n🎬 {description}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            "blender", "--background", "--python", script_name
        ], capture_output=True, text=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - Успішно! (Час: {duration:.1f}с)")
            return True
        else:
            print(f"❌ {description} - Помилка!")
            if result.stderr:
                print("Помилка:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ {description} - Виняток: {e}")
        return False

def main():
    print("🚀 StarCraft Scene Generation Pipeline")
    print("=" * 60)
    
    # Створення директорії для результатів
    os.makedirs("renders/blender", exist_ok=True)
    
    scenes = [
        ("test_blender_simple.py", "Тестова сцена (куб)"),
        ("create_starcraft_scene.py", "StarCraft сцена (повна)"),
        ("create_advanced_starcraft_scene.py", "Розширена сцена (з конфігурацією)")
    ]
    
    successful = 0
    total_time = 0
    
    for script, description in scenes:
        start_time = time.time()
        success = run_scene(script, description)
        end_time = time.time()
        
        if success:
            successful += 1
            total_time += (end_time - start_time)
    
    # Підсумок
    print(f"\n📊 Підсумок")
    print("=" * 30)
    print(f"✅ Успішно: {successful}/{len(scenes)} сцен")
    print(f"⏱️ Загальний час: {total_time:.1f} секунд")
    
    # Перевірка створених файлів
    print(f"\n📁 Створені файли:")
    if os.path.exists("renders/blender/"):
        files = os.listdir("renders/blender/")
        for file in sorted(files):
            if file.endswith('.png'):
                file_path = os.path.join("renders/blender", file)
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size/1024/1024:.1f} MB)")
    
    if successful == len(scenes):
        print(f"\n🎉 Всі сцени створені успішно!")
        print(f"📁 Результати збережено в: renders/blender/")
    else:
        print(f"\n⚠️ Деякі сцени не вдалося створити")
    
    return 0 if successful == len(scenes) else 1

if __name__ == "__main__":
    sys.exit(main())