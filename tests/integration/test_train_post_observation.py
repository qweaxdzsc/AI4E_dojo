"""AB-UPT 两轮训练观察与不观察的权重、输入和恢复数值对照。"""

import json
from pathlib import Path

import torch
import yaml

from tests.integration.test_recipe_explicit_equivalence import case
from tests.integration.test_recipe_extensions import script


def test_two_epoch_observation_does_not_change_training(tmp_path):
    folder, cfg = case(tmp_path, "shapenet_car_abupt")
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    checkpoints = []
    protocols = []
    for enabled in (False, True):
        cfg["run_root"] = str(tmp_path / f"runs-{enabled}")
        cfg["data_root"] = str(tmp_path / f"post-{enabled}")
        cfg["post"].update(
            snapshot_every=1 if enabled else 0,
            snapshot_sample="b",
            snapshot_split="test",
            figures=[],
            fields=["surface:pressure:scalar", "volume:velocity:magnitude"],
        )
        (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        result = script(folder)
        assert result.returncode == 0, result.stdout + result.stderr
        run = next(Path(cfg["run_root"]).iterdir())
        checkpoints.append(torch.load(run / "checkpoints/last.pt", weights_only=False))
        protocols.append(json.loads((run / "artifacts/training-protocol.json").read_text()))
        if enabled:
            report = json.loads((run / "artifacts/training.json").read_text())
            assert [r["epoch"] for r in report["observations"]] == [1, 2]
            for item in report["observations"]:
                output = json.loads(Path(item["result"]["manifest"]).read_text())
                assert output["origin"]["epoch"] == item["epoch"]
            assert len(list(Path(cfg["data_root"]).rglob("b/manifest.json"))) == 2
    for key in checkpoints[0]["model"]:
        torch.testing.assert_close(
            checkpoints[0]["model"][key], checkpoints[1]["model"][key], atol=0, rtol=0
        )
    assert protocols[0]["inputs"] == protocols[1]["inputs"]


def test_snapshot_restores_modes_rng_and_gradients_on_failure(monkeypatch):
    """失败发生在真实快照边界内，仍恢复混合模式、梯度和三类随机流。"""
    import random
    from types import SimpleNamespace

    import numpy as np
    import pytest

    from ai4e_core.applications.aero_cfd.infer import snapshot

    model = torch.nn.Sequential(torch.nn.Linear(3, 3), torch.nn.Dropout())
    model.train()
    model[0].eval()
    model(torch.ones(1, 3)).sum().backward()
    gradients = [p.grad.clone() for p in model.parameters()]
    modes = [m.training for m in model.modules()]
    torch.manual_seed(37)
    random.seed(38)
    np.random.seed(39)
    states = (torch.get_rng_state().clone(), random.getstate(), np.random.get_state())
    prepared = SimpleNamespace(
        config={"sampling": {"seed": 42}},
        view=SimpleNamespace(partitions={"test": ["s"]}, read=lambda *args: {}),
    )

    def fail(job):
        assert not model.training and not torch.is_grad_enabled()
        torch.rand(10)
        random.random()
        np.random.rand(10)
        raise RuntimeError("预测故障")

    monkeypatch.setattr(snapshot, "configure_prediction", fail)
    with pytest.raises(RuntimeError, match="预测故障"):
        snapshot.predict_snapshot(
            model, prepared=prepared, model_component=None, sample="s", split="test", origin={}
        )
    assert modes == [m.training for m in model.modules()]
    assert torch.is_grad_enabled()
    torch.testing.assert_close(states[0], torch.get_rng_state(), atol=0, rtol=0)
    assert states[1] == random.getstate()
    np.testing.assert_equal(states[2], np.random.get_state())
    for p, grad in zip(model.parameters(), gradients, strict=True):
        torch.testing.assert_close(p.grad, grad, atol=0, rtol=0)
