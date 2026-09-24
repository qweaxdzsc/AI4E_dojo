"""双圆柱真实历史窗口；固定两条训练轨迹，不继承旧五轨迹统计。"""

from pathlib import Path

import h5py
import numpy as np

from ai4e_contrib.application.datasets.gencp.cylinder import FIELDS, read_fields
from ai4e_core.abilities.data.save.array_manifest import save_arrays

UNITS = ["published"] * 3 + ["source/100"]


def prepare_source(root, output, dataset, session):
    """物化所选窗口，保存来源时间与实体，无未来输入或隐藏源路径依赖。"""
    paths = {
        "train": sorted((Path(root) / "train").glob("*.h5"))[: dataset["train_count"]],
        "test": sorted((Path(root) / "val").glob("*.h5"))[: dataset["test_count"]],
    }
    results = {}
    for split, files in paths.items():
        if len(files) != dataset[split + "_count"]:
            raise ValueError("双圆柱轨迹数量不足")
        starts = list(range(0, 961, 30)) if split == "train" else list(range(0, 841, 120))
        windows = [
            {"path": str(path), "id": path.stem + f"_{s:04d}", "start": s}
            for path in files
            for s in starts
        ]

        def read(window):
            with h5py.File(window["path"], "r") as f:
                if not np.array_equal(f["metadata/grid/times"][:], np.arange(1000)):
                    raise ValueError("双圆柱时间身份变化")
                for axis in ("x_coordinates", "y_coordinates"):
                    if not np.array_equal(f["metadata/grid/" + axis][:], np.arange(130)):
                        raise ValueError("双圆柱空间身份变化")
            s = window["start"]
            values = read_fields(window["path"], slice(s, s + 31, 10)).astype(np.float32)
            if values.shape != (4, 128, 128, 4):
                raise ValueError("历史窗口形状不符")
            return {
                "input": values[:3],
                "target": values[3],
                "valid": np.ones((128, 128), bool),
                "entity_ids": np.arange(128**2).reshape(128, 128),
                "times": np.arange(s, s + 31, 10),
            }

        samples = session.execute_samples(windows, read, stage="rawprep")
        arrays = {name: np.stack([item[name] for item in samples]) for name in samples[0]}
        results[split] = save_arrays(
            Path(output) / split,
            arrays,
            kind="classic-physical-windows-v1",
            metadata={
                "ids": [w["id"] for w in windows],
                "fields": list(FIELDS),
                "units": UNITS,
                "source_files": [p.name for p in files],
            },
        )
    return results
