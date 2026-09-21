"""VTKHDF 与 PT 共享提交、身份回贴和失败恢复验收。"""

import json
from pathlib import Path

import numpy as np
import pytest
import torch
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf
from tests.integration.test_dataset_recipe import execute_case, setup_case


def test_recipe_vtkhdf_mapping(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg.vtkhdf = True
    assert execute_case(folder, cfg) == 0
    manifests = list((tmp_path / "data").glob("*/rawprep/manifest.json"))
    assert len(manifests) == 1
    manifest = json.loads(manifests[0].read_text())
    for record in manifest["samples"]:
        directory = Path(record["path"])
        assert record["meshes"] == {
            "surface": "surface.vtkhdf",
            "volume": "volume.vtkhdf",
        }
        assert set(record["meshes"].values()) <= set(record["assets"])
        mapping = json.loads((directory / "entity_mapping.json").read_text())
        for name, identity in mapping.items():
            reader = vtk.vtkHDFReader()
            reader.SetFileName(str(directory / identity["mesh"]))
            reader.Update()
            mesh = reader.GetOutput()
            attrs = (
                mesh.GetPointData() if identity["association"] == "point" else mesh.GetCellData()
            )
            values = vtk_to_numpy(attrs.GetArray(name))[identity["entity_ids"]]
            tensor = torch.load(directory / record["filemap"][name], weights_only=True)
            np.testing.assert_allclose(values, tensor.numpy())


def test_auxiliary_failure_preserves_old_tensors(tmp_path):
    target = tmp_path / "sample"
    write_named_tensors(target, {"x": torch.ones(2)}, {"x": "x.pt"})

    def fail(path):
        raise OSError("injected")

    with pytest.raises(OSError):
        write_named_tensors(
            target,
            {"x": torch.zeros(2)},
            {"x": "x.pt"},
            overwrite=True,
            extra_writers={"mesh.vtkhdf": fail},
        )
    torch.testing.assert_close(torch.load(target / "x.pt", weights_only=True), torch.ones(2))
    with pytest.raises(TypeError):
        write_vtkhdf(tmp_path / "bad.vtkhdf", vtk.vtkImageData())


@pytest.mark.parametrize("surface", [True, False])
def test_vtkhdf_topology_point_cell_and_original_identity(tmp_path, surface):
    points = vtk.vtkPoints()
    for xyz in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        points.InsertNextPoint(*xyz)
    mesh = vtk.vtkPolyData() if surface else vtk.vtkUnstructuredGrid()
    mesh.SetPoints(points)
    cell = vtk.vtkTriangle() if surface else vtk.vtkTetra()
    for i in range(cell.GetNumberOfPoints()):
        cell.GetPointIds().SetId(i, i)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(cell)
    if surface:
        mesh.SetPolys(cells)
    else:
        mesh.SetCells(vtk.VTK_TETRA, cells)
    records = [
        {"name": "pressure", "association": "point", "entity_ids": [2, 0], "values": [20.0, 10.0]},
        {"name": "cell_field", "association": "cell", "entity_ids": [0], "values": [7.0]},
    ]
    path = write_vtkhdf(tmp_path / "mesh.vtkhdf", mesh, records)
    reader = vtk.vtkHDFReader()
    reader.SetFileName(str(path))
    reader.Update()
    loaded = reader.GetOutput()
    assert loaded.GetNumberOfPoints() == 4 and loaded.GetNumberOfCells() == 1
    assert loaded.GetCellType(0) == mesh.GetCellType(0)
    assert [loaded.GetCell(0).GetPointId(i) for i in range(cell.GetNumberOfPoints())] == list(
        range(cell.GetNumberOfPoints())
    )
    np.testing.assert_array_equal(
        vtk_to_numpy(loaded.GetPointData().GetArray("ai4e_point_id")), np.arange(4)
    )
    np.testing.assert_array_equal(vtk_to_numpy(loaded.GetCellData().GetArray("ai4e_cell_id")), [0])
    np.testing.assert_allclose(
        vtk_to_numpy(loaded.GetPointData().GetArray("pressure")), [10, np.nan, 20, np.nan]
    )
    np.testing.assert_allclose(vtk_to_numpy(loaded.GetCellData().GetArray("cell_field")), [7])
    assert mesh.GetPointData().GetArray("pressure") is None


@pytest.mark.parametrize(
    "ids,association", [([0, 0], "point"), ([0.0], "point"), ([10], "point"), ([0], "unknown")]
)
def test_vtkhdf_rejects_invalid_identity(tmp_path, ids, association):
    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    mesh.SetPoints(points)
    with pytest.raises(ValueError):
        write_vtkhdf(
            tmp_path / "bad.vtkhdf",
            mesh,
            [
                {
                    "name": "x",
                    "association": association,
                    "entity_ids": ids,
                    "values": [1] * len(ids),
                }
            ],
        )
    assert not (tmp_path / "bad.vtkhdf").exists()


def test_vtk_writer_failure_does_not_publish_asset(tmp_path, monkeypatch):
    folder, cfg = setup_case(tmp_path)
    cfg.vtkhdf = True

    class FailedWriter:
        def AddObserver(self, *args):
            pass

        def SetFileName(self, *args):
            pass

        def SetInputData(self, *args):
            pass

        def Write(self):
            return 0

    monkeypatch.setattr(vtk, "vtkHDFWriter", FailedWriter)
    assert execute_case(folder, cfg) == 1
    root = Path(cfg.paths.datasets.root)
    assert not (root / "manifest.json").exists()
    assert not list(root.rglob("*.pt"))
    assert not list(root.rglob("*.vtkhdf"))
