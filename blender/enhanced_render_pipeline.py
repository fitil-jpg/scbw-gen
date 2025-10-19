"""
Покращений рендер пайплайн для Blender
Підтримує Cycles та Eevee з розширеними налаштуваннями
"""

import bpy
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import json

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRenderPipeline:
    """Покращений рендер пайплайн для Blender"""
    
    def __init__(self, output_dir: str = "renders/blender"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.render_engines = {
            "CYCLES": self._setup_cycles,
            "BLENDER_EEVEE": self._setup_eevee
        }
    
    def setup_render_engine(self, engine: str, settings: Dict[str, Any]) -> None:
        """
        Налаштовує рендер двигун
        
        Args:
            engine: Назва двигуна (CYCLES або BLENDER_EEVEE)
            settings: Налаштування рендерингу
        """
        try:
            scene = bpy.context.scene
            scene.render.engine = engine
            
            if engine in self.render_engines:
                self.render_engines[engine](scene, settings)
            else:
                logger.warning(f"Невідомий рендер двигун: {engine}")
            
            logger.info(f"Рендер двигун налаштовано: {engine}")
            
        except Exception as e:
            logger.error(f"Помилка налаштування рендер двигуна: {e}")
            raise
    
    def _setup_cycles(self, scene: bpy.types.Scene, settings: Dict[str, Any]) -> None:
        """Налаштовує Cycles рендер двигун"""
        cycles = scene.cycles
        
        # Основні налаштування
        cycles.samples = settings.get("samples", 128)
        cycles.use_denoising = settings.get("denoising", True)
        cycles.denoiser = settings.get("denoiser", "OPTIX")
        
        # Налаштування якості
        cycles.max_bounces = settings.get("max_bounces", 12)
        cycles.diffuse_bounces = settings.get("diffuse_bounces", 4)
        cycles.glossy_bounces = settings.get("glossy_bounces", 4)
        cycles.transmission_bounces = settings.get("transmission_bounces", 12)
        cycles.volume_bounces = settings.get("volume_bounces", 0)
        
        # Налаштування освітлення
        cycles.caustics_reflective = settings.get("caustics_reflective", True)
        cycles.caustics_refractive = settings.get("caustics_refractive", True)
        
        # Налаштування пам'яті
        cycles.device = settings.get("device", "CPU")
        cycles.tile_size = settings.get("tile_size", 256)
        
        # Налаштування кольору
        scene.view_settings.view_transform = settings.get("view_transform", "Filmic")
        scene.view_settings.look = settings.get("look", "None")
        scene.view_settings.exposure = settings.get("exposure", 0.0)
        scene.view_settings.gamma = settings.get("gamma", 1.0)
    
    def _setup_eevee(self, scene: bpy.types.Scene, settings: Dict[str, Any]) -> None:
        """Налаштовує Eevee рендер двигун"""
        eevee = scene.eevee
        
        # Основні налаштування
        eevee.taa_render_samples = settings.get("taa_render_samples", 64)
        eevee.taa_samples = settings.get("taa_samples", 16)
        
        # Налаштування освітлення
        eevee.use_bloom = settings.get("use_bloom", True)
        eevee.bloom_threshold = settings.get("bloom_threshold", 0.8)
        eevee.bloom_knee = settings.get("bloom_knee", 0.5)
        eevee.bloom_radius = settings.get("bloom_radius", 6.5)
        eevee.bloom_intensity = settings.get("bloom_intensity", 0.05)
        
        eevee.use_ssr = settings.get("use_ssr", True)
        eevee.use_ssr_refraction = settings.get("use_ssr_refraction", True)
        eevee.ssr_quality = settings.get("ssr_quality", "HIGH")
        eevee.ssr_max_roughness = settings.get("ssr_max_roughness", 0.5)
        
        eevee.use_ssao = settings.get("use_ssao", True)
        eevee.ssao_quality = settings.get("ssao_quality", "HIGH")
        eevee.ssao_distance = settings.get("ssao_distance", 0.1)
        eevee.ssao_factor = settings.get("ssao_factor", 1.0)
        
        # Налаштування тіней
        eevee.shadow_cascade_size = settings.get("shadow_cascade_size", "1024")
        eevee.shadow_cascade_count = settings.get("shadow_cascade_count", 4)
        eevee.use_soft_shadows = settings.get("use_soft_shadows", True)
        
        # Налаштування кольору
        scene.view_settings.view_transform = settings.get("view_transform", "Filmic")
        scene.view_settings.look = settings.get("look", "None")
        scene.view_settings.exposure = settings.get("exposure", 0.0)
        scene.view_settings.gamma = settings.get("gamma", 1.0)
    
    def setup_render_settings(self, settings: Dict[str, Any]) -> None:
        """Налаштовує загальні налаштування рендерингу"""
        try:
            scene = bpy.context.scene
            
            # Роздільність
            resolution = settings.get("resolution", [1920, 1080])
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]
            scene.render.resolution_percentage = settings.get("resolution_percentage", 100)
            
            # Формат виводу
            output_format = settings.get("output_format", "PNG")
            if output_format == "PNG":
                scene.render.image_settings.file_format = "PNG"
                scene.render.image_settings.color_mode = "RGBA"
                scene.render.image_settings.color_depth = "16"
            elif output_format == "JPEG":
                scene.render.image_settings.file_format = "JPEG"
                scene.render.image_settings.color_mode = "RGB"
                scene.render.image_settings.quality = settings.get("jpeg_quality", 90)
            elif output_format == "EXR":
                scene.render.image_settings.file_format = "OPEN_EXR"
                scene.render.image_settings.color_mode = "RGBA"
                scene.render.image_settings.color_depth = "32"
                scene.render.image_settings.exr_codec = "ZIP"
            
            # Налаштування кадрів
            scene.frame_start = settings.get("frame_start", 1)
            scene.frame_end = settings.get("frame_end", 1)
            scene.frame_current = settings.get("frame_current", 1)
            
            # Налаштування виводу
            scene.render.filepath = str(self.output_dir / settings.get("filename", "render"))
            
            # Налаштування композиту
            scene.use_nodes = settings.get("use_compositor", True)
            
            logger.info("Налаштування рендерингу встановлено")
            
        except Exception as e:
            logger.error(f"Помилка налаштування рендерингу: {e}")
            raise
    
    def create_render_passes(self, shot_id: str, passes_config: List[Dict[str, Any]]) -> None:
        """
        Створює рендер паси
        
        Args:
            shot_id: Ідентифікатор шоту
            passes_config: Конфігурація пасів
        """
        try:
            scene = bpy.context.scene
            
            # Включення композитора
            scene.use_nodes = True
            tree = scene.node_tree
            
            # Очищення існуючих вузлів
            for node in tree.nodes:
                tree.nodes.remove(node)
            
            # Створення основних вузлів
            render_layers = tree.nodes.new("CompositorNodeRLayers")
            output = tree.nodes.new("CompositorNodeOutputFile")
            output.base_path = str(self.output_dir / shot_id)
            
            # З'єднання вузлів
            tree.links.new(render_layers.outputs["Image"], output.inputs["Image"])
            
            # Створення додаткових пасів
            for pass_config in passes_config:
                self._create_render_pass(tree, render_layers, output, pass_config)
            
            logger.info(f"Рендер паси створено для шоту: {shot_id}")
            
        except Exception as e:
            logger.error(f"Помилка створення рендер пасів: {e}")
            raise
    
    def _create_render_pass(self, tree, render_layers, output, pass_config: Dict[str, Any]) -> None:
        """Створює окремий рендер пас"""
        pass_type = pass_config.get("type", "beauty")
        pass_name = pass_config.get("name", pass_type)
        
        if pass_type == "depth":
            # Пас глибини
            depth_output = tree.nodes.new("CompositorNodeOutputFile")
            depth_output.base_path = str(self.output_dir / "depth")
            depth_output.file_slots[0].path = f"{pass_name}_"
            tree.links.new(render_layers.outputs["Depth"], depth_output.inputs["Image"])
        
        elif pass_type == "normal":
            # Пас нормалей
            normal_output = tree.nodes.new("CompositorNodeOutputFile")
            normal_output.base_path = str(self.output_dir / "normal")
            normal_output.file_slots[0].path = f"{pass_name}_"
            tree.links.new(render_layers.outputs["Normal"], normal_output.inputs["Image"])
        
        elif pass_type == "diffuse":
            # Пас дифузного освітлення
            diffuse_output = tree.nodes.new("CompositorNodeOutputFile")
            diffuse_output.base_path = str(self.output_dir / "diffuse")
            diffuse_output.file_slots[0].path = f"{pass_name}_"
            tree.links.new(render_layers.outputs["Diffuse"], diffuse_output.inputs["Image"])
        
        elif pass_type == "glossy":
            # Пас дзеркального освітлення
            glossy_output = tree.nodes.new("CompositorNodeOutputFile")
            glossy_output.base_path = str(self.output_dir / "glossy")
            glossy_output.file_slots[0].path = f"{pass_name}_"
            tree.links.new(render_layers.outputs["Glossy"], glossy_output.inputs["Image"])
    
    def render_shot(self, shot_id: str, frame: int = 1) -> Path:
        """
        Рендерить кадр шоту
        
        Args:
            shot_id: Ідентифікатор шоту
            frame: Номер кадру
        
        Returns:
            Шлях до зрендереного зображення
        """
        try:
            scene = bpy.context.scene
            
            # Встановлення кадру
            scene.frame_set(frame)
            
            # Налаштування виводу
            output_path = self.output_dir / shot_id / f"frame_{frame:04d}"
            scene.render.filepath = str(output_path)
            
            # Рендеринг
            bpy.ops.render.render(write_still=True)
            
            # Отримання шляху до файлу
            rendered_file = Path(scene.render.filepath + scene.render.file_extension)
            
            logger.info(f"Кадр зрендерено: {rendered_file}")
            return rendered_file
            
        except Exception as e:
            logger.error(f"Помилка рендерингу кадру: {e}")
            raise
    
    def render_animation(self, shot_id: str, start_frame: int = 1, end_frame: int = 1) -> List[Path]:
        """
        Рендерить анімацію шоту
        
        Args:
            shot_id: Ідентифікатор шоту
            start_frame: Початковий кадр
            end_frame: Кінцевий кадр
        
        Returns:
            Список шляхів до зрендерених кадрів
        """
        try:
            scene = bpy.context.scene
            
            # Налаштування діапазону кадрів
            scene.frame_start = start_frame
            scene.frame_end = end_frame
            
            # Налаштування виводу
            output_path = self.output_dir / shot_id / "animation"
            scene.render.filepath = str(output_path)
            
            # Рендеринг анімації
            bpy.ops.render.render(animation=True)
            
            # Отримання списку файлів
            rendered_files = []
            for frame in range(start_frame, end_frame + 1):
                frame_file = Path(f"{output_path}{frame:04d}{scene.render.file_extension}")
                if frame_file.exists():
                    rendered_files.append(frame_file)
            
            logger.info(f"Анімація зрендерена: {len(rendered_files)} кадрів")
            return rendered_files
            
        except Exception as e:
            logger.error(f"Помилка рендерингу анімації: {e}")
            raise
    
    def create_render_manifest(self, rendered_files: List[Path], shot_id: str) -> Dict[str, Any]:
        """
        Створює маніфест рендерингу
        
        Args:
            rendered_files: Список зрендерених файлів
            shot_id: Ідентифікатор шоту
        
        Returns:
            Маніфест рендерингу
        """
        try:
            manifest = {
                "shot_id": shot_id,
                "render_timestamp": bpy.context.scene.frame_current,
                "render_engine": bpy.context.scene.render.engine,
                "resolution": [
                    bpy.context.scene.render.resolution_x,
                    bpy.context.scene.render.resolution_y
                ],
                "output_format": bpy.context.scene.render.image_settings.file_format,
                "files": [str(f) for f in rendered_files],
                "file_count": len(rendered_files)
            }
            
            # Збереження маніфесту
            manifest_path = self.output_dir / shot_id / "render_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Маніфест рендерингу створено: {manifest_path}")
            return manifest
            
        except Exception as e:
            logger.error(f"Помилка створення маніфесту: {e}")
            raise
    
    def batch_render(self, shots_config: List[Dict[str, Any]]) -> Dict[str, List[Path]]:
        """
        Рендерить кілька шотів пакетно
        
        Args:
            shots_config: Список конфігурацій шотів
        
        Returns:
            Словник з результатами рендерингу
        """
        try:
            results = {}
            
            for shot_config in shots_config:
                shot_id = shot_config.get("shot_id", "unknown")
                logger.info(f"Рендеринг шоту: {shot_id}")
                
                # Налаштування рендерингу для шоту
                render_settings = shot_config.get("render_settings", {})
                self.setup_render_engine(
                    render_settings.get("engine", "CYCLES"),
                    render_settings
                )
                self.setup_render_settings(render_settings)
                
                # Рендеринг
                if shot_config.get("is_animation", False):
                    rendered_files = self.render_animation(
                        shot_id,
                        shot_config.get("start_frame", 1),
                        shot_config.get("end_frame", 1)
                    )
                else:
                    rendered_files = [self.render_shot(shot_id, shot_config.get("frame", 1))]
                
                results[shot_id] = rendered_files
                
                # Створення маніфесту
                self.create_render_manifest(rendered_files, shot_id)
            
            logger.info(f"Пакетний рендеринг завершено: {len(results)} шотів")
            return results
            
        except Exception as e:
            logger.error(f"Помилка пакетного рендерингу: {e}")
            raise

# Приклад використання
if __name__ == "__main__":
    # Ініціалізація пайплайну
    pipeline = EnhancedRenderPipeline("renders/blender")
    
    # Налаштування рендерингу
    render_settings = {
        "engine": "CYCLES",
        "samples": 128,
        "resolution": [1920, 1080],
        "output_format": "PNG",
        "denoising": True
    }
    
    # Налаштування пайплайну
    pipeline.setup_render_engine("CYCLES", render_settings)
    pipeline.setup_render_settings(render_settings)
    
    # Рендеринг
    rendered_file = pipeline.render_shot("test_shot", 1)
    print(f"Рендеринг завершено: {rendered_file}")
