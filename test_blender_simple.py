#!/usr/bin/env python3
"""
Simple test script for Blender SCBW pipeline
"""
import sys
from pathlib import Path

# Add workspace to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_dry_run():
    """Test dry run mode without Blender modules."""
    print("Testing Blender pipeline dry run...")
    
    try:
        from blender.config import load_pack_config, filter_shots
        
        # Load configuration
        config = load_pack_config(Path("params/pack.yaml"))
        print(f"✓ Loaded configuration with {len(config.shots)} shots")
        
        # Filter shots
        selected_shots = filter_shots(config, ["shot_1001"])
        print(f"✓ Selected {len(selected_shots)} shots")
        
        for shot in selected_shots:
            print(f"  - Shot {shot.id}: palette={shot.palette}")
            print(f"    Export: {shot.export}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_dry_run()
    if success:
        print("✓ Blender pipeline test passed!")
        sys.exit(0)
    else:
        print("✗ Blender pipeline test failed!")
        sys.exit(1)