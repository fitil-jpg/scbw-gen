import logging
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from houdini import config as config_module
from houdini.config import ConfigError, load_pack_config
from houdini.generate_passes import _parse_arguments, main
from houdini.passes import HoudiniNotAvailableError


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


def test_load_pack_config_falls_back_when_yaml_unavailable(monkeypatch, tmp_path, caplog):
    yaml_config = tmp_path / "pack.yaml"
    yaml_config.write_text("shots: []")
    json_config = tmp_path / "pack.json"
    json_config.write_text("{\"shots\": []}")

    monkeypatch.setattr(config_module, "yaml", None)
    caplog.set_level(logging.INFO, logger="houdini.config")

    config = load_pack_config(yaml_config)

    assert config.path == json_config
    assert config.data == {"shots": []}
    assert any("falling back" in record.getMessage() for record in caplog.records)


@pytest.mark.skipif(config_module.yaml is None, reason="PyYAML not available")
def test_load_pack_config_invalid_yaml(tmp_path):
    config_path = tmp_path / "pack.yaml"
    config_path.write_text("foo: [bar")

    with pytest.raises(ConfigError) as excinfo:
        load_pack_config(config_path)

    assert str(config_path) in str(excinfo.value)


def test_main_handles_houdini_not_available(monkeypatch, caplog, tmp_path):
    config_path = tmp_path / "pack.yaml"
    config_path.write_text("shots: []")

    fake_config = object()

    monkeypatch.setattr("houdini.generate_passes.load_pack_config", lambda _: fake_config)

    def _raise_houdini_error(*args, **kwargs):
        raise HoudiniNotAvailableError("Houdini is not accessible")

    monkeypatch.setattr("houdini.generate_passes._render", _raise_houdini_error)

    caplog.set_level(logging.INFO)

    exit_code = main(["--config", str(config_path)])

    assert exit_code == 4
    assert any("Houdini is not accessible" in record.getMessage() for record in caplog.records)
    assert "Traceback" not in caplog.text
