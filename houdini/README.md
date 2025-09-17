# Houdini Automation Scripts

The `houdini/` package contains hython-friendly automation utilities that build the
multi-pass EXRs consumed by the SCBW-Gen pipeline. The scripts are designed to run
inside SideFX Houdini via the `hython` interpreter, but they also support a dry-run
mode for validation on systems that do not provide the `hou` module.

## Entry Points

- `generate_passes.py` – Parses `params/pack.yaml`/`.json`, updates the Houdini
  scene with shot-specific parameters, renders the RGBA/mask/Z passes defined in
  your `/out` network, and assembles the output into multi-plane EXR files.

Invoke the script with `hython`:

```bash
hython houdini/generate_passes.py \
  --config params/pack.yaml \
  --shot shot_1001 \
  --output renders/houdini \
  --control-node /obj/scbw_shot_controller1 \
  --render-root /out/scbw_passes \
  --exr-driver /out/scbw_exr_packager
```

Use `--list-shots` to inspect available shot identifiers or `--dry-run` when
running outside Houdini. The latter is useful for CI environments where `hou`
is not available; the script will simply print the actions it would execute.

## Scene Requirements

The automation expects the HIP file to provide a few key nodes:

- A control node (for example `/obj/scbw_shot_controller1`) that exposes a
  `shot_id` parameter and optionally a `shot_json` string parameter for the full
  serialized payload. Any node can be used here – HDA authors typically bind the
  JSON payload to a Python Module or parameter interface that drives asset
  assembly.
- An `/out` container (default `/out/scbw_passes`) with one ROP per pass that you
  intend to render (`rgba`, `mask`, `depth`, etc.). The script automatically sets
  common output parameters such as `vm_picture` to ensure deterministic file
  naming.
- A packing ROP (default `/out/scbw_exr_packager`) that combines the individual
  passes into a multi-plane EXR. The script configures parameters like
  `vm_picture` and `scbw_pass_manifest` when present.

All node paths are configurable via CLI flags so studios can map the automation
onto their preferred network layout.

## Configuration Format

`params/pack.yaml` contains a `shots` list with entries similar to:

```yaml
- id: shot_1001
  palette: [[0.07,0.13,0.09], [0.12,0.2,0.14], [0.17,0.27,0.19]]
  export: { png: true, exr16: true }
```

Every entry is passed verbatim to Houdini (via `shot_json`) so your HDAs can
consume arbitrary metadata. The global keys `seed` and `image_size` at the root
of the file remain available for tools that need deterministic random sequences
or viewport sizing.

## Packaging Multi-Plane EXRs

When `export.exr16` is present on a shot, the packager sets the optional
`bit_depth` parameter to `16` for convenience (default `32`). Studios that
require additional metadata can extend their ROP to read the serialized pass
manifest stored in `scbw_pass_manifest`.

## Troubleshooting

- **`hou` import errors** – Ensure you are running `hython` from a Houdini
  installation that matches your pipeline. When running unit tests or quick
  validations in plain Python, add `--dry-run` so the script can operate without
  Houdini.
- **Missing nodes** – The CLI validates that the configured control node, render
  container, and EXR packer exist. Adjust the `--control-node`, `--render-root`,
  or `--exr-driver` arguments if your scene uses different paths.
- **Custom passes** – Override the default pass list via `--passes` to render
  additional AOVs. The script expects a child ROP under the render root for each
  supplied name.
