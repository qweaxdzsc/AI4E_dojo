"""解析场切面位置与共享插值、原点映射歧义门禁。"""

import numpy as np
import pytest
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from ai4e_core.abilities.postproc.comparison import attach_valid_mesh, cut_plane, match_points


def test_plane_interpolates_shared_linear_field():
    grid = vtk.vtkImageData()
    grid.SetDimensions(3, 3, 3)
    grid.SetSpacing(1, 1, 1)
    points = np.array([grid.GetPoint(i) for i in range(grid.GetNumberOfPoints())])
    value = points[:, 0] + 2 * points[:, 1]
    # ImageData 使用显式点的结构化网格副本。
    explicit = vtk.vtkStructuredGrid()
    explicit.SetDimensions(3, 3, 3)
    pts = vtk.vtkPoints()
    for point in points:
        pts.InsertNextPoint(point)
    explicit.SetPoints(pts)
    mesh = attach_valid_mesh(explicit, points, {"truth": value, "prediction": value + 1})
    cut, metadata = cut_plane(mesh, axis=1, fraction=0.5)
    coords = vtk_to_numpy(cut.GetPoints().GetData())
    actual = vtk_to_numpy(cut.GetPointData().GetArray("truth"))
    predicted = vtk_to_numpy(cut.GetPointData().GetArray("prediction"))
    np.testing.assert_allclose(coords[:, 1], 1)
    np.testing.assert_allclose(actual, coords[:, 0] + 2)
    np.testing.assert_allclose(predicted - actual, 1)
    assert metadata["invalid_region"] == "excluded"


def test_duplicate_source_coordinates_require_explicit_ids():
    with pytest.raises(ValueError, match="歧义"):
        match_points(np.zeros((1, 3)), np.zeros((2, 3)))


def test_render_failure_does_not_leave_success_report(tmp_path, monkeypatch):
    import json

    from ai4e_viz.compose import comparison

    report = {
        "status": "succeeded",
        "domain": "surface",
        "models": ["a", "b"],
        "metrics": {},
        "visuals": [{"sample": "s", "kind": "surface", "fields": ["p"]}],
    }
    path = tmp_path / "comparison.json"
    path.write_text(json.dumps(report))
    out = tmp_path / "output"
    out.mkdir()
    (out / "index.html").write_text("old complete report")

    def fail(*args):
        raise OSError("injected render failure")

    monkeypatch.setattr(comparison, "render", fail)
    with pytest.raises(OSError, match="injected"):
        comparison.compose([path], out, title="test")
    assert json.loads((out / "render-progress.json").read_text())["status"] == "failed"
    assert "Report incomplete" in (out / "index.html").read_text()


def test_report_does_not_assume_one_epoch(tmp_path, monkeypatch):
    """更换训练预算后报告不误标单轮，仍以源运行记录为依据。"""
    import json

    from ai4e_viz.compose import comparison

    report = {
        "status": "succeeded",
        "domain": "surface",
        "models": ["a", "b"],
        "metrics": {},
        "visuals": [{"sample": "s", "kind": "surface", "fields": ["p"]}],
    }
    path = tmp_path / "comparison.json"
    path.write_text(json.dumps(report))
    monkeypatch.setattr(comparison, "render", lambda *args: {"path": str(args[-1])})
    output = comparison.compose([path], tmp_path / "report", title="50 epoch experiment")
    text = output.read_text()
    assert "One epoch" not in text
    assert "source run artifacts" in text
    assert "50 epoch experiment" in text
    assert json.loads((output.parent / "render-progress.json").read_text())["status"] == "succeeded"
