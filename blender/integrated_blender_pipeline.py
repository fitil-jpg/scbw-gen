"""
Інтегрований Blender пайплайн
Об'єднує імпорт конфігурації, генерацію геометрії та рендеринг
"""

import bpy
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Додавання поточної директорії до шляху
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Імпорт модулів
from enhanced_config_importer import EnhancedConfigImporter
from enhanced_geometry_generator import EnhancedGeometryGenerator
from enhanced_render_pipeline import EnhancedRenderPipeline

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedBlenderPipeline:
    """Інтегрований Blender пайплайн"""
    
    def __init__(self, config_dir: str = "assets", output_dir: str = "renders/blender"):
        self.config_importer = EnhancedConfigImporter(config_dir)
        self.geometry_generator = EnhancedGeometryGenerator()
        self.render_pipeline = EnhancedRenderPipeline(output_dir)
        self.current_shot = None
    
    def process_shot(self, shot_id: str, shot_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Обробляє повний цикл шоту: імпорт -> генерація -> рендеринг
        
        Args:
            shot_id: Ідентифікатор шоту
            shot_config: Конфігурація шоту (опціонально)
        
        Returns:
            Результати обробки шоту
        """
        try:
            logger.info(f"Початок обробки шоту: {shot_id}")
            
            # 1. Імпорт конфігурації
            if shot_config is None:
                shot_config = self.config_importer.get_shot_config(shot_id)
            
            self.current_shot = shot_id
            
            # 2. Генерація геометрії
            self.geometry_generator.generate_scene_from_config(shot_config)
            
            # 3. Налаштування рендерингу
            render_settings = shot_config.get("render_settings", {})
            self.render_pipeline.setup_render_engine(
                render_settings.get("engine", "CYCLES"),
                render_settings
            )
            self.render_pipeline.setup_render_settings(render_settings)
            
            # 4. Створення рендер пасів
            passes_config = shot_config.get("render_passes", [])
            if passes_config:
                self.render_pipeline.create_render_passes(shot_id, passes_config)
            
            # 5. Рендеринг
            if shot_config.get("is_animation", False):
                rendered_files = self.render_pipeline.render_animation(
                    shot_id,
                    shot_config.get("start_frame", 1),
                    shot_config.get("end_frame", 1)
                )
            else:
                rendered_files = [self.render_pipeline.render_shot(
                    shot_id,
                    shot_config.get("frame", 1)
                )]
            
            # 6. Створення маніфесту
            manifest = self.render_pipeline.create_render_manifest(rendered_files, shot_id)
            
            result = {
                "shot_id": shot_id,
                "status": "success",
                "rendered_files": rendered_files,
                "manifest": manifest,
                "config": shot_config
            }
            
            logger.info(f"Шот оброблено успішно: {shot_id}")
            return result
            
        except Exception as e:
            logger.error(f"Помилка обробки шоту {shot_id}: {e}")
            return {
                "shot_id": shot_id,
                "status": "error",
                "error": str(e),
                "rendered_files": [],
                "manifest": None
            }
    
    def batch_process_shots(self, shots_config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Обробляє кілька шотів пакетно
        
        Args:
            shots_config: Список конфігурацій шотів
        
        Returns:
            Результати обробки всіх шотів
        """
        try:
            results = {}
            
            for shot_config in shots_config:
                shot_id = shot_config.get("shot_id", "unknown")
                result = self.process_shot(shot_id, shot_config)
                results[shot_id] = result
            
            # Підсумкова статистика
            successful = sum(1 for r in results.values() if r["status"] == "success")
            failed = sum(1 for r in results.values() if r["status"] == "error")
            
            logger.info(f"Пакетна обробка завершена: {successful} успішних, {failed} помилок")
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка пакетної обробки: {e}")
            raise
    
    def create_shot_from_template(self, template_name: str, shot_id: str, 
                                 custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Створює шот на основі шаблону
        
        Args:
            template_name: Назва шаблону
            shot_id: Ідентифікатор шоту
            custom_params: Додаткові параметри
        
        Returns:
            Конфігурація створеного шоту
        """
        try:
            # Завантаження шаблону
            template_config = self.config_importer.load_config("templates", template_name)
            
            # Створення конфігурації шоту
            shot_config = template_config.copy()
            shot_config["shot_id"] = shot_id
            
            # Застосування додаткових параметрів
            if custom_params:
                shot_config.update(custom_params)
            
            # Збереження конфігурації
            self.config_importer.save_config(shot_config, "shots", shot_id)
            
            logger.info(f"Шот створено з шаблону: {template_name} -> {shot_id}")
            return shot_config
            
        except Exception as e:
            logger.error(f"Помилка створення шоту з шаблону: {e}")
            raise
    
    def export_scene(self, shot_id: str, export_format: str = "blend") -> Path:
        """
        Експортує сцену у різних форматах
        
        Args:
            shot_id: Ідентифікатор шоту
            export_format: Формат експорту (blend, fbx, obj, usd)
        
        Returns:
            Шлях до експортованого файлу
        """
        try:
            export_dir = self.render_pipeline.output_dir / shot_id / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            if export_format == "blend":
                # Експорт у .blend файл
                export_path = export_dir / f"{shot_id}.blend"
                bpy.ops.wm.save_as_mainfile(filepath=str(export_path))
                
            elif export_format == "fbx":
                # Експорт у .fbx файл
                export_path = export_dir / f"{shot_id}.fbx"
                bpy.ops.export_scene.fbx(filepath=str(export_path))
                
            elif export_format == "obj":
                # Експорт у .obj файл
                export_path = export_dir / f"{shot_id}.obj"
                bpy.ops.export_scene.obj(filepath=str(export_path))
                
            elif export_format == "usd":
                # Експорт у .usd файл
                export_path = export_dir / f"{shot_id}.usd"
                bpy.ops.wm.usd_export(filepath=str(export_path))
                
            else:
                raise ValueError(f"Непідтримуваний формат експорту: {export_format}")
            
            logger.info(f"Сцена експортована: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Помилка експорту сцени: {e}")
            raise
    
    def get_scene_info(self) -> Dict[str, Any]:
        """Повертає інформацію про поточну сцену"""
        try:
            scene = bpy.context.scene
            
            info = {
                "objects_count": len(scene.objects),
                "materials_count": len(bpy.data.materials),
                "lights_count": len([obj for obj in scene.objects if obj.type == 'LIGHT']),
                "cameras_count": len([obj for obj in scene.objects if obj.type == 'CAMERA']),
                "meshes_count": len([obj for obj in scene.objects if obj.type == 'MESH']),
                "render_engine": scene.render.engine,
                "resolution": [scene.render.resolution_x, scene.render.resolution_y],
                "frame_range": [scene.frame_start, scene.frame_end],
                "current_frame": scene.frame_current
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Помилка отримання інформації про сцену: {e}")
            return {}
    
    def cleanup_scene(self) -> None:
        """Очищає сцену"""
        try:
            self.geometry_generator.clear_scene()
            self.current_shot = None
            logger.info("Сцена очищена")
            
        except Exception as e:
            logger.error(f"Помилка очищення сцени: {e}")
    
    def validate_shot_config(self, shot_config: Dict[str, Any]) -> List[str]:
        """
        Валідує конфігурацію шоту
        
        Args:
            shot_config: Конфігурація шоту
        
        Returns:
            Список помилок валідації
        """
        errors = []
        
        # Перевірка обов'язкових полів
        required_fields = ["shot_id"]
        for field in required_fields:
            if field not in shot_config:
                errors.append(f"Відсутнє обов'язкове поле: {field}")
        
        # Перевірка конфігурації рендерингу
        if "render_settings" in shot_config:
            render_settings = shot_config["render_settings"]
            if "engine" not in render_settings:
                errors.append("Відсутній рендер двигун")
            elif render_settings["engine"] not in ["CYCLES", "BLENDER_EEVEE"]:
                errors.append("Невідомий рендер двигун")
        
        # Перевірка конфігурації камери
        if "camera" in shot_config:
            camera_config = shot_config["camera"]
            if "position" not in camera_config:
                errors.append("Відсутня позиція камери")
            if "rotation" not in camera_config:
                errors.append("Відсутнє обертання камери")
        
        return errors

# Приклад використання
if __name__ == "__main__":
    # Ініціалізація пайплайну
    pipeline = IntegratedBlenderPipeline("assets", "renders/blender")
    
    # Приклад конфігурації шоту
    shot_config = {
        "shot_id": "test_shot_001",
        "terrain": {
            "type": "plane",
            "size": [20, 20]
        },
        "buildings": [
            {
                "name": "Command Center",
                "type": "cube",
                "position": [0, 0, 0],
                "scale": [2, 2, 1.5],
                "materials": [
                    {
                        "name": "Metal",
                        "color": [0.8, 0.8, 0.9],
                        "metallic": 0.8,
                        "roughness": 0.2
                    }
                ]
            }
        ],
        "units": [
            {
                "name": "Marine",
                "type": "soldier",
                "position": [3, 0, 0],
                "scale": [1, 1, 1],
                "materials": [
                    {
                        "name": "Armor",
                        "color": [0.2, 0.2, 0.3],
                        "metallic": 0.1,
                        "roughness": 0.8
                    }
                ]
            }
        ],
        "camera": {
            "position": [0, -10, 5],
            "rotation": [60, 0, 0],
            "focal_length": 50
        },
        "lighting": {
            "sun_light": {
                "position": [10, 10, 10],
                "energy": 3.0,
                "color": [1.0, 0.95, 0.8]
            }
        },
        "render_settings": {
            "engine": "CYCLES",
            "samples": 128,
            "resolution": [1920, 1080],
            "output_format": "PNG",
            "denoising": True
        }
    }
    
    # Валідація конфігурації
    errors = pipeline.validate_shot_config(shot_config)
    if errors:
        print(f"Помилки валідації: {errors}")
    else:
        # Обробка шоту
        result = pipeline.process_shot("test_shot_001", shot_config)
        print(f"Результат обробки: {result['status']}")
        
        if result["status"] == "success":
            print(f"Зрендерено файлів: {len(result['rendered_files'])}")
            print(f"Маніфест: {result['manifest']}")
        
        # Експорт сцени
        export_path = pipeline.export_scene("test_shot_001", "blend")
        print(f"Сцена експортована: {export_path}")
        
        # Інформація про сцену
        scene_info = pipeline.get_scene_info()
        print(f"Інформація про сцену: {scene_info}")
