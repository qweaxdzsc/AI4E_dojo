"""加权正交基的冻结表示及可微系数解码；没有拟合或数据集语义。"""

from copy import deepcopy

import numpy as np
import torch
from torch import nn


class ReducedBasis:
    """使用固定均值与正度量投影；basis 为 [D,r]，快照末轴为 D。"""

    def __init__(self, state: dict) -> None:
        if state.get("kind") != "pod-v1":
            raise ValueError("POD 状态版本不支持")
        self._state = deepcopy(state)
        for name in ("mean", "basis", "weights", "singular_values"):
            if np.iscomplexobj(state[name]):
                raise ValueError("POD 状态必须是实数")
            value = np.array(state[name], dtype=np.float64, copy=True)
            if not np.isfinite(value).all():
                raise ValueError("POD 状态包含非有限数值")
            self._state[name] = value
        mean, basis, weights, singular = (
            self._state[k] for k in ("mean", "basis", "weights", "singular_values")
        )
        rank = state["rank"]
        if (
            type(rank) is not int
            or rank < 1
            or mean.ndim != 1
            or not len(mean)
            or basis.shape != (len(mean), rank)
            or weights.shape != mean.shape
            or (weights <= 0).any()
            or singular.ndim != 1
            or len(singular) < rank
            or (singular < 0).any()
            or singular[rank - 1] <= 0
            or (np.diff(singular) > 0).any()
        ):
            raise ValueError("POD 状态维度、秩、奇异值或正权重不一致")
        if not np.allclose(
            basis.T @ (weights[:, None] * basis), np.eye(rank), rtol=1e-8, atol=1e-10
        ):
            raise ValueError("POD 基不满足加权正交")
        for value in self._state.values():
            if isinstance(value, np.ndarray):
                value.flags.writeable = False

    def _input(self, value, width):
        if np.iscomplexobj(value):
            raise ValueError("POD 输入必须是实数")
        value = np.asarray(value, dtype=np.float64)
        if value.ndim < 1 or value.shape[-1] != width or not np.isfinite(value).all():
            raise ValueError("POD 输入末轴或数值非法")
        return value

    def encode(self, value: np.ndarray) -> np.ndarray:
        """按冻结正度量将 [...,D] 投影到 [...,r]。"""
        state = self._state
        value = self._input(value, len(state["mean"]))
        return ((value - state["mean"]) * state["weights"]) @ state["basis"]

    def decode(self, coefficients: np.ndarray) -> np.ndarray:
        """将 [...,r] 重建为 [...,D]；不会重拟合均值或基底。"""
        value = self._input(coefficients, self._state["rank"])
        return value @ self._state["basis"].T + self._state["mean"]

    def to_state(self) -> dict:
        """返回完全独立的状态副本，保存由调用方承担。"""
        return deepcopy(self._state)

    @classmethod
    def from_state(cls, state: dict) -> "ReducedBasis":
        """校验后恢复冻结基。"""
        return cls(state)

    def torch_decoder(self, *, dtype=torch.float64, device=None) -> "FrozenBasisDecoder":
        """用同一数值状态创建可微系数解码器；只注册缓冲区。"""
        return FrozenBasisDecoder(self).to(device=device, dtype=dtype)


class FrozenBasisDecoder(nn.Module):
    """系数可微，基底和均值为冻结缓冲区，支持普通模块保存及设备迁移。"""

    def __init__(self, representation: ReducedBasis) -> None:
        super().__init__()
        state = representation.to_state()
        self.register_buffer("basis", torch.tensor(state["basis"], dtype=torch.float64))
        self.register_buffer("mean", torch.tensor(state["mean"], dtype=torch.float64))

    def forward(self, coefficients: torch.Tensor) -> torch.Tensor:
        """执行 [...,r]→[...,D]，不剥离系数计算图。"""
        if coefficients.ndim < 1 or coefficients.shape[-1] != self.basis.shape[1]:
            raise ValueError("POD 系数末轴与基底不符")
        if coefficients.dtype != self.basis.dtype or coefficients.device != self.basis.device:
            raise ValueError("系数与冻结解码器设备/精度须一致")
        return coefficients @ self.basis.T + self.mean
