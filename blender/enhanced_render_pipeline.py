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
    
    # ============================
    # Внутрішні утиліти керування
    # ============================
    def _configure_compute_device(self, scene: bpy.types.Scene, settings: Dict[str, Any]) -> None:
        """Налаштування обчислювального пристрою (CPU/GPU) та бекенду (OPTIX/CUDA/HIP/METAL/ONEAPI).

        Очікувані ключі у settings:
        - device: "CPU" | "GPU" | "AUTO" (default: AUTO)
        - device_backend: "OPTIX" | "CUDA" | "HIP" | "METAL" | "ONEAPI" (optional)
        - enabled_devices: Optional[List[str]] (імена GPU, які треба ввімкнути)
        """
        device_mode = (settings.get("device", "AUTO") or "AUTO").upper()
        requested_backend = settings.get("device_backend")
        enabled_devices = settings.get("enabled_devices") or []

        try:
            # Якщо явно CPU, встановлюємо CPU і виходимо
            if device_mode == "CPU":
                scene.cycles.device = "CPU"
                # Для деяких версій Cycles потрібно вимкнути GPU бекенд
                prefs = bpy.context.preferences
                if "cycles" in prefs.addons:
                    cprefs = prefs.addons["cycles"].preferences
                    # NONE/CPU вимикає GPU бекенд у різних версіях Blender
                    if hasattr(cprefs, "compute_device_type"):
                        try:
                            cprefs.compute_device_type = "NONE"
                        except Exception:
                            pass
                return

            # В іншому випадку намагаємось налаштувати GPU
            scene.cycles.device = "GPU"

            prefs = bpy.context.preferences
            if "cycles" not in prefs.addons:
                # Якщо аддон недоступний (малоймовірно), відкат на CPU
                scene.cycles.device = "CPU"
                return

            cprefs = prefs.addons["cycles"].preferences

            # Послідовність пріоритетів бекендів, якщо не задано явно
            backend_priority: List[str] = [
                "OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"
            ]
            if requested_backend:
                backend_priority = [requested_backend.upper()] + [b for b in backend_priority if b != requested_backend.upper()]

            # Спроба активувати перший доступний бекенд
            selected_backend: Optional[str] = None
            for backend in backend_priority:
                try:
                    if hasattr(cprefs, "compute_device_type"):
                        cprefs.compute_device_type = backend
                    # Оновити список пристроїв
                    if hasattr(cprefs, "get_devices"):
                        try:
                            cprefs.get_devices()
                        except Exception:
                            pass

                    devices_attr = getattr(cprefs, "devices", None)
                    if not devices_attr:
                        continue

                    # cprefs.devices може бути плоским списком або списком списків
                    def iter_devices(devs):
                        for d in devs:
                            if isinstance(d, (list, tuple)):
                                for sd in d:
                                    yield sd
                            else:
                                yield d

                    found_any = False
                    for d in iter_devices(devices_attr):
                        # d має поля: name, type, use
                        is_gpu = getattr(d, "type", "").upper() != "CPU"
                        if is_gpu and (not enabled_devices or getattr(d, "name", "") in enabled_devices):
                            if hasattr(d, "use"):
                                d.use = True
                            found_any = True
                        else:
                            if hasattr(d, "use"):
                                d.use = False

                    if found_any:
                        selected_backend = backend
                        break
                except Exception:
                    # Пробуємо наступний бекенд
                    continue

            if not selected_backend:
                # Відкат до CPU, якщо GPU недоступний
                scene.cycles.device = "CPU"
        except Exception as e:
            logger.warning(f"Не вдалося налаштувати GPU, використовую CPU: {e}")
            try:
                scene.cycles.device = "CPU"
            except Exception:
                pass

    def _apply_simplify_settings(self, scene: bpy.types.Scene, settings: Dict[str, Any]) -> None:
        """Застосовує налаштування спрощення сцени (LOD через Simplify)."""
        simplify = settings.get("simplify") or {}
        use_simplify = simplify.get("use_simplify", False) or settings.get("use_simplify", False)
        if not use_simplify:
            return

        try:
            scene.render.use_simplify = True
            # Параметри можуть відрізнятись між версіями Blender – перевіряємо наявність
            mapping: Dict[str, Any] = {
                "simplify_subdivision": simplify.get("subdivision", 1.0),
                "simplify_subdivision_render": simplify.get("subdivision_render", 1.0),
                "simplify_child_particles": simplify.get("child_particles", 1.0),
                "simplify_gpencil": simplify.get("gpencil", 1.0),
                "simplify_texture_limit": simplify.get("texture_limit", 0),  # 0 = без ліміту
                "simplify_volumes": simplify.get("volumes", 1.0),
            }
            for attr, value in mapping.items():
                if hasattr(scene.render, attr):
                    setattr(scene.render, attr, value)
        except Exception as e:
            logger.warning(f"Не вдалося застосувати Simplify налаштування: {e}")

    def _apply_tile_settings(self, scene: bpy.types.Scene, cycles: bpy.types.Cycles, settings: Dict[str, Any]) -> None:
        """Застосовує налаштування тайлів для рендеру, якщо доступно в поточній версії Blender."""
        tile_size = settings.get("tile_size")
        tile_x = settings.get("tile_x")
        tile_y = settings.get("tile_y")
        if tile_size is None and tile_x is None and tile_y is None:
            return

        try:
            # Cycles X (Blender 3.x+) може ігнорувати тайли; намагаємось коректно поставити якщо атрибути існують
            if hasattr(cycles, "tile_size") and isinstance(tile_size, int):
                try:
                    cycles.tile_size = tile_size
                    return
                except Exception:
                    pass
            # Старіші API
            if hasattr(scene.render, "tile_x") and hasattr(scene.render, "tile_y"):
                if isinstance(tile_size, int):
                    scene.render.tile_x = tile_size
                    scene.render.tile_y = tile_size
                else:
                    if isinstance(tile_x, int):
                        scene.render.tile_x = tile_x
                    if isinstance(tile_y, int):
                        scene.render.tile_y = tile_y
        except Exception as e:
            logger.warning(f"Неможливо застосувати тайли: {e}")
    
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
        
        # Пристрій обчислень та бекенд
        self._configure_compute_device(scene, settings)

        # Основні налаштування
        cycles.samples = int(settings.get("samples", 128))

        # Адаптивне семплювання
        if settings.get("use_adaptive_sampling", settings.get("adaptive_sampling", False)):
            try:
                cycles.use_adaptive_sampling = True
                if "adaptive_threshold" in settings:
                    cycles.adaptive_threshold = float(settings.get("adaptive_threshold", 0.01))
                if "adaptive_min_samples" in settings:
                    cycles.adaptive_min_samples = int(settings.get("adaptive_min_samples", 0))
            except Exception as e:
                logger.warning(f"Адаптивне семплювання недоступне: {e}")

        # Денойзинг (ререндер/фінальний)
        denoise_enabled = settings.get("denoising", settings.get("denoise", True))
        denoiser_name = (settings.get("denoiser", "OPTIX") or "OPTIX").upper()
        try:
            # Налаштування денойзера Cycles
            if hasattr(cycles, "denoiser"):
                # 'OPTIX' | 'OPENIMAGEDENOISE' | 'NLM'
                valid_map = {
                    "OPTIX": "OPTIX",
                    "OIDN": "OPENIMAGEDENOISE",
                    "OPENIMAGEDENOISE": "OPENIMAGEDENOISE",
                    "NLM": "NLM",
                }
                cycles.denoiser = valid_map.get(denoiser_name, cycles.denoiser)
            # Вмикаємо денойзинг на рівні View Layer, якщо атрибут існує
            if hasattr(bpy.context.view_layer, "cycles") and hasattr(bpy.context.view_layer.cycles, "use_denoising"):
                bpy.context.view_layer.cycles.use_denoising = bool(denoise_enabled)
            elif hasattr(cycles, "use_denoising"):
                cycles.use_denoising = bool(denoise_enabled)
            # Вхідні паси для кращого денойзингу (OIDN)
            if hasattr(cycles, "denoising_input_passes"):
                cycles.denoising_input_passes = settings.get("denoising_input_passes", "RGB_ALBEDO_NORMAL")

            # Опційний нод-композитор для денойзингу, якщо попросили
            if settings.get("use_compositor_denoise_node", False) and bpy.context.scene.use_nodes:
                tree = bpy.context.scene.node_tree
                try:
                    # Мінімально інвазивно додаємо нод денойзингу, якщо його ще нема
                    has_denoise_node = any(n.type == 'DENOISE' for n in tree.nodes)
                    if not has_denoise_node:
                        denoise_node = tree.nodes.new('CompositorNodeDenoise')
                        denoise_node.location = (200, 0)
                        # Підключення: якщо є Composite або File Output, намагаємося вставити між Render Layers та виходом
                        render_layers = next((n for n in tree.nodes if n.type == 'R_LAYERS'), None)
                        composite = next((n for n in tree.nodes if n.type == 'COMPOSITE'), None)
                        file_out = next((n for n in tree.nodes if n.type == 'OUTPUT_FILE'), None)
                        if render_layers and (composite or file_out):
                            try:
                                # Класичне підключення до Composite
                                if composite:
                                    tree.links.new(render_layers.outputs.get('Image'), denoise_node.inputs.get('Image'))
                                    # Альбедо/Нормалі якщо доступні
                                    if 'Denoising Albedo' in render_layers.outputs and 'Albedo' in denoise_node.inputs:
                                        tree.links.new(render_layers.outputs['Denoising Albedo'], denoise_node.inputs['Albedo'])
                                    if 'Denoising Normal' in render_layers.outputs and 'Normal' in denoise_node.inputs:
                                        tree.links.new(render_layers.outputs['Denoising Normal'], denoise_node.inputs['Normal'])
                                    tree.links.new(denoise_node.outputs.get('Image'), composite.inputs.get('Image'))
                                elif file_out:
                                    tree.links.new(render_layers.outputs.get('Image'), denoise_node.inputs.get('Image'))
                                    tree.links.new(denoise_node.outputs.get('Image'), file_out.inputs.get('Image'))
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Не вдалося налаштувати денойзинг: {e}")
        
        # Налаштування якості
        cycles.max_bounces = int(settings.get("max_bounces", 12))
        cycles.diffuse_bounces = int(settings.get("diffuse_bounces", 4))
        cycles.glossy_bounces = int(settings.get("glossy_bounces", 4))
        cycles.transmission_bounces = int(settings.get("transmission_bounces", 12))
        cycles.volume_bounces = int(settings.get("volume_bounces", 0))
        
        # Налаштування освітлення
        cycles.caustics_reflective = settings.get("caustics_reflective", True)
        cycles.caustics_refractive = settings.get("caustics_refractive", True)
        
        # Тайли (якщо підтримується) та пам'ять
        self._apply_tile_settings(scene, cycles, settings)
        
        # Налаштування кольору
        scene.view_settings.view_transform = settings.get("view_transform", "Filmic")
        scene.view_settings.look = settings.get("look", "None")
        scene.view_settings.exposure = settings.get("exposure", 0.0)
        scene.view_settings.gamma = settings.get("gamma", 1.0)

        # Simplify/LOD
        self._apply_simplify_settings(scene, settings)
    
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
        
        # Simplify/LOD для Eevee також може зменшити геометрію
        self._apply_simplify_settings(scene, settings)
    
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
