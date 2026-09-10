"""完整表面场导出；字段名由业务装配显式提供。"""

import numpy as np

from ai4e_core.abilities.data.save.arrays import atomic_path
from ai4e_core.abilities.postproc.surface_geometry import orient_topology, surface_area_ratio


def write_h5(path, *, arrays, attributes, field_names):
    """保存可审计 HDF5 数组、属性与字段顺序。"""
    import h5py

    with atomic_path(path) as temporary, h5py.File(temporary, "w") as output:
        for key, value in attributes.items():
            output.attrs[key] = value
        for key, value in arrays.items():
            output.create_dataset(
                key, data=value, compression=None if key == "conditions" else "gzip"
            )
        for key, names in field_names.items():
            output[key].attrs["fields"] = np.asarray(names, dtype="S")


def write_vtp(
    path,
    *,
    topology,
    points,
    normals,
    area,
    conditions,
    truth,
    prediction,
    labels,
    condition_names,
    vector_name="cf",
    vector_indices=(1, 2, 3),
):
    """写真实混合面单元；使用 VTK 原生对象，不增加第二套网格运行时。"""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

    oriented = orient_topology(topology, points, normals)
    triangles = np.column_stack(
        (np.full(len(oriented.triangles), 3, dtype=np.int64), oriented.triangles)
    ).ravel()
    quads = np.column_stack(
        (np.full(len(oriented.quads), 4, dtype=np.int64), oriented.quads)
    ).ravel()
    mesh = vtk.vtkPolyData()
    coords = vtk.vtkPoints()
    coords.SetData(numpy_to_vtk(np.ascontiguousarray(points, dtype=np.float32), deep=True))
    mesh.SetPoints(coords)
    cells = vtk.vtkCellArray()
    cells.SetCells(
        oriented.face_count, numpy_to_vtkIdTypeArray(np.concatenate((triangles, quads)), deep=True)
    )
    mesh.SetPolys(cells)

    def add(target, name, values):
        array = numpy_to_vtk(np.ascontiguousarray(values), deep=True)
        array.SetName(name)
        target.AddArray(array)

    add(mesh.GetPointData(), "surface_normal", normals.astype(np.float32, copy=False))
    add(mesh.GetPointData(), "surface_area", area.astype(np.float32, copy=False))
    for index, name in enumerate(labels):
        for suffix, values in (
            ("truth", truth),
            ("prediction", prediction),
            ("error", prediction - truth),
        ):
            add(mesh.GetPointData(), f"{name}_{suffix}", values[:, index])
    vector_indices = list(vector_indices)
    for suffix, values in (
        ("truth", truth),
        ("prediction", prediction),
        ("error", prediction - truth),
    ):
        add(mesh.GetPointData(), f"{vector_name}_{suffix}", values[:, vector_indices])
    actual = np.linalg.norm(truth[:, vector_indices], axis=1)
    predicted = np.linalg.norm(prediction[:, vector_indices], axis=1)
    for suffix, values in (
        ("truth", actual),
        ("prediction", predicted),
        ("error", predicted - actual),
    ):
        add(mesh.GetPointData(), f"{vector_name}_magnitude_{suffix}", values)
    for index, name in enumerate(condition_names):
        add(mesh.GetFieldData(), name, np.asarray([conditions[index]], dtype=np.float32))
    add(
        mesh.GetFieldData(),
        "topology_euler_characteristic",
        np.asarray([oriented.euler_characteristic], dtype=np.int32),
    )
    add(
        mesh.GetFieldData(),
        "reconstructed_to_nodal_area_ratio",
        np.asarray([surface_area_ratio(oriented, points, area)], dtype=np.float64),
    )
    with atomic_path(path) as temporary:
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(str(temporary))
        writer.SetInputData(mesh)
        writer.SetDataModeToBinary()
        if writer.Write() != 1:
            raise OSError(f"VTP 写入失败: {path}")
