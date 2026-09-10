"""张量落盘、外流预处理编排与统计量。"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.vtkConstants import VTK_HEXAHEDRON, VTK_QUAD
from vtkmodules.vtkCommonCore import vtkDoubleArray, vtkFloatArray, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter

from ai4e_core.abilities.data.filter.records import filter_records
from ai4e_core.abilities.data.save import encode_field, load_named_tensor, write_named_tensors
from ai4e_core.abilities.data.stats import accumulate_moments, load_statistics
from ai4e_core.abilities.data.validate import (
    FieldValidationError,
    require_valid_records,
    validate_records,
)
from ai4e_core.applications.aero_cfd.rawprep import enumerate_sample_relatives
from ai4e_core.applications.base import StageError
from ai4e_core.base.config import load_config
from tests.recipe_assets import CONFIG_PATH, RECIPE_DIR
from tests.legacy_pre import build, build_sample
from tests.support import SHAPENET_SAMPLES


def _record(
    name: str,
    values: np.ndarray,
    *,
    association: str = "point",
    kind: str = "scalar",
    group: str,
) -> dict:
    """构造一条具名场记录。"""
    return {
        "name": name,
        "values": np.asarray(values),
        "association": association,
        "kind": kind,
        "group": group,
    }


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


def _add_field(grid: vtkUnstructuredGrid, values, *, name: str, association: str = "point") -> None:
    """添加具名数值数组，不改变活动字段。"""
    array = numpy_to_vtk(np.asarray(values), deep=True)
    array.SetName(name)
    attrs = grid.GetPointData() if association == "point" else grid.GetCellData()
    attrs.AddArray(array)


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


def _volume_hex(*, with_vorticity: bool = False) -> vtkUnstructuredGrid:
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
    if with_vorticity:
        _add_field(grid, [[0.1, 0.2, 0.3]], name="vorticity", association="cell")
    return grid


def _write_vtk(path: Path, grid: vtkUnstructuredGrid) -> None:
    """写出一份 Legacy VTK 网格。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtkUnstructuredGridWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(grid)
    writer.Write()


def _sample_config(root: Path, *, declare_vorticity: bool = False) -> dict:
    """基于案例 YAML 指向临时样本根。"""
    config = load_config(CONFIG_PATH)
    config["dataset"]["root"] = str(root)
    config["pre"]["surface"]["fields"]["pressure"]["array"] = "pressure"
    config["pre"]["volume"]["fields"]["velocity"]["array"] = "velocity"
    if declare_vorticity:
        config["pre"]["volume"]["fields"]["vorticity"] = {
            "array": "vorticity",
            "association": "cell",
            "kind": "vector",
        }
    config["pre"]["discover"] = {"param_count": 1, "exclude": [], "expected_total": None}
    return config


def _write_fixture_sample(sample_dir: Path, *, with_vorticity: bool = False) -> None:
    """写出表面四边形和体积六面体夹具。"""
    _write_vtk(sample_dir / "quadpress_smpl.vtk", _surface_quad_with_unused_point())
    _write_vtk(
        sample_dir / "hexvelo_smpl.vtk",
        _volume_hex(with_vorticity=with_vorticity),
    )


def _aligned(association="point", size=3):
    ids = np.arange(size)
    group = {"source": "mesh", "association": association, "count": size, "entity_ids": ids}
    records = [
        {
            "name": "p",
            "values": np.arange(size, dtype=float),
            "association": association,
            "kind": "scalar",
            "group": "arbitrary",
            "source": "mesh",
            "entity_ids": ids,
        }
    ]
    return records, {"arbitrary": group}


def _sample(tmp_path, *, cell=False, dry_run=False, config=None, overwrite=False):
    raw = tmp_path / "raw"
    _write_fixture_sample(raw / "param0/a", with_vorticity=cell)
    cfg = config if config is not None else _sample_config(raw, declare_vorticity=cell)
    cfg["pre"]["output"]["dir"] = str(tmp_path / "out")
    return build_sample(cfg).run(
        {"config": cfg, "sample": "param0/a", "dry_run": dry_run, "overwrite": overwrite}
    )["result"]


@pytest.mark.parametrize("association", ["point", "cell"])
@pytest.mark.parametrize("defect", ["length", "order", "duplicate", "source", "association"])
def test_explicit_alignment_without_mask(association, defect):
    records, groups = _aligned(association)
    other = {**records[0], "name": "q"}
    if defect == "length":
        other["values"] = np.ones(2)
    elif defect == "order":
        other["entity_ids"] = np.array([1, 0, 2])
    elif defect == "duplicate":
        other["name"] = "p"
    elif defect == "source":
        other["source"] = "different"
    else:
        other["association"] = "cell" if association == "point" else "point"
    report = validate_records([*records, other], groups, sample="case-A")
    assert report["valid"] is False
    assert report["issues"][0]["sample"] == "case-A"
    assert report["issues"][0]["field"] == other["name"]
    with pytest.raises(FieldValidationError):
        require_valid_records([*records, other], groups)


def test_filter_keeps_identity_and_original():
    records, groups = _aligned()
    records.append({**records[0], "name": "q", "values": np.array([9.0, 8.0, 7.0])})
    output, filtered = filter_records(records, groups, {"arbitrary": np.array([True, False, True])})
    assert filtered["arbitrary"]["entity_ids"].tolist() == [0, 2]
    assert output[1]["values"].tolist() == [9.0, 7.0]
    assert output[0]["entity_ids"] is filtered["arbitrary"]["entity_ids"]
    assert records[0]["values"].tolist() == [0.0, 1.0, 2.0]
    assert validate_records(output, filtered)["valid"]
    records, groups = _aligned("cell")
    with pytest.raises(ValueError, match="不适用于单元"):
        filter_records(records, groups, {"arbitrary": np.ones(3, dtype=bool)})


def test_encoder_does_not_guess_group_suffix():
    records, _ = _aligned("cell")
    record = {**records[0], "group": "named_point"}
    tensor = encode_field(record)
    assert tensor.dtype == torch.float32
    assert tensor.shape == (3,)
    tensor[0] = 100
    assert record["values"][0] == 0


@pytest.mark.parametrize("dry_run", [False, True])
def test_preflight_same_for_bad_filename(tmp_path, dry_run):
    raw = tmp_path / "raw"
    cfg = _sample_config(raw)
    cfg["pre"]["output"]["filemap"]["surface_pressure"] = "../invalid.pt"
    with pytest.raises(StageError, match="select_fields"):
        _sample(tmp_path, config=cfg, dry_run=dry_run)
    assert not list(tmp_path.rglob("*.pt"))


@pytest.mark.parametrize("filemap", [{"p": "same.pt", "q": "same.pt"}, {"missing": "x.pt"}])
def test_writer_rejects_duplicate_or_required_missing(tmp_path, filemap):
    with pytest.raises(ValueError):
        write_named_tensors(tmp_path / "x", {"p": torch.ones(1), "q": torch.ones(1)}, filemap)
    assert not (tmp_path / "x").exists()


def test_explicit_optional_field(tmp_path):
    dest = write_named_tensors(
        tmp_path / "x", {"p": torch.ones(1)}, {"p": "p.pt", "q": "q.pt"}, optional=["q"]
    )
    assert sorted(p.name for p in dest.iterdir()) == ["p.pt"]
    with pytest.raises(ValueError, match="输出为空"):
        write_named_tensors(tmp_path / "empty", {}, {"q": "q.pt"}, optional=["q"])


@pytest.mark.parametrize("phase", ["serialize", "backup", "promote", "restore", "cleanup"])
def test_commit_failure_protects_old_data(tmp_path, monkeypatch, phase):
    from ai4e_core.abilities.data.save import store

    dest = tmp_path / "sample"
    dest.mkdir()
    (dest / "old.txt").write_text("old")
    original_replace = Path.replace
    original_rmtree = store.shutil.rmtree
    original_save = store.torch.save

    def replace(path, target):
        if (
            (phase == "backup" and path == dest)
            or (phase in ("promote", "restore") and path.suffix == ".tmp")
            or (phase == "restore" and path.suffix == ".bak")
        ):
            raise OSError(f"injected {phase}")
        return original_replace(path, target)

    def save(*args, **kwargs):
        if phase == "serialize":
            raise RuntimeError("injected serialize")
        return original_save(*args, **kwargs)

    def rmtree(path, *args, **kwargs):
        if phase == "cleanup" and Path(path).suffix == ".bak":
            raise OSError("injected cleanup")
        return original_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(Path, "replace", replace)
    monkeypatch.setattr(store.torch, "save", save)
    monkeypatch.setattr(store.shutil, "rmtree", rmtree)
    if phase == "cleanup":
        with pytest.warns(store.BackupCleanupWarning, match="已提交"):
            assert (
                write_named_tensors(dest, {"p": torch.ones(2)}, {"p": "p.pt"}, overwrite=True)
                == dest
            )
        assert (dest / "p.pt").exists()
        assert next(tmp_path.glob(".sample.*.bak")).joinpath("old.txt").read_text() == "old"
    else:
        with pytest.raises((OSError, RuntimeError)) as caught:
            write_named_tensors(dest, {"p": torch.ones(2)}, {"p": "p.pt"}, overwrite=True)
        if phase == "restore":
            backup = next(tmp_path.glob(".sample.*.bak"))
            assert (backup / "old.txt").read_text() == "old"
            assert str(backup) in str(caught.value)
            assert list(tmp_path.glob(".sample.*.tmp"))
        else:
            assert (dest / "old.txt").read_text() == "old"
            assert not list(tmp_path.glob(".sample.*.tmp"))


def test_leftovers_block_and_parent_alone_does_not(tmp_path):
    (tmp_path / ".sample.previous.bak").mkdir()
    with pytest.raises(FileExistsError, match="遗留"):
        write_named_tensors(tmp_path / "sample", {"p": torch.ones(1)}, {"p": "p.pt"})
    assert write_named_tensors(tmp_path / "other", {"p": torch.ones(1)}, {"p": "p.pt"}).exists()


def test_shapenet_seven_outputs_and_cell(tmp_path):
    result = _sample(tmp_path)
    dest = Path(result["path"])
    assert len(list(dest.glob("*.pt"))) == 7
    assert load_named_tensor(dest / "surface_points.pt").shape == (4, 3)
    assert load_named_tensor(dest / "surface_pressure.pt").tolist() == [1.0, 2.0, 3.0, 4.0]
    assert load_named_tensor(dest / "volume_velocity.pt").shape == (4, 3)
    assert result["validation"]["valid"] and result["filtered_validation"]["valid"]
    result = _sample(tmp_path, cell=True, overwrite=True)
    assert load_named_tensor(Path(result["path"]) / "cell.pt")["vorticity"].shape == (1, 3)


def test_dry_run_and_overwrite_preflight(tmp_path):
    result = _sample(tmp_path, dry_run=True)
    assert not result["written"] and not list(tmp_path.rglob("*.pt"))
    _sample(tmp_path)
    with pytest.raises(StageError, match="write_tensors"):
        _sample(tmp_path, dry_run=True)
    assert _sample(tmp_path, overwrite=True)["written"]


def test_geometry_selection_without_labels_and_surface_cell(tmp_path):
    raw = tmp_path / "raw"
    cfg = _sample_config(raw)
    cfg["pre"]["surface"]["fields"] = {}
    cfg["pre"]["volume"]["fields"] = {}
    cfg["pre"]["output"].update(
        filemap={"distance": "d.pt", "valid": "valid.pt"},
        fields={
            "distance": {"domain": "volume", "field": "signed_distance"},
            "valid": {"domain": "surface", "field": "normals_valid_mask"},
        },
        bundles={},
        optional=[],
    )
    result = _sample(tmp_path, config=cfg)
    assert result["names"] == ["distance", "valid"]
    assert load_named_tensor(Path(result["path"]) / "valid.pt").tolist() == [1.0, 1.0, 1.0, 1.0]
    cfg["pre"]["geometry"]["enabled"] = []
    with pytest.raises(StageError, match="select_fields"):
        _sample(tmp_path, config=cfg, overwrite=True)


def test_arbitrary_directory_and_surface_only_flow(tmp_path):
    raw = tmp_path / "raw"
    _write_fixture_sample(raw / "experiment/car")
    cfg = _sample_config(raw)
    del cfg["pre"]["volume"]
    cfg["pre"]["geometry"]["enabled"] = ["surface_normals"]
    cfg["pre"]["filters"] = {"surface": ["mask"]}
    cfg["pre"]["discover"] = {"glob": "*/*"}
    cfg["pre"]["output"].update(
        dir=str(tmp_path / "out"),
        root_subdir="tensors",
        filemap={"orientation": "n.pt"},
        fields={"orientation": {"domain": "surface", "field": "normals"}},
        bundles={},
        optional=[],
    )
    ctx = build(cfg).run({"config": cfg, "recipe_dir": RECIPE_DIR})
    assert ctx["batch"]["success"] == 1
    assert (tmp_path / "out/tensors/experiment/car/n.pt").exists()


def _stats_context(tmp_path, *, missing=None, dry_run=False):
    raw = tmp_path / "raw"
    _write_fixture_sample(raw / "param0/a")
    _write_fixture_sample(raw / "param0/b")
    cfg = _sample_config(raw)
    cfg["pre"]["output"]["dir"] = str(tmp_path / "out")
    cfg["pre"]["stats"].update(
        recalculate=True,
        train_params=[0],
        fields=["surface_pressure"],
        position_fields=[],
        missing="error",
    )
    if missing is not None:
        cfg["pre"]["stats"]["fields"] = [missing]
    return cfg, {"config": cfg, "recipe_dir": RECIPE_DIR, "dry_run": dry_run}


def test_recomputed_statistics_use_actual_paths(tmp_path):
    cfg, ctx = _stats_context(tmp_path)
    result = build(cfg).run(ctx)
    path = Path(result["statistics"])
    assert path == tmp_path / "out/preprocessed/statistics.yaml"
    stats = load_statistics(path)
    assert stats["surface_pressure_count"] == 8
    assert stats["surface_pressure_mean"] == [2.5]
    assert stats["metadata"]["samples"] == ["param0/a", "param0/b"]


@pytest.mark.parametrize("case", ["empty_train", "missing_field"])
def test_invalid_stats_selection_fails(tmp_path, case):
    cfg, ctx = _stats_context(tmp_path, missing="absent" if case == "missing_field" else None)
    if case == "empty_train":
        cfg["pre"]["stats"]["train_params"] = []
    with pytest.raises(StageError, match="resolve_statistics"):
        build(cfg).run(ctx)
    assert not (tmp_path / "out/preprocessed/statistics.yaml").exists()


def test_dry_run_does_not_scan_old_statistics(tmp_path, monkeypatch):
    import ai4e_core.applications.aero_cfd.rawprep.stats as stats_module

    cfg, ctx = _stats_context(tmp_path, dry_run=True)

    def forbidden(*a, **kw):
        raise AssertionError("dry-run must not load old tensors")

    monkeypatch.setattr(stats_module, "load_named_tensor", forbidden)
    result = build(cfg).run(ctx)
    assert result["reports"]["statistics"]["status"] == "planned"
    assert not list((tmp_path / "out").rglob("*"))


def test_stream_moments_preserve_tail_dimensions():
    x = np.arange(24.0).reshape(2, 3, 4)
    moments = accumulate_moments(iter([x[:1], x[1:]]))
    assert moments["count"] == 2
    np.testing.assert_allclose(moments["mean"], x.mean(axis=0))
    np.testing.assert_allclose(moments["std"], x.std(axis=0))
    with pytest.raises(ValueError, match="尾维"):
        accumulate_moments(iter([x, np.ones((1, 4))]))


def test_enumerate_excludes_stable_ids(tmp_path):
    for p in ["param0/a", "param0/b", "param1/b"]:
        (tmp_path / p).mkdir(parents=True)
    assert enumerate_sample_relatives(tmp_path, param_count=2, exclude=["b"]) == [Path("param0/a")]


@pytest.mark.local_data
@pytest.mark.parametrize("sample_relative", SHAPENET_SAMPLES)
def test_materialize_real_shapenet_sample(shapenet_raw, sample_relative, tmp_path):
    if not (shapenet_raw / sample_relative / "quadpress_smpl.vtk").is_file():
        pytest.skip("本地样本不存在")
    cfg = load_config(CONFIG_PATH)
    cfg["dataset"]["root"] = str(shapenet_raw)
    cfg["pre"]["output"]["dir"] = str(tmp_path)
    result = build_sample(cfg).run({"config": cfg, "sample": sample_relative})["result"]
    assert len(list(Path(result["path"]).glob("*.pt"))) == 7
    assert result["filtered_validation"]["valid"]


@pytest.mark.parametrize("policy", ["error", "skip"])
def test_statistics_failed_training_sample_policy(tmp_path, policy):
    cfg, ctx = _stats_context(tmp_path)
    (tmp_path / "raw/param0/b/quadpress_smpl.vtk").unlink()
    ctx["continue_on_error"] = True
    cfg["pre"]["stats"]["missing"] = policy
    if policy == "error":
        with pytest.raises(StageError, match="resolve_statistics"):
            build(cfg).run(ctx)
        assert not (tmp_path / "out/preprocessed/statistics.yaml").exists()
    else:
        result = build(cfg).run(ctx)
        stats = load_statistics(result["statistics"])
        assert stats["surface_pressure_count"] == 4
        assert stats["metadata"]["excluded"][0]["sample"] == "param0/b"
        assert result["batch"]["failed"] == 1


@pytest.mark.parametrize(
    "enabled,domain,field",
    [
        (["nearest_vertex"], "volume", "nearest_distance"),
        (["mesh_signed_distance"], "volume", "signed_distance"),
        (["surface_normals"], "surface", "normals"),
        (["exterior_mask"], "volume", "exterior_mask"),
        ([], "surface", "points"),
    ],
)
def test_each_selected_ability_can_be_saved(tmp_path, enabled, domain, field):
    cfg = _sample_config(tmp_path / "raw")
    cfg["pre"]["geometry"]["enabled"] = enabled
    cfg["pre"]["filters"] = {}
    cfg["pre"]["surface"]["fields"] = {}
    cfg["pre"]["volume"]["fields"] = {}
    cfg["pre"]["output"].update(
        filemap={"chosen": "chosen.pt"},
        fields={"chosen": {"domain": domain, "field": field}},
        bundles={},
        optional=[],
    )
    result = _sample(tmp_path, config=cfg)
    assert result["names"] == ["chosen"]
    assert result["validation"]["valid"]


def test_surface_cell_field_has_own_identity_and_no_point_filter(tmp_path):
    raw = tmp_path / "raw"
    mesh = _surface_quad_with_unused_point()
    _add_field(mesh, [7.0], name="temperature", association="cell")
    _write_vtk(raw / "param0/a/surface.vtu.vtk", mesh)
    cfg = _sample_config(raw)
    del cfg["pre"]["volume"]
    cfg["source"]["files"] = [{"name": "mesh", "filename": "surface.vtu.vtk", "format": "vtk"}]
    cfg["pre"]["surface"].update(
        source="mesh",
        fields={"t": {"array": "temperature", "association": "cell", "kind": "scalar"}},
    )
    cfg["pre"]["geometry"]["enabled"] = []
    cfg["pre"]["filters"] = {"surface": ["mask"]}
    cfg["pre"]["output"].update(
        dir=str(tmp_path / "out"),
        filemap={"t": "t.pt"},
        fields={"t": {"domain": "surface", "field": "fields.t"}},
        bundles={},
        optional=[],
    )
    result = build_sample(cfg).run({"config": cfg, "sample": "param0/a"})["result"]
    assert load_named_tensor(Path(result["path"]) / "t.pt").tolist() == [7.0]
    assert result["counts"] == {"surface:cell": 1}


def test_disabled_abilities_are_not_called_in_recipe(tmp_path, monkeypatch):
    from ai4e_core.applications.aero_cfd.rawprep import derive

    def forbidden(*args, **kwargs):
        raise AssertionError("disabled ability executed")

    for name in [
        "nearest_vertex_distance_and_direction",
        "mesh_signed_distance",
        "surface_point_normals_with_mask",
        "exterior_mask",
    ]:
        monkeypatch.setattr(derive, name, forbidden)
    cfg = _sample_config(tmp_path / "raw")
    cfg["pre"]["geometry"]["enabled"] = []
    cfg["pre"]["filters"] = {}
    cfg["pre"]["output"].update(
        filemap={"xyz": "x.pt"},
        fields={"xyz": {"domain": "surface", "field": "points"}},
        bundles={},
        optional=[],
    )
    assert _sample(tmp_path, config=cfg)["written"]


def test_statistics_does_not_hold_all_loaded_samples(tmp_path, monkeypatch):
    import weakref

    from ai4e_core.applications.aero_cfd.rawprep import stats as stats_module

    cfg, ctx = _stats_context(tmp_path)
    for i in range(8):
        _write_fixture_sample(tmp_path / f"raw/param0/extra{i}")
    original = stats_module.load_named_tensor
    loaded = []

    def tracked(path):
        # 两个相邻样本允许在生成器交接时短暂共存，不允许整库保留。
        assert sum(ref() is not None for ref in loaded) <= 2
        tensor = original(path)
        loaded.append(weakref.ref(tensor))
        return tensor

    monkeypatch.setattr(stats_module, "load_named_tensor", tracked)
    result = build(cfg).run(ctx)
    assert load_statistics(result["statistics"])["surface_pressure_count"] == 40
