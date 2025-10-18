"""Розширений імпортер конфігурації для Blender SCBW pipeline."""

from __future__ import annotations

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

LOG = logging.getLogger(__name__)


class AdvancedConfigImporter:
    """Розширений імпортер конфігурації з підтримкою різних форматів."""
    
    def __init__(self, config_path: Union[str, Path]):
        self.config_path = Path(config_path)
        self.config_data = {}
        self.asset_configs = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Завантажує основну конфігурацію з файлу."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Конфігураційний файл не знайдено: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix.lower() == '.json':
                self.config_data = json.load(f)
            else:
                self.config_data = yaml.safe_load(f)
        
        LOG.info(f"Завантажено конфігурацію з {self.config_path}")
        return self.config_data
    
    def load_asset_configs(self, assets_dir: Path = Path("assets")) -> Dict[str, Dict]:
        """Завантажує конфігурації асетів (будівлі, юніти, ефекти)."""
        self.asset_configs = {}
        
        # Завантаження конфігурацій будівель
        buildings_config = assets_dir / "buildings" / "buildings_config.yaml"
        if buildings_config.exists():
            with open(buildings_config, 'r', encoding='utf-8') as f:
                self.asset_configs['buildings'] = yaml.safe_load(f)
        
        # Завантаження конфігурацій юнітів
        units_config = assets_dir / "units" / "units_config.yaml"
        if units_config.exists():
            with open(units_config, 'r', encoding='utf-8') as f:
                self.asset_configs['units'] = yaml.safe_load(f)
        
        # Завантаження конфігурацій ефектів
        effects_config = assets_dir / "effects" / "effects_config.yaml"
        if effects_config.exists():
            with open(effects_config, 'r', encoding='utf-8') as f:
                self.asset_configs['effects'] = yaml.safe_load(f)
        
        # Завантаження конфігурації території
        terrain_config = assets_dir / "terrain" / "terrain_config.yaml"
        if terrain_config.exists():
            with open(terrain_config, 'r', encoding='utf-8') as f:
                self.asset_configs['terrain'] = yaml.safe_load(f)
        
        LOG.info(f"Завантажено {len(self.asset_configs)} конфігурацій асетів")
        return self.asset_configs
    
    def get_shot_config(self, shot_id: str) -> Optional[Dict[str, Any]]:
        """Отримує конфігурацію конкретного шоту."""
        shots = self.config_data.get('shots', [])
        for shot in shots:
            if shot.get('id') == shot_id:
                return shot
        return None
    
    def get_palette_colors(self, shot_config: Dict[str, Any]) -> List[List[float]]:
        """Отримує кольори палітри для шоту."""
        palette = shot_config.get('palette', [])
        
        # Якщо палітра - це рядок, шукаємо в попередньо визначених палітрах
        if isinstance(palette, str):
            predefined_palettes = {
                'ArmyColors': [
                    [0.2, 0.4, 0.8],  # Синя армія
                    [0.8, 0.2, 0.2],  # Червона армія
                    [0.2, 0.8, 0.2]   # Зелена армія
                ],
                'TerranColors': [
                    [0.3, 0.3, 0.4],  # Металічний сірий
                    [0.1, 0.1, 0.2],  # Темний синій
                    [0.5, 0.5, 0.6]   # Світлий сірий
                ],
                'ZergColors': [
                    [0.2, 0.4, 0.1],  # Темно-зелений
                    [0.4, 0.6, 0.2],  # Середній зелений
                    [0.6, 0.8, 0.3]   # Світлий зелений
                ],
                'ProtossColors': [
                    [0.8, 0.8, 0.2],  # Золотий
                    [0.2, 0.6, 0.8],  # Блакитний
                    [0.4, 0.2, 0.8]   # Фіолетовий
                ]
            }
            palette = predefined_palettes.get(palette, predefined_palettes['ArmyColors'])
        
        return palette
    
    def get_building_config(self, building_type: str) -> Optional[Dict[str, Any]]:
        """Отримує конфігурацію будівлі за типом."""
        buildings = self.asset_configs.get('buildings', {}).get('buildings', {})
        return buildings.get(building_type)
    
    def get_unit_config(self, unit_type: str) -> Optional[Dict[str, Any]]:
        """Отримує конфігурацію юніта за типом."""
        units = self.asset_configs.get('units', {}).get('units', {})
        return units.get(unit_type)
    
    def get_effect_config(self, effect_type: str) -> Optional[Dict[str, Any]]:
        """Отримує конфігурацію ефекту за типом."""
        effects = self.asset_configs.get('effects', {}).get('effects', {})
        return effects.get(effect_type)
    
    def validate_config(self) -> List[str]:
        """Валідує конфігурацію та повертає список помилок."""
        errors = []
        
        # Перевірка основної структури
        if 'shots' not in self.config_data:
            errors.append("Відсутня секція 'shots' в конфігурації")
        
        if 'image_size' not in self.config_data:
            errors.append("Відсутній параметр 'image_size'")
        
        # Перевірка кожного шоту
        for i, shot in enumerate(self.config_data.get('shots', [])):
            shot_id = shot.get('id')
            if not shot_id:
                errors.append(f"Шот {i+1}: відсутній ID")
                continue
            
            # Перевірка обов'язкових полів
            if 'palette' not in shot:
                errors.append(f"Шот {shot_id}: відсутня палітра кольорів")
            
            if 'left_cluster' not in shot and 'right_cluster' not in shot:
                errors.append(f"Шот {shot_id}: відсутні кластери юнітів")
        
        return errors
    
    def export_config_summary(self, output_path: Path) -> None:
        """Експортує зведення конфігурації в JSON файл."""
        summary = {
            'config_file': str(self.config_path),
            'total_shots': len(self.config_data.get('shots', [])),
            'image_size': self.config_data.get('image_size', [1280, 720]),
            'loaded_assets': {
                'buildings': len(self.asset_configs.get('buildings', {}).get('buildings', {})),
                'units': len(self.asset_configs.get('units', {}).get('units', {})),
                'effects': len(self.asset_configs.get('effects', {}).get('effects', {})),
                'terrain': len(self.asset_configs.get('terrain', {}).get('terrain', {}))
            },
            'shots': []
        }
        
        for shot in self.config_data.get('shots', []):
            shot_summary = {
                'id': shot.get('id'),
                'has_portal': 'portal' in shot,
                'has_left_cluster': 'left_cluster' in shot,
                'has_right_cluster': 'right_cluster' in shot,
                'has_hud': 'hud' in shot,
                'export_formats': shot.get('export', {})
            }
            summary['shots'].append(shot_summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        LOG.info(f"Зведення конфігурації експортовано в {output_path}")


def create_sample_config(output_path: Path) -> None:
    """Створює приклад конфігурації для тестування."""
    sample_config = {
        'seed': 1337,
        'image_size': [1920, 1080],
        'shots': [
            {
                'id': 'demo_shot_001',
                'palette': 'ArmyColors',
                'portal': {
                    'center': [0.5, 0.5],
                    'radius': 0.2,
                    'falloff': 0.25,
                    'invert': False
                },
                'left_cluster': {
                    'rect': [0.1, 0.4],
                    'count': 8,
                    'size': [20, 40],
                    'unit_types': ['marine', 'firebat', 'medic']
                },
                'right_cluster': {
                    'rect': [0.6, 0.6],
                    'count': 6,
                    'size': [18, 36],
                    'unit_types': ['zergling', 'hydralisk']
                },
                'buildings': [
                    {
                        'type': 'command_center',
                        'position': [0.2, 0.2],
                        'owner': 'left'
                    },
                    {
                        'type': 'hatchery',
                        'position': [0.8, 0.8],
                        'owner': 'right'
                    }
                ],
                'hud': {
                    'left': {
                        'Race': 'Terran',
                        'M': 2500,
                        'G': 1200,
                        'Supply': [65, 85],
                        'APM': 200
                    },
                    'right': {
                        'Race': 'Zerg',
                        'M': 2200,
                        'G': 1000,
                        'Supply': [70, 95],
                        'APM': 250
                    }
                },
                'export': {
                    'png': True,
                    'exr16': True,
                    'exr32': False
                }
            }
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f, default_flow_style=False, allow_unicode=True)
    
    LOG.info(f"Приклад конфігурації створено в {output_path}")


if __name__ == "__main__":
    # Тестування імпортера
    logging.basicConfig(level=logging.INFO)
    
    # Створення прикладу конфігурації
    sample_path = Path("sample_config.yaml")
    create_sample_config(sample_path)
    
    # Тестування завантаження
    importer = AdvancedConfigImporter(sample_path)
    config = importer.load_config()
    assets = importer.load_asset_configs()
    
    # Валідація
    errors = importer.validate_config()
    if errors:
        print("Помилки в конфігурації:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Конфігурація валідна!")
    
    # Експорт зведення
    importer.export_config_summary(Path("config_summary.json"))