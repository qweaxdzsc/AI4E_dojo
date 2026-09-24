"""实际小型模型的任务检查点、批量推理、结果和版本身份验收。"""

import json
import time
from pathlib import Path

import ai4e_task as task
import pytest
import yaml

from tests.integration.test_recipe_explicit_equivalence import case


def wait_batch(project, task_id, identity, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = task.read_inference_batch(project, task_id, identity)
        if value["status"] in {"succeeded", "failed", "partial", "canceled", "interrupted"}:
            return value
        time.sleep(0.2)
    pytest.fail("inference_timeout: " + json.dumps(value))


def test_queued_dependency_change_publishes_failed_batch(tmp_path, monkeypatch):
    """排队后外部依赖变更必须在创建任何子运行前进入失败终态。"""
    import shutil

    from ai4e_task.storage.files import read_json, write_json
    from ai4e_task.tasks.inference_worker import coordinate

    from tests.integration.test_task_source_dependencies import provider

    recipe, external, source = provider(tmp_path, monkeypatch)
    project = tmp_path / "project"
    task.create_project(project)
    folder = project / "tasks/t/.dojo/inference_batches/b"
    shutil.copytree(recipe, folder / "code")
    write_json(folder / "request.json", {
        "request": {}, "application_source": source, "checkpoints": [],
    })
    write_json(folder / "state.json", {"id": "b", "status": "queued", "children": []})
    (external / "dependency.py").write_text("VALUE = 9\n")
    coordinate(project, "t", "b")
    result = read_json(folder / "state.json")
    assert result["status"] == "failed"
    assert "application_source_changed" in result["error"]
    assert result["children"] == []
    assert read_json(folder / "request.json")["application_source"] == source


def test_two_checkpoints_two_samples_real_execution(tmp_path, monkeypatch):
    folder, cfg = case(tmp_path, "nasa_crm_abupt")
    # 平台批量推理消费现行 version=2 准备；保留案例专属 rawprep。
    import shutil
    for stage in ("trainprep.py", "train.py", "infer.py"):
        shutil.copyfile(Path(__file__).resolve().parents[2] / "recipes/aero_cfd" / stage, folder / stage)
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg))
    import shutil

    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "infer-test", source=folder)
    first = task.submit_run(project, item["id"], input_keys=["inputs.trainprep.dataset"])
    first = task.wait_run(project, first["id"], timeout=180)
    assert first["status"] == "succeeded", task.read_log(project, first["id"])
    preparation = str(Path(first["run_dir"]) / "artifacts/preparation.json")
    second = task.submit_run(
        project,
        item["id"],
        input_keys=["inputs.train.preparation"],
        overrides=[
            "pipeline.stages=[train]",
            "inputs.train.preparation=" + json.dumps(preparation),
            "train.max_epochs=1",
        ],
    )
    second = task.wait_run(project, second["id"], timeout=180)
    assert second["status"] == "succeeded", task.read_log(project, second["id"])
    catalog = task.list_inference_checkpoints(project, item["id"])
    chosen = [
        next(c for c in catalog if c["run_id"] == r["id"] and c["name"] == "last.pt")
        for r in [first, second]
    ]
    current = task.read_configuration(project, item["id"])
    request = {
        "expected_revision": current["revision"],
        "checkpoints": [{"id": c["id"], "revision": c["revision"]} for c in chosen],
        "samples": ["Sample001", "Sample002"],
        "split": "test",
        "device": "cpu",
        "options": {"evaluate": True, "save_predictions": True, "export_vtk": False},
        "idempotency_key": "batch-1",
    }
    checked = task.check_inference(project, item["id"], request)
    assert checked["total"] == 4
    submitted = task.submit_inference(project, item["id"], request)
    assert task.submit_inference(project, item["id"], request)["id"] == submitted["id"]
    done = wait_batch(project, item["id"], submitted["id"])
    assert done["status"] == "succeeded", done
    assert len(done["children"]) == 2 and done["completed"] == 4
    results = task.inference_results(project, item["id"], done["id"])
    assert len(results["items"]) == 4, results
    assert results["comparison"]["status"] == "comparable", results["comparison"]
    assert all(Path(f["path"]).is_file() for r in results["items"] for f in r["files"])
    assert len(task.get_lineage(project)) == 1
    assert task.read_configuration(project, item["id"]) == current
    assert all(task.get_run(project, c["run_id"])["stages"] == ["infer"] for c in done["children"])
    receipts = [
        project / task.get_run(project, c["run_id"])["request_path"] for c in done["children"]
    ]
    assert (receipts[0].parent / "finished.json").stat().st_mtime_ns <= (
        receipts[1].parent / "started.json"
    ).stat().st_mtime_ns
    # 在启动前模拟执行资源故障，已固定输入可以重试，但旧运行和文件不覆盖。
    # 模拟协调器完成子运行后、提交终态前退出；恢复不能重新执行子运行。
    from datetime import UTC, datetime, timedelta

    from ai4e_task.storage.files import write_json
    from ai4e_task.tasks import inference, inference_worker

    state_path = inference._folder(project, item["id"], done["id"]) / "state.json"
    write_json(
        state_path,
        {
            **done,
            "status": "running",
            "created_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
        },
    )
    before = [(r.parent / "finished.json").stat().st_mtime_ns for r in receipts]
    assert task.read_inference_batch(project, item["id"], done["id"])["status"] == "interrupted"
    resumed = task.recover_inference(project, item["id"], done["id"])
    assert resumed["status"] == "queued"
    # 恢复启动收据写入后，旧协调器收据可能短暂仍在；等待新终态。
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        recovered = task.read_inference_batch(project, item["id"], done["id"])
        if recovered["status"] == "succeeded":
            break
        time.sleep(0.1)
    assert recovered["status"] == "succeeded", recovered
    assert before == [(r.parent / "finished.json").stat().st_mtime_ns for r in receipts]

    launch = inference._launch
    monkeypatch.setattr(inference, "_launch", lambda *_: None)
    failed = task.submit_inference(
        project, item["id"], {**request, "idempotency_key": "batch-fail"}
    )
    start = inference_worker.start_captured_run

    def unavailable(*_):
        raise OSError("executor unavailable")

    monkeypatch.setattr(inference_worker, "start_captured_run", unavailable)
    inference_worker.coordinate(project, item["id"], failed["id"])
    failed = task.read_inference_batch(project, item["id"], failed["id"])
    assert failed["status"] == "failed" and "executor unavailable" in failed["error"]
    retry = task.retry_inference(project, item["id"], failed["id"], idempotency_key="retry-1")
    assert (
        task.retry_inference(project, item["id"], failed["id"], idempotency_key="retry-1")["id"]
        == retry["id"]
    )
    monkeypatch.setattr(inference_worker, "start_captured_run", start)
    launch(project, item["id"], retry["id"])
    retried = wait_batch(project, item["id"], retry["id"])
    assert retried["status"] == "succeeded", retried
    assert {c["run_id"] for c in retried["children"]}.isdisjoint(
        c["run_id"] for c in failed["children"]
    )
    assert [c["checkpoint"]["fixed"] for c in retried["children"]] == [
        c["checkpoint"]["fixed"] for c in failed["children"]
    ]
    canceled = task.submit_inference(
        project, item["id"], {**request, "idempotency_key": "batch-cancel"}
    )
    task.cancel_inference(project, item["id"], canceled["id"])
    inference_worker.coordinate(project, item["id"], canceled["id"])
    canceled = task.read_inference_batch(project, item["id"], canceled["id"])
    assert canceled["status"] == "canceled" and not canceled["children"]
