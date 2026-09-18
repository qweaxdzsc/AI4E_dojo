"""显式物理字段选择；不依赖活动数组，不修改输入网格。"""

from __future__ import annotations

from typing import Any

import numpy as np


def pyvista() -> Any:
    """按需加载绘图库，让纯数组评价不要求安装可视化依赖。"""
    try:
        import pyvista as pv
    except ImportError as exc:
        raise ImportError("三维分析需要安装 ai4e-core[post]") from exc
    return pv


def field_values(
    mesh: Any,
    field: str,
    *,
    association: str = "point",
    component: str | int = "scalar",
    mask: Any = None,
) -> np.ndarray:
    """按归属与分量返回独立数组；有效性只过滤声明无效的实体。"""
    mesh = pyvista().wrap(mesh)
    if association not in {"point", "cell"}:
        raise ValueError("association 必须是 point 或 cell")
    attrs = mesh.point_data if association == "point" else mesh.cell_data
    if field not in attrs:
        raise ValueError(f"缺少 {association} 字段: {field}")
    values = np.asarray(attrs[field])
    if mask is not None:
        valid = np.asarray(mask)
        if valid.dtype != np.bool_ or valid.shape != (len(values),):
            raise ValueError("有效性必须为逐实体布尔数组")
        values = values[valid]
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("字段为空或含未声明的非有限值")
    if component == "vector":
        if values.ndim != 2 or values.shape[1] != 3:
            raise ValueError("矢量能力要求三个分量")
    elif component == "magnitude":
        if values.ndim != 2:
            raise ValueError("模长要求向量字段")
        values = np.linalg.norm(values, axis=1)
    elif component == "scalar":
        if values.ndim == 2 and values.shape[1] == 1:
            values = values[:, 0]
        if values.ndim != 1:
            raise ValueError("向量字段须显式选择分量或模长")
    else:
        if isinstance(component, bool) or str(component) not in {"0", "1", "2"}:
            raise ValueError("非法分量")
        index = int(component)
        if values.ndim != 2 or index >= values.shape[1]:
            raise ValueError("分量越界")
        values = values[:, index]
    return np.array(values, copy=True)


def scalar_mesh(
    mesh: Any, field: str, *, association: str = "point", component: str | int = "scalar"
) -> Any:
    """返回携带专用着色数组的深拷贝，不改变原场及活动数组。"""
    output = pyvista().wrap(mesh).copy(deep=True)
    values = field_values(output, field, association=association, component=component)
    if values.ndim != 1:
        raise ValueError("着色必须选择标量")
    attrs = output.point_data if association == "point" else output.cell_data
    attrs["__post_scalar"] = values
    return output


def derived_mesh(mesh: Any, *, operation: Any, parameters: dict) -> Any:
    """标明派生实体；插值结果不得继续宣称原始点或单元身份。"""
    import json

    for attrs in (mesh.point_data, mesh.cell_data):
        for name in tuple(attrs.keys()):
            if name in {
                "original_point_id",
                "original_cell_id",
                "vtkOriginalPointIds",
                "vtkOriginalCellIds",
            }:
                del attrs[name]
    mesh.field_data["post_transform"] = [json.dumps({"operation": operation, **parameters})]
    return mesh
