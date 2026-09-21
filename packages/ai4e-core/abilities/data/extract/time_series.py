"""按显式字段选择与时间解析组装轨迹，使用数值时间排序。"""

from collections.abc import Callable, Mapping

import numpy as np


def extract_time_series(
    fields: Mapping, select: Callable[[str], bool], parse_time: Callable[[str], float]
):
    """返回时间 [T] 与场 [T,N,...]；重复时间、空字段和形状变化拒绝。"""
    entries = sorted(
        [
            (float(parse_time(name)), np.asarray(value))
            for name, value in fields.items()
            if select(name)
        ],
        key=lambda entry: entry[0],
    )
    if not entries:
        raise ValueError("未匹配时间字段")
    times = np.array([entry[0] for entry in entries], dtype=np.float64)
    if not np.isfinite(times).all() or (np.diff(times) <= 0).any():
        raise ValueError("时间须有限且严格递增")
    if len({value.shape for _, value in entries}) != 1:
        raise ValueError("逐帧字段形状变化")
    return times, np.stack([value for _, value in entries])


def mesh_trajectory(
    mesh, *, displacement_prefix, cell_prefixes, requested, zero_initial_displacement=False
):
    """按参数选择网格时间字段，转点后构造位置轨迹，缺帧报错。"""
    from ai4e_core.abilities.data.validate.time_series import validate_time_series
    from ai4e_core.abilities.transform.mesh_fields import cell_fields_to_points
    from ai4e_core.abilities.transform.trajectory import time_window

    times, displacement = extract_time_series(
        mesh.point_data,
        lambda n: n.startswith(displacement_prefix),
        lambda n: float(n[len(displacement_prefix) :]),
    )
    validate_time_series(times, {"displacement": displacement}, np.arange(mesh.n_points))
    displacement = time_window(times, displacement, requested)
    positions = np.asarray(mesh.points, dtype=np.float64)[None] + displacement
    if zero_initial_displacement:
        positions[0] = mesh.points
    dynamic = []
    for prefix in cell_prefixes:
        names = tuple(name for name in mesh.cell_data if name.startswith(prefix))
        fields, _, _ = cell_fields_to_points(mesh, names)
        dt, values = extract_time_series(
            fields, lambda n: True, lambda n, prefix=prefix: float(n[len(prefix) :])
        )
        if values.ndim == 2:
            values = values[..., None]
        validate_time_series(dt, {"field": values}, np.arange(mesh.n_points))
        dynamic.append(time_window(dt, values, requested))
    return positions.astype(np.float32), np.concatenate(dynamic, axis=-1).astype(np.float32)
