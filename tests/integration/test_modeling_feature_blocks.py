"""共享前馈与单层循环的独立前后向检查；本文件不执行优化器更新。"""

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock
from tools.verification.classic_networks.reference_features import (
    SOURCE,
    feed_forward_reference,
    feed_forward_weights,
    source_identity,
)


@pytest.mark.parametrize("shape", [(3,), (2, 7, 3), (2, 3, 4, 3)])
@pytest.mark.parametrize("hidden,activation,final", [((), "gelu", None), ((5, 4), "relu", "tanh")])
def test_feed_forward_reference_and_gradients(shape, hidden, activation, final):
    torch.manual_seed(17)
    local = FeedForward(3, 2, hidden, activation, final)
    reference = feed_forward_reference(3, 2, hidden, activation, final)
    reference.load_state_dict(feed_forward_weights(local.state_dict()), strict=True)
    x = torch.randn(shape, requires_grad=True)
    other = x.detach().clone().requires_grad_()
    actual, expected = local(x), reference(other)
    torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-6)
    actual.square().sum().backward()
    expected.square().sum().backward()
    torch.testing.assert_close(x.grad, other.grad, rtol=1e-5, atol=1e-6)
    gradients = feed_forward_weights(dict(local.named_parameters()))
    for name, parameter in reference.named_parameters():
        torch.testing.assert_close(gradients[name].grad, parameter.grad, rtol=1e-5, atol=1e-6)


@pytest.mark.parametrize("dropout", [0.25, 1.0])
def test_feed_forward_dropout_is_hidden_only(dropout):
    local = FeedForward(3, 2, (4, 4), "gelu", "sigmoid", dropout)
    reference = feed_forward_reference(3, 2, (4, 4), "gelu", "sigmoid", dropout)
    reference.load_state_dict(feed_forward_weights(local.state_dict()), strict=True)
    x = torch.randn(5, 3)
    torch.manual_seed(3)
    actual = local(x)
    torch.manual_seed(3)
    expected = reference(x)
    torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-6)
    local.eval()
    reference.eval()
    torch.testing.assert_close(local(x), reference(x))


@pytest.mark.parametrize(
    "options", [{"in_features": 0}, {"hidden_features": (-1,)}, {"dropout": 1.2}]
)
def test_feed_forward_rejects_invalid_configuration(options):
    with pytest.raises(ValueError):
        FeedForward(**{"in_features": 3, "out_features": 2, **options})
    with pytest.raises(ValueError, match="末轴"):
        FeedForward(3, 2)(torch.zeros(2, 4))


@pytest.mark.parametrize("nonlinearity", ["tanh", "relu"])
def test_recurrent_block_native_reference_and_state(nonlinearity):
    local = RecurrentBlock(3, 5, nonlinearity)
    reference = nn.RNN(3, 5, nonlinearity=nonlinearity, batch_first=True)
    reference.load_state_dict(local.recurrent.state_dict(), strict=True)
    x = torch.randn(2, 4, 3, requires_grad=True)
    other = x.detach().clone().requires_grad_()
    initial = torch.randn(1, 2, 5, requires_grad=True)
    other_state = initial.detach().clone().requires_grad_()
    output, state = local(x, initial)
    expected, expected_state = reference(other, other_state)
    torch.testing.assert_close(output, expected)
    torch.testing.assert_close(state, expected_state)
    (output.square().sum() + state.square().sum()).backward()
    (expected.square().sum() + expected_state.square().sum()).backward()
    torch.testing.assert_close(x.grad, other.grad)
    torch.testing.assert_close(initial.grad, other_state.grad)
    for name, parameter in local.recurrent.named_parameters():
        torch.testing.assert_close(parameter.grad, dict(reference.named_parameters())[name].grad)
    first, middle = local(x.detach()[:, :2], initial.detach())
    second, final = local(x.detach()[:, 2:], middle)
    torch.testing.assert_close(torch.cat((first, second), dim=1), output)
    torch.testing.assert_close(final, state)
    torch.testing.assert_close(local(x.detach())[0], reference(x.detach())[0])


def test_recurrent_block_rejects_state_shape_dtype_and_empty_time():
    block = RecurrentBlock(3, 5)
    x = torch.ones(2, 3, 3)
    with pytest.raises(ValueError, match="状态"):
        block(x, torch.zeros(2, 2, 5))
    with pytest.raises(ValueError, match="精度"):
        block(x, torch.zeros(1, 2, 5, dtype=torch.float64))
    with pytest.raises(ValueError, match="时间"):
        block(x[:, :0])


def test_independent_reference_source_identity():
    actual = source_identity()
    assert actual["torch_version"] == SOURCE["torch_version"]
    assert actual["torch_commit"] == SOURCE["torch_commit"]
    assert actual["files"] == SOURCE["files"]
