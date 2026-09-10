"""总体矩累计；明确保持逐数组 float64 求和顺序用于参考对照。"""

import numpy as np


class PopulationMoments:
    """分别累计样本行或点行，不替调用方决定统计单位。"""

    def __init__(self, width: int):
        self.width = width
        self.count = 0
        self.total = np.zeros(width, dtype=np.float64)
        self.square_total = np.zeros(width, dtype=np.float64)

    def update(self, values):
        """按调用顺序累计一个数组；非有限输入在统计前拒绝。"""
        matrix = np.asarray(values, dtype=np.float64)
        if matrix.ndim == 1:
            matrix = matrix[None, :]
        if matrix.ndim != 2 or matrix.shape[1] != self.width or not np.isfinite(matrix).all():
            raise ValueError("统计数组形状不符或包含非有限值")
        self.count += matrix.shape[0]
        self.total += matrix.sum(axis=0, dtype=np.float64)
        self.square_total += np.square(matrix, dtype=np.float64).sum(axis=0, dtype=np.float64)

    def finalize(self):
        """返回总体均值与标准差；常量字段不允许静默除零。"""
        if not self.count:
            raise ValueError("统计输入为空")
        mean = self.total / self.count
        std = np.sqrt(np.maximum(self.square_total / self.count - np.square(mean), 0.0))
        if np.any(std <= 1e-12):
            raise ValueError("统计标准差为零")
        return {"mean": mean.tolist(), "std": std.tolist(), "count": self.count}
