"""具名数值数组的清单保存与校验，不解释领域语义。"""

import hashlib
import json
from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.arrays import save_json, save_npy


def digest(path: str | Path) -> str:
    """对完整产物计算稳定内容摘要。"""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_arrays(
    directory: str | Path, arrays: dict[str, np.ndarray], *, kind: str, metadata: dict
) -> str:
    """写独立数据目录与完整数组清单，已存在目录拒绝覆盖。"""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    fields = {}
    for name, value in arrays.items():
        if not name.replace("_", "").isalnum():
            raise ValueError("数组名称非法")
        value = np.asarray(value)
        if value.dtype.kind not in "biuf" or not np.isfinite(value).all():
            raise ValueError(f"{name} 不是有限数值数组")
        path = directory / f"{name}.npy"
        save_npy(path, value)
        fields[name] = {"path": path.name, "shape": list(value.shape), "sha256": digest(path)}
    record = {"kind": kind, "metadata": metadata, "fields": fields}
    save_json(directory / "manifest.json", record)
    return str((directory / "manifest.json").resolve())


def read_arrays(path: str | Path, *, kind: str) -> tuple[dict, dict[str, np.ndarray]]:
    """校验实际字节、维度和路径，拒绝被改写的固定结果。"""
    path = Path(path).resolve()
    record = json.loads(path.read_text())
    if record["kind"] != kind:
        raise ValueError("数组产物类型不兼容")
    arrays = {}
    for name, field in record["fields"].items():
        filename = (path.parent / field["path"]).resolve()
        if not filename.is_relative_to(path.parent) or digest(filename) != field["sha256"]:
            raise ValueError(f"数组路径或内容改变: {name}")
        arrays[name] = np.load(filename, mmap_mode="r", allow_pickle=False)
        if list(arrays[name].shape) != field["shape"]:
            raise ValueError("数组形状改变")
    return record, arrays
