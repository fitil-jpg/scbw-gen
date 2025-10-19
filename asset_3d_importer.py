#!/usr/bin/env python3
"""
3D Asset Importer with Instancing Support
Імпортер 3D асетів з підтримкою інстансингу для GLTF/FBX/OBJ файлів
"""

import os
import logging
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import yaml

try:
    from pxr import Usd, UsdGeom, UsdLux, Gf, Sdf, UsdShade, UsdPhysics
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("Warning: USD Python bindings not available. Install with: pip install usd-core")

from asset_manager import AssetManager, AssetType, AssetInfo, AssetStatus
from config_manager import ConfigManager, ConfigType

LOG = logging.getLogger(__name__)


class ModelFormat(Enum):
    """Підтримувані формати 3D моделей"""
    GLTF = "gltf"
    GLB = "glb"
    FBX = "fbx"
    OBJ = "obj"
    USD = "usd"
    USDA = "usda"
    USDC = "usdc"
    BLEND = "blend"
    DAE = "dae"


@dataclass
class ModelInstance:
    """Інстанс 3D моделі"""
    instance_id: str
    model_path: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    material_overrides: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelAsset:
    """3D модель асет"""
    name: str
    path: Path
    format: ModelFormat
    size: int
    checksum: str
    bounding_box: Tuple[Tuple[float, float, float], Tuple[float, float, float]]
    vertex_count: int = 0
    material_count: int = 0
    texture_count: int = 0
    animation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    instances: List[ModelInstance] = field(default_factory=list)
    status: AssetStatus = AssetStatus.UNKNOWN


@dataclass
class InstancingConfig:
    """Конфігурація інстансингу"""
    max_instances_per_model: int = 1000
    enable_lod: bool = True
    lod_distances: List[float] = field(default_factory=lambda: [10.0, 50.0, 100.0])
    culling_distance: float = 200.0
    batch_size: int = 100
    enable_frustum_culling: bool = True
    enable_occlusion_culling: bool = False


class Asset3DImporter:
    """Імпортер 3D асетів з підтримкою інстансингу"""
    
    def __init__(self, assets_root: Union[str, Path] = "assets", 
                 config_manager: Optional[ConfigManager] = None):
        self.assets_root = Path(assets_root)
        self.config_manager = config_manager or ConfigManager()
        self.asset_manager = AssetManager(assets_root)
        
        # Кеш 3D моделей
        self.models: Dict[str, ModelAsset] = {}
        self.instances: Dict[str, ModelInstance] = {}
        
        # Конфігурація інстансингу
        self.instancing_config = InstancingConfig()
        
        # Підтримувані формати
        self.supported_formats = {
            '.gltf': ModelFormat.GLTF,
            '.glb': ModelFormat.GLB,
            '.fbx': ModelFormat.FBX,
            '.obj': ModelFormat.OBJ,
            '.usd': ModelFormat.USD,
            '.usda': ModelFormat.USDA,
            '.usdc': ModelFormat.USDC,
            '.blend': ModelFormat.BLEND,
            '.dae': ModelFormat.DAE
        }
        
        # Завантажити конфігурацію
        self._load_config()
        
        # Створити директорії
        self._setup_directories()
    
    def _load_config(self) -> None:
        """Завантажити конфігурацію 3D асетів"""
        config_path = self.assets_root / "3d_assets" / "config.yaml"
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                # Завантажити налаштування інстансингу
                instancing_data = config_data.get('instancing', {})
                self.instancing_config = InstancingConfig(
                    max_instances_per_model=instancing_data.get('max_instances_per_model', 1000),
                    enable_lod=instancing_data.get('enable_lod', True),
                    lod_distances=instancing_data.get('lod_distances', [10.0, 50.0, 100.0]),
                    culling_distance=instancing_data.get('culling_distance', 200.0),
                    batch_size=instancing_data.get('batch_size', 100),
                    enable_frustum_culling=instancing_data.get('enable_frustum_culling', True),
                    enable_occlusion_culling=instancing_data.get('enable_occlusion_culling', False)
                )
                
                LOG.info("Завантажено конфігурацію 3D асетів")
                
            except Exception as e:
                LOG.warning(f"Помилка завантаження конфігурації 3D асетів: {e}")
        else:
            # Створити конфігурацію за замовчуванням
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Створити конфігурацію за замовчуванням"""
        config_data = {
            'instancing': {
                'max_instances_per_model': 1000,
                'enable_lod': True,
                'lod_distances': [10.0, 50.0, 100.0],
                'culling_distance': 200.0,
                'batch_size': 100,
                'enable_frustum_culling': True,
                'enable_occlusion_culling': False
            },
            'asset_paths': {
                'models': '3d_assets/models',
                'textures': '3d_assets/textures',
                'materials': '3d_assets/materials',
                'animations': '3d_assets/animations'
            },
            'import_settings': {
                'auto_scale': True,
                'normalize_scale': 1.0,
                'merge_materials': True,
                'generate_tangents': True,
                'optimize_meshes': True
            }
        }
        
        config_path = self.assets_root / "3d_assets" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        LOG.info("Створено конфігурацію 3D асетів за замовчуванням")
    
    def _setup_directories(self) -> None:
        """Створити необхідні директорії"""
        directories = [
            self.assets_root / "3d_assets",
            self.assets_root / "3d_assets" / "models",
            self.assets_root / "3d_assets" / "textures",
            self.assets_root / "3d_assets" / "materials",
            self.assets_root / "3d_assets" / "animations",
            self.assets_root / "3d_assets" / "instances"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def import_model(self, file_path: Union[str, Path], 
                    auto_register: bool = True) -> ModelAsset:
        """Імпортувати 3D модель"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл моделі не існує: {file_path}")
        
        # Визначити формат
        model_format = self._detect_model_format(file_path)
        if not model_format:
            raise ValueError(f"Непідтримуваний формат файлу: {file_path}")
        
        # Отримати інформацію про файл
        file_info = self.asset_manager.file_utils.get_file_info(file_path)
        if not file_info:
            raise ValueError(f"Не вдалося отримати інформацію про файл: {file_path}")
        
        # Витягти метадані моделі
        metadata = self._extract_model_metadata(file_path, model_format)
        
        # Створити об'єкт моделі
        model_asset = ModelAsset(
            name=file_path.stem,
            path=file_path,
            format=model_format,
            size=file_info.size,
            checksum=file_info.checksum or "",
            bounding_box=metadata.get('bounding_box', ((0, 0, 0), (1, 1, 1))),
            vertex_count=metadata.get('vertex_count', 0),
            material_count=metadata.get('material_count', 0),
            texture_count=metadata.get('texture_count', 0),
            animation_count=metadata.get('animation_count', 0),
            metadata=metadata
        )
        
        # Валідувати модель
        self._validate_model(model_asset)
        
        # Зареєструвати в менеджері асетів
        if auto_register:
            asset_info = self.asset_manager.register_asset(
                file_path, 
                category="3d_models",
                auto_detect_type=True
            )
            model_asset.metadata['asset_key'] = f"3d_models_{file_path.stem}"
        
        # Зберегти в кеші
        model_key = f"{model_format.value}_{file_path.stem}"
        self.models[model_key] = model_asset
        
        LOG.info(f"Імпортовано 3D модель: {file_path} (формат: {model_format.value})")
        
        return model_asset
    
    def create_instance(self, model_key: str, 
                       position: Tuple[float, float, float],
                       rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                       scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
                       material_overrides: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Створити інстанс моделі"""
        if model_key not in self.models:
            raise ValueError(f"Модель не знайдена: {model_key}")
        
        model = self.models[model_key]
        
        # Перевірити ліміт інстансів
        if len(model.instances) >= self.instancing_config.max_instances_per_model:
            raise RuntimeError(f"Досягнуто максимальну кількість інстансів для моделі {model_key}")
        
        # Створити унікальний ID інстансу
        instance_id = f"{model_key}_inst_{len(model.instances)}"
        
        # Створити інстанс
        instance = ModelInstance(
            instance_id=instance_id,
            model_path=model_key,
            position=position,
            rotation=rotation,
            scale=scale,
            material_overrides=material_overrides or {},
            metadata=metadata or {}
        )
        
        # Додати до моделі
        model.instances.append(instance)
        
        # Зберегти в кеші інстансів
        self.instances[instance_id] = instance
        
        LOG.info(f"Створено інстанс: {instance_id} для моделі {model_key}")
        
        return instance_id
    
    def create_instances_from_config(self, config_path: Union[str, Path]) -> List[str]:
        """Створити інстанси з конфігураційного файлу"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Файл конфігурації не існує: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        instances = []
        
        for instance_config in config_data.get('instances', []):
            model_key = instance_config['model']
            position = tuple(instance_config['position'])
            rotation = tuple(instance_config.get('rotation', [0.0, 0.0, 0.0]))
            scale = tuple(instance_config.get('scale', [1.0, 1.0, 1.0]))
            material_overrides = instance_config.get('material_overrides', {})
            metadata = instance_config.get('metadata', {})
            
            instance_id = self.create_instance(
                model_key, position, rotation, scale, 
                material_overrides, metadata
            )
            instances.append(instance_id)
        
        LOG.info(f"Створено {len(instances)} інстансів з конфігурації")
        
        return instances
    
    def export_to_usd(self, output_path: Union[str, Path], 
                     use_instancing: bool = True) -> Path:
        """Експортувати 3D асети в USD файл з інстансингом"""
        if not USD_AVAILABLE:
            raise RuntimeError("USD Python bindings not available")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Створити USD stage
        stage = Usd.Stage.CreateNew(str(output_path))
        stage.SetMetadata("upAxis", "Y")
        stage.SetMetadata("metersPerUnit", 1.0)
        
        if use_instancing:
            self._export_with_instancing(stage)
        else:
            self._export_without_instancing(stage)
        
        # Зберегти stage
        stage.Save()
        
        LOG.info(f"Експортовано 3D асети в USD: {output_path}")
        
        return output_path
    
    def _export_with_instancing(self, stage: Usd.Stage) -> None:
        """Експорт з використанням інстансингу"""
        for model_key, model in self.models.items():
            if not model.instances:
                continue
            
            # Створити прототип моделі
            prototype_path = f"/World/Prototypes/{model.name}"
            self._create_model_prototype(stage, model, prototype_path)
            
            # Створити інстанси
            for instance in model.instances:
                instance_path = f"/World/Instances/{instance.instance_id}"
                self._create_instance(stage, prototype_path, instance_path, instance)
    
    def _export_without_instancing(self, stage: Usd.Stage) -> None:
        """Експорт без інстансингу (кожен інстанс як окремий об'єкт)"""
        for model_key, model in self.models.items():
            for instance in model.instances:
                instance_path = f"/World/Instances/{instance.instance_id}"
                self._create_model_instance(stage, model, instance_path, instance)
    
    def _create_model_prototype(self, stage: Usd.Stage, model: ModelAsset, 
                               prototype_path: str) -> None:
        """Створити прототип моделі для інстансингу"""
        # Для спрощення створюємо базову геометрію
        # В реальній реалізації тут буде імпорт з GLTF/FBX/OBJ
        
        if model.format in [ModelFormat.GLTF, ModelFormat.GLB]:
            self._import_gltf_model(stage, model, prototype_path)
        elif model.format == ModelFormat.OBJ:
            self._import_obj_model(stage, model, prototype_path)
        elif model.format in [ModelFormat.USD, ModelFormat.USDA, ModelFormat.USDC]:
            self._import_usd_model(stage, model, prototype_path)
        else:
            # Створити базову геометрію як заглушку
            self._create_placeholder_geometry(stage, model, prototype_path)
    
    def _create_instance(self, stage: Usd.Stage, prototype_path: str, 
                        instance_path: str, instance: ModelInstance) -> None:
        """Створити інстанс з прототипу"""
        # Створити Xform для інстансу
        xform = UsdGeom.Xform.Define(stage, instance_path)
        
        # Застосувати трансформації
        xform.AddTranslateOp().Set(Gf.Vec3f(*instance.position))
        xform.AddRotateXYZOp().Set(Gf.Vec3f(*instance.rotation))
        xform.AddScaleOp().Set(Gf.Vec3f(*instance.scale))
        
        # Створити посилання на прототип
        xform.GetPrim().CreateRelationship("prototype").SetTargets([prototype_path])
        
        # Додати метадані
        for key, value in instance.metadata.items():
            xform.GetPrim().SetMetadata(key, value)
    
    def _create_model_instance(self, stage: Usd.Stage, model: ModelAsset, 
                              instance_path: str, instance: ModelInstance) -> None:
        """Створити повний інстанс моделі без інстансингу"""
        # Створити Xform
        xform = UsdGeom.Xform.Define(stage, instance_path)
        
        # Застосувати трансформації
        xform.AddTranslateOp().Set(Gf.Vec3f(*instance.position))
        xform.AddRotateXYZOp().Set(Gf.Vec3f(*instance.rotation))
        xform.AddScaleOp().Set(Gf.Vec3f(*instance.scale))
        
        # Створити геометрію моделі
        self._create_model_prototype(stage, model, f"{instance_path}/Geometry")
    
    def _import_gltf_model(self, stage: Usd.Stage, model: ModelAsset, 
                          prototype_path: str) -> None:
        """Імпорт GLTF моделі (заглушка)"""
        # В реальній реалізації тут буде використання GLTF імпортера
        LOG.info(f"Імпорт GLTF моделі: {model.path}")
        self._create_placeholder_geometry(stage, model, prototype_path)
    
    def _import_obj_model(self, stage: Usd.Stage, model: ModelAsset, 
                         prototype_path: str) -> None:
        """Імпорт OBJ моделі (заглушка)"""
        # В реальній реалізації тут буде використання OBJ імпортера
        LOG.info(f"Імпорт OBJ моделі: {model.path}")
        self._create_placeholder_geometry(stage, model, prototype_path)
    
    def _import_usd_model(self, stage: Usd.Stage, model: ModelAsset, 
                         prototype_path: str) -> None:
        """Імпорт USD моделі"""
        try:
            # Завантажити USD файл як підсцену
            sub_stage = Usd.Stage.Open(str(model.path))
            if sub_stage:
                # Копіювати вміст підсцени
                Usd.Stage.CopyLayer(sub_stage.GetRootLayer(), stage.GetRootLayer())
                LOG.info(f"Імпортовано USD моделі: {model.path}")
            else:
                self._create_placeholder_geometry(stage, model, prototype_path)
        except Exception as e:
            LOG.warning(f"Помилка імпорту USD моделі {model.path}: {e}")
            self._create_placeholder_geometry(stage, model, prototype_path)
    
    def _create_placeholder_geometry(self, stage: Usd.Stage, model: ModelAsset, 
                                   prototype_path: str) -> None:
        """Створити заглушку геометрії"""
        # Створити куб як заглушку
        cube = UsdGeom.Cube.Define(stage, prototype_path)
        cube.CreateSizeAttr(2.0)
        
        # Додати матеріал
        material = UsdShade.Material.Define(stage, f"{prototype_path}/Material")
        shader = UsdShade.Shader.Define(stage, f"{prototype_path}/Material/Shader")
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(0.5, 0.5, 0.5)
        )
        
        material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI(cube).Bind(material)
    
    def _detect_model_format(self, file_path: Path) -> Optional[ModelFormat]:
        """Визначити формат 3D моделі"""
        suffix = file_path.suffix.lower()
        return self.supported_formats.get(suffix)
    
    def _extract_model_metadata(self, file_path: Path, 
                               model_format: ModelFormat) -> Dict[str, Any]:
        """Витягти метадані з 3D моделі"""
        metadata = {
            'file_format': model_format.value,
            'file_size': file_path.stat().st_size,
            'bounding_box': ((0, 0, 0), (1, 1, 1)),  # Заглушка
            'vertex_count': 0,
            'material_count': 0,
            'texture_count': 0,
            'animation_count': 0
        }
        
        # В реальній реалізації тут буде аналіз файлу моделі
        # для витягування реальних метаданих
        
        return metadata
    
    def _validate_model(self, model: ModelAsset) -> bool:
        """Валідувати 3D модель"""
        try:
            # Перевірити існування файлу
            if not model.path.exists():
                model.status = AssetStatus.MISSING
                return False
            
            # Перевірити розмір файлу
            if model.size == 0:
                model.status = AssetStatus.CORRUPTED
                return False
            
            # Базові перевірки формату
            if model.format not in self.supported_formats.values():
                model.status = AssetStatus.CORRUPTED
                return False
            
            model.status = AssetStatus.VALID
            return True
            
        except Exception as e:
            LOG.warning(f"Помилка валідації моделі {model.path}: {e}")
            model.status = AssetStatus.CORRUPTED
            return False
    
    def get_model(self, model_key: str) -> Optional[ModelAsset]:
        """Отримати модель за ключем"""
        return self.models.get(model_key)
    
    def get_instance(self, instance_id: str) -> Optional[ModelInstance]:
        """Отримати інстанс за ID"""
        return self.instances.get(instance_id)
    
    def list_models(self) -> List[ModelAsset]:
        """Список всіх моделей"""
        return list(self.models.values())
    
    def list_instances(self, model_key: Optional[str] = None) -> List[ModelInstance]:
        """Список інстансів"""
        if model_key:
            model = self.models.get(model_key)
            return model.instances if model else []
        return list(self.instances.values())
    
    def remove_instance(self, instance_id: str) -> bool:
        """Видалити інстанс"""
        if instance_id in self.instances:
            instance = self.instances[instance_id]
            model = self.models.get(instance.model_path)
            if model:
                model.instances = [i for i in model.instances if i.instance_id != instance_id]
            del self.instances[instance_id]
            LOG.info(f"Видалено інстанс: {instance_id}")
            return True
        return False
    
    def clear_instances(self, model_key: Optional[str] = None) -> int:
        """Очистити інстанси"""
        if model_key:
            model = self.models.get(model_key)
            if model:
                count = len(model.instances)
                model.instances.clear()
                # Видалити з кешу інстансів
                self.instances = {k: v for k, v in self.instances.items() 
                                if v.model_path != model_key}
                LOG.info(f"Очищено {count} інстансів для моделі {model_key}")
                return count
        else:
            count = len(self.instances)
            self.instances.clear()
            for model in self.models.values():
                model.instances.clear()
            LOG.info(f"Очищено всі інстанси: {count}")
            return count
        
        return 0
    
    def export_instances_config(self, output_path: Union[str, Path]) -> Path:
        """Експортувати конфігурацію інстансів"""
        output_path = Path(output_path)
        
        config_data = {
            'instances': []
        }
        
        for instance in self.instances.values():
            instance_data = {
                'model': instance.model_path,
                'position': list(instance.position),
                'rotation': list(instance.rotation),
                'scale': list(instance.scale),
                'material_overrides': instance.material_overrides,
                'metadata': instance.metadata
            }
            config_data['instances'].append(instance_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        LOG.info(f"Експортовано конфігурацію інстансів: {output_path}")
        
        return output_path


# Приклад використання
if __name__ == "__main__":
    # Налаштування логування
    logging.basicConfig(level=logging.INFO)
    
    # Створення імпортера 3D асетів
    importer = Asset3DImporter("assets")
    
    try:
        # Імпорт моделі (якщо файл існує)
        # model = importer.import_model("assets/3d_assets/models/test.gltf")
        
        # Створення інстансів
        # instance_id = importer.create_instance(
        #     "gltf_test", 
        #     position=(0, 0, 0),
        #     rotation=(0, 0, 0),
        #     scale=(1, 1, 1)
        # )
        
        # Експорт в USD
        # importer.export_to_usd("output/scene.usda", use_instancing=True)
        
        print("3D Asset Importer готовий до використання")
        
    except Exception as e:
        print(f"Помилка: {e}")