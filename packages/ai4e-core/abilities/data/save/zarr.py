"""Zarr 具名张量编码；目录事务由 store 的单样本提交持有。"""

from collections.abc import Mapping
from pathlib import Path

import numpy as np
import torch


def write_zarr(path: str | Path, payload) -> None:
    """写一个张量或独立成员映射，保持 dtype 和形状，不拼接不同实体。"""
    import zarr

    group = zarr.open_group(str(path), mode="w")
    group.attrs["ai4e_payload"] = "mapping" if isinstance(payload, Mapping) else "tensor"
    members = payload if isinstance(payload, Mapping) else {"value": payload}
    for name, value in members.items():
        if not isinstance(name, str) or not name or "/" in name or name in {".", ".."}:
            raise ValueError(f"非法 Zarr 成员: {name}")
        array = value.detach().cpu().numpy()
        group.create_array(name, data=array)


def read_zarr(path: str | Path):
    """读回明确编码的张量载荷，拒绝未知目录，不执行 Python 对象反序列化。"""
    import zarr

    group = zarr.open_group(str(path), mode="r")
    kind = group.attrs.get("ai4e_payload")
    if kind not in {"mapping", "tensor"}:
        raise ValueError("Zarr 缺少 ai4e 张量编码声明")
    values = {
        name: torch.from_numpy(np.asarray(group[name][...]).copy()) for name in group.array_keys()
    }
    if kind == "tensor":
        if set(values) != {"value"}:
            raise ValueError("单张量 Zarr 成员错误")
        return values["value"]
    if not values:
        raise ValueError("Zarr 张量映射为空")
    return values
