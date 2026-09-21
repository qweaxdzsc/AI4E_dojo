"""FLARE++：锁定上游、独立公式、真实更新恢复和可选组件边界。"""

import ast
import copy
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path

import pytest
import torch
from einops import rearrange
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "packages/ai4e-core/abilities/modeling/modules/flare_attention.py"


@pytest.fixture(scope="module")
def layer():
    """先测工作树源码，安装副本由独立 wheel 用例核验。"""
    spec = importlib.util.spec_from_file_location("dojo_flare_source", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FLAREPlusPlus


@pytest.fixture(scope="module")
def reference():
    """抽取锁定原类原样运行，不导入上游框架或更改数值正文。"""
    path = ROOT / "tests/fixtures/flare_plus_plus/upstream.py.txt"
    provenance = json.loads(
        (ROOT / "packages/ai4e-core/Notice/physicsnemo/flare_plus_plus.json").read_text()
    )
    assert hashlib.sha256(path.read_bytes()).hexdigest() == provenance["source_sha256"]
    source = ast.parse(path.read_text())
    cls = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == "FLAREPlusPlus")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    tree = ast.fix_missing_locations(ast.Module(body=[future, cls], type_ignores=[]))
    namespace = {"math": math, "torch": torch, "nn": nn, "F": F, "rearrange": rearrange}
    exec(compile(tree, str(path), "exec"), namespace)  # noqa: S102 - 固定摘要的上游类数值对照
    return namespace["FLAREPlusPlus"]


@pytest.mark.parametrize(
    "tokens,heads,dim_head,queries,scale", [(1, 2, 3, 4, None), (11, 3, 4, 5, 0.7)]
)
@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_upstream_forward_gradients_and_update(
    layer, reference, tokens, heads, dim_head, queries, scale, dtype
):
    torch.manual_seed(123)
    args = {
        "dim": 9,
        "heads": heads,
        "dim_head": dim_head,
        "n_global_queries": queries,
        "attn_scale": scale,
    }
    upstream, local = reference(**args).to(dtype), layer(**args).to(dtype)
    local.load_state_dict(upstream.state_dict(), strict=True)
    # 切片得到非连续输入；内部宽度可与输入宽度不同。
    data = torch.randn(2, tokens * 2, 9, dtype=dtype)
    x = data[:, ::2].requires_grad_()
    z = data.clone()[:, ::2].requires_grad_()
    expected, actual = upstream(x), local(z)
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    expected.square().mean().backward()
    actual.square().mean().backward()
    torch.testing.assert_close(x.grad, z.grad, rtol=0, atol=0)
    for (name, a), (other, b) in zip(
        upstream.named_parameters(), local.named_parameters(), strict=True
    ):
        assert name == other
        assert torch.isfinite(b.grad).all()
        torch.testing.assert_close(a.grad, b.grad, rtol=0, atol=0)
    for model in (upstream, local):
        torch.optim.Adam(model.parameters(), lr=0.002).step()
    for name, value in upstream.state_dict().items():
        torch.testing.assert_close(local.state_dict()[name], value, rtol=0, atol=0)


def test_explicit_softmax_formula(layer):
    """不用 SDPA 的独立公式核对，避免只比较同一库调用。"""
    torch.manual_seed(4)
    m = layer(6, heads=2, dim_head=3, n_global_queries=4, attn_scale=0.4).double()
    x = torch.randn(2, 7, 6, dtype=torch.float64, requires_grad=True)
    qk, qv, pk, pv = [
        v.reshape(2, 7, 2, 3).transpose(1, 2) for v in m.in_projection(x).chunk(4, -1)
    ]

    def attention(q, k, v):
        return ((q @ k.transpose(-2, -1)) * 0.4).softmax(-1) @ v

    q = attention(m.q_seed.expand(2, -1, -1, -1), qk, qv)
    y = attention(pk, q, attention(q, pk, pv)).transpose(1, 2).reshape(2, 7, 6)
    expected, actual = m.out_linear(y), m(x)
    torch.testing.assert_close(actual, expected, rtol=1e-12, atol=1e-12)
    variables = (x, *m.parameters())
    a = torch.autograd.grad(actual.square().sum(), variables)
    b = torch.autograd.grad(expected.square().sum(), variables)
    for left, right in zip(a, b, strict=True):
        torch.testing.assert_close(left, right, rtol=1e-10, atol=1e-12)


def test_permutation_eval_and_input_conditioning(layer):
    torch.manual_seed(5)
    m = layer(8, heads=2, dim_head=4, n_global_queries=3, dropout=0.4).eval()
    x = torch.randn(2, 9, 8)
    order = torch.randperm(9)
    state = torch.random.get_rng_state().clone()
    with torch.no_grad():
        y = m(x)
        assert torch.equal(y, m(x))
        torch.testing.assert_close(m(x[:, order]), y[:, order])
    assert torch.equal(state, torch.random.get_rng_state())
    # 随样本变化的路由，非一套固定 queries。
    qk, qv, _, _ = m.in_projection(torch.stack([torch.zeros(9, 8), torch.ones(9, 8)])).chunk(4, -1)
    q = F.scaled_dot_product_attention(
        m.q_seed.expand(2, -1, -1, -1),
        qk.reshape(2, 9, 2, 4).transpose(1, 2),
        qv.reshape(2, 9, 2, 4).transpose(1, 2),
        scale=m.scale,
    )
    assert not torch.allclose(q[0], q[1])


def test_training_resume_and_fixed_readback(layer):
    torch.manual_seed(10)
    x, target = torch.randn(2, 9, 8), torch.randn(2, 9, 8)
    m = layer(8, heads=2, dim_head=4, n_global_queries=3, dropout=0.2)
    opt = torch.optim.Adam(m.parameters(), lr=0.001)
    initial = copy.deepcopy(m.state_dict())

    def advance(model, optimizer):
        optimizer.zero_grad()
        loss = (model(x) - target).square().mean()
        loss.backward()
        optimizer.step()

    for _ in range(2):
        advance(m, opt)
    saved = io.BytesIO()
    torch.save(
        {"model": m.state_dict(), "optimizer": opt.state_dict(), "rng": torch.get_rng_state()},
        saved,
    )
    for _ in range(2):
        advance(m, opt)
    restored = layer(8, heads=2, dim_head=4, n_global_queries=3, dropout=0.2)
    ropt = torch.optim.Adam(restored.parameters(), lr=0.001)
    saved.seek(0)
    checkpoint = torch.load(saved, weights_only=True)
    restored.load_state_dict(checkpoint["model"])
    ropt.load_state_dict(checkpoint["optimizer"])
    torch.set_rng_state(checkpoint["rng"])
    for _ in range(2):
        advance(restored, ropt)
    for name, value in m.state_dict().items():
        torch.testing.assert_close(restored.state_dict()[name], value, rtol=0, atol=0)
    assert any(not torch.equal(initial[k], v) for k, v in m.state_dict().items())
    with torch.no_grad():
        expected = m.eval()(x)
        actual = restored.eval()(x)
    fixed = io.BytesIO()
    torch.save(actual, fixed)
    fixed.seek(0)
    torch.testing.assert_close(torch.load(fixed, weights_only=True), expected, rtol=0, atol=0)


@pytest.mark.parametrize(
    "options",
    [
        {"dim": 0},
        {"heads": 0},
        {"heads": True},
        {"dim_head": -1},
        {"n_global_queries": 0},
        {"n_global_queries": 1.5},
        {"dropout": -0.1},
        {"dropout": float("nan")},
        {"attn_scale": 0},
        {"attn_scale": float("inf")},
        {"attn_scale": float("nan")},
        {"use_te": True},
    ],
)
def test_invalid_constructor(layer, options):
    with pytest.raises(ValueError):
        layer(**{"dim": 8, **options})


@pytest.mark.parametrize("shape", [(3, 8), (1, 0, 8), (1, 3, 7), (1, 2, 3, 8)])
def test_invalid_shape(layer, shape):
    with pytest.raises(ValueError):
        layer(8)(torch.ones(shape))


def test_unsupported_input(layer):
    with pytest.raises(TypeError, match="浮点"):
        layer(8)(torch.ones(1, 2, 8, dtype=torch.int64))

    class Sharded:
        redistribute = True

    with pytest.raises(NotImplementedError, match="分片"):
        layer(8)(Sharded())


def test_autocast_cpu_matches_reference(layer, reference):
    torch.manual_seed(2)
    m = layer(8, heads=2, dim_head=4, n_global_queries=3)
    ref = reference(8, heads=2, dim_head=4, n_global_queries=3)
    ref.load_state_dict(m.state_dict())
    x = torch.randn(2, 7, 8)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        actual, expected = m(x), ref(x)
        loss = actual.float().square().mean()
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    loss.backward()
    assert all(torch.isfinite(p.grad).all() for p in m.parameters())
