"""Blender scene generation for StarCraft assets."""

from __future__ import annotations

import bmesh
import bpy
import bpy_extras
import mathutils
from mathutils import Vector, Color
from typing import List, Dict, Any, Tuple
import logging

LOG = logging.getLogger(__name__)


class StarCraftSceneGenerator:
    """Generates StarCraft battle scenes in Blender."""
    
    def __init__(self, config):
        self.config = config
        self.scene = bpy.context.scene
        
    def clear_scene(self):
        """Clear all objects from the scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        
        # Clear materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    
    def setup_scene(self, shot_config):
        """Set up the base scene for a shot."""
        self.clear_scene()
        
        # Set render settings
        self.scene.render.resolution_x = self.config.image_size[0]
        self.scene.render.resolution_y = self.config.image_size[1]
        self.scene.render.resolution_percentage = 100
        
        # Set up camera
        self._setup_camera()
        
        # Set up lighting
        self._setup_lighting()
        
        # Generate terrain
        self._generate_terrain(shot_config)
        
        # Generate units
        self._generate_units(shot_config)
        
        # Generate UI elements
        self._generate_ui(shot_config)
    
    def _setup_camera(self):
        """Set up the camera for the shot."""
        # Create camera
        bpy.ops.object.camera_add(location=(0, -10, 5))
        camera = bpy.context.object
        camera.name = "SCBW_Camera"
        
        # Point camera at origin
        camera.rotation_euler = (1.1, 0, 0)  # Look down at the battlefield
        
        # Set as active camera
        self.scene.camera = camera
    
    def _setup_lighting(self):
        """Set up basic lighting for the scene."""
        # Main light
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.object
        sun.name = "SCBW_Sun"
        sun.data.energy = 3.0
        
        # Fill light
        bpy.ops.object.light_add(type='AREA', location=(-3, -3, 8))
        fill = bpy.context.object
        fill.name = "SCBW_Fill"
        fill.data.energy = 1.0
        fill.data.size = 5.0
    
    def _generate_terrain(self, shot_config):
        """Generate terrain based on shot configuration."""
        # Create a simple plane for the battlefield
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        terrain = bpy.context.object
        terrain.name = "SCBW_Terrain"
        
        # Create material for terrain
        terrain_mat = bpy.data.materials.new(name="Terrain_Material")
        terrain_mat.use_nodes = True
        terrain.data.materials.append(terrain_mat)
        
        # Set up basic terrain shader
        nodes = terrain_mat.node_tree.nodes
        nodes.clear()
        
        # Add Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        
        # Add output
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        # Connect nodes
        terrain_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Set terrain color based on palette
        palette_colors = shot_config.get_palette_colors()
        if palette_colors:
            terrain_color = Color(palette_colors[0])
            bsdf.inputs['Base Color'].default_value = (*terrain_color, 1.0)
    
    def _generate_units(self, shot_config):
        """Generate unit clusters based on shot configuration."""
        # Left cluster
        if shot_config.left_cluster:
            self._create_unit_cluster(
                shot_config.left_cluster,
                shot_config.get_palette_colors(),
                "left"
            )
        
        # Right cluster
        if shot_config.right_cluster:
            self._create_unit_cluster(
                shot_config.right_cluster,
                shot_config.get_palette_colors(),
                "right"
            )
    
    def _create_unit_cluster(self, cluster_config, palette_colors, side):
        """Create a cluster of units."""
        rect = cluster_config.get("rect", [0.1, 0.5])
        count = cluster_config.get("count", 5)
        size = cluster_config.get("size", [16, 32])
        
        # Convert normalized coordinates to world space
        x_start = (rect[0] - 0.5) * 20  # Scale to world coordinates
        y_start = (rect[1] - 0.5) * 20
        
        unit_width = size[0] / 100.0  # Scale down
        unit_height = size[1] / 100.0
        
        for i in range(count):
            # Create a simple unit (cube for now)
            bpy.ops.mesh.primitive_cube_add(
                size=unit_width,
                location=(
                    x_start + (i % 3) * unit_width * 1.5,
                    y_start + (i // 3) * unit_height * 1.5,
                    unit_height / 2
                )
            )
            
            unit = bpy.context.object
            unit.name = f"SCBW_Unit_{side}_{i}"
            
            # Create material for unit
            unit_mat = bpy.data.materials.new(name=f"Unit_Material_{side}_{i}")
            unit_mat.use_nodes = True
            unit.data.materials.append(unit_mat)
            
            # Set up unit shader
            nodes = unit_mat.node_tree.nodes
            nodes.clear()
            
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            unit_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Set unit color from palette
            if palette_colors and len(palette_colors) > 1:
                unit_color = Color(palette_colors[1] if side == "left" else palette_colors[2])
                bsdf.inputs['Base Color'].default_value = (*unit_color, 1.0)
    
    def _generate_ui(self, shot_config):
        """Generate UI elements (HUD) for the shot."""
        if not shot_config.hud:
            return
        
        # Create UI plane
        bpy.ops.mesh.primitive_plane_add(size=2, location=(0, -9.5, 0))
        ui_plane = bpy.context.object
        ui_plane.name = "SCBW_UI"
        ui_plane.scale = (10, 1, 1)  # Make it wide and flat
        
        # Create UI material
        ui_mat = bpy.data.materials.new(name="UI_Material")
        ui_mat.use_nodes = True
        ui_plane.data.materials.append(ui_mat)
        
        # Set up UI shader (emission for HUD elements)
        nodes = ui_mat.node_tree.nodes
        nodes.clear()
        
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (0.1, 0.1, 0.1, 1.0)  # Dark UI background
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        ui_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
    def create_portal_effect(self, shot_config):
        """Create portal/wormhole effect if specified."""
        if not shot_config.portal:
            return
        
        portal_config = shot_config.portal
        center = portal_config.get("center", [0.5, 0.5])
        radius = portal_config.get("radius", 0.2)
        
        # Convert to world coordinates
        x_center = (center[0] - 0.5) * 20
        y_center = (center[1] - 0.5) * 20
        world_radius = radius * 20
        
        # Create portal sphere
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=world_radius,
            location=(x_center, y_center, 0)
        )
        
        portal = bpy.context.object
        portal.name = "SCBW_Portal"
        
        # Create portal material
        portal_mat = bpy.data.materials.new(name="Portal_Material")
        portal_mat.use_nodes = True
        portal.data.materials.append(portal_mat)
        
        # Set up portal shader
        nodes = portal_mat.node_tree.nodes
        nodes.clear()
        
        emission = nodes.new(type='ShaderNodeEmission')
        emission.location = (0, 0)
        emission.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0)  # Blue portal
        emission.inputs['Strength'].default_value = 2.0
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 0)
        
        portal_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])