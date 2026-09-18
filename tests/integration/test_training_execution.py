"""共享执行的有效计数、数值等价、恢复拒绝与局部更新顺序。"""

import copy

import pytest
import torch

from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.execution import execute
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.abilities.training.loop import fit
from tests.integration.test_train_loop import Run


def objective(model, values):
    return model(values).square().mean()


def test_budget_stops_before_fetch_and_skips_do_not_advance():
    consumed, boundaries = [], []

    def source():
        for i in range(8):
            consumed.append(i)
            yield i

    events = list(
        execute(source(), lambda i, x: (x, i % 2 == 1), updates=2, before=boundaries.append)
    )
    assert consumed == [0, 1, 2, 3]
    assert [e.updates for e in events] == [0, 1, 1, 2]
    assert boundaries == [0, 0, 1, 1]
    with pytest.raises(TypeError):
        list(execute([1], lambda i, x: (x, 1)))


def test_epoch_and_update_budget_have_same_parameter_trajectory(tmp_path):
    torch.manual_seed(31)
    initial = torch.nn.Linear(2, 1)
    data = torch.arange(12, dtype=torch.float32).reshape(6, 2) / 12
    trajectories = []
    for unit in ("epoch", "updates"):
        model = copy.deepcopy(initial)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        trace = []
        if unit == "epoch":
            fit(
                model,
                optimizer,
                lambda epoch: data.split(2),
                lambda m, x: {"loss": objective(m, x)},
                lambda: {"loss": 1.0},
                Run(tmp_path / unit),
                config={"max_epochs": 2},
                contract={},
                callbacks=[
                    lambda event, trace=trace, model=model, **kw: (
                        trace.append(copy.deepcopy(model.state_dict()))
                        if event == "update"
                        else None
                    )
                ],
            )
        else:

            class Stream:
                offset = 0

                def next(self):
                    ids = torch.arange(self.offset, self.offset + 2)
                    self.offset = (self.offset + 2) % 6
                    return ids

            fit_iterations(
                model,
                optimizer,
                Stream(),
                lambda ids: data[ids],
                objective,
                updates=6,
                after_update=lambda i, m, trace=trace: trace.append(copy.deepcopy(m.state_dict())),
            )
        trajectories.append(trace)
    assert len(trajectories[0]) == len(trajectories[1]) == 6
    for a, b in zip(*trajectories):
        for key in a:
            torch.testing.assert_close(a[key], b[key], rtol=0, atol=0)


def test_custom_skip_preserves_scheduler_ema_and_callback_order():
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    events, attempts = [], []

    def step(m, opt, values, loss, *, max_grad_norm):
        attempts.append(len(attempts))
        if len(attempts) == 1:
            return 0.0, False
        opt.zero_grad()
        value = loss(m, values)
        value.backward()
        opt.step()
        events.append("optimizer")
        return float(value.detach()), True

    class EMA:
        def update(self, model):
            events.append("ema")

    class Scheduler:
        def step(self):
            events.append("scheduler")

    checkpoints = []
    losses = fit_iterations(
        model,
        optimizer,
        IterationStream(2, 1),
        lambda ids: torch.ones(1, 1),
        objective,
        updates=2,
        update_step=step,
        ema=EMA(),
        scheduler=Scheduler(),
        after_update=lambda i, m: events.append("after"),
        checkpoint=lambda i, h, s: checkpoints.append((i, len(h), s)),
    )
    assert len(attempts) == 3 and len(losses) == 2
    assert events == ["optimizer", "ema", "scheduler", "after"] * 2
    assert checkpoints == [(2, 2, "complete")]
    with pytest.raises(ValueError, match="不能叠加"):
        fit_iterations(
            model,
            optimizer,
            IterationStream(2, 1),
            lambda x: x,
            objective,
            updates=1,
            update_step=step,
            accumulate=2,
        )


def test_accumulation_drops_epoch_tail_without_objective_call():
    model = torch.nn.Linear(1, 1)
    seen = []
    stream = IterationStream(3, 1, seed=2)

    def loss(m, values):
        seen.append(int(values.item()))
        return objective(m, values.float().reshape(1, 1))

    fit_iterations(
        model,
        torch.optim.SGD(model.parameters(), lr=0.01),
        stream,
        lambda x: x,
        loss,
        updates=3,
        accumulate=2,
        epoch_end=lambda s: s.offset == s.count,
    )
    assert len(seen) == 6
    assert stream.offset == 2  # 第三轮只取完成预算所需的两批，不额外读尾批。


def test_finite_stream_does_not_claim_completed_budget():
    class Stream:
        values = iter([torch.ones(1, 1)])

        def next(self):
            return next(self.values)

    model = torch.nn.Linear(1, 1)
    saved = []
    with pytest.raises(ValueError, match="耗尽"):
        fit_iterations(
            model,
            torch.optim.SGD(model.parameters(), lr=0.1),
            Stream(),
            lambda x: x,
            objective,
            updates=2,
            checkpoint=lambda i, h, s: saved.append((i, s)),
        )
    assert saved == [(1, "interrupted")]


def test_invalid_resume_does_not_mutate_stream_or_model(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    stream = IterationStream(4, 1)
    stream.next()
    state = capture_iteration(
        model, optimizer, updates=0, stream=stream, contract={"x": 1}, history=[]
    )
    path = tmp_path / "state.pt"
    torch.save(state, path)
    target = IterationStream(4, 1)
    initial = copy.deepcopy(model.state_dict())
    with pytest.raises(ValueError, match="语义冲突"):
        restore_iteration(path, model, optimizer, stream=target, contract={"x": 2})
    assert target.offset == 4
    for key in initial:
        torch.testing.assert_close(model.state_dict()[key], initial[key], rtol=0, atol=0)


@pytest.mark.parametrize("reduction", ["mean", "sum"])
def test_accumulation_matches_explicit_gradient_reference(reduction):
    torch.manual_seed(13)
    model = torch.nn.Linear(1, 1)
    reference = copy.deepcopy(model)
    data = torch.arange(1, 5, dtype=torch.float32).reshape(4, 1)
    stream = IterationStream(4, 1, seed=4)
    expected_stream = copy.deepcopy(stream)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    expected_optimizer = torch.optim.SGD(reference.parameters(), lr=0.01)
    expected_history = []
    for _ in range(3):
        expected_optimizer.zero_grad()
        losses = []
        for _ in range(2):
            loss = objective(reference, data[expected_stream.next()])
            losses.append(float(loss.detach()))
            (loss / 2 if reduction == "mean" else loss).backward()
        expected_optimizer.step()
        expected_history.append(sum(losses) / 2)
    actual = fit_iterations(
        model,
        optimizer,
        stream,
        lambda ids: data[ids],
        objective,
        updates=3,
        accumulate=2,
        accumulation_reduction=reduction,
        max_grad_norm=None,
    )
    assert actual == expected_history
    for key, value in reference.state_dict().items():
        torch.testing.assert_close(value, model.state_dict()[key], rtol=0, atol=0)


class ControlledScaler:
    """只模拟一次溢出及持久化协议；不声称覆盖 CUDA 硬件。"""

    def __init__(self):
        self.value, self.attempts = 8, 0

    def get_scale(self):
        return self.value

    def scale(self, loss):
        return loss

    def unscale_(self, optimizer):
        pass

    def step(self, optimizer):
        if self.attempts:
            optimizer.step()

    def update(self):
        if not self.attempts:
            self.value /= 2
        self.attempts += 1

    def state_dict(self):
        return {"value": self.value, "attempts": self.attempts}

    def load_state_dict(self, state):
        self.value, self.attempts = state["value"], state["attempts"]


@pytest.mark.parametrize("precision", [False, True])
def test_iteration_assembly_accumulation_resume_and_overflow(tmp_path, monkeypatch, precision):
    from contextlib import nullcontext

    from ai4e_core.abilities.training.moving_average import MovingAverage
    from ai4e_core.applications.base.iteration_training import train_model
    from tools.verification.training_execution import _equal

    monkeypatch.setattr(torch, "autocast", lambda _: nullcontext())
    torch.manual_seed(19)
    initial = torch.nn.Linear(1, 1)

    class Session(Run):
        def checkpoint(self, label, payload, *, namespace):
            return self.writer.write_checkpoint(label, payload)

    def train(name, updates, resume=None, **options):
        model = copy.deepcopy(initial)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        stream = IterationStream(5, 1, seed=5)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)
        result = train_model(
            model,
            optimizer,
            stream,
            lambda ids: ids.float().reshape(-1, 1),
            objective,
            updates=updates,
            session=Session(tmp_path / name),
            contract={"strategy": "default"},
            namespace="train",
            scheduler=scheduler,
            ema=MovingAverage(model),
            resume=resume,
            accumulate=2,
            scaler=ControlledScaler() if precision else None,
            epoch_end=lambda s: s.offset == s.count,
            **options,
        )
        return result, torch.load(result["checkpoint"], weights_only=False)

    _, full = train("full", 4)
    first, _ = train("first", 2)
    _, resumed = train("resumed", 4, first["checkpoint"])
    for key in (
        "model",
        "optimizer",
        "scheduler",
        "ema",
        "scaler",
        "stream",
        "history",
        "torch_rng",
    ):
        _equal(full[key], resumed[key])
    assert full["scheduler"]["last_epoch"] == 4
    if precision:
        assert full["scaler"] == {"value": 4, "attempts": 5}


def test_strategy_contract_rejected_before_mutation(tmp_path):
    from ai4e_core.applications.base.iteration_training import train_model

    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.Adam(model.parameters())
    stream = IterationStream(4, 1)
    state = capture_iteration(
        model, optimizer, updates=0, stream=stream, contract={"strategy": "old"}, history=[]
    )
    state["model"]["weight"].fill_(100)
    state["algorithm_state"] = {}
    path = tmp_path / "old.pt"
    torch.save(state, path)
    before = copy.deepcopy(model.state_dict())
    with pytest.raises(ValueError, match="语义冲突"):
        train_model(
            model,
            optimizer,
            stream,
            lambda x: x,
            objective,
            updates=1,
            session=None,
            contract={"strategy": "new"},
            namespace="train",
            resume=path,
        )
    for key in before:
        torch.testing.assert_close(model.state_dict()[key], before[key], rtol=0, atol=0)
    assert not optimizer.state and stream.offset == 4
