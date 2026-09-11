"""预测导出保留真实单元、字段与原始点/单元身份。"""

import json
from types import SimpleNamespace

import numpy as np
import pytest
import torch
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

from ai4e_core.abilities.postproc.comparison import attach_valid_mesh
from ai4e_core.applications.aero_cfd.post.mesh_export import export_prediction_meshes


@pytest.mark.parametrize("domain,cell_type", [("surface", vtk.VTK_QUAD), ("volume", vtk.VTK_TETRA)])
def test_real_topology_and_prediction_export(tmp_path, domain, cell_type):
    points = np.array(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 1 if domain == "volume" else 0]], dtype=np.float32
    )
    mesh = vtk.vtkUnstructuredGrid()
    vp = vtk.vtkPoints()
    vp.SetData(numpy_to_vtk(points, deep=True))
    mesh.SetPoints(vp)
    conn = vtk.vtkIdList()
    for i in range(4):
        conn.InsertNextId(i)
    mesh.InsertNextCell(cell_type, conn)
    key = f"{domain}.pressure"
    values = np.arange(4, dtype=np.float32)[:, None]
    tensors = {
        "position": points,
        "ids": np.arange(4),
        key + ".prediction": values,
        key + ".truth": values + 1,
    }
    filemap = {k: f"{i}.pt" for i, k in enumerate(tensors)}
    for k, v in tensors.items():
        torch.save(torch.from_numpy(v), tmp_path / filemap[k])
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "identity": {"sample": "real"},
                "filemap": filemap,
                "domains": {
                    domain: {
                        "coordinate_space": {"id": "fixture-frame", "unit": "m"},
                        "position": "position",
                        "ids": "ids",
                        "targets": {"pressure": key},
                        "identity_basis": "source",
                        "units": {"pressure": "Pa"},
                    }
                },
            }
        )
    )
    result = export_prediction_meshes(
        {}, SimpleNamespace(comparison_mesh=lambda *args: mesh), manifest
    )
    reader = (
        vtk.vtkXMLPolyDataReader() if domain == "surface" else vtk.vtkXMLUnstructuredGridReader()
    )
    reader.SetFileName(str(tmp_path / result[domain]["path"]))
    reader.Update()
    out = reader.GetOutput()
    assert out.GetNumberOfCells() == 1 and out.GetCellType(0) == cell_type
    assert out.GetFieldData().GetAbstractArray("coordinate_space_id").GetValue(0) == "fixture-frame"
    assert out.GetFieldData().GetAbstractArray("coordinate_space_unit").GetValue(0) == "m"
    assert result[domain]["coordinate_space"] == {"id": "fixture-frame", "unit": "m"}
    ids = vtk_to_numpy(out.GetPointData().GetArray("original_point_id"))
    np.testing.assert_array_equal(vtk_to_numpy(out.GetPoints().GetData()), points[ids])
    np.testing.assert_array_equal(
        vtk_to_numpy(out.GetPointData().GetArray(key + ".prediction")).reshape(-1, 1), values[ids]
    )
    assert vtk_to_numpy(out.GetCellData().GetArray("original_cell_id")).tolist() == [0]
    with pytest.raises(ValueError, match="唯一"):
        attach_valid_mesh(mesh, points, {}, source_ids=np.zeros(4, dtype=np.int64))
    with pytest.raises(ValueError, match="没有"):
        attach_valid_mesh(mesh, points[:3], {}, source_ids=np.arange(3))
