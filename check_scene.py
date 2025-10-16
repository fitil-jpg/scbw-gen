#!/usr/bin/env python3
"""
Скрипт для перевірки USD сцени
"""
from pxr import Usd, UsdGeom, UsdLux, Gf

def check_scene(usd_file):
    """
    Перевіряє USD сцену та виводить інформацію про неї
    """
    stage = Usd.Stage.Open(usd_file)
    if not stage:
        print(f"Помилка: не вдалося відкрити файл {usd_file}")
        return False
    
    print(f"=== Аналіз сцени: {usd_file} ===")
    print(f"Кореневий примітив: {stage.GetDefaultPrim().GetPath()}")
    
    # Перевіряємо всі примітиви
    for prim in stage.Traverse():
        print(f"Примітив: {prim.GetPath()}")
        print(f"  Тип: {prim.GetTypeName()}")
        
        # Перевіряємо атрибути трансформації
        xform_api = UsdGeom.XformCommonAPI(prim)
        if xform_api:
            # Отримуємо атрибути трансформації через UsdGeom.Xformable
            xformable = UsdGeom.Xformable(prim)
            if xformable:
                # Перевіряємо операції трансформації
                ops = xformable.GetOrderedXformOps()
                for op in ops:
                    print(f"  {op.GetOpName()}: {op.Get()}")
        
        # Перевіряємо специфічні атрибути
        if prim.GetTypeName() == "Cube":
            size_attr = prim.GetAttribute("size")
            if size_attr:
                print(f"  Розмір куба: {size_attr.Get()}")
        
        print()
    
    return True

if __name__ == "__main__":
    import sys
    usd_file = "scene.usda"
    if len(sys.argv) > 1:
        usd_file = sys.argv[1]
    
    check_scene(usd_file)