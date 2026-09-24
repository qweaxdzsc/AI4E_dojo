"""六种空间架构的独立参考、完整尺寸、梯度和组件复用验收。"""

import json
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.modeling.models.cnn import CNN2d, CNN3d
from ai4e_core.abilities.modeling.models.resnet import ResNet2d, ResNet3d
from ai4e_core.abilities.modeling.models.unet import UNet2d, UNet3d
from ai4e_core.abilities.modeling.stages.convolution import ConvStage, ResidualStage
from tools.verification.classic_networks.reference_spatial import (
    build_reference_model,
    copy_weights,
)


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


@pytest.mark.parametrize(
    "family,dim,model_type",
    [
        ("cnn", 2, CNN2d),
        ("cnn", 3, CNN3d),
        ("resnet", 2, ResNet2d),
        ("resnet", 3, ResNet3d),
        ("unet", 2, UNet2d),
        ("unet", 3, UNet3d),
    ],
)
def test_complete_model_independent_forward_backward(family, dim, model_type):
    channels, out = (3, 1) if dim == 2 else (5, 3)
    model = model_type(channels, out).eval()
    reference = build_reference_model(family, dim, channels, out).eval()
    copy_weights(model, reference)
    shape = (85, 85) if dim == 2 else (32, 32, 32)
    x = torch.randn(1, channels, *shape, requires_grad=True)
    reference_x = x.detach().clone().requires_grad_()
    prediction, expected = model(x), reference(reference_x)
    assert prediction.shape == (1, out, *shape)
    torch.testing.assert_close(prediction, expected, rtol=1e-5, atol=1e-6)
    prediction.square().mean().backward()
    expected.square().mean().backward()
    torch.testing.assert_close(x.grad, reference_x.grad, rtol=1e-5, atol=1e-6)
    for parameter, ref_parameter in zip(model.parameters(), reference.parameters(), strict=True):
        assert parameter.grad is not None and torch.isfinite(parameter.grad).all()
        torch.testing.assert_close(parameter.grad, ref_parameter.grad, rtol=1e-5, atol=1e-6)
    assert any(isinstance(m, ConvStage) for m in model.modules())
    if family == "resnet":
        stages = [m for m in model.encoder.blocks if isinstance(m, ResidualStage)]
        assert [len(s.blocks) for s in stages] == [2, 2, 2, 2]


def test_source_and_independent_reference_boundary():
    root = Path(__file__).resolve().parents[2] / "tools/verification/classic_networks"
    source = json.loads((root / "reference_spatial_sources.json").read_text())
    assert source["upstream"]["commit"] == "824e8c8726b65fd9d5abdc9702f81c2b0c4c0dc8"
    reference = (root / "reference_spatial.py").read_text()
    assert "from ai4e_" not in reference and "import ai4e_" not in reference
