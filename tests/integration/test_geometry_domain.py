"""几何派生、域标记与点数校验：点到点、点到面、法向、重合 mask。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from vtkmodules.util.vtkConstants import VTK_HEXAHEDRON, VTK_LINE, VTK_QUAD
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkDataObject, vtkPolyData, vtkUnstructuredGrid
from vtkmodules.vtkFiltersCore import vtkTriangleFilter
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

from ai4e_core.abilities.data.extract import extract_coordinates
from ai4e_core.abilities.data.filter import exterior_mask
from ai4e_core.abilities.data.validate import require_same_leading_dim
from ai4e_core.abilities.geometry import (
    mesh_signed_distance,
    nearest_vertex_distance_and_direction,
    surface_point_normals,
)
from ai4e_core.abilities.geometry.nearest import EPSILON
from ai4e_core.applications.aero_cfd.rawprep import (
    configured_geometry_enabled,
    derive_configured_geometry,
    extract_configured_sample,
)
from ai4e_core.base.config import load_config
from tests.recipe_assets import CONFIG_PATH
from tests.support import SHAPENET_SAMPLES

ALL_GEOMETRY = (
    "nearest_vertex",
    "volume_normals",
    "mesh_signed_distance",
    "surface_normals",
    "exterior_mask",
)


def _quad_xy() -> vtkUnstructuredGrid:
    """边长 2 的正方形，位于 z=0，中心在 (1, 1, 0)。"""
    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    for point in ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0), (0.0, 2.0, 0.0)):
        points.InsertNextPoint(point)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_QUAD, 4, [0, 1, 2, 3])
    return grid


def _closed_cube() -> vtkUnstructuredGrid:
    """边长 1 的封闭立方体外壳，四边形法向朝外。"""
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
    for face in (
        [0, 3, 2, 1],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [3, 7, 6, 2],
        [0, 4, 7, 3],
        [1, 2, 6, 5],
    ):
        grid.InsertNextCell(VTK_QUAD, 4, face)
    return grid


def _closest_point_on_triangle(
    point: np.ndarray, vertex_a: np.ndarray, vertex_b: np.ndarray, vertex_c: np.ndarray
) -> np.ndarray:
    """独立的点到三角形最近点，不走 VTK 隐式距离。"""
    ab = vertex_b - vertex_a
    ac = vertex_c - vertex_a
    ap = point - vertex_a
    d1 = float(np.dot(ab, ap))
    d2 = float(np.dot(ac, ap))
    if d1 <= 0.0 and d2 <= 0.0:
        return vertex_a
    bp = point - vertex_b
    d3 = float(np.dot(ab, bp))
    d4 = float(np.dot(ac, bp))
    if d3 >= 0.0 and d4 <= d3:
        return vertex_b
    vc = d1 * d4 - d3 * d2
    if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
        return vertex_a + (d1 / (d1 - d3)) * ab
    cp = point - vertex_c
    d5 = float(np.dot(ab, cp))
    d6 = float(np.dot(ac, cp))
    if d6 >= 0.0 and d5 <= d6:
        return vertex_c
    vb = d5 * d2 - d1 * d6
    if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
        return vertex_a + (d2 / (d2 - d6)) * ac
    va = d3 * d6 - d5 * d4
    if va <= 0.0 and (d4 - d3) >= 0.0 and (d5 - d6) >= 0.0:
        weight = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        return vertex_b + weight * (vertex_c - vertex_b)
    denom = 1.0 / (va + vb + vc)
    return vertex_a + ab * (vb * denom) + ac * (vc * denom)


def _vtk_surface_triangles(surface) -> list[np.ndarray]:
    """抽出 VTK 三角化后的表面，作为点到面的独立对照网格。"""
    clone = surface.NewInstance()
    clone.DeepCopy(surface)
    extractor = vtkDataSetSurfaceFilter()
    extractor.SetInputData(clone)
    extractor.Update()
    triangulate = vtkTriangleFilter()
    triangulate.SetInputData(extractor.GetOutput())
    triangulate.Update()
    poly = triangulate.GetOutput()
    points = np.array(
        [poly.GetPoint(index) for index in range(poly.GetNumberOfPoints())],
        dtype=np.float64,
    )
    triangles: list[np.ndarray] = []
    for index in range(poly.GetNumberOfCells()):
        cell = poly.GetCell(index)
        if cell.GetNumberOfPoints() != 3:
            continue
        ids = [cell.GetPointId(offset) for offset in range(3)]
        triangles.append(points[ids])
    return triangles


def _brute_mesh_distance(
    queries: np.ndarray, triangles: list[np.ndarray]
) -> tuple[np.ndarray, np.ndarray]:
    """对三角化表面做暴力最近点，核对 VTK 点到面的绝对值与落点。"""
    distances = np.empty(len(queries), dtype=np.float64)
    closest = np.empty_like(queries)
    for index, query in enumerate(queries):
        best_point = triangles[0][0]
        best_distance = np.inf
        for triangle in triangles:
            candidate = _closest_point_on_triangle(query, triangle[0], triangle[1], triangle[2])
            distance = float(np.linalg.norm(query - candidate))
            if distance < best_distance:
                best_distance = distance
                best_point = candidate
        distances[index] = best_distance
        closest[index] = best_point
    return distances, closest


def _hex() -> vtkUnstructuredGrid:
    """单位立方体。"""
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
    return grid


def _extracted(surface: vtkUnstructuredGrid, volume: vtkUnstructuredGrid) -> dict:
    """构造可供几何装配使用的提取结果。"""
    surface_points = extract_coordinates(surface)
    volume_points = extract_coordinates(volume)
    return {
        "surface": {
            "vtk": surface,
            "points": surface_points,
            "fields": {"pressure": np.arange(len(surface_points), dtype=np.float64)},
            "field_specs": {
                "pressure": {"array": "pressure", "association": "point", "kind": "scalar"}
            },
        },
        "volume": {
            "vtk": volume,
            "points": volume_points,
            "fields": {"velocity": np.ones((len(volume_points), 3), dtype=np.float64)},
            "field_specs": {
                "velocity": {"array": "velocity", "association": "point", "kind": "vector"}
            },
        },
    }


def test_nearest_vertex_distance_and_direction() -> None:
    query = np.array([[0.0, 0.0, 1.0]])
    boundary = np.array([[0.0, 0.0, 0.0]])
    distance, direction = nearest_vertex_distance_and_direction(query, boundary)
    assert distance.shape == (1,)
    np.testing.assert_allclose(distance, [1.0])
    np.testing.assert_allclose(direction, [[0.0, 0.0, 1.0]])


def test_nearest_vertex_uses_vertex_not_face_center() -> None:
    query = np.array([[1.0, 1.0, 1.0]])
    boundary = extract_coordinates(_quad_xy())
    distance, _ = nearest_vertex_distance_and_direction(query, boundary)
    np.testing.assert_allclose(distance, [np.sqrt(3.0)])
    assert distance[0] > 1.0


def test_nearest_vertex_rejects_empty_boundary() -> None:
    with pytest.raises(ValueError, match="边界点为空"):
        nearest_vertex_distance_and_direction(np.zeros((1, 3)), np.zeros((0, 3)))


def test_mesh_signed_distance_uses_face() -> None:
    query = np.array([[1.0, 1.0, 1.0], [1.0, 1.0, -2.0]])
    signed, closest, direction = mesh_signed_distance(query, _quad_xy())
    np.testing.assert_allclose(signed, [1.0, -2.0], atol=1e-6)
    np.testing.assert_allclose(closest, [[1.0, 1.0, 0.0], [1.0, 1.0, 0.0]], atol=1e-6)
    assert np.abs(signed[0]) < np.sqrt(3.0) - 1e-6
    np.testing.assert_allclose(direction, [[0.0, 0.0, 1.0], [0.0, 0.0, -1.0]], atol=1e-6)
    np.testing.assert_allclose(
        np.linalg.norm(query - closest, axis=1),
        np.abs(signed),
        atol=1e-12,
    )


def test_mesh_signed_distance_hits_edge_and_vertex() -> None:
    query = np.array(
        [
            [1.0, 1.0, 0.0],
            [3.0, 1.0, 0.0],
            [-1.0, -1.0, 1.0],
            [0.0, 0.0, 0.0],
        ]
    )
    signed, closest, direction = mesh_signed_distance(query, _quad_xy())
    expect_closest = np.array(
        [
            [1.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ]
    )
    np.testing.assert_allclose(np.abs(signed), [0.0, 1.0, np.sqrt(3.0), 0.0], atol=1e-6)
    np.testing.assert_allclose(closest, expect_closest, atol=1e-6)
    offset = query - closest
    np.testing.assert_allclose(
        direction,
        offset / (np.abs(signed)[:, np.newaxis] + EPSILON),
        atol=1e-12,
    )


def test_mesh_signed_distance_closed_cube_inside_outside() -> None:
    query = np.array(
        [
            [0.5, 0.5, 0.5],
            [0.5, 0.5, 2.0],
            [2.0, 0.5, 0.5],
            [-1.0, 0.5, 0.5],
            [0.5, 0.5, -1.0],
            [0.5, 0.5, 1.0],
        ]
    )
    signed, closest, _ = mesh_signed_distance(query, _closed_cube())
    np.testing.assert_allclose(signed, [-0.5, 1.0, 1.0, 1.0, 1.0, 0.0], atol=1e-6)
    np.testing.assert_allclose(
        closest[1:],
        [
            [0.5, 0.5, 1.0],
            [1.0, 0.5, 0.5],
            [0.0, 0.5, 0.5],
            [0.5, 0.5, 0.0],
            [0.5, 0.5, 1.0],
        ],
        atol=1e-6,
    )


def test_mesh_signed_distance_matches_independent_closest() -> None:
    query = np.array(
        [
            [1.0, 1.0, 1.0],
            [1.0, 1.0, -2.0],
            [3.0, 1.0, 0.0],
            [-1.0, -1.0, 1.0],
            [0.2, 1.7, 0.4],
        ]
    )
    surface = _quad_xy()
    signed, closest, _ = mesh_signed_distance(query, surface)
    brute_distance, brute_closest = _brute_mesh_distance(query, _vtk_surface_triangles(surface))
    np.testing.assert_allclose(np.abs(signed), brute_distance, atol=1e-9)
    np.testing.assert_allclose(closest, brute_closest, atol=1e-9)


@pytest.mark.parametrize(
    "surface,match",
    [
        (vtkDataObject(), "带网格"),
        (vtkPolyData(), "裸点云|表面单元"),
    ],
)
def test_mesh_signed_distance_rejects_point_cloud(surface, match) -> None:
    if isinstance(surface, vtkPolyData):
        points = vtkPoints()
        points.InsertNextPoint(0.0, 0.0, 0.0)
        surface.SetPoints(points)
    with pytest.raises(ValueError, match=match):
        mesh_signed_distance(np.zeros((1, 3)), surface)


def test_mesh_signed_distance_rejects_line_and_hex() -> None:
    line = vtkUnstructuredGrid()
    points = vtkPoints()
    points.InsertNextPoint(0.0, 0.0, 0.0)
    points.InsertNextPoint(1.0, 0.0, 0.0)
    line.SetPoints(points)
    line.InsertNextCell(VTK_LINE, 2, [0, 1])
    with pytest.raises(ValueError, match="面单元"):
        mesh_signed_distance(np.zeros((1, 3)), line)
    with pytest.raises(ValueError, match="面单元"):
        mesh_signed_distance(np.zeros((1, 3)), _hex())


def test_mesh_signed_distance_does_not_mutate_input() -> None:
    surface = _quad_xy()
    before_cells = surface.GetNumberOfCells()
    before_points = surface.GetNumberOfPoints()
    mesh_signed_distance(np.array([[1.0, 1.0, 1.0]]), surface)
    assert surface.GetNumberOfCells() == before_cells
    assert surface.GetNumberOfPoints() == before_points
    assert surface.GetCellData().GetNormals() is None


def test_surface_point_normals_on_flat_quad() -> None:
    surface = _quad_xy()
    normals = surface_point_normals(surface)
    assert normals.shape == (4, 3)
    np.testing.assert_allclose(np.abs(normals[:, 2]), 1.0, atol=1e-6)
    assert surface.GetCellData().GetNormals() is None
    assert surface.GetPointData().GetNormals() is None


def test_surface_point_normals_reject_nan() -> None:
    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    points.InsertNextPoint(0.0, 0.0, 0.0)
    points.InsertNextPoint(1.0, 0.0, 0.0)
    points.InsertNextPoint(float("nan"), 1.0, 0.0)
    points.InsertNextPoint(0.0, 1.0, 0.0)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_QUAD, 4, [0, 1, 2, 3])
    with pytest.raises(RuntimeError, match="NaN"):
        surface_point_normals(grid)


def test_exterior_mask_marks_exact_duplicates_only() -> None:
    volume = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 0.5, 0.5],
            [2.0, 2.0, 2.0],
        ]
    )
    surface = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    mask = exterior_mask(volume, surface)
    assert mask.tolist() == [False, False, True, True]
    assert len(volume) == 4


def test_exterior_mask_nearby_points_remain_true() -> None:
    volume = np.array([[0.0, 0.0, 1e-12]])
    surface = np.array([[0.0, 0.0, 0.0]])
    assert exterior_mask(volume, surface).tolist() == [True]


def test_require_same_leading_dim_reports_lengths() -> None:
    with pytest.raises(ValueError, match="position=2.*pressure=1"):
        require_same_leading_dim(
            np.zeros((2, 3)),
            np.zeros(1),
            labels=("position", "pressure"),
        )


def test_require_same_leading_dim_mask_length() -> None:
    with pytest.raises(ValueError, match="exterior_mask=1"):
        require_same_leading_dim(
            np.zeros((2, 3)),
            np.array([True]),
            labels=("position", "exterior_mask"),
        )


def test_derive_configured_geometry_keeps_extract_keys() -> None:
    extracted = _extracted(_quad_xy(), _hex())
    result = derive_configured_geometry(extracted, enabled=ALL_GEOMETRY)
    assert result["surface"]["vtk"] is extracted["surface"]["vtk"]
    assert result["surface"]["points"].shape[0] == 4
    assert "pressure" in result["surface"]["fields"]
    assert result["surface"]["normals"].shape == (4, 3)
    volume = result["volume"]
    n_volume = volume["points"].shape[0]
    assert volume["nearest_distance"].shape == (n_volume,)
    assert volume["nearest_direction"].shape == (n_volume, 3)
    assert volume["signed_distance"].shape == (n_volume,)
    assert volume["closest_on_surface"].shape == (n_volume, 3)
    assert volume["surface_direction"].shape == (n_volume, 3)
    assert volume["exterior_mask"].shape == (n_volume,)
    assert volume["exterior_mask"].dtype == bool
    assert bool(volume["exterior_mask"][0]) is False


@pytest.mark.local_data
@pytest.mark.parametrize("sample_relative", SHAPENET_SAMPLES)
def test_derive_real_shapenet_sample(shapenet_raw: Path, sample_relative: Path) -> None:
    sample = shapenet_raw / sample_relative
    if not (sample / "quadpress_smpl.vtk").is_file():
        pytest.skip(f"样本目录不存在: {sample}")
    config = load_config(CONFIG_PATH)
    config["dataset"]["root"] = str(shapenet_raw)
    extracted = extract_configured_sample(config, sample_relative=sample_relative)
    result = derive_configured_geometry(extracted, enabled=configured_geometry_enabled(config))
    n_surface = result["surface"]["points"].shape[0]
    n_volume = result["volume"]["points"].shape[0]
    assert result["surface"]["normals"].shape == (n_surface, 3)
    assert not np.isnan(result["surface"]["normals"]).any()
    assert result["volume"]["nearest_distance"].shape == (n_volume,)
    assert np.all(result["volume"]["nearest_distance"] >= 0)
    assert result["volume"]["exterior_mask"].shape == (n_volume,)
    signed = result["volume"]["signed_distance"]
    closest = result["volume"]["closest_on_surface"]
    assert signed.shape == (n_volume,)
    np.testing.assert_allclose(
        np.linalg.norm(result["volume"]["points"] - closest, axis=1),
        np.abs(signed),
        atol=1e-12,
    )
    used_mask = result["surface"].get("mask")
    used_vertices = (
        result["surface"]["points"][used_mask]
        if used_mask is not None
        else result["surface"]["points"]
    )
    used_nearest, _ = nearest_vertex_distance_and_direction(
        result["volume"]["points"], used_vertices
    )
    assert np.all(np.abs(signed) <= used_nearest + 1e-6)
    rng = np.random.default_rng(1)
    selected = rng.choice(n_volume, size=min(40, n_volume), replace=False)
    brute_distance, brute_closest = _brute_mesh_distance(
        result["volume"]["points"][selected],
        _vtk_surface_triangles(extracted["surface"]["vtk"]),
    )
    np.testing.assert_allclose(np.abs(signed[selected]), brute_distance, atol=1e-6)
    np.testing.assert_allclose(closest[selected], brute_closest, atol=1e-6)
    assert result["volume"]["points"].shape[0] == extracted["volume"]["points"].shape[0]
    if "mask" in extracted["surface"]:
        assert result["surface"]["mask"].shape == (n_surface,)


@pytest.mark.parametrize("bad_type", [VTK_LINE, VTK_HEXAHEDRON])
def test_mixed_non_surface_rejected_before_any_algorithm(monkeypatch, bad_type):
    """面混入线/体时全体门禁先行，不能先执行最近点算法。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.derive")
    surface = _hex()
    surface.Reset()
    surface.SetPoints(_hex().GetPoints())
    surface.InsertNextCell(VTK_QUAD, 4, [0, 1, 2, 3])
    ids = [0, 1] if bad_type == VTK_LINE else list(range(8))
    surface.InsertNextCell(bad_type, len(ids), ids)

    def forbidden(*args, **kwargs):
        raise AssertionError("门禁失败前不应执行算法")

    monkeypatch.setattr(module, "nearest_vertex_distance_and_direction", forbidden)
    with pytest.raises(ValueError, match=f"第 1 个单元类型={bad_type}"):
        derive_configured_geometry(
            {"surface": {"vtk": surface}, "volume": {"vtk": _hex()}}, enabled=ALL_GEOMETRY
        )
    for function in (surface_point_normals, lambda s: mesh_signed_distance(np.zeros((1, 3)), s)):
        with pytest.raises(ValueError, match="第 1 个单元"):
            function(surface)


def test_normals_original_identity_isolated_points_and_existing_attributes():
    """非顺序引用的两片正交面与孤立点，旧法向不能影响新计算。"""
    from vtkmodules.util.numpy_support import numpy_to_vtk

    from ai4e_core.abilities.geometry import surface_point_normals_with_mask

    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    for p in [
        (99, 99, 99),
        (0, 0, 0),
        (2, 0, 0),
        (2, 2, 0),
        (0, 2, 0),
        (10, 0, 0),
        (10, 2, 0),
        (10, 2, 2),
        (10, 0, 2),
    ]:
        points.InsertNextPoint(p)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_QUAD, 4, [5, 6, 7, 8])
    grid.InsertNextCell(VTK_QUAD, 4, [1, 2, 3, 4])
    old = numpy_to_vtk(np.ones((9, 3)), deep=True)
    old.SetName("Normals")
    grid.GetPointData().SetNormals(old)
    normals, valid = surface_point_normals_with_mask(grid)
    assert valid.tolist() == [False] + [True] * 8
    np.testing.assert_array_equal(normals[0], [0, 0, 0])
    np.testing.assert_allclose(np.abs(normals[1:5]), [[0, 0, 1]] * 4, atol=1e-6)
    np.testing.assert_allclose(np.abs(normals[5:]), [[1, 0, 0]] * 4, atol=1e-6)
    assert grid.GetPointData().GetNormals() is old
    assert grid.GetPointData().GetNumberOfArrays() == 1
    assert grid.GetCell(0).GetPointId(0) == 5
    from vtkmodules.util.numpy_support import vtk_to_numpy

    from ai4e_core.abilities.geometry.surface import ORIGINAL_POINT_IDS, prepare_surface

    prepared = prepare_surface(grid)
    mapped = vtk_to_numpy(prepared.poly.GetPointData().GetArray(ORIGINAL_POINT_IDS))
    assert mapped.tolist() != list(range(9))


@pytest.mark.parametrize("cell_type", [5, 7, 8, 9, 6])
def test_supported_surface_cell_types_and_polydata(cell_type):
    """triangle/polygon/pixel/quad/strip 均支持，并兼容 PolyData。"""
    from ai4e_core.abilities.geometry import surface_point_normals_with_mask

    grid = _quad_xy()
    grid.Reset()
    grid.SetPoints(_quad_xy().GetPoints())
    ids = {5: [0, 1, 2], 7: [0, 1, 2, 3], 8: [0, 1, 3, 2], 9: [0, 1, 2, 3], 6: [0, 1, 3, 2]}[
        cell_type
    ]
    grid.InsertNextCell(cell_type, len(ids), ids)
    extractor = vtkDataSetSurfaceFilter()
    extractor.SetInputData(grid)
    extractor.Update()
    for surface in (grid, extractor.GetOutput()):
        normals, valid = surface_point_normals_with_mask(surface)
        np.testing.assert_allclose(np.abs(normals[valid, 2]), 1, atol=1e-6)
        d, _, _ = mesh_signed_distance(np.array([[1, 1, 1.0]]), surface)
        np.testing.assert_allclose(np.abs(d), [1])


def test_degenerate_face_rejected():
    grid = _quad_xy()
    for i in range(4):
        grid.GetPoints().SetPoint(i, i, 0, 0)
    with pytest.raises(RuntimeError, match="零长度|退化"):
        surface_point_normals(grid)


@pytest.mark.parametrize("selected", [[], *[[x] for x in ALL_GEOMETRY], list(ALL_GEOMETRY)])
def test_optional_geometry_independent_without_labels(monkeypatch, selected):
    """未启用函数绝不执行；只传 vtk，无标签也能计算。"""
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.derive")
    functions = {
        "nearest_vertex": "nearest_vertex_distance_and_direction",
        "volume_normals": "nearest_vertex_distance_and_direction",
        "mesh_signed_distance": "mesh_signed_distance",
        "surface_normals": "surface_point_normals_with_mask",
        "exterior_mask": "exterior_mask",
    }
    expected = {
        "nearest_vertex": {"nearest_distance"},
        "volume_normals": {"nearest_direction"},
        "mesh_signed_distance": {"signed_distance", "closest_on_surface", "surface_direction"},
        "surface_normals": {"normals", "normals_valid_mask"},
        "exterior_mask": {"exterior_mask"},
    }

    def forbidden(*args, **kwargs):
        raise AssertionError("调用了未启用的能力")

    needed = {functions[name] for name in selected}
    for function in set(functions.values()):
        if function not in needed:
            monkeypatch.setattr(module, function, forbidden)
    data = {"surface": {"vtk": _quad_xy()}, "volume": {"vtk": _hex()}, "extra": {"note": "保留"}}
    result = derive_configured_geometry(data, enabled=selected)
    actual = (set(result["surface"]) | set(result["volume"])) - {"vtk"}
    assert actual == set().union(*(expected[x] for x in selected))
    assert result["extra"] == data["extra"]
    assert set(data["surface"]) == {"vtk"}


def test_normals_only_and_point_cloud_paths():
    result = derive_configured_geometry(
        {"surface": {"vtk": _quad_xy()}}, enabled=["surface_normals"]
    )
    assert "volume" not in result
    cloud = vtkPolyData()
    cloud.SetPoints(_quad_xy().GetPoints())
    data = {"surface": {"vtk": cloud}, "volume": {"vtk": _hex()}}
    result = derive_configured_geometry(data, enabled=["nearest_vertex", "exterior_mask"])
    assert result["volume"]["nearest_distance"].shape == (8,)
    assert "nearest_direction" not in result["volume"]
    only_normals = derive_configured_geometry(data, enabled=["volume_normals"])
    assert only_normals["volume"]["nearest_direction"].shape == (8, 3)
    assert "nearest_distance" not in only_normals["volume"]
    with pytest.raises(ValueError, match="裸点云"):
        derive_configured_geometry(data, enabled=["mesh_signed_distance"])


@pytest.mark.parametrize(
    "enabled,match",
    [(["bad"], "未知"), (["exterior_mask"] * 2, "重复"), ("surface_normals", "序列")],
)
def test_invalid_selection_fails_before_geometry(enabled, match):
    with pytest.raises(ValueError, match=match):
        derive_configured_geometry({}, enabled=enabled)


def test_conflict_preflight_and_fields_are_opaque(monkeypatch):
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.derive")
    fields = {"pressure": np.array([7.0]), "other": np.ones(13)}
    specs = {"pressure": {"association": "cell", "kind": "scalar", "array": "P"}}
    mask = np.array([True, True, True, True])
    data = {
        "surface": {"vtk": _quad_xy(), "fields": fields, "field_specs": specs, "mask": mask},
        "volume": {"vtk": _hex()},
    }
    result = derive_configured_geometry(data, enabled=ALL_GEOMETRY)
    assert result["surface"]["fields"] is fields
    assert result["surface"]["field_specs"] is specs
    assert result["surface"]["mask"] is mask
    data["surface"]["normals"] = np.zeros((4, 3))

    def forbidden(*args, **kwargs):
        raise AssertionError("冲突检查前不能执行算法")

    monkeypatch.setattr(module, "nearest_vertex_distance_and_direction", forbidden)
    with pytest.raises(ValueError, match="冲突"):
        derive_configured_geometry(data, enabled=ALL_GEOMETRY)


def test_config_selection_defaults_and_shapenet():
    assert configured_geometry_enabled({}) == ()
    assert configured_geometry_enabled({"pre": {"geometry": {}}}) == ()
    assert configured_geometry_enabled(load_config(CONFIG_PATH)) == ALL_GEOMETRY
    for config in (
        {"pre": {"geometry": {"enabled": "surface_normals"}}},
        {"pre": {"geometry": {"enabled": ["bad"]}}},
    ):
        with pytest.raises(ValueError):
            configured_geometry_enabled(config)
    assert derive_configured_geometry({"extra": {"note": 3}}, enabled=[]) == {"extra": {"note": 3}}


def test_mixed_face_types_on_curved_surface_and_reverse_winding():
    """门禁允许混合二维面和非共面表面，距离符号仍跟随绕序。"""
    from vtkmodules.util.vtkConstants import VTK_TRIANGLE
    from vtkmodules.vtkFiltersCore import vtkReverseSense

    from ai4e_core.abilities.geometry import require_surface_mesh, surface_point_normals_with_mask

    surface = _closed_cube()
    surface.InsertNextCell(VTK_TRIANGLE, 3, [0, 1, 5])
    assert require_surface_mesh(surface) is surface
    _, valid = surface_point_normals_with_mask(surface)
    assert valid.all()
    extractor = vtkDataSetSurfaceFilter()
    extractor.SetInputData(_closed_cube())
    extractor.Update()
    reverse = vtkReverseSense()
    reverse.SetInputData(extractor.GetOutput())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()
    reverse.Update()
    query = np.array([[0.5, 0.5, 0.5], [2, 0.5, 0.5]])
    d1 = mesh_signed_distance(query, extractor.GetOutput())[0]
    d2 = mesh_signed_distance(query, reverse.GetOutput())[0]
    np.testing.assert_allclose(d1, -d2)
