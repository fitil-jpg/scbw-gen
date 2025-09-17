import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from houdini import config as config_module
from houdini.config import ConfigError, load_pack_config
from houdini.generate_passes import _parse_arguments


def test_parse_arguments_prefers_yaml(monkeypatch, tmp_path):
    params_dir = tmp_path / "params"
    params_dir.mkdir()
    (params_dir / "pack.yaml").write_text("shots: []")

    monkeypatch.chdir(tmp_path)

    args = _parse_arguments([])

    assert args.config == Path("params/pack.yaml")
    assert not args.config_fallback_used


def test_parse_arguments_falls_back_to_json(monkeypatch, tmp_path):
    params_dir = tmp_path / "params"
    params_dir.mkdir()
    (params_dir / "pack.json").write_text("{\"shots\": []}")

    monkeypatch.chdir(tmp_path)

    args = _parse_arguments([])

    assert args.config == Path("params/pack.json")
    assert args.config_fallback_used


def test_load_pack_config_invalid_json(tmp_path):
    config_path = tmp_path / "pack.json"
    config_path.write_text("{invalid json}")

    with pytest.raises(ConfigError) as excinfo:
        load_pack_config(config_path)

    assert str(config_path) in str(excinfo.value)


@pytest.mark.skipif(config_module.yaml is None, reason="PyYAML not available")
def test_load_pack_config_invalid_yaml(tmp_path):
    config_path = tmp_path / "pack.yaml"
    config_path.write_text("foo: [bar")

    with pytest.raises(ConfigError) as excinfo:
        load_pack_config(config_path)

    assert str(config_path) in str(excinfo.value)
