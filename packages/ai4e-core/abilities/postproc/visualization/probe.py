"""空间探针与沿线采样，域外值仅由有效性声明决定。"""

from __future__ import annotations

from typing import Any

import numpy as np

from .fields import pyvista
from .sections import plane


def probe_points(mesh: Any, *, positions: Any, fields: Any, association: str = "point") -> dict:
    """采样指定数组并返回独立数据，保留域外位置和无效标记。"""
    pv = pyvista()
    mesh = pv.wrap(mesh)
    if association not in {"point", "cell"}:
        raise ValueError("采样必须声明 point 或 cell")
    positions = np.asarray(positions, dtype=float)
    if (
        positions.ndim != 2
        or positions.shape[1] != 3
        or not len(positions)
        or not np.isfinite(positions).all()
    ):
        raise ValueError("探针位置必须为有限三维点")
    source = mesh.copy(deep=True)
    # 去掉另一归属，避免 VTK 对同名 point/cell 数组作隐式优先选择。
    (source.cell_data if association == "point" else source.point_data).clear()
    for name in fields:
        attrs = source.point_data if association == "point" else source.cell_data
        if name not in attrs:
            raise ValueError(f"缺少采样字段: {name}")
    sampled = pv.PolyData(positions).sample(source)
    valid = np.asarray(sampled["vtkValidPointMask"], dtype=bool)
    return {
        "positions": positions.copy(),
        "valid": valid,
        "fields": {name: np.array(sampled.point_data[name], copy=True) for name in fields},
        "association": association,
        "interpolation": "VTK cell interpolation"
        if association == "point"
        else "containing cell value",
    }


def sample_line(
    mesh: Any, *, start: Any, end: Any, count: int = 101, fields: Any, association: str = "point"
) -> dict:
    """沿物理线段采样；距离从起点累计，不删除域外点。"""
    start, _ = plane(start, (1, 0, 0))
    end, _ = plane(end, (1, 0, 0))
    if isinstance(count, bool) or int(count) != count or count < 2 or np.array_equal(start, end):
        raise ValueError("剖面需要不同端点和至少两个采样位置")
    result = probe_points(
        mesh, positions=np.linspace(start, end, count), fields=fields, association=association
    )
    result["distance"] = np.linalg.norm(result["positions"] - start, axis=1)
    return result
