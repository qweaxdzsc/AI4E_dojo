"""NumPy NPY 转为无网格 VTK 对象，使用 FieldData 保留数组与恢复信息。"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonCore import vtkStringArray
from vtkmodules.vtkCommonDataModel import vtkDataObject


def load(path: Path) -> vtkDataObject:
    """读取 NPY 并转为包含 values 和恢复元数据的 VTK FieldData。

    数组按 C 顺序展平为单分量数组，不猜测坐标、向量或网格归属。
    VTK 持有数据副本，原始 NumPy 数组释放后仍可使用。元数据中的
    schema_version、shape、dtype、order 分别记录表示版本和恢复规则。

    Args:
        path: 已确认存在的 NPY 文件路径。

    Returns:
        无网格 vtkDataObject；values 存数值，__ai4e_npy_metadata 存 JSON。
        支持 bool、8/16/32/64 位整数及 float32/64。布尔用 uint8 承载，
        其他数值保持精度；非本机字节序转本机字节序，元数据保留原 dtype。

    Raises:
        ValueError: 文件损坏、需要 pickle 或 dtype 不在支持范围内。
    """
    try:
        array = np.load(path, allow_pickle=False)
    except (ValueError, EOFError, OSError) as exc:
        raise ValueError(f"NPY 读取失败: {path}: {exc}") from exc
    if not isinstance(array, np.ndarray):
        close = getattr(array, "close", None)
        if close is not None:
            close()
        # 这是输入文件内容错误，统一使用 ValueError。
        raise ValueError(f"NPY 内容不是单个数组: {path}")  # noqa: TRY004

    dtype = array.dtype
    supported = (
        dtype.kind == "b"
        or (dtype.kind in "iu" and dtype.itemsize in (1, 2, 4, 8))
        or (dtype.kind == "f" and dtype.itemsize in (4, 8))
    )
    if not supported:
        raise ValueError(f"NPY 不支持的 dtype: {dtype} ({path})")

    storage_dtype = np.dtype("uint8") if dtype.kind == "b" else dtype.newbyteorder("=")
    flat = np.ascontiguousarray(array.astype(storage_dtype, copy=False).ravel(order="C"))
    values = numpy_to_vtk(flat, deep=True)
    values.SetName("values")

    metadata = vtkStringArray()
    metadata.SetName("__ai4e_npy_metadata")
    metadata.InsertNextValue(
        json.dumps(
            {
                "schema_version": 1,
                "shape": list(array.shape),
                "dtype": dtype.str,
                "order": "C",
            }
        )
    )
    output = vtkDataObject()
    output.GetFieldData().AddArray(values)
    output.GetFieldData().AddArray(metadata)
    return output
