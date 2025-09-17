import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

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
