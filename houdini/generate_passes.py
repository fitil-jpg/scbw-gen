"""CLI entry point for building SCBW multi-pass EXRs with Houdini."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

if __package__ in {None, ""}:  # pragma: no cover - executed when run as a script
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from houdini.config import ConfigError, PackConfig, filter_shots, list_shot_ids, load_pack_config
from houdini.passes import FrameRange, HoudiniSession, PassAssembler

try:  # pragma: no cover - hython-only dependency
    import hou  # type: ignore
except Exception:  # pragma: no cover
    hou = None  # type: ignore


LOG = logging.getLogger(__name__)


def _parse_arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("params/pack.yaml"), help="Pack description (YAML/JSON)")
    parser.add_argument("--shot", dest="shots", action="append", help="Only render the specified shot ID(s)")
    parser.add_argument("--list-shots", action="store_true", help="List shots defined in the configuration and exit")
    parser.add_argument("--output", type=Path, default=Path("renders/houdini"), help="Output directory for rendered passes")
    parser.add_argument("--hip-file", type=Path, help="Optional HIP file to load before rendering")
    parser.add_argument("--control-node", help="Houdini node path that accepts shot parameters")
    parser.add_argument("--render-root", default="/out/scbw_passes", help="Parent node containing per-plane ROPs")
    parser.add_argument("--exr-driver", default="/out/scbw_exr_packager", help="ROP that packs the multi-plane EXR")
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
    parser.add_argument("--dry-run", action="store_true", help="Skip Houdini calls and just report actions")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args(argv)


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
    control_node: Optional[str],
    render_root: str,
    exr_driver: Optional[str],
    frame_range: Sequence[int],
    hip_file: Optional[Path],
    dry_run: bool,
) -> int:
    selected_shots = filter_shots(config, shots)
    if not selected_shots:
        LOG.warning("No matching shots found; nothing to do")
        return 0

    assembler = PassAssembler(
        config=config,
        output_directory=output,
        passes=passes,
        control_node_path=control_node,
        render_root=render_root,
        exr_driver=exr_driver,
        frame_range=FrameRange(*frame_range),
    )

    if hou is None and not dry_run:
        LOG.warning("hou module is unavailable; falling back to dry-run mode")
        dry_run = True

    manifests: List = []
    if dry_run:
        manifests = assembler.process_shots(selected_shots, dry_run=True)
    else:
        with HoudiniSession(hip_file):
            manifests = assembler.process_shots(selected_shots, dry_run=False)

    for manifest in manifests:
        LOG.info("Shot %s", manifest.shot.id)
        for plane, path in sorted(manifest.pass_paths.items()):
            LOG.info("  %s -> %s", plane, path)
        if manifest.packed_exr:
            LOG.info("  multi-plane -> %s", manifest.packed_exr)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_arguments(argv)
    _configure_logging(args.verbose)

    try:
        config = load_pack_config(args.config)
    except ConfigError as exc:
        LOG.error("%s", exc)
        return 2

    if args.list_shots:
        return _list_and_exit(config)

    try:
        return _render(
            config=config,
            shots=args.shots or [],
            output=args.output,
            passes=args.passes,
            control_node=args.control_node,
            render_root=args.render_root,
            exr_driver=args.exr_driver,
            frame_range=args.frame_range,
            hip_file=args.hip_file,
            dry_run=args.dry_run,
        )
    except ConfigError as exc:
        LOG.error("%s", exc)
        return 3


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
