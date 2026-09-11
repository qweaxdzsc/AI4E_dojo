"""共享几何上的模型比较、原点映射与物理平面切割。"""

import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy


def match_points(points, source_points):
    """在 PT 保存精度下精确匹配原点；歧义、遗漏或重复均拒绝。"""
    points = np.asarray(points)
    source = np.asarray(source_points, dtype=points.dtype)
    key_type = np.dtype((np.void, points.dtype.itemsize * 3))
    keys = np.ascontiguousarray(source).view(key_type).ravel()
    query = np.ascontiguousarray(points).view(key_type).ravel()
    unique, counts = np.unique(keys, return_counts=True)
    if np.any(np.isin(unique[counts > 1], query)):
        raise ValueError("原坐标映射存在重复点歧义，需要显式原 ID")
    order = np.argsort(keys)
    locations = np.searchsorted(keys[order], query)
    if (locations >= len(order)).any() or not np.array_equal(keys[order[locations]], query):
        raise ValueError("物理点无法精确映射到原网格")
    result = order[locations]
    if len(np.unique(result)) != len(result):
        raise ValueError("物理点重复映射")
    return result


def attach_valid_mesh(mesh, points, arrays, *, source_ids=None):
    """仅保留所有顶点均有真实预测的单元，过滤区不补零。"""
    original = vtk_to_numpy(mesh.GetPoints().GetData())
    ids = match_points(points, original) if source_ids is None else np.asarray(source_ids)
    if (
        ids.ndim != 1
        or ids.dtype.kind not in "iu"
        or len(ids) != len(points)
        or len(np.unique(ids)) != len(ids)
        or (ids < 0).any()
        or (ids >= len(original)).any()
    ):
        raise ValueError("原点身份必须为唯一且范围内的整数序列")
    if any(len(values) != len(points) for values in arrays.values()):
        raise ValueError("预测字段与点数量不一致")
    if not np.array_equal(np.asarray(original[ids], dtype=points.dtype), points):
        raise ValueError("原点身份与坐标不一致")
    mapping = np.full(len(original), -1, dtype=np.int64)
    mapping[ids] = np.arange(len(ids))
    result = vtk.vtkUnstructuredGrid()
    coords = vtk.vtkPoints()
    coords.SetData(numpy_to_vtk(points, deep=True))
    result.SetPoints(coords)
    result.Allocate(mesh.GetNumberOfCells())
    original_cells = []
    for cell_id in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(cell_id)
        nodes = np.array([cell.GetPointId(i) for i in range(cell.GetNumberOfPoints())])
        rows = mapping[nodes]
        if (rows < 0).any():
            continue
        connectivity = vtk.vtkIdList()
        for row in rows:
            connectivity.InsertNextId(int(row))
        result.InsertNextCell(cell.GetCellType(), connectivity)
        original_cells.append(cell_id)
    if not result.GetNumberOfCells():
        raise ValueError("没有顶点全部有效的网格单元")
    for name, values in {**arrays, "original_point_id": ids}.items():
        value = numpy_to_vtk(np.ascontiguousarray(values), deep=True)
        value.SetName(name)
        result.GetPointData().AddArray(value)
    cell_ids = numpy_to_vtk(np.asarray(original_cells, dtype=np.int64), deep=True)
    cell_ids.SetName("original_cell_id")
    result.GetCellData().AddArray(cell_ids)
    return result


def cut_plane(mesh, *, axis, fraction):
    """物理包围盒内定位，VTK 对同一拓扑同时插值真值和全部预测。"""
    if axis not in (0, 1, 2) or not 0 < fraction < 1:
        raise ValueError("切面轴或比例不合法")
    bounds = mesh.GetBounds()
    origin = [(bounds[2 * i] + bounds[2 * i + 1]) / 2 for i in range(3)]
    origin[axis] = bounds[2 * axis] + fraction * (bounds[2 * axis + 1] - bounds[2 * axis])
    normal = [0.0, 0.0, 0.0]
    normal[axis] = 1.0
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)
    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputData(mesh)
    cutter.Update()
    output = vtk.vtkPolyData()
    output.DeepCopy(cutter.GetOutput())
    if not output.GetNumberOfPoints():
        raise ValueError("切面与有效几何没有交点")
    return output, {
        "axis": axis,
        "fraction": fraction,
        "origin": origin,
        "normal": normal,
        "interpolation": "VTK cell interpolation",
        "invalid_region": "excluded",
    }


def surface(mesh):
    """保留已装配场量并提取可渲染表面。"""
    algorithm = vtk.vtkDataSetSurfaceFilter()
    algorithm.SetInputData(mesh)
    algorithm.Update()
    result = vtk.vtkPolyData()
    result.DeepCopy(algorithm.GetOutput())
    return result


def write_polydata(path, mesh):
    """通过数据保存事务输出稳定 VTP，供独立 viz 读取。"""
    from ai4e_core.abilities.data.save.arrays import atomic_path

    with atomic_path(path) as temporary:
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(str(temporary))
        writer.SetInputData(mesh)
        if writer.Write() != 1:
            raise OSError(f"网格写入失败: {path}")
