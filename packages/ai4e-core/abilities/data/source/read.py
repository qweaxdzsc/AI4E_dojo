"""通用读取：先校验路径，再按格式转换为统一 VTK 内存对象。"""

from __future__ import annotations

from pathlib import Path

from vtkmodules.vtkCommonDataModel import vtkDataObject

from ai4e_core.abilities.data.source.adapter import ADAPTERS, NativeData
from ai4e_core.base.events import traced

_SUFFIX_TO_FORMAT = {
    ".vtk": "vtk",
    ".vtp": "vtk",
    ".vtu": "vtk",
    ".vtkhdf": "vtk",
    ".vtkh5": "vtk",
    ".npy": "npy",
}


def infer_format(path: str | Path) -> str:
    """根据扩展名推断格式名。

    Raises:
        ValueError: 扩展名没有对应适配器。
    """
    suffix = Path(path).suffix.lower()
    fmt = _SUFFIX_TO_FORMAT.get(suffix)
    if fmt is None:
        raise ValueError(f"不认识的文件格式: {path}")
    return fmt


@traced("读取")
def read_file(path: str | Path, *, format: str | None = None) -> NativeData:
    """读取单个文件。文件不在或格式不认识时不打开适配器。

    Args:
        path: 本地文件路径。
        format: 显式格式名；缺省时按扩展名推断。

    Returns:
        统一的 VTK 数据对象；无网格数组使用 FieldData 承载。

    Raises:
        FileNotFoundError: 目标文件不存在。
        ValueError: 格式不支持或数据转换失败。
        TypeError: 适配器未返回 VTK 对象。
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"读取目标不是已存在的文件: {file_path}")
    fmt = format or infer_format(file_path)
    adapter = ADAPTERS.get(fmt)
    if adapter is None:
        raise ValueError(f"没有适配器: {fmt}")
    output = adapter(file_path)
    if not isinstance(output, vtkDataObject):
        raise TypeError(f"适配器未返回 vtkDataObject: {file_path} ({fmt})")
    return output


def read_many(
    paths: list[str | Path],
    *,
    format: str | None = None,
) -> list[NativeData]:
    """按顺序读取多个文件，返回 VTK 对象列表；每项均校验返回契约。"""
    return [read_file(path, format=format) for path in paths]


def read_tree(
    root: str | Path,
    *,
    recursive: bool = True,
    format: str | None = None,
) -> list[tuple[Path, NativeData]]:
    """读取目录中已登记格式的文件，逐个转换为 VTK 对象。

    Args:
        root: 目录根。
        recursive: 是否进入子目录。
        format: 若给出，只读该格式。

    Returns:
        ``(路径, VTK 内存对象)`` 列表，按路径排序。
    """
    directory = Path(root)
    if not directory.is_dir():
        raise FileNotFoundError(f"读取目录不存在: {directory}")

    candidates = directory.rglob("*") if recursive else directory.iterdir()
    files = sorted(path for path in candidates if path.is_file() and _matches(path, format))
    return [(path, read_file(path, format=format)) for path in files]


def _matches(path: Path, format: str | None) -> bool:
    """文件是否属于已登记格式，或指定格式。"""
    suffix = path.suffix.lower()
    if format is None:
        return suffix in _SUFFIX_TO_FORMAT
    expected = {key for key, name in _SUFFIX_TO_FORMAT.items() if name == format}
    return suffix in expected
