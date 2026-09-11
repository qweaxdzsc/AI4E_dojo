"""显式声明的张量几何关联，不从成员名称猜测点云。"""

from pathlib import Path


def read_tensor_points(path: Path, declaration: dict):
    """按受信描述读取坐标、点场和身份；不创建拓扑或插值。"""
    import numpy as np
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk

    from ..inspect.tensor import read_tensors

    if declaration.get("kind") != "tensor_points" or declaration.get("association") != "point":
        raise ValueError("tensor_geometry_requires_explicit_point_declaration")
    arrays = read_tensors(path)
    coordinates = np.asarray(arrays[declaration["coordinates"]])
    values = np.asarray(arrays[declaration["field"]])
    ids = np.asarray(arrays[declaration["ids"]])
    if coordinates.ndim != 2 or coordinates.shape[1] != 3 or not np.isfinite(coordinates).all():
        raise ValueError("invalid_tensor_coordinates")
    if values.ndim not in (1, 2) or len(values) != len(coordinates):
        raise ValueError("tensor_field_entity_count_mismatch")
    if (
        ids.ndim != 1
        or len(ids) != len(coordinates)
        or ids.dtype.kind not in "iu"
        or len(np.unique(ids)) != len(ids)
    ):
        raise ValueError("invalid_tensor_entity_identity")
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(coordinates, deep=True))
    mesh = vtk.vtkPolyData()
    mesh.SetPoints(points)
    field = numpy_to_vtk(values, deep=True)
    field.SetName(declaration["field"])
    mesh.GetPointData().AddArray(field)
    identity = numpy_to_vtk(ids, deep=True)
    identity.SetName("__dojo_original_point")
    mesh.GetPointData().AddArray(identity)
    return mesh
