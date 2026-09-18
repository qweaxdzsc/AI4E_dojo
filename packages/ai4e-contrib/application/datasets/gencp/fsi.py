"""两个 FSI 原数据的独立读取与窗口描述，保留原物理预处理。"""

from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.ability.transform.gencp.normalization import fsi_normalize, load_fsi_statistics
from ai4e_contrib.ability.transform.gencp.preprocessing import fsi_physical_fields
from ai4e_core.abilities.data.extract.time_windows import window_count, window_slices
from ai4e_core.abilities.data.source.array_read import read_array

BRANCHES = {
    "double_cylinder": {
        "fluid": "flow_condition_on_cylinder",
        "structure": "cylinder_condition_on_flow",
    },
    "turek_hron": {"fluid": "flow_condition_on_beam", "structure": "beam_condition_on_flow"},
}


def describe(root, dataset, field, split, count, *, seed=42):
    """按官方文件顺序冻结窗口选择；couple 与 decouple 分开。"""
    root = Path(root)
    base = root / dataset
    branch = "couple" if field == "couple" else BRANCHES[dataset][field]
    folder = base / branch
    files = sorted((folder / split).glob("*.h5"))
    expected = 9 if split == "train" else 1
    if len(files) != expected:
        raise FileNotFoundError(
            f"原始分片不完整: {folder / split}，需要 {expected} 个 HDF5，实际 {len(files)}"
        )
    interval = 10 if dataset == "double_cylinder" else 5
    per_file = window_count(999, 3, 12, interval=interval)
    total = len(files) * per_file
    if count > total or count < 1:
        raise ValueError("窗口抽样数量非法")
    ids = (
        np.random.default_rng(seed).choice(total, count, replace=False)
        if split == "train"
        else np.linspace(0, total - 1, count, dtype=int)
    )
    return {
        "dataset": dataset,
        "field": field,
        "split": split,
        "normalization": load_fsi_statistics(folder / "max_min_train.pt"),
        "statistics_path": str((folder / "max_min_train.pt").resolve()),
        "records": [
            {
                "id": f"{files[int(i) // per_file].stem}:{int(i) % per_file}",
                "path": str(files[int(i) // per_file].resolve()),
                "window": int(i) % per_file,
                "interval": interval,
            }
            for i in ids
        ],
        "sample_indices": ids.tolist(),
        "axes": ["T", "H", "W", "C"],
        "fields": ["velocity_x", "velocity_y", "pressure", "sdf"],
        "units": ["unknown"] * 4,
    }


def read_sample(record, description):
    """仅读取当前窗口，先原 SDF 缩放和 mask，再裁剪与归一化。"""
    history, target = window_slices(record["window"], 999, 3, 12, interval=record["interval"])
    crop = (
        (slice(1, 129), slice(1, 129))
        if description["dataset"] == "double_cylinder"
        else (slice(26, 134), slice(66, 154))
    )

    def read(selection, role):
        arrays = [
            torch.from_numpy(read_array(record["path"], (selection, *crop), key="data/" + key))
            for key in ("velocity_x", "velocity_y", "pressure", "sdf")
        ]
        value = fsi_physical_fields(arrays)
        return fsi_normalize(value, description["normalization"], role=role), value

    inputs, _ = read(history, "input")
    target, physical = read(target, "target")
    return {"input": inputs, "target": target, "physical": physical, "id": record["id"]}


def coordinates(description):
    """从准备已冻结的 HDF5 读实际网格与时间，单位未声明则不猜测。"""
    crop = (
        (slice(1, 129), slice(1, 129))
        if description["dataset"] == "double_cylinder"
        else (slice(26, 134), slice(66, 154))
    )
    first = description["records"][0]["path"]
    grid = {
        "H": read_array(first, crop[0], key="metadata/grid/x_coordinates").tolist(),
        "W": read_array(first, crop[1], key="metadata/grid/y_coordinates").tolist(),
    }
    times = {}
    for record in description["records"]:
        history, target = window_slices(record["window"], 999, 3, 12, interval=record["interval"])
        times[record["id"]] = {
            "history": read_array(record["path"], history, key="metadata/grid/times").tolist(),
            "prediction": read_array(record["path"], target, key="metadata/grid/times").tolist(),
        }
    return {
        "axes": grid,
        "physical_times": times,
        "coordinate_units": "not_declared_in_source",
        "time_units": "not_declared_in_source",
    }
