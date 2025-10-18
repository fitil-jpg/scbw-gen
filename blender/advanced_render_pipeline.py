"""Розширений пайплайн рендерингу для Blender SCBW pipeline."""

from __future__ import annotations

import bpy
import bpy_extras
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import mathutils
from mathutils import Vector, Color

LOG = logging.getLogger(__name__)


class AdvancedRenderPass:
    """Розширений клас для рендер пасів з додатковими налаштуваннями."""
    
    def __init__(self, name: str, output_path: Path, **kwargs):
        self.name = name
        self.output_path = output_path
        self.settings = kwargs
        self.compositor_nodes = []
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує параметри рендерингу для пасу."""
        pass
    
    def setup_compositor(self, scene: bpy.types.Scene, tree: bpy.types.CompositorNodeTree):
        """Налаштовує композитор для пасу."""
        pass


class BeautyPass(AdvancedRenderPass):
    """Красивий пас з повним освітленням та матеріалами."""
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для красивого рендерингу."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 512
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPTIX' if bpy.app.version >= (3, 0, 0) else 'NLM'
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        
        # Налаштування для якості
        scene.cycles.max_bounces = 12
        scene.cycles.diffuse_bounces = 4
        scene.cycles.glossy_bounces = 4
        scene.cycles.transmission_bounces = 4
        scene.cycles.volume_bounces = 2
        
        # Налаштування зображення
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 0  # Без стиснення
        
        # Налаштування камери
        if scene.camera:
            scene.camera.data.lens = 50
            scene.camera.data.sensor_width = 32


class MaskPass(AdvancedRenderPass):
    """Пас масок для об'єктів."""
    
    def __init__(self, name: str, output_path: Path, object_names: List[str], color: Tuple[float, float, float] = (1.0, 1.0, 1.0)):
        super().__init__(name, output_path)
        self.object_names = object_names
        self.color = color
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для рендерингу масок."""
        # Приховуємо всі об'єкти крім потрібних
        for obj in scene.objects:
            if obj.name in self.object_names:
                obj.hide_render = False
            else:
                obj.hide_render = True
        
        # Налаштування рендерингу
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 1  # Швидкий рендеринг для масок
        
        # Створення білого матеріалу для масок
        mask_mat = bpy.data.materials.new(name="Advanced_Mask_Material")
        mask_mat.use_nodes = True
        mask_mat.node_tree.nodes.clear()
        
        emission = mask_mat.node_tree.nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = (*self.color, 1.0)
        emission.inputs['Strength'].default_value = 1.0
        
        output = mask_mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        mask_mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Застосування матеріалу до об'єктів маски
        for obj_name in self.object_names:
            obj = scene.objects.get(obj_name)
            if obj:
                obj.data.materials.clear()
                obj.data.materials.append(mask_mat)


class DepthPass(AdvancedRenderPass):
    """Пас глибини з налаштуваннями."""
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для рендерингу глибини."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 64
        
        # Включаємо пас глибини
        scene.view_layers[0].use_pass_z = True
        
        # Налаштування зображення для EXR
        scene.render.image_settings.file_format = 'OPEN_EXR'
        scene.render.image_settings.color_mode = 'BW'
        scene.render.image_settings.color_depth = '32'
        scene.render.image_settings.exr_codec = 'ZIP'
    
    def setup_compositor(self, scene: bpy.types.Scene, tree: bpy.types.CompositorNodeTree):
        """Налаштовує композитор для глибини."""
        if not scene.use_nodes:
            scene.use_nodes = True
        
        # Очищаємо дерево
        tree.nodes.clear()
        
        # Render Layers
        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)
        
        # Normalize для глибини
        normalize = tree.nodes.new(type='CompositorNodeNormalize')
        normalize.location = (200, 0)
        
        # Invert для правильного відображення глибини
        invert = tree.nodes.new(type='CompositorNodeInvert')
        invert.location = (400, 0)
        
        # Output
        output = tree.nodes.new(type='CompositorNodeOutputFile')
        output.location = (600, 0)
        output.base_path = str(self.output_path.parent)
        output.file_slots[0].path = self.output_path.stem
        output.format.file_format = 'OPEN_EXR'
        output.format.color_mode = 'BW'
        output.format.color_depth = '32'
        
        # З'єднання
        tree.links.new(render_layers.outputs['Depth'], normalize.inputs['Value'])
        tree.links.new(normalize.outputs['Value'], invert.inputs['Color'])
        tree.links.new(invert.outputs['Color'], output.inputs['Image'])


class NormalPass(AdvancedRenderPass):
    """Пас нормалей."""
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для рендерингу нормалей."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        
        # Включаємо пас нормалей
        scene.view_layers[0].use_pass_normal = True
        
        # Налаштування зображення
        scene.render.image_settings.file_format = 'OPEN_EXR'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'


class AmbientOcclusionPass(AdvancedRenderPass):
    """Пас ambient occlusion."""
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для рендерингу AO."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 256
        
        # Включаємо пас AO
        scene.view_layers[0].use_pass_ambient_occlusion = True


class EmissionPass(AdvancedRenderPass):
    """Пас емісії для світлових ефектів."""
    
    def setup_render_settings(self, scene: bpy.types.Scene):
        """Налаштовує для рендерингу емісії."""
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 128
        
        # Включаємо пас емісії
        scene.view_layers[0].use_pass_emit = True


class AdvancedMultiPassRenderer:
    """Розширений мульти-пас рендерер."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Стандартні паси
        self.default_passes = [
            'beauty', 'mask_units', 'mask_buildings', 'mask_terrain',
            'depth', 'normal', 'ao', 'emission'
        ]
    
    def create_advanced_passes(self, shot_id: str, frame: int = 1, 
                             custom_passes: Optional[List[str]] = None) -> List[AdvancedRenderPass]:
        """Створює розширені рендер паси."""
        passes = []
        passes_to_create = custom_passes or self.default_passes
        
        for pass_name in passes_to_create:
            if pass_name == 'beauty':
                beauty_path = self.output_directory / f"{shot_id}_beauty_{frame:04d}.png"
                passes.append(BeautyPass("beauty", beauty_path))
            
            elif pass_name == 'mask_units':
                mask_path = self.output_directory / f"{shot_id}_mask_units_{frame:04d}.png"
                unit_objects = [obj.name for obj in bpy.context.scene.objects 
                               if obj.name.startswith("SCBW_Unit_")]
                passes.append(MaskPass("mask_units", mask_path, unit_objects, (1.0, 1.0, 1.0)))
            
            elif pass_name == 'mask_buildings':
                mask_path = self.output_directory / f"{shot_id}_mask_buildings_{frame:04d}.png"
                building_objects = [obj.name for obj in bpy.context.scene.objects 
                                   if obj.name.startswith("SCBW_Building_")]
                passes.append(MaskPass("mask_buildings", mask_path, building_objects, (0.8, 0.8, 0.8)))
            
            elif pass_name == 'mask_terrain':
                mask_path = self.output_directory / f"{shot_id}_mask_terrain_{frame:04d}.png"
                terrain_objects = [obj.name for obj in bpy.context.scene.objects 
                                  if obj.name.startswith("SCBW_Terrain") or obj.name.startswith("SCBW_Advanced_Terrain")]
                passes.append(MaskPass("mask_terrain", mask_path, terrain_objects, (0.6, 0.6, 0.6)))
            
            elif pass_name == 'depth':
                depth_path = self.output_directory / f"{shot_id}_depth_{frame:04d}.exr"
                passes.append(DepthPass("depth", depth_path))
            
            elif pass_name == 'normal':
                normal_path = self.output_directory / f"{shot_id}_normal_{frame:04d}.exr"
                passes.append(NormalPass("normal", normal_path))
            
            elif pass_name == 'ao':
                ao_path = self.output_directory / f"{shot_id}_ao_{frame:04d}.exr"
                passes.append(AmbientOcclusionPass("ao", ao_path))
            
            elif pass_name == 'emission':
                emission_path = self.output_directory / f"{shot_id}_emission_{frame:04d}.exr"
                passes.append(EmissionPass("emission", emission_path))
        
        return passes
    
    def render_advanced_passes(self, shot_id: str, frame: int = 1, 
                              custom_passes: Optional[List[str]] = None) -> Dict[str, Path]:
        """Рендерить розширені паси."""
        passes = self.create_advanced_passes(shot_id, frame, custom_passes)
        rendered_paths = {}
        
        for pass_obj in passes:
            LOG.info(f"Рендеринг пасу: {pass_obj.name}")
            
            # Налаштування рендерингу
            pass_obj.setup_render_settings(bpy.context.scene)
            
            # Налаштування композитора
            if hasattr(pass_obj, 'setup_compositor'):
                if not bpy.context.scene.use_nodes:
                    bpy.context.scene.use_nodes = True
                pass_obj.setup_compositor(bpy.context.scene, bpy.context.scene.node_tree)
            
            # Встановлення шляху виводу
            bpy.context.scene.render.filepath = str(pass_obj.output_path.parent / pass_obj.output_path.stem)
            
            # Рендеринг
            bpy.ops.render.render(write_still=True)
            
            rendered_paths[pass_obj.name] = pass_obj.output_path
        
        return rendered_paths
    
    def setup_advanced_compositor(self, shot_id: str, frame: int = 1):
        """Налаштовує розширений композитор для мульти-площинного EXR."""
        scene = bpy.context.scene
        
        if not scene.use_nodes:
            scene.use_nodes = True
        
        tree = scene.node_tree
        tree.nodes.clear()
        
        # Render Layers
        render_layers = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers.location = (0, 0)
        
        # Output для мульти-площинного EXR
        output = tree.nodes.new(type='CompositorNodeOutputFile')
        output.location = (400, 0)
        output.base_path = str(self.output_directory)
        output.file_slots[0].path = f"{shot_id}_multi_{frame:04d}"
        output.format.file_format = 'OPEN_EXR'
        output.format.color_mode = 'RGBA'
        output.format.color_depth = '16'
        output.format.exr_codec = 'ZIP'
        
        # З'єднання основних пасів
        tree.links.new(render_layers.outputs['Image'], output.inputs['Image'])
        
        # Додавання додаткових пасів як окремі слоти
        if 'Depth' in render_layers.outputs:
            depth_output = tree.nodes.new(type='CompositorNodeOutputFile')
            depth_output.location = (400, -200)
            depth_output.base_path = str(self.output_directory)
            depth_output.file_slots[0].path = f"{shot_id}_depth_{frame:04d}"
            depth_output.format.file_format = 'OPEN_EXR'
            depth_output.format.color_mode = 'BW'
            depth_output.format.color_depth = '32'
            tree.links.new(render_layers.outputs['Depth'], depth_output.inputs['Image'])
        
        if 'Normal' in render_layers.outputs:
            normal_output = tree.nodes.new(type='CompositorNodeOutputFile')
            normal_output.location = (400, -400)
            normal_output.base_path = str(self.output_directory)
            normal_output.file_slots[0].path = f"{shot_id}_normal_{frame:04d}"
            normal_output.format.file_format = 'OPEN_EXR'
            normal_output.format.color_mode = 'RGBA'
            normal_output.format.color_depth = '16'
            tree.links.new(render_layers.outputs['Normal'], normal_output.inputs['Image'])
        
        if 'AO' in render_layers.outputs:
            ao_output = tree.nodes.new(type='CompositorNodeOutputFile')
            ao_output.location = (400, -600)
            ao_output.base_path = str(self.output_directory)
            ao_output.file_slots[0].path = f"{shot_id}_ao_{frame:04d}"
            ao_output.format.file_format = 'OPEN_EXR'
            ao_output.format.color_mode = 'BW'
            ao_output.format.color_depth = '16'
            tree.links.new(render_layers.outputs['AO'], ao_output.inputs['Image'])
        
        if 'Emit' in render_layers.outputs:
            emit_output = tree.nodes.new(type='CompositorNodeOutputFile')
            emit_output.location = (400, -800)
            emit_output.base_path = str(self.output_directory)
            emit_output.file_slots[0].path = f"{shot_id}_emission_{frame:04d}"
            emit_output.format.file_format = 'OPEN_EXR'
            emit_output.format.color_mode = 'RGBA'
            emit_output.format.color_depth = '16'
            tree.links.new(render_layers.outputs['Emit'], emit_output.inputs['Image'])


class EeveeRenderer:
    """Спеціалізований рендерер для Eevee."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
    
    def setup_eevee_settings(self, scene: bpy.types.Scene):
        """Налаштовує Eevee для оптимального рендерингу."""
        scene.render.engine = 'BLENDER_EEVEE'
        
        # Налаштування якості
        scene.eevee.taa_render_samples = 64
        scene.eevee.use_bloom = True
        scene.eevee.bloom_threshold = 1.0
        scene.eevee.bloom_knee = 0.5
        scene.eevee.bloom_radius = 6.5
        scene.eevee.bloom_intensity = 0.05
        scene.eevee.bloom_clamp = 0.0
        
        # Screen Space Reflections
        scene.eevee.use_ssr = True
        scene.eevee.use_ssr_refraction = True
        scene.eevee.ssr_quality = 'HIGH'
        scene.eevee.ssr_max_roughness = 0.5
        scene.eevee.ssr_thickness = 0.2
        scene.eevee.ssr_border_fade = 0.075
        scene.eevee.ssr_firefly_fac = 10.0
        
        # Shadows
        scene.eevee.use_soft_shadows = True
        scene.eevee.shadow_cascade_size = '1024'
        scene.eevee.shadow_cascade_count = '4'
        scene.eevee.shadow_high_bitdepth = True
        
        # Ambient Occlusion
        scene.eevee.use_gtao = True
        scene.eevee.gtao_distance = 0.2
        scene.eevee.gtao_factor = 1.0
        scene.eevee.gtao_quality = 'HIGH'
        
        # Subsurface Scattering
        scene.eevee.use_sss = True
        scene.eevee.sss_samples = 7
        scene.eevee.sss_jitter_threshold = 0.3
        
        # Volumetrics
        scene.eevee.use_volumetric_lights = True
        scene.eevee.volumetric_tile_size = '2'
        scene.eevee.volumetric_samples = 64
        scene.eevee.volumetric_start = 0.0
        scene.eevee.volumetric_end = 100.0
        scene.eevee.volumetric_tile_size = '2'
        
        # Motion Blur
        scene.eevee.use_motion_blur = True
        scene.eevee.motion_blur_shutter = 0.5
        scene.eevee.motion_blur_depth_scale = 1.0
        scene.eevee.motion_blur_max = 32
        scene.eevee.motion_blur_steps = 1
    
    def render_eevee_passes(self, shot_id: str, frame: int = 1) -> Dict[str, Path]:
        """Рендерить паси через Eevee."""
        self.setup_eevee_settings(bpy.context.scene)
        
        # Базовий рендерер для пасів
        renderer = AdvancedMultiPassRenderer(self.output_directory)
        
        # Рендеринг основних пасів
        passes = ['beauty', 'mask_units', 'mask_buildings', 'depth']
        return renderer.render_advanced_passes(shot_id, frame, passes)


class CyclesRenderer:
    """Спеціалізований рендерер для Cycles."""
    
    def __init__(self, output_directory: Path):
        self.output_directory = output_directory
    
    def setup_cycles_settings(self, scene: bpy.types.Scene, quality: str = 'high'):
        """Налаштовує Cycles для різних рівнів якості."""
        scene.render.engine = 'CYCLES'
        
        quality_settings = {
            'low': {
                'samples': 64,
                'max_bounces': 4,
                'diffuse_bounces': 2,
                'glossy_bounces': 2,
                'transmission_bounces': 2,
                'volume_bounces': 1
            },
            'medium': {
                'samples': 256,
                'max_bounces': 8,
                'diffuse_bounces': 3,
                'glossy_bounces': 3,
                'transmission_bounces': 3,
                'volume_bounces': 2
            },
            'high': {
                'samples': 512,
                'max_bounces': 12,
                'diffuse_bounces': 4,
                'glossy_bounces': 4,
                'transmission_bounces': 4,
                'volume_bounces': 2
            },
            'ultra': {
                'samples': 1024,
                'max_bounces': 16,
                'diffuse_bounces': 5,
                'glossy_bounces': 5,
                'transmission_bounces': 5,
                'volume_bounces': 3
            }
        }
        
        settings = quality_settings.get(quality, quality_settings['high'])
        
        scene.cycles.samples = settings['samples']
        scene.cycles.max_bounces = settings['max_bounces']
        scene.cycles.diffuse_bounces = settings['diffuse_bounces']
        scene.cycles.glossy_bounces = settings['glossy_bounces']
        scene.cycles.transmission_bounces = settings['transmission_bounces']
        scene.cycles.volume_bounces = settings['volume_bounces']
        
        # Додаткові налаштування
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = 'OPTIX' if bpy.app.version >= (3, 0, 0) else 'NLM'
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.01
        scene.cycles.adaptive_min_samples = 0
    
    def render_cycles_passes(self, shot_id: str, frame: int = 1, 
                           quality: str = 'high') -> Dict[str, Path]:
        """Рендерить паси через Cycles."""
        self.setup_cycles_settings(bpy.context.scene, quality)
        
        # Розширений рендерер для пасів
        renderer = AdvancedMultiPassRenderer(self.output_directory)
        
        # Рендеринг всіх пасів
        passes = ['beauty', 'mask_units', 'mask_buildings', 'mask_terrain', 
                 'depth', 'normal', 'ao', 'emission']
        return renderer.render_advanced_passes(shot_id, frame, passes)


def create_render_manifest(rendered_paths: Dict[str, Path], shot_id: str) -> Dict[str, Any]:
    """Створює маніфест рендерингу."""
    manifest = {
        'shot_id': shot_id,
        'render_time': bpy.context.scene.frame_current,
        'engine': bpy.context.scene.render.engine,
        'resolution': [
            bpy.context.scene.render.resolution_x,
            bpy.context.scene.render.resolution_y
        ],
        'passes': {}
    }
    
    for pass_name, path in rendered_paths.items():
        manifest['passes'][pass_name] = {
            'path': str(path),
            'format': path.suffix[1:].upper(),
            'size_bytes': path.stat().st_size if path.exists() else 0
        }
    
    return manifest


if __name__ == "__main__":
    # Тестування рендер пайплайну
    logging.basicConfig(level=logging.INFO)
    
    output_dir = Path("test_renders")
    output_dir.mkdir(exist_ok=True)
    
    # Тестування Eevee
    print("Тестування Eevee рендерера...")
    eevee_renderer = EeveeRenderer(output_dir)
    # eevee_paths = eevee_renderer.render_eevee_passes("test_shot", 1)
    
    # Тестування Cycles
    print("Тестування Cycles рендерера...")
    cycles_renderer = CyclesRenderer(output_dir)
    # cycles_paths = cycles_renderer.render_cycles_passes("test_shot", 1, "high")
    
    print("Рендер пайплайн готовий до використання!")