"""结果目录分组、固定身份与坏分支隔离。"""

import ai4e_task as task

from tests.integration.test_task_post_metrics import (
    results_project as results_project,  # noqa: PLC0414 - pytest跨模块夹具
)


def test_catalog_complete_and_noncolliding(results_project):
    result = task.post_results(results_project, "t")
    assert len(result["items"]) == 8
    assert result["files"] == []
    assert all(i["evaluable"] for i in result["items"])
    assert len({i["batch_id"] for i in result["items"]}) == 2
    top = task.list_post_result_files(results_project, "t")
    assert top["files"] and all(f.get("directory") for f in top["files"])
    sample = result["items"][0]
    listed = task.list_post_result_files(
        results_project, "t", directory=f"{sample['tree_prefix']}/结果/{sample['sample']}"
    )
    assert listed["files"] and all(not f.get("directory") for f in listed["files"])
    assert len({f["id"] for f in listed["files"]}) == len(listed["files"])


def test_missing_member_keeps_other_samples(results_project):
    initial = task.post_results(results_project, "t")
    from pathlib import Path

    Path(initial["items"][0]["files"][1]["path"]).unlink()
    result = task.post_results(results_project, "t")
    assert len(result["items"]) == 7 and result["errors"]


def test_corrupt_batch_state_keeps_other_batch(results_project):
    (results_project / "tasks/t/.dojo/inference_batches/b0/state.json").write_text("bad json")
    result = task.post_results(results_project, "t")
    assert len(result["items"]) == 4
    assert result["errors"][0]["batch_id"] == "b0"


def test_vector_header_and_missing_truth(results_project):
    import json
    from pathlib import Path

    import torch

    initial = task.post_results(results_project, "t")
    item = initial["items"][0]
    manifest = Path(item["manifest"])
    record = json.loads(manifest.read_text())
    for suffix in ("prediction", "truth"):
        torch.save(
            torch.ones(3, 3), manifest.parent / record["filemap"]["surface.pressure." + suffix]
        )
    result = task.post_results(results_project, "t")
    fields = next(i for i in result["items"] if i["id"] == item["id"])["fields"]
    assert {f["component"] for f in fields} == {"magnitude", "0", "1", "2"}
    del record["filemap"]["surface.pressure.truth"]
    manifest.write_text(json.dumps(record))
    result = task.post_results(results_project, "t")
    missing = next(i for i in result["items"] if i["id"] == item["id"])
    assert not missing["evaluable"] and missing["evaluation_error"]
