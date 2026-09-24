"""跨族公开组件的前后向、状态注册与保存读回；没有优化器或训练。"""

import io

import numpy as np
import pytest
import torch

from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock
from ai4e_core.abilities.modeling.stages.recurrent import RecurrentStage
from ai4e_core.abilities.modeling.stages.transformer import TransformerEncoder
from examples.recipe_extensions.network_composition import (
    cnn_rnn,
    resunet,
    unet_transformer,
    user_outputs,
)


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


@pytest.mark.parametrize(
    "module,dim", [(resunet, 2), (resunet, 3), (unet_transformer, 2), (unet_transformer, 3)]
)
def test_spatial_cross_family(module, dim):
    config = {
        "in_channels": 3 if dim == 2 else 5,
        "out_channels": 1 if dim == 2 else 3,
        "spatial_dims": dim,
        "parameters": {"base_channels": 2, "levels": 3, "attention_dim": 16, "num_heads": 2},
    }
    model = module.build_model(config).eval()
    shape = (17, 19) if dim == 2 else (8, 10, 12)
    x = torch.randn(2, config["in_channels"], *shape, requires_grad=True)
    before = {name: value.clone() for name, value in model.state_dict().items()}
    result = model(x)
    assert result.shape == (2, config["out_channels"], *shape)
    result.square().mean().backward()
    assert torch.isfinite(x.grad).all()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    assert any(
        isinstance(m, BasicResidualBlock if module is resunet else TransformerEncoder)
        for m in model.modules()
    )
    assert all(torch.equal(before[k], v) for k, v in model.state_dict().items())
    storage = io.BytesIO()
    torch.save(model.state_dict(), storage)
    storage.seek(0)
    restored = module.build_model(config).eval()
    restored.load_state_dict(torch.load(storage, weights_only=True), strict=True)
    torch.testing.assert_close(restored(x), result)


def test_cnn_rnn_explicit_state_and_spatial_identity():
    config = {
        "in_channels": 4,
        "out_channels": 4,
        "parameters": {"spatial_channels": 4, "hidden_size": 6, "num_layers": 2},
    }
    model = cnn_rnn.build_model(config).eval()
    assert isinstance(model.recurrent, RecurrentStage)
    x = torch.randn(2, 3, 7, 9, 4, requires_grad=True)
    result, state = model.forward_with_state(x)
    assert result.shape == (2, 7, 9, 4) and state.shape == (2, 2 * 7 * 9, 6)
    _, prefix_state = model.forward_with_state(x[:, :1])
    resumed, resumed_state = model.forward_with_state(x[:, 1:], prefix_state)
    torch.testing.assert_close(resumed, result)
    torch.testing.assert_close(resumed_state, state)
    # 一例单独执行验证空间批轴不会跨样本混合。
    torch.testing.assert_close(model(x[:1]), result[:1])
    result.square().mean().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    restored = cnn_rnn.build_model(config).eval()
    storage = io.BytesIO()
    torch.save(model.state_dict(), storage)
    storage.seek(0)
    restored.load_state_dict(torch.load(storage, weights_only=True))
    torch.testing.assert_close(restored(x), result)
    with pytest.raises(ValueError, match="状态"):
        model.forward_with_state(x, torch.zeros(2, 1, 6))


def test_user_output_saved_and_consumed(tmp_path):
    prediction = np.array([[[3.0, 4.0], [5.0, 12.0]]], dtype=np.float32)
    valid = np.ones((1, 2), dtype=bool)
    new, declarations = user_outputs.derive(
        {"prediction": prediction}, {"unit": "m/s", "entity": "grid", "mask": "valid"}
    )
    np.save(tmp_path / "norm.npy", new["prediction_norm"])
    loaded = np.load(tmp_path / "norm.npy")
    np.testing.assert_array_equal(loaded[..., 0], [[5.0, 13.0]])
    summary = user_outputs.consume({"prediction_norm": loaded, "valid": valid}, declarations)
    assert summary["prediction_norm"] == {"shape": [1, 2, 1], "finite": True, "unit": "m/s"}
    np.testing.assert_array_equal(prediction, [[[3, 4], [5, 12]]])
