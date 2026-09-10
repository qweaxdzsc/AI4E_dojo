"""字段提取与有效点 mask：VTK 内存对象抽场、认单元、装配串联。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.util.vtkConstants import VTK_HEXAHEDRON, VTK_QUAD, VTK_TRIANGLE
from vtkmodules.vtkCommonCore import vtkDoubleArray, vtkFloatArray, vtkPoints, vtkStringArray
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkUnstructuredGrid

from ai4e_core.abilities.data.filter import used_vertex_mask
from ai4e_core.abilities.data.extract import (
    extract_coordinates,
    extract_field,
    extract_scalars,
    extract_vectors,
)
from ai4e_core.abilities.data.source.read import read_file
from ai4e_core.applications.aero_cfd.rawprep import extract_configured_sample
from ai4e_core.base.config import load_config
from tests.recipe_assets import CONFIG_PATH
from tests.support import SHAPENET_SAMPLES


def _with_scalars(grid: vtkUnstructuredGrid, values: list[float]) -> None:
    """写入活动点标量。"""
    scalars = vtkDoubleArray()
    scalars.SetName("pressure")
    for value in values:
        scalars.InsertNextValue(value)
    grid.GetPointData().SetScalars(scalars)


def _with_vectors(grid: vtkUnstructuredGrid, values: list[tuple[float, float, float]]) -> None:
    """写入活动点矢量。"""
    vectors = vtkFloatArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for value in values:
        vectors.InsertNextTuple(value)
    grid.GetPointData().SetVectors(vectors)


def _surface_quad_with_unused_point() -> vtkUnstructuredGrid:
    """四个点组成一个 quad，第五个点不参与单元。"""
    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    for point in (
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (2.0, 2.0, 0.0),
    ):
        points.InsertNextPoint(point)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_QUAD, 4, [0, 1, 2, 3])
    _with_scalars(grid, [1.0, 2.0, 3.0, 4.0, 99.0])
    return grid


def _volume_hex() -> vtkUnstructuredGrid:
    """一个六面体，八点带速度。"""
    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    for point in (
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 1.0),
        (0.0, 1.0, 1.0),
    ):
        points.InsertNextPoint(point)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_HEXAHEDRON, 8, list(range(8)))
    _with_vectors(
        grid,
        [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 1.0, 0.0),
            (1.0, 0.0, 1.0),
            (0.0, 1.0, 1.0),
            (1.0, 1.0, 1.0),
            (0.5, 0.5, 0.5),
        ],
    )
    return grid


def test_extract_surface_scalars_and_coordinates() -> None:
    grid = _surface_quad_with_unused_point()
    points = extract_coordinates(grid)
    scalars = extract_scalars(grid, name="pressure", association="point")

    assert points.shape == (5, 3)
    assert scalars.shape == (5,)
    assert scalars.tolist() == [1.0, 2.0, 3.0, 4.0, 99.0]


def test_extract_volume_vectors_and_coordinates() -> None:
    grid = _volume_hex()
    points = extract_coordinates(grid)
    vectors = extract_vectors(grid, name="velocity", association="point")

    assert points.shape == (8, 3)
    assert vectors.shape == (8, 3)


def test_extract_fails_without_points_or_field() -> None:
    empty = vtkDataObject()
    with pytest.raises(TypeError, match="带点的 VTK 数据集"):
        extract_coordinates(empty)

    grid = _surface_quad_with_unused_point()
    grid.GetPointData().SetScalars(None)
    with pytest.raises(ValueError, match="字段不存在"):
        extract_scalars(grid, name="pressure", association="point")


def test_used_vertex_mask_marks_unused_and_rejects_wrong_type() -> None:
    grid = _surface_quad_with_unused_point()
    mask = used_vertex_mask(grid, cell_type="quad")

    assert mask.dtype == bool
    assert mask.tolist() == [True, True, True, True, False]
    assert extract_scalars(grid, name="pressure", association="point").shape[0] == 5

    triangle = vtkUnstructuredGrid()
    points = vtkPoints()
    for point in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        points.InsertNextPoint(point)
    triangle.SetPoints(points)
    triangle.InsertNextCell(VTK_TRIANGLE, 3, [0, 1, 2])
    with pytest.raises(ValueError, match="单元类型不符"):
        used_vertex_mask(triangle, cell_type="quad")


def test_extract_configured_sample_wires_read_extract_clean(tmp_path: Path) -> None:
    from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter

    sample = tmp_path / "param0" / "design_a"
    sample.mkdir(parents=True)
    surface_path = sample / "quadpress_smpl.vtk"
    volume_path = sample / "hexvelo_smpl.vtk"
    writer = vtkUnstructuredGridWriter()
    writer.SetFileName(str(surface_path))
    writer.SetInputData(_surface_quad_with_unused_point())
    writer.Write()
    writer.SetFileName(str(volume_path))
    writer.SetInputData(_volume_hex())
    writer.Write()

    config = load_config(CONFIG_PATH)
    config["dataset"]["root"] = str(tmp_path)
    config["pre"]["surface"]["fields"]["pressure"]["array"] = "pressure"
    config["pre"]["volume"]["fields"]["velocity"]["array"] = "velocity"
    result = extract_configured_sample(config, sample_relative=Path("param0/design_a"))

    assert result["surface"]["points"].shape == (5, 3)
    assert result["surface"]["fields"]["pressure"].shape == (5,)
    assert result["surface"]["mask"].tolist() == [True, True, True, True, False]
    assert result["volume"]["points"].shape == (8, 3)
    assert result["volume"]["fields"]["velocity"].shape == (8, 3)
    assert "mask" not in result["volume"]


@pytest.mark.local_data
@pytest.mark.parametrize("sample_relative", SHAPENET_SAMPLES)
def test_extract_configured_real_shapenet_sample(shapenet_raw: Path, sample_relative: Path) -> None:
    sample = shapenet_raw / sample_relative
    if not (sample / "quadpress_smpl.vtk").is_file():
        pytest.skip(f"样本目录不存在: {sample}")

    config = load_config(CONFIG_PATH)
    config["dataset"]["root"] = str(shapenet_raw)
    result = extract_configured_sample(config, sample_relative=sample_relative)

    n_surface = result["surface"]["points"].shape[0]
    assert result["surface"]["points"].shape[1] == 3
    assert result["surface"]["fields"]["pressure"].shape[0] == n_surface
    assert result["surface"]["mask"].shape == (n_surface,)
    assert result["surface"]["mask"].dtype == bool
    assert bool(result["surface"]["mask"].any())
    assert result["volume"]["points"].shape[1] == 3
    assert result["volume"]["fields"]["velocity"].shape[0] == result["volume"]["points"].shape[0]

    loaded = read_file(sample / "quadpress_smpl.vtk")
    np.testing.assert_array_equal(
        result["surface"]["mask"], used_vertex_mask(loaded, cell_type="quad")
    )
    for role, filename, physical, array_name in (
        ("surface", "quadpress_smpl.vtk", "pressure", "point_scalars"),
        ("volume", "hexvelo_smpl.vtk", "velocity", "point_vectors"),
    ):
        original = read_file(sample / filename)
        np.testing.assert_array_equal(
            result[role]["points"], vtk_to_numpy(original.GetPoints().GetData())
        )
        np.testing.assert_array_equal(
            result[role]["fields"][physical],
            vtk_to_numpy(original.GetPointData().GetArray(array_name)),
        )
        assert result[role]["vtk"].GetNumberOfCells() == original.GetNumberOfCells()


def _add_field(grid, values, *, name="pressure", association="point") -> None:
    """测试夹具添加具名数值数组，不改变活动字段。"""
    array = numpy_to_vtk(np.asarray(values), deep=True)
    array.SetName(name)
    attrs = grid.GetPointData() if association == "point" else grid.GetCellData()
    attrs.AddArray(array)


def _shared_config() -> dict:
    """两个域引用同一源，表面同时声明点压力和单元压力。"""
    return {
        "dataset": {"root": "/unused"},
        "source": {"files": [{"name": "mesh", "filename": "mesh.vtu", "format": "vtk"}]},
        "pre": {
            "surface": {
                "source": "mesh",
                "cell_type": "quad",
                "fields": {
                    "pressure": {"array": "pressure", "association": "point", "kind": "scalar"},
                    "cell_pressure": {"array": "pressure", "association": "cell", "kind": "scalar"},
                },
            },
            "volume": {
                "source": "mesh",
                "fields": {
                    "pressure": {"array": "pressure", "association": "point", "kind": "scalar"}
                },
            },
        },
    }


def test_named_fields_ignore_active_and_respect_association() -> None:
    """同名点/单元场正确分离，活动场切换不影响具名选择。"""
    grid = _surface_quad_with_unused_point()
    _add_field(grid, [300.0] * 5, name="temperature")
    _add_field(grid, [7.0], association="cell")
    _add_field(grid, [[1.0, 2.0, 3.0]], name="velocity", association="cell")
    grid.GetPointData().SetActiveScalars("temperature")
    np.testing.assert_array_equal(
        extract_scalars(grid, name="pressure", association="point"), [1, 2, 3, 4, 99]
    )
    np.testing.assert_array_equal(extract_scalars(grid, name="pressure", association="cell"), [7])
    np.testing.assert_array_equal(
        extract_vectors(grid, name="velocity", association="cell"), [[1, 2, 3]]
    )
    assert grid.GetPointData().GetScalars().GetName() == "temperature"


@pytest.mark.parametrize(
    "association,values,kind,error",
    [
        ("point", [1.0, 2.0], "scalar", "数量不对齐"),
        ("cell", [1.0, 2.0], "scalar", "数量不对齐"),
        ("point", np.zeros((5, 2)), "scalar", "分量数错误"),
        ("point", np.zeros((5, 2)), "vector", "分量数错误"),
        ("cell", np.zeros((1, 2)), "vector", "分量数错误"),
    ],
)
def test_invalid_field_shape(association, values, kind, error) -> None:
    """按字段归属校验数量与分量数，不以坐标长度代替单元数。"""
    grid = _surface_quad_with_unused_point()
    _add_field(grid, values, association=association)
    with pytest.raises(ValueError, match=error):
        extract_field(grid, name="pressure", association=association, kind=kind)


def test_missing_non_numeric_and_invalid_selector() -> None:
    """不跨归属回退，不把字符串或无效选择器当作有效物理场。"""
    grid = _surface_quad_with_unused_point()
    strings = vtkStringArray()
    strings.SetName("labels")
    for _ in range(5):
        strings.InsertNextValue("x")
    grid.GetPointData().AddArray(strings)
    with pytest.raises(TypeError, match="不是数值数组"):
        extract_scalars(grid, name="labels", association="point")
    with pytest.raises(ValueError, match="不存在"):
        extract_scalars(grid, name="pressure", association="cell")
    for args in ({"name": ""}, {"association": "field"}, {"kind": "tensor"}):
        selector = {"name": "pressure", "association": "point", "kind": "scalar"} | args
        with pytest.raises(ValueError):
            extract_field(grid, **selector)


def test_pre_shares_vtk_views_and_only_reads_source_once(monkeypatch) -> None:
    """保留同一对象、原拓扑和点 mask，提取不修改数据且返回视图可共享修改。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    grid = _surface_quad_with_unused_point()
    _add_field(grid, [7.0], association="cell")
    before = vtk_to_numpy(grid.GetPoints().GetData()).copy()
    calls = []

    def read(path, **kwargs):
        calls.append(path)
        return grid

    monkeypatch.setattr(module, "read_file", read)
    result = extract_configured_sample(_shared_config())
    surface = result["surface"]
    assert len(calls) == 1
    assert surface["vtk"] is result["volume"]["vtk"] is grid
    assert grid.GetNumberOfPoints() == 5 and grid.GetNumberOfCells() == 1
    assert [grid.GetCell(0).GetPointId(i) for i in range(4)] == [0, 1, 2, 3]
    np.testing.assert_array_equal(surface["points"], before)
    np.testing.assert_array_equal(surface["fields"]["pressure"], [1, 2, 3, 4, 99])
    np.testing.assert_array_equal(surface["fields"]["cell_pressure"], [7])
    assert surface["mask"].tolist() == [True, True, True, True, False]
    assert "mask" not in result["volume"]
    assert surface["field_specs"]["cell_pressure"]["association"] == "cell"
    surface["points"][0, 0] = 42
    surface["fields"]["pressure"][0] = 123
    assert grid.GetPoint(0)[0] == 42
    assert grid.GetPointData().GetArray("pressure").GetTuple1(0) == 123
    assert result["volume"]["fields"]["pressure"][0] == 123


@pytest.mark.parametrize(
    "problem",
    [
        "duplicate",
        "missing_fields",
        "missing_array",
        "missing_association",
        "bad_association",
        "bad_kind",
        "legacy",
        "bad_source",
        "bad_cell_type",
    ],
)
def test_config_rejected_before_read(monkeypatch, problem) -> None:
    """第二个域配置错误也必须在第一次文件读取之前失败。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    config = _shared_config()
    volume = config["pre"]["volume"]
    field = volume["fields"]["pressure"]
    if problem == "duplicate":
        config["source"]["files"] *= 2
    elif problem == "missing_fields":
        del volume["fields"]
    elif problem == "missing_array":
        del field["array"]
    elif problem == "missing_association":
        del field["association"]
    elif problem == "bad_association":
        field["association"] = "field"
    elif problem == "bad_kind":
        field["kind"] = "tensor"
    elif problem == "legacy":
        volume["field"] = "scalars"
    elif problem == "bad_source":
        volume["source"] = "missing"
    elif problem == "bad_cell_type":
        volume["cell_type"] = []

    def reject(*args, **kwargs):
        raise AssertionError("不应读取文件")

    monkeypatch.setattr(module, "read_file", reject)
    with pytest.raises(ValueError) as error:
        extract_configured_sample(config)
    if problem == "legacy":
        assert "迁移到 fields" in str(error.value)


def test_field_failure_retains_context_and_cause(monkeypatch) -> None:
    """提取错误同时包含域、物理量、文件路径和原始异常。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    monkeypatch.setattr(module, "read_file", lambda *a, **k: _surface_quad_with_unused_point())
    with pytest.raises(ValueError) as error:
        extract_configured_sample(_shared_config())
    for text in ("surface", "cell_pressure", "/unused/mesh.vtu"):
        assert text in str(error.value)
    assert isinstance(error.value.__cause__, ValueError)


def test_explicit_empty_fields_supports_unlabelled_geometry(monkeypatch):
    """显式空场配置仍读取坐标和拓扑，不触发物理场读取。"""
    import importlib

    from ai4e_core.applications.aero_cfd.rawprep import derive_configured_geometry

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    from tests.integration.test_geometry_domain import _quad_xy

    config = _shared_config()
    for domain in ("surface", "volume"):
        config["pre"][domain]["fields"] = {}
    monkeypatch.setattr(module, "read_file", lambda *a, **kw: _quad_xy())

    def forbidden(*args, **kwargs):
        raise AssertionError("空字段不能触发场提取")

    monkeypatch.setattr(module, "extract_field", forbidden)
    extracted = extract_configured_sample(config)
    assert extracted["surface"]["fields"] == {}
    result = derive_configured_geometry(extracted, enabled=["surface_normals"])
    assert result["surface"]["normals_valid_mask"].all()
