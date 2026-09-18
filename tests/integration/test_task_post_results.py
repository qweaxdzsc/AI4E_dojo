"""结果目录分组、固定身份与坏分支隔离。"""

import ai4e_task as task
from ai4e_task.storage.database import transaction
from ai4e_task.storage.records import put

from tests.integration.test_task_post_metrics import (
    results_project as results_project,  # noqa: PLC0414 - pytest跨模块夹具
)


def _project_with_run(tmp_path, *, run_id, stages, files=(), extras=(), status="succeeded"):
    root = tmp_path / "project"
    task.create_project(root)
    with transaction(root) as db:
        put(db, "task", {"id": "t", "version_id": "v", "archived": False})
    run_dir = root / "tasks/t/runs" / run_id
    data_dir = root / "tasks/t/data" / run_id
    (run_dir / "checkpoints").mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True)
    (run_dir / "checkpoints/last.pt").write_bytes(b"ckpt")
    (run_dir / "logs/run.log").write_text("train log")
    (run_dir / "summary.json").write_text("{}")
    data_dir.mkdir(parents=True)
    for name in ("infer", "post", "rawprep", "trainprep"):
        (data_dir / name).mkdir()
    for relative, content in files:
        target = data_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content if isinstance(content, bytes) else content.encode())
    for relative, content in extras:
        target = run_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content if isinstance(content, bytes) else content.encode())
    with transaction(root) as db:
        put(
            db,
            "run",
            {
                "id": run_id,
                "task_id": "t",
                "status": status,
                "stages": stages,
                "run_path": str(run_dir.relative_to(root)),
                "data_path": str(data_dir.relative_to(root)),
                "created_at": "2026-09-17T10:00:00+00:00",
            },
        )
    return root


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
    files = [item for item in listed["files"] if not item.get("directory")]
    notes = [item for item in listed["files"] if item.get("empty")]
    assert files
    assert notes and all("未写出VTK" in item["name"] for item in notes)
    assert len({item["id"] for item in listed["files"]}) == len(listed["files"])


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


def test_train_data_results_listed_without_inference(tmp_path):
    root = _project_with_run(
        tmp_path,
        run_id="train1",
        stages=["train"],
        files=(
            ("infer/predictions/car-a/surface.vtp", b"<vtk/>"),
            ("infer/predictions/car-a/pressure.pt", b"pt"),
            ("post/analysis/metrics.json", b"{}"),
        ),
    )
    catalog = task.post_results(root, "t")
    assert catalog["items"] == []
    assert any(item["id"] == "train:train1" for item in catalog["batches"])
    top = task.list_post_result_files(root, "t")
    paths = {item["tree_path"] for item in top["files"]}
    assert "训练运行 · train1" in paths
    assert {item["tree_path"] for item in top["files"] if item.get("directory")} >= {
        "训练运行 · train1"
    }
    infer = task.list_post_result_files(root, "t", directory="训练运行 · train1")
    assert {item["tree_path"] for item in infer["files"]} == {
        "训练运行 · train1/infer",
        "训练运行 · train1/post",
    }
    files = task.list_post_result_files(
        root, "t", directory="训练运行 · train1/infer/predictions/car-a"
    )
    names = {item["name"] for item in files["files"]}
    assert names == {"surface.vtp", "pressure.pt"}
    assert all(not item.get("directory") for item in files["files"])
    mesh = next(item for item in files["files"] if item["name"] == "surface.vtp")
    assert mesh["visualizable"] is True
    searched = task.list_post_result_files(root, "t", query="surface.vtp")
    assert any(item["name"] == "surface.vtp" for item in searched["files"])
    assert not any("last.pt" in item.get("tree_path", "") for item in searched["files"])
    assert not any("run.log" in item.get("tree_path", "") for item in searched["files"])
    records = task.list_post_result_files(root, "t", query="run.log")
    assert records["files"] == []


def test_train_without_result_files_still_lists_run(tmp_path):
    root = _project_with_run(tmp_path, run_id="empty001", stages=["train"])
    catalog = task.post_results(root, "t")
    assert catalog["items"] == []
    assert catalog["batches"] == []
    listed = task.list_post_result_files(root, "t")
    assert {item["tree_path"] for item in listed["files"]} == {"训练运行 · empty001"}
    inner = task.list_post_result_files(root, "t", directory="训练运行 · empty001")
    assert {item["name"] for item in inner["files"]} == {"没有写出预测或网格"}
    assert all(item.get("directory") for item in inner["files"])
    assert all(not item.get("visualizable") for item in inner["files"])
    searched = task.list_post_result_files(root, "t", query="empty001")
    assert any(item["tree_path"] == "训练运行 · empty001" for item in searched["files"])


def test_failed_train_listed_without_fake_results(tmp_path):
    root = _project_with_run(tmp_path, run_id="fail0001", stages=["train"], status="failed")
    listed = task.list_post_result_files(root, "t")
    assert {item["tree_path"] for item in listed["files"]} == {"训练运行 · fail0001"}
    inner = task.list_post_result_files(root, "t", directory="训练运行 · fail0001")
    assert {item["name"] for item in inner["files"]} == {"没有预测或网格（开训失败）"}
    assert all(item.get("directory") for item in inner["files"])
    hidden = task.list_post_result_files(root, "t", status="succeeded")
    assert hidden["files"] == []


def test_rawprep_run_not_listed_as_result_files(tmp_path):
    root = _project_with_run(
        tmp_path,
        run_id="raw1",
        stages=["rawprep"],
        files=(("rawprep/manifest.json", b"{}"),),
    )
    assert task.list_post_result_files(root, "t")["files"] == []


def _publish_dataset(root, *, task_id, name, samples):
    import json

    from ai4e_task.storage.processed_datasets import manifest_digest

    folder = root / "shared/datasets" / name
    content = folder / "content"
    content.mkdir(parents=True)
    entries = []
    partitions = []
    for sample, files in samples:
        sample_dir = content / "train" / sample
        sample_dir.mkdir(parents=True)
        for filename, data in files:
            (sample_dir / filename).write_bytes(data)
        partitions.append(sample)
        entries.append({"sample": sample, "path": str(sample_dir), "partition": "train"})
    manifest = content / "manifest.json"
    manifest.write_text(
        json.dumps({"version": 1, "partitions": {"train": partitions}, "samples": entries})
    )
    (folder / "asset.json").write_text(
        json.dumps(
            {
                "id": name,
                "kind": "dataset",
                "name": name,
                "path": f"shared/datasets/{name}/content/manifest.json",
                "status": "available",
                "source": {"task_id": task_id},
                "created_at": "2026-09-17T10:00:00+00:00",
                "manifest_digest": manifest_digest(manifest),
            }
        )
    )


def test_platform_dataset_listed_with_sample_id(tmp_path):
    root = _project_with_run(tmp_path, run_id="empty001", stages=["train"])
    _publish_dataset(
        root,
        task_id="t",
        name="shapenet_car2",
        samples=(
            (
                "param1/1dc58be25e1b6e5675cad724c63e222e",
                (("surface_pressure.pt", b"pt"), ("surface.vtkhdf", b"vtk")),
            ),
        ),
    )
    catalog = task.post_results(root, "t")
    assert any(item["id"] == "dataset:shapenet_car2" for item in catalog["batches"])
    top = task.list_post_result_files(root, "t")
    paths = {item["tree_path"] for item in top["files"]}
    assert "训练运行 · empty001" in paths
    assert "平台数据集 · shapenet_car2" in paths
    assert [item["tree_path"] for item in top["files"] if item.get("directory")].index(
        "平台数据集 · shapenet_car2"
    ) < [item["tree_path"] for item in top["files"]].index("训练运行 · empty001")
    samples = task.list_post_result_files(root, "t", directory="平台数据集 · shapenet_car2")
    assert {item["name"] for item in samples["files"]} == {
        "param1/1dc58be25e1b6e5675cad724c63e222e"
    }
    assert {item["tree_path"] for item in samples["files"]} == {
        "平台数据集 · shapenet_car2/param1／1dc58be25e1b6e5675cad724c63e222e"
    }
    assert all(
        item.get("sample") == "param1/1dc58be25e1b6e5675cad724c63e222e" for item in samples["files"]
    )
    files = task.list_post_result_files(
        root,
        "t",
        directory="平台数据集 · shapenet_car2/param1／1dc58be25e1b6e5675cad724c63e222e",
    )
    names = {item["name"] for item in files["files"]}
    assert names == {"surface_pressure.pt", "surface.vtkhdf"}
    mesh = next(item for item in files["files"] if item["name"] == "surface.vtkhdf")
    assert mesh["visualizable"] is True
    assert mesh["sample"] == "param1/1dc58be25e1b6e5675cad724c63e222e"
    searched = task.list_post_result_files(root, "t", query="1dc58be25e1b6e5675cad724c63e222e")
    assert any(
        item.get("sample") == "param1/1dc58be25e1b6e5675cad724c63e222e"
        for item in searched["files"]
    )


def test_standalone_infer_run_without_batch_is_listed(tmp_path):
    root = _project_with_run(
        tmp_path,
        run_id="infer1",
        stages=["infer"],
        files=(("infer/predictions/sample/surface.vtp", b"<vtk/>"),),
    )
    top = task.list_post_result_files(root, "t")
    assert any(item["tree_path"] == "推理运行 · infer1" for item in top["files"])
    catalog = task.post_results(root, "t")
    assert any(item["id"] == "infer:infer1" for item in catalog["batches"])


def test_infer_sample_without_vtk_lists_reason(tmp_path):
    import json

    sample = "param1/1dc757e77f3cfad0253c03b7df20edd5"
    root = _project_with_run(tmp_path, run_id="infer2", stages=["infer"])
    dest = root / "tasks/t/data/infer2/infer/predictions" / sample
    dest.mkdir(parents=True)
    (dest / "surface.pressure.prediction.pt").write_bytes(b"pt")
    manifest = dest / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "identity": {"sample": sample, "split": "test"},
                "domains": {},
                "filemap": {"surface.pressure.prediction": "surface.pressure.prediction.pt"},
                "vtk": {"exported": False, "reason": "用户关闭了导出网格"},
            }
        )
    )
    report = root / "tasks/t/runs/infer2/artifacts/inference-results.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"results": [{"sample": sample, "manifest": str(manifest)}]}))
    listed = task.list_post_result_files(
        root, "t", directory=f"推理运行 · infer2/结果/{sample.replace('/', '／')}"
    )
    names = {item["name"] for item in listed["files"]}
    assert "manifest.json" in names
    assert any(
        item.get("empty") and "未写出VTK：用户关闭了导出网格" in item["name"]
        for item in listed["files"]
    )
