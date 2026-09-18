"""真实小模型跨分片子运行：部分失败、只评价、重试继承和取消。"""

import shutil
from pathlib import Path

import ai4e_task as task
import yaml

from tests.integration.test_recipe_explicit_equivalence import case
from tests.integration.test_task_infer_batches import wait_batch


def test_partition_failure_retry_and_evaluation_only(tmp_path, monkeypatch):
    """同名样本按分片保留，最后成功不得掩盖前一分片失败。"""
    folder, cfg = case(tmp_path, "nasa_crm_abupt")
    # 平台批量推理消费现行 version=2 准备；保留案例专属 rawprep。
    import shutil
    for stage in ("trainprep.py", "train.py", "infer.py"):
        shutil.copyfile(Path(__file__).resolve().parents[2] / "recipes/aero_cfd" / stage, folder / stage)
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg))
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "分片验收", source=folder)
    trained = task.submit_run(project, item["id"], input_keys=["inputs.trainprep.dataset"])
    trained = task.wait_run(project, trained["id"], timeout=180)
    assert trained["status"] == "succeeded", task.read_log(project, trained["id"])
    cp = next(
        c for c in task.list_inference_checkpoints(project, item["id"]) if c["name"] == "last.pt"
    )
    initial = task.read_configuration(project, item["id"])
    request = {
        "expected_revision": initial["revision"],
        "checkpoints": [{"id": cp["id"], "revision": cp["revision"]}],
        "sample_selection": [{"split": s, "sample": "Sample001"} for s in ["train", "test"]],
        "fields": ["surface:cp:scalar"],
        "metrics": ["mae", "rmse"],
        "device": "cpu",
        "options": {"evaluate": True, "save_predictions": False, "export_vtk": False},
        "idempotency_key": "partial",
    }
    from ai4e_task.tasks import inference, inference_worker
    from ai4e_task.tasks.query import get_stage_summary

    launch = inference._launch
    monkeypatch.setattr(inference, "_launch", lambda *_: None)
    submit = inference_worker.submit_run

    def broken_first(*args, **kwargs):
        # 只向首个隔离子进程注入无效指标，实际算法进程必须报告失败。
        if kwargs["metadata"]["split"] == "train":
            kwargs["overrides"] += ['infer.metrics=["invalid_metric"]']
        return submit(*args, **kwargs)

    monkeypatch.setattr(inference_worker, "submit_run", broken_first)
    batch = task.submit_inference(project, item["id"], request)
    inference_worker.coordinate(project, item["id"], batch["id"])
    failed = task.read_inference_batch(project, item["id"], batch["id"])
    assert failed["status"] == "partial", failed
    assert [c["status"] for c in failed["children"]] == ["failed", "succeeded"]
    assert get_stage_summary(project, item["id"])["infer"]["status"] == "partial"
    assert len({c["checkpoint"]["fixed"]["path"] for c in failed["children"]}) == 1
    result = task.inference_results(project, item["id"], batch["id"])
    assert len(result["items"]) == 1 and not result["items"][0]["files"]
    assert result["items"][0]["split"] == "test" and result["statistics"]
    retained = failed["children"][1]["run_id"]
    monkeypatch.setattr(inference_worker, "submit_run", submit)
    retry = task.retry_inference(project, item["id"], batch["id"], idempotency_key="retry")
    assert retry["subrun_count"] == retry["checkpoint_count"] == 1
    assert retry["inherited_children"][0]["run_id"] == retained
    launch(project, item["id"], retry["id"])
    done = wait_batch(project, item["id"], retry["id"])
    assert done["status"] == "succeeded", done
    result = task.inference_results(project, item["id"], retry["id"])
    assert {(r["split"], r["sample"]) for r in result["items"]} == {
        ("train", "Sample001"),
        ("test", "Sample001"),
    }
    assert all(not r["files"] for r in result["items"])
    assert retained in {r["run_id"] for r in result["items"]}
    assert task.read_configuration(project, item["id"]) == initial
    assert len(task.get_lineage(project)) == 1
    canceled = task.submit_inference(project, item["id"], {**request, "idempotency_key": "cancel"})
    task.cancel_inference(project, item["id"], canceled["id"])
    inference_worker.coordinate(project, item["id"], canceled["id"])
    assert task.read_inference_batch(project, item["id"], canceled["id"])["status"] == "canceled"
