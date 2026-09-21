"""公开 Darcy MAT 的文件、字段、样本身份绑定；原始421网格只读。"""

from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.source.matlab import read_matlab


class DarcySource:
    """读取 smooth1/smooth2；内存只保留当前来源 MAT。"""

    def __init__(self, root, *, train_count=1000, evaluation_count=200):
        self.root = Path(root)
        self.counts = {"train": train_count, "test": evaluation_count}
        self.cache = None
        self.cache_split = None
        self.files = {}
        for split, suffix in [("train", "smooth1"), ("test", "smooth2")]:
            matches = list(self.root.rglob(f"piececonst_r421_N1024_{suffix}.mat"))
            if len(matches) != 1:
                raise ValueError(f"期望唯一 {suffix} MAT")
            self.files[split] = matches[0]

    def samples(self):
        """保留来源行号与固定分片，计数可缩小用于接口测试。"""
        return [
            {"id": f"{split}_{i:04d}", "split": split, "index": i}
            for split, count in self.counts.items()
            for i in range(count)
        ]

    def read(self, sample):
        """读取原系数和解，不在物理准备中下采样。"""
        import pyvista as pv

        split, index = sample["split"], sample["index"]
        if self.cache_split != split:
            self.cache = read_matlab(self.files[split], ("coeff", "sol"))
            self.cache_split = split
        coeff, solution = self.cache["coeff"][index], self.cache["sol"][index]
        if coeff.shape != solution.shape or coeff.ndim != 2:
            raise ValueError("Darcy coeff/sol 网格不一致")
        # VTK i 轴最快；转置坐标构造使点顺序等于 MAT C-order。
        x, y = np.meshgrid(
            np.linspace(0, 1, coeff.shape[1]), np.linspace(0, 1, coeff.shape[0]), indexing="xy"
        )
        mesh = pv.StructuredGrid(x.T, y.T, np.zeros_like(x.T)).cast_to_unstructured_grid()
        mesh.point_data["coeff"] = coeff.reshape(-1)
        mesh.point_data["sol"] = solution.reshape(-1)
        return mesh, {
            "grid_shape": list(coeff.shape),
            "grid_order": "C",
            "source": self.files[split].name,
            "units": {"coeff": "benchmark", "sol": "benchmark"},
        }
