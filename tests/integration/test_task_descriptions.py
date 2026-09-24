"""真实应用声明、来源固定与跨领域标签匹配。"""

from pathlib import Path

import pytest
from ai4e_task.tasks.asset_matching import match_asset
from ai4e_task.tasks.descriptions import describe_recipe, described_entry
from ai4e_task.tasks.operation_sources import capture_source, invoke_source
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]


def test_run_handoff_keeps_scientific_summary_in_fixed_file(tmp_path):
    """未评价的无穷占位不阻断目录检查，Task 不将其伪装为有效指标。"""
    import json

    recipe = tmp_path / "recipe"
    recipe.mkdir()
    OmegaConf.save({"components": {"application": "custom"}}, recipe / "config.yaml")
    (recipe / "custom.py").write_text(
        "import json, math\nfrom pathlib import Path\n"
        "def inspect(request):\n"
        "    run = request['run']\n"
        "    data = json.loads((Path(run['run_dir']) / 'summary.json').read_text())\n"
        "    return {'embedded': 'summary' in run or 'lineage' in run, "
        "'unavailable': math.isinf(data['best']), 'id': run['id']}\n"
    )
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    summary = {"best": float("inf")}
    raw = json.dumps(summary)
    (run_dir / "summary.json").write_text(raw)
    source = capture_source(recipe, "inspect")
    request = {
        "run": {
            "id": "one",
            "run_dir": str(run_dir),
            "summary": summary,
            "lineage": {"run_id": "one"},
        }
    }
    assert invoke_source(source, recipe, request) == {
        "embedded": False,
        "unavailable": True,
        "id": "one",
    }
    assert request["run"]["summary"] == summary
    assert (run_dir / "summary.json").read_text() == raw


def test_rawprep_cache_includes_external_application_revision(tmp_path, monkeypatch):
    """配置不变时，当前应用依赖变更也会刷新原始处理描述。"""
    import os

    import ai4e_task as task

    from tests.integration.test_task_management import recipe

    source = recipe(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    dependency = external / "rawprep_settings.py"
    dependency.write_text("WORKERS = 1\n")
    (source / "custom_app.py").write_text(
        "from rawprep_settings import WORKERS\n"
        "def inspect(request):\n    return {'rawprep': {'workers': WORKERS}}\n"
    )
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.components = {"application": "custom_app"}
    OmegaConf.save(cfg, source / "config.yaml")
    monkeypatch.setenv("PYTHONPATH", str(external) + os.pathsep + os.environ.get("PYTHONPATH", ""))
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "description", source=source)
    before = task.read_configuration(project, item["id"])
    assert task.describe_rawprep(project, item["id"])["rawprep"]["workers"] == 1
    dependency.write_text("WORKERS = 2\n")
    assert task.describe_rawprep(project, item["id"])["rawprep"]["workers"] == 2
    assert task.read_configuration(project, item["id"]) == before


def test_two_applications_describe_without_task_domain_branch():
    aero = described_entry(ROOT / "recipes/aero_cfd")
    control = described_entry(ROOT / "recipes/safediffcon")
    assert aero["inputs"]["inputs.infer.preparation"] == "preparation"
    assert control["inputs"]["inputs.posttrain.preparation_cal"] == "preparation"
    assert "posttrain" in control["stages"]
    assert control["shared_outputs"] == {}


@pytest.mark.parametrize(
    "actual,expected,matched", [(1, True, False), (1, 1, True), ("1", 1, False)]
)
def test_labels_are_typed(actual, expected, matched):
    result = match_asset(
        {"kind": "preparation", "semantics": {"format_version": actual}},
        {"kind": "preparation", "semantics": {"format_version": expected}},
        status="succeeded",
    )
    assert result["matches"] is matched


def test_missing_split_and_wrong_phase_are_not_candidates():
    requirement = {
        "kind": "preparation",
        "semantics": {"type": "control.preparation", "split": "cal"},
    }
    asset = {"kind": "preparation", "semantics": {"type": "control.preparation"}}
    assert match_asset(asset, requirement, status="succeeded")["missing"] == ["semantics.split"]
    asset["semantics"]["split"] = "train"
    assert not match_asset(asset, requirement, status="succeeded")["matches"]
    assert not match_asset(
        {"kind": "checkpoint", "semantics": {"phase": "train"}},
        {"kind": "checkpoint", "semantics": {"phase": "posttrain"}},
        status="succeeded",
    )["matches"]


def test_source_is_verified_and_local_copy_relocates(tmp_path):
    from shutil import copytree

    recipe = tmp_path / "recipe"
    recipe.mkdir()
    OmegaConf.save({"components": {"application": "custom"}}, recipe / "config.yaml")
    (recipe / "custom.py").write_text('def inspect(request):\n    return {"value": 7}\n')
    source = capture_source(recipe, "inspect")
    copied = tmp_path / "captured"
    copytree(recipe, copied)
    (recipe / "custom.py").write_text('def inspect(request):\n    return {"value": 9}\n')
    assert invoke_source(source, copied, {}) == {"value": 7}
    with pytest.raises(ValueError, match="application_source_changed"):
        invoke_source(source, recipe, {})


def test_plain_script_has_no_invented_description(tmp_path):
    OmegaConf.save({"pipeline": {"stages": ["simulate"]}, "inputs": {}}, tmp_path / "config.yaml")
    assert describe_recipe(tmp_path) == {"description": None, "source": None}
    entry = described_entry(tmp_path)
    assert entry["shared_outputs"] == {}
    assert "resume_key" not in entry


def test_dependency_revision_invalidates_description_cache(tmp_path, monkeypatch):
    """配置不变但应用依赖更新时，持久描述缓存不能返回旧值。"""
    from tests.integration.test_task_source_dependencies import provider

    recipe, external, _ = provider(tmp_path, monkeypatch)
    (recipe / "custom.py").write_text(
        "from dependency import VALUE\ndef inspect(request):\n"
        "    return {'schema_version': 1, 'stages': ['simulate'], 'inputs': {}, 'revision_value': VALUE}\n"
    )
    first = describe_recipe(recipe, cache_dir=tmp_path / "cache")
    (external / "dependency.py").write_text("VALUE = 2\n")
    second = describe_recipe(recipe, cache_dir=tmp_path / "cache")
    assert first["source"]["revision"] != second["source"]["revision"]
    assert first["description"]["revision_value"] == 1
    assert second["description"]["revision_value"] == 2
    assert len(list((tmp_path / "cache").glob("*.json"))) == 2


def test_new_unrelated_source_does_not_invalidate_capture(tmp_path):
    OmegaConf.save({"components": {"application": "custom"}}, tmp_path / "config.yaml")
    (tmp_path / "custom.py").write_text('def inspect(request):\n    return {"ok": True}\n')
    source = capture_source(tmp_path, "inspect")
    (tmp_path / "new_ability.py").write_text("VALUE = 9\n")
    assert invoke_source(source, tmp_path, {}) == {"ok": True}


def test_execution_plan_rejects_incomplete_or_ambiguous_units():
    from ai4e_spec.artifacts.task_operations import validate_execution_plan

    unit = {
        "id": "0",
        "checkpoint_id": "c",
        "split": "cal",
        "samples": ["one"],
        "stages": ["calibrate"],
        "input_keys": ["inputs.calibrate.trajectory"],
        "overrides": ["pipeline.stages=[calibrate]"],
    }
    assert validate_execution_plan([unit]) == [unit]
    with pytest.raises(ValueError, match="duplicate_execution_unit"):
        validate_execution_plan([unit, unit])
    with pytest.raises(ValueError, match="invalid_execution_input"):
        validate_execution_plan([{**unit, "input_keys": ["train.data"]}])


def test_configuration_conversion_is_explicit_and_does_not_mutate_input():
    from ai4e_contrib.application.aero_cfd.configuration import convert_configuration

    original = {"trainprep": {"sampling": {"budget": 9}}}
    converted = convert_configuration(original)
    assert converted == {"trainprep": {}, "model": {"sampling": {"budget": 9}}}
    assert "sampling" in original["trainprep"]
    with pytest.raises(ValueError, match="不能同时存在"):
        convert_configuration({**original, "model": {"sampling": {}}})


def test_coordinator_source_drift_publishes_terminal_failure(tmp_path, monkeypatch):
    """协调器发现固定来源变化，必须写失败收据而不是遗留排队状态。"""
    from ai4e_task.storage.files import read_json, write_json
    from ai4e_task.tasks import inference_worker, operation_sources

    folder = tmp_path / "batch"
    folder.mkdir()
    monkeypatch.setattr(inference_worker, "_folder", lambda *_: folder)
    write_json(folder / "state.json", {"children": [], "status": "queued"})
    write_json(folder / "request.json", {"request": {}, "checkpoints": []})
    monkeypatch.setattr(
        operation_sources,
        "operation_context",
        lambda *_a, **_kw: {"source": {}, "recipe": str(tmp_path)},
    )

    def changed(*_):
        raise ValueError("application_source_changed")

    monkeypatch.setattr(operation_sources, "verify_source", changed)
    inference_worker.coordinate(tmp_path, "task", "batch")
    result = read_json(folder / "state.json")
    assert result["status"] == "failed"
    assert "application_source_changed" in result["error"]


def test_capture_rejects_conflicting_producer_labels(tmp_path, monkeypatch):
    """两份索引对同一真实文件声明不同用途，捕获不得任取其一。"""
    import ai4e_task as task
    from ai4e_task.storage import records
    from ai4e_task.tasks.assets import capture_inputs

    from ai4e_core.run.writer import RunWriter

    project = tmp_path / "p"
    task.create_project(project)
    recipe = tmp_path / "recipe"
    recipe.mkdir()
    data = project / "trajectory.bin"
    data.write_bytes(b"fixed contents")
    OmegaConf.save({"inputs": {"calibrate": {"data": str(data)}}}, recipe / "config.yaml")
    runs = []
    for split in ("train", "cal"):
        run_path = project / split
        run_path.mkdir()
        RunWriter(run_path).record_asset(
            "trajectory",
            data,
            kind="dataset",
            stage="prepare",
            semantics={"type": "trajectory", "split": split},
        )
        runs.append({"id": split, "task_id": "producer", "run_path": split})
    monkeypatch.setattr(records, "listing", lambda *_: runs)
    with pytest.raises(ValueError, match="asset_labels_conflict"):
        capture_inputs(
            recipe,
            {"config": "config.yaml", "inputs": {"inputs.calibrate.data": "dataset"}},
            project=project,
        )
