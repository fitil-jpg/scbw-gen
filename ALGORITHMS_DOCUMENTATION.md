# StarCraft Map Scene Generation Algorithms
# Алгоритми генерації сцен карт StarCraft

## Огляд / Overview

Цей документ описує розширені алгоритми генерації сцен для карт StarCraft, які були розроблені для покращення існуючої системи SCBW-Gen. Алгоритми включають в себе софістиковані підходи до генерації рельєфу, розміщення юнітів, будівель, пошуку шляхів та композиції сцен.

This document describes advanced algorithms for StarCraft map scene generation that have been developed to enhance the existing SCBW-Gen system. The algorithms include sophisticated approaches to terrain generation, unit placement, building placement, pathfinding, and scene composition.

## Структура алгоритмів / Algorithm Structure

### 1. Генерація рельєфу / Terrain Generation (`algorithms/terrain_generator.py`)

#### Основні функції / Key Features:
- **Perlin Noise Implementation**: Реалізація шуму Перліна для природної генерації рельєфу
- **Multi-layer Terrain**: Багатошаровий рельєф з різними типами місцевості
- **Strategic Features**: Генерація стратегічних особливостей (вузькі проходи, ресурси, бази)
- **Height Map Export**: Експорт карт висот та типів рельєфу

#### Класи / Classes:
- `PerlinNoise`: Реалізація шуму Перліна
- `TerrainGenerator`: Основний генератор рельєфу
- `TerrainFeature`: Представлення особливостей рельєфу

#### Приклад використання / Usage Example:
```python
from algorithms.terrain_generator import TerrainGenerator, create_sample_terrain

# Створити генератор рельєфу
terrain = create_sample_terrain(512, 512)

# Експортувати карти
terrain.export_height_map("height_map.png")
terrain.export_terrain_type_map("terrain_types.png")
```

### 2. Розміщення юнітів / Unit Placement (`algorithms/unit_placement.py`)

#### Основні функції / Key Features:
- **Tactical Formations**: Тактичні формації (лінія, дуга, клин, коло, квадрат)
- **AI-driven Positioning**: Розумне позиціонування на основі тактичних міркувань
- **Formation Optimization**: Оптимізація формацій для кращої тактичної позиції
- **Strategic Analysis**: Аналіз стратегічної ситуації для розміщення

#### Класи / Classes:
- `TacticalAnalyzer`: Аналізатор тактичної ситуації
- `FormationGenerator`: Генератор формацій
- `UnitPlacementOptimizer`: Оптимізатор розміщення

#### Типи формацій / Formation Types:
- `LINE`: Лінійна формація
- `ARC`: Дугова формація
- `WEDGE`: Клинова формація
- `CIRCLE`: Кругова формація
- `SQUARE`: Квадратна формація
- `TACTICAL`: Тактична формація з урахуванням місцевості

### 3. Розміщення будівель / Building Placement (`algorithms/building_placement.py`)

#### Основні функції / Key Features:
- **Strategic Positioning**: Стратегічне позиціонування будівель
- **Resource Optimization**: Оптимізація доступу до ресурсів
- **Defensive Layout**: Оборонне розташування з вежами та стінами
- **Base Layout Generation**: Генерація повних макетів баз

#### Класи / Classes:
- `StrategicAnalyzer`: Аналізатор стратегічних позицій
- `BaseLayoutGenerator`: Генератор макетів баз
- `BaseLayoutOptimizer`: Оптимізатор макетів

#### Типи будівель / Building Types:
- `CASTLE`: Замок (головна будівля)
- `TOWER`: Оборонна вежа
- `BARRACKS`: Казарми
- `MAGE_TOWER`: Вежа магів
- `WALL`: Стіна
- `GATE`: Ворота
- `RESOURCE_DEPOT`: Ресурсне депо

### 4. Пошук шляхів / Pathfinding (`algorithms/pathfinding.py`)

#### Основні функції / Key Features:
- **A* Pathfinding**: A* алгоритм з урахуванням рельєфу
- **Formation Movement**: Рух формацій юнітів
- **Strategic Path Planning**: Стратегічне планування шляхів
- **Dynamic Obstacle Avoidance**: Уникнення динамічних перешкод

#### Класи / Classes:
- `PathfindingGrid`: Сітка для пошуку шляху
- `AStarPathfinder`: A* алгоритм
- `FormationPathfinder`: Пошук шляхів для формацій
- `StrategicPathPlanner`: Стратегічний планувальник
- `DynamicObstacleAvoidance`: Уникнення перешкод

#### Типи рельєфу для пошуку / Terrain Types for Pathfinding:
- `GRASS`: Трава (вартість: 1.0)
- `WATER`: Вода (вартість: 2.0)
- `MOUNTAIN`: Гори (вартість: 3.0)
- `FOREST`: Ліс (вартість: 1.5)
- `SWAMP`: Болото (вартість: 2.5)
- `ROAD`: Дорога (вартість: 0.5)

### 5. Композиція сцен / Scene Composition (`algorithms/scene_composition.py`)

#### Основні функції / Key Features:
- **Rule-based Camera Positioning**: Позиціонування камери на основі правил
- **Dynamic Lighting Setup**: Динамічне налаштування освітлення
- **Atmospheric Effects**: Атмосферні ефекти
- **Compositional Balance**: Композиційний баланс

#### Класи / Classes:
- `CompositionAnalyzer`: Аналізатор композиції
- `LightingDesigner`: Дизайнер освітлення
- `AtmosphericDesigner`: Дизайнер атмосфери
- `SceneComposer`: Композитор сцен

#### Типи камер / Camera Types:
- `OVERVIEW`: Оглядова камера
- `TACTICAL`: Тактична камера
- `CINEMATIC`: Кінематографічна камера
- `FOLLOW`: Камера слідування
- `ORBIT`: Орбітальна камера

## Інтеграція з існуючою системою / Integration with Existing System

### Використання з Blender Pipeline / Using with Blender Pipeline

```python
# В blender/scene_generator.py
from algorithms.terrain_generator import TerrainGenerator
from algorithms.unit_placement import FormationGenerator, TacticalAnalyzer
from algorithms.scene_composition import SceneComposer

# Ініціалізація
terrain_gen = TerrainGenerator(100, 100)
analyzer = TacticalAnalyzer(100, 100)
composer = SceneComposer(100, 100)

# Генерація рельєфу
terrain_gen.generate_height_map()
terrain_gen.generate_strategic_features()

# Генерація формацій
formation_gen = FormationGenerator(analyzer)
positions = formation_gen.generate_formation(units, config)

# Композиція сцени
scene_config = composer.compose_scene(scene_type, objects, areas)
```

### Використання з USD Generator / Using with USD Generator

```python
# В generate_usd_scene.py
from algorithms.building_placement import BaseLayoutGenerator, StrategicAnalyzer
from algorithms.pathfinding import PathfindingGrid, AStarPathfinder

# Створення стратегічного аналізатора
analyzer = StrategicAnalyzer(100, 100)

# Генерація макету бази
layout_gen = BaseLayoutGenerator(analyzer)
base_layout = layout_gen.generate_base_layout((50, 50), "player")

# Пошук шляхів
grid = PathfindingGrid(50, 50)
pathfinder = AStarPathfinder(grid)
path = pathfinder.find_path(start, goal)
```

## Параметри налаштування / Configuration Parameters

### Terrain Generation / Генерація рельєфу
- `octaves`: Кількість октав для фрактального шуму (за замовчуванням: 4)
- `persistence`: Персистентність шуму (за замовчуванням: 0.5)
- `lacunarity`: Лакунарність шуму (за замовчуванням: 2.0)
- `scale`: Масштаб шуму (за замовчуванням: 50.0)

### Unit Placement / Розміщення юнітів
- `spacing`: Відстань між юнітами (за замовчуванням: 2.0)
- `formation_type`: Тип формації
- `tactical_considerations`: Тактичні міркування (true/false)

### Building Placement / Розміщення будівель
- `base_size`: Розмір бази (за замовчуванням: 30.0)
- `defense_priority`: Пріоритет оборони (0.0-1.0)
- `resource_accessibility`: Доступність ресурсів (0.0-1.0)

### Pathfinding / Пошук шляхів
- `cell_size`: Розмір клітинки сітки (за замовчуванням: 1.0)
- `terrain_costs`: Вартості проходження різних типів рельєфу
- `obstacle_avoidance`: Уникнення перешкод (true/false)

### Scene Composition / Композиція сцен
- `camera_type`: Тип камери
- `lighting_type`: Тип освітлення
- `weather_type`: Тип погоди
- `time_of_day`: Час доби

## Приклади використання / Usage Examples

### 1. Генерація повної карти / Full Map Generation

```python
from algorithms.terrain_generator import create_sample_terrain
from algorithms.unit_placement import create_sample_army, FormationGenerator
from algorithms.building_placement import create_sample_strategic_analyzer
from algorithms.scene_composition import SceneComposer

# Генерація рельєфу
terrain = create_sample_terrain(512, 512)

# Створення армії
army = create_sample_army()
analyzer = create_sample_strategic_analyzer()
formation_gen = FormationGenerator(analyzer)

# Генерація формації
config = FormationConfig(FormationType.TACTICAL, 2.0)
positions = formation_gen.generate_formation(army, config)

# Композиція сцени
composer = SceneComposer(100, 100)
scene_config = composer.compose_scene("battle", objects, areas)
```

### 2. Оптимізація існуючої сцени / Optimizing Existing Scene

```python
from algorithms.unit_placement import UnitPlacementOptimizer
from algorithms.building_placement import BaseLayoutOptimizer

# Оптимізація розміщення юнітів
unit_optimizer = UnitPlacementOptimizer(analyzer)
optimized_positions = unit_optimizer.optimize_formation(units, positions)

# Оптимізація макету бази
layout_optimizer = BaseLayoutOptimizer(analyzer)
optimized_layout = layout_optimizer.optimize_base_layout(base_layout)
```

### 3. Динамічне планування шляхів / Dynamic Path Planning

```python
from algorithms.pathfinding import PathfindingGrid, StrategicPathPlanner

# Створення сітки
grid = PathfindingGrid(50, 50)

# Стратегічне планування
planner = StrategicPathPlanner(grid)
attack_path = planner.plan_attack_path(start, enemy_base)
patrol_path = planner.plan_patrol_path(patrol_points, loop=True)
```

## Продуктивність / Performance

### Оптимізації / Optimizations
- **Spatial Hashing**: Просторове хешування для швидкого пошуку сусідів
- **LOD System**: Система рівнів деталізації для великих карт
- **Parallel Processing**: Паралельна обробка для складних сцен
- **Caching**: Кешування результатів для повторного використання

### Рекомендації / Recommendations
- Для карт розміром до 256x256: використовуйте стандартні налаштування
- Для карт 512x512+: зменшіть кількість октав шуму та використовуйте LOD
- Для складних сцен: активуйте кешування та паралельну обробку

## Розширення / Extensions

### Додавання нових типів рельєфу / Adding New Terrain Types
```python
# В terrain_generator.py
class TerrainType(Enum):
    # ... існуючі типи
    VOLCANIC = "volcanic"
    CRYSTAL = "crystal"

# Додати вартості в TerrainGenerator
self.terrain_costs = {
    # ... існуючі вартості
    TerrainType.VOLCANIC: 4.0,
    TerrainType.CRYSTAL: 1.2
}
```

### Додавання нових формацій / Adding New Formations
```python
# В unit_placement.py
class FormationType(Enum):
    # ... існуючі типи
    PHALANX = "phalanx"
    SKIRMISH = "skirmish"

# Додати реалізацію в FormationGenerator
def _generate_phalanx_formation(self, units, config):
    # Реалізація фаланги
    pass
```

## Відомі обмеження / Known Limitations

1. **Memory Usage**: Великі карти можуть вимагати багато пам'яті
2. **Generation Time**: Складні сцени можуть генеруватися довго
3. **Terrain Detail**: Деталізація рельєфу обмежена розміром сітки
4. **Pathfinding**: A* алгоритм може бути повільним для дуже великих сіток

## Майбутні покращення / Future Improvements

1. **Machine Learning Integration**: Інтеграція машинного навчання для покращення алгоритмів
2. **Real-time Generation**: Генерація в реальному часі
3. **Multi-threading**: Покращена підтримка багатопотоковості
4. **GPU Acceleration**: Прискорення на GPU для складних обчислень

## Ліцензія / License

Ці алгоритми розроблені як частина проекту SCBW-Gen та поширюються під тією ж ліцензією.

These algorithms are developed as part of the SCBW-Gen project and are distributed under the same license.

## Контакти / Contacts

Для питань та пропозицій щодо алгоритмів звертайтеся до команди розробки SCBW-Gen.

For questions and suggestions regarding the algorithms, please contact the SCBW-Gen development team.