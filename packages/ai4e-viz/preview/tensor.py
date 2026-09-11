"""张量维度切片，保留类型与整数精度，不隐式展平高维数据。"""

from pathlib import Path


def preview_tensor(
    path: Path, field=None, offset=0, limit=100, axes=None, indices=None, **_
) -> dict:
    """指定行列轴，其余维度固定索引；兼容旧二维分页调用。"""
    import numpy as np

    from ..inspect.hdf5 import read_hdf5_array
    from ..inspect.tensor import read_tensors

    if path.suffix.lower() in {".h5", ".hdf5"}:
        a = read_hdf5_array(path, field)
        key = field or "array"
    else:
        values = read_tensors(path)
        key = field or next(iter(values))
        a = values[key]
    axes = axes if axes is not None else list(range(min(2, len(a.shape))))
    if (
        len(set(axes)) != len(axes)
        or len(axes) > 2
        or any(i < 0 or i >= len(a.shape) for i in axes)
    ):
        raise ValueError("invalid_slice_axes")
    selection = []
    indices = indices or {}
    for i, size in enumerate(a.shape):
        if i in axes:
            selection.append(
                slice(max(0, offset), max(0, offset) + min(200, max(1, limit)))
                if i == axes[0]
                else slice(0, 64)
            )
        else:
            index = int(indices.get(str(i), indices.get(i, 0)))
            if not 0 <= index < size:
                raise ValueError("slice_index_out_of_range")
            selection.append(index)
    data = np.asarray(a[tuple(selection)] if a.shape else a[()])
    if len(axes) == 2 and axes[0] > axes[1]:
        data = data.T
    data = data.reshape(1, 1) if data.ndim == 0 else data[:, None] if data.ndim == 1 else data

    def cell(x):
        if np.issubdtype(data.dtype, np.integer):
            n = int(x)
            return str(n) if abs(n) > 2**53 - 1 else n
        if np.issubdtype(data.dtype, np.bool_):
            return bool(x)
        return float(x) if np.isfinite(x) else None

    return {
        "kind": "tensor",
        "field": key,
        "shape": list(a.shape),
        "dtype": str(a.dtype),
        "offset": offset,
        "axes": axes,
        "indices": indices,
        "total": a.shape[axes[0]] if axes else 1,
        "columns_truncated": len(axes) > 1 and a.shape[axes[1]] > 64,
        "rows": [[cell(x) for x in row] for row in data],
    }
