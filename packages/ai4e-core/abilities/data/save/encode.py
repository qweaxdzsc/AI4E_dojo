"""把具名场记录编码为 float32 张量。"""

from __future__ import annotations

import numpy as np
import torch

from ai4e_core.abilities.data.extract.records import FieldRecord
from ai4e_core.base.events import traced


@traced("张量编码")
def encode_field(record: FieldRecord) -> torch.Tensor:
    """按归属和分量检查形状后编成 ``float32`` 张量。

    标量保持 ``(N,)``，矢量保持 ``(N, 3)``。单元场不得放进点对齐组。

    Args:
        record: 含名字、数组、点/单元、标量/矢量和对齐组。

    Returns:
        与输入数值一致的 ``float32`` 张量，不共享原数组存储。

    Raises:
        TypeError: 记录不是映射，或数组无法转成数值。
        ValueError: 名称/归属/分量/对齐组不合法，或形状与声明不符。
    """
    if not isinstance(record, dict):
        raise TypeError("场记录必须是映射")
    name = record.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError("场记录名称必须是非空字符串")
    association = record.get("association")
    kind = record.get("kind")
    group = record.get("group")
    if association not in ("point", "cell"):
        raise ValueError(f"场 {name} 归属必须是 point 或 cell")
    if kind not in ("scalar", "vector"):
        raise ValueError(f"场 {name} 类别必须是 scalar 或 vector")
    if not isinstance(group, str) or not group:
        raise ValueError(f"场 {name} 对齐组必须是非空字符串")
    try:
        values = np.asarray(record["values"])
    except Exception as exc:
        raise TypeError(f"场 {name} 的数值无法转为数组") from exc
    if kind == "scalar":
        if values.ndim != 1:
            raise ValueError(f"场 {name} 标量形状必须是 (N,)，得到 {values.shape}")
    elif values.ndim != 2 or values.shape[1] != 3:
        raise ValueError(f"场 {name} 矢量形状必须是 (N, 3)，得到 {values.shape}")
    return torch.as_tensor(np.ascontiguousarray(values), dtype=torch.float32).clone()
