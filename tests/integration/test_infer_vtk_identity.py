"""推理 VTK 默认写出预测与真值，并带稳定 sample_id。"""

import json

import torch
from vtk.util.numpy_support import vtk_to_numpy

from ai4e_core.applications.aero_cfd.infer.vtk_export import (
    VTK_DISABLED,
    skip_vtk,
    write_anchor_prediction_vtk,
)


def _manifest(dest, *, sample="param1/abc"):
    dest.mkdir(parents=True, exist_ok=True)
    n = 4
    torch.save(torch.zeros(n, 3), dest / "surface.position.pt")
    torch.save(torch.ones(n, 1), dest / "surface.pressure.prediction.pt")
    torch.save(torch.full((n, 1), 2.0), dest / "surface.pressure.truth.pt")
    path = dest / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "identity": {"sample": sample, "split": "test"},
                "domains": {
                    "surface": {
                        "position": "surface.position",
                        "ids": "surface.ids",
                        "targets": {"pressure": "surface.pressure"},
                    }
                },
                "filemap": {
                    "surface.position": "surface.position.pt",
                    "surface.pressure.prediction": "surface.pressure.prediction.pt",
                    "surface.pressure.truth": "surface.pressure.truth.pt",
                },
            }
        )
    )
    return path


def test_anchor_vtk_writes_truth_and_sample_id(tmp_path):
    import vtk

    path = _manifest(tmp_path / "param1" / "abc")
    written = write_anchor_prediction_vtk(path)
    assert written["surface"]["fields"] == [
        "surface.pressure.prediction",
        "surface.pressure.truth",
    ]
    mesh = path.parent / "surface.vtp"
    assert mesh.is_file()
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(str(mesh))
    reader.Update()
    output = reader.GetOutput()
    names = [
        output.GetPointData().GetArrayName(i)
        for i in range(output.GetPointData().GetNumberOfArrays())
    ]
    assert "surface.pressure.prediction" in names
    assert "surface.pressure.truth" in names
    assert vtk_to_numpy(output.GetPointData().GetArray("surface.pressure.prediction")).tolist() != vtk_to_numpy(
        output.GetPointData().GetArray("surface.pressure.truth")
    ).tolist()
    field = {
        output.GetFieldData().GetArrayName(i): output.GetFieldData().GetAbstractArray(i).GetValue(0)
        for i in range(output.GetFieldData().GetNumberOfArrays())
    }
    assert field["sample_id"] == "param1/abc"
    assert field["source_sample_id"] == "param1/abc"
    record = json.loads(path.read_text())
    assert record["vtk"]["exported"] is True
    assert record["vtk"]["sample_id"] == "param1/abc"


def test_skip_vtk_records_reason(tmp_path):
    path = _manifest(tmp_path / "param1" / "xyz")
    status = skip_vtk(path, VTK_DISABLED)
    assert status["exported"] is False
    assert status["reason"] == VTK_DISABLED
    assert json.loads(path.read_text())["vtk"]["reason"] == VTK_DISABLED
    assert not (path.parent / "surface.vtp").exists()
