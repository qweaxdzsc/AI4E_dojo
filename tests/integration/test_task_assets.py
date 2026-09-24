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
    cfg = OmegaConf.load(source / "config.yaml")
    for kind in ("preparation", "checkpoint"):
        file = tmp_path / f"{kind}.bin"
        file.write_bytes(kind.encode())
        key = "preparation" if kind == "preparation" else "resume"
        OmegaConf.update(cfg, "inputs.train." + key, str(file), force_add=True)
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
            assert Path(copied_cfg.inputs.test.dataset) == asset_path(
                project, child["assets"]["inputs.test.dataset"]
            )
    assert len(task.get_lineage(project)) == 5


def test_shared_reference_keeps_array_dependencies(tmp_path):
    from ai4e_task.tasks.assets import describe_asset

    project = tmp_path / "project"
    task.create_project(project)
    manifest, array = tmp_path / "arrays.json", tmp_path / "field.npy"
    manifest.write_text('{"field": "field.npy"}')
    array.write_bytes(b"array contents")
    dependencies = [describe_asset(array, kind="other")]
    with pytest.raises(ValueError, match="asset_copy_not_portable"):
        task.register_shared(
            project,
            "incomplete-copy",
            manifest,
            kind="dataset",
            copy=True,
            dependencies=dependencies,
        )
    shared = task.register_shared(
        project, "array-reference", manifest, kind="dataset", dependencies=dependencies
    )
    task.get_shared(project, shared["id"])
    array.write_bytes(b"changed")
    with pytest.raises(ValueError, match="asset_changed"):
        task.get_shared(project, shared["id"])


def test_rebound_shared_bundle_survives_fork(tmp_path):
    """同一输入槽从旧文件改绑共享清单，fork必须保留新资产的完整目录。"""
    from ai4e_task.tasks.assets import describe_asset

    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    old = tmp_path / "old.bin"
    old.write_bytes(b"old")
    cfg = OmegaConf.load(source / "config.yaml")
    OmegaConf.update(cfg, "inputs.train.preparation", str(old), force_add=True)
    OmegaConf.save(cfg, source / "config.yaml")
    parent = task.new_task(project, "root", source=source)
    bundle = tmp_path / "prepared"
    bundle.mkdir()
    manifest = bundle / "manifest.json"
    manifest.write_text('{"field":"field.npy"}')
    (bundle / "field.npy").write_bytes(b"complete-array")
    shared = task.register_shared(
        project,
        "prepared",
        manifest,
        kind="preparation",
        copy=True,
        dependencies=[describe_asset(bundle / "field.npy", kind="other")],
        bundle=describe_asset(bundle, kind="other"),
    )
    current = task.read_configuration(project, parent["id"])
    current["config"].setdefault("inputs", {}).setdefault("train", {})["preparation"] = str(
        project / shared["path"]
    )
    task.replace_configuration(
        project, parent["id"], current["config"], revision=current["revision"]
    )
    child = task.fork_task(project, parent["id"], copy_preparation=True)
    copied = validate_asset(project, child["assets"]["inputs.train.preparation"])
    assert (copied.parent / "field.npy").read_bytes() == b"complete-array"
    assert child["assets"]["inputs.train.preparation"]["bundle"]
