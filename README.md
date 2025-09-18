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
   - Confirm that the machine sees a valid Houdini license. If `hython` can render without throwing a "no license" dialog, the client is already pulling a license (including the free Apprentice tier). For extra certainty, run one of the license-status commands:
     ```bash
     sesictrl status
     hserver -S
     ```
     Both utilities print the host that supplies the license so you can validate that your environment is pointed at the expected SideFX server or local installation.
   - (Optional) Set `HOUDINI_PATH` or project-specific environment variables if your studio pipeline requires them. See `houdini/README.md` (to be added) for detailed environment notes.
3. **Install helper Python dependencies**
   The Houdini automation scripts rely on [`pyyaml`](https://pyyaml.org/) to read `.yaml` pack descriptions. Create a virtual environment and install the bundled requirements before running the utilities:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```
   After installation you can confirm that YAML loading is available:
   ```bash
   python -c "import yaml; print('pyyaml ready')"
   ```
   If `pyyaml` is unavailable, the tools automatically look for a JSON twin of the configuration (for example `params/pack.json`) so you can still run the helpers by pointing `--config` to that file or allowing the fallback to kick in.

## Houdini Automation Workflow

The Houdini pipeline converts input StarCraft assets into multi-layer EXRs using HDA-driven automation. The primary entry point is the hython-friendly CLI `houdini/generate_passes.py`.

1. **Prepare input assets**
   - Place the source `.scx`/`.chk` maps, sprites, and palette data in the `assets/` directory (create it if necessary).
   - Update `params/pack.yaml` (or `.json`) with references to the assets you want to process.
2. **Inspect available shots**
   ```bash
   hython houdini/generate_passes.py --list-shots
   ```
   The command parses the pack file and prints the shot identifiers that can be rendered.
3. **Launch the automation**
   Run the build script headlessly via `hython`:
   ```bash
   hython houdini/generate_passes.py \
     --hip-file <path/to/your_scene.hip> \
     --config params/pack.yaml \
     --shot shot_1001 \
     --output renders/houdini
   ```
   The CLI defaults to `/obj/scbw_shot_controller1`, `/out/scbw_passes`, and `/out/scbw_exr_packager` for the control node, render container, and EXR packager respectively. Ensure your HIP defines nodes at those locations or override the flags with your studio-specific paths before running the automation.
   The CLI loads the Houdini scene, applies the selected shot parameters, renders the RGBA/mask/Z passes, and finally assembles them into a multi-plane EXR in the requested output folder.
4. **Dry run outside Houdini**
   For CI or quick verification, you may run the script without `hython` by enabling `--dry-run`. The script will validate configuration files and print the paths it would generate without requiring the `hou` module.
5. **Review outputs**
   - Each EXR contains separate layers for the standard RGBA, selection mask, and depth/utility passes configured in your Houdini network.
   - Use your preferred compositing package to inspect the renders or feed them into downstream batch tools.

### Optional Blender Fallback

If Houdini access is unavailable, you may still adapt the legacy Blender scripts for simple sprite renders. This path is community-supported and not part of the primary pipeline; see `docs/blender_fallback.md` (when available) for community notes.

## Legacy Components

The historical Wolfram Language prototype (`wolfram/generate.wl`) remains in the repository for archival and reference purposes only. It is no longer invoked by the project documentation, and day-to-day production should rely on the Houdini pipeline described above.

## Contributing

1. Fork and clone the repository.
2. Create a branch for your feature or bug fix.
3. Run the tests before submitting a pull request:
   ```bash
   pytest
   ```
4. Submit a pull request with a clear description of the changes.

