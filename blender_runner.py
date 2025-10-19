#!/usr/bin/env python3
"""Blender script runner that properly handles command line arguments."""

import sys
import os
from pathlib import Path

# Add workspace to Python path
workspace_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(workspace_path))

# Change to workspace directory
os.chdir(workspace_path)

# Set up the command line arguments
sys.argv = [
    'blender_runner.py',
    '--config', 'params/pack.yaml',
    '--shot', 'shot_1001',
    '--output', 'renders/blender'
]

print("Starting Blender script execution...")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

try:
    # Import the main function from the generate_passes module
    from blender.generate_passes import main
    
    # Run the main function
    result = main()
    print(f"Script completed with exit code: {result}")
    sys.exit(result)
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)
except Exception as e:
    print(f"Error running script: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)