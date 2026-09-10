"""按显式能力清单派生几何：仅消费 VTK，不读取或校验物理场。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal, TypedDict, cast

import numpy as np
from vtkmodules.vtkCommonDataModel import vtkDataObject

from ai4e_core.abilities.data.extract import extract_coordinates
from ai4e_core.abilities.data.filter import exterior_mask
from ai4e_core.abilities.data.validate import require_same_leading_dim
from ai4e_core.abilities.geometry import (
    mesh_signed_distance,
    nearest_vertex_distance_and_direction,
    require_surface_mesh,
    surface_point_normals_with_mask,
)
from ai4e_core.applications.aero_cfd.rawprep.read import FieldConfig

GeometryAbility = Literal[
    "nearest_vertex", "mesh_signed_distance", "surface_normals", "exterior_mask"
]


class GeometryDomainInput(TypedDict):
    """几何域最低输入仅为 vtk；可附带已有提取结果，保持共享引用。"""

    vtk: vtkDataObject


class GeometryDomainResult(GeometryDomainInput, total=False):
    """保留已有提取内容，并按启用能力添加原点序几何量。"""

    points: np.ndarray
    fields: dict[str, np.ndarray]
    field_specs: dict[str, FieldConfig]
    mask: np.ndarray
    normals: np.ndarray
    normals_valid_mask: np.ndarray
    nearest_distance: np.ndarray
    nearest_direction: np.ndarray
    signed_distance: np.ndarray
    closest_on_surface: np.ndarray
    surface_direction: np.ndarray
    exterior_mask: np.ndarray


_OUTPUTS: dict[GeometryAbility, tuple[str, tuple[str, ...]]] = {
    "nearest_vertex": ("volume", ("nearest_distance", "nearest_direction")),
    "mesh_signed_distance": (
        "volume",
        ("signed_distance", "closest_on_surface", "surface_direction"),
    ),
    "surface_normals": ("surface", ("normals", "normals_valid_mask")),
    "exterior_mask": ("volume", ("exterior_mask",)),
}


def _validate_enabled(enabled: Sequence[str]) -> tuple[GeometryAbility, ...]:
    """在计算前拒绝错误容器、未知和重复能力。"""
    if isinstance(enabled, (str, bytes)) or not isinstance(enabled, Sequence):
        raise ValueError("enabled 必须是能力名称序列")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
    result: list[GeometryAbility] = []
    for name in enabled:
        if not isinstance(name, str) or name not in _OUTPUTS:
            raise ValueError(f"未知几何能力: {name!r}")
        if name in result:
            raise ValueError(f"重复几何能力: {name}")
        result.append(cast(GeometryAbility, name))
    return tuple(result)


def configured_geometry_enabled(config: Mapping[str, object]) -> tuple[GeometryAbility, ...]:
    """读取 pre.geometry.enabled；缺省为空，显式值须为无重复的能力列表。

    不执行能力，也不读取数据；配置结构错误抛 ValueError。
    """
    pre = config.get("pre", {})
    if not isinstance(pre, Mapping):
        raise ValueError("pre 必须是映射")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
    geometry = pre.get("geometry", {})
    if not isinstance(geometry, Mapping):
        raise ValueError("pre.geometry 必须是映射")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
    enabled = geometry.get("enabled", [])
    if not isinstance(enabled, list):
        raise ValueError("pre.geometry.enabled 必须是列表")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
    return _validate_enabled(enabled)


def derive_configured_geometry(
    extracted: Mapping[str, GeometryDomainInput],
    *,
    enabled: Sequence[str],
    parameters: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, GeometryDomainResult]:
    """仅从域内 VTK 获取坐标/拓扑，执行显式选择的能力并保留已有内容。

    只算法向仅需 surface；其他能力需要 surface/volume。空 enabled 透传，
    不访问 vtk。全体所选能力先做输入门禁和输出冲突检查，失败不执行算法。
    输入字段及额外域保持引用；不套 mask、不改输入、不落盘。不验证物理场。
    返回原域映射副本与所选派生量；缺域、非法能力或同名输出冲突抛 ValueError。
    """
    if not isinstance(extracted, Mapping):
        raise TypeError("几何装配需要域映射")
    selected = _validate_enabled(enabled)
    parameters = parameters or {}
    if set(parameters) - set(selected):
        raise ValueError("几何参数包含未启用能力")
    for name, options in parameters.items():
        allowed = set() if name == "exterior_mask" else {"epsilon"}
        if not isinstance(options, Mapping) or set(options) - allowed:
            raise ValueError(f"几何参数不支持: {name}")
        if "epsilon" in options and (
            not np.isfinite(options["epsilon"]) or options["epsilon"] <= 0
        ):
            raise ValueError("epsilon 必须为正有限数")
    output = {name: cast(GeometryDomainResult, dict(domain)) for name, domain in extracted.items()}
    if not selected:
        return output

    needed = {"surface"}
    if any(name != "surface_normals" for name in selected):
        needed.add("volume")
    points: dict[str, np.ndarray] = {}
    for role in sorted(needed):
        if role not in extracted or "vtk" not in extracted[role]:
            raise ValueError(f"几何装配缺少 {role}.vtk")
        points[role] = extract_coordinates(extracted[role]["vtk"])
        if not np.isfinite(points[role]).all():
            raise ValueError(f"{role} 坐标含 NaN 或 Inf")
    if any(name in selected for name in ("mesh_signed_distance", "surface_normals")):
        require_surface_mesh(extracted["surface"]["vtk"])
    for name in selected:
        role, keys = _OUTPUTS[name]
        for key in keys:
            if key in output[role]:
                raise ValueError(f"派生输出冲突: {role}.{key}")

    for name in selected:
        role, keys = _OUTPUTS[name]
        match name:
            case "nearest_vertex":
                values = nearest_vertex_distance_and_direction(
                    points["volume"], points["surface"], **parameters.get(name, {})
                )
            case "mesh_signed_distance":
                values = mesh_signed_distance(
                    points["volume"], extracted["surface"]["vtk"], **parameters.get(name, {})
                )
            case "surface_normals":
                values = surface_point_normals_with_mask(
                    extracted["surface"]["vtk"], **parameters.get(name, {})
                )
            case "exterior_mask":
                values = (
                    exterior_mask(points["volume"], points["surface"], **parameters.get(name, {})),
                )
        require_same_leading_dim(points[role], *values, labels=("position", *keys))
        # keys 来自闭合集合；TypedDict 动态赋值在此集中处理。
        target = cast(dict[str, object], output[role])
        target.update(zip(keys, values, strict=True))
    return output


def derive_geometry(ctx: dict, *, enabled, parameters=None) -> dict:
    """业务步骤只计算显式启用项，独立原子 API 保持不变。"""
    return {
        **ctx,
        "data": derive_configured_geometry(ctx["data"], enabled=enabled, parameters=parameters),
    }
