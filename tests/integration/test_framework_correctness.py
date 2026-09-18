"""输入诊断、提交账本与真实后处理故障注入，不以文件存在冒充完整成功。"""

import copy
import json
from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_contrib.ability.model.abupt.batch import collate
from ai4e_contrib.ability.model.abupt.inference import InferenceContext
from ai4e_contrib.ability.model.abupt.model import construct, predict
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core import run
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.applications.aero_cfd.infer import anchor_stage as stage
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.base.events import SAMPLE, phase, sample_context
from ai4e_core.run.training import TrainingRun
from ai4e_core.run.writer import RunWriter
from tests.integration.test_abupt_multidomain import make_model
from tests.integration.test_post_inference import _fit_then_post_config, _run_script
from tests.integration.test_post_mesh import _query_config
from tests.integration.test_train_recipe import prepared_case


@pytest.mark.parametrize(
    "value,message",
    [
        ([], "输入类型"),
        (torch.zeros(2, 3), "形状"),
        (torch.zeros(1, 3, dtype=torch.float64), "精度"),
        (torch.zeros(1, 3, device="meta"), "设备"),
        (torch.full((1, 3), float("nan")), "非有限"),
    ],
)
def test_tensor_diagnostic(value, message):
    with pytest.raises(ValueError, match=message) as caught:
        make_model()._tensor(value, (1, 3), "surface.coordinates")
    assert "surface.coordinates" in str(caught.value)
    if message != "非有限":
        assert "actual=" in str(caught.value)


@pytest.mark.parametrize(
    "device",
    [
        "cpu",
        pytest.param(
            "mps",
            marks=pytest.mark.skipif(
                not torch.backends.mps.is_available(), reason="需要真实 Apple GPU"
            ),
        ),
    ],
)
def test_move_preserves_index_mask_and_float_precision(device):
    values = {
        "coordinates": torch.ones(2, 3),
        "extra": (torch.tensor([0, 1]), torch.tensor([True, False])),
    }
    moved = to_device(values, device)
    assert moved["coordinates"].device.type == device
    assert moved["coordinates"].dtype == torch.float32
    assert isinstance(moved["extra"], tuple)
    assert [v.dtype for v in moved["extra"]] == [torch.int64, torch.bool]


def test_batch_error_identity_restores_context():
    items = [{"sample_id": "car-a", "index": 0}, {"sample_id": "car-b", "index": 1}]
    with phase("post"), pytest.raises(ValueError) as error, sample_context("predict", items):
        raise ValueError("bad input")
    assert error.value.dojo_context == {"stage": "post", "operation": "predict", "samples": items}
    assert SAMPLE.get() == ""


class RecordingRun:
    """用正式 writer 验证部分进度的磁盘交付。"""

    def __init__(self, path):
        self.writer = RunWriter.create(path, nested=False)
        self.summary = {}

    def report(self, value, **kwargs):
        self.summary = copy.deepcopy(value)

    def artifact(self, name, value):
        return self.writer.write_artifact(name, value)


def test_progress_write_error_does_not_replace_original(tmp_path, monkeypatch):
    target = RecordingRun(tmp_path)
    progress = PostProgress(target, {"evaluation": True, "predictions": True, "mesh": True})

    def broken(*args):
        raise OSError("journal disk full")

    with pytest.raises(ValueError, match="original"):
        try:
            with progress.operation("evaluation"):
                monkeypatch.setattr(target, "artifact", broken)
                raise ValueError("original")
        except Exception as exc:
            progress.finish(exc)
            raise
    assert target.summary["status"] == "failed"
    assert target.summary["operations"]["predictions"]["status"] == "pending"


@pytest.fixture
def trained(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    _query_config(cfg)
    cfg.post.evaluate = True
    cfg.post.save_predictions = True
    cfg.post.export_vtk = True
    cfg.paths.datasets.predictions = str(tmp_path / "post-output")
    return folder, cfg


def execute_post(folder, cfg, predictor=None):
    root = Path(cfg.run_root)
    before = set(root.iterdir())

    def execute(value):
        reference = OmegaConf.to_container(value, resolve=True)
        reference.pop("infer", None)  # 此处覆盖历史数值路径的失败交付。
        return stage.run(
            reference,
            TrainingRun(),
            construct=construct,
            predict=predictor or predict,
            prepare_inputs=prepare_inputs,
            collate=collate,
            context_factory=InferenceContext,
        )

    status = run.run_recipe(
        cfg,
        stages={"post": execute},
        only=["post"],
        script=folder / "post.py",
        resolver=apply_resolved,
    )
    (directory,) = set(root.iterdir()) - before
    summary = json.loads((directory / "summary.json").read_text())
    return status, directory, summary


@pytest.mark.parametrize("failure", ["evaluation", "tensor", "pointcloud", "surface", "volume"])
def test_post_failure_retains_completed_work(trained, monkeypatch, failure):
    from ai4e_core.applications.aero_cfd.infer import anchor_export as export
    from ai4e_core.applications.aero_cfd.infer import mesh

    folder, cfg = trained

    def broken(*args, **kwargs):
        raise OSError("injected failure")

    if failure == "evaluation":
        monkeypatch.setattr(stage, "evaluate_model", broken)
    elif failure == "tensor":
        monkeypatch.setattr(export, "write_tensor_file", broken)
    elif failure == "pointcloud":
        original = export.write_pointcloud

        def fail_compatibility_cloud(path, *args, **kwargs):
            if Path(path).parent.name == "vtk":
                raise OSError("injected failure")
            return original(path, *args, **kwargs)

        monkeypatch.setattr(export, "write_pointcloud", fail_compatibility_cloud)
    else:
        monkeypatch.setattr(mesh, f"write_{failure}_mesh", broken)
    status, directory, summary = execute_post(folder, cfg)
    report = summary["reports"]["post"]
    assert status == 1 and summary["failed"] and report["status"] == "failed"
    assert json.loads((directory / "artifacts/post-progress.json").read_text()) == report
    operations = report["operations"]
    if failure == "evaluation":
        assert operations["evaluation"]["status"] == "failed"
        assert operations["predictions"]["status"] == operations["mesh"]["status"] == "pending"
    elif failure in {"tensor", "pointcloud"}:
        assert operations["evaluation"]["status"] == "succeeded"
        assert operations["predictions"]["status"] == "failed"
        assert operations["predictions"]["completed"] == 0
        committed = operations["predictions"]["artifacts"]
        assert committed and all(Path(p).exists() for p in committed)
        assert operations["mesh"]["status"] == "pending"
        if failure == "pointcloud":
            assert any(p.endswith("sample_0000.pt") for p in committed)
    else:
        assert operations["predictions"]["status"] == "succeeded"
        assert report["predictions"]
        assert operations["mesh"]["status"] == "failed"
        assert operations["mesh"]["completed"] == 0
        assert operations["mesh"]["error"]["samples"][0]["index"] == 0
        assert operations["mesh"]["error"]["stage"] == "post"
        if failure == "volume":
            assert operations["mesh"]["artifacts"][0].endswith("_surface.vtp")


def test_query_only_does_not_rewrite_anchor_files(trained):
    from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint

    folder, cfg = trained
    cfg.post.query = False
    status, _, summary = execute_post(folder, cfg)
    assert status == 0
    files = [Path(record["packed"]) for record in summary["reports"]["post"]["predictions"]]
    hashes = [file_fingerprint(p) for p in files]
    cfg.post.query = True
    cfg.post.evaluate = cfg.post.save_predictions = cfg.post.export_vtk = False
    status, directory, summary = execute_post(folder, cfg)
    assert status == 0
    assert not (directory / "checkpoints").exists()
    assert hashes == [file_fingerprint(p) for p in files]
    assert summary["reports"]["post"]["operations"]["predictions"]["status"] == "skipped"
    status, _, summary = execute_post(folder, cfg)
    assert status == 1  # 默认覆盖保护，不静默替换


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="需要真实 Apple GPU")
def test_radius_fallback_matches_cpu():
    from torch_cluster import radius

    from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import _cluster_edges

    x = torch.arange(18, dtype=torch.float32).reshape(6, 3)
    y = x[[0, 2, 4]]
    bx, by = torch.zeros(6, dtype=torch.long), torch.zeros(3, dtype=torch.long)
    expected = _cluster_edges(radius, x, y, batch_x=bx, batch_y=by, r=6.0, max_num_neighbors=6)
    actual = _cluster_edges(
        radius,
        x.to("mps"),
        y.to("mps"),
        batch_x=bx.to("mps"),
        batch_y=by.to("mps"),
        r=6.0,
        max_num_neighbors=6,
    )
    assert actual.device.type == "mps"
    assert torch.equal(expected, actual.cpu())


def test_evaluation_forward_failure_has_batch_identity(trained):
    folder, cfg = trained

    def broken(*args):
        raise ValueError("forward failed")

    status, _, summary = execute_post(folder, cfg, predictor=broken)
    assert status == 1
    error = summary["reports"]["post"]["operations"]["evaluation"]["error"]
    assert error["samples"][0]["sample_id"]
    assert error["samples"][0]["index"] == 0
    assert error["stage"] == "post"


def test_generated_protocol_and_unknown_history_gate(trained, tmp_path, monkeypatch):
    import shutil
    from importlib import import_module

    folder, cfg = trained
    cfg.post.query = False
    status, directory, summary = execute_post(folder, cfg)
    assert status == 0
    protocol_path = directory / "artifacts/comparison-protocol.json"
    facts = json.loads(protocol_path.read_text())
    assert facts["execution"]["entrypoint"] == str((folder / "post.py").resolve())
    assert facts["initialization"] and facts["dataset"] and facts["source"]["entrypoint"]
    assert facts["inputs"]["predictions"] and facts["inputs"]["evaluation"]
    root = Path(cfg.paths.datasets.predictions)
    ref = tmp_path / "reference"
    destination = ref / "eval/predictions"
    destination.mkdir(parents=True)
    shutil.copytree(root / "vtk", destination / "vtk")
    for i, item in enumerate(summary["reports"]["post"]["predictions"]):
        bundle = torch.load(item["packed"], weights_only=True)
        bundle["surface_pressure"] += 100
        torch.save(bundle, destination / f"sample_{i:04d}.pt")
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "tools/verification"))
    compare = import_module("compare_post").compare
    output = tmp_path / "comparison.json"
    with pytest.raises(AssertionError):
        compare(Path(cfg.data_root) / "manifest.json", root, ref, output)
    result = json.loads(output.read_text())
    assert result["contract_passed"] and not result["passed"]
    assert result["eligibility"]["status"] == "not_comparable"
    assert "surface_pressure" not in result["max_abs"]
    with pytest.raises(AssertionError):
        compare(
            Path(cfg.data_root) / "manifest.json",
            root,
            ref,
            output,
            actual_protocol=protocol_path,
            reference_protocol=protocol_path,
        )
    result = json.loads(output.read_text())
    assert result["contract_passed"] and not result["passed"]
    assert result["max_abs"]["surface_pressure"] >= 99


def test_training_report_is_snapshot():
    from ai4e_core.run.session import CURRENT

    state = {}
    token = CURRENT.set(state)
    try:
        report = {"status": "running", "nested": {"completed": 1}}
        TrainingRun().report(report, stage="post")
        report["nested"]["completed"] = 99
        assert state["reports"]["post"]["nested"]["completed"] == 1
    finally:
        CURRENT.reset(token)


def test_training_step_failure_has_real_batch_identity(trained):
    from ai4e_contrib.ability.model.abupt.model import SOURCE
    from ai4e_core.applications.aero_cfd.train import fitting

    folder, cfg = trained
    root = Path(cfg.run_root)
    before = set(root.iterdir())

    def broken(*args):
        raise ValueError("training forward failed")

    def execute(value):
        return fitting.train(
            OmegaConf.to_container(value, resolve=True),
            TrainingRun(),
            factory=construct,
            predict=predict,
            prepare=prepare_inputs,
            collate=collate,
            source=SOURCE,
            step=broken,
        )

    status = run.run_recipe(
        cfg,
        stages={"train": execute},
        only=["train"],
        script=folder / "train.py",
        resolver=apply_resolved,
    )
    (directory,) = set(root.iterdir()) - before
    assert status == 1
    error_log = (directory / "logs/errors.log").read_text()
    assert "training forward failed" in error_log
    assert "训练计算" in error_log and "sample_id" in error_log and "index" in error_log
    assert "阶段=train" in error_log
