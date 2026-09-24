"""固定中心的三次径向响应；核尺度与多项式尾项要求显式声明。"""

import numpy as np


class RadialBasis:
    """三次核 phi(r)=r**3；条件正定阶要求至少一次多项式尾项。"""

    minimum_degree = 1

    def __init__(self, kernel: str = "cubic") -> None:
        if kernel != "cubic":
            raise ValueError("当前仅实现明确的 cubic 核")
        self.kernel = kernel

    def __call__(self, query: np.ndarray, centers: np.ndarray) -> np.ndarray:
        """返回 [N,M] 核矩阵；仅在每个输入维度累计距离，避免 N*M*d 大临时量。"""
        if np.iscomplexobj(query) or np.iscomplexobj(centers):
            raise ValueError("径向输入必须是实数")
        x, c = np.asarray(query, dtype=np.float64), np.asarray(centers, dtype=np.float64)
        if (
            x.ndim != 2
            or c.ndim != 2
            or x.shape[1] != c.shape[1]
            or c.shape[1] < 1
            or not np.isfinite(x).all()
            or not np.isfinite(c).all()
        ):
            raise ValueError("径向输入维数或数值非法")
        distance2 = np.zeros((len(x), len(c)), dtype=np.float64)
        for dim in range(x.shape[1]):
            distance2 += (x[:, dim, None] - c[None, :, dim]) ** 2
        result = distance2 * np.sqrt(distance2)
        if not np.isfinite(result).all():
            raise FloatingPointError("径向核溢出")
        return result

    def to_state(self) -> dict:
        """返回核定义；不隐式标准化中心或距离。"""
        return {"version": 1, "kernel": self.kernel}

    @classmethod
    def from_state(cls, state: dict) -> "RadialBasis":
        """从明确版本恢复核定义。"""
        if state.get("version") != 1:
            raise ValueError("径向核版本不支持")
        return cls(state["kernel"])
