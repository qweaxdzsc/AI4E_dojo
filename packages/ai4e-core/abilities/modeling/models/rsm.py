"""共享参数基与拟合系数组成的多输出响应面，不隐式拟合。"""

from copy import deepcopy

import numpy as np

from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis


class ResponseSurface:
    """普通预测对象；兼容的基可注入替换，系数与项序必须一致。"""

    def __init__(self, state: dict, *, basis=None) -> None:
        if state.get("kind") != "rsm-v1":
            raise ValueError("响应面状态版本不支持")
        expected = PolynomialBasis.from_state(state["basis"])
        self.basis = expected if basis is None else basis
        if self.basis.to_state() != expected.to_state():
            raise ValueError("替换基与系数项序不同，必须重新拟合")
        self._state = deepcopy(state)
        if np.iscomplexobj(state["coefficients"]):
            raise ValueError("响应面系数必须是实数")
        self.coefficients = np.array(state["coefficients"], dtype=np.float64, copy=True)
        if (
            self.coefficients.ndim != 2
            or self.coefficients.shape[0] != len(expected.powers)
            or self.coefficients.shape[1] < 1
            or not np.isfinite(self.coefficients).all()
        ):
            raise ValueError("响应面系数维数或数值非法")
        self.coefficients.flags.writeable = False

    def predict(self, inputs) -> np.ndarray:
        """输入 [N,d]，输出 [N,q]，实际调用公开基函数。"""
        return self.basis(inputs) @ self.coefficients

    __call__ = predict

    def to_state(self) -> dict:
        """返回独立拟合状态，保存由调用方承担。"""
        return deepcopy({**self._state, "coefficients": self.coefficients})

    get_state = to_state

    @classmethod
    def from_state(cls, state: dict) -> "ResponseSurface":
        """经项序及维数检查恢复预测。"""
        return cls(state)
