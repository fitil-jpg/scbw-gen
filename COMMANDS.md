# Available Commands

The following commands demonstrate common invocations of the Houdini render automation entry point `houdini/generate_passes.py`.

```bash
hython houdini/generate_passes.py --help
hython houdini/generate_passes.py --list-shots
hython houdini/generate_passes.py --config params/pack.yaml --shot shot_1001 --output renders/houdini
hython houdini/generate_passes.py --config params/pack.yaml --shot shot_1001 --shot shot_1002 --output renders/houdini --verbose
hython houdini/generate_passes.py --config params/pack.yaml --passes rgba mask normal --frame-range 1 24 --output renders/houdini
hython houdini/generate_passes.py --config params/pack.yaml --hip-file path/to/scene.hip --control-node /obj/custom_controller --render-root /out/custom_passes --exr-driver /out/custom_exr
python houdini/generate_passes.py --config params/pack.yaml --dry-run --verbose
python houdini/generate_passes.py --config params/pack.yaml --shot shot_debug --frame-range 10 12 --dry-run --verbose
```

Each `hython` command assumes that Houdini is installed and that the scene contains the default `/obj/scbw_shot_controller1`, `/out/scbw_passes`, and `/out/scbw_exr_packager` nodes (or that you have overridden them with custom paths). The `python` commands run the script in dry-run mode for validation without Houdini.
