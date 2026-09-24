"""平方指数协方差及固定克里金条件预测；分解和参数估计由training负责。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np


def _numeric(value: Any, name: str, ndim: int) -> np.ndarray:
    raw = np.asarray(value)
    if raw.dtype.kind not in "fiu" or raw.ndim != ndim or not raw.size:
        raise ValueError(f"{name}须为非空{ndim}维实数数组")
    result = np.array(raw, dtype=np.float64, copy=True)
    if not np.isfinite(result).all():
        raise ValueError(f"{name}含非有限值")
    return result


class SquaredExponential:
    """各向异性平方指数协方差：variance*exp(-0.5*sum((dx/length_scale)^2))。

    variance为过程方差；不添加观测噪声、扰动或隐式特征缩放。
    length_scale接受正标量或每个特征的正尺度；普通数组输入输出。
    """

    def __init__(self, length_scale: Any = 1.0, variance: float = 1.0) -> None:
        scales = _numeric(np.atleast_1d(length_scale), "长度尺度", 1)
        if (scales <= 0).any() or isinstance(variance, (bool, np.bool_)):
            raise ValueError("长度尺度和过程方差须为正实数")
        if not np.isscalar(variance) or not np.isfinite(variance) or variance <= 0:
            raise ValueError("过程方差须为有限正标量")
        scales.setflags(write=False)
        self.length_scale, self.variance = scales, float(variance)

    def __call__(self, x: Any, z: Any) -> np.ndarray:
        """接收[N,D]、[M,D]并返回[N,M]协方差；不改变输入数组。"""
        left, right = _numeric(x, "左特征", 2), _numeric(z, "右特征", 2)
        if left.shape[1] != right.shape[1] or self.length_scale.size not in (1, left.shape[1]):
            raise ValueError("特征维数与长度尺度不匹配")
        difference = (left[:, None, :] - right[None, :, :]) / self.length_scale
        return self.variance * np.exp(-0.5 * np.einsum("nmd,nmd->nm", difference, difference))

    def diagonal(self, x: Any) -> np.ndarray:
        """返回每个查询点的自身过程方差，不包含任何噪声或扰动。"""
        points = _numeric(x, "查询特征", 2)
        if self.length_scale.size not in (1, points.shape[1]):
            raise ValueError("特征维数与长度尺度不匹配")
        return np.full(len(points), self.variance, dtype=np.float64)

    def get_state(self) -> dict:
        """返回可由外部保存的独立数值状态；本对象不写文件。"""
        return {
            "kind": "squared_exponential",
            "version": 1,
            "length_scale": self.length_scale.copy(),
            "variance": self.variance,
        }

    @classmethod
    def from_state(cls, state: dict) -> SquaredExponential:
        """读取显式版本和参数；不拟合也不恢复任意可执行对象。"""
        if set(state) != {"kind", "version", "length_scale", "variance"} or (
            state["kind"] != "squared_exponential"
            or type(state["version"]) is not int
            or state["version"] != 1
        ):
            raise ValueError("协方差状态版本或字段不匹配")
        return cls(state["length_scale"], state["variance"])


class KrigingCondition:
    """消费已求解条件状态，独立计算未知趋势克里金均值和方差。

    构造与读取只校验状态，不做GLS、矩阵分解或超参数优化。预测使用已存
    Cholesky因子作三角求解。条件方差不含超参数估计的不确定性。
    """

    def __init__(self, state: dict) -> None:
        fields = {
            "kind",
            "version",
            "beta",
            "alpha",
            "chol_covariance",
            "inv_covariance_trend",
            "chol_trend",
            "noise_variance",
            "jitter",
            "negative_variance_tolerance",
        }
        if (
            set(state) != fields
            or state["kind"] != "kriging_condition"
            or (type(state["version"]) is not int or state["version"] != 1)
        ):
            raise ValueError("克里金条件状态版本或字段不匹配")
        arrays = {
            key: _numeric(state[key], key, rank)
            for key, rank in (
                ("beta", 1),
                ("alpha", 1),
                ("chol_covariance", 2),
                ("inv_covariance_trend", 2),
                ("chol_trend", 2),
                ("noise_variance", 1),
            )
        }
        n, p = len(arrays["alpha"]), len(arrays["beta"])
        expected = {
            "chol_covariance": (n, n),
            "inv_covariance_trend": (n, p),
            "chol_trend": (p, p),
            "noise_variance": (n,),
        }
        if n <= p or any(arrays[key].shape != shape for key, shape in expected.items()):
            raise ValueError("条件状态形状或趋势自由度不相容")
        for key in ("chol_covariance", "chol_trend"):
            value = arrays[key]
            if (np.diag(value) <= 0).any() or np.any(np.triu(value, 1) != 0):
                raise ValueError("状态须含正对角的下三角Cholesky因子")
        if (arrays["noise_variance"] < 0).any():
            raise ValueError("观测噪声方差不得为负")
        scalars = {}
        for key in ("jitter", "negative_variance_tolerance"):
            value = state[key]
            if (
                isinstance(value, (bool, np.bool_))
                or not np.isscalar(value)
                or (not np.isfinite(value) or value < 0)
            ):
                raise ValueError(f"{key}须为有限非负标量")
            scalars[key] = float(value)
        self._state = {"kind": "kriging_condition", "version": 1, **arrays, **scalars}
        for value in arrays.values():
            value.setflags(write=False)
        self.sample_count, self.trend_count = n, p

    def predict(
        self,
        cross_covariance: Any,
        query_diagonal: Any,
        query_trend: Any,
        *,
        return_variance: bool = False,
        query_noise: Any = 0.0,
    ) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """给定[M,N]交叉协方差、[M]自身方差和[M,P]趋势返回[M]预测。

        默认方差为潜在响应；显式query_noise为[M]或标量观测噪声方差。
        jitter仅影响训练分解，绝不自动添加到查询方差。
        """
        cross = _numeric(cross_covariance, "查询交叉协方差", 2)
        diagonal = _numeric(query_diagonal, "查询过程方差", 1)
        trend = _numeric(query_trend, "查询趋势", 2)
        if cross.shape[1] != self.sample_count or trend.shape != (len(cross), self.trend_count):
            raise ValueError("查询协方差/趋势形状不相容")
        if diagonal.shape != (len(cross),) or (diagonal < 0).any():
            raise ValueError("查询方差形状错误或为负")
        raw_noise = np.asarray(query_noise)
        if raw_noise.dtype.kind not in "fiu":
            raise ValueError("查询观测噪声须为实数")
        noise = np.asarray(raw_noise, dtype=np.float64)
        if (
            noise.shape not in ((), (len(cross),))
            or not np.isfinite(noise).all()
            or (noise < 0).any()
        ):
            raise ValueError("查询观测噪声须为非负标量或对应每个查询点")
        if not return_variance and np.any(noise != 0):
            raise ValueError("query_noise只在请求方差时生效")
        state = self._state
        mean = trend @ state["beta"] + cross @ state["alpha"]
        if not np.isfinite(mean).all():
            raise FloatingPointError("条件均值非有限")
        if not return_variance:
            return mean
        from scipy.linalg import solve_triangular

        projected = solve_triangular(state["chol_covariance"], cross.T, lower=True)
        remainder = trend - cross @ state["inv_covariance_trend"]
        correction = solve_triangular(state["chol_trend"], remainder.T, lower=True)
        variance = diagonal - np.square(projected).sum(0) + np.square(correction).sum(0)
        tolerance = state["negative_variance_tolerance"] * max(1.0, float(np.max(diagonal)))
        if not np.isfinite(variance).all() or np.min(variance) < -tolerance:
            raise FloatingPointError("条件方差显著为负或非有限，不能当作数值舍入归零")
        return mean, np.maximum(variance, 0.0) + noise

    def get_state(self) -> dict:
        """返回独立数组副本；外部修改不影响已有预测状态。"""
        return deepcopy(self._state)

    @classmethod
    def from_state(cls, state: dict) -> KrigingCondition:
        """校验并读取固定条件状态，不触发重新拟合。"""
        return cls(state)
