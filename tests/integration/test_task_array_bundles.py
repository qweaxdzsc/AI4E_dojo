"""公共自包含数组目录可共享、复制、fork，科学清单字节保持原样。"""

import json
import shutil
from pathlib import Path

import ai4e_task as task
import numpy as np
import pytest
from ai4e_task.tasks.assets import copy_assets, indexed_asset, validate_asset

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.run.indexes import validate_asset_content
from ai4e_core.run.writer import RunWriter


def test_array_bundle_share_copy_fork_and_relocate(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    path = Path(save_arrays(tmp_path / "physical", {"u": np.arange(12).reshape(3, 4)},
                            kind="physical", metadata={"ids": [0, 1, 2]}))
    writer = RunWriter.create(tmp_path / "runs")
    index = writer.record_asset("train", path, kind="dataset", stage="rawprep",
                               dependencies=[path.parent / "u.npy"], bundle_root=path.parent)
    item = json.loads(index.read_text())["items"]["rawprep/train"]
    record = indexed_asset(item, provenance={"run_id": "producer"})
    shared = task.register_shared(project, "arrays/train", path, kind="dataset", copy=True,
                                  dependencies=record["dependencies"], bundle=record["bundle"])
    shared_path = validate_asset(project, shared)
    assert shared_path.read_bytes() == path.read_bytes()
    staged, final = project / "staged", project / "consumer"
    copied = copy_assets(project, {"inputs.trainprep.dataset": shared}, staged, final, {"dataset"})
    staged.rename(final)
    shutil.rmtree(path.parent)
    shutil.rmtree(shared_path.parent)
    relocated = validate_asset(project, copied["inputs.trainprep.dataset"])
    metadata, arrays = read_arrays(relocated, kind="physical")
    np.testing.assert_array_equal(arrays["u"], np.arange(12).reshape(3, 4))
    assert metadata["metadata"]["ids"] == [0, 1, 2]
    moved = tmp_path / "moved-project"
    project.rename(moved)
    assert validate_asset(moved, copied["inputs.trainprep.dataset"]).is_file()
    (moved / relocated.relative_to(project)).with_name("u.npy").write_bytes(b"changed")
    with pytest.raises(ValueError, match="asset_changed"):
        validate_asset(moved, copied["inputs.trainprep.dataset"])


def test_bundle_rejects_external_dependency_and_content_drift(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    source = root / "manifest.json"
    source.write_text("{}")
    outside = tmp_path / "outside"
    outside.write_text("x")
    writer = RunWriter.create(tmp_path / "runs")
    with pytest.raises(ValueError, match="outside_root"):
        writer.record_asset("data", source, kind="dataset", stage="rawprep",
                            dependencies=[outside], bundle_root=root)
    index = writer.record_asset("data", source, kind="dataset", stage="rawprep", bundle_root=root)
    item = json.loads(index.read_text())["items"]["rawprep/data"]
    (root / "new.bin").write_bytes(b"new")
    with pytest.raises(ValueError, match="bundle_changed"):
        validate_asset_content(item)


def test_run_asset_public_share_and_fork_remain_consumable(tmp_path):
    import yaml

    from tests.integration.test_task_management import recipe

    project = tmp_path / "project"
    task.create_project(project)
    source = recipe(tmp_path)
    cfg = yaml.safe_load((source / "config.yaml").read_text())
    cfg["inputs"] = {"rawprep": {}, "trainprep": {"dataset": None}}
    cfg["pipeline"]["stages"] = ["rawprep"]
    (source / "config.yaml").write_text(yaml.safe_dump(cfg))
    (source / "pipeline.py").write_text('''from ai4e_core import run
from ai4e_core.base.config.conventions import load_recipe_config
from ai4e_core.abilities.data.save.array_manifest import save_arrays
from pathlib import Path
import numpy as np

def rawprep(cfg):
    session = run.TrainingRun()
    path = Path(save_arrays(session.output_dir("rawprep") / "physical", {"u": np.arange(6)}, kind="physical", metadata={}))
    session.record_asset("train", path, kind="dataset", stage="rawprep", dependencies=[path.parent / "u.npy"], bundle_root=path.parent)
    session.report({"manifest": str(path)}, stage="rawprep")

if __name__ == "__main__":
    raise SystemExit(run.launch({"rawprep": rawprep}, script=__file__, config_loader=load_recipe_config))
''')
    producer = task.new_task(project, "producer", source=source)
    run = task.wait_run(project, task.submit_run(project, producer["id"])["id"], timeout=45)
    assert run["status"] == "succeeded", task.read_log(project, run["id"])
    summary = json.loads((Path(run["run_dir"]) / "summary.json").read_text())
    original = Path(summary["reports"]["rawprep"]["manifest"])
    shared = task.share_run_asset(project, run["id"], "arrays/train", original, kind="dataset", copy=True)
    cfg["inputs"]["trainprep"]["dataset"] = str(validate_asset(project, shared))
    consumer = task.new_task(project, "consumer", source=source, configuration=cfg)
    child = task.fork_task(project, consumer["id"], copy_datasets=True)
    reference = task.read_configuration(project, child["id"])["config"]["inputs"]["trainprep"]["dataset"]
    shutil.rmtree(original.parent)
    shutil.rmtree(validate_asset(project, shared).parent)
    _, arrays = read_arrays(reference, kind="physical")
    np.testing.assert_array_equal(arrays["u"], np.arange(6))
    assert len(task.get_lineage(project)) == 3
