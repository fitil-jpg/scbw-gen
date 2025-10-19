# Матеріали, Ноди, Процедурні Матеріали, Текстури та UV-розгортання

## Зміст
1. [Вступ до матеріалів](#вступ-до-матеріалів)
2. [Система нодів](#система-нодів)
3. [Процедурні матеріали](#процедурні-матеріали)
4. [Текстури](#текстури)
5. [UV-розгортання](#uv-розгортання)
6. [Практичні приклади](#практичні-приклади)
7. [Оптимізація та продуктивність](#оптимізація-та-продуктивність)

## Вступ до матеріалів

### Що таке матеріали?
Матеріали в 3D-графіці визначають, як поверхня об'єкта взаємодіє зі світлом. Вони контролюють:
- **Колір** (Base Color) - основний колір поверхні
- **Металічність** (Metallic) - чи є поверхня металевою
- **Шорсткість** (Roughness) - наскільки гладенька поверхня
- **Прозорість** (Transmission) - рівень прозорості
- **Емісія** (Emission) - чи світиться поверхня

### Типи матеріалів
1. **PBR (Physically Based Rendering)** - реалістичні матеріали
2. **Toon/Cel Shading** - стилізовані матеріали
3. **Emission** - світлові матеріали
4. **Volume** - об'ємні матеріали

## Система нодів

### Що таке ноди?
Ноди - це блоки, які обробляють дані в системі матеріалів. Кожен нод має:
- **Входи** (Inputs) - дані, які надходять
- **Виходи** (Outputs) - оброблені дані
- **Параметри** - налаштування нода

### Основні типи нодів

#### 1. Shader Nodes (Шейдерні ноди)
```python
# Principled BSDF - основний шейдер
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

# Emission - для світлових матеріалів
emission = nodes.new(type='ShaderNodeEmission')

# Glass - для скляних матеріалів
glass = nodes.new(type='ShaderNodeBsdfGlass')
```

#### 2. Input Nodes (Вхідні ноди)
```python
# Texture Coordinate - координати текстури
tex_coord = nodes.new(type='ShaderNodeTexCoord')

# Geometry - геометричні дані
geometry = nodes.new(type='ShaderNodeNewGeometry')

# Light Path - інформація про світло
light_path = nodes.new(type='ShaderNodeLightPath')
```

#### 3. Texture Nodes (Текстурні ноди)
```python
# Image Texture - зображення
image_tex = nodes.new(type='ShaderNodeTexImage')

# Noise - шум
noise = nodes.new(type='ShaderNodeTexNoise')

# Voronoi - процедурна текстура
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
```

#### 4. Color Nodes (Кольорові ноди)
```python
# Mix - змішування кольорів
mix = nodes.new(type='ShaderNodeMix')

# Hue Saturation Value - налаштування HSV
hsv = nodes.new(type='ShaderNodeHueSaturationValue')

# Bright/Contrast - яскравість/контраст
bright_contrast = nodes.new(type='ShaderNodeBrightContrast')
```

#### 5. Vector Nodes (Векторні ноди)
```python
# Mapping - трансформація координат
mapping = nodes.new(type='ShaderNodeMapping')

# Normal Map - карта нормалей
normal_map = nodes.new(type='ShaderNodeNormalMap')

# Vector Math - математичні операції
vector_math = nodes.new(type='ShaderNodeVectorMath')
```

## Процедурні матеріали

### Що таке процедурні матеріали?
Процедурні матеріали створюються за допомогою математичних функцій, а не зображень. Вони:
- **Масштабуються** без втрати якості
- **Анімуються** легко
- **Займають менше місця** в пам'яті
- **Генеруються** в реальному часі

### Основні процедурні текстури

#### 1. Noise (Шум)
```python
def create_noise_material():
    """Створює матеріал на основі шуму"""
    material = bpy.data.materials.new(name="Noise_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Noise texture
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 15.0
    noise.inputs['Roughness'].default_value = 0.5
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Connections
    material.node_tree.links.new(noise.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

#### 2. Voronoi (Вороной)
```python
def create_voronoi_material():
    """Створює матеріал на основі діаграми Вороного"""
    material = bpy.data.materials.new(name="Voronoi_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Voronoi texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 10.0
    voronoi.inputs['Randomness'].default_value = 1.0
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Connections
    material.node_tree.links.new(voronoi.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

#### 3. Wave (Хвилі)
```python
def create_wave_material():
    """Створює матеріал з хвилями"""
    material = bpy.data.materials.new(name="Wave_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Wave texture
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 5.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value = 2.0
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Connections
    material.node_tree.links.new(wave.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

### Складні процедурні матеріали

#### Матеріал з кількома шарами
```python
def create_layered_material():
    """Створює складний матеріал з кількома шарами"""
    material = bpy.data.materials.new(name="Layered_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Noise 1
    noise1 = nodes.new(type='ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 10.0
    noise1.location = (-400, 200)
    
    # Noise 2
    noise2 = nodes.new(type='ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 50.0
    noise2.location = (-400, 0)
    
    # Mix node
    mix = nodes.new(type='ShaderNodeMix')
    mix.inputs['Fac'].default_value = 0.5
    mix.location = (-200, 100)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(noise1.outputs['Color'], mix.inputs['Color1'])
    material.node_tree.links.new(noise2.outputs['Color'], mix.inputs['Color2'])
    material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

## Текстури

### Типи текстур

#### 1. Diffuse/Albedo (Дифузна)
- Основний колір поверхні
- Не містить інформації про освітлення

#### 2. Normal Map (Карта нормалей)
- Додає деталі без збільшення геометрії
- Синій колір = поверхня перпендикулярна
- Червоний/зелений = нахили

#### 3. Roughness Map (Карта шорсткості)
- Білий = шорстка поверхня
- Чорний = гладенька поверхня

#### 4. Metallic Map (Карта металевості)
- Білий = металева поверхня
- Чорний = неметалева поверхня

#### 5. Emission Map (Карта емісії)
- Визначає, які частини світять

### Завантаження та налаштування текстур

```python
def load_texture_material(texture_path, material_name="Texture_Material"):
    """Завантажує матеріал з текстурою"""
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Image Texture node
    image_tex = nodes.new(type='ShaderNodeTexImage')
    
    # Load image
    if os.path.exists(texture_path):
        image = bpy.data.images.load(texture_path)
        image_tex.image = image
    else:
        print(f"Текстура не знайдена: {texture_path}")
        return None
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Connections
    material.node_tree.links.new(image_tex.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

### PBR матеріал з усіма картами

```python
def create_pbr_material(base_path, material_name="PBR_Material"):
    """Створює PBR матеріал з усіма картами"""
    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Albedo texture
    albedo_tex = nodes.new(type='ShaderNodeTexImage')
    albedo_tex.location = (-400, 200)
    if os.path.exists(f"{base_path}_albedo.png"):
        albedo_tex.image = bpy.data.images.load(f"{base_path}_albedo.png")
    
    # Normal map
    normal_tex = nodes.new(type='ShaderNodeTexImage')
    normal_tex.location = (-400, 0)
    if os.path.exists(f"{base_path}_normal.png"):
        normal_tex.image = bpy.data.images.load(f"{base_path}_normal.png")
    
    # Roughness map
    roughness_tex = nodes.new(type='ShaderNodeTexImage')
    roughness_tex.location = (-400, -200)
    if os.path.exists(f"{base_path}_roughness.png"):
        roughness_tex.image = bpy.data.images.load(f"{base_path}_roughness.png")
    
    # Metallic map
    metallic_tex = nodes.new(type='ShaderNodeTexImage')
    metallic_tex.location = (-400, -400)
    if os.path.exists(f"{base_path}_metallic.png"):
        metallic_tex.image = bpy.data.images.load(f"{base_path}_metallic.png")
    
    # Normal Map node
    normal_map = nodes.new(type='ShaderNodeNormalMap')
    normal_map.location = (-200, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(albedo_tex.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(normal_tex.outputs['Color'], normal_map.inputs['Color'])
    material.node_tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
    material.node_tree.links.new(roughness_tex.outputs['Color'], bsdf.inputs['Roughness'])
    material.node_tree.links.new(metallic_tex.outputs['Color'], bsdf.inputs['Metallic'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

## UV-розгортання

### Що таке UV-розгортання?
UV-розгортання - це процес "розгортання" 3D-моделі на 2D-площину для нанесення текстур.

### UV-координати
- **U** - горизонтальна вісь (0-1)
- **V** - вертикальна вісь (0-1)
- (0,0) - лівий нижній кут
- (1,1) - правий верхній кут

### Основні методи UV-розгортання

#### 1. Automatic Unwrap (Автоматичне розгортання)
```python
def auto_unwrap_mesh(obj):
    """Автоматично розгортає UV для об'єкта"""
    # Select object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Enter Edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Unwrap
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    # Return to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
```

#### 2. Smart UV Project
```python
def smart_uv_project(obj, angle_limit=66, island_margin=0.001):
    """Розумне UV-проектування"""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(angle_limit),
        island_margin=island_margin,
        area_weight=0.0,
        correct_aspect=True
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
```

#### 3. Cube Projection
```python
def cube_projection(obj):
    """Кубічна проекція UV"""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    
    bpy.ops.uv.cube_project(
        cube_size=1.0,
        correct_aspect=True,
        clip_to_bounds=False,
        scale_to_bounds=True
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
```

### Ручне UV-розгортання

```python
def manual_uv_unwrap(obj):
    """Ручне UV-розгортання з налаштуваннями"""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select faces by normal direction
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
    
    # Unwrap selected faces
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    # Pack UV islands
    bpy.ops.uv.pack_islands(margin=0.001)
    
    bpy.ops.object.mode_set(mode='OBJECT')
```

### UV-редактор та інструменти

```python
def setup_uv_editor():
    """Налаштовує UV-редактор"""
    # Split area to show UV editor
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
    
    # Change area type to UV Editor
    area = bpy.context.area
    area.type = 'UV_EDITOR'
    
    # Set UV editor settings
    space = area.spaces[0]
    space.show_region_ui = True
    space.show_region_toolbar = True
```

## Практичні приклади

### 1. Створення матеріалу для StarCraft юніта

```python
def create_starcraft_unit_material(unit_type, team_color):
    """Створює матеріал для юніта StarCraft"""
    material = bpy.data.materials.new(name=f"SC_{unit_type}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Team color
    team_color_node = nodes.new(type='ShaderNodeRGB')
    team_color_node.outputs[0].default_value = (*team_color, 1.0)
    team_color_node.location = (-400, 200)
    
    # Noise for detail
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 5.0
    noise.location = (-400, 0)
    
    # Mix team color with noise
    mix = nodes.new(type='ShaderNodeMix')
    mix.inputs['Fac'].default_value = 0.3
    mix.location = (-200, 100)
    
    # Metallic value
    metallic_value = nodes.new(type='ShaderNodeValue')
    metallic_value.outputs[0].default_value = 0.1
    metallic_value.location = (-400, -200)
    
    # Roughness value
    roughness_value = nodes.new(type='ShaderNodeValue')
    roughness_value.outputs[0].default_value = 0.8
    roughness_value.location = (-400, -400)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(team_color_node.outputs['Color'], mix.inputs['Color1'])
    material.node_tree.links.new(noise.outputs['Color'], mix.inputs['Color2'])
    material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(metallic_value.outputs['Value'], bsdf.inputs['Metallic'])
    material.node_tree.links.new(roughness_value.outputs['Value'], bsdf.inputs['Roughness'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

### 2. Створення матеріалу для території

```python
def create_terrain_material(terrain_type="grass"):
    """Створює матеріал для території"""
    material = bpy.data.materials.new(name=f"Terrain_{terrain_type}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Terrain color based on type
    if terrain_type == "grass":
        base_color = (0.2, 0.6, 0.2, 1.0)
    elif terrain_type == "dirt":
        base_color = (0.4, 0.3, 0.2, 1.0)
    elif terrain_type == "stone":
        base_color = (0.5, 0.5, 0.5, 1.0)
    else:
        base_color = (0.3, 0.3, 0.3, 1.0)
    
    # Base color
    color_node = nodes.new(type='ShaderNodeRGB')
    color_node.outputs[0].default_value = base_color
    color_node.location = (-400, 200)
    
    # Noise for variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 10.0
    noise.inputs['Detail'].default_value = 10.0
    noise.location = (-400, 0)
    
    # Mix base color with noise
    mix = nodes.new(type='ShaderNodeMix')
    mix.inputs['Fac'].default_value = 0.2
    mix.location = (-200, 100)
    
    # Roughness
    roughness_value = nodes.new(type='ShaderNodeValue')
    roughness_value.outputs[0].default_value = 0.9
    roughness_value.location = (-400, -200)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(color_node.outputs['Color'], mix.inputs['Color1'])
    material.node_tree.links.new(noise.outputs['Color'], mix.inputs['Color2'])
    material.node_tree.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(roughness_value.outputs['Value'], bsdf.inputs['Roughness'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

### 3. Анімований матеріал

```python
def create_animated_material():
    """Створює анімований матеріал"""
    material = bpy.data.materials.new(name="Animated_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Animated noise
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.location = (-400, 0)
    
    # Time node for animation
    time = nodes.new(type='ShaderNodeTexCoord')
    time.location = (-600, 0)
    
    # Mapping for animation
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-500, 0)
    
    # Animate mapping
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", frame=1)
    mapping.inputs['Location'].default_value = (0, 0, 0)
    mapping.inputs['Location'].keyframe_insert(data_path="default_value", frame=100)
    mapping.inputs['Location'].default_value = (1, 1, 0)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Connections
    material.node_tree.links.new(time.outputs['Generated'], mapping.inputs['Vector'])
    material.node_tree.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    material.node_tree.links.new(noise.outputs['Color'], bsdf.inputs['Base Color'])
    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return material
```

## Оптимізація та продуктивність

### Поради для оптимізації

#### 1. Використання текстурних атласів
```python
def create_texture_atlas(texture_paths, atlas_size=2048):
    """Створює текстурний атлас з кількох текстур"""
    # Implementation for texture atlas creation
    pass
```

#### 2. LOD (Level of Detail) матеріали
```python
def create_lod_materials(base_material, lod_levels=3):
    """Створює матеріали різних рівнів деталізації"""
    materials = []
    
    for i in range(lod_levels):
        lod_material = base_material.copy()
        lod_material.name = f"{base_material.name}_LOD_{i}"
        
        # Reduce texture resolution for higher LOD
        scale_factor = 1.0 / (2 ** i)
        # Apply scale factor to texture nodes
        
        materials.append(lod_material)
    
    return materials
```

#### 3. Кешування матеріалів
```python
class MaterialCache:
    """Кеш для матеріалів"""
    
    def __init__(self):
        self.cache = {}
    
    def get_material(self, material_name, create_func):
        """Отримує матеріал з кешу або створює новий"""
        if material_name not in self.cache:
            self.cache[material_name] = create_func()
        return self.cache[material_name]
    
    def clear_cache(self):
        """Очищає кеш"""
        for material in self.cache.values():
            bpy.data.materials.remove(material)
        self.cache.clear()
```

### Налаштування рендерингу для матеріалів

```python
def optimize_render_settings_for_materials():
    """Оптимізує налаштування рендерингу для матеріалів"""
    scene = bpy.context.scene
    
    if scene.render.engine == 'CYCLES':
        cycles = scene.cycles
        
        # Optimize for materials
        cycles.samples = 64  # Lower samples for preview
        cycles.use_denoising = True
        cycles.max_bounces = 8  # Reduce bounces
        cycles.diffuse_bounces = 2
        cycles.glossy_bounces = 2
        
    elif scene.render.engine == 'BLENDER_EEVEE':
        eevee = scene.eevee
        
        # Optimize for materials
        eevee.taa_render_samples = 32
        eevee.use_bloom = True
        eevee.use_ssr = True
        eevee.use_ssao = True
```

## Висновок

Матеріали, ноди, процедурні текстури та UV-розгортання - це основні компоненти створення реалістичних та стилізованих 3D-сцен. Правильне використання цих інструментів дозволяє:

1. **Створювати реалістичні матеріали** з PBR підходом
2. **Генерувати процедурні текстури** для унікальних ефектів
3. **Оптимізувати UV-розгортання** для кращої якості текстур
4. **Анімувати матеріали** для динамічних ефектів
5. **Оптимізувати продуктивність** для швидшого рендерингу

Цей гід надає основи для роботи з матеріалами в Blender та може бути розширений для конкретних потреб проекту.