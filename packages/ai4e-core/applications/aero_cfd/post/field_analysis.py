"""物理场分析的领域适配；计算交给公开原子能力。"""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from ai4e_core.abilities.eval.region_statistics import region_statistics as statistics
from ai4e_core.abilities.postproc import visualization as abilities


def _record_mesh(mesh, operation):
    """只记录替换函数的来源，不序列化函数或绘图对象。"""
    if operation is not None:
        from ai4e_core.base.config import operation_record

        transform = (
            json.loads(str(mesh.field_data["post_transform"][0]))
            if "post_transform" in mesh.field_data
            else {}
        )
        mesh.field_data["post_transform"] = [
            json.dumps({**transform, "custom_operation": operation_record(operation)})
        ]
    return mesh


def mesh_field(mesh: Any, field: str) -> str:
    """将领域字段选择映射到网格数组，拒绝跨域错绑。"""
    if ":" not in field:
        return field
    domain, name, variant = field.split(":")
    if str(mesh.field_data["post_domain"][0]) != domain:
        raise ValueError("物理场与网格域不一致")
    return f"{domain}.{name}.{variant}"


def slice_field(mesh: Any, *, origin: Any, normal: Any, operation: Any = None) -> Any:
    """按物理平面切片，可注入替换计算函数。"""
    return _record_mesh(
        (operation or abilities.slice_mesh)(mesh, origin=origin, normal=normal), operation
    )


def clip_field(
    mesh: Any, *, origin: Any, normal: Any, keep: str = "positive", operation: Any = None
) -> Any:
    """剖切领域网格。"""
    return _record_mesh(
        (operation or abilities.clip_mesh)(mesh, origin=origin, normal=normal, keep=keep), operation
    )


def contour_field(mesh: Any, *, field: str, operation: Any = None, **parameters: Any) -> Any:
    """提取指定物理场等值。"""
    return _record_mesh(
        (operation or abilities.contour_mesh)(mesh, field=mesh_field(mesh, field), **parameters),
        operation,
    )


def vector_field(mesh: Any, *, field: str, operation: Any = None, **parameters: Any) -> Any:
    """绘制完整三分量物理矢量。"""
    return _record_mesh(
        (operation or abilities.glyph_mesh)(mesh, field=mesh_field(mesh, field), **parameters),
        operation,
    )


def streamlines(mesh: Any, *, field: str, operation: Any = None, **parameters: Any) -> Any:
    """从显式种子积分物理流线。"""
    return _record_mesh(
        (operation or abilities.streamline_mesh)(mesh, field=mesh_field(mesh, field), **parameters),
        operation,
    )


def profile_field(mesh: Any, *, fields: Any, operation: Any = None, **parameters: Any) -> dict:
    """沿线采样所选物理场。"""
    return (operation or abilities.sample_line)(
        mesh, fields=[mesh_field(mesh, field) for field in fields], **parameters
    )


def probe_field(mesh: Any, *, fields: Any, operation: Any = None, **parameters: Any) -> dict:
    """在显式位置采样物理场，域外位置保留无效标记。"""
    return (operation or abilities.probe_points)(
        mesh, fields=[mesh_field(mesh, field) for field in fields], **parameters
    )


def region_statistics(
    mesh: Any,
    *,
    field: str,
    component: str | int = "scalar",
    association: str = "point",
    operation: Any = None,
) -> dict:
    """计算派生域统计，保留变换与插值口径。"""
    if isinstance(mesh, dict) and "positions" in mesh and "valid" in mesh:
        name = field.replace(":", ".")
        values = np.asarray(mesh["fields"][name], dtype=np.float64)
        if values.ndim == 2:
            if component == "magnitude":
                values = np.linalg.norm(values, axis=1)
            else:
                index = 0 if component == "scalar" and values.shape[1] == 1 else int(component)
                if not 0 <= index < values.shape[1]:
                    raise ValueError("分量选择不合法")
                values = values[:, index]
        return {
            **(operation or statistics)(
                values,
                mask=mesh["valid"],
                region="profile" if "distance" in mesh else "probe",
                interpolation=mesh["interpolation"],
            ),
            "field": name,
            "component": component,
        }
    values = abilities.field_values(
        mesh, mesh_field(mesh, field), association=association, component=component
    )
    transform = (
        json.loads(str(mesh.field_data["post_transform"][0]))
        if "post_transform" in mesh.field_data
        else {"operation": "whole"}
    )
    result = (operation or statistics)(
        values, region=transform, interpolation=transform.get("interpolation")
    )
    units = (
        json.loads(str(mesh.field_data["post_units"][0])) if "post_units" in mesh.field_data else {}
    )
    name = mesh_field(mesh, field)
    return {
        **result,
        "field": name,
        "component": component,
        "unit": units.get(name.split(".")[1]) if "." in name else None,
    }
