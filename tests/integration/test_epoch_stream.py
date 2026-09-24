"""有限记录收批：独立参考、轮界/轮内恢复、失败原子性和真实训练交接。"""

import copy
import importlib
import importlib.util
import os
from pathlib import Path

import numpy as np
import pytest
import torch

from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.run.writer import RunWriter


def capability(name):
    """源码与独立 wheel 验收复用相同测试，不重装工作环境。"""
    if os.environ.get("DOJO_CAPABILITY_INSTALLED") == "1":
        return importlib.import_module(f"ai4e_core.abilities.training.{name}")
    path = Path(__file__).resolve().parents[2] / "packages/ai4e-core/abilities/training"
    spec = importlib.util.spec_from_file_location(f"audit_{name}", path / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def stream_type():
    return capability("epoch_stream").EpochBatchStream


@pytest.mark.parametrize("drop_last,sizes", [(False, [16, 16, 16, 16, 6]), (True, [16] * 4)])
def test_tail_identity_epoch_boundary_and_no_prefetch(stream_type, drop_last, sizes):
    calls = []

    def records(rng, epoch):
        calls.append(epoch)
        return list(range(70))

    stream = stream_type(records, 16, drop_last=drop_last, source_contract={"n": 70})
    assert calls == [] and stream.epoch == -1 and not stream.epoch_end
    batches = [stream.next() for _ in sizes]
    assert [len(batch) for batch in batches] == sizes
    assert [item for batch in batches for item in batch] == list(range(sum(sizes)))
    assert stream.epoch_end and stream.offset == sum(sizes) and calls == [0]
    stream.state_dict()
    assert calls == [0]
    assert stream.next() == list(range(16)) and calls == [0, 1]


@pytest.mark.parametrize("cut", [0, 1, 4, 5, 6, 10])
@pytest.mark.parametrize("temporal", [False, True])
def test_reference_sampling_and_exact_resume(stream_type, cut, temporal):
    def records(rng, epoch):
        starts = rng.integers(0, 162, size=70) if temporal else np.zeros(70, dtype=int)
        return [(int(i), int(starts[i])) for i in rng.permutation(70)]

    # 独立参考直接按科学顺序抽起点、排列、切片，未调用被测流。
    rng = np.random.Generator(np.random.PCG64(42))
    expected = []
    for epoch in range(4):
        current = records(rng, epoch)
        expected.extend(current[i : i + 16] for i in range(0, 70, 16))
    stream = stream_type(records, 16, source_contract={"temporal": temporal})
    assert [stream.next() for _ in range(cut)] == expected[:cut]
    state = stream.state_dict()
    restored = stream_type(records, 16, seed=123, source_contract={"temporal": temporal})
    restored.load_state_dict(state)
    assert [restored.next() for _ in range(20 - cut)] == expected[cut:]
    assert restored.state_dict()["rng"] == rng.bit_generator.state


@pytest.mark.parametrize(
    "bad", ["offset", "epoch", "rng", "batch_size", "drop_last", "contract", "items"]
)
def test_restore_rejects_without_mutating_or_sampling(stream_type, bad):
    calls = []

    def records(rng, epoch):
        calls.append(epoch)
        return rng.permutation(7).tolist()

    stream = stream_type(records, 3, source_contract={"data": "a"})
    stream.next()
    before = stream.state_dict()
    state = copy.deepcopy(before)
    key, value = {
        "offset": ("offset", 2),
        "epoch": ("epoch", -1),
        "rng": ("rng", {}),
        "batch_size": ("batch_size", 4),
        "drop_last": ("drop_last", True),
        "contract": ("source_contract", {"data": "b"}),
        "items": ("items", [object()]),
    }[bad]
    state[key] = value
    with pytest.raises(ValueError):
        stream.load_state_dict(state)
    assert stream.state_dict() == before and calls == [0]


@pytest.mark.parametrize(
    "items,drop_last",
    [([], False), ([1], True), ((i for i in range(3)), False), ([float("nan")], False)],
)
def test_invalid_epoch_does_not_advance_rng(stream_type, items, drop_last):
    def records(rng, epoch):
        rng.random()
        return items

    stream = stream_type(records, 4, drop_last=drop_last, source_contract={})
    state = stream.state_dict()
    with pytest.raises(ValueError):
        stream.next()
    assert stream.state_dict() == state


def test_snapshot_batch_and_contract_are_independent(stream_type):
    contract = {"ids": [1, 2]}
    stream = stream_type(
        lambda rng, epoch: [{"ids": [1]}, {"ids": [2]}], 1, source_contract=contract
    )
    contract["ids"].append(3)
    batch = stream.next()
    batch[0]["ids"].append(9)
    state = stream.state_dict()
    state["items"][1]["ids"].append(8)
    assert stream.next() == [{"ids": [2]}]
    assert stream.state_dict()["source_contract"] == {"ids": [1, 2]}
    one = stream_type(lambda rng, epoch: [3], 5, source_contract={})
    assert one.next() == [3] and one.epoch_end


@pytest.mark.parametrize("batch_size,drop_last", [(0, False), (True, False), (1.5, False), (2, 1)])
def test_invalid_batch_settings(stream_type, batch_size, drop_last):
    with pytest.raises(ValueError):
        stream_type(lambda rng, epoch: [1], batch_size, drop_last=drop_last, source_contract={})


def test_reject_executable_records_without_calling_copy_hooks(stream_type):
    class Record:
        def __deepcopy__(self, memo):
            pytest.fail("must not call arbitrary object copy hook")

    stream = stream_type(lambda rng, epoch: [Record()], 1, source_contract={})
    with pytest.raises(ValueError):
        stream.next()


def test_accumulation_consumes_boundary_without_cross_epoch_groups(stream_type):
    stream = stream_type(lambda rng, epoch: list(range(7)), 3, source_contract={})
    seen = []
    model = torch.nn.Linear(1, 1)

    def objective(model, x):
        seen.append(x[:, 0].tolist())
        return model(x).square().mean()

    fit_iterations(
        model,
        torch.optim.SGD(model.parameters(), lr=0.01),
        stream,
        lambda ids: torch.tensor(ids, dtype=torch.float32)[:, None],
        objective,
        updates=2,
        accumulate=2,
        epoch_end=lambda current: current.epoch_end,
        max_grad_norm=None,
    )
    assert seen == [[0, 1, 2], [3, 4, 5], [0, 1, 2], [3, 4, 5]]
    assert stream.epoch == 1 and stream.offset == 6


@pytest.mark.parametrize("temporal", [False, True])
def test_short_training_reference_and_checkpoint_resume(stream_type, tmp_path, temporal):
    torch.manual_seed(7)
    initial = copy.deepcopy(torch.nn.Linear(1, 1).state_dict())
    data = torch.arange(70 * 8, dtype=torch.float32).reshape(70, 8, 1) / 560

    def records(rng, epoch):
        starts = rng.integers(0, 7, 70) if temporal else np.zeros(70, dtype=int)
        return [(int(i), int(starts[i])) for i in rng.permutation(70)]

    def batch(ids):
        return torch.stack([data[i, start] for i, start in ids])

    def loss(model, x):
        return (model(x) - 2 * x).square().mean()

    def setup():
        model = torch.nn.Linear(1, 1)
        model.load_state_dict(initial)
        return model, torch.optim.SGD(model.parameters(), lr=0.03, momentum=0.9)

    # 无 Dojo 流/循环的参考：相同批次、损失、梯度和参数轨迹。
    reference, opt = setup()
    rng = np.random.default_rng(42)
    expected, grads = [], []
    for epoch in range(2):
        rows = records(rng, epoch)
        for offset in range(0, 70, 16):
            opt.zero_grad()
            loss(reference, batch(rows[offset : offset + 16])).backward()
            grads.append([p.grad.clone() for p in reference.parameters()])
            opt.step()
            expected.append(copy.deepcopy(reference.state_dict()))

    model, opt = setup()
    stream = stream_type(records, 16, source_contract={"temporal": temporal})
    traces = []

    def observe(i, m):
        traces.append(copy.deepcopy(m.state_dict()))
        for actual, wanted in zip(m.parameters(), grads[i - 1], strict=True):
            torch.testing.assert_close(actual.grad, wanted, rtol=0, atol=0)

    history = fit_iterations(
        model, opt, stream, batch, loss, updates=7, max_grad_norm=None, after_update=observe
    )
    writer = RunWriter.create(tmp_path / "run", nested=False)
    path = writer.write_checkpoint(
        "latest",
        capture_iteration(
            model,
            opt,
            updates=7,
            stream=stream,
            contract={},
            history=history,
        ),
    )
    restored, optimizer = setup()
    resumed = stream_type(records, 16, source_contract={"temporal": temporal})
    saved = restore_iteration(path, restored, optimizer, stream=resumed, contract={})
    fit_iterations(
        restored,
        optimizer,
        resumed,
        batch,
        loss,
        updates=10,
        start=7,
        history=saved["history"],
        max_grad_norm=None,
        after_update=observe,
    )
    assert len(traces) == 10
    for a, b in zip(traces, expected, strict=True):
        for key in a:
            torch.testing.assert_close(a[key], b[key], rtol=0, atol=0)
