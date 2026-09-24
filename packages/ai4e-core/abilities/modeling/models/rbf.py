"""公共径向响应和多项式尾项组成的固定中心预测器。"""

from copy import deepcopy

import numpy as np

from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
from ai4e_core.abilities.modeling.modules.radial import RadialBasis


class RBFInterpolator:
    """固定中心插值/平滑结果；不会重新拟合、改变核或自动添加抖动。"""

    def __init__(self, state: dict, *, radial=None, polynomial=None) -> None:
        if state.get("kind") != "rbf-v1":
            raise ValueError("径向模型状态版本不支持")
        expected_radial = RadialBasis.from_state(state["radial"])
        expected_polynomial = PolynomialBasis.from_state(state["polynomial"])
        self.radial = expected_radial if radial is None else radial
        self.polynomial = expected_polynomial if polynomial is None else polynomial
        if (
            self.radial.to_state() != expected_radial.to_state()
            or self.polynomial.to_state() != expected_polynomial.to_state()
        ):
            raise ValueError("径向核或尾项变化，必须重新拟合")
        self._state = deepcopy(state)
        for name in ("centers", "shift", "scale", "radial_coefficients", "polynomial_coefficients"):
            if np.iscomplexobj(state[name]):
                raise ValueError("径向状态必须为实数")
            value = np.array(state[name], dtype=np.float64, copy=True)
            if not np.isfinite(value).all():
                raise ValueError("径向状态包含非有限值")
            value.flags.writeable = False
            self._state[name] = value
        s = self._state
        n, d = s["centers"].shape if s["centers"].ndim == 2 else (0, 0)
        coefficients = s["radial_coefficients"]
        q = coefficients.shape[1] if coefficients.ndim == 2 else 0
        if (
            n < 1
            or d != self.polynomial.input_dim
            or q < 1
            or coefficients.shape != (n, q)
            or s["polynomial_coefficients"].shape != (len(self.polynomial.powers), q)
            or s["shift"].shape != (d,)
            or s["scale"].shape != (d,)
            or (s["scale"] <= 0).any()
            or not np.isfinite(s["smoothing"])
            or s["smoothing"] < 0
            or self.polynomial.degree < self.radial.minimum_degree
            or not self.polynomial.include_bias
        ):
            raise ValueError("径向状态的维数、尺度或尾项不一致")

    def predict(self, inputs) -> np.ndarray:
        """返回 [N,q]，分块预测可由调用方按内存预算安排。"""
        s = self._state
        kernel = self.radial(inputs, s["centers"])
        tail = self.polynomial((np.asarray(inputs) - s["shift"]) / s["scale"])
        return kernel @ s["radial_coefficients"] + tail @ s["polynomial_coefficients"]

    __call__ = predict

    def to_state(self) -> dict:
        """交付独立的完整拟合状态，不序列化外部对象。"""
        return deepcopy(self._state)

    get_state = to_state

    @classmethod
    def from_state(cls, state: dict) -> "RBFInterpolator":
        """核对数值及定义后恢复模型。"""
        return cls(state)
