"""Helpers that orchestrate pass rendering in Houdini."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .config import PackConfig, ShotParameters

try:  # pragma: no cover - Houdini is not available in the unit test environment.
    import hou  # type: ignore
except Exception:  # pragma: no cover - hython-only dependency.
    hou = None  # type: ignore


LOG = logging.getLogger(__name__)


class HoudiniNotAvailableError(RuntimeError):
    """Raised when the :mod:`hou` module cannot be imported."""


@dataclass
class FrameRange:
    start: int = 1
    end: int = 1

    def as_tuple(self) -> Tuple[int, int]:
        return (self.start, self.end)


@dataclass
class PassManifest:
    """Describes the rendered outputs for a particular shot."""

    shot: ShotParameters
    pass_paths: Dict[str, Path] = field(default_factory=dict)
    packed_exr: Optional[Path] = None


_DEFAULT_PASS_ORDER = ("rgba", "mask", "depth")


class HoudiniSession:
    """Utility wrapper that validates access to the :mod:`hou` module."""

    def __init__(self, hip_file: Optional[Path] = None):
        self.hip_file = hip_file

    def __enter__(self) -> "HoudiniSession":
        if hou is None:
            raise HoudiniNotAvailableError(
                "The 'hou' module is unavailable. Run this script from hython or "
                "enable --dry-run when executing outside Houdini."
            )
        if self.hip_file:
            LOG.info("Loading HIP file: %s", self.hip_file)
            hou.hipFile.load(str(self.hip_file))
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # The Houdini session remains open; nothing to clean up explicitly.
        return None


class PassAssembler:
    """Sets up Houdini nodes and triggers rendering for a pack of shots."""

    def __init__(
        self,
        config: PackConfig,
        output_directory: Path,
        passes: Optional[Sequence[str]] = None,
        control_node_path: Optional[str] = None,
        render_root: str = "/out/scbw_passes",
        exr_driver: Optional[str] = "/out/scbw_exr_packager",
        frame_range: FrameRange = FrameRange(),
    ) -> None:
        self.config = config
        self.output_directory = output_directory
        self.passes = list(passes) if passes else list(_DEFAULT_PASS_ORDER)
        self.control_node_path = control_node_path
        self.render_root = render_root
        self.exr_driver = exr_driver
        self.frame_range = frame_range

    # ------------------------------------------------------------------
    # High level workflow
    # ------------------------------------------------------------------
    def process_shots(self, shots: Iterable[ShotParameters], dry_run: bool = False) -> List[PassManifest]:
        manifests: List[PassManifest] = []
        for shot in shots:
            LOG.info("Processing shot %s", shot.id)
            manifest = PassManifest(shot=shot)
            if dry_run or hou is None:
                LOG.info("Dry-run mode active; skipping Houdini execution for shot %s", shot.id)
                manifest.pass_paths = self._simulate_pass_paths(shot)
                manifest.packed_exr = self.output_directory / f"{shot.id}.exr"
                manifests.append(manifest)
                continue

            self._ensure_output_directory()
            self._apply_global_parameters(shot)
            manifest.pass_paths = self._render_passes(shot)
            manifest.packed_exr = self._pack_exr(shot, manifest.pass_paths)
            manifests.append(manifest)
        return manifests

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _ensure_output_directory(self) -> None:
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def _apply_global_parameters(self, shot: ShotParameters) -> None:
        if not self.control_node_path:
            return
        node = hou.node(self.control_node_path)
        if node is None:
            raise HoudiniNotAvailableError(
                f"Configured control node '{self.control_node_path}' does not exist in the scene."
            )

        LOG.debug("Updating control node %s with parameters for %s", self.control_node_path, shot.id)
        if node.parm("shot_id"):
            node.parm("shot_id").set(shot.id)
        if node.parm("shot_json"):
            node.parm("shot_json").set(json.dumps(shot.raw))
        else:
            node.setUserData(f"scbw::shot::{shot.id}", json.dumps(shot.raw))

    def _render_passes(self, shot: ShotParameters) -> Dict[str, Path]:
        outputs: Dict[str, Path] = {}
        render_parent = hou.node(self.render_root)
        if render_parent is None:
            raise HoudiniNotAvailableError(
                f"Render node container '{self.render_root}' does not exist."
            )

        for plane in self.passes:
            rop_path = f"{self.render_root}/{plane}"
            rop = hou.node(rop_path)
            if rop is None:
                raise HoudiniNotAvailableError(
                    f"Expected ROP node '{rop_path}' for plane '{plane}', but it was not found."
                )

            LOG.info("Rendering %s -> %s", shot.id, rop_path)
            output_path = self._configure_output_path(rop, shot, plane)
            rop.render(frame_range=self.frame_range.as_tuple(), ignore_inputs=True)
            if output_path:
                outputs[plane] = output_path
        return outputs

    def _configure_output_path(self, rop, shot: ShotParameters, plane: str) -> Optional[Path]:
        output_parm = self._find_output_parameter(rop)
        if output_parm is None:
            LOG.debug("ROP %s does not expose a recognizable output parameter", rop.path())
            return None

        filename = f"{shot.id}_{plane}.exr"
        output_path = self.output_directory / "passes" / shot.id
        output_path.mkdir(parents=True, exist_ok=True)
        full_path = output_path / filename
        LOG.debug("Configuring %s output to %s", rop.path(), full_path)
        output_parm.set(str(full_path))
        return full_path

    def _pack_exr(self, shot: ShotParameters, pass_paths: Mapping[str, Path]) -> Optional[Path]:
        if not self.exr_driver:
            return None
        driver = hou.node(self.exr_driver)
        if driver is None:
            raise HoudiniNotAvailableError(
                f"EXR driver '{self.exr_driver}' is not present in the HIP file."
            )

        output_path = self.output_directory / f"{shot.id}.exr"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._prime_packager_parameters(driver, shot, output_path, pass_paths)
        LOG.info("Packing multi-plane EXR for %s -> %s", shot.id, output_path)
        driver.render(frame_range=self.frame_range.as_tuple(), ignore_inputs=True)
        return output_path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _prime_packager_parameters(
        self,
        driver,
        shot: ShotParameters,
        output_path: Path,
        pass_paths: Mapping[str, Path],
    ) -> None:
        if driver.parm("vm_picture"):
            driver.parm("vm_picture").set(str(output_path))
        if driver.parm("scbw_pass_manifest"):
            driver.parm("scbw_pass_manifest").set(json.dumps({k: str(v) for k, v in pass_paths.items()}))
        if driver.parm("shot_id"):
            driver.parm("shot_id").set(shot.id)
        if driver.parm("bit_depth") and isinstance(shot.export_settings.get("exr16"), bool):
            driver.parm("bit_depth").set(16 if shot.export_settings["exr16"] else 32)

    def _find_output_parameter(self, rop) -> Optional["hou.Parm"]:  # type: ignore[name-defined]
        for name in ("vm_picture", "picture", "sopoutput", "copoutput"):
            parm = rop.parm(name)
            if parm is not None:
                return parm
        return None

    def _simulate_pass_paths(self, shot: ShotParameters) -> Dict[str, Path]:
        simulated: Dict[str, Path] = {}
        for plane in self.passes:
            simulated[plane] = self.output_directory / "passes" / shot.id / f"{shot.id}_{plane}.exr"
        return simulated


__all__ = [
    "FrameRange",
    "HoudiniNotAvailableError",
    "HoudiniSession",
    "PassAssembler",
    "PassManifest",
]
