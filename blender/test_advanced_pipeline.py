"""Тести для розширеного Blender SCBW pipeline."""

import unittest
import tempfile
import shutil
from pathlib import Path
import yaml
import json
import sys

# Додавання шляху до модулів
sys.path.append(str(Path(__file__).parent.parent))

from blender.advanced_config_importer import AdvancedConfigImporter, create_sample_config


class TestAdvancedConfigImporter(unittest.TestCase):
    """Тести для розширеного імпортера конфігурації."""
    
    def setUp(self):
        """Налаштування перед кожним тестом."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "test_config.yaml"
        
        # Створення тестової конфігурації
        self.test_config = {
            'seed': 42,
            'image_size': [1920, 1080],
            'shots': [
                {
                    'id': 'test_shot_001',
                    'palette': 'ArmyColors',
                    'left_cluster': {
                        'rect': [0.1, 0.4],
                        'count': 5,
                        'size': [16, 32]
                    },
                    'right_cluster': {
                        'rect': [0.6, 0.6],
                        'count': 3,
                        'size': [18, 36]
                    },
                    'export': {
                        'png': True,
                        'exr16': True
                    }
                }
            ]
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.test_config, f, default_flow_style=False, allow_unicode=True)
    
    def tearDown(self):
        """Очищення після кожного тесту."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Тест завантаження конфігурації."""
        importer = AdvancedConfigImporter(self.config_path)
        config = importer.load_config()
        
        self.assertEqual(config['seed'], 42)
        self.assertEqual(config['image_size'], [1920, 1080])
        self.assertEqual(len(config['shots']), 1)
        self.assertEqual(config['shots'][0]['id'], 'test_shot_001')
    
    def test_load_nonexistent_config(self):
        """Тест завантаження неіснуючої конфігурації."""
        importer = AdvancedConfigImporter("nonexistent.yaml")
        
        with self.assertRaises(FileNotFoundError):
            importer.load_config()
    
    def test_get_shot_config(self):
        """Тест отримання конфігурації шоту."""
        importer = AdvancedConfigImporter(self.config_path)
        importer.load_config()
        
        shot = importer.get_shot_config('test_shot_001')
        self.assertIsNotNone(shot)
        self.assertEqual(shot['id'], 'test_shot_001')
        
        # Тест неіснуючого шоту
        shot = importer.get_shot_config('nonexistent')
        self.assertIsNone(shot)
    
    def test_get_palette_colors(self):
        """Тест отримання кольорів палітри."""
        importer = AdvancedConfigImporter(self.config_path)
        importer.load_config()
        
        shot = importer.get_shot_config('test_shot_001')
        colors = importer.get_palette_colors(shot)
        
        # Перевірка попередньо визначеної палітри
        self.assertEqual(len(colors), 3)
        self.assertEqual(colors[0], [0.2, 0.4, 0.8])  # Синя армія
        self.assertEqual(colors[1], [0.8, 0.2, 0.2])  # Червона армія
        self.assertEqual(colors[2], [0.2, 0.8, 0.2])  # Зелена армія
    
    def test_get_palette_colors_custom(self):
        """Тест отримання кастомних кольорів палітри."""
        custom_config = {
            'shots': [
                {
                    'id': 'custom_shot',
                    'palette': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
                }
            ]
        }
        
        custom_path = self.temp_dir / "custom_config.yaml"
        with open(custom_path, 'w', encoding='utf-8') as f:
            yaml.dump(custom_config, f, default_flow_style=False, allow_unicode=True)
        
        importer = AdvancedConfigImporter(custom_path)
        importer.load_config()
        
        shot = importer.get_shot_config('custom_shot')
        colors = importer.get_palette_colors(shot)
        
        self.assertEqual(colors, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
    
    def test_validate_config_valid(self):
        """Тест валідації валідної конфігурації."""
        importer = AdvancedConfigImporter(self.config_path)
        importer.load_config()
        
        errors = importer.validate_config()
        self.assertEqual(len(errors), 0)
    
    def test_validate_config_invalid(self):
        """Тест валідації невалідної конфігурації."""
        invalid_config = {
            'shots': [
                {
                    'id': 'invalid_shot',
                    # Відсутні обов'язкові поля
                }
            ]
        }
        
        invalid_path = self.temp_dir / "invalid_config.yaml"
        with open(invalid_path, 'w', encoding='utf-8') as f:
            yaml.dump(invalid_config, f, default_flow_style=False, allow_unicode=True)
        
        importer = AdvancedConfigImporter(invalid_path)
        importer.load_config()
        
        errors = importer.validate_config()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('відсутня палітра' in error.lower() for error in errors))
    
    def test_export_config_summary(self):
        """Тест експорту зведення конфігурації."""
        importer = AdvancedConfigImporter(self.config_path)
        importer.load_config()
        
        summary_path = self.temp_dir / "summary.json"
        importer.export_config_summary(summary_path)
        
        self.assertTrue(summary_path.exists())
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        self.assertEqual(summary['total_shots'], 1)
        self.assertEqual(summary['image_size'], [1920, 1080])
        self.assertEqual(len(summary['shots']), 1)
        self.assertEqual(summary['shots'][0]['id'], 'test_shot_001')
    
    def test_create_sample_config(self):
        """Тест створення прикладу конфігурації."""
        sample_path = self.temp_dir / "sample.yaml"
        create_sample_config(sample_path)
        
        self.assertTrue(sample_path.exists())
        
        # Перевірка валідності створеної конфігурації
        importer = AdvancedConfigImporter(sample_path)
        config = importer.load_config()
        errors = importer.validate_config()
        
        self.assertEqual(len(errors), 0)
        self.assertIn('shots', config)
        self.assertGreater(len(config['shots']), 0)


class TestAssetConfigs(unittest.TestCase):
    """Тести для конфігурацій асетів."""
    
    def setUp(self):
        """Налаштування перед кожним тестом."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Створення тестових конфігурацій асетів
        self.create_asset_configs()
    
    def tearDown(self):
        """Очищення після кожного тесту."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_asset_configs(self):
        """Створює тестові конфігурації асетів."""
        # Конфігурація будівель
        buildings_config = {
            'buildings': {
                'command_center': {
                    'sprite': 'command_center.png',
                    'size': [128, 128],
                    'scale': 2.0,
                    'health': 500,
                    'cost': 500
                },
                'barracks': {
                    'sprite': 'barracks.png',
                    'size': [80, 80],
                    'scale': 1.2,
                    'health': 300,
                    'cost': 200
                }
            }
        }
        
        buildings_path = self.temp_dir / "buildings" / "buildings_config.yaml"
        buildings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(buildings_path, 'w', encoding='utf-8') as f:
            yaml.dump(buildings_config, f, default_flow_style=False, allow_unicode=True)
        
        # Конфігурація юнітів
        units_config = {
            'units': {
                'marine': {
                    'sprite': 'marine.png',
                    'size': [32, 32],
                    'health': 40,
                    'damage': 6,
                    'speed': 1.5
                },
                'zergling': {
                    'sprite': 'zergling.png',
                    'size': [24, 24],
                    'health': 35,
                    'damage': 5,
                    'speed': 2.0
                }
            }
        }
        
        units_path = self.temp_dir / "units" / "units_config.yaml"
        units_path.parent.mkdir(parents=True, exist_ok=True)
        with open(units_path, 'w', encoding='utf-8') as f:
            yaml.dump(units_config, f, default_flow_style=False, allow_unicode=True)
    
    def test_load_asset_configs(self):
        """Тест завантаження конфігурацій асетів."""
        importer = AdvancedConfigImporter("dummy.yaml")
        assets = importer.load_asset_configs(self.temp_dir)
        
        self.assertIn('buildings', assets)
        self.assertIn('units', assets)
        
        # Перевірка будівель
        buildings = assets['buildings']['buildings']
        self.assertIn('command_center', buildings)
        self.assertIn('barracks', buildings)
        self.assertEqual(buildings['command_center']['health'], 500)
        
        # Перевірка юнітів
        units = assets['units']['units']
        self.assertIn('marine', units)
        self.assertIn('zergling', units)
        self.assertEqual(units['marine']['damage'], 6)
    
    def test_get_building_config(self):
        """Тест отримання конфігурації будівлі."""
        importer = AdvancedConfigImporter("dummy.yaml")
        importer.load_asset_configs(self.temp_dir)
        
        # Тест існуючої будівлі
        config = importer.get_building_config('command_center')
        self.assertIsNotNone(config)
        self.assertEqual(config['health'], 500)
        
        # Тест неіснуючої будівлі
        config = importer.get_building_config('nonexistent')
        self.assertIsNone(config)
    
    def test_get_unit_config(self):
        """Тест отримання конфігурації юніта."""
        importer = AdvancedConfigImporter("dummy.yaml")
        importer.load_asset_configs(self.temp_dir)
        
        # Тест існуючого юніта
        config = importer.get_unit_config('marine')
        self.assertIsNotNone(config)
        self.assertEqual(config['damage'], 6)
        
        # Тест неіснуючого юніта
        config = importer.get_unit_config('nonexistent')
        self.assertIsNone(config)


class TestJSONConfig(unittest.TestCase):
    """Тести для JSON конфігурацій."""
    
    def setUp(self):
        """Налаштування перед кожним тестом."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_path = self.temp_dir / "test_config.json"
        
        # Створення тестової JSON конфігурації
        self.test_config = {
            'seed': 42,
            'image_size': [1920, 1080],
            'shots': [
                {
                    'id': 'json_shot_001',
                    'palette': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                    'left_cluster': {
                        'rect': [0.1, 0.4],
                        'count': 5,
                        'size': [16, 32]
                    },
                    'export': {
                        'png': True
                    }
                }
            ]
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=2, ensure_ascii=False)
    
    def tearDown(self):
        """Очищення після кожного тесту."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_json_config(self):
        """Тест завантаження JSON конфігурації."""
        importer = AdvancedConfigImporter(self.config_path)
        config = importer.load_config()
        
        self.assertEqual(config['seed'], 42)
        self.assertEqual(config['image_size'], [1920, 1080])
        self.assertEqual(len(config['shots']), 1)
        self.assertEqual(config['shots'][0]['id'], 'json_shot_001')
    
    def test_json_palette_colors(self):
        """Тест отримання кольорів палітри з JSON."""
        importer = AdvancedConfigImporter(self.config_path)
        importer.load_config()
        
        shot = importer.get_shot_config('json_shot_001')
        colors = importer.get_palette_colors(shot)
        
        self.assertEqual(colors, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])


class TestErrorHandling(unittest.TestCase):
    """Тести обробки помилок."""
    
    def test_invalid_yaml_syntax(self):
        """Тест обробки невалідного YAML синтаксису."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            invalid_yaml_path = temp_dir / "invalid.yaml"
            with open(invalid_yaml_path, 'w', encoding='utf-8') as f:
                f.write("invalid: yaml: content: [\n")  # Невалідний YAML
            
            importer = AdvancedConfigImporter(invalid_yaml_path)
            
            with self.assertRaises(Exception):  # Може бути yaml.YAMLError або інша помилка
                importer.load_config()
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def test_empty_config(self):
        """Тест обробки порожньої конфігурації."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            empty_path = temp_dir / "empty.yaml"
            with open(empty_path, 'w', encoding='utf-8') as f:
                f.write("")  # Порожній файл
            
            importer = AdvancedConfigImporter(empty_path)
            config = importer.load_config()
            
            # Порожня конфігурація повинна повернути None або порожній dict
            self.assertTrue(config is None or config == {})
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def run_tests():
    """Запуск всіх тестів."""
    # Створення тестового suite
    test_suite = unittest.TestSuite()
    
    # Додавання тестів
    test_classes = [
        TestAdvancedConfigImporter,
        TestAssetConfigs,
        TestJSONConfig,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Запуск тестів
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Запуск тестів Blender SCBW Pipeline")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ Всі тести пройшли успішно!")
    else:
        print("\n❌ Деякі тести не пройшли!")
    
    print("=" * 50)