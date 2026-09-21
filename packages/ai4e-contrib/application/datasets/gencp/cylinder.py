"""Double Cylinder 原始未清零场读取，供来源相符的连续性约束使用。"""

import json
from pathlib import Path

import h5py
import numpy as np
import torch

from ai4e_core.abilities.constraint.field_supervision import interior_mask
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.stats.masked_fields import masked_statistics

FIELDS = ("velocity_x", "velocity_y", "pressure", "sdf")


def read_fields(path, selection):
    """裁剪保护层，保留交错分量；SDF仅沿来源约定除以100。"""
    with h5py.File(path, "r") as f:
        values = np.stack([f["data/" + name][selection, 1:129, 1:129] for name in FIELDS], axis=-1)
    values[..., 3] /= 100
    if not np.isfinite(values).all():
        raise ValueError(f"来源字段包含非有限值: {path}")
    return values


def describe(source, output):
    """核验现有5/1轨迹身份、坐标及1000帧；冻结只读来源摘要。"""
    root = Path(source).resolve()
    splits = {}
    for split, count in (("train", 5), ("val", 1)):
        paths = sorted((root / split).glob("*.h5"))
        if len(paths) != count:
            raise ValueError(f"{split}需{count}条原始轨迹，实际{len(paths)}")
        records = []
        for path in paths:
            with h5py.File(path, "r") as f:
                for field in FIELDS:
                    if f["data/" + field].shape != (1000, 130, 130):
                        raise ValueError("来源字段形状不一致")
                for axis in ("x_coordinates", "y_coordinates"):
                    if not np.array_equal(f["metadata/grid/" + axis][:], np.arange(130)):
                        raise ValueError("来源坐标与已验证单位网格不符")
                if not np.array_equal(f["metadata/grid/times"][:], np.arange(1000)):
                    raise ValueError("来源时间索引变化")
            # 全字段扫描包含验证轨迹，不从验证轨迹拟合统计量。
            for start in range(0, 1000, 50):
                read_fields(path, slice(start, start + 50))
            records.append(
                {"id": f"{split}/{path.stem}", "path": str(path), "sha256": digest(path)}
            )
        splits[split] = records
    record = {
        "kind": "pcno-cylinder-dataset-v1",
        "case": "double_cylinder",
        "splits": splits,
        "fields": list(FIELDS),
        "units": "published velocity/pressure/grid units; SDF source / 100",
        "frames": 1000,
    }
    save_json(output, record)
    return str(Path(output).resolve())


def prepare(dataset, output, *, history, horizon, interval=10):
    """训练统计与冻结窗口规则；不物化大规模窗口张量。"""
    record = json.loads(Path(dataset).read_text())
    if record.get("case") != "double_cylinder":
        raise ValueError("不是双圆柱数据")
    gradient_sum = gradient_count = 0.0

    def chunks():
        nonlocal gradient_sum, gradient_count
        for item in record["splits"]["train"]:
            if digest(item["path"]) != item["sha256"]:
                raise ValueError("来源摘要变化")
            for start in range(0, 1000, 50):
                values = read_fields(item["path"], slice(start, start + 50))
                mask = interior_mask(torch.from_numpy(values[..., 3] > 0.02)).numpy()
                weights = np.concatenate(
                    (np.repeat(mask[..., None], 3, axis=-1), np.ones_like(mask[..., None])), axis=-1
                )
                u = values[..., :2].astype(np.float64)
                gx = (u[:, 2:, 1:-1] - u[:, :-2, 1:-1]) / 2
                gy = (u[:, 1:-1, 2:] - u[:, 1:-1, :-2]) / 2
                active = mask[:, 1:-1, 1:-1]
                gradient_sum += ((gx**2 + gy**2).sum(-1) * active).sum()
                gradient_count += active.sum()
                yield values, weights

    stats = masked_statistics(chunks())
    max_start = 1000 - 1 - (history + horizon - 1) * interval
    if max_start < 0:
        raise ValueError("历史和预测超出轨迹")
    prepared = {
        **record,
        "kind": "pcno-cylinder-prepared-v1",
        "statistics": stats,
        "gradient_scale": float((gradient_sum / gradient_count) ** 0.5),
        "history": history,
        "horizon": horizon,
        "interval": interval,
        "train_starts": list(range(max_start + 1)),
        "evaluation_starts": list(range(0, max_start + 1, horizon * interval)),
        "admission": "double-cylinder-source-staggered-20260921",
    }
    save_json(output, prepared)
    return str(Path(output).resolve())


def read_window(prepared, trajectory, start):
    """读取单个窗口；未来标签与已知历史分开返回。"""
    count = prepared["history"] + prepared["horizon"]
    interval = prepared["interval"]
    values = read_fields(trajectory["path"], slice(start, start + count * interval, interval))
    if len(values) != count:
        raise ValueError("窗口越过轨迹末尾")
    mean = np.asarray(prepared["statistics"]["mean"], dtype=np.float32)
    scale = np.asarray(prepared["statistics"]["scale"], dtype=np.float32)
    normalized = (values - mean) / scale
    h = prepared["history"]
    return {
        "input": torch.from_numpy(normalized[:h]).unsqueeze(0),
        "target": torch.from_numpy(normalized[h:]).unsqueeze(0),
        "physical": torch.from_numpy(values[h:]).unsqueeze(0),
        "id": trajectory["id"],
        "start": start,
    }
