"""按精确名称和点/单元归属提取 VTK 数值字段，优先保留共享视图。"""

from __future__ import annotations

from typing import Literal

import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonCore import vtkDataArray
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSet

from ai4e_core.base.events import traced

Association = Literal["point", "cell"]
FieldKind = Literal["scalar", "vector"]


@traced("坐标提取")
def extract_coordinates(data: vtkDataObject) -> np.ndarray:
    """提取原点序的 ``(N, 3)`` 坐标，不计算单元中心。

    返回值优先共享 VTK 存储，不强制连续化、复制或转换 dtype。
    修改共享数组可能改变 VTK；替换点表或拓扑后必须重新提取。

    Args:
        data: 带点的 VTK 数据集。

    Returns:
        原点序坐标数组；不保证所有 VTK 后端都支持零复制。

    Raises:
        TypeError: 输入不是 VTK 数据集。
        ValueError: 没有坐标或坐标形状不是 (N, 3)。
    """
    dataset = _as_dataset(data)
    points = dataset.GetPoints()
    if points is None or dataset.GetNumberOfPoints() == 0:
        raise ValueError("VTK 对象没有点坐标")
    array = vtk_to_numpy(points.GetData())
    if array.shape != (dataset.GetNumberOfPoints(), 3):
        raise ValueError(f"点坐标形状不是 (N, 3): {array.shape}")
    return array


@traced("字段提取")
def extract_field(
    data: vtkDataObject, *, name: str, association: Association, kind: FieldKind
) -> np.ndarray:
    """按名称与归属提取数值字段，不依赖活动字段或转换点/单元场。

    Args:
        data: VTK 数据集。
        name: VTK 原始数组精确名称。
        association: point 读取 PointData，cell 读取 CellData。
        kind: scalar 要求一个分量；vector 要求三个分量。

    Returns:
        标量 (N,) 或矢量 (N, 3)，N 为相应点数或单元数。优先共享 VTK
        存储，不复制或强制转 dtype。调用方修改数组可能改变原场；替换字段
        数组或改变拓扑、点序后必须重新提取，所有后端不保证零复制。

    Raises:
        TypeError: 输入不是数据集，或字段不是数值数组。
        ValueError: 名称/归属/类别无效、字段缺失、分量数或元组数错误。
    """
    dataset = _as_dataset(data)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("字段名称必须是非空字符串")
    if association not in ("point", "cell"):
        raise ValueError(f"字段归属必须是 point 或 cell: {association}")
    if kind not in ("scalar", "vector"):
        raise ValueError(f"字段类别必须是 scalar 或 vector: {kind}")
    attrs = dataset.GetPointData() if association == "point" else dataset.GetCellData()
    field = attrs.GetAbstractArray(name)
    if field is None:
        raise ValueError(
            f"VTK {association} 字段不存在: {name}；可用数组={[attrs.GetArrayName(i) for i in range(attrs.GetNumberOfArrays())]}"
        )
    if not isinstance(field, vtkDataArray):
        raise TypeError(f"VTK {association} 字段不是数值数组: {name}")
    components = 1 if kind == "scalar" else 3
    if field.GetNumberOfComponents() != components:
        raise ValueError(
            f"字段 {name} 分量数错误: 期望 {components}，得到 {field.GetNumberOfComponents()}"
        )
    count = dataset.GetNumberOfPoints() if association == "point" else dataset.GetNumberOfCells()
    if field.GetNumberOfTuples() != count:
        raise ValueError(
            f"字段 {name} 数量不对齐: field={field.GetNumberOfTuples()}, {association}={count}"
        )
    return vtk_to_numpy(field)


def extract_scalars(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray:
    """按显式名称和归属提取单分量字段，共享行为与错误契约同 extract_field。"""
    return extract_field(data, name=name, association=association, kind="scalar")


def extract_vectors(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray:
    """按显式名称和归属提取三分量字段，共享行为与错误契约同 extract_field。"""
    return extract_field(data, name=name, association=association, kind="vector")


def _as_dataset(data: vtkDataObject) -> vtkDataSet:
    """拒绝无网格 FieldData 容器及非 VTK 数据集。"""
    if not isinstance(data, vtkDataSet):
        raise TypeError("抽取需要带点的 VTK 数据集")
    return data
