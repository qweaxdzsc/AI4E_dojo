"""多层循环段的原生参考、显式重组、状态梯度与内存保存读回。"""

import io

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock
from ai4e_core.abilities.modeling.stages.recurrent import RecurrentStage
from tools.verification.classic_networks.reference_features import recurrent_weights


@pytest.mark.parametrize("layers", [1, 2, 3])
def test_stage_matches_native_layers_and_gradients(layers):
    torch.manual_seed(9)
    stage = RecurrentStage(4, hidden_size=5, num_layers=layers)
    reference = nn.RNN(4, 5, layers, batch_first=True)
    reference.load_state_dict(recurrent_weights(stage.state_dict(), num_layers=layers), strict=True)
    x = torch.randn(2, 4, 4, requires_grad=True)
    other = x.detach().clone().requires_grad_()
    state = torch.randn(layers, 2, 5, requires_grad=True)
    other_state = state.detach().clone().requires_grad_()
    output, final = stage(x, state)
    expected, expected_final = reference(other, other_state)
    torch.testing.assert_close(output, expected, rtol=1e-5, atol=1e-6)
    torch.testing.assert_close(final, expected_final, rtol=1e-5, atol=1e-6)
    (output.square().sum() + final.square().sum()).backward()
    (expected.square().sum() + expected_final.square().sum()).backward()
    torch.testing.assert_close(x.grad, other.grad, rtol=1e-5, atol=1e-6)
    torch.testing.assert_close(state.grad, other_state.grad, rtol=1e-5, atol=1e-6)
    parameters = recurrent_weights(dict(stage.named_parameters()), num_layers=layers)
    for name, parameter in reference.named_parameters():
        torch.testing.assert_close(parameters[name].grad, parameter.grad, rtol=1e-5, atol=1e-6)


def test_stage_composition_and_state_save_readback():
    blocks = [RecurrentBlock(4, 5), RecurrentBlock(5, 5)]
    stage = RecurrentStage(4, 5, blocks=blocks)
    assert stage.blocks[0] is blocks[0]
    x = torch.randn(2, 6, 4)
    complete, final = stage(x)
    first, state = stage(x[:, :3])
    stream = io.BytesIO()
    torch.save({"weights": stage.state_dict(), "state": state}, stream)
    stream.seek(0)
    saved = torch.load(stream, weights_only=True)
    restored = RecurrentStage(4, 5)
    restored.load_state_dict(saved["weights"], strict=True)
    second, restored_state = restored(x[:, 3:], saved["state"])
    torch.testing.assert_close(torch.cat((first, second), dim=1), complete)
    torch.testing.assert_close(restored_state, final)
    # 继续梯度必须穿过传入状态；调用者可选择显式 detach，但阶段本身不做。
    first_state = state.detach().clone().requires_grad_()
    restored(x[:, 3:], first_state)[0].sum().backward()
    assert first_state.grad is not None and first_state.grad.abs().sum() > 0


def test_stage_rejects_invalid_layer_contract():
    with pytest.raises(ValueError, match="数量"):
        RecurrentStage(4, 5, blocks=[RecurrentBlock(4, 5)])
    stage = RecurrentStage(4, 5, blocks=[RecurrentBlock(4, 6), RecurrentBlock(5, 5)])
    with pytest.raises(ValueError, match="替换"):
        stage(torch.zeros(2, 3, 4))
    with pytest.raises(ValueError, match="状态"):
        RecurrentStage(4, 5)(torch.zeros(2, 3, 4), torch.zeros(1, 2, 5))


def test_reference_mapping_rejects_extra_parameters():
    state = dict(RecurrentStage(4, 5).state_dict())
    state["extra.weight"] = torch.ones(1)
    with pytest.raises(ValueError, match="集合"):
        recurrent_weights(state, num_layers=2)
