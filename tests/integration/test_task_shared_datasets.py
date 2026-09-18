"""项目共享查询、绑定事务、归档与显式复制行为。"""

from pathlib import Path

import ai4e_task as task
import pytest
from ai4e_task.tasks.assets import validate_asset

from tests.integration.test_task_shared_execution import run_success, setup_shared


def test_bind_revision_guard_and_archive_keeps_data(tmp_path):
    project, producer, source = setup_shared(tmp_path)
    consumer = task.new_task(project, "consumer", source=source)
    run_success(project, producer)
    current = task.read_configuration(project, consumer["id"])
    with pytest.raises(ValueError, match="configuration_revision_conflict"):
        task.bind_shared_dataset(project, consumer["id"], "sample_data", revision="old")
    assert task.read_configuration(project, consumer["id"]) == current
    task.bind_shared_dataset(project, consumer["id"], "sample_data", revision=current["revision"])
    derived = task.fork_task(project, consumer["id"])
    assert derived["assets"]["inputs.trainprep.dataset"]["shared_dataset"]
    assert derived["assets"]["inputs.trainprep.dataset"]["path"].startswith("shared/datasets/")
    task.update_task(project, producer["id"], archived=True)
    assert task.list_shared_datasets(project)[0]["status"] == "available"
    assert len(task.get_lineage(project)) == 3


def test_fork_explicit_copy_is_self_contained(tmp_path):
    project, producer, _ = setup_shared(tmp_path)
    run_success(project, producer)
    current = task.read_configuration(project, producer["id"])
    task.bind_shared_dataset(project, producer["id"], "sample_data", revision=current["revision"])
    child = task.fork_task(project, producer["id"], copy_datasets=True)
    copied = child["assets"]["inputs.trainprep.dataset"]
    assert not copied.get("shared_dataset")
    assert validate_asset(project, copied).is_relative_to(project / "tasks" / child["id"])
    run_success(project, producer, overwrite=True, overrides=["score=9"])
    prepared = run_success(project, child, overrides=["pipeline.stages=[trainprep]"])
    assert (Path(prepared["data_dir"]) / "prepared.txt").read_text() == "2.0"


def test_explicit_cross_project_reference_follows_current_content(tmp_path):
    project, producer, source = setup_shared(tmp_path)
    run_success(project, producer)
    other = tmp_path / "other"
    task.create_project(other)
    consumer = task.new_task(other, "consumer", source=source)
    cfg = task.read_configuration(other, consumer["id"])
    manifest = task.get_shared_dataset(project, "sample_data")["manifest_path"]
    task.save_configuration(
        other, consumer["id"], {"inputs": {"trainprep": {"dataset": manifest}}}, revision=cfg["revision"]
    )
    before = task.read_configuration(other, consumer["id"])
    run_success(project, producer, overwrite=True, overrides=["score=19"])
    run = run_success(other, consumer, overrides=["pipeline.stages=[trainprep]"])
    assert (Path(run["data_dir"]) / "prepared.txt").read_text() == "19"
    assert task.read_configuration(other, consumer["id"]) == before
    assert run["lineage"]["assets"]["inputs.trainprep.dataset"]["shared_project"] == str(project)
