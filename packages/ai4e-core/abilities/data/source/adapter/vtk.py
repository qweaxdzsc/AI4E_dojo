"""VTK 家族文件：读取为保留原始拓扑和字段的 VTK 对象。"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from vtkmodules.vtkCommonCore import vtkCommand
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkIOHDF import vtkHDFReader
from vtkmodules.vtkIOLegacy import vtkGenericDataObjectReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLUnstructuredGridReader

type VTKReader = (
    vtkGenericDataObjectReader | vtkXMLPolyDataReader | vtkXMLUnstructuredGridReader | vtkHDFReader
)
type ReaderFactory = Callable[[], VTKReader]


_READERS: dict[str, ReaderFactory] = {
    ".vtk": vtkGenericDataObjectReader,
    ".vtp": vtkXMLPolyDataReader,
    ".vtu": vtkXMLUnstructuredGridReader,
    ".vtkhdf": vtkHDFReader,
    ".vtkh5": vtkHDFReader,
}


def load(path: Path) -> vtkDataObject:
    """读取受支持的 VTK 家族文件，保留具体类型和全部关联数组。

    本函数直接返回 reader 的原生输出，不抽取数组、不转换数据类型，也不改变
    PointData、CellData、FieldData 或拓扑。``.vtkh5`` 作为标准
    ``.vtkhdf`` 内容的兼容扩展名处理。

    Args:
        path: 已确认存在的 VTK 家族文件路径。

    Returns:
        VTK reader 生成的原生数据对象。

    Raises:
        ValueError: 扩展名不受支持、文件损坏、内容与格式不匹配或 reader 没有输出。
    """
    suffix = path.suffix.lower()
    reader_factory = _READERS.get(suffix)
    if reader_factory is None:
        raise ValueError(f"不支持的 VTK 家族格式: {path}")

    reader = reader_factory()
    if isinstance(reader, vtkGenericDataObjectReader):
        # Legacy 默认可能只读取首个同类数组；显式保留所有数组。
        reader.ReadAllScalarsOn()
        reader.ReadAllVectorsOn()
        reader.ReadAllNormalsOn()
        reader.ReadAllTensorsOn()
        reader.ReadAllTCoordsOn()
        reader.ReadAllFieldsOn()
    errors: list[str] = []

    def record_error(_caller: object, event: str) -> None:
        """记录 VTK 管线错误，避免把空输出当作成功。"""
        errors.append(event)

    reader.AddObserver(vtkCommand.ErrorEvent, record_error)
    reader.SetFileName(str(path))

    can_read = getattr(reader, "CanReadFile", None)
    if can_read is not None and can_read(str(path)) == 0:
        raise ValueError(f"VTK 文件内容与格式不匹配: {path} ({suffix})")

    reader.Update()
    if errors or reader.GetErrorCode() != 0:
        raise ValueError(f"VTK 文件读取失败: {path} ({suffix})")

    output = reader.GetOutputDataObject(0)
    if output is None:
        raise ValueError(f"VTK reader 没有产生数据对象: {path} ({suffix})")
    return output
