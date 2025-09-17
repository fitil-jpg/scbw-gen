# SCBW-Gen

SCBW-Gen (StarCraft: Brood War Generator) is a collection of tools for building and rendering StarCraft: Brood War assets. The toolkit now centers on a Houdini-driven pipeline that automates the generation of multi-layer EXRs for downstream compositing and analysis.

## Prerequisites

- **Houdini 19.5+ with _hython_** – the primary runtime for the asset pipeline. Ensure the Houdini installation directory is on your `PATH` so the `hython` interpreter is available from the command line.
- **Python 3.10+** – optional, used for ancillary utilities and validation scripts outside of Houdini.
- **Optional: Blender 3.x** – maintained as a fallback path for teams that cannot access Houdini, but not required for the main workflow.
- Optional: Git for version control.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scbw-gen
   ```
2. **Configure your Houdini environment**
   - Verify that `hython` runs from your shell:
     ```bash
     hython --version
     ```
   - (Optional) Set `HOUDINI_PATH` or project-specific environment variables if your studio pipeline requires them. See `houdini/README.md` (to be added) for detailed environment notes.
3. **Install helper Python dependencies (optional)**
   If you plan to use the standalone utilities, create a virtual environment and install the requirements:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

## Houdini Automation Workflow

The Houdini pipeline converts input StarCraft assets into multi-layer EXRs using HDA-driven automation. The entry point script is `houdini/scripts/build_multilayer_exr.py` (added alongside the Houdini digital assets).

1. **Prepare input assets**
   - Place the source `.scx`/`.chk` maps, sprites, and palette data in the `assets/` directory (create it if necessary).
   - Update `params/pack.yaml` with references to the assets you want to process.
2. **Launch the automation**
   Run the build script headlessly via `hython`:
   ```bash
   hython houdini/scripts/build_multilayer_exr.py \
     --config params/pack.yaml \
     --output renders/multilayer
   ```
   The script loads the Houdini scene, imports the requested game assets, and writes layered EXR plates for each animation state to the specified output folder.
3. **Review outputs**
   - Each EXR contains separate layers for diffuse, emission, selection masks, and any auxiliary passes authored in the HDA network.
   - Use your preferred compositing package to inspect the renders or feed them into downstream batch tools.

### Optional Blender Fallback

If Houdini access is unavailable, you may still adapt the legacy Blender scripts for simple sprite renders. This path is community-supported and not part of the primary pipeline; see `docs/blender_fallback.md` (when available) for community notes.

## Legacy Components

An earlier Wolfram Language prototype remains in the repository for archival and reference purposes only. It is no longer maintained, and day-to-day production should rely on the Houdini pipeline described above.

## Contributing

1. Fork and clone the repository.
2. Create a branch for your feature or bug fix.
3. Run the tests before submitting a pull request:
   ```bash
   pytest
   ```
4. Submit a pull request with a clear description of the changes.

