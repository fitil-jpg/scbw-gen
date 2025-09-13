# SCBW-Gen

SCBW-Gen (StarCraft: Brood War Generator) is a collection of tools for building and rendering StarCraft: Brood War assets with Blender and Python. The goal of the project is to automate asset creation for modding, research, or visualization workflows.

## Prerequisites

- **Blender 3.x** – generation scripts expect Blender 3.x to be installed and accessible from the command line.
- **Python 3.10+** – used to run helper utilities and automation scripts.
- Optional: Git for version control.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scbw-gen
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows
   ```
3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   If Blender's bundled Python differs from your system Python, you can install dependencies for Blender itself:
   ```bash
   blender --background --python -m pip install -r requirements.txt
   ```

## Basic Usage

The following examples assume a script named `generate.py` exists in the `scripts/` directory. Adjust paths and options as your own scripts require.

### Headless rendering
Run Blender without the GUI to generate assets:
```bash
blender --background --python scripts/generate.py -- --map maps/(2)Destination.scx --output renders/
```

### Running with system Python
Some helper scripts may run directly via Python:
```bash
python scripts/generate.py --tileset jungle --count 10
```
Generated files will be placed in the specified output directory.

## Contributing

1. Fork and clone the repository.
2. Create a branch for your feature or bug fix.
3. Run the tests before submitting a pull request:
   ```bash
   pytest
   ```
4. Submit a pull request with a clear description of the changes.

