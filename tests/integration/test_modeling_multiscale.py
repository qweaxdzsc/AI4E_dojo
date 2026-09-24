"""多尺度显式交接、公开阶段替换及保存读回，不执行训练。"""

import copy
import io

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.models.unet import UNet2d, UNet3d
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock2d
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock2d
from ai4e_core.abilities.modeling.stages.convolution import ConvStage, ResidualStage


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


@pytest.mark.parametrize("model_type,shape", [(UNet2d, (17, 19)), (UNet3d, (8, 10, 12))])
def test_explicit_multiscale_and_roundtrip(model_type, shape):
    model = model_type(3, 2, base_channels=2).eval()
    x = torch.randn(1, 3, *shape, requires_grad=True)
    bottom, skips, sizes = model.encoder(x)
    assert sizes == [tuple(n // 2**i for n in shape) for i in range(3)]
    assert all(s.requires_grad for s in skips)
    assert isinstance(model.encoder.stages, nn.ModuleList)
    assert isinstance(model.decoder.up_fusions, nn.ModuleList)
    features = model.decoder(model.bottleneck(bottom), skips, sizes)
    y = model.head(features)
    torch.testing.assert_close(y, model(x))
    (y.square().mean() + skips[1].square().mean()).backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    storage = io.BytesIO()
    torch.save(model.state_dict(), storage)
    storage.seek(0)
    restored = model_type(3, 2, base_channels=2).eval()
    restored.load_state_dict(torch.load(storage, weights_only=True), strict=True)
    torch.testing.assert_close(restored(x), y)
    with pytest.raises(ValueError, match="层数"):
        model.decoder(model.bottleneck(bottom), skips[:-1], sizes[:-1])
    with pytest.raises(ValueError, match="排序"):
        model.decoder(model.bottleneck(bottom), list(reversed(skips)), list(reversed(sizes)))


def test_residual_encoder_and_independent_stage_replacement():
    base = UNet2d(3, 1, base_channels=2).eval()
    encoder = copy.deepcopy(base.encoder)
    encoder.stages[0] = ResidualStage([BasicResidualBlock2d(3, 2), BasicResidualBlock2d(2, 2)])
    middle = ConvStage([ConvBlock2d(8, 16), ConvBlock2d(16, 16)])
    head = nn.Conv2d(2, 1, 1)
    model = UNet2d(
        3,
        1,
        base_channels=2,
        encoder=encoder,
        bottleneck=middle,
        decoder=copy.deepcopy(base.decoder),
        head=head,
    ).eval()
    x = torch.randn(2, 3, 17, 19)
    before = {name: value.clone() for name, value in model.state_dict().items()}
    prediction = model(x)
    assert prediction.shape == (2, 1, 17, 19)
    prediction.square().mean().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    assert all(torch.equal(before[k], v) for k, v in model.state_dict().items())
    assert model.bottleneck is middle and model.head is head and model.encoder is encoder
    assert any("encoder.stages.0.blocks.0.shortcut" in k for k in model.state_dict())
    restored = copy.deepcopy(model)
    restored.load_state_dict(before)
    torch.testing.assert_close(restored(x), prediction)


def test_empty_or_invalid_stage():
    with pytest.raises(ValueError):
        ConvStage([])
    with pytest.raises(ValueError):
        ConvStage([lambda value: value])
    with pytest.raises(ValueError, match="过小"):
        UNet2d(3, 1)(torch.randn(1, 3, 7, 9))
