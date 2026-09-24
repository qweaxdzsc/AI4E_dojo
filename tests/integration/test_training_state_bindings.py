"""独立周期与用户内存状态：真实更新、保存、恢复及拒绝原子性。"""

import copy

import pytest
import torch

from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.applications.base.iteration_training import train_model


class Session:
    def __init__(self, root):
        self.root, self.saved, self.payloads = root, [], []
        root.mkdir(parents=True, exist_ok=True)

    def checkpoint(self, name, payload, namespace):
        self.saved.append(payload["updates"])
        self.payloads.append(copy.deepcopy(payload))
        path = self.root / f"{name}.pt"
        torch.save(payload, path)
        return path

    def report(self, value, stage):
        pass


class State:
    def __init__(self):
        self.calls = 0
        self.fail_once = False

    def save(self):
        return {"calls": self.calls}

    def validate(self, state):
        if set(state) != {"calls"} or type(state["calls"]) is not int or state["calls"] < 0:
            raise ValueError("bad counter")

    def load(self, state):
        self.calls = state["calls"]
        if self.fail_once:
            self.fail_once = False
            raise RuntimeError("user load failure")

    def bindings(self):
        return {"counter": {"save": self.save, "validate": self.validate, "load": self.load}}


def setup(root):
    torch.manual_seed(42)
    model = torch.nn.Linear(1, 1)
    return (
        model,
        torch.optim.Adam(model.parameters(), lr=0.01),
        IterationStream(4, 2),
        Session(root),
    )


def run(parts, state=None, **options):
    model, optimizer, stream, session = parts

    def loss(current, values):
        if state:
            state.calls += 1
        return current(values).square().mean()

    return train_model(
        model,
        optimizer,
        stream,
        lambda ids: torch.ones(len(ids), 1),
        loss,
        session=session,
        contract={"test": "state"},
        namespace="train",
        state_bindings=state.bindings() if state else None,
        **options,
    )


def test_independent_cadence_and_evaluation_state_order(tmp_path):
    parts, state = setup(tmp_path), State()
    evaluations = []

    def evaluate(index, model):
        evaluations.append(index)
        state.calls = index * 100

    run(parts, state, updates=7, checkpoint_every=3, evaluate_every=2, evaluate=evaluate)
    assert evaluations == [2, 4, 6, 7]
    assert parts[3].saved == [3, 6, 7]
    assert [p["user_state"]["values"]["counter"]["calls"] for p in parts[3].payloads] == [
        201,
        600,
        700,
    ]


def test_dynamic_state_exact_resume(tmp_path):
    continuous, original = setup(tmp_path / "continuous"), State()
    run(continuous, original, updates=7)
    first, state = setup(tmp_path / "first"), State()
    checkpoint = run(first, state, updates=3)["checkpoint"]
    resumed, fresh = setup(tmp_path / "resume"), State()
    result = run(resumed, fresh, updates=7, resume=checkpoint)
    assert original.calls == fresh.calls == 7
    for name, value in continuous[0].state_dict().items():
        torch.testing.assert_close(resumed[0].state_dict()[name], value, rtol=0, atol=0)
    assert result["history"] == continuous[3].payloads[-1]["history"]
    assert resumed[2].state_dict()["offset"] == continuous[2].state_dict()["offset"]


@pytest.mark.parametrize(
    "defect", ["missing", "extra", "version", "bool_version", "invalid", "load_failure"]
)
def test_user_restore_rejection_keeps_model_stream_rng_and_user(tmp_path, defect):
    source, state = setup(tmp_path / "source"), State()
    path = run(source, state, updates=2)["checkpoint"]
    payload = torch.load(path, weights_only=False)
    if defect == "missing":
        del payload["user_state"]
    elif defect == "extra":
        payload["user_state"]["values"]["unknown"] = {}
    elif defect == "version":
        payload["user_state"]["version"] = 99
    elif defect == "bool_version":
        payload["user_state"]["version"] = True
    elif defect == "invalid":
        payload["user_state"]["values"]["counter"]["calls"] = -1
    torch.save(payload, path)
    parts, fresh = setup(tmp_path / "target"), State()
    fresh.calls = 81
    fresh.fail_once = defect == "load_failure"
    before = copy.deepcopy(parts[0].state_dict())
    rng = torch.get_rng_state().clone()
    order = parts[2].state_dict()
    with pytest.raises((ValueError, RuntimeError)):
        run(parts, fresh, updates=3, resume=path)
    assert fresh.calls == 81 and not parts[3].saved
    for name, value in before.items():
        torch.testing.assert_close(parts[0].state_dict()[name], value, rtol=0, atol=0)
    assert parts[1].state_dict()["state"] == {}
    torch.testing.assert_close(torch.get_rng_state(), rng, rtol=0, atol=0)
    torch.testing.assert_close(parts[2].state_dict()["rng"], order["rng"], rtol=0, atol=0)
    assert parts[2].offset == order["offset"]


def test_saved_user_state_cannot_be_silently_dropped(tmp_path):
    parts, state = setup(tmp_path / "first"), State()
    path = run(parts, state, updates=1)["checkpoint"]
    with pytest.raises(ValueError, match="名称"):
        run(setup(tmp_path / "second"), updates=2, resume=path)


def test_old_checkpoint_without_user_state_and_cancel_or_zero(tmp_path):
    first = setup(tmp_path / "first")
    path = run(first, updates=2)["checkpoint"]
    result = run(setup(tmp_path / "resume"), updates=3, resume=path)
    assert result["updates"] == 3
    parts = setup(tmp_path / "cancel")
    with pytest.raises(TimeoutError):
        run(parts, updates=10, cancelled=lambda: True)
    assert parts[3].saved == [0]
    assert parts[3].payloads[0]["status"] == "interrupted"
    empty = setup(tmp_path / "zero")
    run(empty, updates=0)
    assert empty[3].saved == [0]


def test_custom_legacy_iterate_equal_cadence_and_early_reject(tmp_path):
    from ai4e_core.abilities.training.iterations import fit_iterations

    called = []

    # 删除新增参数后的旧公开签名，不用**kwargs伪装兼容。
    import inspect

    def legacy(*args, **kwargs):
        called.append(True)
        assert "checkpoint_every" not in kwargs
        return fit_iterations(*args, **kwargs)

    legacy.__signature__ = inspect.signature(fit_iterations).replace(
        parameters=[
            p
            for n, p in inspect.signature(fit_iterations).parameters.items()
            if n != "checkpoint_every"
        ]
    )
    run(setup(tmp_path / "equal"), updates=2, checkpoint_every=2, iterate=legacy)
    assert called == [True]
    with pytest.raises(ValueError, match="自定义iterate"):
        run(
            setup(tmp_path / "different"),
            updates=2,
            checkpoint_every=3,
            evaluate_every=2,
            iterate=legacy,
        )
    assert called == [True]


def test_failed_rollback_still_attempts_all_user_bindings(tmp_path):
    from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration

    parts = setup(tmp_path)
    model, optimizer, stream, _ = parts
    values, calls = {"first": 1, "second": 2}, []

    def load(name, value):
        calls.append((name, value))
        values[name] = value
        if name == "first":
            raise RuntimeError("user cannot load")

    bindings = {
        name: {
            "save": lambda name=name: values[name],
            "validate": lambda value: None,
            "load": lambda value, name=name: load(name, value),
        }
        for name in values
    }
    payload = capture_iteration(
        model,
        optimizer,
        updates=0,
        stream=stream,
        contract={},
        history=[],
        state_bindings=bindings,
    )
    path = tmp_path / "state.pt"
    torch.save(payload, path)
    values.update(first=11, second=22)
    with pytest.raises(RuntimeError, match="部分内存状态无法回滚"):
        restore_iteration(
            path, model, optimizer, stream=stream, contract={}, state_bindings=bindings
        )
    assert calls == [("first", 1), ("first", 11), ("second", 22)]
    assert values == {"first": 11, "second": 22}
