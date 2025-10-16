"""Configuration management for Blender SCBW pipeline."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

LOG = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration parsing or validation error."""


class ShotConfig:
    """Configuration for a single shot."""
    
    def __init__(self, shot_id: str, data: Dict[str, Any]):
        self.id = shot_id
        self.palette = data.get("palette", [])
        self.portal = data.get("portal", {})
        self.left_cluster = data.get("left_cluster", {})
        self.right_cluster = data.get("right_cluster", {})
        self.hud = data.get("hud", {})
        self.export = data.get("export", {})
        
        # Store raw data for custom parameters
        self.raw_data = data
    
    def get_palette_colors(self) -> List[List[float]]:
        """Get palette colors as RGB values (0-1 range)."""
        if isinstance(self.palette, str):
            # Handle named palettes
            return self._get_named_palette(self.palette)
        return self.palette
    
    def _get_named_palette(self, name: str) -> List[List[float]]:
        """Get colors for named palettes."""
        palettes = {
            "ArmyColors": [
                [0.2, 0.3, 0.8],  # Blue
                [0.8, 0.2, 0.2],  # Red
                [0.2, 0.8, 0.2],  # Green
            ]
        }
        return palettes.get(name, [[0.5, 0.5, 0.5]])


class PackConfig:
    """Main configuration container."""
    
    def __init__(self, data: Dict[str, Any], path: Optional[Path] = None):
        self.seed = data.get("seed", 1337)
        self.image_size = data.get("image_size", [1280, 720])
        self.shots = []
        
        for shot_data in data.get("shots", []):
            shot_id = shot_data.get("id")
            if not shot_id:
                raise ConfigError("Shot missing required 'id' field")
            self.shots.append(ShotConfig(shot_id, shot_data))
        
        self.path = path
    
    def get_shot(self, shot_id: str) -> Optional[ShotConfig]:
        """Get shot configuration by ID."""
        for shot in self.shots:
            if shot.id == shot_id:
                return shot
        return None
    
    def list_shot_ids(self) -> List[str]:
        """Get list of all shot IDs."""
        return [shot.id for shot in self.shots]


def load_pack_config(config_path: Path) -> PackConfig:
    """Load configuration from YAML or JSON file."""
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to parse configuration file: {e}")
    
    if not isinstance(data, dict):
        raise ConfigError("Configuration must be a dictionary")
    
    return PackConfig(data, config_path)


def filter_shots(config: PackConfig, shot_ids: Optional[List[str]]) -> List[ShotConfig]:
    """Filter shots by ID list."""
    if not shot_ids:
        return config.shots
    
    filtered = []
    for shot_id in shot_ids:
        shot = config.get_shot(shot_id)
        if shot:
            filtered.append(shot)
        else:
            LOG.warning("Shot '%s' not found in configuration", shot_id)
    
    return filtered