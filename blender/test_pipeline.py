"""Test script for Blender SCBW pipeline."""

import sys
from pathlib import Path

# Add workspace to path
workspace_path = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_path))

from blender.config import load_pack_config, PackConfig
from blender.scene_generator import StarCraftSceneGenerator

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        config = load_pack_config(Path("params/pack.yaml"))
        print(f"✓ Loaded config with {len(config.shots)} shots")
        
        for shot in config.shots:
            print(f"  - Shot {shot.id}: {len(shot.get_palette_colors())} palette colors")
        
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_scene_generation():
    """Test scene generation (requires Blender)."""
    print("Testing scene generation...")
    
    try:
        import bpy
        print("✓ Blender Python API available")
        
        # Load config
        config = load_pack_config(Path("params/pack.yaml"))
        shot = config.shots[0]
        
        # Create scene generator
        generator = StarCraftSceneGenerator(config)
        print(f"✓ Created scene generator for shot {shot.id}")
        
        return True
    except ImportError:
        print("✗ Blender Python API not available (run with Blender)")
        return False
    except Exception as e:
        print(f"✗ Scene generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running Blender SCBW Pipeline Tests")
    print("=" * 40)
    
    tests = [
        test_config_loading,
        test_scene_generation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests completed: {passed}/{total} passed")
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())