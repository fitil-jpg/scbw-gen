# Blender SCBW Pipeline

This directory contains the Blender-based pipeline for generating StarCraft: Brood War assets. It provides an alternative to the Houdini pipeline with similar functionality for multi-pass EXR generation.

## Features

- **Scene Assembly**: Automated generation of StarCraft battle scenes with units, terrain, and UI elements
- **Multi-Pass Rendering**: RGBA, mask, depth, and custom AOV passes
- **EXR Packaging**: Multi-plane EXR output compatible with compositing workflows
- **Configuration Driven**: Uses the same `pack.yaml` configuration as the Houdini pipeline

## Usage

```bash
blender --background --python blender/generate_passes.py \
  -- --config params/pack.yaml \
     --shot shot_1001 \
     --output renders/blender
```

## Requirements

- Blender 3.0+ with Python API
- bpy (Blender Python API)
- OpenEXR support for multi-plane EXR output
- Pillow for image processing