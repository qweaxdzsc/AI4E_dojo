"""真实时间缺帧、拓扑变化和时序提取验收。"""

from pathlib import Path
import vtk
import pytest
from modules.dataAssets import source_fingerprint
from modules.visPhysField import default_spec
from modules.visPhysField.scene import Scene


def test_exact_time_and_changed_topology(tmp_path):
    frames = []
    for index, size in enumerate((3, 5)):
        path = tmp_path / f"{index}.vti"
        grid = vtk.vtkImageData()
        grid.SetDimensions(size, size, size)
        array = vtk.vtkDoubleArray()
        array.SetName("temperature")
        for _ in range(size**3):
            array.InsertNextValue(index + 10)
        grid.GetPointData().AddArray(array)
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetInputData(grid)
        writer.SetFileName(str(path))
        writer.Write()
        frames.append(
            {"time": float(index), "path": str(path), "revision": source_fingerprint(path)}
        )
    ref = {"asset_id": "series", "revision": frames[0]["revision"]}
    bindings = [{"ref": ref, "path": frames[0]["path"], "frames": frames}]
    scene = Scene(bindings, default_spec([{"id": "s", "ref": ref}]))
    try:
        assert scene.datasets["s"].GetNumberOfPoints() == 27
        first = scene.datasets["s"]
        scene.command({"operation": "apply", "spec": scene.snapshot()["spec"]})
        assert scene.datasets["s"] is first
        scene.command({"operation": "time", "value": 1})
        assert scene.datasets["s"].GetNumberOfPoints() == 125
        result = scene.command(
            {"operation": "temporal", "input": "s", "positions": [[0.5, 0.5, 0.5]]}
        )
        assert [r["values"]["temperature"][0] for r in result["rows"]] == [10.0, 11.0]
        derived = scene.command(
            {"operation": "temporal", "input": "base-s", "positions": [[0.5, 0.5, 0.5]]}
        )
        assert [r["values"]["temperature"][0] for r in derived["rows"]] == [10.0, 11.0]
        assert scene.snapshot()["extraction"]["operation"] == "temporal"
        assert scene.snapshot()["spec"]["time"]["value"] == 1
        missing = scene.command({"operation": "time", "value": 0.5})
        assert missing["missing"] == ["s", "base-s"]
        assert missing["times"] == [0.0, 1.0]
    finally:
        scene.close()
