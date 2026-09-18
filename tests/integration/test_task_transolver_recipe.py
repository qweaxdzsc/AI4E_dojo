"""Transolver 保留领域流程，经普通 Task 与直接脚本执行同一正文。"""

import json
from pathlib import Path

import ai4e_task as task
import torch
import yaml

from tests.integration.test_recipe_explicit_equivalence import case
from tests.integration.test_recipe_extensions import script
from tools.verification.recipe_task.nasa import compare_predictions


def test_transolver_direct_task_and_independent_post(tmp_path, monkeypatch):
    # 两个独立进程使用相同 CPU 归约线程数，严格逐值比较才有意义。
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("VECLIB_MAXIMUM_THREADS", "1")
    folder, cfg = case(tmp_path, "nasa_crm_transolver3")
    cfg["pipeline"]["stages"] = ["trainprep", "train", "infer", "post"]
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg))
    result = script(folder)
    assert result.returncode == 0, result.stdout + result.stderr
    direct = next(Path(cfg["run_root"]).glob("*/checkpoints/last.pt")).parent.parent

    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "Transolver", source=folder)
    submitted = task.submit_run(project, item["id"])
    managed = task.wait_run(project, submitted["id"], timeout=180)
    assert managed["status"] == "succeeded", task.read_log(project, submitted["id"])
    directory = Path(managed["run_dir"])
    left, right = [torch.load(p / "checkpoints/last.pt", weights_only=False) for p in (direct, directory)]
    assert left["updates"] == right["updates"] > 0
    for name in left["model"]:
        torch.testing.assert_close(left["model"][name], right["model"][name], rtol=0, atol=0)
    results = directory / "artifacts/inference-results.json"
    compare_predictions(direct / "artifacts/inference-results.json", results)
    old = json.loads((directory / "artifacts/preparation.json").read_text())
    assert old["version"] == 2 and old["kind"] == "physical_fields"
    catalog = task.list_inference_checkpoints(project, item["id"])
    selected = next(c for c in catalog if c["name"] == "last.pt")
    current = task.read_configuration(project, item["id"])
    request = {
        "expected_revision": current["revision"],
        "checkpoints": [{"id": selected["id"], "revision": selected["revision"]}],
        "samples": cfg["infer"]["samples"], "split": "test", "device": "cpu",
        "options": {"evaluate": True, "save_predictions": True, "export_vtk": False},
    }
    checked = task.check_inference(project, item["id"], request)
    assert checked["total"] == 2
    from tests.integration.test_task_infer_batches import wait_batch

    batch = task.submit_inference(project, item["id"], request)
    batch = wait_batch(project, item["id"], batch["id"])
    assert batch["status"] == "succeeded", batch
    child = task.get_run(project, batch["children"][0]["run_id"])
    compare_predictions(results, Path(child["run_dir"]) / "artifacts/inference-results.json")
    post = task.submit_run(project, item["id"], overrides=[
        "pipeline.stages=[post]", f"inputs.post.results={results}",
        "inputs.infer.checkpoint=/unavailable/checkpoint.pt",
    ])
    post = task.wait_run(project, post["id"], timeout=60)
    assert post["status"] == "succeeded", task.read_log(project, post["id"])
    assert len(task.get_lineage(project)) == 1
