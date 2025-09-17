import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from houdini.config import ConfigError, PackConfig, ShotParameters
from houdini.passes import PassAssembler


def test_process_shots_dry_run_without_exr_driver(tmp_path):
    config = PackConfig(path=tmp_path / "pack.yaml", data={"shots": []})
    assembler = PassAssembler(
        config=config,
        output_directory=tmp_path,
        exr_driver=None,
    )

    shot = ShotParameters(id="shot001", raw={"id": "shot001"})

    manifests = assembler.process_shots([shot], dry_run=True)

    assert len(manifests) == 1
    manifest = manifests[0]

    assert manifest.pass_paths
    assert manifest.packed_exr is None


def test_pack_config_shots_missing_id_raises(tmp_path):
    config = PackConfig(path=tmp_path / "pack.yaml", data={"shots": [{}]})

    with pytest.raises(ConfigError) as exc_info:
        _ = config.shots

    message = str(exc_info.value)
    assert "index 0" in message
    assert str(config.path) in message


def test_default_frame_range_isolation(tmp_path):
    config = PackConfig(path=tmp_path / "pack.yaml", data={"shots": []})

    assembler_one = PassAssembler(config=config, output_directory=tmp_path)
    assembler_two = PassAssembler(config=config, output_directory=tmp_path)

    assembler_one.frame_range.start = 10
    assembler_one.frame_range.end = 20

    assert assembler_one.frame_range.as_tuple() == (10, 20)
    assert assembler_two.frame_range.as_tuple() == (1, 1)
    assert assembler_one.frame_range is not assembler_two.frame_range
