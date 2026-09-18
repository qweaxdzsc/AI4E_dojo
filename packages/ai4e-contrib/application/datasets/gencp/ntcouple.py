"""NTcouple 原生 NPY 按样本读取；不同场先分别归一化，再拼条件。"""

from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.ability.transform.gencp.preprocessing import nt_sample_fields
from ai4e_core.abilities.data.source.array_read import read_array

SOURCES = {
    "neutron": ["bc_neu", "fuel_neu", "fluid_neu", "neu"],
    "solid": ["neu_fuel", "fluid_fuel", "fuel"],
    "fluid": ["delta_fuel_fluid", "fluid"],
}


def describe(root, dataset, field, split, count, *, seed=42):
    """保留官方 decouple/couple 分片，冻结样本下标。"""
    del dataset
    root = Path(root)
    if (root / "NTcouple").is_dir():
        root = root / "NTcouple"
    folder = root / split
    names = SOURCES[field] if split.startswith("decouple") else ["bc", "fuel", "fluid", "neu"]
    files = {name: str((folder / (name + ".npy")).resolve()) for name in names}
    for path in files.values():
        if not Path(path).is_file():
            raise FileNotFoundError(f"核热原始数据缺失: {path}")
    shapes = [np.load(path, mmap_mode="r").shape for path in files.values()]
    if len({shape[0] for shape in shapes}) != 1:
        raise ValueError("原始核热样本数不配对")
    total = shapes[0][0]
    if not 0 < count <= total:
        raise ValueError("核热抽样数量非法")
    ids = (
        np.random.default_rng(seed).choice(total, count, replace=False)
        if split == "decouple_train"
        else np.arange(count)
    )
    return {
        "dataset": "ntcouple",
        "field": field,
        "split": split,
        "normalization": {"kind": "nt_fixed_bounds_v1"},
        "files": files,
        "records": [{"id": str(int(i)), "index": int(i)} for i in ids],
        "sample_indices": ids.tolist(),
        "axes": ["T", "H", "W", "C"],
        "time_indices": list(range(16)),
        "units": {"neutron": ["unknown"], "solid": ["K"], "fluid": ["K", "m/s", "m/s", "MPa"]}[
            field
        ],
    }


def read_sample(record, description):
    """单样本 C,T,H,W 转 T,H,W,C；数值映射按原数据读取器。"""
    files = description["files"]

    values = {
        name: torch.from_numpy(read_array(path, record["index"]))
        .float()
        .permute(1, 2, 3, 0)
        .contiguous()
        for name, path in files.items()
    }
    result = nt_sample_fields(
        values, description["field"], decoupled=description["split"].startswith("decouple")
    )
    return {**result, "id": record["id"]}
