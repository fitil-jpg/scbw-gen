"""Blender startup script for SCBW pipeline."""

import sys
import os
from pathlib import Path

# Add the workspace to Python path
workspace_path = Path(__file__).parent.parent
if str(workspace_path) not in sys.path:
    sys.path.insert(0, str(workspace_path))

# Import and run the main script
from blender.generate_passes import main

if __name__ == "__main__":
    # Remove '--' from arguments if present (Blender passes them with --)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(argv))