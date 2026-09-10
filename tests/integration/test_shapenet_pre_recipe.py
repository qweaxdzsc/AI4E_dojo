"""案例前处理入口、阶段盒子与 run 开车记录。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from vtkmodules.util.vtkConstants import VTK_HEXAHEDRON, VTK_QUAD
from vtkmodules.vtkCommonCore import vtkDoubleArray, vtkFloatArray, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter

from ai4e_core.abilities.data.save import load_named_tensors
from ai4e_core.applications.aero_cfd.rawprep import discover_samples
from ai4e_core.applications.aero_cfd.rawprep.save import sample_destination
from ai4e_core.applications.base import Pipeline, Stage, StageError
from ai4e_core.base.config import load_config
from ai4e_core.run import run_from_config
from tests.recipe_assets import CONFIG_PATH, RECIPE_DIR, STATS_PATH
from tests.legacy_pre import build
from tests.support import SHAPENET_SAMPLES, shapenet_raw_root

REQUIRED_LIBRARY_FIELDS = (
    "surface_pressure",
    "surface_position",
    "surface_normals",
    "volume_velocity",
    "volume_position",
    "volume_sdf",
    "volume_normals",
)


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


def _surface_quad() -> vtkUnstructuredGrid:
    """四个点组成一个 quad。"""
    grid = vtkUnstructuredGrid()
    points = vtkPoints()
    for point in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)):
        points.InsertNextPoint(point)
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_QUAD, 4, [0, 1, 2, 3])
    _with_scalars(grid, [1.0, 2.0, 3.0, 4.0])
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


def _write_vtk(path: Path, grid: vtkUnstructuredGrid) -> None:
    """写出一份 Legacy VTK 网格。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtkUnstructuredGridWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(grid)
    writer.Write()


def _write_sample(sample_dir: Path) -> None:
    """写出表面四边形和体积六面体夹具。"""
    _write_vtk(sample_dir / "quadpress_smpl.vtk", _surface_quad())
    _write_vtk(sample_dir / "hexvelo_smpl.vtk", _volume_hex())


def _fixture_root(tmp_path: Path) -> Path:
    """三样本原始树。"""
    root = tmp_path / "training_data"
    for name in ("s1", "s2", "s3"):
        _write_sample(root / "param0" / name)
    return root


def _recipe_overrides(tmp_path: Path, raw_root: Path) -> dict[str, object]:
    """指向临时夹具，不写本机默认路径。"""
    return {
        "dataset.root": str(raw_root),
        "pre.output.dir": str(tmp_path / "out"),
        "pre.surface.fields.pressure.array": "pressure",
        "pre.volume.fields.velocity.array": "velocity",
        "pre.discover.param_count": 1,
        "pre.discover.exclude": [],
        "pre.discover.expected_total": 3,
        "pipeline.stages": ["pre"],
    }


def _run_recipe(tmp_path: Path, *, dry_run: bool = False, extra: dict | None = None):
    """走案例入口开车。"""
    raw_root = _fixture_root(tmp_path)
    overrides = _recipe_overrides(tmp_path, raw_root)
    if extra:
        overrides.update(extra)
    return run_from_config(
        CONFIG_PATH,
        builders={"pre": build},
        overrides=overrides,
        run_root=tmp_path,
        recipe_dir=RECIPE_DIR,
        dry_run=dry_run,
        overwrite=True,
    )


def _run_pts(path: Path) -> list[Path]:
    """运行目录里的训练张量。"""
    return list(path.rglob("*.pt"))


def test_recipe_writes_tensors_and_run_record(tmp_path: Path) -> None:
    ctx = _run_recipe(tmp_path)

    out = tmp_path / "out" / "preprocessed"
    sample = out / "param0" / "s1"
    assert (sample / "surface_pressure.pt").is_file()
    assert (sample / "surface_points.pt").is_file()
    assert (sample / "volume_velocity.pt").is_file()
    assert (sample / "volume_points.pt").is_file()
    assert ctx["summary"]["success"] == 3
    assert ctx["summary"]["failed_count"] == 0
    assert Path(ctx["statistics"]) == STATS_PATH
    run_dir = Path(ctx["run_dir"])
    assert (run_dir / "inputs" / "config.yaml").is_file()
    assert (run_dir / "logs" / "run.log").is_file()
    assert (run_dir / "summary.json").is_file()
    assert not _run_pts(run_dir)


def test_recipe_dry_run_keeps_names_without_pt(tmp_path: Path) -> None:
    ctx = _run_recipe(tmp_path, dry_run=True)

    assert not list((tmp_path / "out").rglob("*.pt"))
    assert ctx["summary"]["names"]
    assert "surface_pressure" in ctx["summary"]["names"]
    assert "volume_velocity" in ctx["summary"]["names"]
    assert not _run_pts(Path(ctx["run_dir"]))


def test_override_dataset_root_enters_resolved_and_log(tmp_path: Path) -> None:
    raw_root = _fixture_root(tmp_path)
    other = tmp_path / "other_root"
    other.mkdir()
    for child in (raw_root / "param0").iterdir():
        target = other / "param0" / child.name
        target.mkdir(parents=True, exist_ok=True)
        for vtk in child.iterdir():
            target.joinpath(vtk.name).write_bytes(vtk.read_bytes())
    ctx = run_from_config(
        CONFIG_PATH,
        builders={"pre": build},
        overrides={
            **_recipe_overrides(tmp_path, raw_root),
            "dataset.root": str(other),
        },
        run_root=tmp_path,
        recipe_dir=RECIPE_DIR,
        dry_run=True,
        overwrite=True,
    )

    resolved = (Path(ctx["run_dir"]) / "inputs" / "config.yaml").read_text(encoding="utf-8")
    log = (Path(ctx["run_dir"]) / "logs" / "run.log").read_text(encoding="utf-8")
    assert str(other) in resolved
    assert str(other) in ctx["config"]["dataset"]["root"]
    assert str(other) in log


def test_run_directory_has_config_log_and_no_tensors(tmp_path: Path) -> None:
    ctx = _run_recipe(tmp_path, dry_run=True)
    run_dir = Path(ctx["run_dir"])
    assert (run_dir / "inputs" / "config.yaml").is_file()
    assert (run_dir / "inputs" / "config.yaml").is_file()
    assert (run_dir / "logs" / "run.log").is_file()
    assert not _run_pts(run_dir)


def test_pipeline_runs_only_declared_pre_stage() -> None:
    seen: list[str] = []

    def pre(_cfg):
        def mark(ctx):
            seen.append("pre")
            return ctx

        return Stage(name="pre", steps=[mark])

    def train(_cfg):
        def mark(ctx):
            seen.append("train")
            return ctx

        return Stage(name="train", steps=[mark])

    pipeline = Pipeline.from_config(
        {"pipeline": {"stages": ["pre"]}},
        {"pre": pre, "train": train},
    )
    pipeline.run({})
    assert seen == ["pre"]


def test_stage_stops_on_second_step_and_summary_names_it(tmp_path: Path) -> None:
    def first(ctx):
        ctx["seen"] = ["first"]
        return ctx

    def boom(_ctx):
        raise ValueError("第二步炸了")

    def third(ctx):
        ctx["seen"].append("third")
        return ctx

    def failing(_cfg):
        return Stage(name="pre", steps=[first, boom, third])

    with pytest.raises(StageError, match="boom") as caught:
        run_from_config(
            CONFIG_PATH,
            builders={"pre": failing},
            overrides={
                "dataset.root": str(tmp_path / "unused"),
                "pre.output.dir": str(tmp_path / "out"),
                "pipeline.stages": ["pre"],
            },
            run_root=tmp_path,
            recipe_dir=RECIPE_DIR,
        )

    assert caught.value.step_name == "boom"
    run_dir = next((tmp_path / "runs").iterdir())
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == "boom"
    assert summary["stage"] == "pre"
    assert summary["failed"] is True


def test_load_config_dotted_override_is_roundtrippable(tmp_path: Path) -> None:
    loaded = load_config(CONFIG_PATH, overrides={"dataset.root": str(tmp_path / "alt")})
    assert loaded["dataset"]["root"] == str(tmp_path / "alt")
    assert loaded["pipeline"]["stages"] == ["pre"]


@pytest.mark.local_data
def test_local_shapenet_one_sample_via_recipe(tmp_path: Path) -> None:
    raw = shapenet_raw_root()
    sample = raw / SHAPENET_SAMPLES[0]
    if not sample.is_dir():
        pytest.skip(f"本地 ShapeNet 样本不存在: {sample}")
    dest_root = tmp_path / "training_data"
    link = dest_root / SHAPENET_SAMPLES[0]
    link.parent.mkdir(parents=True)
    link.symlink_to(sample)
    ctx = run_from_config(
        CONFIG_PATH,
        builders={"pre": build},
        overrides={
            "dataset.root": str(dest_root),
            "pre.output.dir": str(tmp_path / "out"),
            "pre.discover.param_count": 1,
            "pre.discover.exclude": [],
            "pre.discover.expected_total": 1,
        },
        run_root=tmp_path,
        recipe_dir=RECIPE_DIR,
        dry_run=True,
        overwrite=True,
    )
    assert ctx["summary"]["success"] == 1
    assert not list((tmp_path / "out").rglob("*.pt"))
    assert ctx["summary"]["names"]


@pytest.mark.local_data
def test_local_shapenet_full_library_via_recipe() -> None:
    """整库 889：走案例配置发现，核对每个样本的对照表点场。"""
    config = load_config(CONFIG_PATH)
    raw = Path(str(config["dataset"]["root"]))
    if not raw.is_dir():
        pytest.skip(f"本地 ShapeNet 原始树不存在: {raw}")
    ctx = discover_samples({"config": config})
    items = ctx["items"]
    assert len(items) == 889
    output = config["pre"]["output"]
    filemap = output["filemap"]
    optional = list(output.get("optional") or [])
    missing: list[str] = []
    for sample in items:
        dest = sample_destination(config, sample)
        try:
            loaded = load_named_tensors(dest, filemap, optional=optional)
        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            missing.append(f"{sample}: {exc}")
            continue
        absent = [name for name in REQUIRED_LIBRARY_FIELDS if name not in loaded]
        if absent:
            missing.append(f"{sample}: 缺少 {absent}")
    assert missing == []


@pytest.mark.parametrize("continue_on_error", [False, True])
def test_sample_failure_propagates_with_partial_summary(tmp_path, continue_on_error):
    from ai4e_core.run import BatchExecutionError

    raw = _fixture_root(tmp_path)
    (raw / "param0/s2/quadpress_smpl.vtk").unlink()
    arguments = {
        "builders": {"pre": build},
        "overrides": _recipe_overrides(tmp_path, raw),
        "run_root": tmp_path,
        "recipe_dir": RECIPE_DIR,
        "continue_on_error": continue_on_error,
    }
    if continue_on_error:
        ctx = run_from_config(CONFIG_PATH, **arguments)
        summary = ctx["summary"]
        assert summary["success"] == 2
        assert summary["unexecuted"] == 0
    else:
        with pytest.raises(StageError) as caught:
            run_from_config(CONFIG_PATH, **arguments)
        assert isinstance(caught.value.cause, BatchExecutionError)
        summary = json.loads(next((tmp_path / "runs").glob("*/summary.json")).read_text())
        assert summary["success"] == 1
        assert summary["unexecuted"] == 1
        assert "statistics" not in summary["reports"]
    assert summary["failed"] is True and summary["failed_count"] == 1
    failure = summary["failures"][0]
    assert failure["sample"] == "param0/s2"
    assert failure["step"] == "dataread"
    assert summary["attempted"] == (3 if continue_on_error else 2)
    assert (tmp_path / "out/preprocessed/param0/s1/surface_points.pt").exists()


def test_generic_runner_has_no_pre_requirement(tmp_path):
    config = tmp_path / "minimal.yaml"
    config.write_text("pipeline:\n  stages: [custom]\n")

    def custom(cfg):
        def report(ctx):
            ctx["reports"] = {"custom": {"answer": 42}}
            return ctx

        return Stage("custom", [report])

    ctx = run_from_config(config, builders={"custom": custom}, run_root=tmp_path)
    assert ctx["summary"]["reports"]["custom"]["answer"] == 42


def test_recipe_shows_named_business_steps():
    from functools import partial

    from tests.legacy_pre import build_sample

    stage = build_sample(load_config(CONFIG_PATH))
    names = [(s.func if isinstance(s, partial) else s).__name__ for s in stage.steps]
    assert names == [
        "dataread",
        "extract_fields",
        "derive_geometry",
        "select_fields",
        "validate_fields",
        "filter_points",
        "tensorize",
        "write_tensors",
    ]


def test_duplicate_sample_targets_rejected_before_read(tmp_path):
    raw = _fixture_root(tmp_path)
    with pytest.raises(StageError, match="discover_samples"):
        run_from_config(
            CONFIG_PATH,
            builders={"pre": build},
            overrides={
                **_recipe_overrides(tmp_path, raw),
                "pre.discover.expected_total": None,
                "pre.discover.samples": ["param0/s1", "param0/./s1"],
            },
            run_root=tmp_path,
            recipe_dir=RECIPE_DIR,
        )
    assert not list((tmp_path / "out").rglob("*.pt"))
