#!/usr/bin/env python3
"""Test PyYAML in Blender on macOS."""

import sys
import os
from pathlib import Path

# Add workspace to Python path
workspace_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(workspace_path))

print("Testing PyYAML in Blender...")
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import yaml
    print("✓ PyYAML imported successfully")
    print(f"PyYAML version: {yaml.__version__}")
    
    # Test basic YAML functionality
    test_data = {'test': 'value', 'number': 42}
    yaml_str = yaml.dump(test_data)
    print(f"✓ YAML dump works: {yaml_str.strip()}")
    
    loaded_data = yaml.safe_load(yaml_str)
    print(f"✓ YAML load works: {loaded_data}")
    
    # Test loading the actual config file
    config_path = workspace_path / 'params' / 'pack.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✓ Successfully loaded config file: {list(config.keys())}")
    else:
        print(f"✗ Config file not found: {config_path}")
        
except ImportError as e:
    print(f"✗ Failed to import PyYAML: {e}")
    print("PyYAML needs to be installed in Blender's Python environment")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✓ All PyYAML tests passed!")