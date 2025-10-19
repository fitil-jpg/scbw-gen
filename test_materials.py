#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціональності матеріалів
"""

import bpy
import sys
from pathlib import Path

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent))

def test_material_creation():
    """Тестує створення матеріалів"""
    print("Тестування створення матеріалів...")
    
    try:
        from blender.material_generator import StarCraftMaterialGenerator
        
        # Ініціалізація генератора
        material_gen = StarCraftMaterialGenerator()
        
        # Тест 1: Створення матеріалу для юніта
        marine_material = material_gen.create_unit_material("marine", (0.2, 0.4, 0.8))
        assert marine_material is not None
        assert marine_material.name == "SC_marine_Material"
        print("✓ Матеріал для юніта створено успішно")
        
        # Тест 2: Створення матеріалу для території
        grass_material = material_gen.create_terrain_material("grass")
        assert grass_material is not None
        assert grass_material.name == "Terrain_grass_Material"
        print("✓ Матеріал для території створено успішно")
        
        # Тест 3: Створення UI матеріалу
        hud_material = material_gen.create_ui_material("hud")
        assert hud_material is not None
        assert hud_material.name == "UI_hud_Material"
        print("✓ UI матеріал створено успішно")
        
        # Тест 4: Створення матеріалу ефекту
        portal_material = material_gen.create_effect_material("portal")
        assert portal_material is not None
        assert portal_material.name == "Effect_portal_Material"
        print("✓ Матеріал ефекту створено успішно")
        
        print("Всі тести матеріалів пройшли успішно!")
        return True
        
    except Exception as e:
        print(f"✗ Помилка в тестах матеріалів: {e}")
        return False

def test_scene_generation():
    """Тестує генерацію сцени"""
    print("Тестування генерації сцени...")
    
    try:
        from blender.enhanced_scene_generator import EnhancedStarCraftSceneGenerator
        
        # Конфігурація
        config = type('Config', (), {'image_size': [1920, 1080]})()
        
        # Створення генератора
        generator = EnhancedStarCraftSceneGenerator(config)
        
        # Конфігурація шоту
        shot_config = {
            "terrain_type": "grass",
            "left_cluster": {
                "rect": [0.2, 0.5],
                "count": 3,
                "size": [16, 32],
                "unit_type": "marine"
            },
            "right_cluster": {
                "rect": [0.8, 0.5],
                "count": 3,
                "size": [16, 32],
                "unit_type": "zealot"
            },
            "hud": True
        }
        
        # Генерація сцени
        generator.setup_scene(shot_config)
        
        # Перевірка створених об'єктів
        objects = bpy.context.scene.objects
        assert len(objects) > 0
        print(f"✓ Створено {len(objects)} об'єктів")
        
        # Перевірка матеріалів
        materials = bpy.data.materials
        assert len(materials) > 0
        print(f"✓ Створено {len(materials)} матеріалів")
        
        print("Тест генерації сцени пройшов успішно!")
        return True
        
    except Exception as e:
        print(f"✗ Помилка в тесті генерації сцени: {e}")
        return False

def test_uv_mapping():
    """Тестує UV-розгортання"""
    print("Тестування UV-розгортання...")
    
    try:
        from blender.material_generator import StarCraftMaterialGenerator
        
        # Створення тестового об'єкта
        bpy.ops.mesh.primitive_cube_add(size=2)
        test_obj = bpy.context.object
        test_obj.name = "Test_UV_Object"
        
        # Ініціалізація генератора
        material_gen = StarCraftMaterialGenerator()
        
        # Тест різних типів UV-розгортання
        mapping_types = ["smart", "cube", "cylinder", "sphere"]
        
        for mapping_type in mapping_types:
            # Створення копії об'єкта для тесту
            bpy.ops.object.duplicate()
            test_copy = bpy.context.object
            test_copy.name = f"Test_UV_{mapping_type}"
            
            # Застосування UV-розгортання
            material_gen.apply_uv_mapping(test_copy, mapping_type)
            
            # Перевірка, чи є UV дані
            if test_copy.data.uv_layers:
                print(f"✓ UV-розгортання {mapping_type} працює")
            else:
                print(f"✗ UV-розгортання {mapping_type} не працює")
        
        print("Тест UV-розгортання завершено!")
        return True
        
    except Exception as e:
        print(f"✗ Помилка в тесті UV-розгортання: {e}")
        return False

def test_procedural_materials():
    """Тестує створення процедурних матеріалів"""
    print("Тестування процедурних матеріалів...")
    
    try:
        # Створення тестового об'єкта
        bpy.ops.mesh.primitive_cube_add(size=1)
        test_obj = bpy.context.object
        test_obj.name = "Test_Procedural"
        
        # Створення процедурного матеріалу
        material = bpy.data.materials.new(name="Test_Procedural_Material")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        
        # Noise texture
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 5.0
        noise.inputs['Detail'].default_value = 15.0
        noise.location = (-400, 0)
        
        # Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (200, 0)
        
        # Connections
        material.node_tree.links.new(noise.outputs['Color'], bsdf.inputs['Base Color'])
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Застосування матеріалу
        test_obj.data.materials.append(material)
        
        # Перевірка
        assert len(test_obj.data.materials) > 0
        assert test_obj.data.materials[0].name == "Test_Procedural_Material"
        
        print("✓ Процедурний матеріал створено успішно")
        print("Тест процедурних матеріалів пройшов успішно!")
        return True
        
    except Exception as e:
        print(f"✗ Помилка в тесті процедурних матеріалів: {e}")
        return False

def run_all_tests():
    """Запускає всі тести"""
    print("=== Запуск тестів матеріалів ===")
    
    # Очищення сцени
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Запуск тестів
    tests = [
        test_material_creation,
        test_scene_generation,
        test_uv_mapping,
        test_procedural_materials
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Критична помилка в тесті {test.__name__}: {e}")
    
    print(f"\n=== Результати тестів ===")
    print(f"Пройдено: {passed}/{total}")
    print(f"Успішність: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 Всі тести пройшли успішно!")
    else:
        print("⚠️ Деякі тести не пройшли")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)