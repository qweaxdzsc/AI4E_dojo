"""完整 VTK 表面的公共门禁与私有工作副本，转换中保留原点身份。"""

from dataclasses import dataclass

import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.util.vtkConstants import (
    VTK_PIXEL,
    VTK_POLYGON,
    VTK_QUAD,
    VTK_TRIANGLE,
    VTK_TRIANGLE_STRIP,
)
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSet, vtkPolyData
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

SURFACE_CELL_TYPES = frozenset({VTK_TRIANGLE, VTK_TRIANGLE_STRIP, VTK_POLYGON, VTK_PIXEL, VTK_QUAD})
ORIGINAL_POINT_IDS = "__ai4e_original_point_ids"


@dataclass(frozen=True)
class PreparedSurface:
    """与输入存储独立的表面，以及原点数和面参与标记。"""

    poly: vtkPolyData
    point_count: int
    used_points: np.ndarray


def require_surface_mesh(data: vtkDataObject) -> vtkDataSet:
    """要求非空 VTK 网格的全部单元均为支持的二维面；不提取体外壳。

    允许混合面类型和弯曲、开放表面。首次遇到点、线、体或不支持的
    面类型即抛 ValueError，并报告原单元编号与类型。输入不会被修改。
    """
    if not isinstance(data, vtkDataSet):
        raise ValueError("表面需要带网格的 VTK 数据集，不能是无网格对象或点云")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
    if data.GetNumberOfPoints() == 0:
        raise ValueError("表面网格没有点")
    if data.GetNumberOfCells() == 0:
        raise ValueError("表面需要面单元，不能是裸点云")
    for index in range(data.GetNumberOfCells()):
        cell = data.GetCell(index)
        if cell.GetCellType() not in SURFACE_CELL_TYPES or cell.GetCellDimension() != 2:
            raise ValueError(
                f"表面单元门禁失败: 第 {index} 个单元类型={cell.GetCellType()}，"
                "必须全部为支持的二维面单元"
            )
    return data


def prepare_surface(data: vtkDataObject) -> PreparedSurface:
    """验证并转换私有表面副本，携带原 point ID，不继承调用方旧法向。

    几何计算不需要物理场；工作副本清除属性后仅添加身份数组，避免
    VTK 复用已有 Normals 或同名身份字段。原始对象的所有属性不变。
    """
    dataset = require_surface_mesh(data)
    count = dataset.GetNumberOfPoints()
    used = np.zeros(count, dtype=bool)
    for index in range(dataset.GetNumberOfCells()):
        ids = dataset.GetCell(index).GetPointIds()
        used[[ids.GetId(i) for i in range(ids.GetNumberOfIds())]] = True
    for index in np.flatnonzero(used):
        if not np.isfinite(dataset.GetPoint(int(index))).all():
            raise RuntimeError(f"表面点 {index} 坐标含 NaN 或 Inf")

    clone = dataset.NewInstance()
    clone.DeepCopy(dataset)
    clone.GetPointData().Initialize()
    clone.GetCellData().Initialize()
    clone.GetFieldData().Initialize()
    original = numpy_to_vtk(np.arange(count, dtype=np.int64), deep=True)
    original.SetName(ORIGINAL_POINT_IDS)
    clone.GetPointData().AddArray(original)
    extractor = vtkDataSetSurfaceFilter()
    extractor.SetInputData(clone)
    extractor.Update()
    poly = vtkPolyData()
    poly.DeepCopy(extractor.GetOutput())
    original_ids = poly.GetPointData().GetArray(ORIGINAL_POINT_IDS)
    if original_ids is None or poly.GetNumberOfCells() == 0:
        raise ValueError("表面转换未保留面单元或原点身份")
    ids = vtk_to_numpy(original_ids)
    if np.any(ids < 0) or np.any(ids >= count):
        raise ValueError("表面转换的原点身份越界")
    return PreparedSurface(poly, count, used)
