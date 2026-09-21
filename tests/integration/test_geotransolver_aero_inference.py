"""普通函数可独立调用索引预测，错误排列必须在预测前失败。"""

import pytest
import torch

from ai4e_core.abilities.inference.indexed_prediction import predict_indexed


def test_permutation_tail_and_cpu_results():
    calls = []

    def operation(ids):
        calls.append(len(ids))
        return ids[:, None].float() * 2

    output, coverage = predict_indexed(
        7, torch.tensor([6, 0, 3, 2, 1, 5, 4]), chunk_size=3, operation=operation
    )
    assert calls == [3, 3, 1]
    assert torch.equal(output[:, 0], torch.arange(7) * 2)
    assert coverage["written"] == 7


@pytest.mark.parametrize("order", [[0, 0, 2], [0, 1], [0, 1, 3]])
def test_bad_order_does_not_call_predictor(order):
    def fail(_):
        raise AssertionError("模型不应被调用")

    with pytest.raises(ValueError, match="重复、遗漏或越界"):
        predict_indexed(3, torch.tensor(order), chunk_size=2, operation=fail)


def test_nonfinite_prediction_is_not_delivered():
    with pytest.raises(ValueError, match="非有限"):
        predict_indexed(
            3,
            torch.arange(3),
            chunk_size=2,
            operation=lambda ids: torch.full((len(ids), 1), float("nan")),
        )


def test_physical_mesh_preserves_noncontiguous_ids_without_raw_source(tmp_path):
    import json
    from types import SimpleNamespace

    import numpy as np
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf
    from ai4e_core.applications.aero_cfd.post.mesh_export import export_prediction_meshes

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    mesh = vtk.vtkUnstructuredGrid()
    vp = vtk.vtkPoints()
    vp.SetData(numpy_to_vtk(points, deep=True))
    mesh.SetPoints(vp)
    ids = vtk.vtkIdList()
    for i in range(3):
        ids.InsertNextId(i)
    mesh.InsertNextCell(vtk.VTK_TRIANGLE, ids)
    for container, name, data in (
        (mesh.GetPointData(), "original_point_id", [40, 7, 90]),
        (mesh.GetCellData(), "original_cell_id", [112]),
    ):
        array = numpy_to_vtk(np.array(data, dtype=np.int64), deep=True)
        array.SetName(name)
        container.AddArray(array)
    source = tmp_path / "source.vtkhdf"
    write_vtkhdf(source, mesh)
    order = [2, 0, 1]
    fields = {
        "xyz": torch.from_numpy(points[order]),
        "ids": torch.tensor([90, 40, 7]),
        "p.prediction": torch.tensor([[9.0], [4.0], [0.7]]),
        "p.truth": torch.zeros(3, 1),
    }
    for name, data in fields.items():
        torch.save(data, tmp_path / (name + ".pt"))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "identity": {"sample": "a"},
                "domains": {
                    "surface": {
                        "position": "xyz",
                        "ids": "ids",
                        "targets": {"p": "p"},
                        "identity_basis": "source",
                    }
                },
                "filemap": {name: name + ".pt" for name in fields},
            }
        )
    )

    def forbidden(*args):
        raise AssertionError("不能读取原始来源")

    export_prediction_meshes(
        {}, SimpleNamespace(comparison_mesh=forbidden), manifest, source_meshes={"surface": source}
    )
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(str(tmp_path / "surface.vtp"))
    reader.Update()
    output = reader.GetOutput()
    np.testing.assert_array_equal(
        vtk_to_numpy(output.GetCellData().GetArray("original_cell_id")), [112]
    )
    actual_ids = vtk_to_numpy(output.GetPointData().GetArray("original_point_id"))
    actual_values = vtk_to_numpy(output.GetPointData().GetArray("p.prediction"))
    assert dict(zip(actual_ids.tolist(), actual_values.tolist(), strict=True)) == {
        90: 9.0,
        40: 4.0,
        7: pytest.approx(0.7),
    }
