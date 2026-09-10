"""表面法向按原始点身份回贴，孤立点以零值及有效性 mask 表达。"""

from __future__ import annotations

import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkCellDataToPointData, vtkPolyDataNormals

from ai4e_core.abilities.geometry.nearest import EPSILON
from ai4e_core.abilities.geometry.surface import ORIGINAL_POINT_IDS, prepare_surface
from ai4e_core.base.events import traced


@traced("表面法向")
def surface_point_normals_with_mask(
    surface: vtkDataObject, *, epsilon: float = EPSILON
) -> tuple[np.ndarray, np.ndarray]:
    """返回原点序法向 (N, 3) 和 normals_valid_mask (N,)。

    全部单元须为支持的二维面。只在私有表面上计算 cell normals 并转为
    point normals，再按原 point ID 回贴；不以数量推断顺序。沿用 VTK
    一致化和自动定向；开放表面不保证物理外向。孤立点为零且 mask=False。
    面或参与面的点出现非有限/零长度法向时抛 RuntimeError；输入不变。
    epsilon 必须为正有限数，保留已有两步归一化公式。
    """
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon 必须为正有限数")
    prepared = prepare_surface(surface)
    normal_filter = vtkPolyDataNormals()
    normal_filter.SetInputData(prepared.poly)
    normal_filter.SetAutoOrientNormals(1)
    normal_filter.SetConsistency(1)
    normal_filter.SplittingOff()
    normal_filter.SetComputeCellNormals(1)
    normal_filter.SetComputePointNormals(0)
    normal_filter.Update()
    poly = normal_filter.GetOutput()
    cell_array = poly.GetCellData().GetNormals()
    if cell_array is None:
        raise ValueError("无法从表面网格计算单元法向")
    cell_normals = vtk_to_numpy(cell_array)
    if not np.isfinite(cell_normals).all() or np.any(np.linalg.norm(cell_normals, axis=1) == 0):
        raise RuntimeError("表面单元法向含 NaN/Inf 或零长度（退化面）")

    cell_to_point = vtkCellDataToPointData()
    cell_to_point.SetInputData(poly)
    cell_to_point.Update()
    output = cell_to_point.GetOutput()
    point_array = output.GetPointData().GetNormals()
    id_array = output.GetPointData().GetArray(ORIGINAL_POINT_IDS)
    if point_array is None or id_array is None:
        raise ValueError("单元转点后缺少法向或原点身份")
    ids = np.asarray(vtk_to_numpy(id_array), dtype=np.int64)
    normals = np.asarray(vtk_to_numpy(point_array), dtype=np.float64)
    if normals.shape != (len(ids), 3) or len(np.unique(ids)) != len(ids):
        raise ValueError("表面点法向与原点身份不能一一对应")
    if np.any(ids < 0) or np.any(ids >= prepared.point_count):
        raise ValueError("表面法向原点身份越界")
    active = prepared.used_points[ids]
    values = normals[active]
    if not np.isfinite(values).all() or np.any(np.linalg.norm(values, axis=1) == 0):
        raise RuntimeError("参与面的点法向含 NaN/Inf 或零长度")
    values = values / (np.max(np.abs(values), axis=1, keepdims=True) + epsilon)
    values = values / (np.linalg.norm(values, axis=1, keepdims=True) + epsilon)
    result = np.zeros((prepared.point_count, 3), dtype=np.float64)
    valid = np.zeros(prepared.point_count, dtype=bool)
    result[ids[active]] = values
    valid[ids[active]] = True
    if not np.array_equal(valid, prepared.used_points):
        raise ValueError("表面转换丢失参与面的原点身份")
    return result, valid


def surface_point_normals(surface: vtkDataObject, *, epsilon: float = EPSILON) -> np.ndarray:
    """兼容数组返回接口；完整门禁与有效性语义见 surface_point_normals_with_mask。

    返回原点序 (N, 3)，孤立点为零；需要区分孤立点时使用带 mask 的入口。
    """
    return surface_point_normals_with_mask(surface, epsilon=epsilon)[0]
