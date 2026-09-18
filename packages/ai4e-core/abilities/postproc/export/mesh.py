"""把预测场写回原始网格，并按模版门禁验收表面 VTP 与体积 VTU。"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkCommand
from vtkmodules.vtkCommonDataModel import (
    vtkDataSet,
    vtkImageData,
    vtkPolyData,
    vtkRectilinearGrid,
    vtkStructuredGrid,
    vtkUnstructuredGrid,
)
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkIOXML import (
    vtkXMLPolyDataReader,
    vtkXMLPolyDataWriter,
    vtkXMLUnstructuredGridReader,
    vtkXMLUnstructuredGridWriter,
)


def mesh_topology_kind(mesh) -> str:
    """判断网格是结构化、非结构、表面还是只有点，不猜测文件名。

    结构化含图像/矩形/结构网格；有面或体单元的 PolyData 算表面；
    只有独立顶点时算点云。调用方据此选择写出器，不能把点云冒充网格。
    """
    if isinstance(mesh, (vtkImageData, vtkRectilinearGrid, vtkStructuredGrid)):
        return "structured"
    if isinstance(mesh, vtkUnstructuredGrid):
        return "unstructured" if mesh.GetNumberOfCells() > 0 else "points"
    if isinstance(mesh, vtkPolyData):
        if mesh.GetNumberOfPolys() > 0 or mesh.GetNumberOfStrips() > 0:
            return "surface"
        if mesh.GetNumberOfVerts() > 0 and mesh.GetNumberOfCells() == mesh.GetNumberOfPoints():
            return "pointcloud"
        return "surface" if mesh.GetNumberOfCells() > 0 else "points"
    if isinstance(mesh, vtkDataSet) and mesh.GetNumberOfCells() > 0:
        return "unstructured"
    return "points"


def extract_point_field(data, *, kind: str, names: tuple[str, ...] = ()):
    """从点数据取出第一个匹配场；没有则返回 ``None``，不猜单元场。"""
    if not isinstance(data, vtkDataSet):
        raise TypeError("抽取真值需要带点的 VTK 数据集")
    if kind not in {"scalar", "vector"}:
        raise ValueError(f"字段类别必须是 scalar 或 vector: {kind}")
    attrs = data.GetPointData()
    candidates = list(names)
    active = attrs.GetScalars() if kind == "scalar" else attrs.GetVectors()
    if active is not None:
        candidates.append(active.GetName())
    for index in range(attrs.GetNumberOfArrays()):
        candidates.append(attrs.GetArrayName(index))
    seen: set[str] = set()
    expected = 1 if kind == "scalar" else 3
    for name in candidates:
        if not name or name in seen:
            continue
        seen.add(name)
        field = attrs.GetArray(name)
        if field is None or field.GetNumberOfComponents() != expected:
            continue
        array = np.asarray(vtk_to_numpy(field))
        return array.reshape(-1) if kind == "scalar" else array
    return None


def write_surface_mesh(source, pred_pressure, path, *, gt=None, overwrite: bool = False) -> Path:
    """把压力写回原始网格，抽成面网格后存为 ``.vtp``。"""
    pred = _as_scalar(pred_pressure, source.GetNumberOfPoints(), "压力")
    mesh = _clone(source)
    _attach(mesh, "pred_pressure", pred)
    truth = None if gt is None else _as_scalar(gt, len(pred), "压力真值", required=False)
    if truth is not None:
        _attach(mesh, "gt_pressure", truth)
        _attach(mesh, "error_pressure", np.abs(pred - truth))
    return _write_polydata(_extract_surface(mesh), path, overwrite=overwrite)


def surface_mesh_point_count(source) -> int:
    """返回面提取后的点数；原始网格未被单元引用的点不会进入表面交付。"""
    return _extract_surface(source).GetNumberOfPoints()


def write_volume_mesh(source, pred_velocity, path, *, gt=None, overwrite: bool = False) -> Path:
    """把速度写回原始体积网格，保留体单元后存为 ``.vtu``。"""
    if not isinstance(source, vtkDataSet) or source.GetNumberOfCells() <= 0:
        raise TypeError("体积回写需要带体单元的网格")
    pred = _as_vector(pred_velocity, source.GetNumberOfPoints(), "速度")
    mesh = _as_unstructured(source)
    _attach(mesh, "pred_velocity", pred)
    truth = None if gt is None else _as_vector(gt, len(pred), "速度真值", required=False)
    if truth is not None:
        _attach(mesh, "gt_velocity", truth)
        _attach(mesh, "error_velocity", np.linalg.norm(pred - truth, axis=-1))
    return _write_unstructured(mesh, path, overwrite=overwrite)


def verify_mesh_outputs(
    surface_path,
    volume_path,
    *,
    n_surface: int | None = None,
    n_volume: int | None = None,
    min_points: int | None = None,
) -> None:
    """验收已写网格：必须有预测场和单元；夹具对齐原点数，正式样本大于锚点数。"""
    surface = _read_polydata(surface_path)
    volume = _read_unstructured(volume_path)
    if surface.GetNumberOfCells() <= 0:
        raise RuntimeError(f"{surface_path} 没有面单元")
    if volume.GetNumberOfCells() <= 0:
        raise RuntimeError(f"{volume_path} 没有体单元")
    if surface.GetPointData().GetArray("pred_pressure") is None:
        raise RuntimeError(f"{surface_path} 缺少 pred_pressure")
    if volume.GetPointData().GetArray("pred_velocity") is None:
        raise RuntimeError(f"{volume_path} 缺少 pred_velocity")
    if min_points is not None:
        if surface.GetNumberOfPoints() <= min_points:
            raise RuntimeError(f"{surface_path} 点数不是完整网格")
        if volume.GetNumberOfPoints() <= min_points:
            raise RuntimeError(f"{volume_path} 点数不是完整网格")
        return
    if n_surface is not None and surface.GetNumberOfPoints() != n_surface:
        raise RuntimeError(f"{surface_path} 点数与原始网格不一致")
    if n_volume is not None and volume.GetNumberOfPoints() != n_volume:
        raise RuntimeError(f"{volume_path} 点数与原始网格不一致")


def _as_scalar(value, count: int, label: str, *, required: bool = True):
    array = np.asarray(value).reshape(-1)
    if array.shape[0] != count:
        if required:
            raise ValueError(f"{label}长度必须等于原始顶点数")
        return None
    return array


def _as_vector(value, count: int, label: str, *, required: bool = True):
    array = np.asarray(value)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if array.shape != (count, 3):
        if required:
            raise ValueError(f"{label}形状必须是 (N, 3)")
        return None
    return array


def _clone(data):
    clone = data.NewInstance()
    clone.DeepCopy(data)
    return clone


def _as_unstructured(source) -> vtkUnstructuredGrid:
    if isinstance(source, vtkUnstructuredGrid):
        mesh = vtkUnstructuredGrid()
        mesh.DeepCopy(source)
        return mesh
    from vtkmodules.vtkFiltersCore import vtkAppendFilter

    filt = vtkAppendFilter()
    filt.SetInputData(source)
    filt.Update()
    mesh = vtkUnstructuredGrid()
    mesh.DeepCopy(filt.GetOutput())
    return mesh


def _attach(mesh, name: str, values) -> None:
    array = np.ascontiguousarray(values)
    vtk_array = numpy_to_vtk(array, deep=True)
    vtk_array.SetName(name)
    mesh.GetPointData().AddArray(vtk_array)


def _extract_surface(mesh) -> vtkPolyData:
    filt = vtkDataSetSurfaceFilter()
    filt.PassThroughPointIdsOn()
    filt.PassThroughCellIdsOn()
    filt.SetInputData(mesh)
    filt.Update()
    surface = vtkPolyData()
    surface.DeepCopy(filt.GetOutput())
    return surface


def _write_polydata(mesh, path, *, overwrite: bool) -> Path:
    return _write_xml(mesh, path, vtkXMLPolyDataWriter(), overwrite=overwrite, label="表面网格")


def _write_unstructured(mesh, path, *, overwrite: bool) -> Path:
    return _write_xml(
        mesh, path, vtkXMLUnstructuredGridWriter(), overwrite=overwrite, label="体积网格"
    )


def _write_xml(mesh, path, writer, *, overwrite: bool, label: str) -> Path:
    target = Path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(f"{label}已存在: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.stem}.{uuid4().hex}{target.suffix}")
    errors = []
    writer.AddObserver(vtkCommand.ErrorEvent, lambda *_: errors.append(True))
    writer.SetFileName(str(temporary))
    writer.SetInputData(mesh)
    try:
        if writer.Write() != 1 or errors or not temporary.is_file():
            raise RuntimeError(f"{label}写出失败")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def _read_polydata(path) -> vtkPolyData:
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()


def _read_unstructured(path) -> vtkUnstructuredGrid:
    reader = vtkXMLUnstructuredGridReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()
