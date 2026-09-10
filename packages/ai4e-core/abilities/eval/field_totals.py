"""物理场总误差累计；标量场与声明的向量模长分别统计。"""

import numpy as np


class FieldTotals:
    """保留完整样本的 float64 累计次序，支持点数不相等的样本。"""

    def __init__(self, names, *, vector_name="cf", vector_indices=(1, 2, 3)):
        self.names = tuple(names)
        self.vector_name, self.vector_indices = vector_name, list(vector_indices)
        self.squared = np.zeros(len(names), dtype=np.float64)
        self.absolute = np.zeros(len(names), dtype=np.float64)
        self.truth_squared = np.zeros(len(names), dtype=np.float64)
        self.vector_squared = self.vector_absolute = self.vector_truth = 0.0
        self.count = 0

    def update(self, prediction, truth):
        """累计真实点数；形状与有限值门禁不允许广播掩盖错位。"""
        if (
            prediction.shape != truth.shape
            or prediction.ndim != 2
            or prediction.shape[1] != len(self.names)
        ):
            raise ValueError("预测和真值形状不一致")
        if not np.isfinite(prediction).all() or not np.isfinite(truth).all():
            raise ValueError("预测或真值含非有限值")
        difference = prediction.astype(np.float64) - truth.astype(np.float64)
        self.squared += np.square(difference).sum(axis=0)
        self.absolute += np.abs(difference).sum(axis=0)
        self.truth_squared += np.square(truth.astype(np.float64)).sum(axis=0)
        predicted = np.linalg.norm(prediction[:, self.vector_indices].astype(np.float64), axis=1)
        actual = np.linalg.norm(truth[:, self.vector_indices].astype(np.float64), axis=1)
        difference = predicted - actual
        self.vector_squared += float(np.square(difference).sum())
        self.vector_absolute += float(np.abs(difference).sum())
        self.vector_truth += float(np.square(actual).sum())
        self.count += len(prediction)

    def finalize(self):
        """返回按点加权指标；零真值分母沿用最小正浮点门禁。"""
        if not self.count:
            raise ValueError("指标输入为空")
        tiny = np.finfo(np.float64).tiny
        return {
            "point_count": self.count,
            "mse": dict(zip(self.names, (self.squared / self.count).tolist(), strict=True)),
            "mae": dict(zip(self.names, (self.absolute / self.count).tolist(), strict=True)),
            "relative_l2": dict(
                zip(
                    self.names,
                    np.sqrt(self.squared / np.maximum(self.truth_squared, tiny)).tolist(),
                    strict=True,
                )
            ),
            self.vector_name + "_magnitude": {
                "mse": self.vector_squared / self.count,
                "mae": self.vector_absolute / self.count,
                "relative_l2": float(np.sqrt(self.vector_squared / max(self.vector_truth, tiny))),
            },
        }
