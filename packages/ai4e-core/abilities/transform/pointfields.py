"""具名工况与点标签的冻结 float32 标准化能力。"""

import numpy as np


class FieldNormalization:
    """保持 float32 NumPy 参考算术；工况和点标签分别变换。"""

    def __init__(self, statistics):
        self.record = statistics
        self.values = {}
        for key in ("conditions", "labels"):
            mean = np.asarray(statistics[key]["mean"], dtype=np.float32)
            std = np.asarray(statistics[key]["std"], dtype=np.float32)
            if not np.isfinite(mean).all() or not np.isfinite(std).all() or np.any(std <= 1e-12):
                raise ValueError(f"{key}: 归一化统计不合法")
            self.values[key] = mean, std

    def apply(self, key, value):
        """逐通道标准化，不修改物理数组。"""
        mean, std = self.values[key]
        return ((value.astype(np.float32) - mean) / std).astype(np.float32)

    def inverse(self, value):
        """将标签恢复为物理量。"""
        mean, std = self.values["labels"]
        return (value.astype(np.float32) * std + mean).astype(np.float32)
