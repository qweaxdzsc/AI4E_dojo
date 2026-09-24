"""经典完整模型的参考与可替换组合；不执行优化器、训练或真实精度验收。"""

import io

import pytest
import torch
from torch import nn
from torch.nn import functional as F

from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.modeling.models.rnn import RNN
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward, Mlp
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp as ProjectedMlp
from ai4e_core.abilities.modeling.stages.recurrent import RecurrentStage
from tools.verification.classic_networks.reference_features import (
    RNNReference,
    feed_forward_reference,
    feed_forward_weights,
    rnn_model_weights,
)


@pytest.mark.parametrize("shape,out", [((2, 7, 7, 3), 1), ((1, 4, 4, 4, 5), 3)])
def test_complete_mlp_reuses_public_feed_forward(shape, out):
    model = MLP(shape[-1], out)
    reference = feed_forward_reference(shape[-1], out)
    reference.load_state_dict(
        feed_forward_weights(model.state_dict(), prefix="feed_forward.projection.layers."),
        strict=True,
    )
    assert isinstance(model.feed_forward, FeedForward)
    x = torch.randn(shape)
    torch.testing.assert_close(model(x), reference(x))
    replacement = FeedForward(shape[-1], out, (8, 8), "tanh")
    changed = MLP(shape[-1], out, feed_forward=replacement)
    assert changed.feed_forward is replacement
    assert sum(p.numel() for p in changed.parameters()) < sum(p.numel() for p in model.parameters())
    changed(x).square().mean().backward()
    assert all(
        p.grad is not None and torch.isfinite(p.grad).all() for p in replacement.parameters()
    )
    stream = io.BytesIO()
    torch.save(changed.state_dict(), stream)
    stream.seek(0)
    restored = MLP(shape[-1], out, feed_forward=FeedForward(shape[-1], out, (8, 8), "tanh"))
    restored.load_state_dict(torch.load(stream, weights_only=True), strict=True)
    torch.testing.assert_close(restored(x), changed(x))


def test_complete_rnn_reference_gradients_and_independent_windows():
    model, reference = RNN(4, 4), RNNReference(4, 4)
    reference.load_state_dict(rnn_model_weights(model.state_dict()), strict=True)
    x = torch.randn(7, 3, 4, requires_grad=True)
    other = x.detach().clone().requires_grad_()
    actual, state = model(x)
    expected, expected_state = reference(other)
    torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-6)
    torch.testing.assert_close(state, expected_state, rtol=1e-5, atol=1e-6)
    actual.square().mean().backward()
    expected.square().mean().backward()
    torch.testing.assert_close(x.grad, other.grad, rtol=1e-5, atol=1e-6)
    parameters = rnn_model_weights(dict(model.named_parameters()))
    for name, parameter in reference.named_parameters():
        torch.testing.assert_close(parameters[name].grad, parameter.grad, rtol=1e-5, atol=1e-6)
    model(torch.randn_like(x), state)
    torch.testing.assert_close(model(x)[0], actual)
    order = torch.tensor([6, 0, 1, 4, 2, 5, 3])
    torch.testing.assert_close(model(x[order])[0], actual[order])


def test_rnn_all_three_components_are_replaceable_and_serializable():
    input_mapping = nn.Linear(4, 8)
    stage = RecurrentStage(8, hidden_size=6, num_layers=3)
    output_mapping = FeedForward(6, 4, (9,), "relu")
    model = RNN(
        4, 4, input_mapping=input_mapping, recurrent_stage=stage, output_mapping=output_mapping
    )
    assert model.input_mapping is input_mapping
    assert model.recurrent_stage is stage
    assert model.output_mapping is output_mapping
    x = torch.randn(2, 5, 4)
    actual, state = model(x)
    assert state.shape == (3, 2, 6)
    actual.square().sum().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    buffer = io.BytesIO()
    torch.save(model.state_dict(), buffer)
    buffer.seek(0)
    restored = RNN(
        4,
        4,
        input_mapping=nn.Linear(4, 8),
        recurrent_stage=RecurrentStage(8, 6, 3),
        output_mapping=FeedForward(6, 4, (9,), "relu"),
    )
    restored.load_state_dict(torch.load(buffer, weights_only=True), strict=True)
    torch.testing.assert_close(restored(x)[0], actual)
    torch.testing.assert_close(restored(x)[1], state)


def test_legacy_mlp_weights_and_math_are_unchanged():
    old = Mlp(3)
    assert set(old.state_dict()) == {"fc1.weight", "fc1.bias", "fc2.weight", "fc2.bias"}
    x = torch.randn(2, 4, 3)
    expected = F.linear(
        F.gelu(F.linear(x, old.fc1.weight, old.fc1.bias)), old.fc2.weight, old.fc2.bias
    )
    torch.testing.assert_close(old(x), expected, rtol=0, atol=0)
    projected = ProjectedMlp(3, [7, 5], 2)
    reference = feed_forward_reference(3, 2, (7, 5))
    reference.load_state_dict(
        {key.removeprefix("layers."): p for key, p in projected.state_dict().items()}
    )
    torch.testing.assert_close(projected(x), reference(x), rtol=0, atol=0)


def test_replacement_preserves_declared_output_axes():
    with pytest.raises(ValueError, match="输出"):
        MLP(3, 2, feed_forward=nn.Linear(3, 4))(torch.zeros(5, 3))
    with pytest.raises(ValueError, match="输入映射"):
        RNN(4, 4, input_mapping=nn.Flatten())(torch.zeros(2, 3, 4))
    with pytest.raises(ValueError, match="输出映射"):
        RNN(4, 4, output_mapping=nn.Linear(32, 5))(torch.zeros(2, 3, 4))
