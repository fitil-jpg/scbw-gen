#!/usr/bin/env python3
"""
Скрипт для рендерингу USD сцени з використанням Storm рендер-делегата
"""
import sys
from pxr import Usd, UsdImagingGL, Gf

def render_usd_scene(usd_file, output_image="output.png", width=800, height=600):
    """
    Рендерить USD сцену в зображення
    """
    # Створюємо stage
    stage = Usd.Stage.Open(usd_file)
    if not stage:
        print(f"Помилка: не вдалося відкрити файл {usd_file}")
        return False
    
    # Налаштовуємо рендер-контекст
    renderer = UsdImagingGL.Engine()
    
    # Встановлюємо розмір зображення
    renderer.SetRendererAov("color")
    
    # Рендеримо сцену
    try:
        # Отримуємо камеру
        camera_prim = stage.GetPrimAtPath("/World/Camera")
        if not camera_prim:
            print("Помилка: камера не знайдена")
            return False
        
        # Рендеримо
        result = renderer.Render(stage, camera_prim, width, height)
        
        if result:
            print(f"Рендеринг завершено успішно: {output_image}")
            return True
        else:
            print("Помилка рендерингу")
            return False
            
    except Exception as e:
        print(f"Помилка під час рендерингу: {e}")
        return False

if __name__ == "__main__":
    usd_file = "scene.usda"
    if len(sys.argv) > 1:
        usd_file = sys.argv[1]
    
    output_file = "output.png"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    print(f"Рендеринг сцени: {usd_file}")
    print(f"Вихідний файл: {output_file}")
    
    success = render_usd_scene(usd_file, output_file)
    if success:
        print("Рендеринг завершено!")
    else:
        print("Рендеринг не вдався!")
        sys.exit(1)