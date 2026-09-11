"""真实字段有效值统计，不修改训练归一化记录。"""

from pathlib import Path


def summarize(path: Path, field: str, bins: int = 32, **_) -> dict:
    """计算完整选中字段的范围和直方图，排除非有限值。"""
    import numpy as np

    from ..inspect.hdf5 import is_vtkhdf, read_hdf5_array
    from ..inspect.mesh import read_mesh
    from ..inspect.tensor import read_tensors

    suffix = path.suffix.lower()
    if suffix in {".pt", ".npy", ".zarr"}:
        values = np.asarray(read_tensors(path)[field])
    elif suffix in {".h5", ".hdf5"} and not is_vtkhdf(path):
        values = np.asarray(read_hdf5_array(path, field))
    else:
        from vtk.util.numpy_support import vtk_to_numpy

        association, name = field.split(":", 1)
        mesh = read_mesh(path)
        attrs = mesh.GetPointData() if association == "point" else mesh.GetCellData()
        array = attrs.GetArray(name)
        if array is None:
            raise ValueError("unknown_field")
        values = vtk_to_numpy(array)
    finite = values[np.isfinite(values)]
    counts, edges = np.histogram(finite, bins=max(1, min(256, bins)))
    return {
        "field": field,
        "scope": "complete_field",
        "count": int(values.size),
        "valid": int(finite.size),
        "range": [float(finite.min()), float(finite.max())] if finite.size else None,
        "histogram": {"counts": counts.tolist(), "edges": edges.tolist()},
    }
