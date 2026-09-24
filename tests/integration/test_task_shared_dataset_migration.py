"""历史物理产物的复制迁移、依赖修正与幂等验收。"""

import json
from pathlib import Path

import ai4e_task as task
import pytest

from tests.integration.test_task_shared_execution import run_success, shared_recipe


def migrate(project, **kwargs):
    context = task.configuration_context({"components": {"application": "ai4e_contrib.application.aero_cfd.operations"}}, project)
    return task.migrate_shared_datasets(project, context=context, **kwargs)


def legacy_recipe(tmp_path):
    """真实运行一个没有公共共享名声明的旧式本地生产器。"""
    from omegaconf import OmegaConf

    source = shared_recipe(tmp_path)
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.dataset.pop("processed_name")
    OmegaConf.save(cfg, source / "config.yaml")
    code = (source / "pipeline.py").read_text()
    code = code.replace("from ai4e_core.base.config import load_config", "from ai4e_core.base.config import load_config as _load_config")
    code = code.replace('TrainingRun().output_dir("rawprep")', "TrainingRun().data_dir")
    loader = '\ndef load_config(path, overrides=None):\n    cfg = _load_config(path, overrides)\n    cfg.setdefault("dataset", {})["processed_name"] = "sample_data"\n    return cfg\n'
    code = code.replace('if __name__ == "__main__":', loader + '\nif __name__ == "__main__":')
    (source / "pipeline.py").write_text(code)
    return source


def test_migrate_formal_only_preserves_original_and_is_idempotent(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    source = legacy_recipe(tmp_path)
    item = task.new_task(project, "legacy", source=source)
    formal = run_success(project, item)
    run_success(project, item, operation_mode="trial", overrides=["score=8"])
    manifest = Path(formal["data_dir"]) / "manifest.json"
    before = manifest.read_bytes()
    plan = migrate(project)
    assert len(plan) == 1 and plan[0]["run_id"] == formal["id"]
    assert not (project / "shared/datasets").exists()
    result = migrate(project, dry_run=False)
    assert result[0]["status"] == "migrated"
    record = task.get_shared_dataset(project, "sample_data")
    migrated = json.loads(Path(record["manifest_path"]).read_text())
    assert migrated["samples"][0]["path"] == "."
    assert manifest.read_bytes() == before
    assert migrate(project, dry_run=False)[0]["status"] == "already_migrated"
    assert (Path(record["manifest_path"]).parent / "field.bin").read_text() == "2.0"


def test_explicit_registered_names_preserve_exact_runs(tmp_path):
    """旧登记名称不等于配置名称时，不把最新同名运行当作用户选中的数据。"""
    project = tmp_path / "project"
    task.create_project(project)
    source = legacy_recipe(tmp_path)
    item = task.new_task(project, "legacy", source=source)
    old = run_success(project, item)
    new = run_success(project, item, overrides=["score=5"])
    trial = run_success(project, item, operation_mode="trial")
    with pytest.raises(ValueError, match="multiple_candidates"):
        migrate(project)
    assert migrate(project, sources={}) == []
    with pytest.raises(ValueError, match="source_not_eligible"):
        migrate(
            project, sources={"old": old["id"], "trial": trial["id"]}, dry_run=False
        )
    assert not (project / "shared/datasets").exists()
    selected = {"registered_old": old["id"], "registered_new": new["id"]}
    result = migrate(project, sources=selected, dry_run=False)
    assert [r["run_id"] for r in result] == [old["id"], new["id"]]
    for name, expected in [("registered_old", "2.0"), ("registered_new", "5")]:
        manifest = Path(task.get_shared_dataset(project, name)["manifest_path"])
        assert (manifest.parent / "field.bin").read_text() == expected
    assert all(
        r["status"] == "already_migrated"
        for r in migrate(project, sources=selected, dry_run=False)
    )


def test_migration_failure_conflict_and_corrupt_repeat(tmp_path, monkeypatch):
    """复制失败撤下登记，同名须覆盖，已迁移副本损坏不能冒充幂等成功。"""
    from ai4e_task.storage import asset_transfer

    project = tmp_path / "project"
    task.create_project(project)
    source = legacy_recipe(tmp_path)
    producer = task.new_task(project, "legacy", source=source)
    original = run_success(project, producer)
    manifest = Path(original["data_dir"]) / "manifest.json"
    before = manifest.read_bytes()
    copy = asset_transfer.copy_declared_dataset

    def interrupted(*args, **kwargs):
        copy(*args, **kwargs)
        raise OSError("interrupted copy")

    monkeypatch.setattr(asset_transfer, "copy_declared_dataset", interrupted)
    with pytest.raises(OSError, match="interrupted copy"):
        migrate(project, dry_run=False)
    assert task.get_shared_dataset(project, "sample_data")["status"] == "unavailable"
    assert manifest.read_bytes() == before
    monkeypatch.setattr(asset_transfer, "copy_declared_dataset", copy)
    with pytest.raises(FileExistsError, match="shared_dataset_exists"):
        migrate(project, dry_run=False)
    migrate(project, dry_run=False, overwrite=True)
    shared = task.get_shared_dataset(project, "sample_data")
    field = Path(shared["manifest_path"]).parent / "field.bin"
    field.write_text("damaged")
    with pytest.raises(ValueError, match="asset_changed"):
        migrate(project, dry_run=False)
    assert manifest.read_bytes() == before
