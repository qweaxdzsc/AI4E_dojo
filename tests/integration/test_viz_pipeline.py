"""真实 VTK 过滤与二进制显示资产交接。"""

import json

import numpy as np
import vtk
from ai4e_viz.pipeline import execute_pipeline
from ai4e_viz.serialization import write_display
from vtk.util.numpy_support import numpy_to_vtk


def test_slice_binary(tmp_path):
    grid = vtk.vtkImageData()
    grid.SetDimensions(4, 4, 4)
    values = numpy_to_vtk(np.arange(64, dtype=float))
    values.SetName("pressure")
    grid.GetPointData().AddArray(values)
    result, generated = execute_pipeline(
        grid, [{"type": "slice", "origin": [1, 0, 0], "normal": [1, 0, 0]}]
    )
    assert result.GetNumberOfPoints() > 0
    manifest = write_display(
        result, tmp_path, source={"revision": "1"}, pipeline=[], generated=generated
    )
    assert manifest["entity_mapping"]["generated_entities"]
    for buffer in manifest["geometry_buffers"] + manifest["topology_buffers"]:
        assert (tmp_path / buffer["path"]).stat().st_size == buffer["byte_length"]
    assert json.loads((tmp_path / "manifest.json").read_text())["fields"][0]["name"] == "pressure"


def test_contour_rejects_cell():
    import pytest

    grid = vtk.vtkImageData()
    grid.SetDimensions(3, 3, 3)
    a = numpy_to_vtk(np.arange(8, dtype=float))
    a.SetName("p")
    grid.GetCellData().AddArray(a)
    with pytest.raises(ValueError, match="point_scalar"):
        execute_pipeline(grid, [{"type": "contour", "field": "cell:p", "value": 2}])


def test_threshold_preserves_source_identity(tmp_path):
    from vtk.util.numpy_support import vtk_to_numpy

    grid = vtk.vtkImageData()
    grid.SetDimensions(4, 4, 4)
    a = numpy_to_vtk(np.arange(27, dtype=float))
    a.SetName("index")
    grid.GetCellData().AddArray(a)
    result, generated = execute_pipeline(
        grid, [{"type": "threshold", "field": "cell:index", "lower": 10, "upper": 15}]
    )
    assert not generated
    ids = vtk_to_numpy(result.GetCellData().GetArray("__dojo_original_cell"))
    np.testing.assert_array_equal(ids, np.arange(10, 16))
    manifest = write_display(result, tmp_path, source={}, pipeline=[])
    record = manifest["entity_mapping"]["cell"]
    restored = np.fromfile(tmp_path / record["path"], dtype=record["dtype"])
    assert set(restored) <= set(range(10, 16))


def test_tensor_slice_large_integer(tmp_path):
    from ai4e_viz.preview.tensor import preview_tensor

    array = np.arange(24, dtype=np.int64).reshape(2, 3, 4) + 2**54
    path = tmp_path / "values.npy"
    np.save(path, array)
    result = preview_tensor(path, axes=[2, 0], indices={"1": 1})
    assert result["shape"] == [2, 3, 4]
    assert result["rows"][0][0] == str(array[0, 1, 0])
    assert len(result["rows"]) == 4


def test_worker_modern_and_legacy(tmp_path):
    import subprocess
    import sys

    path = tmp_path / "x.npy"
    np.save(path, np.arange(6))
    request = {
        "protocol_version": 1,
        "request_id": "test",
        "operation": "read_slice",
        "source": {"path": str(path), "revision": "1"},
        "options": {},
        "output_dir": str(tmp_path / "out"),
    }
    completed = subprocess.run(
        [sys.executable, "-m", "ai4e_viz"],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True,
    )
    events = [json.loads(line) for line in completed.stdout.splitlines()]
    assert events[0]["type"] == "progress"
    assert events[-1]["type"] == "result"
    assert events[-1]["result"]["rows"][0] == [0]
