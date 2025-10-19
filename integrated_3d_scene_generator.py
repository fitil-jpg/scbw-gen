#!/usr/bin/env python3
"""
Integrated 3D Scene Generator with Asset Import and Instancing
Інтегрований генератор 3D сцен з імпортом асетів та інстансингом
"""

import os
import sys
import logging
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Додати поточну директорію до шляху для імпорту
sys.path.append(str(Path(__file__).parent))

from asset_3d_importer import Asset3DImporter, ModelFormat, ModelInstance
from asset_manager import AssetManager, AssetType
from config_manager import ConfigManager, ConfigType
from usd_utils import USDSceneUtils
from generate_usd_scene import USDSceneGenerator

try:
    from pxr import Usd, UsdGeom, UsdLux, Gf, Sdf, UsdShade
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("Warning: USD Python bindings not available")

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOG = logging.getLogger(__name__)


class Integrated3DSceneGenerator:
    """Інтегрований генератор 3D сцен з підтримкою імпорту асетів"""
    
    def __init__(self, assets_root: str = "assets", config_path: Optional[str] = None):
        self.assets_root = Path(assets_root)
        self.config_path = config_path
        
        # Ініціалізувати компоненти
        self.asset_manager = AssetManager(assets_root)
        self.config_manager = ConfigManager()
        self.asset_3d_importer = Asset3DImporter(assets_root, self.config_manager)
        
        # Завантажити конфігурацію сцени
        self.scene_config = self._load_scene_config()
        
        # USD stage
        self.stage = None
    
    def _load_scene_config(self) -> Dict[str, Any]:
        """Завантажити конфігурацію сцени"""
        if self.config_path and Path(self.config_path).exists():
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Конфігурація за замовчуванням
        return {
            'scene': {
                'name': 'Integrated 3D Scene',
                'terrain': {
                    'type': 'grassland',
                    'size': 200.0,
                    'height_variation': 0.3
                },
                'lighting': {
                    'sun_angle': [45, 30],
                    'sun_intensity': 1.0,
                    'ambient': 0.3
                }
            },
            '3d_assets': {
                'import_models': True,
                'use_instancing': True,
                'model_placement': {
                    'strategy': 'random',  # random, grid, formation
                    'density': 0.1,
                    'spacing': 5.0
                }
            },
            'buildings': {
                'enabled': True,
                'use_3d_models': True,
                'instancing_enabled': True
            },
            'units': {
                'enabled': True,
                'use_3d_models': True,
                'instancing_enabled': True
            }
        }
    
    def create_stage(self, output_path: str):
        """Створити USD stage"""
        if not USD_AVAILABLE:
            raise RuntimeError("USD Python bindings not available")
        
        self.stage = Usd.Stage.CreateNew(output_path)
        self.stage.SetMetadata("upAxis", "Y")
        self.stage.SetMetadata("metersPerUnit", 1.0)
        
        LOG.info(f"Створено USD stage: {output_path}")
    
    def setup_terrain(self):
        """Налаштувати рельєф"""
        terrain_config = self.scene_config.get('scene', {}).get('terrain', {})
        terrain_type = terrain_config.get('type', 'grassland')
        size = terrain_config.get('size', 200.0)
        
        # Створити площину рельєфу
        plane = UsdGeom.Plane.Define(self.stage, "/World/Terrain")
        plane.CreateSizeAttr(size)
        
        # Додати матеріал
        material = UsdShade.Material.Define(self.stage, "/World/Terrain/Material")
        shader = UsdShade.Shader.Define(self.stage, "/World/Terrain/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        
        # Кольори залежно від типу рельєфу
        terrain_colors = {
            'grassland': [0.2, 0.6, 0.2],
            'desert': [0.8, 0.6, 0.3],
            'snow': [0.9, 0.9, 0.9],
            'forest': [0.1, 0.4, 0.1]
        }
        
        color = terrain_colors.get(terrain_type, [0.2, 0.6, 0.2])
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color))
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(plane).Bind(material)
        
        LOG.info(f"Створено рельєф: {terrain_type}")
    
    def setup_lighting(self):
        """Налаштувати освітлення"""
        lighting_config = self.scene_config.get('scene', {}).get('lighting', {})
        sun_angle = lighting_config.get('sun_angle', [45, 30])
        sun_intensity = lighting_config.get('sun_intensity', 1.0)
        ambient = lighting_config.get('ambient', 0.3)
        
        USDSceneUtils.setup_lighting(
            self.stage, 
            sun_angle=tuple(sun_angle),
            sun_intensity=sun_intensity,
            ambient=ambient
        )
        
        LOG.info("Налаштовано освітлення")
    
    def import_3d_assets(self):
        """Імпортувати 3D асети"""
        if not self.scene_config.get('3d_assets', {}).get('import_models', True):
            return
        
        # Створити зразкові 3D моделі якщо не існують
        self._create_sample_3d_models()
        
        # Імпортувати моделі
        models_dir = self.assets_root / "3d_assets" / "models"
        imported_count = 0
        
        for model_file in models_dir.glob("*"):
            if model_file.suffix.lower() in ['.gltf', '.glb', '.obj', '.fbx', '.usd', '.dae']:
                try:
                    model = self.asset_3d_importer.import_model(model_file)
                    imported_count += 1
                    LOG.info(f"Імпортовано 3D модель: {model.name}")
                except Exception as e:
                    LOG.warning(f"Помилка імпорту {model_file}: {e}")
        
        LOG.info(f"Всього імпортовано 3D моделей: {imported_count}")
    
    def create_3d_buildings(self):
        """Створити 3D будівлі з інстансингом"""
        if not self.scene_config.get('buildings', {}).get('enabled', True):
            return
        
        buildings_config = self.scene_config.get('buildings', {})
        use_3d_models = buildings_config.get('use_3d_models', True)
        use_instancing = buildings_config.get('instancing_enabled', True)
        
        if not use_3d_models:
            # Використати стандартні будівлі
            self._create_standard_buildings()
            return
        
        # Знайти підходящі 3D моделі для будівель
        building_models = self._find_building_models()
        
        if not building_models:
            LOG.warning("Не знайдено 3D моделей для будівель")
            return
        
        # Створити інстанси будівель
        building_positions = self._generate_building_positions()
        
        for i, position in enumerate(building_positions):
            # Вибрати випадкову модель будівлі
            model_key = random.choice(building_models)
            
            # Параметри будівлі
            rotation = (0, random.uniform(0, 360), 0)
            scale = (random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.8, 1.2))
            
            # Створити інстанс
            try:
                instance_id = self.asset_3d_importer.create_instance(
                    model_key=model_key,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    metadata={
                        'type': 'building',
                        'building_id': i,
                        'created_by': 'integrated_generator'
                    }
                )
                LOG.info(f"Створено 3D будівлю: {instance_id}")
                
            except Exception as e:
                LOG.error(f"Помилка створення 3D будівлі: {e}")
    
    def create_3d_units(self):
        """Створити 3D юніти з інстансингом"""
        if not self.scene_config.get('units', {}).get('enabled', True):
            return
        
        units_config = self.scene_config.get('units', {})
        use_3d_models = units_config.get('use_3d_models', True)
        use_instancing = units_config.get('instancing_enabled', True)
        
        if not use_3d_models:
            # Використати стандартні юніти
            self._create_standard_units()
            return
        
        # Знайти підходящі 3D моделі для юнітів
        unit_models = self._find_unit_models()
        
        if not unit_models:
            LOG.warning("Не знайдено 3D моделей для юнітів")
            return
        
        # Створити інстанси юнітів
        unit_positions = self._generate_unit_positions()
        
        for i, position in enumerate(unit_positions):
            # Вибрати випадкову модель юніта
            model_key = random.choice(unit_models)
            
            # Параметри юніта
            rotation = (0, random.uniform(0, 360), 0)
            scale = (random.uniform(0.9, 1.1), random.uniform(0.9, 1.1), random.uniform(0.9, 1.1))
            
            # Створити інстанс
            try:
                instance_id = self.asset_3d_importer.create_instance(
                    model_key=model_key,
                    position=position,
                    rotation=rotation,
                    scale=scale,
                    metadata={
                        'type': 'unit',
                        'unit_id': i,
                        'created_by': 'integrated_generator'
                    }
                )
                LOG.info(f"Створено 3D юніт: {instance_id}")
                
            except Exception as e:
                LOG.error(f"Помилка створення 3D юніта: {e}")
    
    def export_scene_with_instancing(self, output_path: str):
        """Експортувати сцену з інстансингом"""
        if not self.stage:
            raise RuntimeError("USD stage не створено")
        
        # Експортувати 3D асети з інстансингом
        try:
            self.asset_3d_importer.export_to_usd(output_path, use_instancing=True)
            LOG.info(f"Експортовано сцену з інстансингом: {output_path}")
        except Exception as e:
            LOG.error(f"Помилка експорту сцени: {e}")
    
    def _create_sample_3d_models(self):
        """Створити зразкові 3D моделі"""
        models_dir = self.assets_root / "3d_assets" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        sample_models = {
            'castle.gltf': 'building',
            'tower.obj': 'building',
            'barracks.fbx': 'building',
            'warrior.glb': 'unit',
            'archer.glb': 'unit',
            'mage.glb': 'unit'
        }
        
        for model_file, model_type in sample_models.items():
            model_path = models_dir / model_file
            if not model_path.exists():
                with open(model_path, 'w') as f:
                    f.write(f"# Placeholder {model_file} ({model_type})\n")
    
    def _find_building_models(self) -> List[str]:
        """Знайти моделі будівель"""
        building_models = []
        for model_key, model in self.asset_3d_importer.models.items():
            if 'castle' in model.name.lower() or 'tower' in model.name.lower() or 'barracks' in model.name.lower():
                building_models.append(model_key)
        return building_models
    
    def _find_unit_models(self) -> List[str]:
        """Знайти моделі юнітів"""
        unit_models = []
        for model_key, model in self.asset_3d_importer.models.items():
            if 'warrior' in model.name.lower() or 'archer' in model.name.lower() or 'mage' in model.name.lower():
                unit_models.append(model_key)
        return unit_models
    
    def _generate_building_positions(self) -> List[Tuple[float, float, float]]:
        """Генерувати позиції будівель"""
        positions = []
        count = random.randint(5, 15)
        
        for _ in range(count):
            x = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            y = 0.0  # На рівні землі
            positions.append((x, y, z))
        
        return positions
    
    def _generate_unit_positions(self) -> List[Tuple[float, float, float]]:
        """Генерувати позиції юнітів"""
        positions = []
        count = random.randint(20, 50)
        
        for _ in range(count):
            x = random.uniform(-90, 90)
            z = random.uniform(-90, 90)
            y = 0.0  # На рівні землі
            positions.append((x, y, z))
        
        return positions
    
    def _create_standard_buildings(self):
        """Створити стандартні будівлі (заглушка)"""
        LOG.info("Створення стандартних будівель")
    
    def _create_standard_units(self):
        """Створити стандартні юніти (заглушка)"""
        LOG.info("Створення стандартних юнітів")
    
    def generate_complete_scene(self, output_path: str):
        """Згенерувати повну сцену"""
        LOG.info("Генерація інтегрованої 3D сцени")
        
        try:
            # Створити stage
            self.create_stage(output_path)
            
            # Налаштувати базові елементи сцени
            self.setup_terrain()
            self.setup_lighting()
            
            # Імпортувати 3D асети
            self.import_3d_assets()
            
            # Створити 3D об'єкти
            self.create_3d_buildings()
            self.create_3d_units()
            
            # Зберегти сцену
            self.stage.Save()
            
            LOG.info(f"Сцена згенерована: {output_path}")
            
            # Показати статистику
            self._print_scene_statistics()
            
        except Exception as e:
            LOG.error(f"Помилка генерації сцени: {e}")
            raise
    
    def _print_scene_statistics(self):
        """Показати статистику сцени"""
        LOG.info("=== Статистика сцени ===")
        LOG.info(f"3D моделей: {len(self.asset_3d_importer.models)}")
        LOG.info(f"Інстансів: {len(self.asset_3d_importer.instances)}")
        
        for model_key, model in self.asset_3d_importer.models.items():
            LOG.info(f"  {model.name}: {len(model.instances)} інстансів")


def main():
    """Головна функція"""
    LOG.info("Запуск інтегрованого генератора 3D сцен")
    
    try:
        # Створити генератор
        generator = Integrated3DSceneGenerator("assets")
        
        # Згенерувати сцену
        output_path = "output/integrated_3d_scene.usda"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        generator.generate_complete_scene(output_path)
        
        LOG.info("Генерація завершена успішно!")
        
    except Exception as e:
        LOG.error(f"Помилка: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())