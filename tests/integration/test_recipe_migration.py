"""离线变更包核验原件、故障恢复和用户修改保护。"""

import json
from pathlib import Path

import pytest


def test_cli_preview_apply_rollback(tmp_path, capsys):
    from tools.migration.recipe_conventions.cli import main
    source, candidate, bundle = (tmp_path / name for name in ("recipe", "candidate", "bundle"))
    source.mkdir()
    candidate.mkdir()
    (source / "pipeline.py").write_text("old\n")
    (candidate / "pipeline.py").write_text("new\n")
    assert main(["prepare", "--source", str(source), "--candidate", str(candidate), "--bundle", str(bundle)]) == 0
    assert (source / "pipeline.py").read_text() == "old\n"
    assert main(["inspect", "--bundle", str(bundle)]) == 0
    assert main(["apply", "--bundle", str(bundle), "--offline"]) == 0
    assert (source / "pipeline.py").read_text() == "new\n"
    assert main(["rollback", "--bundle", str(bundle), "--offline"]) == 0
    assert (source / "pipeline.py").read_text() == "old\n"


def test_partial_candidate_copy_can_be_rolled_back(tmp_path, monkeypatch):
    from tools.migration.recipe_conventions import transaction
    source, bundle = tmp_path / "recipe", tmp_path / "bundle"
    source.mkdir()
    (source / "pipeline.py").write_text("original")
    transaction.prepare(source, bundle, {"pipeline.py": b"candidate"})
    copytree = transaction.shutil.copytree

    def fail_copy(src, dst, *args, **kwargs):
        if Path(dst).name == ".recipe-migration-new":
            Path(dst).mkdir()
            (Path(dst) / "partial").write_text("incomplete")
            raise OSError("disk full")
        return copytree(src, dst, *args, **kwargs)

    monkeypatch.setattr(transaction.shutil, "copytree", fail_copy)
    with pytest.raises(OSError, match="disk full"):
        transaction.apply(bundle)
    transaction.rollback(bundle)
    assert (source / "pipeline.py").read_text() == "original"
    assert not (tmp_path / ".recipe-migration-new").exists()

from tools.migration.recipe_conventions.transaction import apply, inventory, prepare, rollback


def source(tmp_path):
    recipe = tmp_path / "task/recipe"
    recipe.mkdir(parents=True)
    (recipe / "pipeline.py").write_text("# user callback\n")
    (recipe / "config.yaml").write_text("train: {}\n")
    (recipe / "task-entry.json").write_text("{}")
    return recipe


def test_offline_migration_preserves_source_history_and_rolls_back(tmp_path):
    recipe = source(tmp_path)
    history = recipe.parent / "runs/frozen.py"
    history.parent.mkdir()
    history.write_text("frozen")
    before = inventory(recipe)
    bundle = tmp_path / "migration"
    plan = prepare(recipe, bundle, {"config.yaml": b"inputs: {}\n", "task-entry.json": None})
    assert inventory(recipe) == before
    assert plan["changes"] == ["config.yaml", "task-entry.json"]
    apply(bundle)
    assert (recipe / "pipeline.py").read_text() == "# user callback\n"
    assert not (recipe / "task-entry.json").exists()
    assert history.read_text() == "frozen"
    rollback(bundle)
    assert inventory(recipe) == before
    assert history.read_text() == "frozen"


@pytest.mark.parametrize("target", ["source", "candidate", "original"])
def test_migration_refuses_drift_before_apply(tmp_path, target):
    recipe = source(tmp_path)
    bundle = tmp_path / "migration"
    prepare(recipe, bundle, {"config.yaml": b"inputs: {}\n"})
    root = recipe if target == "source" else bundle / target
    (root / "pipeline.py").write_text("modified")
    with pytest.raises(ValueError, match="changed"):
        apply(bundle)


def test_interrupted_rename_recovers_exact_bytes(tmp_path, monkeypatch):
    recipe = source(tmp_path)
    before = inventory(recipe)
    bundle = tmp_path / "migration"
    prepare(recipe, bundle, {"config.yaml": b"inputs: {}\n"})
    original = Path.rename

    def failing(path, target):
        if path.name == ".recipe-migration-new":
            raise OSError("injected publish failure")
        return original(path, target)

    monkeypatch.setattr(Path, "rename", failing)
    with pytest.raises(OSError, match="publish failure"):
        apply(bundle)
    assert json.loads((bundle / "journal.json").read_text())["status"] == "applying"
    rollback(bundle)
    assert inventory(recipe) == before


def test_rollback_does_not_erase_later_user_edits(tmp_path):
    recipe = source(tmp_path)
    bundle = tmp_path / "migration"
    prepare(recipe, bundle, {"config.yaml": b"inputs: {}\n"})
    apply(bundle)
    (recipe / "pipeline.py").write_text("new user research")
    with pytest.raises(ValueError, match="changed_after_apply"):
        rollback(bundle)
    assert (recipe / "pipeline.py").read_text() == "new user research"


def test_aero_conversion_retains_prediction_settings_and_checkpoint():
    from tools.migration.recipe_conventions.configuration import convert_aero

    old = {"paths": {"datasets": {"root": "/data/output"}},
           "dataset": {"root": "/data/source", "partition": "official"},
           "components": {}, "train": {}, "model": {}, "trainprep": {},
           "post": {"checkpoint": "/weights/fixed.pt", "samples": ["chosen"], "query_chunk_size": 17},
           "pipeline": {"stages": ["trainprep", "train", "post"]}}
    value = convert_aero(old)
    assert value["data_root"] == "/data/output"
    assert value["inputs"]["infer"]["checkpoint"] == "/weights/fixed.pt"
    assert value["infer"]["samples"] == ["chosen"]
    assert value["infer"]["query_chunk_size"] == 17
    assert value["pipeline"]["stages"] == ["trainprep", "train", "infer", "post"]
    assert convert_aero(value) == value
    assert old["post"]["checkpoint"] == "/weights/fixed.pt"
    old["post"]["checkpoint"] = "best"
    with pytest.raises(ValueError, match="固定为实际文件"):
        convert_aero(old)
