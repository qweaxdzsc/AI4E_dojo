"""显示管线的拓扑、范围、多块、Zarr 与错误边界。"""

import json

import numpy as np
import pytest
import vtk
from ai4e_viz.inspect.dispatch import inspect_file
from ai4e_viz.inspect.mesh import read_mesh
from ai4e_viz.pipeline import execute_pipeline
from ai4e_viz.preview.fields import summarize
from ai4e_viz.preview.tensor import preview_tensor
from ai4e_viz.serialization import write_display
from vtk.util.numpy_support import numpy_to_vtk


def volume():
    grid = vtk.vtkImageData()
    grid.SetDimensions(4, 4, 4)
    coords = np.asarray([grid.GetPoint(i) for i in range(grid.GetNumberOfPoints())])
    a = numpy_to_vtk(coords[:, 0])
    a.SetName("x")
    grid.GetPointData().AddArray(a)
    return grid


def test_contour_plane_matches_analytic_field():
    result, generated = execute_pipeline(
        volume(), [{"type": "contour", "field": "point:x", "value": 1.5}]
    )
    assert generated and result.GetNumberOfCells() > 0
    assert result.GetBounds()[:2] == (1.5, 1.5)


def test_clip_keeps_correct_half():
    result, generated = execute_pipeline(
        volume(), [{"type": "clip", "origin": [1.5, 0, 0], "normal": [1, 0, 0]}]
    )
    assert generated
    assert result.GetBounds()[:2] == (1.5, 3.0)


def test_vector_ranges_and_invalid_mask(tmp_path):
    grid = volume()
    values = np.tile([3.0, 4.0, 0.0], (64, 1))
    values[0] = np.nan
    a = numpy_to_vtk(values)
    a.SetName("velocity")
    grid.GetPointData().AddArray(a)
    manifest = write_display(grid, tmp_path, source={}, pipeline=[])
    f = next(f for f in manifest["fields"] if f["name"] == "velocity")
    assert f["magnitude_range"] == [5.0, 5.0]
    assert f["component_ranges"] == [[3.0, 3.0], [4.0, 4.0], [0.0, 0.0]]
    valid = np.fromfile(tmp_path / f["validity"]["path"], dtype="uint8")
    assert not valid.all()


def test_multiblock_requires_selection(tmp_path):
    multi = vtk.vtkMultiBlockDataSet()
    multi.SetBlock(0, volume())
    multi.SetBlock(1, volume())
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetInputData(multi)
    writer.SetFileName(str(tmp_path / "blocks.vtm"))
    writer.Write()
    info = inspect_file(tmp_path / "blocks.vtm")
    assert len(info["blocks"]) == 2
    assert info["requires_block_selection"]
    with pytest.raises(ValueError, match="block_selection"):
        read_mesh(tmp_path / "blocks.vtm")
    assert read_mesh(tmp_path / "blocks.vtm", 1).GetNumberOfPoints() == 64


def test_zarr_real_slice(tmp_path):
    import zarr

    store = zarr.open_group(str(tmp_path / "arrays.zarr"), mode="w")
    store.create_array("pressure", data=np.arange(24, dtype="float32").reshape(2, 3, 4))
    result = preview_tensor(tmp_path / "arrays.zarr", field="pressure", indices={"2": 2})
    assert result["rows"] == [[2.0, 6.0, 10.0], [14.0, 18.0, 22.0]]
    info = inspect_file(tmp_path / "arrays.zarr")
    assert info["fields"][0]["shape"] == [2, 3, 4]


def test_summary_all_invalid(tmp_path):
    np.save(tmp_path / "invalid.npy", np.array([np.nan, np.inf]))
    result = summarize(tmp_path / "invalid.npy", field="array")
    assert result["valid"] == 0 and result["range"] is None
    json.dumps(result, allow_nan=False)


def test_invalid_plane_rejected():
    with pytest.raises(ValueError, match="normal"):
        execute_pipeline(volume(), [{"type": "slice", "normal": [0, 0, 0]}])


def test_unknown_filter_rejected():
    with pytest.raises(ValueError, match="unsupported_filter"):
        execute_pipeline(volume(), [{"type": "python"}])


def test_explicit_tensor_points_preserves_ids_and_units(tmp_path):
    import torch
    from ai4e_viz.runtime.worker import execute

    path = tmp_path / "difference.pt"
    torch.save(
        {
            "coordinates": torch.tensor([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
            "values": torch.tensor([1.0, float("nan")]),
            "ids": torch.tensor([2**54, 2**54 + 1]),
        },
        path,
    )
    result = execute(
        {
            "protocol_version": 1,
            "request_id": "points",
            "operation": "transform",
            "source": {"path": str(path), "revision": "a"},
            "options": {
                "geometry": {
                    "kind": "tensor_points",
                    "coordinates": "coordinates",
                    "field": "values",
                    "ids": "ids",
                    "association": "point",
                    "unit": "Pa",
                    "entity_set": "sample-1",
                }
            },
            "output_dir": str(tmp_path / "display"),
        }
    )
    assert result["fields"][0]["unit"] == "Pa"
    assert result["fields"][0]["entity_set"] == "sample-1"
    record = result["entity_mapping"]["point"]
    ids = np.fromfile(tmp_path / "display" / record["path"], dtype=record["dtype"])
    np.testing.assert_array_equal(ids, np.array([2**54, 2**54 + 1], dtype="int64"))
    assert [b["name"] for b in result["topology_buffers"]] == ["verts"]


def test_tensor_points_rejects_implicit_geometry(tmp_path):
    from ai4e_viz.pipeline.tensor_points import read_tensor_points

    with pytest.raises(ValueError, match="explicit_point"):
        read_tensor_points(tmp_path / "not_read.pt", {"coordinates": "xyz"})


def test_existing_original_entity_ids_survive_surface(tmp_path):
    grid = volume()
    ids = numpy_to_vtk(np.arange(64, dtype=np.int64) + 2**53, deep=True)
    ids.SetName("original_point_id")
    grid.GetPointData().AddArray(ids)
    result, _ = execute_pipeline(grid, [{"type": "surface"}])
    from vtk.util.numpy_support import vtk_to_numpy

    actual = vtk_to_numpy(result.GetPointData().GetArray("__dojo_original_point"))
    assert actual.min() >= 2**53
    assert np.array_equal(actual, vtk_to_numpy(result.GetPointData().GetArray("original_point_id")))
    ids.SetValue(1, ids.GetValue(0))
    with pytest.raises(ValueError, match="duplicate_original_entity_ids"):
        execute_pipeline(grid, [])


def test_explicit_coordinate_space_from_real_vtk(tmp_path):
    grid = volume()
    for name, value in (("coordinate_space_id", "declared-frame"), ("coordinate_space_unit", "m")):
        array = vtk.vtkStringArray()
        array.SetName(name)
        array.InsertNextValue(value)
        grid.GetFieldData().AddArray(array)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(tmp_path / "declared.vti"))
    writer.SetInputData(grid)
    assert writer.Write()
    source = {"project_id": "p", "asset_id": "a", "revision": "fixed", "block": "0"}
    loaded = read_mesh(tmp_path / "declared.vti")
    filtered, generated = execute_pipeline(loaded, [{"type": "surface"}])
    manifest = write_display(
        filtered, tmp_path / "display", source=source, pipeline=[], generated=generated
    )
    assert manifest["coordinate_space"] == {
        "id": "declared-frame",
        "unit": "m",
        "evidence": "source-declaration",
        "source_refs": [source],
    }
    plain = write_display(volume(), tmp_path / "unknown", source=source, pipeline=[])
    assert "coordinate_space" not in plain
    grid.GetFieldData().RemoveArray("coordinate_space_unit")
    with pytest.raises(ValueError, match="invalid_coordinate_space"):
        write_display(grid, tmp_path / "invalid", source=source, pipeline=[])


def test_trusted_tensor_coordinate_declaration(tmp_path):
    source = {"project_id": "p", "asset_id": "difference", "revision": "fixed"}
    result = write_display(
        volume(),
        tmp_path,
        source=source,
        pipeline=[],
        field_metadata={"unit": "Pa", "coordinate_space": {"id": "declared-frame", "unit": "m"}},
    )
    assert result["coordinate_space"]["unit"] == "m"
    assert result["coordinate_space"]["source_refs"] == [source]
