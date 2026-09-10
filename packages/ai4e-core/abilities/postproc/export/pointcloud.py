"""把锚点坐标与具名场写成带独立顶点单元的 VTK 点云。"""

from pathlib import Path
from uuid import uuid4

import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray


def write_pointcloud(path: str | Path, positions, fields: dict) -> Path:
    """写出每个点带一个 VTK_VERTEX 的 ``.vtp`` 点云，保留输入数值类型。

    这是锚点预览，不是完整网格回贴。标量 ``(N, 1)`` 压成一维，矢量保留分量。

    Args:
        path: 目标 ``.vtp`` 路径。
        positions: 点坐标，形状必须是 ``(N, 3)``。
        fields: 点数据场，首维必须等于点数。

    Returns:
        已提交的目标路径。

    Raises:
        ValueError: 坐标不是 ``(N, 3)``，或场点数对不上。
        RuntimeError: VTK 写出失败。
    """
    points = np.asarray(positions)
    if points.ndim != 2 or points.shape[1] != 3 or not len(points):
        raise ValueError("锚点坐标必须是非空 (N, 3)")
    count = len(points)
    poly = vtk.vtkPolyData()
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(np.ascontiguousarray(points), deep=True))
    poly.SetPoints(vtk_points)
    vertices = vtk.vtkCellArray()
    vertices.SetData(
        numpy_to_vtkIdTypeArray(np.arange(count + 1, dtype=np.int64), deep=True),
        numpy_to_vtkIdTypeArray(np.arange(count, dtype=np.int64), deep=True),
    )
    poly.SetVerts(vertices)
    for name, values in fields.items():
        array = np.asarray(values)
        if array.shape[0] != count:
            raise ValueError("点数或场形状对不上")
        if array.ndim == 2 and array.shape[1] == 1:
            array = array.reshape(count)
        vtk_array = numpy_to_vtk(np.ascontiguousarray(array), deep=True)
        vtk_array.SetName(str(name))
        poly.GetPointData().AddArray(vtk_array)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.stem}.{uuid4().hex}.vtp")
    errors = []
    writer = vtk.vtkXMLPolyDataWriter()
    writer.AddObserver(vtk.vtkCommand.ErrorEvent, lambda *_: errors.append(True))
    writer.SetFileName(str(temporary))
    writer.SetInputData(poly)
    try:
        if writer.Write() != 1 or errors or not temporary.is_file():
            raise RuntimeError("点云写出失败")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target
