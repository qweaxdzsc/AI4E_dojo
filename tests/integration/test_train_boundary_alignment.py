"""非整除累积、回调异常重放与独立 EMA 产物的行为验收。"""

import pytest
import torch

from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.abilities.training.optimization import parameter_groups
from tests.integration.test_train_loop import Run


def step(model, batch):
    return {"loss": model(batch).square().mean()}


def test_drop_tail_without_forward(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    calls = []

    def track(model, batch):
        calls.append(float(batch.item()))
        return step(model, batch)

    report = fit(
        model,
        optimizer,
        lambda epoch: [torch.tensor([[float(i)]]) for i in [1, 2, 99]],
        track,
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 2, "accumulate": 2},
        contract={},
    )
    assert calls == [1.0, 2.0, 1.0, 2.0]
    assert report["updates"] == 2


def test_callback_failure_replays_epoch_exactly(tmp_path):
    torch.manual_seed(18)
    model = torch.nn.Linear(1, 1)
    initial = {k: v.clone() for k, v in model.state_dict().items()}
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    run = Run(tmp_path / "interrupted")

    def fail(event, **kwargs):
        if event == "update":
            raise RuntimeError("callback failed")

    with pytest.raises(RuntimeError, match="callback failed"):
        fit(
            model,
            optimizer,
            lambda epoch: [torch.ones(1, 1)] * 3,
            step,
            lambda: {"loss": 1.0},
            run,
            config={"max_epochs": 2},
            contract={},
            callbacks=[fail],
        )
    path = run.writer.run_dir / "checkpoints/latest.pt"
    state = torch.load(path, weights_only=False)
    assert state["epoch"] == state["updates"] == 0
    for key, value in initial.items():
        torch.testing.assert_close(value, state["model"][key], rtol=0, atol=0)
    fit(
        model,
        optimizer,
        lambda epoch: [torch.ones(1, 1)] * 3,
        step,
        lambda: {"loss": 1.0},
        Run(tmp_path / "resumed"),
        config={"max_epochs": 2, "resume": str(path)},
        contract={},
    )
    other = torch.nn.Linear(1, 1)
    other.load_state_dict(initial)
    fit(
        other,
        torch.optim.SGD(other.parameters(), lr=0.1),
        lambda epoch: [torch.ones(1, 1)] * 3,
        step,
        lambda: {"loss": 1.0},
        Run(tmp_path / "full"),
        config={"max_epochs": 2},
        contract={},
    )
    for k, v in model.state_dict().items():
        torch.testing.assert_close(v, other.state_dict()[k], rtol=0, atol=0)


def test_ema_persists_across_non_save_epoch_and_real_diagnostics(tmp_path):
    model = torch.nn.Linear(1, 1)
    run = Run(tmp_path)
    observed = []
    fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda epoch: [torch.ones(1, 1)],
        step,
        lambda: {"loss": 1.0},
        run,
        config={"max_epochs": 11, "stability": True},
        contract={},
        ema=MovingAverage(model, 0.9),
        callbacks=[lambda event, **kw: observed.append((event, kw))],
    )
    root = run.writer.run_dir / "checkpoints"
    assert torch.load(root / "ema_latest.pt", weights_only=False)["epoch"] == 10
    assert torch.load(root / "latest.pt", weights_only=False)["ema"] is not None
    assert not (root / "ema_last.pt").exists()
    diagnostics = observed[0][1]["result"]["diagnostics"]
    assert diagnostics["gradient_norm_before_clip"] > 0
    assert diagnostics["parameter_norm"] > 0
    groups = parameter_groups(model, weight_decay=0.05)
    assert groups[0]["params"] == [model.weight]
    assert groups[1]["params"] == [model.bias] and groups[1]["weight_decay"] == 0
