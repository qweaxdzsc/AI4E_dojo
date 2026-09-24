"""经典前馈与循环的独立 PyTorch 参考，不导入 Dojo 被验证计算。

参考为公开经典数学的本地组装，底层框架采用下列实际锁定版本。
本文件不表示论文任务复现；权重转换只处理明确的默认组合，拒绝漏键。
"""

import hashlib
import inspect
from collections.abc import Mapping
from itertools import pairwise
from pathlib import Path

import torch
from torch import nn

SOURCE = {
    "torch_version": "2.14.0",
    "torch_commit": "08187d9e0fba026dc8217405802ab5381dc88d90",
    "license": "PyTorch BSD-style license; installed distribution LICENSE retained",
    "license_sha256": "bd018feef8825e88181c84eb7e3aa4eafb8f08a20d9fd6ef948569610c4a3e43",
    "files": {
        "torch/nn/modules/linear.py": "1961ad1a1f650e104b3c7f78d19af2d21bf977e7af6c3fdf2420aad563c9e202",
        "torch/nn/modules/rnn.py": "902deeba8fd7d3c92b00e3557071b3bb41cf747bd4b2b9d63757d88562688bde",
    },
    "documentation": [
        "https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html",
        "https://docs.pytorch.org/docs/stable/generated/torch.nn.RNN.html",
    ],
    "scope": "Independent Sequential and native multilayer Elman RNN; no paper accuracy claim",
}


def source_identity() -> dict:
    """返回当前框架真实版本与已读线性/循环源码摘要，供主控保存并比对锁定值。"""
    files = {}
    for name, cls in (("linear", nn.Linear), ("rnn", nn.RNN)):
        path = Path(inspect.getsourcefile(cls))
        files[f"torch/nn/modules/{name}.py"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "torch_version": torch.__version__,
        "torch_commit": torch.version.git_version,
        "files": files,
    }


def feed_forward_reference(
    in_features: int,
    out_features: int,
    hidden_features: tuple[int, ...] = (64, 64, 64),
    activation: str = "gelu",
    final_activation: str | None = None,
    dropout: float = 0.0,
) -> nn.Sequential:
    """独立按线性/激活/dropout 顺序组装，不调用 Dojo 投影或前馈。"""
    activations = {
        "gelu": nn.GELU,
        "relu": nn.ReLU,
        "tanh": nn.Tanh,
        "silu": nn.SiLU,
        "sigmoid": nn.Sigmoid,
        "softplus": nn.Softplus,
        "ELU": nn.ELU,
    }
    widths = (in_features, *hidden_features, out_features)
    layers = []
    for index, (before, after) in enumerate(pairwise(widths)):
        layers.append(nn.Linear(before, after))
        if index < len(widths) - 2:
            layers.append(activations[activation]())
            if dropout:
                layers.append(nn.Dropout(dropout))
    if final_activation is not None:
        layers.append(activations[final_activation]())
    return nn.Sequential(*layers)


def feed_forward_weights(
    state: Mapping[str, torch.Tensor], *, prefix: str = "projection.layers."
) -> dict[str, torch.Tensor]:
    """将已知前馈路径转换为参考 Sequential 键；不忽略其他参数。"""
    if any(not key.startswith(prefix) for key in state):
        raise ValueError("前馈参考只接受明确的线性层参数，不能忽略额外组件权重")
    return {key.removeprefix(prefix): value for key, value in state.items()}


class RNNReference(nn.Module):
    """原生多层 RNN加线性读出的独立参考，保留双偏置与状态顺序。"""

    def __init__(
        self, in_features: int, out_features: int, hidden_size: int = 32, num_layers: int = 2
    ) -> None:
        super().__init__()
        self.recurrent = nn.RNN(in_features, hidden_size, num_layers, batch_first=True)
        self.output_mapping = nn.Linear(hidden_size, out_features)

    def forward(
        self, x: torch.Tensor, state: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """返回全部读出序列与原生总状态，不执行训练或状态缓存。"""
        features, state = self.recurrent(x, state)
        return self.output_mapping(features), state


def recurrent_weights(
    state: Mapping[str, torch.Tensor], *, num_layers: int, prefix: str = "blocks."
) -> dict[str, torch.Tensor]:
    """逐层把单层原生键映射到多层原生键；拒绝遗漏和额外参数。"""
    mapping = {
        f"{prefix}{layer}.recurrent.{kind}_l0": f"{kind}_l{layer}"
        for layer in range(num_layers)
        for kind in ("weight_ih", "weight_hh", "bias_ih", "bias_hh")
    }
    if set(state) != set(mapping):
        raise ValueError("循环参考的参数集合与默认 Elman 组合不一致")
    return {mapping[key]: value for key, value in state.items()}


def rnn_model_weights(
    state: Mapping[str, torch.Tensor], *, num_layers: int = 2
) -> dict[str, torch.Tensor]:
    """完整默认模型到原生参考；自定义输入投影须使用对应独立参考。"""
    outputs = {key: value for key, value in state.items() if key.startswith("output_mapping.")}
    if set(outputs) != {"output_mapping.weight", "output_mapping.bias"}:
        raise ValueError("默认参考要求一个带偏置的线性输出映射")
    recurrent = {key: value for key, value in state.items() if key not in outputs}
    converted = recurrent_weights(
        recurrent, num_layers=num_layers, prefix="recurrent_stage.blocks."
    )
    return {**{f"recurrent.{key}": value for key, value in converted.items()}, **outputs}
