"""训练准备：选定 AB-UPT、官方分片与按对照表读盘。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch
import yaml

from ai4e_core.abilities.data.source.split import (
    load_split_expected,
    load_split_lists,
    require_split_counts,
)
from ai4e_core.applications.aero_cfd.train import (
    open_preprocessed_sample,
    resolve_preprocessed_root,
    standard,
)
from ai4e_core.applications.aero_cfd.trainprep.dataset import read_probe_stage as train_build
from ai4e_core.applications.base import Pipeline, StageError
from ai4e_core.base.config import load_config
from ai4e_core.run import run_from_config
from tests.legacy_pre import build as pre_build
from tests.recipe_assets import CONFIG_PATH, RECIPE_DIR, SPLITS_PATH
from tests.support import shapenet_processed_root

OFFICIAL_TEST0 = "param0/100715345ee54d7ae38b52b4ee9d36a3"
DISK_KEYS = (
    "surface_pressure",
    "surface_position",
    "surface_normals",
    "volume_velocity",
    "volume_position",
    "volume_sdf",
    "volume_normals",
)
FILEMAP = {
    "surface_pressure": "surface_pressure.pt",
    "surface_position": "surface_points.pt",
    "surface_normals": "surface_normals.pt",
    "volume_velocity": "volume_velocity.pt",
    "volume_position": "volume_points.pt",
    "volume_sdf": "volume_sdf.pt",
    "volume_normals": "volume_normals.pt",
}
DEFAULT_FILEMAP = {**FILEMAP, "cell": "cell.pt"}
FORBIDDEN_KEYS = ("friction", "area")


def _tensor(shape: tuple[int, ...]) -> torch.Tensor:
    """生成可复现的 float32 张量。"""
    size = 1
    for dim in shape:
        size *= dim
    return torch.arange(size, dtype=torch.float32).reshape(shape)


def _write_sample(
    sample_dir: Path,
    *,
    pressure_1d: bool = False,
    volume_sdf_1d: bool = False,
    missing: str | None = None,
    extra_filemap: dict[str, str] | None = None,
) -> None:
    """写出对照表磁盘场，默认不含表面距离文件。"""
    sample_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "surface_pressure": _tensor((4,) if pressure_1d else (4, 1)),
        "surface_position": _tensor((4, 3)),
        "surface_normals": _tensor((4, 3)),
        "volume_velocity": _tensor((8, 3)),
        "volume_position": _tensor((8, 3)),
        "volume_sdf": _tensor((8,) if volume_sdf_1d else (8, 1)),
        "volume_normals": _tensor((8, 3)),
    }
    filemap = dict(FILEMAP)
    if extra_filemap:
        filemap.update(extra_filemap)
    for name, filename in filemap.items():
        if name == missing or name not in payloads:
            continue
        torch.save(payloads[name], sample_dir / filename)


def _write_splits(path: Path) -> None:
    """写出夹具 train 2 / test 1 名单。"""
    path.write_text(
        yaml.safe_dump(
            {
                "expected": {"train": 2, "test": 1},
                "train": ["param0/s1", "param0/s2"],
                "test": ["param0/s3"],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _fixture_library(tmp_path: Path, *, pressure_1d: bool = True) -> Path:
    """三样本预处理库，写出根停在数据根。"""
    data_root = tmp_path / "out"
    processed = data_root / "preprocessed"
    for name in ("s1", "s2", "s3"):
        _write_sample(processed / "param0" / name, pressure_1d=pressure_1d, volume_sdf_1d=True)
    return data_root


def _builders() -> dict:
    """同时注册 pre 与 train。"""
    return {"pre": pre_build, "train": train_build}


def _train_overrides(tmp_path: Path, data_root: Path, splits: Path) -> dict[str, object]:
    """只开 train，指向夹具库与名单。"""
    return {
        "pipeline.stages": ["train"],
        "pre.output.dir": str(data_root),
        "train.splits": str(splits),
    }


def _run_train(tmp_path: Path, extra: dict | None = None):
    """走案例开车，只开 train。"""
    data_root = _fixture_library(tmp_path)
    splits = tmp_path / "splits.yaml"
    _write_splits(splits)
    overrides = _train_overrides(tmp_path, data_root, splits)
    if extra:
        overrides.update(extra)
    return run_from_config(
        CONFIG_PATH,
        builders=_builders(),
        overrides=overrides,
        run_root=tmp_path,
        recipe_dir=RECIPE_DIR,
    )


def test_train_stage_uses_writer_run_dir_and_selects_abupt(tmp_path: Path) -> None:
    ctx = _run_train(tmp_path)

    run_dir = Path(ctx["run_dir"])
    assert run_dir.is_dir()
    assert run_dir.parent.name == "runs"
    assert ctx["model"] == "ab_upt"
    assert ctx["summary"]["reports"]["train"]["model"] == "ab_upt"
    assert run_dir == Path(ctx["summary"]["run_dir"])


def test_unknown_model_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(StageError) as caught:
        _run_train(tmp_path, extra={"train.model": "other_model"})
    assert caught.value.stage == "train"
    assert caught.value.step_name == "select_abupt_step"
    assert "AB-UPT" in str(caught.value.cause)


def test_default_stages_still_construct_only_pre() -> None:
    config = load_config(CONFIG_PATH)
    pipeline = Pipeline.from_config(config, _builders())
    assert [stage.name for stage in pipeline.stages] == ["pre"]


def test_output_root_appends_preprocessed_and_missing_fails(tmp_path: Path) -> None:
    data_root = tmp_path / "dataset"
    processed = data_root / "preprocessed"
    processed.mkdir(parents=True)
    assert resolve_preprocessed_root(data_root) == processed
    assert resolve_preprocessed_root(processed) == processed
    with pytest.raises(FileNotFoundError, match="preprocessed"):
        resolve_preprocessed_root(tmp_path / "missing")


def test_official_split_counts_and_first_test() -> None:
    splits = load_split_lists(SPLITS_PATH)
    expected = load_split_expected(SPLITS_PATH)
    require_split_counts(splits, expected)
    assert expected == {"train": 789, "test": 100}
    assert len(splits["train"]) == 789
    assert len(splits["test"]) == 100
    assert splits["test"][0] == OFFICIAL_TEST0


def test_missing_required_file_reports_full_path(tmp_path: Path) -> None:
    sample = tmp_path / "param0" / "s1"
    _write_sample(sample, missing="surface_pressure")
    with pytest.raises(RuntimeError, match=str(sample / "surface_pressure.pt")):
        open_preprocessed_sample(sample, FILEMAP)


def test_surface_sdf_is_on_the_fly_zeros(tmp_path: Path) -> None:
    sample = tmp_path / "param0" / "s1"
    _write_sample(sample)
    fields = open_preprocessed_sample(sample, FILEMAP)
    assert fields["surface_sdf"].shape == (4, 1)
    assert torch.equal(fields["surface_sdf"], torch.zeros(4, 1))
    assert not (sample / "surface_sdf.pt").exists()


def test_one_dimensional_pressure_becomes_column(tmp_path: Path) -> None:
    sample = tmp_path / "param0" / "s1"
    _write_sample(sample, pressure_1d=True, volume_sdf_1d=True)
    fields = open_preprocessed_sample(sample, FILEMAP)
    assert fields["surface_pressure"].shape == (4, 1)
    assert fields["volume_sdf"].shape == (8, 1)


def test_optional_cell_is_skipped_and_extra_fields_unread(tmp_path: Path) -> None:
    sample = tmp_path / "param0" / "s1"
    _write_sample(sample)
    torch.save(torch.ones(4, 1), sample / "friction.pt")
    filemap = dict(DEFAULT_FILEMAP)
    filemap["friction"] = "friction.pt"
    fields = open_preprocessed_sample(sample, {k: filemap[k] for k in (*DISK_KEYS, "cell")})
    assert "cell" not in fields
    assert "friction" not in fields
    assert "area" not in fields
    for key in FORBIDDEN_KEYS:
        assert key not in fields


def test_full_drive_reads_probe_without_run_tensors(tmp_path: Path) -> None:
    ctx = _run_train(tmp_path)

    assert "placeholders" not in ctx
    assert "trainer" not in ctx
    assert ctx["model"] == "ab_upt"
    assert isinstance(ctx["sample"], dict)
    assert "surface_sdf" in ctx["sample"]
    assert ctx["sample_id"] == "param0/s3"
    assert ctx["split_counts"] == {"train": 2, "test": 1}
    run_dir = Path(ctx["run_dir"])
    assert (run_dir / "inputs" / "config.yaml").is_file()
    assert (run_dir / "summary.json").is_file()
    assert list(run_dir.rglob("*.pt")) == []
    assert len(list((tmp_path / "runs").iterdir())) == 1


def test_read_probe_contains_no_training_placeholders():
    stage = standard({})
    assert [step.__name__ for step in stage.steps] == [
        "select_abupt_step",
        "open_splits_step",
        "read_probe_sample_step",
    ]


def test_summary_copies_probe_fields(tmp_path: Path) -> None:
    ctx = _run_train(tmp_path)
    summary = json.loads((Path(ctx["run_dir"]) / "summary.json").read_text(encoding="utf-8"))
    summary = summary["reports"]["train"]
    assert summary["model"] == "ab_upt"
    assert summary["split_counts"] == {"train": 2, "test": 1}
    assert "surface_pressure" in summary["names"]
    assert "surface_sdf" in summary["names"]
    assert "sample" not in summary


@pytest.mark.local_data
def test_local_official_test0_field_shapes() -> None:
    root = shapenet_processed_root()
    try:
        processed = resolve_preprocessed_root(root)
    except FileNotFoundError:
        pytest.skip(f"本地预处理目录不存在: {root}")
    sample = processed / OFFICIAL_TEST0
    if not sample.is_dir():
        pytest.skip(f"本地官方 test 第 0 个不存在: {sample}")
    fields = open_preprocessed_sample(sample, DEFAULT_FILEMAP)
    assert set(DISK_KEYS).issubset(fields)
    assert fields["surface_pressure"].ndim == 2
    assert fields["surface_pressure"].shape[1] == 1
    assert fields["volume_sdf"].ndim == 2
    assert fields["volume_sdf"].shape[1] == 1
    assert fields["surface_sdf"].shape[1] == 1
    assert torch.equal(fields["surface_sdf"], torch.zeros_like(fields["surface_sdf"]))
    assert fields["surface_sdf"].shape[0] == fields["surface_position"].shape[0]
    assert "friction" not in fields
    assert "area" not in fields


def test_manifest_index_parses_once_and_reads_on_demand(tmp_path, monkeypatch):
    from ai4e_core.abilities.data.source import manifest as module
    from tests.integration.test_dataset_recipe import execute_case, setup_case

    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg) == 0
    calls = []
    original = module.load_named_tensors
    monkeypatch.setattr(
        module, "load_named_tensors", lambda *a, **kw: (calls.append(a[0]), original(*a, **kw))[1]
    )
    index = module.ManifestIndex(Path(cfg.paths.datasets.root) / "manifest.json")
    assert not calls
    for _ in range(2):
        assert index.read("train")["surface_pressure"].numel() == 4
    assert len(calls) == 2 and calls[0] == calls[1]
    record = index.records[("train", "a")]
    record["fields"]["surface_pressure"]["state"] = "normalized"
    with pytest.raises(ValueError, match="清单"):
        index.read("train")
    record["fields"]["surface_pressure"]["state"] = "physical"
    record["fields"]["surface_pressure"]["shape"] = [999]
    with pytest.raises(ValueError, match="清单"):
        index.read("train")
