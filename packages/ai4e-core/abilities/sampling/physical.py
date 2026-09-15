"""冻结物理点集：监督抽点、域内/初边界采样及周期配对。"""

import hashlib
import importlib

import torch

from ai4e_core.abilities.geometry.parametric import (
    boundary_axis,
    outward_normals,
    physical_coordinates,
    validate_points,
)


def grid_points(sample):
    """按声明轴顺序生成网格点，与展平真值一一对应。"""
    return torch.cartesian_prod(*(sample["axes"][n] for n in sample["axis_names"]))


def sample_points(
    sample, declaration, *, seed, name, boundary=None, initial=False, supervised=False
):
    """准备单个具名点集；预算不足、未知键、无标签监督点直接失败。"""
    allowed = {"method", "num_points", "function", "include_boundary"}
    if set(declaration) - allowed:
        raise ValueError(f"{name}: 未知采样配置 {set(declaration) - allowed}")
    method = declaration.get("method", "all")
    include_boundary = declaration.get("include_boundary", False)
    if not isinstance(include_boundary, bool):
        raise TypeError("include_boundary 必须为布尔值")
    if include_boundary and (
        method not in {"all", "grid", "random_without_replacement"}
        or boundary
        or initial
        or supervised
    ):
        raise ValueError("include_boundary 仅用于已有网格的 PDE 配点")
    names, bounds = sample["axis_names"], sample["bounds"]
    generator = torch.Generator().manual_seed(
        int.from_bytes(
            hashlib.sha256(f"{seed}/{sample['id']}/{name}".encode()).digest()[:8], "little"
        )
    )
    indices = None
    fixed = (0, bounds["t"][0]) if initial else None
    if boundary:
        axis, sign = boundary_axis(boundary, len(names))
        fixed = (axis, bounds[names[axis]][0 if sign < 0 else 1])
    count = declaration.get("num_points")
    if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 1):
        raise ValueError(f"{name}: num_points 必须为正整数")
    if method in {"all", "grid", "random_without_replacement"}:
        points = grid_points(sample)
        indices = torch.arange(len(points))
        if fixed:
            axis, value = fixed
            mask = points[:, axis] == value
            points, indices = points[mask], indices[mask]
            # 周期不重复端点数据仍允许查询几何端点，但不能伪造标签。
            if not len(points) and boundary and not supervised:
                axes = [sample["axes"][n] for n in names]
                axes[axis] = torch.tensor([value], dtype=torch.float64)
                points, indices = torch.cartesian_prod(*axes), None
        elif not supervised and not include_boundary:
            mask = points[:, 0] > bounds["t"][0]
            for axis, axis_name in enumerate(names[1:], 1):
                lo, hi = bounds[axis_name]
                mask &= (points[:, axis] > lo) & (points[:, axis] < hi)
            points, indices = points[mask], indices[mask]
        if count is not None:
            if count > len(points):
                raise ValueError(f"{name}: 候选点不足 {len(points)} < {count}")
            selected = (
                torch.randperm(len(points), generator=generator)[:count]
                if method == "random_without_replacement"
                else torch.linspace(0, len(points) - 1, count).round().long()
            )
            points = points[selected]
            indices = indices[selected] if indices is not None else None
    elif method in {"uniform", "custom"}:
        if supervised:
            raise ValueError("监督采样只能选择已有标签点")
        if count is None:
            raise ValueError(f"{name}: 新生成点必须指定 num_points")
        spans = torch.tensor([bounds[n] for n in names], dtype=torch.float64)
        if method == "custom":
            module, attr = declaration["function"].rsplit(".", 1)
            points = getattr(importlib.import_module(module), attr)(
                bounds=spans, num_points=count, generator=generator
            )
        else:
            points = spans[:, 0] + torch.rand(
                count, len(names), generator=generator, dtype=torch.float64
            ) * (spans[:, 1] - spans[:, 0])
            if sample["mapping"] == "trapezoid" and boundary is None:
                # dX dY=(2-eta) dxi deta；反演边际 CDF 保证物理面积均匀。
                points[:, 1] = 2 - torch.sqrt(4 - 3 * points[:, 1])
        if fixed:
            points[:, fixed[0]] = fixed[1]
        if len(points) != count:
            raise ValueError("自定义采样器返回点数与预算不符")
    else:
        raise ValueError(f"未知采样方法: {method}")
    validate_points(points, bounds, names)
    if method in {"uniform", "custom"} and fixed is None:
        for axis, axis_name in enumerate(names):
            lo, hi = bounds[axis_name]
            if not ((points[:, axis] > lo) & (points[:, axis] < hi)).all():
                raise ValueError(f"{name}: 域内配点不能位于初始面或边界")
    result = {
        "points": points,
        "physical_points": physical_coordinates(points, sample["mapping"]),
        "indices": indices,
        "sample_id": sample["id"],
    }
    if supervised:
        result["target"] = sample["u"].reshape(-1)[indices]
    if boundary:
        result["normals"] = outward_normals(points, boundary, sample["mapping"])
    return result


def periodic_points(sample, declaration, *, seed, name, boundaries):
    """生成共享时间/切向坐标的平移周期点对，每行保留同一配对身份。"""
    if len(boundaries) != 2 or boundaries[0] == boundaries[1]:
        raise ValueError("周期条件需要不同的两个边界")
    first_axis, first_sign = boundary_axis(boundaries[0], len(sample["axis_names"]))
    axis, sign = boundary_axis(boundaries[1], len(sample["axis_names"]))
    if axis != first_axis or sign == first_sign or sample["mapping"] != "identity":
        raise ValueError("首期周期配对仅支持直角域相对边界")
    cfg = dict(declaration)
    cfg["num_points"] = cfg.pop("num_pairs")
    left = sample_points(sample, cfg, seed=seed, name=name, boundary=boundaries[0])
    right = left["points"].clone()
    right[:, axis] = sample["bounds"][sample["axis_names"][axis]][0 if sign < 0 else 1]
    return {
        "points": left["points"],
        "paired_points": right,
        "pair_ids": torch.arange(len(right)),
        "sample_id": sample["id"],
    }
