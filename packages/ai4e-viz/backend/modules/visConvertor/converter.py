"""把VTK可读几何格式转换为浏览器O3DV可加载的GLB表现。"""

from __future__ import annotations

import os


def _reader(source_path: str):
    import vtk

    ext = os.path.splitext(source_path)[1].lower()
    readers = {
        ".vtu": vtk.vtkXMLUnstructuredGridReader,
        ".vts": vtk.vtkXMLStructuredGridReader,
        ".vtm": vtk.vtkXMLMultiBlockDataReader,
        ".vtp": vtk.vtkXMLPolyDataReader,
        ".stl": vtk.vtkSTLReader,
        ".ply": vtk.vtkPLYReader,
        ".obj": vtk.vtkOBJReader,
    }
    cls = readers.get(ext)
    if cls is None:
        raise ValueError(f"unsupported GEO source format: {ext}")
    reader = cls()
    reader.SetFileName(source_path)
    reader.Update()
    return reader.GetOutputDataObject(0)


def _datasets(data_object):
    import vtk

    if isinstance(data_object, vtk.vtkDataSet):
        yield data_object
        return
    if isinstance(data_object, vtk.vtkCompositeDataSet):
        iterator = data_object.NewIterator()
        iterator.VisitOnlyLeavesOn()
        iterator.SkipEmptyNodesOn()
        iterator.InitTraversal()
        while not iterator.IsDoneWithTraversal():
            current = iterator.GetCurrentDataObject()
            if isinstance(current, vtk.vtkDataSet):
                yield current
            iterator.GoToNextItem()


def _surface_mesh(dataset):
    import numpy as np
    import trimesh
    import vtk
    from vtk.util import numpy_support

    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(dataset)
    surface.Update()
    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputConnection(surface.GetOutputPort())
    triangles.Update()
    poly = triangles.GetOutput()
    if poly.GetNumberOfPoints() == 0 or poly.GetNumberOfCells() == 0:
        return None

    vertices = numpy_support.vtk_to_numpy(poly.GetPoints().GetData()).astype(np.float64)
    faces = []
    for cell_index in range(poly.GetNumberOfCells()):
        cell = poly.GetCell(cell_index)
        point_ids = [cell.GetPointId(index) for index in range(cell.GetNumberOfPoints())]
        if len(point_ids) == 3:
            faces.append(point_ids)
        elif len(point_ids) > 3:
            for index in range(1, len(point_ids) - 1):
                faces.append([point_ids[0], point_ids[index], point_ids[index + 1]])
    if not faces:
        return None
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces, dtype=np.int64), process=False)


def convert_to_glb(source_path: str, output_path: str) -> str:
    """写出确定性的GLB表面表现并返回输出路径。"""
    import trimesh

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    source_mtime = os.path.getmtime(source_path)
    if os.path.exists(output_path) and os.path.getmtime(output_path) >= source_mtime:
        return output_path

    scene = trimesh.Scene()
    for index, dataset in enumerate(_datasets(_reader(source_path))):
        mesh = _surface_mesh(dataset)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=f"mesh-{index + 1}")
    if not scene.geometry:
        raise ValueError("no renderable surface geometry found")
    payload = scene.export(file_type="glb")
    with open(output_path, "wb") as handle:
        handle.write(payload)
    return output_path
