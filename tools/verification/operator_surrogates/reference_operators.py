"""锁定上游算术的独立 DeepONet/FNO 核对工具，不导入待验证 core。

DeepXDE 99b6620386d18cefb1549dddb7b7fe468cfad607，LGPL-2.1：运行原
strategy、Cartesian merge/concatenate 方法；编码器由独立 PyTorch 层构造。
NeuralOperator 00b7d86f8d74ff0af55da53eb585fe26df9c71f0，MIT：运行原
SpectralConv.forward 和 _contract_dense。只替换导入装配：TensorLy 的 ndim/
einsum 由其 PyTorch 后端等价函数提供；不使用 factorization/complexhalf。
完整 FNO 的升维/局部分支/激活/裁剪由下方透明 harness 组合，不声称执行了
整个 NeuralOperator 包或论文训练工程。原方法未经修改，先验证文件 SHA256。

源码快照只缓存到调用方显式目录；CLI 可下载，不向主环境安装依赖。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from itertools import pairwise, product
from pathlib import Path
from types import SimpleNamespace
from urllib.request import urlopen

import torch
from torch import Tensor, nn
from torch.nn import functional as F

SOURCES = {
    "deeponet.py": (
        "https://raw.githubusercontent.com/lululxvi/deepxde/99b6620386d18cefb1549dddb7b7fe468cfad607/deepxde/nn/pytorch/deeponet.py",
        "1a745a5756b4be3becb0ec5955f57f63070fca698ab496481fb678b8a21a796d",
        "LGPL-2.1",
    ),
    "deeponet_strategy.py": (
        "https://raw.githubusercontent.com/lululxvi/deepxde/99b6620386d18cefb1549dddb7b7fe468cfad607/deepxde/nn/deeponet_strategy.py",
        "f2f4ef0f03b310cdcfe836cb008e360a4f87a3aac4e7219c63d014c5352b183e",
        "LGPL-2.1",
    ),
    "spectral_convolution.py": (
        "https://raw.githubusercontent.com/neuraloperator/neuraloperator/00b7d86f8d74ff0af55da53eb585fe26df9c71f0/neuralop/layers/spectral_convolution.py",
        "9f8987667cf6f1236ee23f1365a883c5916cacac82c1242f91dad84f020aeeaa",
        "MIT",
    ),
}


def load_sources(root: str | Path, *, download: bool = False) -> dict[str, str]:
    """读取并验证锁定参考；缺文件仅在显式 download 时下载。"""
    root = Path(root)
    source = {}
    for name, (url, expected, _) in SOURCES.items():
        path = root / name
        if not path.is_file() and download:
            root.mkdir(parents=True, exist_ok=True)
            with urlopen(url, timeout=30) as response:
                raw = response.read()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError(f"下载参考摘要不符: {name}")
            path.write_bytes(raw)
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"参考来源摘要不符: {name}")
        source[name] = raw.decode()
    return source


def _verify_text(sources, names):
    for name in names:
        if hashlib.sha256(sources[name].encode()).hexdigest() != SOURCES[name][1]:
            raise ValueError(f"参考来源摘要不符: {name}")


def _method(source: str, class_name: str, name: str, namespace: dict):
    cls = next(
        n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == class_name
    )
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    # 静态方法去掉装饰器才成为普通可绑定函数；函数体完全保留。
    method.decorator_list = []
    exec(  # noqa: S102 - 构造器先验证固定 SHA256
        compile(ast.Module(body=[method], type_ignores=[]), "<pinned-upstream>", "exec"), namespace
    )
    return namespace[name]


def _dense(widths, activation: str, *, final: bool = False) -> nn.Sequential:
    activations = {"tanh": nn.Tanh, "gelu": nn.GELU, "relu": nn.ReLU, "silu": nn.SiLU}
    layers = []
    for i, (a, b) in enumerate(pairwise(widths)):
        layers.append(nn.Linear(a, b))
        if i < len(widths) - 2 or final:
            layers.append(activations[activation]())
    return nn.Sequential(*layers)


class DeepONetReference(nn.Module):
    """独立编码器与原 DeepXDE 策略/读出的可执行组合。"""

    def __init__(
        self,
        sources: dict[str, str],
        branch_widths,
        trunk_widths,
        *,
        out_channels: int = 1,
        multi_output: str | None = None,
        activation: str = "tanh",
        trunk_final_activation: str | None = "tanh",
    ) -> None:
        super().__init__()
        _verify_text(sources, ("deeponet.py", "deeponet_strategy.py"))
        self.num_outputs = out_channels
        self.branch = _dense(branch_widths, activation)
        self.trunk = _dense(trunk_widths, activation)
        self.activation_trunk = (
            nn.Identity()
            if trunk_final_activation is None
            else {"tanh": nn.Tanh, "gelu": nn.GELU, "relu": nn.ReLU, "silu": nn.SiLU}[
                trunk_final_activation
            ]()
        )
        self.b = nn.ParameterList([nn.Parameter(torch.zeros(1)) for _ in range(out_channels)])
        namespace = {"torch": torch}
        merge = _method(
            sources["deeponet.py"], "DeepONetCartesianProd", "merge_branch_trunk", namespace
        )
        concat = _method(
            sources["deeponet.py"], "DeepONetCartesianProd", "concatenate_outputs", namespace
        )
        self.merge_branch_trunk = merge.__get__(self)
        self.concatenate_outputs = concat
        strategy_namespace = {}
        exec(  # noqa: S102 - 固定 SHA256 的上游策略
            compile(sources["deeponet_strategy.py"], "<pinned-deepxde-strategy>", "exec"),
            strategy_namespace,
        )
        strategy = {
            None: "SingleOutputStrategy",
            "split_branch": "SplitBranchStrategy",
            "split_trunk": "SplitTrunkStrategy",
            "split_both": "SplitBothStrategy",
        }[multi_output]
        self.strategy = strategy_namespace[strategy](self)

    def forward(self, branch_input: Tensor, queries: Tensor, *, query_layout="shared") -> Tensor:
        """执行原共享查询策略；逐样本查询逐个调用同一原策略。"""
        if query_layout == "per_sample":
            return torch.cat(
                [self.forward(b[None], q) for b, q in zip(branch_input, queries, strict=True)]
            )
        if query_layout != "shared":
            raise ValueError("未知查询布局")
        output = self.strategy.call(branch_input, queries)
        return output[..., None] if self.num_outputs == 1 else output


def _copy_linears(target: nn.Module, source: nn.Module) -> None:
    a = [m for m in target.modules() if isinstance(m, nn.Linear)]
    b = [m for m in source.modules() if isinstance(m, nn.Linear)]
    for left, right in zip(a, b, strict=True):
        left.load_state_dict(right.state_dict())


def copy_deeponet_weights(reference: DeepONetReference, candidate: nn.Module) -> None:
    """映射默认前馈的线性层和逐输出偏置，不复用候选前向。"""
    _copy_linears(reference.branch, candidate.branch)
    _copy_linears(reference.trunk, candidate.trunk)
    with torch.no_grad():
        for i, bias in enumerate(reference.b):
            bias.copy_(candidate.readout.bias[i])


def corners_to_center(weight: Tensor) -> Tensor:
    """正/负频角权重 [corner,I,O,*m] 映射到上游 fftshift 中心窗。"""
    modes = weight.shape[3:]
    result = weight.new_zeros(*weight.shape[1:3], *(2 * m for m in modes[:-1]), modes[-1])
    for index, negative in enumerate(product((False, True), repeat=len(modes) - 1)):
        region = tuple(
            slice(0, m) if neg else slice(m, 2 * m)
            for m, neg in zip(modes[:-1], negative, strict=True)
        ) + (slice(None),)
        result[(slice(None), slice(None), *region)] = weight[index]
    return result


class SpectralReference(nn.Module):
    """执行原 NeuralOperator dense FP32 谱前向；明确关闭其他变体。"""

    def __init__(
        self, sources: dict[str, str], in_channels, out_channels, modes, *, fft_norm="forward"
    ):
        super().__init__()
        _verify_text(sources, ("spectral_convolution.py",))
        self.order, self.out_channels = len(modes), out_channels
        self.complex_data, self.separable = False, False
        self.fno_block_precision, self.fft_norm = "full", fft_norm
        self.n_modes = [*(2 * m for m in modes[:-1]), modes[-1]]
        self.max_n_modes = self.n_modes[:]
        self.resolution_scaling_factor = None
        self.enforce_hermitian_symmetry = False
        self.bias = None
        self.weight = nn.Parameter(
            torch.zeros(in_channels, out_channels, *self.n_modes, dtype=torch.complex64)
        )
        namespace = {
            "torch": torch,
            "Optional": __import__("typing").Optional,
            "Tuple": __import__("typing").Tuple,
            "tl": SimpleNamespace(ndim=lambda t: t.ndim, einsum=torch.einsum),
            "einsum_symbols": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        }
        source = sources["spectral_convolution.py"]
        contract = next(
            n
            for n in ast.parse(source).body
            if isinstance(n, ast.FunctionDef) and n.name == "_contract_dense"
        )
        exec(  # noqa: S102 - 固定 SHA256 的上游收缩
            compile(
                ast.Module(body=[contract], type_ignores=[]), "<pinned-dense-contract>", "exec"
            ),
            namespace,
        )
        self._contract = namespace["_contract_dense"]
        self.original_forward = _method(source, "SpectralConv", "forward", namespace).__get__(self)

    def forward(self, value: Tensor) -> Tensor:
        """仅 FP32 对照；原上游内部固定 cfloat，不能用它证明 FP64。"""
        if value.dtype != torch.float32:
            raise ValueError("锁定上游 forward 固定 complex64，仅支持 FP32 对照")
        return self.original_forward(value)


class FNOReference(nn.Module):
    """经典 FNO 明确变体：独立线性/卷积组合真实上游谱方法。"""

    def __init__(
        self,
        sources,
        in_channels,
        out_channels,
        *,
        modes,
        width=32,
        depth=4,
        padding=None,
        lifting_hidden=(),
        projection_hidden=(128,),
        activation="gelu",
        fft_norm="forward",
    ):
        super().__init__()
        self.padding = (0,) * len(modes) if padding is None else tuple(padding)
        self.lifting = _dense((in_channels, *lifting_hidden, width), activation)
        self.projection = _dense((width, *projection_hidden, out_channels), activation)
        self.spectral = nn.ModuleList(
            [
                SpectralReference(sources, width, width, modes, fft_norm=fft_norm)
                for _ in range(depth)
            ]
        )
        conv = nn.Conv2d if len(modes) == 2 else nn.Conv3d
        self.local = nn.ModuleList([conv(width, width, 1) for _ in range(depth)])
        self.activation = {"gelu": nn.GELU, "relu": nn.ReLU}[activation]()

    def forward(self, value: Tensor) -> Tensor:
        """无坐标嵌入、channel MLP、归一化或缩放；最后谱块不激活。"""
        sizes = value.shape[2:]
        value = self.lifting(value.movedim(1, -1)).movedim(-1, 1)
        value = F.pad(value, tuple(n for p in reversed(self.padding) for n in (0, p)))
        for i, (spectral, local) in enumerate(zip(self.spectral, self.local, strict=True)):
            value = spectral(value) + local(value)
            if i < len(self.spectral) - 1:
                value = self.activation(value)
        value = value[(slice(None), slice(None), *(slice(0, n) for n in sizes))]
        return self.projection(value.movedim(1, -1)).movedim(-1, 1)


def copy_fno_weights(reference: FNOReference, candidate: nn.Module) -> None:
    """映射默认组件的升维/读出/局部权重及频率角到中心窗。"""
    _copy_linears(reference.lifting, candidate.lifting)
    _copy_linears(reference.projection, candidate.projection)
    with torch.no_grad():
        for spectral, local, block in zip(
            reference.spectral, reference.local, candidate.operator.blocks, strict=True
        ):
            spectral.weight.copy_(corners_to_center(block.spectral.weight))
            local.load_state_dict(block.local.conv.state_dict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    load_sources(args.cache, download=args.download)
    print(
        json.dumps(
            {
                name: {"url": url, "sha256": sha, "license": license_name}
                for name, (url, sha, license_name) in SOURCES.items()
            },
            indent=2,
        )
    )
