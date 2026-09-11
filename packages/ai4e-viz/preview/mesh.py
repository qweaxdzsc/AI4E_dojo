"""真实表面三角形和点云预览；单元场通过独立面顶点保持平涂。"""

from pathlib import Path

from ..inspect.mesh import read_mesh


def preview_mesh(path: Path, field: str | None = None, **_) -> dict:
    """转换基础网格；点场与单元场保持不同实体归属，不做插值。"""
    import numpy as np
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    mesh = read_mesh(path)
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(mesh)
    surface.Update()
    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputConnection(surface.GetOutputPort())
    triangles.Update()
    poly = triangles.GetOutput()
    if poly.GetNumberOfPoints() > 250000:
        raise ValueError("preview_too_large: 250000 points limit")
    if not poly.GetPoints():
        raise ValueError("empty_or_invalid_mesh")
    positions = vtk_to_numpy(poly.GetPoints().GetData())
    faces = [
        (i, [poly.GetCell(i).GetPointId(j) for j in range(3)])
        for i in range(poly.GetNumberOfCells())
        if poly.GetCell(i).GetCellType() == vtk.VTK_TRIANGLE
    ]
    values = None
    if field:
        association, name = field.split(":", 1) if ":" in field else ("point", field)
        if association not in {"point", "cell"}:
            raise ValueError("preview_field_association")
        attrs = poly.GetPointData() if association == "point" else poly.GetCellData()
        array = attrs.GetArray(name)
        if array is None:
            raise ValueError("preview_field_missing")
        values = vtk_to_numpy(array)
        if values.ndim == 2:
            values = np.linalg.norm(values, axis=1)
        if association == "cell":
            if not faces:
                raise ValueError("cell_preview_requires_surface")
            if len(faces) * 3 > 750000:
                raise ValueError("preview_too_large")
            positions = np.array([positions[j] for _, ids in faces for j in ids])
            values = np.array([values[i] for i, _ in faces for _ in range(3)])
            faces = [(i, [i * 3, i * 3 + 1, i * 3 + 2]) for i in range(len(faces))]
    result = {
        "kind": "mesh",
        "positions": positions.ravel().tolist(),
        "indices": [j for _, ids in faces for j in ids],
        "field": field,
        "color_mode": "vector_magnitude_or_scalar",
        "fields": [
            f"{a}:{d.GetArrayName(i)}"
            for a, d in [("point", poly.GetPointData()), ("cell", poly.GetCellData())]
            for i in range(d.GetNumberOfArrays())
        ],
    }
    if values is not None:
        result["values"] = [float(v) if np.isfinite(v) else None for v in values]
    return result
