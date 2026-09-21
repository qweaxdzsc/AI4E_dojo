"""真实网络损失阶段、状态恢复及未来标签隔离。"""

import copy
import json
from pathlib import Path

import h5py
import numpy as np
import pytest
import torch
import yaml

from ai4e_contrib.application.datasets.gencp.cylinder import read_window
from ai4e_contrib.application.spatiotemporal_pde.pcno.configuration import validate
from ai4e_contrib.application.spatiotemporal_pde.pcno.objective import objective, ramp
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import construct, train_branch
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import digest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def tiny(tmp_path):
    path = tmp_path / "tiny.h5"
    x, y = np.meshgrid(
        np.arange(18, dtype=np.float32) / 18, np.arange(18, dtype=np.float32) / 18, indexing="ij"
    )
    time = np.arange(30, dtype=np.float32)[:, None, None] / 100
    with h5py.File(path, "w") as f:
        for key, value in {
            "velocity_x": x + time,
            "velocity_y": -y + time,
            "pressure": x + y + time,
            "sdf": np.ones((30, 18, 18), np.float32) * 10,
        }.items():
            f.create_dataset("data/" + key, data=value)
    record = {"id": "train/tiny", "path": str(path), "sha256": digest(path)}
    prepared = {
        "kind": "pcno-cylinder-prepared-v1",
        "case": "double_cylinder",
        "admission": "double-cylinder-source-staggered-20260921",
        "statistics": {"mean": [0, 0, 0, 0], "scale": [1, 1, 1, 1]},
        "gradient_scale": 0.1,
        "history": 3,
        "horizon": 4,
        "interval": 1,
        "splits": {"train": [record], "val": [record]},
        "train_starts": list(range(10)),
        "evaluation_starts": [0],
        "fields": ["u", "v", "p", "sdf"],
        "units": "test",
    }
    prep = tmp_path / "preparation.json"
    prep.write_text(json.dumps(prepared))
    cfg = yaml.safe_load((ROOT / "recipes/pcno_cylinder/config.yaml").read_text())
    cfg["model"].update(modes=[2, 2, 2], horizon=4)
    cfg["train"].update(updates=10, threads=2)
    cfg["pipeline"]["stages"] = ["train"]
    cfg["run_root"] = str(tmp_path / "runs")
    cfg["data_root"] = str(tmp_path / "data")
    return cfg, str(prep), prepared


def execute(cfg, prep, *, resume=None, stop=None):
    results = []

    def flow(c):
        result = train_branch(
            validate(c),
            prep,
            "fluid",
            "physics",
            session=run.TrainingRun(),
            resume=resume,
            stop_after=stop,
        )
        results.append(result)
        return result

    assert run.run_recipe(cfg, stages=flow, script=__file__) == 0
    return results[0]


def test_exact_recovery_across_warmup_and_ramp(tiny):
    cfg, prep, _ = tiny
    full = execute(cfg, prep)
    warm = execute(cfg, prep, stop=2)
    ramped = execute(cfg, prep, resume=warm["checkpoint"], stop=4)
    restored = execute(cfg, prep, resume=ramped["checkpoint"])
    a = torch.load(full["checkpoint"], weights_only=False)
    b = torch.load(restored["checkpoint"], weights_only=False)
    for key in a["model"]:
        torch.testing.assert_close(a["model"][key], b["model"][key], rtol=1e-5, atol=1e-6)
    assert a["history"] == b["history"]
    for key in a["optimizer"]["state"]:
        for field in a["optimizer"]["state"][key]:
            torch.testing.assert_close(
                a["optimizer"]["state"][key][field],
                b["optimizer"]["state"][key][field],
                rtol=1e-5,
                atol=1e-6,
            )
    assert b["stream"]["updates"] == 10
    bad = copy.deepcopy(cfg)
    bad["loss"]["divergence_weight"] = 0.2

    def rejected(c):
        train_branch(
            validate(c),
            prep,
            "fluid",
            "physics",
            session=run.TrainingRun(),
            resume=ramped["checkpoint"],
        )

    assert run.run_recipe(bad, stages=rejected, script=__file__) == 1


def test_active_physics_and_no_label_input(tiny):
    cfg, _, prepared = tiny
    model = construct(cfg, "fluid")
    sample = read_window(prepared, prepared["splits"]["train"][0], 0)
    sample["update"] = 10
    supervised = objective(prepared, cfg, "fluid", "supervised")(model, sample)
    physics = objective(prepared, cfg, "fluid", "physics")(model, sample)
    gradients = torch.autograd.grad(
        physics - supervised, tuple(model.parameters()), allow_unused=True
    )
    assert any(g is not None and g.abs().sum() > 0 for g in gradients)
    assert all(g is None or torch.isfinite(g).all() for g in gradients)
    before = model(sample["input"]).detach()
    sample["target"].fill_(100)
    sample["physical"].fill_(-100)
    torch.testing.assert_close(model(sample["input"]), before)
    assert ramp(2, 10) == 0 and ramp(4, 10) == 1
