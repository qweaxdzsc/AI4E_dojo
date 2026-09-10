"""共享、资产来源与复制开关验收。"""

from pathlib import Path

import ai4e_task as task
import pytest
from ai4e_task.tasks.assets import asset_path, validate_asset
from omegaconf import OmegaConf

from tests.integration.test_task_management import recipe


def test_shared_reference_copy_and_change_detection(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    file = tmp_path / "weights.pt"
    file.write_bytes(b"weights")
    ref = task.register_shared(project, "weights-ref", file, kind="checkpoint")
    copied = task.register_shared(project, "weights-copy", file, kind="checkpoint", copy=True)
    assert ref["external"] and not copied["external"]
    assert (project / "shared/weights-copy/asset.json").exists()
    assert task.get_shared(project, copied["id"])["digest"] == ref["digest"]
    file.write_bytes(b"changed")
    with pytest.raises(ValueError, match="asset_changed"):
        task.get_shared(project, ref["id"])
    task.get_shared(project, copied["id"])


def test_copy_switches_and_execution_binding(tmp_path):
    project = tmp_path / "p"
    task.create_project(project)
    source = recipe(tmp_path)
    import json

    entry = json.loads((source / "task-entry.json").read_text())
    cfg = OmegaConf.load(source / "config.yaml")
    for kind in ("preparation", "checkpoint"):
        file = tmp_path / f"{kind}.bin"
        file.write_bytes(kind.encode())
        cfg[kind] = str(file)
        entry["inputs"][kind] = kind
    (source / "task-entry.json").write_text(json.dumps(entry))
    OmegaConf.save(cfg, source / "config.yaml")
    first = task.new_task(project, "root", source=source)
    default = task.fork_task(project, first["id"])
    assert all(a["external"] for a in default["assets"].values())
    for flag, kind in [
        ("copy_datasets", "dataset"),
        ("copy_preparation", "preparation"),
        ("copy_checkpoints", "checkpoint"),
    ]:
        child = task.fork_task(project, first["id"], **{flag: True})
        for asset in child["assets"].values():
            assert asset["external"] != (asset["kind"] == kind)
            validate_asset(project, asset)
        if kind == "dataset":
            copied_cfg = OmegaConf.load(project / "tasks" / child["id"] / "recipe/config.yaml")
            assert Path(copied_cfg.dataset.root) == asset_path(
                project, child["assets"]["dataset.root"]
            )
    assert len(task.get_lineage(project)) == 5
