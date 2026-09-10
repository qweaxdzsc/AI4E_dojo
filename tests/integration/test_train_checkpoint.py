"""检查点冻结、语义冲突、随机状态和保存策略验收。"""

import copy
import random

import numpy as np
import pytest
import torch

from ai4e_core.abilities.training.checkpoint import capture, restore
from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.moving_average import MovingAverage


def test_snapshot_is_frozen_and_restores_rng(tmp_path):
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.AdamW(model.parameters())
    model(torch.ones(1, 2)).sum().backward()
    optimizer.step()
    ema = MovingAverage(model)
    contract = {"normalization": {"version": 1}}
    state = capture(model, optimizer, epoch=1, updates=1, best=1, contract=contract, ema=ema)
    expected = (random.random(), np.random.rand(), torch.rand(3))
    weights = copy.deepcopy(state["model"])
    with torch.no_grad():
        for p in model.parameters():
            p.add_(10)
    ema.update(model)
    contract["normalization"]["version"] = 2
    for name, value in weights.items():
        torch.testing.assert_close(state["model"][name], value)
    assert state["contract"]["normalization"]["version"] == 1
    path = tmp_path / "state.pt"
    torch.save(state, path)
    restore(path, model, optimizer, contract=state["contract"], ema=ema)
    actual = (random.random(), np.random.rand(), torch.rand(3))
    assert actual[:2] == expected[:2]
    torch.testing.assert_close(actual[2], expected[2])
    for name, value in weights.items():
        torch.testing.assert_close(model.state_dict()[name], value)


@pytest.mark.parametrize("field", ["normalization", "data", "sampling", "source", "objectives"])
def test_semantic_conflict_rejected_before_model_load(tmp_path, field):
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.AdamW(model.parameters())
    contract = {
        key: "original" for key in ["normalization", "data", "sampling", "source", "objectives"]
    }
    state = capture(model, optimizer, epoch=1, updates=1, best=1, contract=contract)
    path = tmp_path / "state.pt"
    torch.save(state, path)
    before = copy.deepcopy(model.state_dict())
    contract[field] = "changed"
    with pytest.raises(ValueError, match="冲突"):
        restore(path, model, optimizer, contract=contract)
    for name, value in before.items():
        torch.testing.assert_close(model.state_dict()[name], value)


def test_ema_absent_reinitializes_from_model(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.AdamW(model.parameters())
    path = tmp_path / "state.pt"
    torch.save(capture(model, optimizer, epoch=1, updates=1, best=1, contract={}), path)
    ema = MovingAverage(model)
    restore(path, model, optimizer, contract={}, ema=ema)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(ema.state[name], value)


def test_ema_present_without_object_rejected(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.AdamW(model.parameters())
    ema = MovingAverage(model)
    path = tmp_path / "state.pt"
    torch.save(capture(model, optimizer, epoch=1, updates=1, best=1, contract={}, ema=ema), path)
    with pytest.raises(ValueError, match="EMA"):
        restore(path, model, optimizer, contract={})


def test_best_requires_strict_improvement():
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    calls = []

    class Run:
        def checkpoint(self, label, payload):
            calls.append((label, payload["epoch"]))

    losses = iter([3.0, 3.0, 2.0])
    fit(
        model,
        optimizer,
        lambda _: [None],
        lambda m, _: {"loss": m(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": next(losses)},
        Run(),
        config={"max_epochs": 3},
        contract={},
    )
    assert calls == [
        ("latest", 1),
        ("best", 1),
        ("latest", 2),
        ("latest", 3),
        ("best", 3),
        ("last", 3),
    ]


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="需要真实 Apple GPU")
def test_mps_checkpoint_replays_random_sequence(tmp_path):
    model = torch.nn.Linear(2, 1).to("mps")
    optimizer = torch.optim.AdamW(model.parameters())
    state = capture(model, optimizer, epoch=1, updates=1, best=1, contract={})
    expected = torch.rand(16, device="mps").cpu()
    path = tmp_path / "mps.pt"
    torch.save(state, path)
    restore(path, model, optimizer, contract={})
    actual = torch.rand(16, device="mps").cpu()
    assert torch.equal(expected, actual)
