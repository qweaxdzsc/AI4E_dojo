"""VTKHDF 公共网格写出：保留拓扑、具名场及原实体身份。"""

from pathlib import Path
from uuid import uuid4

import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk


def write_vtkhdf(path: str | Path, mesh, records=()) -> Path:
    """原子写出受支持网格，筛选字段按实体 ID 回贴，未选实体为 NaN。"""
    if not isinstance(mesh, (vtk.vtkPolyData, vtk.vtkUnstructuredGrid)):
        raise TypeError("VTKHDF 当前只支持 PolyData 和 UnstructuredGrid")
    records = tuple(records)
    if any(r["association"] not in {"point", "cell"} for r in records):
        raise ValueError("VTKHDF 字段必须声明 point/cell")
    copy = mesh.NewInstance()
    copy.DeepCopy(mesh)
    for association, count, attributes in [
        ("point", copy.GetNumberOfPoints(), copy.GetPointData()),
        ("cell", copy.GetNumberOfCells(), copy.GetCellData()),
    ]:
        identity = numpy_to_vtk(np.arange(count, dtype=np.int64), deep=True)
        identity.SetName("ai4e_" + association + "_id")
        attributes.AddArray(identity)
        for record in records:
            if record["association"] != association:
                continue
            ids = np.asarray(record["entity_ids"])
            values = np.asarray(record["values"])
            if (
                ids.ndim != 1
                or not np.issubdtype(ids.dtype, np.integer)
                or len(np.unique(ids)) != len(ids)
            ):
                raise ValueError("VTKHDF 实体 ID 必须为不重复整数序列")
            if len(ids) != len(values) or (ids < 0).any() or (ids >= count).any():
                raise ValueError("VTKHDF 字段身份越界或数量不一致")
            full = np.full((count, *values.shape[1:]), np.nan, dtype=float)
            full[ids] = values
            array = numpy_to_vtk(full, deep=True)
            array.SetName(record["name"])
            attributes.AddArray(array)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.stem}.{uuid4().hex}.vtkhdf")
    errors = []
    writer = vtk.vtkHDFWriter()
    writer.AddObserver(vtk.vtkCommand.ErrorEvent, lambda *_: errors.append(True))
    writer.SetFileName(str(temporary))
    writer.SetInputData(copy)
    try:
        if writer.Write() != 1 or errors or not temporary.is_file():
            raise RuntimeError("VTKHDF 写出失败")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target
