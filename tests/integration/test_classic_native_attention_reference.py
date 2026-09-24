"""原生注意力 oracle 的算术分支与梯度；无训练和优化器更新。"""

import copy

import pytest
import torch

from ai4e_core.abilities.modeling.models.transformer import PatchTransformer
from ai4e_core.abilities.modeling.modules.attention import CrossAttention, SelfAttention
from tools.verification.classic_networks import reference_interactions as reference

DEVICES = ["cpu"] + (["mps"] if torch.backends.mps.is_available() else [])


def forbidden(*args, **kwargs):
    raise AssertionError("oracle must not call a production forward")


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("mode", ["train", "eval_grad", "eval_no_grad"])
@pytest.mark.parametrize("mask_kind", ["padding", "bool", "float", "heads"])
def test_native_attention_dispatch_masks_and_gradients(device, mode, mask_kind, monkeypatch):
    torch.manual_seed(418)
    production = SelfAttention(8, 2).to(device)
    production.train(mode == "train")
    oracle = copy.deepcopy(production)
    value = torch.randn(2, 5, 8, device=device, requires_grad=True)
    other = value.detach().clone().requires_grad_()
    padding = torch.zeros(2, 5, device=device, dtype=torch.bool)
    padding[0, -1] = True
    mask = torch.triu(torch.ones(5, 5, device=device, dtype=torch.bool), diagonal=1)
    if mask_kind == "padding":
        mask = None
    elif mask_kind == "float":
        mask = torch.zeros_like(mask, dtype=torch.float32).masked_fill(mask, -torch.inf)
    elif mask_kind == "heads":
        mask = mask.unsqueeze(0).expand(4, -1, -1).clone()
    call_args = {"key_padding_mask": padding, "attn_mask": mask}
    expected_route = (
        "fast"
        if (device == "cpu" and mode == "eval_no_grad" and mask_kind != "float")
        else "functional"
    )
    observed = []
    functional = reference.F.multi_head_attention_forward
    native = torch._native_multi_head_attention

    def trace_functional(query, key, val, *args, **kwargs):
        assert query is key is val  # 一次 packed QKV；三个独立投影不能替代此检查。
        observed.append("functional")
        return functional(query, key, val, *args, **kwargs)

    def trace_native(*args, **kwargs):
        observed.append("fast")
        return native(*args, **kwargs)

    with torch.set_grad_enabled(mode != "eval_no_grad"):
        expected = production(value, **call_args)
        monkeypatch.setattr(oracle.attention, "forward", forbidden)
        monkeypatch.setattr(reference.F, "multi_head_attention_forward", trace_functional)
        monkeypatch.setattr(torch, "_native_multi_head_attention", trace_native)
        actual = reference.native_attention(oracle, other, other, **call_args)
        assert observed == [expected_route]
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)
        if mode != "eval_no_grad":
            expected.square().sum().backward()
            actual.square().sum().backward()
            torch.testing.assert_close(other.grad, value.grad, rtol=0, atol=0)
            for left, right in zip(production.parameters(), oracle.parameters(), strict=True):
                torch.testing.assert_close(left.grad, right.grad, rtol=0, atol=0)


@pytest.mark.parametrize("device", DEVICES)
def test_native_cross_attention_separate_projection(device):
    torch.manual_seed(419)
    module = CrossAttention(8, 2, context_dim=6).to(device)
    query, context = torch.randn(2, 3, 8, device=device), torch.randn(2, 5, 6, device=device)
    torch.testing.assert_close(
        module(query, context), reference.native_attention(module, query, context), rtol=0, atol=0
    )


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("shape,patch", [((9, 11), (2, 3)), ((5, 6, 7), (2, 2, 2))])
def test_complete_native_transformer_parameter_gradients_without_core_forward(
    device, shape, patch, monkeypatch
):
    torch.manual_seed(420)
    production = PatchTransformer(
        3, 2, patch_shape=patch, dim=12, num_heads=2, num_layers=2, feed_forward_dim=16
    ).to(device)
    oracle = reference.reference_model(production, attention_backend="torch_native")
    value = torch.randn(1, *shape, 3, device=device, requires_grad=True)
    other = value.detach().clone().requires_grad_()
    mask = torch.ones(1, *shape, device=device, dtype=torch.bool)
    mask[(0, *([slice(0, 2)] * len(shape)))] = False
    output = production(value, mask)
    # 所有原子/阶段/模型 forward 禁用，参数和形状只读映射。
    for module in oracle.modules():
        if module is not oracle:
            monkeypatch.setattr(module, "forward", forbidden)
    actual = oracle(other, mask)
    torch.testing.assert_close(output, actual, rtol=1e-5, atol=1e-6)
    output.square().mean().backward()
    actual.square().mean().backward()
    torch.testing.assert_close(value.grad, other.grad, rtol=1e-5, atol=1e-6)
    for name, parameter in production.named_parameters():
        torch.testing.assert_close(
            parameter.grad,
            dict(oracle.named_parameters())[name].grad,
            rtol=1e-5,
            atol=1e-6,
            msg=lambda message, name=name: name + ": " + message,
        )


def test_reference_backend_explicit_default_and_validation():
    model = PatchTransformer(3, 1, dim=8, num_heads=2, num_layers=1)
    assert reference.reference_model(model).forward.__func__ is reference.patch_transformer
    assert reference.reference_model(model, attention_backend="torch_native").forward.__func__ is (
        reference.native_patch_transformer
    )
    with pytest.raises(ValueError, match="attention_backend"):
        reference.reference_model(model, attention_backend="unknown")


def test_reference_relu_retains_pytorch_zero_subgradient():
    value = torch.tensor([0.0], requires_grad=True)
    reference.dense(torch.nn.ReLU(), value).sum().backward()
    torch.testing.assert_close(value.grad, torch.zeros_like(value))
