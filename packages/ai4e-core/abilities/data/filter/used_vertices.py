"""用 VTK 单元类型和点号生成有效点 mask。"""

from __future__ import annotations

import numpy as np
from vtkmodules.util.vtkConstants import (
    VTK_HEXAHEDRON,
    VTK_QUAD,
    VTK_TETRA,
    VTK_TRIANGLE,
)
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkDataSet

from ai4e_core.base.events import traced

CELL_TYPE_NAMES: dict[str, int] = {
    "triangle": VTK_TRIANGLE,
    "quad": VTK_QUAD,
    "tetra": VTK_TETRA,
    "hexahedron": VTK_HEXAHEDRON,
    "hex": VTK_HEXAHEDRON,
}


def resolve_cell_type(cell_type: str | int) -> int:
    """把约定的单元类型名或 VTK 类型号解析为类型号。

    Raises:
        ValueError: 类型名不认识。
    """
    if isinstance(cell_type, int):
        return cell_type
    key = cell_type.strip().lower()
    if key not in CELL_TYPE_NAMES:
        raise ValueError(f"不认识的单元类型: {cell_type}")
    return CELL_TYPE_NAMES[key]


@traced("有效点标记")
def used_vertex_mask(data: vtkDataObject, *, cell_type: str | int) -> np.ndarray:
    """标出参与指定类型单元的顶点，不修改原对象、不删点。

    所有单元必须是约定类型。点表里从未出现在任何单元中的点为无效。

    Args:
        data: 已读入的 VTK 内存对象。
        cell_type: 单元类型名（如 ``quad``）或 VTK 类型号。

    Returns:
        与点数等长的布尔 mask，``True`` 表示该点参与了网格。

    Raises:
        TypeError: 不是带单元的数据集。
        ValueError: 没有点或单元，或存在其他类型的单元。
    """
    if not isinstance(data, vtkDataSet):
        raise TypeError("有效点 mask 需要带单元的 VTK 数据集")
    expected = resolve_cell_type(cell_type)
    n_points = data.GetNumberOfPoints()
    n_cells = data.GetNumberOfCells()
    if n_points == 0:
        raise ValueError("VTK 对象没有点")
    if n_cells == 0:
        raise ValueError("VTK 对象没有单元")

    used: set[int] = set()
    for index in range(n_cells):
        cell = data.GetCell(index)
        actual = cell.GetCellType()
        if actual != expected:
            raise ValueError(f"单元类型不符: 期望 {expected}，得到 {actual}（第 {index} 个单元）")
        ids = cell.GetPointIds()
        for offset in range(ids.GetNumberOfIds()):
            used.add(ids.GetId(offset))

    mask = np.zeros(n_points, dtype=bool)
    if used:
        mask[np.fromiter(used, dtype=np.int64, count=len(used))] = True
    return mask
