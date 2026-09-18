"""公共研究约定的执行证据，不依赖某个模型的任务描述。"""

import json
from pathlib import Path

import pytest

from ai4e_core import run
from ai4e_core.base.config.conventions import (
    load_recipe_config,
    normalize_recipe_config,
    require_current_keys,
    resolve_input,
)
from ai4e_core.run.session import run_recipe


def test_public_paths_overrides_and_invalid_inputs(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    config.write_text("run_root: runs\ndata_root: data\npipeline:\n  stages: [train]\ninputs:\n  train:\n    preparation: prepared.json\n")
    monkeypatch.chdir(tmp_path.parent)
    value = load_recipe_config(config, ["inputs.train.resume=weights.pt"])
    assert value["inputs"]["train"]["preparation"] == str(tmp_path / "prepared.json")
    assert value["inputs"]["train"]["resume"] == str(tmp_path / "weights.pt")
    with pytest.raises(TypeError, match="路径或 null"):
        normalize_recipe_config({"inputs": {"train": {"resume": {"fluid": "a.pt"}}}}, base=tmp_path)
    with pytest.raises(ValueError, match="旧配置键"):
        require_current_keys({"train": {"resume": None}, "inputs": {}}, {"train.resume": "inputs.train.resume"})
    with pytest.raises(ValueError, match="输入冲突"):
        resolve_input("a.json", "b.json", name="prepared")


def test_inference_preparation_owns_source_without_mutating_training():
    from ai4e_core.applications.aero_cfd.infer.configuration import inference_parameters

    cfg = {"infer": {"preparation": "chosen.json"},
           "train": {"manifest": "other-stage.json", "preparation": "training.json"}}
    value = inference_parameters(cfg)
    assert value["train"]["manifest"] is None
    assert value["train"]["preparation"] == "chosen.json"
    assert cfg["train"] == {"manifest": "other-stage.json", "preparation": "training.json"}


def test_imported_physical_manifest_overrides_selected_path(tmp_path):
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.trainprep.physical import open_dataset

    prepared = tmp_path / "prepared.json"
    prepared.write_text(json.dumps({"version": 1, "dataset": "fixed",
                                    "manifest": str(tmp_path / "original.json")}))
    view = SimpleNamespace(partitions={"train": ["s"]})
    data = open_dataset(
        {"train": {"manifest": str(tmp_path / "missing.json")}},
        SimpleNamespace(open_physical=lambda _cfg: view),
        object(),
        reference=prepared,
    )
    assert data.config["train"]["manifest"] == str(tmp_path / "original.json")
    assert data.view is view


def test_stage_outputs_assets_metrics_and_readback(tmp_path):
    code = tmp_path / "recipe"
    code.mkdir()
    script = code / "pipeline.py"
    script.write_text("# provenance\n")
    cfg = {"run_root": str(tmp_path / "runs"), "data_root": str(tmp_path / "data"),
           "pipeline": {"stages": ["infer", "post"]}}
    captured = {}

    def infer(cfg):
        session = run.TrainingRun()
        path = session.output_dir("infer") / "prediction.json"
        path.write_text('[3, 4]')
        session.record_asset("prediction", path, kind="other", stage="infer")
        return path

    def post(cfg, source):
        session = run.TrainingRun()
        assert json.loads(source.read_text()) == [3, 4]
        path = session.output_dir("post") / "magnitude.json"
        path.write_text('5')
        session.record_asset("magnitude", path, kind="other", stage="post", dependencies=[source])
        session.record_metric("magnitude", 5.0, stage="post", assets=[path], semantics={
            "field": "velocity", "unit": "m/s", "split": "test", "statistic": "norm",
            "data_identity": "fixed_sample_0",
        })
        captured["run"] = session.run_dir
        captured["data"] = session.data_dir

    def pipeline(cfg):
        source = run.stage("infer", infer, cfg)
        run.stage("post", post, cfg, source)

    assert run_recipe(cfg, stages=pipeline, script=script) == 0
    summary = json.loads((captured["run"] / "summary.json").read_text())
    assert summary["research_status"] == "completed"
    assert [item["stage"] for item in summary["stage_events"]] == ["infer", "post"]
    assert captured["data"].parent == tmp_path / "data"
    assets = json.loads((captured["run"] / "artifacts/assets.json").read_text())["items"]
    assert len(assets["post/magnitude"]["dependency_digests"]) == 1
    metrics = json.loads((captured["run"] / "artifacts/metrics.json").read_text())["items"]
    assert metrics["post/magnitude"]["value"] == 5


def test_missing_stage_is_not_research_completion(tmp_path):
    cfg = {"run_root": str(tmp_path / "runs"), "pipeline": {"stages": ["infer"]}}
    script = tmp_path / "recipe/pipeline.py"
    script.parent.mkdir()
    script.write_text("")
    assert run_recipe(cfg, stages=lambda cfg: None, script=script) == 0
    summary = json.loads(next((tmp_path / "runs").glob("*/summary.json")).read_text())
    assert summary["research_status"] == "incomplete"
    assert summary["unverified_stages"] == ["infer"]


def test_metric_requires_semantics_and_real_asset(tmp_path):
    from ai4e_core.run.writer import RunWriter
    writer = RunWriter.create(tmp_path)
    path = tmp_path / "data.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="metric_semantics_required"):
        writer.record_metric("error", 1.0, stage="post", semantics={}, assets=[path])
    with pytest.raises(FileNotFoundError):
        writer.record_asset("absent", tmp_path / "absent", kind="other", stage="post")


def test_aero_public_inputs_preserve_domain_defaults(tmp_path):
    from omegaconf import OmegaConf

    from ai4e_contrib.application.aero_cfd.configuration import (
        application_parameters,
        load_configuration,
    )

    root = Path(__file__).resolve().parents[2]
    for path in (root / "examples/aero_cfd").glob("*/config.yaml"):
        config = load_configuration(path)
        domain = application_parameters(config)
        assert domain["model"]["initial_weights"] is None
        assert "statistics" not in domain["normalization"]
        if "shapenet" in path.parent.name:
            assert domain["dataset"]["partition"] == "official"
            assert config.inputs.trainprep.partition is None
    user = OmegaConf.to_container(config, resolve=True)
    user["dataset"]["partitions"] = {"train": ["a"], "test": ["b"]}
    user["inputs"]["trainprep"]["partition"] = str(tmp_path / "partition.yaml")
    with pytest.raises(ValueError, match="不能同时"):
        application_parameters(user)


def test_asset_dependency_content_is_required(tmp_path):
    from ai4e_core.run.indexes import validate_asset_content
    from ai4e_core.run.writer import RunWriter

    writer = RunWriter.create(tmp_path / "runs")
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}")
    array = tmp_path / "array.bin"
    array.write_bytes(b"original")
    writer.record_asset("dataset", manifest, kind="dataset", stage="rawprep", dependencies=[array])
    item = json.loads((writer.run_dir / "artifacts/assets.json").read_text())["items"]["rawprep/dataset"]
    validate_asset_content(item)
    array.write_bytes(b"changed")
    with pytest.raises(ValueError, match="asset_content_changed"):
        validate_asset_content(item)
    item["dependency_digests"] = {}
    with pytest.raises(ValueError, match="incomplete"):
        validate_asset_content(item)


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_coupled_iteration_slice_rejects_invalid_before_reading_data(value):
    from ai4e_core.applications.coupled_physics.train import train_field

    with pytest.raises(ValueError, match="updates_per_run"):
        train_field({"updates": 3, "batch_size": 1, "updates_per_run": value}, "/missing",
                    field="field", construct=None, reader=None, objective=None, session=None)
