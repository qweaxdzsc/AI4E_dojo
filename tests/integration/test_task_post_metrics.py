"""真实持久张量、独立评价进程、导出与修订门禁验收。"""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import ai4e_task as task
import pytest
import torch
from ai4e_task.storage.database import transaction
from ai4e_task.storage.files import write_json
from ai4e_task.storage.records import put
from ai4e_task.tasks.checkpoints import file_digest


@pytest.fixture
def results_project(tmp_path):
    root = tmp_path / "project"
    task.create_project(root)
    with transaction(root) as db:
        put(db, "task", {"id": "t", "version_id": "v", "archived": False})
    for batch in range(2):
        children = []
        for cp in range(2):
            run = f"b{batch}-r{cp}"
            data = root / "tasks/t/data" / run
            run_dir = root / "tasks/t/runs" / run
            members = []
            for sample in ("a", "b"):
                folder = data / sample
                folder.mkdir(parents=True)
                payload = {
                    "surface.ids": torch.tensor([10, 20, 30]),
                    "surface.position": torch.zeros(3, 3),
                    "surface.pressure.prediction": torch.tensor([[2.0], [4.0], [6.0]]),
                    "surface.pressure.truth": torch.tensor([[1.0], [2.0], [3.0]]),
                }
                filemap = {key: key + ".pt" for key in payload}
                for key, value in payload.items():
                    torch.save(value, folder / filemap[key])
                manifest = folder / "manifest.json"
                write_json(
                    manifest,
                    {
                        "identity": {"sample": sample},
                        "filemap": filemap,
                        "domains": {
                            "surface": {
                                "ids": "surface.ids",
                                "targets": {"pressure": "surface.pressure"},
                                "units": {"pressure": "Pa"},
                            }
                        },
                    },
                )
                members.append({"sample": sample, "manifest": str(manifest)})
            write_json(
                run_dir / "artifacts/physical-predictions.json",
                {"status": "succeeded", "results": members},
            )
            children.append(
                {
                    "run_id": run,
                    "checkpoint": {
                        "id": f"cp{cp}",
                        "name": f"cp{cp}.pt",
                        "revision": str(cp),
                        "epoch": cp + 1,
                    },
                }
            )
            with transaction(root) as db:
                put(
                    db,
                    "run",
                    {
                        "id": run,
                        "task_id": "t",
                        "status": "succeeded",
                        "stages": ["infer"],
                        "run_path": str(run_dir.relative_to(root)),
                        "data_path": str(data.relative_to(root)),
                    },
                )
        value = {
            "id": f"b{batch}",
            "task_id": "t",
            "name": f"批次{batch}",
            "status": "succeeded",
            "created_at": datetime.now(UTC).isoformat(),
            "children": children,
        }
        write_json(root / f"tasks/t/.dojo/inference_batches/b{batch}/state.json", value)
        with transaction(root) as db:
            put(db, "inference_batch", value)
    return root


def wait_job(root, identity):
    for _ in range(200):
        job = task.read_post_metrics(root, "t", identity)
        if job["status"] in {"succeeded", "failed", "partial", "canceled", "interrupted"}:
            return job
        time.sleep(0.1)
    pytest.fail(str(job))


def request_for(root):
    catalog = task.post_results(root, "t")
    return {
        "results": [{"id": i["id"], "revision": i["revision"]} for i in catalog["items"]],
        "fields": ["surface:pressure:scalar"],
        "metrics": ["relative_l2", "rmse", "mse", "mae", "r2"],
        "idempotency_key": "once",
    }


def test_real_worker_multi_batch_export_and_immutable_inputs(results_project):
    root = results_project
    before = {str(p): file_digest(p) for p in (root / "tasks/t/data").rglob("*") if p.is_file()}
    request = request_for(root)
    job = task.submit_post_metrics(root, "t", request)
    assert task.submit_post_metrics(root, "t", request)["id"] == job["id"]
    done = wait_job(root, job["id"])
    assert done["status"] == "succeeded", done
    assert len(done["rows"]) == 8 and len({r["id"] for r in done["rows"]}) == 8
    assert all(r["values"]["r2"] == -6 for r in done["rows"])
    assert task.get_task(root, "t")["version_id"] == "v"
    assert before == {p: file_digest(Path(p)) for p in before}
    output = task.export_post_metrics(
        root, "t", job["id"], {"format": "json", "row_ids": [done["rows"][0]["id"]]}
    )
    assert len(json.loads(Path(output["path"]).read_text())["rows"]) == 1
    csv = task.export_post_metrics(root, "t", job["id"], {"format": "csv"})
    assert "surface" in Path(csv["path"]).read_text()
    assert len(task.post_results(root, "t")["items"]) == 8
    listed = task.list_post_result_files(root, "t", query="metrics.json")
    assert any(f["tree_path"].startswith("指标计算/") for f in listed["files"])
    with pytest.raises(ValueError, match="task_mismatch"):
        with transaction(root) as db:
            put(db, "task", {"id": "other", "version_id": "v"})
        task.read_post_metrics(root, "other", job["id"])
    with pytest.raises(ValueError):
        task.export_post_metrics(root, "t", job["id"], {"format": "csv", "path": "/elsewhere"})


def test_revision_conflict_and_partial_field_failure(results_project):
    root = results_project
    request = request_for(root)
    item = task.post_results(root, "t")["items"][0]
    Path(item["manifest"]).write_text(Path(item["manifest"]).read_text() + " ")
    with pytest.raises(ValueError, match="revision_conflict"):
        task.submit_post_metrics(root, "t", request)
    request = request_for(root)
    # 身份声明错误保留对应失败行，其他样本仍完成。
    meta = json.loads(Path(item["manifest"]).read_text())
    file = Path(item["manifest"]).parent / meta["filemap"]["surface.ids"]
    torch.save(torch.tensor([1, 1, 1]), file)
    request = request_for(root)
    done = wait_job(root, task.submit_post_metrics(root, "t", request)["id"])
    assert done["status"] == "partial" and done["failed"] == 1
    assert "实体ID" in next(r["error"] for r in done["rows"] if r["status"] == "failed")


def test_cancel_keeps_completed_rows_and_checks_changed_member(results_project):
    from ai4e_core.applications.aero_cfd.post import evaluate_result, run_evaluation

    root = results_project
    items = [task.freeze_result_item(i) for i in task.post_results(root, "t")["items"]]
    published = []
    job = {
        "id": "cancel",
        "run_id": "cancel-run",
        "task_id": "t",
        "version_id": "v",
        "run_dir": str(root / "tasks/t/runs/cancel"),
        "data_dir": str(root / "tasks/t/data/post/cancel"),
        "inputs": items,
        "request": {"fields": items[0]["fields"], "metrics": ["mse"]},
    }
    value = run_evaluation(job, publish=published.append, canceled=lambda: bool(published))
    assert value["status"] == "canceled" and value["completed"] == 1
    assert json.loads((Path(job["data_dir"]) / "metrics.json").read_text())["status"] == "canceled"
    Path(items[0]["files"][1]["path"]).write_bytes(b"changed")
    with pytest.raises(ValueError, match="来源修订变化"):
        evaluate_result(items[0], items[0]["fields"], ["mse"])
