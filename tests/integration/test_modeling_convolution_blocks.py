"""公共空间块独立数值、梯度与错误边界；不运行优化器。"""

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.convolution import ConvBlock2d, ConvBlock3d
from ai4e_core.abilities.modeling.modules.residual import (
    BasicResidualBlock2d,
    BasicResidualBlock3d,
    Bottleneck2d,
    Bottleneck3d,
)
from ai4e_core.abilities.modeling.modules.skip_fusion import SkipFusion
from ai4e_core.abilities.modeling.modules.spatial_resampling import (
    SpatialDownsample,
    SpatialUpsample,
)
from tools.verification.classic_networks.reference_spatial import (
    ReferenceResidual,
    copy_weights,
    layer,
)


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


def compare(model, reference, shape):
    copy_weights(model, reference)
    x = torch.randn(*shape, requires_grad=True)
    independent_x = x.detach().clone().requires_grad_()
    y, ref_y = model(x), reference(independent_x)
    torch.testing.assert_close(y, ref_y, rtol=1e-5, atol=1e-6)
    y.square().mean().backward()
    ref_y.square().mean().backward()
    torch.testing.assert_close(x.grad, independent_x.grad, rtol=1e-5, atol=1e-6)
    for parameter, expected in zip(model.parameters(), reference.parameters(), strict=True):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()
        torch.testing.assert_close(parameter.grad, expected.grad, rtol=1e-5, atol=1e-6)


@pytest.mark.parametrize("dim,block", [(2, ConvBlock2d), (3, ConvBlock3d)])
@pytest.mark.parametrize("normalization,activation", [("none", "gelu"), ("batch", "relu")])
def test_convolution_independent(dim, block, normalization, activation):
    model = block(3, 5, normalization=normalization, activation=activation)
    reference = layer(dim, 3, 5, batch=normalization == "batch", relu=activation == "relu")
    compare(model, reference, (2, 3, *([9] * dim)))


@pytest.mark.parametrize(
    "dim,basic,bottle",
    [(2, BasicResidualBlock2d, Bottleneck2d), (3, BasicResidualBlock3d, Bottleneck3d)],
)
@pytest.mark.parametrize(
    "bottleneck,stride,identity",
    [(False, 1, True), (False, 2, False), (True, 1, True), (True, 2, False)],
)
def test_residual_independent(dim, basic, bottle, bottleneck, stride, identity):
    inc = (8 if bottleneck else 2) if identity else 3
    model = (bottle if bottleneck else basic)(inc, 2, stride=stride)
    reference = ReferenceResidual(dim, inc, 2, stride=stride, bottleneck=bottleneck)
    assert isinstance(model.shortcut, nn.Identity) == identity
    compare(model, reference, (2, inc, *([9] * dim)))


@pytest.mark.parametrize("dim", [2, 3])
def test_resampling_fusion_projection(dim):
    shape = (9, 11) if dim == 2 else (9, 11, 13)
    conv = nn.Conv2d if dim == 2 else nn.Conv3d
    x = torch.randn(1, 4, *shape, requires_grad=True)
    down = SpatialDownsample(dim, projection=conv(4, 6, 1))
    bottom = down(x)
    fusion = SkipFusion(conv(6, 3, 1), upsample=SpatialUpsample(projection=conv(6, 2, 1)))
    y = fusion(bottom, x, shape)
    assert y.shape == (1, 3, *shape)
    y.square().mean().backward()
    assert torch.isfinite(x.grad).all()
    assert all(p.grad is not None for p in [*down.parameters(), *fusion.parameters()])
    with pytest.raises(ValueError, match="尺寸"):
        fusion(bottom, x, tuple(n - 1 for n in shape))
    with pytest.raises(ValueError, match="过小"):
        down(torch.randn(1, 4, *([1] * dim)))


@pytest.mark.parametrize(
    "kwargs",
    [{"in_channels": 0}, {"kernel_size": 2}, {"normalization": "unknown"}, {"stride": True}],
)
def test_invalid_convolution(kwargs):
    config = {"in_channels": 2, "out_channels": 3, **kwargs}
    with pytest.raises(ValueError):
        ConvBlock2d(**config)


def test_wrong_tensor_layout():
    with pytest.raises(ValueError, match="维度"):
        ConvBlock2d(2, 3)(torch.randn(1, 2, 3))
    with pytest.raises(ValueError, match="浮点"):
        ConvBlock2d(2, 3)(torch.ones(1, 2, 3, 3, dtype=torch.long))
