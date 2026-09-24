"""完整克里金普通对象，组合公共趋势、协方差与固定条件预测。"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import numpy as np

from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition, SquaredExponential
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis


class Kriging:
    """单响应ordinary/universal克里金；不拟合、不存盘、不隐式标准化。

    多输出由调用方有序组合独立模型，本对象不声明输出间协方差。
    普通趋势对象可注入，但持久化首批只接受共享PolynomialBasis的0/1阶。
    """

    def __init__(
        self,
        training_x: Any,
        *,
        trend: PolynomialBasis,
        covariance: SquaredExponential,
        condition: KrigingCondition,
    ) -> None:
        raw = np.asarray(training_x)
        if raw.dtype.kind not in "fiu" or raw.ndim != 2 or not raw.size:
            raise ValueError("训练特征须为非空二维实数数组")
        x = np.array(raw, dtype=np.float64, copy=True)
        if not np.isfinite(x).all():
            raise ValueError("训练特征非有限")
        if isinstance(trend, PolynomialBasis) and (
            trend.degree not in (0, 1) or not trend.include_bias
        ):
            raise ValueError("首批克里金须含常数或线性未知趋势")
        design = np.asarray(trend(x))
        if len(x) != condition.sample_count or design.shape != (len(x), condition.trend_count):
            raise ValueError("趋势、训练特征与条件状态形状不匹配")
        covariance.diagonal(x)
        x.setflags(write=False)
        self.training_x, self.trend = x, trend
        self.covariance, self.condition = covariance, condition

    def predict(
        self,
        x: Any,
        *,
        return_variance: bool = False,
        query_noise: Any = 0.0,
    ) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """查询[N,D]特征，返回[N]均值及可选方差；噪声按当前输出单位平方声明。"""
        return self.condition.predict(
            self.covariance(x, self.training_x),
            self.covariance.diagonal(x),
            self.trend(x),
            return_variance=return_variance,
            query_noise=query_noise,
        )

    def get_state(self) -> dict:
        """交付完整数值预测状态，不包含优化器的任意步恢复声明。"""
        if not isinstance(self.trend, PolynomialBasis):
            raise TypeError("自定义趋势的持久化由调用方显式定义，不能自动保存可执行对象")
        return {
            "kind": "kriging",
            "version": 1,
            "training_x": self.training_x.copy(),
            "trend": deepcopy(self.trend.to_state()),
            "covariance": self.covariance.get_state(),
            "condition": self.condition.get_state(),
        }

    @classmethod
    def from_state(cls, state: dict) -> Kriging:
        """从普通状态重组同一公共组件；不读取旧数据目录或重新估计参数。"""
        if set(state) != {"kind", "version", "training_x", "trend", "covariance", "condition"} or (
            state["kind"] != "kriging" or type(state["version"]) is not int or state["version"] != 1
        ):
            raise ValueError("克里金模型状态版本或字段错误")
        return cls(
            state["training_x"],
            trend=PolynomialBasis.from_state(state["trend"]),
            covariance=SquaredExponential.from_state(state["covariance"]),
            condition=KrigingCondition.from_state(state["condition"]),
        )
