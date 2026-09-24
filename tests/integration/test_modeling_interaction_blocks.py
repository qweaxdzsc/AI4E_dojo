"""注意力、编码与空间分块的独立非训练数值测试。"""

import copy

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.attention import CrossAttention, SelfAttention
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding, patch_centers
from ai4e_core.abilities.modeling.modules.patch_reconstruction import PatchReconstruction
from ai4e_core.abilities.modeling.modules.transformer import EncoderBlock
from ai4e_core.abilities.modeling.stages.transformer import TransformerEncoder
from tools.verification.classic_networks import reference_interactions as reference


def compare(actual, expected):
    torch.testing.assert_close(actual, expected, atol=1e-10, rtol=1e-8)


@pytest.mark.parametrize("context_dim", [8, 6])
def test_cross_attention_independent_forward_backward_and_mask(context_dim):
    torch.manual_seed(41)
    model = CrossAttention(8, 2, context_dim=context_dim).double()
    clone = copy.deepcopy(model)
    q = torch.randn(2, 3, 8, dtype=torch.float64, requires_grad=True)
    k = torch.randn(2, 5, context_dim, dtype=torch.float64, requires_grad=True)
    qr, kr = q.detach().clone().requires_grad_(), k.detach().clone().requires_grad_()
    padding = torch.tensor([[False, False, True, False, True], [False, True, False, True, False]])
    mask = torch.zeros(3, 5, dtype=torch.float64)
    mask[0, 1] = -torch.inf
    actual = model(q, k, key_padding_mask=padding, attn_mask=mask)
    expected = reference.attention(clone, qr, kr, key_padding_mask=padding, attn_mask=mask)
    compare(actual, expected)
    actual.square().sum().backward()
    expected.square().sum().backward()
    compare(q.grad, qr.grad)
    compare(k.grad, kr.grad)
    for a, b in zip(model.parameters(), clone.parameters(), strict=True):
        compare(a.grad, b.grad)
    modified = k.detach().clone()
    modified[padding] = 10000
    compare(model(q, modified, key_padding_mask=padding, attn_mask=mask), actual)


def test_self_attention_reference_and_mask_failures():
    model = SelfAttention(8, 2).double()
    x = torch.randn(2, 4, 8, dtype=torch.float64)
    mask = torch.triu(torch.ones(4, 4, dtype=torch.bool), diagonal=1)
    compare(model(x, attn_mask=mask), reference.attention(model, x, x, attn_mask=mask))
    with pytest.raises(ValueError, match="全部键"):
        model(x, key_padding_mask=torch.ones(2, 4, dtype=torch.bool))
    with pytest.raises(ValueError, match="全部键"):
        model(x, attn_mask=torch.ones(4, 4, dtype=torch.bool))
    with pytest.raises(ValueError, match="形状"):
        model(x, attn_mask=torch.zeros(3, 4, dtype=torch.bool))


def test_postnorm_encoder_matches_independent_and_pytorch_layer():
    torch.manual_seed(71)
    block = EncoderBlock(8, 2, feed_forward_dim=12).double()
    clone = copy.deepcopy(block)
    upstream = nn.TransformerEncoderLayer(
        8, 2, 12, dropout=0, batch_first=True, norm_first=False
    ).double()
    upstream.self_attn.load_state_dict(block.attention.attention.state_dict())
    linears = [m for m in block.feed_forward.modules() if isinstance(m, nn.Linear)]
    upstream.linear1.load_state_dict(linears[0].state_dict())
    upstream.linear2.load_state_dict(linears[1].state_dict())
    upstream.norm1.load_state_dict(block.norm1.state_dict())
    upstream.norm2.load_state_dict(block.norm2.state_dict())
    x = torch.randn(2, 4, 8, dtype=torch.float64, requires_grad=True)
    xr = x.detach().clone().requires_grad_()
    padding = torch.tensor([[False, False, False, True], [False, True, False, False]])
    output = block(x, key_padding_mask=padding)
    expected = reference.encoder_block(clone, xr, key_padding_mask=padding)
    compare(output, expected)
    compare(output, upstream(x, src_key_padding_mask=padding))
    output.square().sum().backward()
    expected.square().sum().backward()
    compare(x.grad, xr.grad)
    for a, b in zip(block.parameters(), clone.parameters(), strict=True):
        compare(a.grad, b.grad)
    assert isinstance(block.feed_forward, FeedForward)


def test_encoder_stage_explicit_composition_and_injection():
    first = EncoderBlock(
        8, 2, feed_forward=FeedForward(8, 8, hidden_features=(7, 5), activation="relu")
    ).double()
    second = EncoderBlock(8, 2).double()
    encoder = TransformerEncoder([first, second])
    x = torch.randn(1, 3, 8, dtype=torch.float64)
    compare(encoder(x), second(first(x)))
    assert any("feed_forward" in name for name, _ in encoder.named_parameters())


@pytest.mark.parametrize("shape,patch", [((3, 5), (2, 3)), ((3, 4, 5), (2, 3, 2))])
def test_patch_identity_projection_roundtrip_layout_and_masks(shape, patch):
    count = torch.Size(patch).numel()
    embedding = PatchEmbedding(1, count, patch).double()
    reconstruction = PatchReconstruction(count, 1, patch).double()
    with torch.no_grad():
        for linear in (embedding.projection, reconstruction.projection):
            linear.weight.copy_(torch.eye(count, dtype=torch.float64))
            linear.bias.zero_()
    x = torch.arange(torch.Size(shape).numel(), dtype=torch.float64).reshape(1, *shape, 1)
    valid = torch.ones(1, *shape, dtype=torch.bool)
    valid[(0, *([0] * len(shape)))] = False
    tokens, ignored, info = embedding(x, valid)
    result = reconstruction(tokens, info)
    compare(result, x.masked_fill(~valid.unsqueeze(-1), 0))
    centers = patch_centers(info)
    assert centers.shape == (tokens.shape[1], len(shape))
    assert ((centers > 0) & (centers < 1)).all()
    assert ignored.shape == tokens.shape[:2]
    with pytest.raises(ValueError, match="token"):
        reconstruction(tokens[:, :-1], info)
    with pytest.raises(ValueError, match="有效格点"):
        embedding(x, torch.zeros_like(valid))


def test_patch_all_invalid_blocks_and_partial_valid_blocks():
    model = PatchEmbedding(2, 8, (2, 2))
    x = torch.ones(1, 4, 4, 2)
    valid = torch.zeros(1, 4, 4, dtype=torch.bool)
    valid[0, 0, 0] = True
    _, mask, _ = model(x, valid)
    assert mask.tolist() == [[False, True, True, True]]


def test_existing_position_fp32_unchanged_and_double_buffer_supported():
    from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed

    encoding = ContinuousSincosEmbed(12, 3)
    coords = torch.rand(7, 3)
    angles = coords.unsqueeze(-1) @ encoding.omega.unsqueeze(0)
    original = torch.cat((angles.sin(), angles.cos()), -1).reshape(7, -1)
    torch.testing.assert_close(encoding(coords), original, atol=0, rtol=0)
    encoding.double()
    torch.testing.assert_close(encoding(coords.double()), original, atol=0, rtol=0)
    assert encoding.omega.dtype == torch.float64
