"""经典案例资源与本地重组组件物化检查；不创建优化器或推进训练。"""

import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from ai4e_task.templates import resources

from ai4e_contrib.application.classic_networks.binding import construct
from ai4e_contrib.application.classic_networks.configuration import load_configuration
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays

ROOT = Path(__file__).resolve().parents[2]
VARIANTS = ("resunet", "unet_transformer", "cnn_rnn")
CASES = ("darcy", "shapenet_volume", "double_cylinder")


@pytest.fixture(autouse=True)
def source_resources(monkeypatch):
    """使用当前源码资源目录，独立wheel运行另由主控验证。"""
    monkeypatch.setattr(resources, "resource_root", lambda: ROOT)
    threads = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(threads)


def test_standalone_sources_and_catalog_identity():
    cases = resources.list_examples()
    assert len({case["id"] for case in cases}) == len(cases)
    by_id = {case["id"]: case for case in cases}
    for name in CASES:
        case = by_id[f"classic_networks.{name}"]
        assert resources.check_example(case["id"])["ok"]
        for file in case["shared_stage_files"]:
            assert (ROOT / "examples" / case["path"] / file).read_bytes() == (
                ROOT / "recipes" / case["recipe_source"] / file
            ).read_bytes()


@pytest.mark.parametrize("name", VARIANTS)
def test_extension_materializes_local_network_and_fixed_consumer(tmp_path, monkeypatch, name):
    """复制后通过实际构造连接前向，再保存读回派生数组；无优化器更新。"""
    case_id = f"recipe_extensions.network_composition.{name}"
    assert resources.check_example(case_id)["ok"]
    target = tmp_path / name
    receipt = resources.copy_example(case_id, target)
    base = "double_cylinder" if name == "cnn_rnn" else "darcy"
    assert receipt["base_case"] == f"classic_networks.{base}"
    assert all(
        (target / f"{stage}.py").is_file()
        for stage in ("rawprep", "trainprep", "train", "infer", "post")
    )
    assert (target / "pipeline.py").is_file()
    root_components = ROOT / "examples/recipe_extensions/network_composition"
    for file in (f"{name}.py", "user_outputs.py"):
        assert (target / file).read_bytes() == (root_components / file).read_bytes()
    provenance = json.loads((target / ".dojo-provenance.json").read_text())
    assert provenance["case_id"] == case_id
    cfg = load_configuration(target / "config.yaml")
    assert cfg["dataset"]["case"] == base
    assert cfg["train"]["sample_points"] is None
    assert cfg["components"]["model"] == f"{name}.build_model"
    monkeypatch.syspath_prepend(str(target))
    previous = {key: sys.modules.pop(key, None) for key in (name, "user_outputs")}
    try:
        model = construct(cfg).eval()
        shape = (1, 3, 7, 9, 4) if name == "cnn_rnn" else (1, 17, 19, 3)
        with torch.no_grad():
            prediction = model(torch.randn(shape))
        assert prediction.shape == ((1, 7, 9, 4) if name == "cnn_rnn" else (1, 17, 19, 1))
        assert torch.isfinite(prediction).all()
        local = importlib.import_module(name)
        assert Path(local.__file__).resolve().parent == target.resolve()
        user_outputs = importlib.import_module("user_outputs")
        payload = {"prediction": prediction.numpy(), "valid": np.ones(prediction.shape[:-1], bool)}
        additions, declarations = user_outputs.derive(payload, {})
        path = save_arrays(
            tmp_path / "fixed",
            {**payload, **additions},
            kind="composition-example",
            metadata={"derived": declarations},
        )
        record, arrays = read_arrays(path, kind="composition-example")
        consumed = user_outputs.consume(arrays, record["metadata"]["derived"])
        assert consumed["prediction_norm"]["finite"]
        assert consumed["prediction_norm"]["unit"] == "unknown"
    finally:
        for key, value in previous.items():
            sys.modules.pop(key, None)
            if value is not None:
                sys.modules[key] = value
