"""训练机制验收；小线性模型仅验证循环，不代替正式 AB-UPT 门禁。"""

import copy

import pytest
import torch

from ai4e_core.abilities.constraint.supervised import supervised_mse
from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.run.writer import RunWriter


class Run:
    def __init__(self, root):
        self.writer = RunWriter.create(root, nested=False)

    def checkpoint(self, label, payload):
        return self.writer.write_checkpoint(label, payload)


def test_epoch_resume_and_updates(tmp_path):
    torch.manual_seed(3)
    initial = torch.nn.Linear(2, 1).state_dict()
    batches = [{"x": torch.ones(1, 2), "y": torch.zeros(1, 1)}] * 3

    def execute(root, epochs, resume=None):
        model = torch.nn.Linear(2, 1)
        model.load_state_dict(copy.deepcopy(initial))
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.02)
        ema = MovingAverage(model)
        run = Run(root)
        calls = []

        def step(network, batch):
            calls.append(1)
            return {"loss": (network(batch["x"]) - batch["y"]).square().mean()}

        report = fit(
            model,
            optimizer,
            lambda _: iter(batches),
            step,
            lambda: {"loss": float(model(torch.ones(1, 2)).detach().square().mean())},
            run,
            config={"max_epochs": epochs, "resume": resume},
            contract={"data": "fixed"},
            ema=ema,
        )
        return model, ema, report, run, calls

    full, _full_ema, report, _, calls = execute(tmp_path / "full", 2)
    _, _, _, one, _ = execute(tmp_path / "one", 1)
    resumed, _resumed_ema, result, _, calls2 = execute(
        tmp_path / "resume", 2, one.writer.run_dir / "checkpoints/latest.pt"
    )
    assert report["updates"] == result["updates"] == 6
    assert len(calls) == 6 and len(calls2) == 3
    for key, value in full.state_dict().items():
        torch.testing.assert_close(value, resumed.state_dict()[key], rtol=1e-5, atol=1e-6)


def test_loss_rejects_broadcast_and_weights():
    terms = [{"name": "p", "prediction": "p", "target": "p", "weight": 1}]
    with pytest.raises(ValueError, match="形状"):
        supervised_mse({"p": torch.ones(2, 1)}, {"p": torch.zeros(2)}, terms)
    result = supervised_mse({"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, terms)
    assert result["loss"] == 1


def test_checkpoint_failure_preserves_old(tmp_path, monkeypatch):
    writer = RunWriter.create(tmp_path, nested=False)
    target = writer.write_checkpoint("latest", {"x": torch.ones(1)})

    def fail(*args, **kwargs):
        raise OSError("injected")

    monkeypatch.setattr(torch, "save", fail)
    with pytest.raises(OSError):
        writer.write_checkpoint("latest", {"x": torch.zeros(1)})
    assert torch.load(target, weights_only=True)["x"].item() == 1


def test_training_bridge_preserves_effective_config(tmp_path):
    from ai4e_core.run.session import CURRENT
    from ai4e_core.run.training import TrainingRun

    writer = RunWriter.create(tmp_path, nested=False)
    config = {"train": {"max_epochs": 2}}
    token = CURRENT.set({"writer": writer, "flags": {"dry_run": False}, "config": config})
    try:
        path = TrainingRun().checkpoint("latest", {"model": {}})
        assert torch.load(path, weights_only=True)["effective_config"] == config
    finally:
        CURRENT.reset(token)


@pytest.mark.parametrize("skip", [False, True])
def test_precision_update_order_and_overflow_counters(tmp_path, monkeypatch, skip):
    """可控缩放器检验协议与跳步；不冒充 CUDA 硬件验收。"""
    from contextlib import nullcontext

    events = []
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    ema = MovingAverage(model)
    before = copy.deepcopy(ema.state)
    real_clip = torch.nn.utils.clip_grad_norm_

    def clip(*args, **kwargs):
        events.append("clip")
        return real_clip(*args, **kwargs)

    class Scaler:
        value = 8

        def get_scale(self):
            return self.value

        def scale(self, loss):
            events.append("scale")
            return loss

        def unscale_(self, optimizer):
            events.append("unscale")

        def step(self, optimizer):
            events.append("step")
            if not skip:
                optimizer.step()

        def update(self):
            events.append("update")
            if skip:
                self.value /= 2

        def state_dict(self):
            return {"scale": self.value}

    monkeypatch.setattr(torch, "autocast", lambda _: nullcontext())
    monkeypatch.setattr(torch.nn.utils, "clip_grad_norm_", clip)
    report = fit(
        model,
        optimizer,
        lambda _: [None],
        lambda m, _: {"loss": m(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 1},
        contract={},
        ema=ema,
        scaler=Scaler(),
    )
    assert events == ["scale", "unscale", "clip", "step", "update"]
    assert report["updates"] == (0 if skip else 1)
    if skip:
        for name, value in before.items():
            torch.testing.assert_close(ema.state[name], value)
    else:
        assert any(not torch.equal(ema.state[k], v) for k, v in before.items())


def test_initial_weights_freezing_and_two_weighted_losses(tmp_path):
    from ai4e_core.abilities.modeling.weights import initialize_weights

    model = torch.nn.Sequential(torch.nn.Linear(2, 2), torch.nn.Linear(2, 1))
    path = tmp_path / "weights.pt"
    torch.save(model.state_dict(), path)
    other = copy.deepcopy(model)
    initialize_weights(other, path=path, freeze=["0"])
    assert not other[0].weight.requires_grad and other[1].weight.requires_grad
    with pytest.raises(ValueError, match="匹配"):
        initialize_weights(other, freeze=["missing"])
    with pytest.raises(ValueError, match="可训练"):
        initialize_weights(other, freeze=["1"])
    terms = [
        {"name": key, "prediction": key, "target": key, "weight": weight}
        for key, weight in [("p", 2), ("v", 3)]
    ]
    result = supervised_mse(
        {"p": torch.ones(2, 1), "v": 2 * torch.ones(2, 3)},
        {"p": torch.zeros(2, 1), "v": torch.zeros(2, 3)},
        terms,
    )
    assert result["loss"].item() == 14


def test_device_and_clip_validation(monkeypatch):
    from ai4e_core.abilities.training.optimization import resolve_device, update

    assert resolve_device("cpu").type == "cpu"
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: True)
    assert resolve_device("auto").type == "cuda"
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert resolve_device("auto").type == "mps"
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)
    with pytest.warns(UserWarning, match="回退到 CPU"):
        assert resolve_device("auto").type == "cpu"
    for device in ["cuda", "mps", "meta"]:
        with pytest.raises(ValueError):
            resolve_device(device)
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    for clip in [0, -1, float("inf")]:
        with pytest.raises(ValueError, match="裁剪"):
            update(model, optimizer, None, None, clip=clip)


def test_log_frequency_preserves_history_and_final_event(tmp_path, monkeypatch):
    from ai4e_core.abilities.training import loop

    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append(kwargs))
    model = torch.nn.Linear(1, 1)
    report = loop.fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: [None],
        lambda m, _: {"loss": m(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 3, "log_every": 2},
        contract={},
    )
    assert [event["轮次"] for event in events] == [2, 3]
    assert len(report["history"]) == 3
    assert all(not isinstance(value, torch.Tensor) for event in events for value in event.values())


def test_disabled_evaluation_keeps_last_without_best(tmp_path):
    """关闭训练期评价同时关闭重复评价，不虚构 best 权重。"""
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    run = Run(tmp_path)

    def forbidden():
        raise AssertionError("训练期间禁止消费测试集")

    report = fit(
        model,
        optimizer,
        lambda _: iter([torch.ones(1, 1)]),
        lambda network, batch: {"loss": network(batch).square().mean()},
        forbidden,
        run,
        config={"max_epochs": 1, "evaluation_enabled": False},
        contract={},
        evaluate_repeat=forbidden,
    )
    assert report["history"][0]["evaluation"] is None
    assert (run.writer.run_dir / "checkpoints/last.pt").exists()
    assert not (run.writer.run_dir / "checkpoints/best.pt").exists()
