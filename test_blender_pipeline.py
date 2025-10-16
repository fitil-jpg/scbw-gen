#!/usr/bin/env python3
"""Test script for Blender SCBW pipeline."""

import sys
from pathlib import Path

# Add the workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

from blender.config import load_pack_config, ConfigError
from blender.generate_passes import main as blender_main

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        config = load_pack_config(Path("params/pack.yaml"))
        print(f"✓ Loaded configuration with {len(config.shots)} shots")
        
        for shot in config.shots:
            print(f"  - Shot {shot.id}: palette={shot.palette}")
        
        return True
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_dry_run():
    """Test dry run mode."""
    print("\nTesting dry run mode...")
    
    try:
        # Run in dry-run mode
        exit_code = blender_main([
            "--config", "params/pack.yaml",
            "--shot", "shot_1001",
            "--output", "test_renders",
            "--dry-run",
            "--verbose"
        ])
        
        if exit_code == 0:
            print("✓ Dry run completed successfully")
            return True
        else:
            print(f"✗ Dry run failed with exit code {exit_code}")
            return False
    except Exception as e:
        print(f"✗ Dry run error: {e}")
        return False

def main():
    """Run all tests."""
    print("Blender SCBW Pipeline Test")
    print("=" * 40)
    
    tests = [
        test_config_loading,
        test_dry_run,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())