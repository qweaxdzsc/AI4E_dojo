"""CylinderFlow 数据字段、轨迹和 TFRecord 适配。

通用 TFRecord framing、图边和边特征由 core 提供；本模块只解释 DeepMind
CylinderFlow 的 meta.json、字段名称、节点类别和固定网格轨迹语义。
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.source.tfrecord import iter_tfrecord, parse_example_bytes
from ai4e_core.abilities.geometry.mesh_graph import edge_features, triangles_to_edges

NODE_TYPE_COUNT = 9
TRAINABLE_NODE_TYPES = (0, 5)
NOISE_NODE_TYPES = (0,)
_DTYPES = {
    "float32": np.dtype("<f4"),
    "float64": np.dtype("<f8"),
    "int32": np.dtype("<i4"),
    "int64": np.dtype("<i8"),
}


def _as_tensor(value, *, dtype=None) -> torch.Tensor:
    if isinstance(value, torch.Tensor):
        return value.to(dtype=dtype) if dtype is not None else value
    return torch.as_tensor(value, dtype=dtype)


def decode_trajectory(payload: bytes, meta: dict) -> dict[str, torch.Tensor]:
    """按 DeepMind ``meta.json`` 解码一条 CylinderFlow trajectory。"""
    encoded = parse_example_bytes(payload)
    missing = set(meta.get("field_names", ())) - set(encoded)
    if missing:
        raise ValueError(f"CylinderFlow TFRecord 缺少字段: {sorted(missing)}")
    trajectory_length = int(meta["trajectory_length"])
    decoded: dict[str, torch.Tensor] = {}
    for name, declaration in meta["features"].items():
        dtype_name = declaration["dtype"]
        if dtype_name not in _DTYPES:
            raise ValueError(f"CylinderFlow 不支持 dtype: {dtype_name}")
        array = np.frombuffer(b"".join(encoded[name]), dtype=_DTYPES[dtype_name]).copy()
        try:
            array = array.reshape(declaration["shape"])
        except ValueError as exc:
            raise ValueError(f"CylinderFlow 字段 {name} 无法按 meta shape 重排") from exc
        kind = declaration["type"]
        if kind == "static":
            if array.shape[0] != 1:
                raise ValueError(f"CylinderFlow 静态字段 {name} 第一维必须为 1")
            array = array[0]
        elif kind == "dynamic":
            if array.shape[0] != trajectory_length:
                raise ValueError(f"CylinderFlow 动态字段 {name} 时间长度与 meta 不一致")
        else:
            raise ValueError(f"CylinderFlow 首期不支持字段类型: {kind}")
        decoded[name] = torch.from_numpy(array)
    return validate_trajectory(
        {
            "position": decoded["mesh_pos"],
            "cells": decoded["cells"],
            "node_type": decoded["node_type"].squeeze(-1),
            "velocity": decoded["velocity"],
            **({"pressure": decoded["pressure"]} if "pressure" in decoded else {}),
        }
    )


def read_tfrecord_split(
    directory: str | Path, split: str, *, limit: int | None = None
) -> list[dict[str, torch.Tensor]]:
    """读取一个官方 split；``limit`` 只限制轨迹条数，不改写源分片。"""
    directory = Path(directory)
    meta_path = directory / "meta.json"
    record_path = directory / f"{split}.tfrecord"
    if not meta_path.is_file() or not record_path.is_file():
        raise FileNotFoundError(f"CylinderFlow split 缺少 meta.json 或 {record_path.name}")
    if limit is not None and limit <= 0:
        raise ValueError("轨迹条数上限必须为正")
    meta = json.loads(meta_path.read_text())
    trajectories = []
    for index, payload in enumerate(iter_tfrecord(record_path)):
        if limit is not None and index >= limit:
            break
        trajectory = decode_trajectory(payload, meta)
        trajectory["sample_id"] = f"{split}/{index:06d}"
        trajectories.append(trajectory)
    if not trajectories:
        raise ValueError(f"CylinderFlow split {split!r} 没有轨迹")
    return trajectories


def validate_trajectory(sample: dict) -> dict:
    """校验固定二维网格轨迹并返回规范张量字段。"""
    missing = {"position", "cells", "velocity", "node_type"} - set(sample)
    if missing:
        raise ValueError(f"CylinderFlow 轨迹缺少字段: {sorted(missing)}")
    position = _as_tensor(sample["position"], dtype=torch.float32)
    cells = _as_tensor(sample["cells"], dtype=torch.long)
    velocity = _as_tensor(sample["velocity"], dtype=torch.float32)
    node_type = _as_tensor(sample["node_type"], dtype=torch.long).squeeze(-1)
    if position.ndim != 2 or position.shape[1] != 2:
        raise ValueError("CylinderFlow position 必须是 (nodes, 2)")
    if cells.ndim != 2 or cells.shape[1] != 3:
        raise ValueError("CylinderFlow cells 必须是 (faces, 3)")
    if velocity.ndim != 3 or velocity.shape[1:] != position.shape:
        raise ValueError("CylinderFlow velocity 必须是 (time, nodes, 2)")
    if velocity.shape[0] < 3:
        raise ValueError("CylinderFlow 训练轨迹至少需要三个时间帧")
    if node_type.ndim != 1 or node_type.shape[0] != position.shape[0]:
        raise ValueError("node_type 必须是每个节点一个类别")
    if node_type.numel() and (node_type.min() < 0 or node_type.max() >= NODE_TYPE_COUNT):
        raise ValueError("node_type 超出 DeepMind 的 9 类范围")
    if cells.numel() and (cells.min() < 0 or cells.max() >= position.shape[0]):
        raise ValueError("cells 超出节点范围")
    result = {
        "position": position,
        "cells": cells,
        "velocity": velocity,
        "node_type": node_type,
    }
    if "pressure" in sample:
        result["pressure"] = _as_tensor(sample["pressure"], dtype=torch.float32)
    if "sample_id" in sample:
        result["sample_id"] = str(sample["sample_id"])
    return result


def graph_sample(sample: dict) -> dict:
    """把一个 CylinderFlow 物理帧转换为 core 中立图字段。"""
    missing = {"position", "cells", "velocity", "node_type"} - set(sample)
    if missing:
        raise ValueError(f"CylinderFlow 样本缺少字段: {sorted(missing)}")
    position = _as_tensor(sample["position"], dtype=torch.float32)
    cells = _as_tensor(sample["cells"], dtype=torch.long)
    velocity = _as_tensor(sample["velocity"], dtype=torch.float32)
    node_type = _as_tensor(sample["node_type"], dtype=torch.long).squeeze(-1)
    if position.ndim != 2 or position.shape[1] != 2:
        raise ValueError("CylinderFlow position 必须是 (nodes, 2)")
    if cells.ndim != 2 or cells.shape[1] != 3:
        raise ValueError("CylinderFlow cells 必须是 (faces, 3)")
    if velocity.shape != position.shape:
        raise ValueError("CylinderFlow velocity 必须与 position 同形")
    if node_type.ndim != 1 or node_type.shape[0] != position.shape[0]:
        raise ValueError("node_type 必须是每个节点一个类别")
    if node_type.numel() and (node_type.min() < 0 or node_type.max() >= NODE_TYPE_COUNT):
        raise ValueError("node_type 超出 DeepMind 的 9 类范围")
    edges = triangles_to_edges(cells)
    one_hot = torch.nn.functional.one_hot(node_type, NODE_TYPE_COUNT).to(torch.float32)
    result = {
        "position": position,
        "cells": cells,
        "edge_index": edges,
        "edge_features": edge_features(position, edges),
        "node_features": torch.cat([velocity, one_hot], dim=-1),
        "velocity": velocity,
        "node_type": node_type,
    }
    if "target_velocity" in sample:
        target = _as_tensor(sample["target_velocity"], dtype=torch.float32)
        if target.shape != velocity.shape:
            raise ValueError("target_velocity 必须与 velocity 同形")
        result["target_velocity"] = target
    if "target_trajectory" in sample:
        target = _as_tensor(sample["target_trajectory"], dtype=torch.float32)
        if target.ndim != 3 or target.shape[1:] != velocity.shape:
            raise ValueError("target_trajectory 必须是 (time, nodes, 2)")
        result["target_trajectory"] = target
    if "sample_id" in sample:
        result["sample_id"] = str(sample["sample_id"])
    return result


def training_frame(trajectory: dict, index: int) -> dict:
    """按 DeepMind ``add_targets`` 口径取 ``1..T-2`` 的输入和后一帧目标。"""
    trajectory = validate_trajectory(trajectory)
    if index < 1 or index >= trajectory["velocity"].shape[0] - 1:
        raise IndexError("CylinderFlow 训练帧必须位于 1..T-2")
    return graph_sample(
        {
            "position": trajectory["position"],
            "cells": trajectory["cells"],
            "node_type": trajectory["node_type"],
            "velocity": trajectory["velocity"][index],
            "target_velocity": trajectory["velocity"][index + 1],
            "sample_id": f"{trajectory.get('sample_id', 'trajectory')}@{index}",
        }
    )


def _load_path(path: Path):
    if path.suffix == ".pt":
        return torch.load(path, map_location="cpu", weights_only=True)
    if path.suffix == ".npz":
        return {key: value for key, value in np.load(path, allow_pickle=False).items()}
    raise ValueError(f"不支持的 CylinderFlow 容器: {path.suffix}")


def read_samples(source: str | Path | Iterable[dict]) -> list[dict]:
    """读取 torch/NumPy 小样本，并区分物理帧与完整轨迹。"""
    if isinstance(source, (str, Path)):
        loaded = _load_path(Path(source))
        if isinstance(loaded, dict) and "samples" in loaded:
            loaded = loaded["samples"]
        if isinstance(loaded, dict):
            loaded = [loaded]
        source = loaded
    result = []
    for sample in source:
        velocity = _as_tensor(sample["velocity"])
        result.append(validate_trajectory(sample) if velocity.ndim == 3 else graph_sample(sample))
    return result
