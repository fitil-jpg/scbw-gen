"""EXR packaging system for multi-plane outputs."""

from __future__ import annotations

import bpy
import bpy_extras
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

LOG = logging.getLogger(__name__)


class EXRPackager:
    """Packages multiple render passes into multi-plane EXR files."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
    
    def package_passes(self, shot_id: str, pass_paths: Dict[str, Path], 
                      frame: int = 1, bit_depth: int = 16) -> Optional[Path]:
        """Package individual passes into a multi-plane EXR."""
        if not pass_paths:
            LOG.warning("No passes to package for shot %s", shot_id)
            return None
        
        # Set up compositor for multi-plane EXR
        scene = bpy.context.scene
        
        if not scene.use_nodes:
            scene.use_nodes = True
        
        tree = scene.node_tree
        tree.nodes.clear()
        
        # Create output node for multi-plane EXR
        output = tree.nodes.new(type='CompositorNodeOutputFile')
        output.location = (300, 0)
        output.base_path = str(self.output_directory)
        output.file_slots[0].path = f"{shot_id}_multi_{frame:04d}"
        output.format.file_format = 'OPEN_EXR'
        output.format.color_mode = 'RGBA'
        output.format.color_depth = str(bit_depth)
        
        # Add render layers node
        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)
        
        # Connect main RGBA output
        if 'rgba' in pass_paths:
            tree.links.new(render_layers.outputs['Image'], output.inputs['Image'])
        
        # Add additional planes for other passes
        plane_index = 1
        
        # Add mask plane
        if 'mask' in pass_paths:
            mask_output = tree.nodes.new(type='CompositorNodeOutputFile')
            mask_output.location = (300, -200)
            mask_output.base_path = str(self.output_directory)
            mask_output.file_slots[0].path = f"{shot_id}_mask_{frame:04d}"
            mask_output.format.file_format = 'OPEN_EXR'
            mask_output.format.color_mode = 'BW'
            mask_output.format.color_depth = str(bit_depth)
            
            # For mask, we need to create a separate render layer
            # This is a simplified approach - in production you'd want proper layer setup
            LOG.info("Mask pass will be packaged separately")
        
        # Add depth plane
        if 'depth' in pass_paths and 'Depth' in render_layers.outputs:
            depth_output = tree.nodes.new(type='CompositorNodeOutputFile')
            depth_output.location = (300, -400)
            depth_output.base_path = str(self.output_directory)
            depth_output.file_slots[0].path = f"{shot_id}_depth_{frame:04d}"
            depth_output.format.file_format = 'OPEN_EXR'
            depth_output.format.color_mode = 'BW'
            depth_output.format.color_depth = str(bit_depth)
            
            tree.links.new(render_layers.outputs['Depth'], depth_output.inputs['Image'])
        
        # Render the multi-plane EXR
        output_path = self.output_directory / f"{shot_id}_multi_{frame:04d}.exr"
        bpy.context.scene.render.filepath = str(output_path.parent / output_path.stem)
        bpy.ops.render.render(write_still=True)
        
        if output_path.exists():
            LOG.info("Created multi-plane EXR: %s", output_path)
            return output_path
        else:
            LOG.error("Failed to create multi-plane EXR: %s", output_path)
            return None
    
    def create_pass_manifest(self, shot_id: str, pass_paths: Dict[str, Path], 
                           packed_exr: Optional[Path]) -> Dict[str, any]:
        """Create a manifest of all passes for a shot."""
        manifest = {
            "shot_id": shot_id,
            "passes": {},
            "packed_exr": str(packed_exr) if packed_exr else None
        }
        
        for pass_name, pass_path in pass_paths.items():
            manifest["passes"][pass_name] = {
                "path": str(pass_path),
                "exists": pass_path.exists(),
                "size_bytes": pass_path.stat().st_size if pass_path.exists() else 0
            }
        
        return manifest


class BlenderNotAvailableError(Exception):
    """Raised when Blender Python API is not available."""
    pass


def check_blender_availability():
    """Check if Blender Python API is available."""
    try:
        import bpy
        return True
    except ImportError:
        return False


class BlenderSession:
    """Context manager for Blender sessions."""
    
    def __init__(self, blend_file: Optional[Path] = None):
        self.blend_file = blend_file
        self.original_file = None
    
    def __enter__(self):
        if not check_blender_availability():
            raise BlenderNotAvailableError("Blender Python API (bpy) is not available")
        
        # Save current file
        if bpy.data.filepath:
            self.original_file = Path(bpy.data.filepath)
        
        # Load specified file if provided
        if self.blend_file and self.blend_file.exists():
            bpy.ops.wm.open_mainfile(filepath=str(self.blend_file))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original file if it existed
        if self.original_file and self.original_file.exists():
            bpy.ops.wm.open_mainfile(filepath=str(self.original_file))
        elif not self.original_file:
            # If no original file, create a new one
            bpy.ops.wm.read_homefile(use_empty=True)