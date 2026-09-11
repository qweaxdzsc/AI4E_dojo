"""按文件扩展名分派真实读取能力。"""

from pathlib import Path

from ai4e_spec.data.inspection import FileInspection

from .hdf5 import inspect_hdf5
from .mesh import inspect_mesh
from .tensor import inspect_tensor
from .text import inspect_text


def inspect_file(path: str | Path) -> FileInspection:
    """返回文件实际字段；未知格式明确不支持。"""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".vtk", ".vtp", ".vtu", ".vtkhdf", ".vtkh5", ".vti", ".vts", ".vtr", ".vtm"}:
        return inspect_mesh(path)
    if suffix in {".h5", ".hdf5"}:
        return inspect_hdf5(path)
    if suffix in {".pt", ".npy", ".zarr"}:
        return inspect_tensor(path)
    if suffix in {".txt", ".csv", ".json", ".yaml", ".yml", ".log", ".md", ".py"}:
        return inspect_text(path)
    raise ValueError(f"unsupported_format: {suffix}")
