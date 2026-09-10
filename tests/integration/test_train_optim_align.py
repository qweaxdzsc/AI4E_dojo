"""可换优化器、公开调度、累积、十轮 EMA 与缺键警告。"""

import warnings

import pytest
import torch

from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.abilities.training.optimization import Lion, build_optimizer
from ai4e_core.abilities.training.schedule import build_scheduler, total_updates
from ai4e_core.abilities.training.split import route
from tests.integration.test_train_loop import Run


def _step(network, batch):
    return {"loss": (network(batch["x"]) - batch["y"]).square().mean()}


def test_optimizer_kinds_and_invalid_name():
    model = torch.nn.Linear(1, 1)
    for name, expected in [
        ("adam", torch.optim.Adam),
        ("adamw", torch.optim.AdamW),
        ("lion", Lion),
    ]:
        optimizer = build_optimizer(name, model.parameters(), lr=1e-3, weight_decay=0.01)
        assert isinstance(optimizer, expected)
        assert optimizer.param_groups[0]["lr"] == 1e-3
    with pytest.raises(ValueError, match="未知优化器"):
        build_optimizer("soap", model.parameters(), lr=1e-3)


def test_warmup_cosine_rises_then_decays_and_resumes(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = build_optimizer("lion", model.parameters(), lr=1.0, weight_decay=0.0)
    scheduler = build_scheduler(
        "warmup_cosine", optimizer, total_updates=20, warmup_ratio=0.25, min_lr=0.1
    )
    rates = [optimizer.param_groups[0]["lr"]]
    for _ in range(20):
        optimizer.step()
        scheduler.step()
        rates.append(optimizer.param_groups[0]["lr"])
    assert rates[1] < rates[5]
    assert rates[-1] < rates[8]
    assert rates[-1] == pytest.approx(0.1, rel=1e-5)
    path = tmp_path / "sched.pt"
    torch.save(scheduler.state_dict(), path)
    other = torch.nn.Linear(1, 1)
    resumed = build_optimizer("lion", other.parameters(), lr=1.0)
    again = build_scheduler(
        "warmup_cosine", resumed, total_updates=20, warmup_ratio=0.25, min_lr=0.1
    )
    again.load_state_dict(torch.load(path, weights_only=False))
    assert again.get_last_lr()[0] == pytest.approx(rates[-1])


def test_constant_scheduler_and_missing_total_updates():
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.2)
    scheduler = build_scheduler("constant", optimizer, total_updates=3)
    optimizer.step()
    scheduler.step()
    assert optimizer.param_groups[0]["lr"] == 0.2
    with pytest.raises(ValueError, match="总有效更新"):
        build_scheduler("warmup_cosine", optimizer, total_updates=0)


def test_accumulate_two_makes_one_effective_update(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    batches = [{"x": torch.ones(1, 1), "y": torch.zeros(1, 1)}] * 4
    report = fit(
        model,
        optimizer,
        lambda _: iter(batches),
        _step,
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 1, "accumulate": 2},
        contract={},
    )
    assert report["updates"] == 2
    assert total_updates(2, 3, 2) == 2


def test_ema_saved_on_tenth_epoch_not_on_last(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    ema = MovingAverage(model, 0.5)
    run = Run(tmp_path)
    fit(
        model,
        optimizer,
        lambda _: [{"x": torch.ones(1, 1), "y": torch.zeros(1, 1)}],
        _step,
        lambda: {"loss": 1.0},
        run,
        config={"max_epochs": 10, "ema_save_every": 10},
        contract={},
        ema=ema,
    )
    latest = torch.load(run.writer.run_dir / "checkpoints/latest.pt", weights_only=False)
    last = torch.load(run.writer.run_dir / "checkpoints/last.pt", weights_only=False)
    assert latest["ema"] is not None
    assert last["ema"] is not None


def test_missing_and_extra_keys_warn_then_constraint_still_fails():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        routed = route({"keep": 1, "extra": 2}, ["keep", "absent"], kind="目标")
    assert routed == {"keep": 1}
    text = " ".join(str(item.message) for item in caught)
    assert "缺键" in text and "多键" in text
    from ai4e_core.abilities.constraint.supervised import supervised_mse

    with pytest.raises(KeyError):
        supervised_mse(
            {"p": torch.ones(1, 1)},
            {},
            [{"name": "p", "prediction": "p", "target": "p", "weight": 1}],
        )
