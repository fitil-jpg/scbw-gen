#!/usr/bin/env python3
"""
Blender script to run the SCBW pipeline
"""
import sys
import os
from pathlib import Path

# Add workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import after setting up path
import bpy
from blender.config import load_pack_config, filter_shots
from blender.scene_generator import StarCraftSceneGenerator
from blender.render_pipeline import MultiPassRenderer
from blender.exr_packager import EXRPackager

def main():
    """Main function to run the Blender pipeline."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Blender SCBW Pipeline")
    parser.add_argument("--config", type=Path, default=Path("params/pack.yaml"))
    parser.add_argument("--shot", dest="shots", action="append", help="Shot ID(s) to render")
    parser.add_argument("--output", type=Path, default=Path("renders/blender"))
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--engine", choices=["cycles", "eevee"], default="cycles")
    
    # Parse arguments from sys.argv, skipping the first one (script name)
    args = parser.parse_args(sys.argv[1:])
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    print(f"Loading configuration from {args.config}")
    config = load_pack_config(args.config)
    
    selected_shots = filter_shots(config, args.shots)
    if not selected_shots:
        print("No shots selected")
        return 1
    
    if args.dry_run:
        print("DRY RUN MODE - No actual rendering will occur")
        for shot in selected_shots:
            print(f"Would render shot: {shot.id}")
            print(f"  Palette: {shot.palette}")
            print(f"  Export: {shot.export}")
        return 0
    
    # Initialize components
    scene_generator = StarCraftSceneGenerator(config)
    renderer = MultiPassRenderer(args.output, engine=('BLENDER_EEVEE' if args.engine.lower() == 'eevee' else 'CYCLES'))
    packager = EXRPackager(args.output)
    
    for shot in selected_shots:
        print(f"Processing shot: {shot.id}")
        
        # Generate scene
        scene_generator.setup_scene(shot)
        scene_generator.create_portal_effect(shot)
        
        # Render passes
        pass_paths = renderer.render_passes(shot.id, 1)
        
        # Package into EXR if requested
        packed_exr = None
        if shot.export.get("exr16", False) or shot.export.get("exr32", False):
            bit_depth = 16 if shot.export.get("exr16", False) else 32
            packed_exr = packager.package_passes(shot.id, pass_paths, 1, bit_depth)
        
        print(f"Shot {shot.id} completed")
        for plane, path in sorted(pass_paths.items()):
            print(f"  {plane} -> {path}")
        if packed_exr:
            print(f"  multi-plane -> {packed_exr}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())