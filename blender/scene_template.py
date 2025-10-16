"""Blender scene template for SCBW assets."""

import bpy
from pathlib import Path


def create_scene_template():
    """Create a basic Blender scene template for SCBW assets."""
    
    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Set up render settings
    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    
    # Set up camera
    bpy.ops.object.camera_add(location=(0, -10, 5))
    camera = bpy.context.object
    camera.name = "SCBW_Camera"
    camera.rotation_euler = (1.1, 0, 0)
    scene.camera = camera
    
    # Set up lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.object
    sun.name = "SCBW_Sun"
    sun.data.energy = 3.0
    
    # Create basic terrain
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    terrain = bpy.context.object
    terrain.name = "SCBW_Terrain"
    
    # Create terrain material
    terrain_mat = bpy.data.materials.new(name="Terrain_Material")
    terrain_mat.use_nodes = True
    terrain.data.materials.append(terrain_mat)
    
    # Set up basic terrain shader
    nodes = terrain_mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.2, 0.4, 0.2, 1.0)  # Green terrain
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    terrain_mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Set up compositor for multi-pass rendering
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    
    # Add render layers node
    render_layers = tree.nodes.new(type='CompositorNodeRLayers')
    render_layers.location = (0, 0)
    
    # Add output node
    output_node = tree.nodes.new(type='CompositorNodeOutputFile')
    output_node.location = (300, 0)
    output_node.base_path = str(Path.home() / "scbw_renders")
    output_node.file_slots[0].path = "test_render"
    output_node.format.file_format = 'PNG'
    output_node.format.color_mode = 'RGBA'
    
    tree.links.new(render_layers.outputs['Image'], output_node.inputs['Image'])
    
    print("SCBW scene template created successfully!")
    print("Camera, lighting, terrain, and compositor are set up.")
    print("You can now add units, UI elements, and other assets.")


if __name__ == "__main__":
    create_scene_template()