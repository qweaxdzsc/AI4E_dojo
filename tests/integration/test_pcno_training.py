"""轮换流、共享评价回调和科学损失日程门禁。"""

import random

import pytest
import torch

from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
from ai4e_core.applications.base.iteration_training import train_model


def test_rotating_stream_follows_original_and_resumes():
    random.seed(7)
    paths = [str(i) for i in range(8)]
    expected = []
    for epoch in range(1, 4):
        random.shuffle(paths)
        expected.extend((p, i, epoch) for p in paths[:-1] for i in range(3))
    random.seed(7)
    stream = RotatingChunkStream([str(i) for i in range(8)], 3)
    result = [stream.next() for _ in range(22)]
    state = stream.state_dict()
    restored = RotatingChunkStream([str(i) for i in range(8)], 3)
    restored.load_state_dict(state)
    result.extend(restored.next() for _ in range(41))
    assert result == expected
    state["cursor"] = 22
    with pytest.raises(ValueError):
        restored.load_state_dict(state)


def test_evaluation_callback_and_default_interval(tmp_path):
    class Session:
        def checkpoint(self, label, payload, namespace):
            p = tmp_path / (namespace + ".pt")
            torch.save(payload, p)
            return p

        def report(self, *args, **kwargs):
            pass

    calls = []
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    stream = RotatingChunkStream(["a", "b"], 2)
    result = train_model(
        model,
        optimizer,
        stream,
        lambda i: torch.ones(1, 1),
        lambda m, x: m(x).square().mean(),
        updates=3,
        session=Session(),
        contract={},
        namespace="test",
        evaluate=lambda i, m: calls.append(i),
        evaluate_every=2,
    )
    assert calls == [2, 3] and result["updates"] == 3
    observed = {}

    def iterate(*args, **kwargs):
        observed.update(kwargs)
        return []

    train_model(
        model,
        optimizer,
        stream,
        None,
        None,
        updates=0,
        session=Session(),
        contract={},
        namespace="test",
        iterate=iterate,
    )
    assert observed["evaluate_every"] == 500 and "evaluate" not in observed


def test_loss_stages_are_not_compressed_for_short_training():
    from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

    x = torch.tensor(1.0)
    assert ModelConfig.loss_weights(49, x, x, x)["w_phys"] == 0
    assert ModelConfig.loss_weights(50, x, x, x)["w_phys"] == 0.1
    assert ModelConfig.loss_weights(80, x, x, x)["w_task"] == 0.1
    assert ModelConfig.loss_weights(110, x, x, x)["w_phys"] == 0.8


def test_complete_restore_spans_chunk_epoch_and_loss_phase(tmp_path):
    from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration

    random.seed(7)
    torch.manual_seed(7)
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.AdamW(model.parameters())
    stream = RotatingChunkStream([str(i) for i in range(8)], 3)
    for boundary in [21, 49 * 21, 79 * 21, 109 * 21]:
        stream = RotatingChunkStream([str(i) for i in range(8)], 3)
        for _ in range(boundary):
            stream.next()
        state = capture_iteration(
            model,
            opt,
            updates=boundary,
            stream=stream,
            contract={"statistics": "frozen"},
            history=[0.0] * boundary,
        )
        p = tmp_path / "state.pt"
        torch.save(state, p)
        expected = stream.next()
        restored = RotatingChunkStream([str(i) for i in range(8)], 3)
        restore_iteration(p, model, opt, stream=restored, contract={"statistics": "frozen"})
        assert restored.next() == expected
        with pytest.raises(ValueError, match="语义冲突"):
            restore_iteration(p, model, opt, stream=restored, contract={"statistics": "changed"})
