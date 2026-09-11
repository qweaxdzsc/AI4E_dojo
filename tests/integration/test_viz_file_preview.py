"""检查器与真实独立读取一致，字段归属和缓存不会混用。"""

from pathlib import Path

import numpy as np
import pytest
import torch
import vtk
from ai4e_viz.inspect.dispatch import inspect_file
from ai4e_viz.runtime.worker import execute
from vtk.util.numpy_support import numpy_to_vtk

pytest_plugins = ["tests.integration.test_web_project_task"]


def _nasa_like(path):
    import h5py

    with h5py.File(path, "w") as source:
        for sample in ("s1", "s2"):
            group = source.create_group(sample)
            group.create_dataset("CoordinateX", data=np.arange(4, dtype="float32"))
            group.create_dataset("PressureCoefficient", data=np.array([2.0, 3.0, 5.0, 7.0]))


def test_hdf5_inspect_and_preview(tmp_path):
    _nasa_like(tmp_path / "trainingData_NASA-CRM.h5")
    info = inspect_file(tmp_path / "trainingData_NASA-CRM.h5")
    assert info["kind"] == "tensor"
    assert {field["name"] for field in info["fields"]} == {"CoordinateX", "PressureCoefficient"}
    assert all(field["shape"] == [4] for field in info["fields"])
    result = execute(
        {
            "path": str(tmp_path / "trainingData_NASA-CRM.h5"),
            "operation": "preview",
            "options": {"field": "PressureCoefficient"},
        }
    )
    assert result["rows"] == [[2.0], [3.0], [5.0], [7.0]]
    flat = tmp_path / "pressure.h5"
    import h5py

    with h5py.File(flat, "w") as source:
        source.create_dataset("pressure", data=np.arange(6, dtype="float32").reshape(2, 3))
    assert inspect_file(flat)["fields"][0]["shape"] == [2, 3]
    empty = tmp_path / "empty.h5"
    with h5py.File(empty, "w"):
        pass
    with pytest.raises(ValueError, match="empty_tensor_store"):
        inspect_file(empty)


def test_real_nasa_h5_field_catalog():
    matches = list(Path("/Users/zonghui/work/datasets/NASA").glob("**/trainingData_NASA-CRM.h5"))
    if not matches:
        pytest.skip("real NASA h5 absent")
    info = inspect_file(matches[0])
    names = {field["name"] for field in info["fields"]}
    assert {"CoordinateX", "PressureCoefficient"} <= names
    assert len(info["fields"]) < 40


def test_tensor_text_mesh(tmp_path):
    a = np.arange(18, dtype="float32").reshape(6, 3)
    np.save(tmp_path / "a.npy", a)
    torch.save({"pressure": torch.tensor(a)}, tmp_path / "a.pt")
    assert inspect_file(tmp_path / "a.pt")["fields"][0]["shape"] == [6, 3]
    result = execute(
        {
            "path": str(tmp_path / "a.pt"),
            "operation": "preview",
            "options": {"field": "pressure", "offset": 2},
        }
    )
    assert result["rows"] == a[2:].tolist()
    (tmp_path / "a.csv").write_text("x,y\n1,2\n3,4\n")
    assert execute({"path": str(tmp_path / "a.csv"), "operation": "preview"})["rows"][0] == [
        "1",
        "2",
    ]
    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    for p in [[0, 0, 0], [1, 0, 0], [0, 1, 0]]:
        points.InsertNextPoint(*p)
    mesh.SetPoints(points)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(3)
    for i in range(3):
        cells.InsertCellPoint(i)
    mesh.SetPolys(cells)
    field = numpy_to_vtk(np.array([2.0, 3.0, 5.0]))
    field.SetName("p")
    mesh.GetPointData().AddArray(field)
    field = numpy_to_vtk(np.array([7.0]))
    field.SetName("p")
    mesh.GetCellData().AddArray(field)
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(mesh)
    writer.SetFileName(str(tmp_path / "mesh.vtp"))
    writer.Write()
    info = inspect_file(tmp_path / "mesh.vtp")
    assert {f["id"] for f in info["fields"]} == {"point:p", "cell:p", "geometry:points"}
    result = execute(
        {
            "path": str(tmp_path / "mesh.vtp"),
            "operation": "preview",
            "options": {"field": "point:p"},
        }
    )
    assert result["indices"] == [0, 1, 2] and result["values"] == [2, 3, 5]
    result = execute(
        {"path": str(tmp_path / "mesh.vtp"), "operation": "preview", "options": {"field": "cell:p"}}
    )
    assert result["values"] == [7, 7, 7]


def test_scope_and_revision_cache(platform, tmp_path):
    c, p, _t, root, _ = platform
    file = root / "hello.txt"
    file.write_text("first")
    url = f"/api/v1/projects/{p}/preview"
    q = {"root": "data0", "path": "hello.txt", "operation": "preview"}
    first = c.get(url, params=q).json()
    assert first["lines"] == ["first"]
    file.write_text("second")
    second = c.get(url, params=q).json()
    assert second["revision"] != first["revision"] and second["lines"] == ["second"]
    for path in ["../secret", str(file), ".hidden"]:
        assert c.get(url, params={**q, "path": path}).status_code == 400
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    (root / "escape.txt").symlink_to(outside)
    assert c.get(url, params={**q, "path": "escape.txt"}).status_code == 400
    listing = c.get(f"/api/v1/projects/{p}/files", params={"root": "data0"}).json()
    assert all(x["name"] != "escape.txt" for x in listing)
