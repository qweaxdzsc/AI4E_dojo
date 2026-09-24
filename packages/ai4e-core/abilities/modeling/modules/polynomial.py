"""确定项序的零至二次多项式基，供响应面、趋势与径向尾项直接复用。"""

import itertools

import numpy as np


class PolynomialBasis:
    """无需拟合的参数基；常数、一次、二次按组合索引排序。"""

    def __init__(self, input_dim: int, degree: int, include_bias: bool = True) -> None:
        if type(input_dim) is not int or input_dim < 1:
            raise ValueError("input_dim 必须为正整数")
        if type(degree) is not int or degree not in (0, 1, 2):
            raise ValueError("degree 必须为 0、1 或 2")
        if type(include_bias) is not bool or (degree == 0 and not include_bias):
            raise ValueError("多项式基必须至少有一列，include_bias 为布尔值")
        self.input_dim, self.degree, self.include_bias = input_dim, degree, include_bias
        powers = []
        for order in range(0 if include_bias else 1, degree + 1):
            for indices in itertools.combinations_with_replacement(range(input_dim), order):
                powers.append(np.bincount(indices, minlength=input_dim))
        self._powers = np.asarray(powers, dtype=np.int64)

    @property
    def powers(self) -> np.ndarray:
        """返回独立的各列指数副本，禁止调用方改变基列定义。"""
        return self._powers.copy()

    def transform(self, inputs: np.ndarray) -> np.ndarray:
        """将有限实数 [N,d] 映射为 [N,P]，保留原输入列次序。"""
        original = np.asarray(inputs)
        if np.iscomplexobj(original):
            raise ValueError("多项式输入必须是实数")
        values = np.asarray(original, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != self.input_dim or not np.isfinite(values).all():
            raise ValueError("多项式输入形状或数值非法")
        result = np.ones((len(values), len(self._powers)), dtype=np.float64)
        for column, powers in enumerate(self._powers):
            for index in np.flatnonzero(powers):
                result[:, column] *= values[:, index] ** powers[index]
        if not np.isfinite(result).all():
            raise FloatingPointError("多项式特征溢出")
        return result

    __call__ = transform

    def to_state(self) -> dict:
        """返回可保存的局部配置及项序，不携带数据字段语义。"""
        return {
            "version": 1,
            "input_dim": self.input_dim,
            "degree": self.degree,
            "include_bias": self.include_bias,
            "powers": self._powers.tolist(),
        }

    @classmethod
    def from_state(cls, state: dict) -> "PolynomialBasis":
        """严格校验项序后重建；旧系数不能配合重排的基。"""
        if state.get("version") != 1:
            raise ValueError("多项式状态版本不支持")
        result = cls(state["input_dim"], state["degree"], state["include_bias"])
        if not np.array_equal(state["powers"], result._powers):
            raise ValueError("多项式列指数不一致")
        return result
