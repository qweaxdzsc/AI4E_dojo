"""PCNO实际入口配置、源码边界、完整案例与清单约定。"""

import ast
import json
from pathlib import Path

import pytest
import yaml

from ai4e_contrib.application.geothermal.pcno.configuration import load_configuration, validate

ROOT = Path(__file__).resolve().parents[2]


def test_case_has_explicit_stages_and_portable_configuration():
    cfg = load_configuration(ROOT / "recipes/pcno/config.yaml")
    assert cfg["train"]["updates"] == 21 and cfg["train"]["device"] == "cpu"
    for file in (ROOT / "recipes/pcno").glob("*.py"):
        assert file.read_bytes() == (ROOT / "examples/geothermal/pcno" / file.name).read_bytes()
    tree = ast.parse((ROOT / "recipes/pcno/train.py").read_text())
    calls = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "train_branch"
    ]
    assert len(calls) == 2
    assert not any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text())
    assert (
        next(c for c in manifest["cases"] if c["id"] == "geothermal.pcno")["type"] == "standalone"
    )
    assert (
        next(c for c in manifest["cases"] if c["id"] == "extension.pcno")["base_case"]
        == "geothermal.pcno"
    )


@pytest.mark.parametrize(
    "edit",
    [
        lambda c: c["train"].update(updates=0),
        lambda c: c["model"].update(temp_width=7),
        lambda c: c["infer"].update(device="mps"),
        lambda c: c["post"].update(capacity_factor=2),
        lambda c: c["inputs"]["train"].update(resume="ambiguous"),
    ],
)
def test_invalid_configuration_fails_at_public_loader(edit):
    cfg = yaml.safe_load((ROOT / "recipes/pcno/config.yaml").read_text())
    edit(cfg)
    with pytest.raises(ValueError):
        validate(cfg)
