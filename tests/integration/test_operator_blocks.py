"""算子组件的非训练对照：查询身份、上游算术、频率、梯度与状态。

真实上游测试需 DOJO_OPERATOR_REFERENCE_CACHE 指向锁定源码目录；未准备则
明确 skip。统一训练由主控在归并后执行，本文件不创建优化器或更新权重。
"""

import copy
import itertools
import math
import os

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.models.deeponet import DeepONet
from ai4e_core.abilities.modeling.models.fno import FNO
from ai4e_core.abilities.modeling.modules.branch_trunk import BranchTrunkReadout
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock, SpectralConv
from ai4e_core.abilities.modeling.stages.fourier import FourierStage
from tools.verification.operator_surrogates.reference_operators import (
    DeepONetReference,
    FNOReference,
    SpectralReference,
    copy_deeponet_weights,
    copy_fno_weights,
    corners_to_center,
    load_sources,
)


@pytest.fixture(scope="module", autouse=True)
def one_thread():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


@pytest.fixture(scope="module")
def upstream():
    root = os.environ.get("DOJO_OPERATOR_REFERENCE_CACHE")
    if root is None:
        pytest.skip("未提供锁定上游源码；不是参考验证通过")
    return load_sources(root)


@pytest.mark.parametrize("strategy", [None, "split_branch", "split_trunk", "split_both"])
def test_readout_queries_outputs_and_gradients(strategy):
    torch.manual_seed(73)
    outputs = 1 if strategy is None else 3
    readout = BranchTrunkReadout(4, outputs, strategy).double()
    branch = torch.randn(2, readout.branch_width, dtype=torch.float64, requires_grad=True)
    trunk = torch.randn(5, readout.trunk_width, dtype=torch.float64, requires_grad=True)
    shared = readout(branch, trunk, query_layout="shared")
    expected = []
    for b in range(2):
        rows = []
        for q in range(5):
            rows.append(
                torch.stack(
                    [
                        (
                            branch[b, o * 4 : (o + 1) * 4]
                            if strategy in ("split_branch", "split_both")
                            else branch[b]
                        ).dot(
                            trunk[q, o * 4 : (o + 1) * 4]
                            if strategy in ("split_trunk", "split_both")
                            else trunk[q]
                        )
                        for o in range(outputs)
                    ]
                )
            )
        expected.append(torch.stack(rows))
    torch.testing.assert_close(shared, torch.stack(expected))
    personal = readout(branch, torch.stack((trunk, trunk.flip(0))), query_layout="per_sample")
    torch.testing.assert_close(shared[0], personal[0])
    torch.testing.assert_close(shared[1].flip(0), personal[1])
    assert not torch.allclose(shared[1], personal[1])
    shared.square().mean().backward()
    assert branch.grad.abs().sum() > 0 and trunk.grad.abs().sum() > 0
    assert readout.bias.grad.shape == (outputs,)


def test_readout_rejects_implicit_layout_width_batch_and_strategy():
    with pytest.raises(ValueError, match="单输出"):
        BranchTrunkReadout(4, 2)
    with pytest.raises(ValueError, match="单输出"):
        BranchTrunkReadout(4, 1, "split_branch")
    readout = BranchTrunkReadout(4)
    for branch, trunk, layout in [
        (torch.ones(2, 3), torch.ones(3, 4), "shared"),
        (torch.ones(2, 4), torch.ones(1, 3, 4), "per_sample"),
        (torch.ones(2, 4), torch.ones(2, 3, 4), "shared"),
        (torch.ones(2, 4), torch.ones(3, 4), "paired"),
    ]:
        with pytest.raises(ValueError):
            readout(branch, trunk, query_layout=layout)


@pytest.mark.parametrize("strategy", [None, "split_branch", "split_trunk", "split_both"])
@pytest.mark.parametrize("layout", ["shared", "per_sample"])
def test_deeponet_matches_original_deepxde_strategy(upstream, strategy, layout):
    torch.manual_seed(37)
    outputs = 1 if strategy is None else 2
    model = DeepONet(3, 2, 4, outputs, strategy, branch_hidden=(7,), trunk_hidden=(6,)).double()
    reference = DeepONetReference(
        upstream,
        (3, 7, model.readout.branch_width),
        (2, 6, model.readout.trunk_width),
        out_channels=outputs,
        multi_output=strategy,
    ).double()
    copy_deeponet_weights(reference, model)
    branch = torch.randn(2, 3, dtype=torch.float64, requires_grad=True)
    shape = (5, 2) if layout == "shared" else (2, 5, 2)
    queries = torch.randn(shape, dtype=torch.float64, requires_grad=True)
    ref_branch, ref_queries = [v.detach().clone().requires_grad_() for v in (branch, queries)]
    actual, expected = (
        model(branch, queries, query_layout=layout),
        reference(ref_branch, ref_queries, query_layout=layout),
    )
    torch.testing.assert_close(actual, expected, atol=2e-14, rtol=2e-13)
    actual.square().mean().backward()
    expected.square().mean().backward()
    torch.testing.assert_close(branch.grad, ref_branch.grad)
    torch.testing.assert_close(queries.grad, ref_queries.grad)
    actual_linears = [m for m in model.modules() if isinstance(m, nn.Linear)]
    ref_linears = [m for m in reference.modules() if isinstance(m, nn.Linear)]
    for a, b in zip(actual_linears, ref_linears, strict=True):
        torch.testing.assert_close(a.weight.grad, b.weight.grad)
        assert a.weight.grad.abs().sum() > 0


def _direct_dft(value, weight, modes, norm):
    """显式指数矩阵 DFT/实逆变换；不调用 FFT 或生产频率切片。"""
    sizes = value.shape[2:]
    points = torch.tensor(list(itertools.product(*(range(n) for n in sizes))), dtype=torch.float64)
    frequencies = list(
        itertools.product(*(range(n) for n in sizes[:-1]), range(sizes[-1] // 2 + 1))
    )
    k = torch.tensor(frequencies, dtype=torch.float64)
    phase = (points / torch.tensor(sizes)) @ k.T
    basis = torch.exp(-2j * math.pi * phase)
    count = math.prod(sizes)
    scale = 1 / count if norm == "forward" else 1 / math.sqrt(count) if norm == "ortho" else 1
    spectrum = torch.einsum("bip,pf->bif", value.flatten(2).to(torch.complex128), basis) * scale
    mapped = []
    for f, frequency in enumerate(frequencies):
        index, corner, keep = [], 0, True
        for n, m, frequency_i in zip(sizes[:-1], modes[:-1], frequency[:-1], strict=True):
            corner *= 2
            if frequency_i < m:
                index.append(frequency_i)
            elif frequency_i >= n - m:
                corner += 1
                index.append(frequency_i - (n - m))
            else:
                keep = False
        if frequency[-1] >= modes[-1]:
            keep = False
        if keep:
            index.append(frequency[-1])
            mapped.append(spectrum[..., f] @ weight[(corner, slice(None), slice(None), *index)])
        else:
            mapped.append(spectrum.new_zeros(value.shape[0], weight.shape[2]))
    mapped = torch.stack(mapped, dim=-1)
    multiplicity = torch.tensor(
        [
            1 if f[-1] == 0 or (sizes[-1] % 2 == 0 and f[-1] == sizes[-1] // 2) else 2
            for f in frequencies
        ],
        dtype=torch.complex128,
    )
    inverse = 1 if norm == "forward" else 1 / math.sqrt(count) if norm == "ortho" else 1 / count
    result = torch.einsum("bof,pf,f->bop", mapped, basis.conj(), multiplicity).real * inverse
    return result.reshape(value.shape[0], weight.shape[2], *sizes)


@pytest.mark.parametrize(
    "sizes,modes",
    [((5, 7), (2, 3)), ((6, 8), (3, 5)), ((4, 5, 6), (2, 2, 4)), ((5, 4, 5), (2, 2, 2))],
)
@pytest.mark.parametrize("norm", ["forward", "backward", "ortho"])
def test_spectral_fp64_against_independent_direct_dft(sizes, modes, norm):
    torch.manual_seed(19)
    model = SpectralConv(2, 3, modes, fft_norm=norm, dtype=torch.float64)
    value = torch.randn(2, 2, *sizes, dtype=torch.float64, requires_grad=True)
    actual = model(value)
    expected = _direct_dft(value, model.weight, modes, norm)
    torch.testing.assert_close(actual, expected, rtol=3e-12, atol=3e-12)
    gradients = torch.autograd.grad(
        actual.square().mean(), (value, model.weight_parts), retain_graph=True
    )
    ref_gradients = torch.autograd.grad(expected.square().mean(), (value, model.weight_parts))
    for a, b in zip(gradients, ref_gradients, strict=True):
        torch.testing.assert_close(a, b, rtol=3e-11, atol=3e-12)


@pytest.mark.parametrize(
    "sizes,modes", [((7, 9), (2, 3)), ((8, 10), (4, 6)), ((5, 6, 7), (2, 3, 4))]
)
def test_spectral_matches_original_neuraloperator(upstream, sizes, modes):
    torch.manual_seed(23)
    model = SpectralConv(2, 3, modes)
    reference = SpectralReference(upstream, 2, 3, modes)
    with torch.no_grad():
        reference.weight.copy_(corners_to_center(model.weight))
    value = torch.randn(2, 2, *sizes, requires_grad=True)
    ref_value = value.detach().clone().requires_grad_()
    actual, expected = model(value), reference(ref_value)
    torch.testing.assert_close(actual, expected, rtol=1e-6, atol=1e-6)
    actual.square().mean().backward()
    expected.square().mean().backward()
    torch.testing.assert_close(value.grad, ref_value.grad, rtol=2e-5, atol=2e-7)
    mapped_grad = corners_to_center(torch.view_as_complex(model.weight_parts.grad))
    torch.testing.assert_close(mapped_grad, reference.weight.grad, rtol=2e-5, atol=2e-7)


def test_known_frequency_retention_truncation_dc_and_nyquist():
    model = SpectralConv(1, 1, (2, 3), dtype=torch.float64)
    with torch.no_grad():
        model.weight.fill_(1)
    x = torch.arange(8, dtype=torch.float64)[:, None] / 8
    y = torch.arange(10, dtype=torch.float64)[None, :] / 10
    retained = 3 + torch.cos(2 * torch.pi * x) + torch.sin(2 * torch.pi * y)
    removed = torch.cos(6 * torch.pi * x) + torch.cos(8 * torch.pi * y)
    torch.testing.assert_close(model((retained + removed)[None, None])[0, 0], retained)
    full = SpectralConv(1, 1, (4, 6), dtype=torch.float64)
    with torch.no_grad():
        full.weight.fill_(1)
    nyquist = torch.cos(8 * torch.pi * x) + torch.cos(10 * torch.pi * y)
    torch.testing.assert_close(full(nyquist[None, None])[0, 0], nyquist)


def test_spectral_precision_conversion_and_state_readback(tmp_path):
    model = SpectralConv(2, 3, (2, 3))
    original = model.weight.detach().clone()
    model.double()
    assert model.weight.dtype == torch.complex128
    torch.testing.assert_close(model.weight, original.to(torch.complex128))
    model.to(dtype=torch.float32)
    torch.testing.assert_close(model.weight, original)
    assert model.weight.imag.abs().sum() > 0
    path = tmp_path / "spectral.pt"
    torch.save(model.state_dict(), path)
    restored = SpectralConv(2, 3, (2, 3))
    restored.load_state_dict(torch.load(path, weights_only=True))
    value = torch.randn(2, 2, 7, 9)
    torch.testing.assert_close(model(value), restored(value), rtol=0, atol=0)
    with pytest.raises(ValueError, match="精度"):
        model(value.double())
    with pytest.raises(ValueError, match="精度"):
        model.half()(value.half())


@pytest.mark.parametrize(
    "modes,sizes", [((4, 2), (7, 8)), ((2, 6), (8, 9)), ((2, 4, 2), (6, 7, 8))]
)
def test_spectral_rejects_overlap_and_excess_modes(modes, sizes):
    with pytest.raises(ValueError, match="交叠|越界"):
        SpectralConv(1, 1, modes)(torch.randn(1, 1, *sizes))


@pytest.mark.parametrize(
    "sizes,modes,padding", [((7, 9), (2, 3), (1, 2)), ((5, 6, 7), (2, 2, 3), (1, 0, 2))]
)
def test_fno_full_assembly_upstream_gradients_and_restore(
    upstream, tmp_path, sizes, modes, padding
):
    torch.manual_seed(11)
    config = {"modes": modes, "width": 4, "depth": 2, "padding": padding, "projection_hidden": (5,)}
    model = FNO(3, 2, **config)
    reference = FNOReference(upstream, 3, 2, **config)
    copy_fno_weights(reference, model)
    value = torch.randn(2, 3, *sizes, requires_grad=True)
    ref_value = value.detach().clone().requires_grad_()
    actual, expected = model(value), reference(ref_value)
    assert actual.shape == (2, 2, *sizes)
    torch.testing.assert_close(actual, expected, rtol=2e-6, atol=2e-7)
    actual.square().mean().backward()
    expected.square().mean().backward()
    torch.testing.assert_close(value.grad, ref_value.grad, rtol=1e-4, atol=2e-7)
    for p in model.parameters():
        assert p.grad is not None and torch.isfinite(p.grad).all()
        assert p.grad.abs().sum() > 0
    for block, spectral in zip(model.operator.blocks, reference.spectral, strict=True):
        torch.testing.assert_close(
            corners_to_center(torch.view_as_complex(block.spectral.weight_parts.grad)),
            spectral.weight.grad,
            rtol=1e-4,
            atol=2e-7,
        )
    for block, local in zip(model.operator.blocks, reference.local, strict=True):
        torch.testing.assert_close(
            block.local.conv.weight.grad, local.weight.grad, rtol=1e-4, atol=2e-7
        )
    for left, right in (
        (model.lifting, reference.lifting),
        (model.projection, reference.projection),
    ):
        candidate_layers = [m for m in left.modules() if isinstance(m, nn.Linear)]
        reference_layers = [m for m in right.modules() if isinstance(m, nn.Linear)]
        for a, b in zip(candidate_layers, reference_layers, strict=True):
            torch.testing.assert_close(a.weight.grad, b.weight.grad, rtol=1e-4, atol=2e-7)
    saved = tmp_path / "fno.pt"
    torch.save(model.state_dict(), saved)
    restored = FNO(3, 2, **config)
    restored.load_state_dict(torch.load(saved, weights_only=True))
    torch.testing.assert_close(restored(value), actual, atol=0, rtol=0)


def test_public_component_reconstruction_and_replacement(tmp_path):
    torch.manual_seed(43)
    original = DeepONet(3, 2, 5, branch_hidden=(6,), trunk_hidden=(7,)).double()
    rebuilt = DeepONet(
        3,
        2,
        5,
        branch=copy.deepcopy(original.branch),
        trunk=copy.deepcopy(original.trunk),
        readout=copy.deepcopy(original.readout),
    )
    branch, queries = torch.randn(2, 3, dtype=torch.float64), torch.randn(4, 2, dtype=torch.float64)
    torch.testing.assert_close(original(branch, queries), rebuilt(branch, queries), rtol=0, atol=0)
    # 有意义的替换：缩小分支和主干编码器，保持读出合同和坐标梯度。
    changed = DeepONet(
        3, 2, 5, branch=nn.Linear(3, 5), trunk=nn.Sequential(nn.Linear(2, 5), nn.Tanh())
    ).double()
    q = queries.clone().requires_grad_()
    changed(branch, q).square().mean().backward()
    assert q.grad.abs().sum() > 0
    assert changed.branch.weight.grad.abs().sum() > 0
    path = tmp_path / "deeponet.pt"
    torch.save(changed.state_dict(), path)
    twin = copy.deepcopy(changed)
    twin.load_state_dict(torch.load(path, weights_only=True))
    torch.testing.assert_close(changed(branch, q), twin(branch, q), atol=0, rtol=0)
    fno = FNO(2, 1, modes=(2, 3), width=4, depth=2, padding=(1, 2), projection_hidden=(5,))
    assert isinstance(fno.lifting, FeedForward) and isinstance(fno.projection, FeedForward)
    assert isinstance(fno.operator, FourierStage)
    assert isinstance(fno.operator.blocks[0].local, ConvBlock)
    reconstructed = FNO(
        2,
        1,
        modes=(2, 3),
        width=4,
        padding=(1, 2),
        lifting=copy.deepcopy(fno.lifting),
        operator=copy.deepcopy(fno.operator),
        projection=copy.deepcopy(fno.projection),
    )
    x = torch.randn(2, 2, 7, 9, requires_grad=True)
    torch.testing.assert_close(fno(x), reconstructed(x), atol=0, rtol=0)
    replacement = FourierStage(
        [FourierBlock(4, 4, (2, 3), local=nn.Conv2d(4, 4, 1), activation="none")]
    )
    reconstructed.operator = replacement
    reconstructed(x).square().mean().backward()
    assert x.grad.abs().sum() > 0
    assert replacement.blocks[0].local.weight.grad.abs().sum() > 0
    assert replacement.blocks[0].spectral.weight_parts.grad.abs().sum() > 0


def test_query_chunking_is_equivalent_only_for_pointwise_default_trunk():
    model = DeepONet(3, 2, 4)
    branch, queries = torch.randn(2, 3), torch.randn(11, 2)
    full = model(branch, queries)
    chunks = torch.cat([model(branch, q) for q in queries.split(4)], dim=1)
    torch.testing.assert_close(full, chunks)
    # FNO 的整域 FFT 不能按空间切块保留同一算子，这不是推理分块功能。
    fno = FNO(1, 1, modes=(1, 2), width=3, depth=1, projection_hidden=())
    field = torch.randn(1, 1, 8, 8)
    whole = fno(field)
    tiles = torch.cat([fno(v) for v in field.split(4, dim=2)], dim=2)
    assert not torch.allclose(whole, tiles)


def test_fno_rejects_component_broadcast_and_invalid_padding():
    with pytest.raises(ValueError, match="padding"):
        FNO(1, 1, modes=(2, 3), padding=(1,))
    bad_block = FourierBlock(2, 2, (2, 3), local=nn.AdaptiveAvgPool2d((1, 1)))
    with pytest.raises(ValueError, match="形状"):
        bad_block(torch.randn(1, 2, 7, 9))
    model = FNO(2, 1, modes=(2, 3), width=3, operator=nn.Conv2d(3, 4, 1))
    with pytest.raises(ValueError, match="operator"):
        model(torch.randn(1, 2, 7, 9))


def test_available_cuda_device_migration():
    if not torch.cuda.is_available():
        pytest.skip("CUDA 不可用；CPU 已验证，不能声称 CUDA 通过")
    model = FNO(2, 1, modes=(2, 3), width=3, depth=1).cuda()
    value = torch.randn(2, 2, 7, 9, device="cuda", requires_grad=True)
    model(value).square().mean().backward()
    assert value.grad.is_cuda
    assert model.operator.blocks[0].spectral.weight.is_cuda


@pytest.mark.parametrize("kind", ["deeponet", "fno"])
def test_available_mps_forward_backward_and_cpu_readback(kind):
    if not torch.backends.mps.is_available():
        pytest.skip("MPS 不可用，不声明设备通过")
    torch.manual_seed(61)
    if kind == "deeponet":
        cpu = DeepONet(3, 2, 4, branch_hidden=(6,), trunk_hidden=(5,))
        inputs = (torch.randn(2, 3), torch.randn(7, 2))
    else:
        cpu = FNO(2, 1, modes=(2, 3), width=3, depth=2, projection_hidden=(5,))
        inputs = (torch.randn(2, 2, 7, 9),)
    device = copy.deepcopy(cpu).to("mps")
    cpu_inputs = tuple(v.requires_grad_() for v in inputs)
    device_inputs = tuple(v.detach().to("mps").requires_grad_() for v in inputs)
    expected, actual = cpu(*cpu_inputs), device(*device_inputs)
    torch.testing.assert_close(actual.cpu(), expected, rtol=2e-4, atol=2e-5)
    expected.square().mean().backward()
    actual.square().mean().backward()
    for a, b in zip(cpu_inputs, device_inputs, strict=True):
        torch.testing.assert_close(a.grad, b.grad.cpu(), rtol=5e-4, atol=2e-5)
    for a, b in zip(cpu.parameters(), device.parameters(), strict=True):
        assert b.grad is not None and torch.isfinite(b.grad).all()
        torch.testing.assert_close(a.grad, b.grad.cpu(), rtol=5e-4, atol=2e-5)
    device.to("cpu")
    torch.testing.assert_close(device(*inputs), expected, rtol=0, atol=0)


def test_reference_rejects_unverified_source_before_execution(upstream):
    corrupt = dict(upstream)
    corrupt["spectral_convolution.py"] += "\n# changed\n"
    with pytest.raises(ValueError, match="摘要"):
        SpectralReference(corrupt, 1, 1, (2, 3))
    corrupt["deeponet.py"] += "\n# changed\n"
    with pytest.raises(ValueError, match="摘要"):
        DeepONetReference(corrupt, (2, 3), (2, 3))


@pytest.mark.parametrize("strategy", [None, "split_branch", "split_trunk", "split_both"])
def test_deeponet_fp32_strided_full_field_and_gradients_match_reference(upstream, strategy):
    """覆盖真实场的非连续查询布局；弱容差小张量测试会遗漏此舍入路径。"""
    torch.manual_seed(42)
    outputs = 1 if strategy is None else 3
    model = DeepONet(320, 3, 16, outputs, strategy, branch_hidden=(32, 32), trunk_hidden=(32, 32))
    reference = DeepONetReference(
        upstream,
        (320, 32, 32, model.readout.branch_width),
        (3, 32, 32, model.readout.trunk_width),
        out_channels=outputs,
        multi_output=strategy,
    )
    copy_deeponet_weights(reference, model)
    branch = torch.randn(1, 320, requires_grad=True)
    # 物理输入末轴含坐标和其他场；抽前三维后每行仍以5为步长。
    queries = torch.randn(1, 32768, 5)[..., :3].requires_grad_()
    assert not queries.is_contiguous()
    ref_branch = branch.detach().clone().requires_grad_()
    ref_queries = queries.detach().requires_grad_()
    actual = model(branch, queries, query_layout="per_sample")
    expected = reference(ref_branch, ref_queries, query_layout="per_sample")
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    target = torch.randn_like(actual)
    (actual - target).square().mean().backward()
    (expected - target).square().mean().backward()
    torch.testing.assert_close(branch.grad, ref_branch.grad, rtol=0, atol=0)
    torch.testing.assert_close(queries.grad, ref_queries.grad, rtol=0, atol=0)
    for left, right in ((model.branch, reference.branch), (model.trunk, reference.trunk)):
        a = [m for m in left.modules() if isinstance(m, nn.Linear)]
        b = [m for m in right.modules() if isinstance(m, nn.Linear)]
        for first, second in zip(a, b, strict=True):
            torch.testing.assert_close(first.weight.grad, second.weight.grad, rtol=0, atol=0)
            torch.testing.assert_close(first.bias.grad, second.bias.grad, rtol=0, atol=0)
    torch.testing.assert_close(
        model.readout.bias.grad, torch.cat([p.grad for p in reference.b]), rtol=0, atol=0
    )


def test_deeponet_custom_coupled_trunk_keeps_sample_and_query_axes():
    """不能为点式线性层的数值对照改变用户跨查询模块的输入语义。"""

    class CoupledTrunk(nn.Module):
        def __init__(self):
            super().__init__()
            self.projection = nn.Linear(2, 4)
            self.received = None

        def forward(self, queries):
            self.received = queries.shape
            assert queries.ndim == 3
            return self.projection(queries - queries.mean(dim=1, keepdim=True))

    trunk = CoupledTrunk()
    model = DeepONet(3, 2, 4, trunk=trunk)
    branch, queries = torch.randn(2, 3), torch.randn(2, 7, 2)
    result = model(branch, queries, query_layout="per_sample")
    assert trunk.received == (2, 7, 2)
    assert result.shape == (2, 7, 1)
    result.square().mean().backward()
    assert trunk.projection.weight.grad.abs().sum() > 0
