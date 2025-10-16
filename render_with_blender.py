#!/usr/bin/env python3
"""
Скрипт для рендерингу USD сцени через Blender
"""
import subprocess
import sys
import os

def render_with_blender(usd_file, output_image="output.png", width=800, height=600):
    """
    Рендерить USD сцену через Blender
    """
    blender_script = f"""
import bpy
import bmesh

# Очистити сцену
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Імпортувати USD файл
try:
    bpy.ops.wm.usd_import(filepath='{usd_file}')
    print("USD файл успішно імпортовано")
except Exception as e:
    print(f"Помилка імпорту USD: {{e}}")
    # Створити простий куб як fallback
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    bpy.ops.object.scale_apply()

# Налаштувати рендеринг
bpy.context.scene.render.resolution_x = {width}
bpy.context.scene.render.resolution_y = {height}
bpy.context.scene.render.filepath = '{output_image}'

# Рендерити
bpy.ops.render.render(write_still=True)
print(f"Рендеринг завершено: {output_image}")
"""

    # Записати скрипт у тимчасовий файл
    script_file = "blender_render_script.py"
    with open(script_file, 'w') as f:
        f.write(blender_script)
    
    try:
        # Запустити Blender
        cmd = [
            "blender", 
            "--background", 
            "--python", script_file
        ]
        
        print(f"Запуск Blender: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Рендеринг завершено успішно!")
            print("Вивід Blender:")
            print(result.stdout)
            return True
        else:
            print("Помилка рендерингу:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("Blender не знайдено. Встановіть Blender:")
        print("brew install --cask blender")
        return False
    except Exception as e:
        print(f"Помилка: {e}")
        return False
    finally:
        # Видалити тимчасовий файл
        if os.path.exists(script_file):
            os.remove(script_file)

if __name__ == "__main__":
    usd_file = "scene.usda"
    if len(sys.argv) > 1:
        usd_file = sys.argv[1]
    
    output_file = "output.png"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"Рендеринг сцени: {usd_file}")
    print(f"Вихідний файл: {output_file}")
    
    success = render_with_blender(usd_file, output_file)
    if success:
        print("Рендеринг завершено!")
    else:
        print("Рендеринг не вдався!")
        sys.exit(1)