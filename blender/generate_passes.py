"""CLI entry point for building SCBW multi-pass EXRs with Blender."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


def _add_user_site_packages_to_sys_path() -> None:
    """Ensure user's site-packages is importable (needed for PyYAML under Blender).

    Blender's embedded Python sometimes excludes user site-packages. When PyYAML is
    installed with "--user" via Blender's interpreter, it may land outside of
    sys.path and cause "ModuleNotFoundError: yaml". This function appends common
    user site-packages locations to sys.path if they exist.
    """
    try:
        import site  # noqa: WPS433  (module import inside function by design)

        user_sites = site.getusersitepackages()  # type: ignore[attr-defined]
        candidate_paths: List[str]
        if isinstance(user_sites, str):
            candidate_paths = [user_sites]
        else:
            candidate_paths = list(user_sites)
    except Exception:
        # Fall back to typical per-platform locations
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidate_paths = [
            str(Path.home() / ".local" / "lib" / f"python{py_ver}" / "site-packages"),  # Linux
            str(
                Path.home()
                / "Library"
                / "Python"
                / py_ver
                / "lib"
                / "python"
                / "site-packages"
            ),  # macOS
        ]

    for path in candidate_paths:
        if path and Path(path).is_dir() and path not in sys.path:
            sys.path.append(path)


# Make sure user-level site-packages (e.g., PyYAML) are importable under Blender
_add_user_site_packages_to_sys_path()

if __package__ in {None, ""}:  # pragma: no cover - executed when run as a script
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from blender.config import ConfigError, PackConfig, filter_shots, list_shot_ids, load_pack_config
from blender.scene_generator import StarCraftSceneGenerator
from blender.render_pipeline import MultiPassRenderer
from blender.exr_packager import EXRPackager, BlenderNotAvailableError, BlenderSession

try:  # pragma: no cover - blender-only dependency
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None  # type: ignore


LOG = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("params/pack.yaml")
FALLBACK_CONFIG_PATH = DEFAULT_CONFIG_PATH.with_suffix(".json")


def _parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Pack description (YAML/JSON, defaults to params/pack.yaml with params/pack.json as fallback)",
    )
    parser.add_argument("--shot", dest="shots", action="append", help="Only render the specified shot ID(s)")
    parser.add_argument("--list-shots", action="store_true", help="List shots defined in the configuration and exit")
    parser.add_argument("--output", type=Path, default=Path("renders/blender"), help="Output directory for rendered passes")
    parser.add_argument("--blend-file", type=Path, help="Optional BLEND file to load before rendering")
    parser.add_argument(
        "--passes",
        nargs="+",
        help="Override the list of AOVs/passes to render (default: rgba mask depth)",
    )
    parser.add_argument(
        "--frame-range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        default=(1, 1),
        help="Frame range to render (inclusive)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Skip Blender calls and just report actions")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--engine",
        choices=["cycles", "eevee"],
        default="cycles",
        help="Blender render engine to use (cycles or eevee)",
    )

    args = parser.parse_args(argv)

    raw_args = sys.argv[1:] if argv is None else list(argv)
    config_option_provided = any(arg == "--config" or arg.startswith("--config=") for arg in raw_args)

    args.config_was_default = not config_option_provided and args.config == DEFAULT_CONFIG_PATH
    args.config_fallback_used = False

    if args.config_was_default and not args.config.exists() and FALLBACK_CONFIG_PATH.exists():
        args.config = FALLBACK_CONFIG_PATH
        args.config_fallback_used = True

    return args


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")


def _list_and_exit(config: PackConfig) -> int:
    print("Available shots:")
    for shot_id in list_shot_ids(config):
        print(f"  - {shot_id}")
    return 0


def _render(
    config: PackConfig,
    shots: Iterable[str],
    output: Path,
    passes: Optional[Sequence[str]],
    frame_range: Sequence[int],
    blend_file: Optional[Path],
    dry_run: bool,
    engine: str,
) -> int:
    selected_shots = filter_shots(config, shots)
    if not selected_shots:
        LOG.warning("No matching shots found; nothing to do")
        return 0

    if bpy is None and not dry_run:
        LOG.warning("bpy module is unavailable; falling back to dry-run mode")
        dry_run = True

    manifests: List = []
    
    if dry_run:
        LOG.info("DRY RUN: Would render %d shots", len(selected_shots))
        for shot in selected_shots:
            LOG.info("  - Shot %s", shot.id)
            LOG.info("    Palette: %s", shot.palette)
            LOG.info("    Export: %s", shot.export)
        return 0

    with BlenderSession(blend_file):
        # Initialize components
        scene_generator = StarCraftSceneGenerator(config)
        renderer = MultiPassRenderer(output, engine=('BLENDER_EEVEE' if engine.lower() == 'eevee' else 'CYCLES'))
        packager = EXRPackager(output)
        
        for shot in selected_shots:
            LOG.info("Processing shot: %s", shot.id)
            
            # Generate scene
            scene_generator.setup_scene(shot)
            scene_generator.create_portal_effect(shot)
            
            # Render passes
            pass_paths = renderer.render_passes(shot.id, frame_range[0], list(passes) if passes else None)
            
            # Package into EXR if requested
            packed_exr = None
            if shot.export.get("exr16", False) or shot.export.get("exr32", False):
                bit_depth = 16 if shot.export.get("exr16", False) else 32
                packed_exr = packager.package_passes(shot.id, pass_paths, frame_range[0], bit_depth)
            
            # Create manifest
            manifest = packager.create_pass_manifest(shot.id, pass_paths, packed_exr)
            manifests.append(manifest)
            
            LOG.info("Shot %s completed", shot.id)
            for plane, path in sorted(pass_paths.items()):
                LOG.info("  %s -> %s", plane, path)
            if packed_exr:
                LOG.info("  multi-plane -> %s", packed_exr)

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_arguments(argv)
    _configure_logging(args.verbose)

    if getattr(args, "config_fallback_used", False):
        LOG.info(
            "Default configuration %s was not found; falling back to %s",
            DEFAULT_CONFIG_PATH,
            args.config,
        )

    LOG.info("Loading configuration from %s", args.config)

    try:
        config = load_pack_config(args.config)
    except ConfigError as exc:
        LOG.error("%s", exc)
        return 2

    resolved_path = getattr(config, "path", args.config)
    if resolved_path != args.config:
        LOG.info("Configuration resolved to %s", resolved_path)
        args.config_fallback_used = True

    if args.list_shots:
        return _list_and_exit(config)

    try:
        return _render(
            config=config,
            shots=args.shots or [],
            output=args.output,
            passes=args.passes,
            frame_range=args.frame_range,
            blend_file=args.blend_file,
            dry_run=args.dry_run,
            engine=args.engine,
        )
    except BlenderNotAvailableError as exc:
        LOG.error("%s", exc)
        return 4
    except ConfigError as exc:
        LOG.error("%s", exc)
        return 3


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())