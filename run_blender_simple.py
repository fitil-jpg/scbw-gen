#!/usr/bin/env python3
"""
Простий скрипт для запуску Blender pipeline
"""
import subprocess
import sys
import os

def main():
    print("🎬 Запуск Blender StarCraft Pipeline")
    print("=" * 50)
    
    # Перевірка наявності Blender
    try:
        result = subprocess.run(["blender", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Blender знайдено")
            print(result.stdout.split('\n')[0])
        else:
            print("❌ Blender не знайдено")
            return 1
    except FileNotFoundError:
        print("❌ Blender не встановлено")
        return 1
    
    # Створення директорії для результатів
    os.makedirs("renders/blender", exist_ok=True)
    
    # Запуск Blender з нашим скриптом
    cmd = [
        "blender",
        "--background",
        "--python", "blender/generate_passes.py",
        "--",
        "--config", "params/pack.yaml",
        "--shot", "shot_1001",
        "--output", "renders/blender",
        "--dry-run",
        "--verbose"
    ]
    
    print(f"\n🚀 Запуск команди: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("\n=== Результат ===")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Команда виконана успішно")
        else:
            print(f"❌ Команда завершилася з кодом {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Помилка при запуску: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())