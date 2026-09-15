"""公开原子推理：梯度、模式、随机流及失败恢复。"""

import random

import numpy as np
import pytest
import torch

from ai4e_core.abilities.inference import predict


@pytest.mark.parametrize("fail", [False, True])
def test_predict_preserves_modes_gradients_and_randomness(fail):
    model = torch.nn.Sequential(torch.nn.Linear(2, 2), torch.nn.Dropout())
    model.train()
    model[0].eval()
    before = torch.get_rng_state().clone()
    py = random.getstate()
    numpy = np.random.get_state()
    modes = [m.training for m in model.modules()]

    def operation(model, values):
        assert not torch.is_grad_enabled()
        assert not any(m.training for m in model.modules())
        torch.rand(3)
        random.random()
        np.random.rand()
        if fail:
            raise ValueError("calculation failed")
        return model(values)

    if fail:
        with pytest.raises(ValueError, match="calculation failed"):
            predict(model, torch.ones(2, 2), operation=operation)
    else:
        values = predict(model, torch.ones(2, 2), operation=operation)
        assert not values.requires_grad
    assert [m.training for m in model.modules()] == modes
    assert torch.equal(torch.get_rng_state(), before)
    assert random.getstate() == py
    np.testing.assert_equal(np.random.get_state(), numpy)
    assert all(p.grad is None for p in model.parameters())


def test_shared_random_stream_consumes_in_sequence():
    model = torch.nn.Linear(1, 1)
    torch.manual_seed(7)
    expected = torch.rand(2)
    torch.manual_seed(7)
    result = [
        predict(model, None, operation=lambda m, x: torch.rand(1), preserve_rng=False)
        for _ in range(2)
    ]
    torch.testing.assert_close(torch.cat(result), expected, atol=0, rtol=0)
