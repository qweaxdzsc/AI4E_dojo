"""按文件格式读取并统一返回 VTK 内存对象。"""

from collections.abc import Callable
from pathlib import Path

from vtkmodules.vtkCommonDataModel import vtkDataObject

from ai4e_core.abilities.data.source.adapter import npy, vtk

type NativeData = vtkDataObject
type AdapterFn = Callable[[Path], NativeData]

ADAPTERS: dict[str, AdapterFn] = {
    "vtk": vtk.load,
    "npy": npy.load,
}

__all__ = ["ADAPTERS", "AdapterFn", "NativeData"]
