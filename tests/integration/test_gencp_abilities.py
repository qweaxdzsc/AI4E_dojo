"""生成耦合原子能力的解析与恢复验收，不依赖大数据。"""

import numpy as np
import pytest
import torch

from ai4e_core.abilities.data.extract.time_windows import window_count, window_slices
from ai4e_core.abilities.data.source.array_read import read_array
from ai4e_core.abilities.data.validate.trajectory import validate_pairing
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from ai4e_core.abilities.inference.coupled_steps import (
    sequential_euler_step,
    synchronous_euler_step,
)
from ai4e_core.abilities.inference.execution import inference_group
from ai4e_core.abilities.inference.integration import integrate
from ai4e_core.abilities.sampling.flow import flow_randomness
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.abilities.transform.field_transforms import logarithm, signed_range
from ai4e_core.abilities.transform.flow_path import conditional_path


def test_real_window_endpoints_and_native_slice(tmp_path):
    assert window_count(999, 3, 12, interval=10) == 850
    x, y = window_slices(849, 999, 3, 12, interval=10)
    assert list(range(999))[x] == [849, 859, 869]
    assert list(range(999))[y][-1] == 989
    with pytest.raises(IndexError):
        window_slices(850, 999, 3, 12, interval=10)
    array = np.arange(60).reshape(3, 4, 5)
    np.save(tmp_path / "a.npy", array)
    np.testing.assert_array_equal(
        read_array(tmp_path / "a.npy", (1, slice(None), slice(1, 3))), array[1, :, 1:3]
    )


def test_pairing_rejects_reordered_trajectory():
    with pytest.raises(ValueError):
        validate_pairing(
            [
                {"sample_ids": [1, 2], "time_indices": [0, 1]},
                {"sample_ids": [2, 1], "time_indices": [0, 1]},
            ]
        )


def test_transform_and_explicit_flow_randomness():
    x = torch.tensor([[0.0, 3.0, 100.0]])
    torch.testing.assert_close(logarithm(logarithm(x), inverse=True), x)
    torch.testing.assert_close(
        signed_range(signed_range(x, [0] * 3, [100] * 3), [0] * 3, [100] * 3, inverse=True), x
    )
    initial = torch.zeros_like(x)
    noise = torch.ones_like(x)
    t = torch.tensor([0.25])
    sampled = flow_randomness(x, initial=initial, time=t, noise=noise)
    state, velocity = conditional_path(sampled[0], x, sampled[1], sampled[2], sigma=0.1)
    torch.testing.assert_close(state, x * 0.25 + 0.1)
    torch.testing.assert_close(velocity, x)


def test_jacobi_and_sequential_read_different_states():
    states = {"a": torch.tensor([1.0]), "b": torch.tensor([2.0])}
    velocities = {"a": lambda s, t: s["b"], "b": lambda s, t: s["a"]}
    jacobi = integrate(
        states, [0.0, 0.5], step=synchronous_euler_step, velocities=velocities, order=("a", "b")
    )
    sequential = integrate(
        states, [0.0, 0.5], step=sequential_euler_step, velocities=velocities, order=("a", "b")
    )
    assert jacobi["b"].item() == 2.5 and sequential["b"].item() == 3
    assert states["a"].item() == 1


def test_stream_and_ema_buffers_resume():
    stream = IterationStream(8, 2)
    stream.next()
    state = stream.state_dict()
    expected = [stream.next() for _ in range(9)]
    other = IterationStream(8, 2)
    other.load_state_dict(state)
    assert all(torch.equal(a, other.next()) for a in expected)
    model = torch.nn.BatchNorm1d(2)
    ema = MovingAverage(model, 0.5, buffer_policy="copy")
    model.running_mean.fill_(3)
    ema.update(model)
    assert torch.equal(ema.state["running_mean"], model.running_mean)


def test_group_restores_modes_and_rng_on_error():
    models = [torch.nn.Linear(2, 2), torch.nn.BatchNorm1d(2).eval()]
    rng = torch.get_rng_state()
    with pytest.raises(RuntimeError), inference_group(models):
        assert all(not model.training for model in models)
        torch.rand(4)
        raise RuntimeError("injected")
    assert models[0].training and not models[1].training
    assert torch.equal(rng, torch.get_rng_state())


def test_metrics_do_not_mix_units():
    target = torch.ones(2, 3, 4, 5, 2)
    target[..., 1] *= 1000
    prediction = target.clone()
    prediction[..., 0] *= 2
    values = trajectory_metrics(prediction, target)
    assert values["component_relative_l2"] == [1.0, 0.0]
    assert values["field_relative_l2"] == 0.5


def test_writer_isolates_fields_and_preserves_old_api(tmp_path):
    from ai4e_core.run.writer import RunWriter

    writer = RunWriter(tmp_path)
    old = writer.write_checkpoint("latest", {"value": 0})
    first = writer.write_checkpoint("latest", {"value": 1}, namespace="fluid")
    second = writer.write_checkpoint("latest", {"value": 2}, namespace="solid")
    assert len({old, first, second}) == 3
    assert torch.load(old, weights_only=True)["value"] == 0
    with pytest.raises(ValueError):
        writer.write_checkpoint("latest", {}, namespace="../escape")


def test_constant_range_and_explicit_layout_roundtrip():
    from ai4e_core.abilities.transform.layout import transpose

    values = torch.tensor([[3.0, 4.0]])
    normalized = signed_range(values, [3.0, 4.0], [3.0, 4.0])
    torch.testing.assert_close(normalized, torch.full_like(values, -1.0), rtol=0, atol=0)
    torch.testing.assert_close(
        signed_range(normalized, [3.0, 4.0], [3.0, 4.0], inverse=True), values, rtol=0, atol=0
    )
    array = torch.arange(48).reshape(2, 3, 4, 2)
    moved = transpose(array, ("T", "H", "W", "C"), ("C", "T", "H", "W"))
    torch.testing.assert_close(
        transpose(moved, ("C", "T", "H", "W"), ("T", "H", "W", "C")), array, rtol=0, atol=0
    )
    with pytest.raises(ValueError):
        transpose(array, ("T", "H", "W", "C"), ("T", "H", "H", "C"))
