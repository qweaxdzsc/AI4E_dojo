"""有拓扑网格的具名插值与规则格回贴；无支撑点显式返回无效标记。"""

import numpy as np


def regular_coordinates(bounds, shape):
    """按物理包围盒生成末轴xyz、C顺序规则格，禁止退化轴。"""
    if len(bounds) != 6 or len(shape) != 3 or any(type(n) is not int or n < 2 for n in shape):
        raise ValueError("三维包围盒或格点数非法")
    if not np.isfinite(bounds).all() or any(bounds[2 * i] >= bounds[2 * i + 1] for i in range(3)):
        raise ValueError("包围盒必须有限且非退化")
    return np.stack(
        np.meshgrid(
            *[np.linspace(bounds[2 * i], bounds[2 * i + 1], shape[i]) for i in range(3)],
            indexing="ij",
        ),
        axis=-1,
    )


def probe_fields(mesh, points, names):
    """用真实单元插值点场；返回具名数组和布尔有效域，不启用最近点补洞。"""
    import pyvista as pv

    points = np.asarray(points)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError("查询坐标须为有限N×3数组")
    if not names or mesh.n_cells == 0 or any(n not in mesh.point_data for n in names):
        raise ValueError("插值需真实网格单元和明确点场")
    sampled = pv.PolyData(points).sample(mesh, snap_to_closest_point=False)
    valid = np.asarray(sampled["vtkValidPointMask"], dtype=bool)
    values = {}
    for name in names:
        value = np.array(sampled.point_data[name], copy=True)
        if not np.isfinite(value[valid]).all():
            raise ValueError("有效插值结果非有限")
        value[~valid] = 0
        values[name] = value
    return values, valid


def probe_regular(coordinates, values, valid, points):
    """规则格回贴，只接受所有插值支撑均有效的点，保持查询实体行序。"""
    import pyvista as pv

    coordinates, values, valid = map(np.asarray, (coordinates, values, valid))
    if coordinates.ndim != 4 or coordinates.shape[-1] != 3:
        raise ValueError("规则格坐标须为Nx×Ny×Nz×3")
    if values.shape[:3] != coordinates.shape[:3] or valid.shape != coordinates.shape[:3]:
        raise ValueError("规则格字段与有效域尺寸不一致")
    # VTK i轴最快；反转逻辑维度，使实际points恰为公开C-order。
    grid = pv.StructuredGrid()
    grid.points = coordinates.reshape(-1, 3)
    grid.dimensions = coordinates.shape[:3][::-1]
    grid.point_data["value"] = values.reshape((valid.size,) + values.shape[3:])
    cell_valid = np.ones(tuple(n - 1 for n in valid.shape), dtype=bool)
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                cell_valid &= valid[
                    i : i + valid.shape[0] - 1,
                    j : j + valid.shape[1] - 1,
                    k : k + valid.shape[2] - 1,
                ]
    if not cell_valid.any():
        return np.zeros((len(points),) + values.shape[3:], dtype=values.dtype), np.zeros(
            len(points), bool
        )
    # 先删不完整支撑的单元，禁止用接近1的插值mask阈值“补回”孔洞。
    complete = grid.extract_cells(np.flatnonzero(cell_valid.reshape(-1)))
    arrays, supported = probe_fields(complete, points, ("value",))
    return arrays["value"], supported
