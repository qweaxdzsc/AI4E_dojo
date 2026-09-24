"""JOREK 用户组件的公开连接与保存读回回归，不冒充完整训练证据。"""

import copy
import importlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "tools/verification/dojo_validity/rmhd/recipe_probe/overlay"


@pytest.fixture
def components(monkeypatch):
    monkeypatch.syspath_prepend(str(OVERLAY))
    return importlib.import_module("local_training")


def import_overlay(monkeypatch, name):
    """隔离不同 recipe 复用的顶层模块名，避免测试收集顺序污染。"""
    monkeypatch.syspath_prepend(str(OVERLAY))
    for module in ("configuration", "infer", "post", name):
        monkeypatch.delitem(__import__("sys").modules, module, raising=False)
    return importlib.import_module(name)


def test_window_stream_keeps_tail_and_recovers_inside_epoch(components):
    stream = components.WindowStream(70, 16, seed=42)
    rng = np.random.Generator(np.random.PCG64(42))
    starts, order = rng.integers(0, 162, size=70), rng.permutation(70)
    batches = [stream.next() for _ in range(2)]
    state = copy.deepcopy(stream.state_dict())
    continued = [stream.next() for _ in range(4)]
    resumed = components.WindowStream(70, 16, seed=42)
    resumed.load_state_dict(state)
    assert [resumed.next() for _ in range(4)] == continued
    first_epoch = batches + continued[:3]
    assert [len(x) for x in first_epoch] == [16, 16, 16, 16, 6]
    assert [item for batch in first_epoch for item in batch] == [
        (int(i), int(starts[i])) for i in order
    ]
    assert state["cursor"] == 32
    with pytest.raises(ValueError, match="游标"):
        resumed.load_state_dict({**state, "cursor": 71})


def test_block_rollout_keeps_future_gradient(components):
    class Scale(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.tensor(0.9))

        def forward(self, x):
            return x[:, -30:] * self.weight

    model = Scale()
    history = torch.ones(1, 10, 6, 100, 100)
    prediction = components.predict_blocks(model, history)
    torch.testing.assert_close(prediction[:, -5:], torch.full((1, 5, 6, 100, 100), 0.9**8))
    prediction[:, -5:].mean().backward()
    torch.testing.assert_close(model.weight.grad, torch.tensor(8 * 0.9**7), rtol=1e-5, atol=1e-6)


def test_recipe_config_handles_launch_container_and_components(monkeypatch):
    module = import_overlay(monkeypatch, "configuration")
    raw = {
        "science": {"fields": ["Psi", "u", "zj", "omega", "rho", "T"], "history": 10, "future": 40},
        "train": {"updates": 5, "batch_size": 16},
    }
    result = module.validate(OmegaConf.create(raw))
    assert isinstance(result, dict) and isinstance(result["science"]["fields"], list)
    assert module.component("torch.optim.Adam") is torch.optim.Adam
    with pytest.raises(ValueError, match="六场"):
        module.validate({**raw, "science": {**raw["science"], "fields": ["u"]}})


def test_fixed_post_reads_arrays_without_a_model(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(OVERLAY))
    module = importlib.import_module("local_post")
    from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
    from ai4e_core.abilities.data.save.arrays import save_json

    target = np.ones((2, 3, 6, 2, 2), dtype=np.float64)
    prediction = target * 1.25
    path = save_arrays(
        tmp_path / "predictions",
        {"prediction": prediction, "target": target},
        kind="rmhd-validation-predictions-v1",
        metadata={},
    )
    save_json(
        tmp_path / "evaluation.json", {"arrays": path, "rows": np.full((2, 6), 0.25).tolist()}
    )
    report = module.fixed_errors(tmp_path / "evaluation.json", tmp_path / "post")
    assert report["recomputed_mean_relative_l2"] == 0.25
    _, data = read_arrays(report["arrays"], kind="rmhd-diagnostics-v1")
    np.testing.assert_array_equal(data["relative_l2"], 0.25)


def test_infer_post_public_asset_handoff(tmp_path, monkeypatch):
    """以真实运行写入器贯通资产枚举、冻结数组与独立后处理。"""
    infer = import_overlay(monkeypatch, "infer")
    post = import_overlay(monkeypatch, "post")
    from ai4e_core import run
    from ai4e_core.abilities.data.save.array_manifest import save_arrays
    from ai4e_core.run.session import run_recipe

    class ValidationFixture:
        def __init__(self, *args):
            pass

        def evaluate(self, model, *, output):
            assert isinstance(model, torch.nn.Linear)
            target = np.ones((1, 3, 6, 2, 2), dtype=np.float64)
            path = save_arrays(
                output,
                {"prediction": target * 1.25, "target": target},
                kind="rmhd-validation-predictions-v1",
                metadata={},
            )
            return {"arrays": path, "rows": [[0.25] * 6]}

    monkeypatch.setattr(infer, "Validation", ValidationFixture)
    monkeypatch.setattr(infer, "latency", lambda *args: {"fixture": True})
    checkpoint = tmp_path / "weights.pt"
    torch.save(torch.nn.Linear(1, 1).state_dict(), checkpoint)
    preparation = tmp_path / "preparation.json"
    preparation.write_text(
        json.dumps({"validation": [], "statistics": {"mean": [0] * 6, "std": [1] * 6}})
    )
    cfg = {
        "run_root": str(tmp_path / "runs"),
        "data_root": str(tmp_path / "data"),
        "pipeline": {"stages": ["infer", "post"]},
        "model": {"in_features": 1, "out_features": 1},
        "infer": {"device": "cpu"},
        "components": {
            "model": "torch.nn.Linear",
            "advance": "local_training.direct_prediction",
            "post": "local_post.fixed_errors",
        },
        "inputs": {
            "infer": {"checkpoint": str(checkpoint), "preparation": str(preparation)},
            "post": {"predictions": None},
        },
    }

    def pipeline(cfg):
        results = run.stage("infer", infer.infer, cfg)
        run.stage("post", post.post, cfg, results)

    assert run_recipe(cfg, stages=pipeline, script=OVERLAY / "infer.py") == 0
    result_path = next((tmp_path / "runs").glob("*/summary.json"))
    result = json.loads(result_path.read_text())
    assert result["research_status"] == "completed"
    assert result["reports"]["post"]["recomputed_mean_relative_l2"] == 0.25
    assets = json.loads((result_path.parent / "artifacts/assets.json").read_text())["items"]
    assert set(assets) == {"infer/predictions", "post/diagnostics"}
    assert assets["post/diagnostics"]["dependency_digests"]
