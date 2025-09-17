"""Configuration helpers for Houdini automation scripts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - yaml is optional during tests
    yaml = None  # type: ignore


class ConfigError(RuntimeError):
    """Raised when a configuration file cannot be parsed or queried."""


@dataclass
class ShotParameters:
    """Container describing a single shot entry in the pack file."""

    id: str
    raw: Mapping[str, Any]

    @property
    def export_settings(self) -> Mapping[str, Any]:
        return self.raw.get("export", {})


@dataclass
class PackConfig:
    """Represents the SCBW pack description consumed by Houdini scripts."""

    path: Path
    data: MutableMapping[str, Any]

    @property
    def shots(self) -> List[ShotParameters]:
        shots_data = self.data.get("shots", [])
        if not isinstance(shots_data, Iterable):
            raise ConfigError(
                f"'shots' in {self.path} must be iterable, got: {type(shots_data)!r}."
            )
        resolved: List[ShotParameters] = []

        for index, entry in enumerate(shots_data):
            if not isinstance(entry, Mapping):
                raise ConfigError(
                    f"Shot entry at index {index} in {self.path} must be a mapping, got: {type(entry)!r}."
                )

            if "id" not in entry:
                raise ConfigError(
                    f"Shot entry at index {index} in {self.path} is missing required 'id'."
                )

            shot_id = entry["id"]
            if not isinstance(shot_id, str):
                raise ConfigError(
                    f"Shot entry at index {index} in {self.path} must have a string 'id', got: {type(shot_id)!r}."
                )

            resolved.append(ShotParameters(id=shot_id, raw=entry))

        return resolved

    def find_shot(self, shot_id: str) -> ShotParameters:
        for shot in self.shots:
            if shot.id == shot_id:
                return shot
        raise ConfigError(f"Shot '{shot_id}' was not found in {self.path}.")


_SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}


def load_pack_config(path: Path) -> PackConfig:
    """Load the YAML/JSON pack configuration."""

    if not path.exists():
        raise ConfigError(f"Configuration file '{path}' does not exist.")

    if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
        raise ConfigError(
            f"Unsupported configuration extension '{path.suffix}'. "
            "Expected one of: " + ", ".join(sorted(_SUPPORTED_EXTENSIONS))
        )

    if path.suffix.lower() == ".json":
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Failed to parse JSON configuration at '{path}': {exc}") from exc
    else:
        if yaml is None:
            raise ConfigError("pyyaml is required to load YAML configuration files.")
        try:
            data = yaml.safe_load(path.read_text())  # type: ignore[arg-type]
        except yaml.YAMLError as exc:  # type: ignore[attr-defined]
            raise ConfigError(f"Failed to parse YAML configuration at '{path}': {exc}") from exc

    if not isinstance(data, MutableMapping):
        raise ConfigError(f"Configuration root must be a mapping, got: {type(data)!r}")

    return PackConfig(path=path, data=data)


def list_shot_ids(config: PackConfig) -> List[str]:
    """Return all shot identifiers defined in the pack file."""

    return [shot.id for shot in config.shots]


def filter_shots(config: PackConfig, shot_ids: Optional[Iterable[str]]) -> List[ShotParameters]:
    """Return the subset of shots requested by the user."""

    if not shot_ids:
        return config.shots

    resolved: List[ShotParameters] = []
    for shot_id in shot_ids:
        resolved.append(config.find_shot(shot_id))
    return resolved


__all__ = ["ConfigError", "PackConfig", "ShotParameters", "load_pack_config", "list_shot_ids", "filter_shots"]
