"""通用具名物理指标，累计元素而不是平均样本指标。"""

import numpy as np


class PhysicalMetrics:
    """每分量及向量模长累计；零真值范数对应不可定义的相对误差。"""

    def __init__(self):
        self.totals = {}

    def update(self, name, prediction, truth):
        """拒绝广播、空场和非有限值，所有算术使用 float64。"""
        pred, actual = np.asarray(prediction, dtype=np.float64), np.asarray(truth, dtype=np.float64)
        if pred.shape != actual.shape or pred.ndim != 2 or not len(pred) or not pred.shape[1]:
            raise ValueError(f"{name}: 预测和真值必须是同形非空点场")
        if not np.isfinite(pred).all() or not np.isfinite(actual).all():
            raise ValueError(f"{name}: 非有限预测或真值")
        self._add(name, pred, actual)
        if pred.shape[1] > 1:
            for i in range(pred.shape[1]):
                self._add(f"{name}/{i}", pred[:, i], actual[:, i])
            self._add(
                f"{name}/magnitude", np.linalg.norm(pred, axis=1), np.linalg.norm(actual, axis=1)
            )

    def _add(self, name, pred, actual):
        delta = pred - actual
        previous = self.totals.setdefault(name, np.zeros(4))
        previous += [
            delta.size,
            np.square(delta).sum(),
            np.abs(delta).sum(),
            np.square(actual).sum(),
        ]

    def finalize(self):
        """保留原始累计量，允许下游独立重算加权结果。"""
        if not self.totals:
            raise ValueError("没有物理指标输入")
        return {
            name: {
                "count": int(count),
                "squared_error": float(squared),
                "absolute_error": float(absolute),
                "truth_squared": float(truth),
                "mse": float(squared / count),
                "mae": float(absolute / count),
                "relative_l2": float(np.sqrt(squared / truth)) if truth else None,
            }
            for name, (count, squared, absolute, truth) in self.totals.items()
        }
