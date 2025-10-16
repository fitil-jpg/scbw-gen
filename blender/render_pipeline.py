"""Multi-pass rendering system for Blender SCBW pipeline."""

from __future__ import annotations

import bpy
import bpy_extras
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

LOG = logging.getLogger(__name__)


class RenderPass:
    """Configuration for a single render pass."""
    
    def __init__(self, name: str, output_path: Path, **kwargs):
        self.name = name
        self.output_path = output_path
        self.settings = kwargs
    
    def setup_render_settings(self, scene):
        """Apply pass-specific render settings to the scene."""
        # Override in subclasses
        pass


class RGBAPass(RenderPass):
    """Standard RGBA beauty pass."""
    
    def setup_render_settings(self, scene):
        """Set up for RGBA rendering."""
        # Use default render settings
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        
        # Ensure we're rendering RGBA
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'


class MaskPass(RenderPass):
    """Object selection mask pass."""
    
    def __init__(self, name: str, output_path: Path, object_names: List[str]):
        super().__init__(name, output_path)
        self.object_names = object_names
    
    def setup_render_settings(self, scene):
        """Set up for mask rendering."""
        # Hide all objects except the ones we want in the mask
        for obj in scene.objects:
            if obj.name in self.object_names:
                obj.hide_render = False
            else:
                obj.hide_render = True
        
        # Set up for mask rendering
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 1  # Fast rendering for masks
        
        # Use white material for mask objects
        mask_mat = bpy.data.materials.new(name="Mask_Material")
        mask_mat.use_nodes = True
        mask_mat.node_tree.nodes.clear()
        
        emission = mask_mat.node_tree.nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)  # White
        emission.inputs['Strength'].default_value = 1.0
        
        output = mask_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        mask_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Apply to mask objects
        for obj_name in self.object_names:
            obj = scene.objects.get(obj_name)
            if obj:
                obj.data.materials.clear()
                obj.data.materials.append(mask_mat)


class DepthPass(RenderPass):
    """Depth/Z-buffer pass."""
    
    def setup_render_settings(self, scene):
        """Set up for depth rendering."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 64
        
        # Enable depth pass
        scene.view_layers[0].use_pass_z = True
        
        # Set up compositor for depth output
        if not scene.use_nodes:
            scene.use_nodes = True
        
        tree = scene.node_tree
        tree.nodes.clear()
        
        # Add render layers node
        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)
        
        # Add output node
        output = tree.nodes.new(type='CompositorNodeOutputFile')
        output.location = (300, 0)
        output.base_path = str(self.output_path.parent)
        output.file_slots[0].path = self.output_path.stem
        
        # Connect depth output
        tree.links.new(render_layers.outputs['Depth'], output.inputs['Image'])


class MultiPassRenderer:
    """Handles multi-pass rendering for SCBW assets."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Default passes
        self.default_passes = ['rgba', 'mask', 'depth']
    
    def create_passes(self, shot_id: str, frame: int = 1) -> List[RenderPass]:
        """Create render passes for a shot."""
        passes = []
        
        # RGBA pass
        rgba_path = self.output_directory / f"{shot_id}_rgba_{frame:04d}.png"
        passes.append(RGBAPass("rgba", rgba_path))
        
        # Mask pass (all units)
        mask_path = self.output_directory / f"{shot_id}_mask_{frame:04d}.png"
        unit_objects = [obj.name for obj in bpy.context.scene.objects 
                       if obj.name.startswith("SCBW_Unit_")]
        passes.append(MaskPass("mask", mask_path, unit_objects))
        
        # Depth pass
        depth_path = self.output_directory / f"{shot_id}_depth_{frame:04d}.exr"
        passes.append(DepthPass("depth", depth_path))
        
        return passes
    
    def render_passes(self, shot_id: str, frame: int = 1) -> Dict[str, Path]:
        """Render all passes for a shot."""
        passes = self.create_passes(shot_id, frame)
        rendered_paths = {}
        
        for pass_obj in passes:
            LOG.info("Rendering pass: %s", pass_obj.name)
            
            # Set up render settings for this pass
            pass_obj.setup_render_settings(bpy.context.scene)
            
            # Set output path
            bpy.context.scene.render.filepath = str(pass_obj.output_path.parent / pass_obj.output_path.stem)
            
            # Render
            bpy.ops.render.render(write_still=True)
            
            rendered_paths[pass_obj.name] = pass_obj.output_path
        
        return rendered_paths
    
    def setup_compositor_for_exr(self, shot_id: str, frame: int = 1):
        """Set up compositor for multi-plane EXR output."""
        scene = bpy.context.scene
        
        if not scene.use_nodes:
            scene.use_nodes = True
        
        tree = scene.node_tree
        tree.nodes.clear()
        
        # Add render layers node
        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)
        
        # Add output node for EXR
        output = tree.nodes.new(type='CompositorNodeOutputFile')
        output.location = (300, 0)
        output.base_path = str(self.output_directory)
        output.file_slots[0].path = f"{shot_id}_multi_{frame:04d}"
        output.format.file_format = 'OPEN_EXR'
        output.format.color_mode = 'RGBA'
        output.format.color_depth = '16'
        
        # Connect RGBA output
        tree.links.new(render_layers.outputs['Image'], output.inputs['Image'])
        
        # Add depth output if available
        if 'Depth' in render_layers.outputs:
            depth_output = tree.nodes.new(type='CompositorNodeOutputFile')
            depth_output.location = (300, -200)
            depth_output.base_path = str(self.output_directory)
            depth_output.file_slots[0].path = f"{shot_id}_depth_{frame:04d}"
            depth_output.format.file_format = 'OPEN_EXR'
            depth_output.format.color_mode = 'BW'
            depth_output.format.color_depth = '16'
            
            tree.links.new(render_layers.outputs['Depth'], depth_output.inputs['Image'])