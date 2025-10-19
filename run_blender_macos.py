#!/usr/bin/env python3
"""Wrapper script to run Blender generate_passes on macOS with proper argument handling."""

import sys
import os
from pathlib import Path

# Add workspace to Python path
workspace_path = Path(__file__).parent.absolute()
sys.path.insert(0, str(workspace_path))

# Set up the command line arguments that the script expects
sys.argv = [
    'blender/generate_passes.py',
    '--config', 'params/pack.yaml',
    '--shot', 'shot_1001',
    '--output', 'renders/blender'
]

# Change to workspace directory
os.chdir(workspace_path)

print("Running Blender generate_passes script...")
print(f"Working directory: {os.getcwd()}")
print(f"Arguments: {sys.argv}")

try:
    # Import and run the main function
    from blender.generate_passes import main
    result = main()
    print(f"Script completed with exit code: {result}")
    sys.exit(result)
except Exception as e:
    print(f"Error running script: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)