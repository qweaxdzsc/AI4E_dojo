"""平台固定资产、场景修订与阶段配置的真实服务验收。"""

import time

from ai4e_server.bootstrap.app import create_app
from fastapi.testclient import TestClient

from tests.integration.test_web_project_task import platform as _platform

platform = _platform


def test_fixed_asset_scene_revision_and_scope(platform):
    client, project, _, data, settings = platform
    path = data / "field.txt"
    path.write_text("real data")
    base = f"/api/v1/projects/{project}"
    ref = client.post(base + "/assets", json={"root": "data0", "path": "field.txt"}).json()
    assert client.get(base + f"/assets/{ref['asset_id']}/content").text == "real data"
    document = {
        "schema_version": 1,
        "sources": [ref],
        "pipeline_nodes": [],
        "representations": [],
        "viewports": [],
        "link_groups": [],
        "active_view": None,
        "selected_node": None,
    }
    saved = client.post(base + "/scenes", json={"scene": document})
    assert saved.status_code == 200, saved.text
    value = saved.json()
    assert (
        client.put(
            base + "/scenes/" + value["scene_id"],
            json={"scene": document, "expected_revision": "wrong"},
        ).status_code
        == 409
    )
    with TestClient(create_app(settings)) as other:
        assert other.get(base + "/scenes/" + value["scene_id"]).json() == value
    path.write_text("changed")
    assert client.get(base + f"/assets/{ref['asset_id']}/content").status_code == 409
    assert (
        client.post(base + "/assets", json={"root": "data0", "path": "../escape"}).status_code
        == 400
    )


def test_stage_revision_readonly_statistics_and_versions(platform):
    c, p, t, _, _ = platform
    base = f"/api/v1/projects/{p}/tasks/{t['id']}/configuration"
    value = c.get(base + "?stage=train").json()
    values = {**value["values"], "max_epochs": 3}
    body = {"stage": "train", "expected_revision": value["revision"], "values": values}
    saved = c.put(base, json=body)
    assert saved.status_code == 200, saved.text
    assert c.put(base, json=body).status_code == 409
    forbidden = {
        "stage": "trainprep",
        "expected_revision": saved.json()["revision"],
        "values": {"normalization": {"fields": {"pressure": {"mean": 0}}}},
    }
    assert c.put(base, json=forbidden).status_code == 400
    assert len(c.get(f"/api/v1/projects/{p}/lineage").json()) == 1


def test_real_text_worker_and_idempotency(platform):
    c, p, _, data, _ = platform
    (data / "sample.txt").write_text("真实文本\nsecond line\n")
    base = f"/api/v1/projects/{p}"
    ref = c.post(base + "/assets", json={"root": "data0", "path": "sample.txt"}).json()
    body = {"source": ref, "operation": "inspect", "idempotency_key": "inspect-one"}
    response = c.post(base + "/previews/operations", json=body)
    assert response.status_code == 200, response.text
    value = response.json()
    assert (
        c.post(base + "/previews/operations", json=body).json()["operation_id"]
        == value["operation_id"]
    )
    deadline = time.monotonic() + 30
    while (
        value["status"] not in {"succeeded", "failed", "canceled"} and time.monotonic() < deadline
    ):
        time.sleep(0.05)
        value = c.get(base + "/operations/" + value["operation_id"]).json()
    assert value["status"] == "succeeded", value
    assert value["result"]
    body["operation"] = "summarize"
    assert c.post(base + "/previews/operations", json=body).status_code == 409


def test_scene_dangling_links_and_same_content_symlink(platform, tmp_path):
    c, p, _, data, _ = platform
    base = f"/api/v1/projects/{p}"
    source = data / "file.txt"
    source.write_text("same")
    ref = c.post(base + "/assets", json={"root": "data0", "path": "file.txt"}).json()
    outside = tmp_path / "outside.txt"
    outside.write_text("same")
    source.unlink()
    source.symlink_to(outside)
    assert c.get(base + f"/assets/{ref['asset_id']}/content").status_code == 400
    document = {
        "schema_version": 1,
        "sources": [],
        "pipeline_nodes": [],
        "representations": [],
        "viewports": [{"id": "one"}],
        "link_groups": [{"kind": "camera", "enabled": True, "view_ids": ["one", "missing"]}],
        "active_view": "one",
        "selected_node": None,
    }
    assert c.post(base + "/scenes", json={"scene": document}).status_code == 400


def test_restart_marks_abandoned_operation_interrupted(platform):
    c, p, _, _, settings = platform
    value = {
        "operation_id": "lost",
        "project_id": p,
        "kind": "visualization",
        "status": "running",
        "phase": None,
        "progress": None,
        "result_refs": [],
        "error": None,
        "event_cursor": 1,
    }
    c.app.state.services.store.put("operation", "lost", value)
    with TestClient(create_app(settings)) as other:
        result = other.get(f"/api/v1/projects/{p}/operations/lost").json()
        assert result["status"] == "interrupted"
        assert result["event_cursor"] == 2


def test_registered_cases_created_before_version_snapshot(platform):
    import ai4e_task as task

    c, p, _, _, _ = platform
    url = f"/api/v1/projects/{p}/tasks"
    available = c.get(url + "/cases").json()
    assert {item["id"] for item in available} == {
        "shapenet_car_abupt",
        "shapenet_car_transolver3_surface",
        "shapenet_car_transolver3_volume",
        "nasa_crm_abupt",
        "nasa_crm_transolver3",
    }
    for case in available:
        assert case["dataset_id"] in {"shapenet_car", "nasa_crm"}
        assert case["model_id"] in {"abupt", "transolver3"}
        assert case["binding_mode"] in {"directory", "files"}
        response = c.post(url, json={"name": case["id"], "case_id": case["id"]})
        assert response.status_code == 200, response.text
        created = response.json()
        cfg = task.read_configuration(c.app.state.services.project(p), created["id"])["config"]
        assert ("nasa_crm" in cfg["components"]["dataset"]) == case["id"].startswith("nasa")
        assert task.compare_worktree(c.app.state.services.project(p), created["id"])["files"] == []
    assert c.post(url, json={"name": "bad", "case_id": "../../untrusted"}).status_code == 400


def test_trial_mode_and_stale_revision_submission(tmp_path):
    import ai4e_task as task
    import pytest

    from tests.integration.test_task_management import recipe

    task.create_project(tmp_path / "project", name="modes")
    root = tmp_path / "project"
    created = task.new_task(root, "sample", source=recipe(tmp_path))
    config = task.read_configuration(root, created["id"])
    with pytest.raises(ValueError, match="revision_conflict"):
        task.submit_run(root, created["id"], expected_revision="outdated")
    result = task.wait_run(
        root,
        task.submit_run(
            root, created["id"], operation_mode="trial", expected_revision=config["revision"]
        )["id"],
    )
    assert result["status"] == "succeeded", result
    assert result["operation_mode"] == "trial"
    assert task.list_stage_artifacts(root, created["id"]) == []


def test_sampling_save_migrates_old_single_key(platform):
    import ai4e_task as task

    c, p, t, _, _ = platform
    base = c.app.state.services.project(p)
    cfg = task.read_configuration(base, t["id"])
    # 旧任务持久化树单独迁移，不重写旧运行快照。
    from pathlib import Path

    from omegaconf import OmegaConf

    path = Path(task.get_task(base, t["id"])["directory"]) / "recipe/config.yaml"
    raw = OmegaConf.load(path)
    raw.trainprep.sampling = raw.model.pop("sampling")
    OmegaConf.save(raw, path)
    cfg = task.read_configuration(base, t["id"])
    saved = task.save_configuration(
        base,
        t["id"],
        {"model": {"sampling": dict(cfg["config"]["trainprep"]["sampling"])}},
        revision=cfg["revision"],
    )
    assert "sampling" not in saved["config"]["trainprep"]
    assert saved["config"]["model"]["sampling"]


def test_stage_input_capture_preserves_strict_downstream(tmp_path):
    """原始阶段不要求尚未产出的下游清单，下游消费仍严格。"""
    import ai4e_task as task
    import pytest

    from tests.integration.test_task_management import recipe

    template = recipe(tmp_path)
    root = tmp_path / "p"
    task.create_project(root, name="stage inputs")
    created = task.new_task(root, "sample", source=template)
    cfg = task.read_configuration(root, created["id"])
    task.save_configuration(
        root,
        created["id"],
        {"inputs": {"train": {"dataset": str(tmp_path / "not_yet_produced.json")}}},
        revision=cfg["revision"],
    )
    with pytest.raises(FileNotFoundError):
        task.submit_run(root, created["id"], overrides=["pipeline.stages=[train]"])
    result = task.wait_run(root, task.submit_run(root, created["id"])["id"])
    assert result["status"] == "succeeded", result


def test_transport_nonfinite_keeps_success_and_nulls_nested(tmp_path):
    """Infinity best 是缺失评价，不应把已成功训练伪装成 HTTP 失败。"""
    import json

    import ai4e_task as task
    from ai4e_server.bootstrap.settings import Settings

    from tests.integration.test_task_management import recipe

    settings = Settings(tmp_path / "platform", recipe(tmp_path))
    with TestClient(create_app(settings)) as c:
        p = c.post("/api/v1/projects", json={"name": "finite"}).json()["id"]
        t = c.post(f"/api/v1/projects/{p}/tasks", json={"name": "run"}).json()["id"]
        base = c.app.state.services.project(p)
        run = task.wait_run(base, task.submit_run(base, t)["id"])
        path = base / run["run_path"] / "summary.json"
        summary = json.loads(path.read_text())
        summary.setdefault("reports", {})["train"] = {
            "best": float("inf"),
            "history": [
                {"loss": float("nan"), "evaluation": {"metrics": {"x": {"value": float("-inf")}}}}
            ],
        }
        path.write_text(json.dumps(summary))
        url = f"/api/v1/projects/{p}/runs"
        for response in [
            c.get(url),
            c.get(url + "/" + run["id"]),
            c.get(url + "/" + run["id"] + "/metrics"),
        ]:
            assert response.status_code == 200, response.text
            assert "Infinity" not in response.text and "NaN" not in response.text
        detail = c.get(url + "/" + run["id"]).json()
        assert detail["status"] == "succeeded"
        assert detail["summary"]["reports"]["train"]["best"] is None
        assert (
            detail["summary"]["reports"]["train"]["history"][0]["evaluation"]["metrics"]["x"][
                "value"
            ]
            is None
        )
        assert json.loads(path.read_text())["reports"]["train"]["best"] == float("inf")


def test_dataset_sources_are_controlled_and_revision_protected(platform):
    client, project, record, data, _ = platform
    (data / "training.h5").write_bytes(b"controlled test fixture")
    record = client.post(
        f"/api/v1/projects/{project}/tasks",
        json={"name": "NASA binding", "case_id": "nasa_crm_abupt"},
    ).json()
    base = f"/api/v1/projects/{project}/tasks/{record['id']}"
    revision = client.get(base + "/configuration").json()["revision"]
    body = {
        "expected_revision": revision,
        "sources": {
            key: {"root": "data0", "path": "training.h5"}
            for key in ("train_h5", "test_h5", "connectivity_h5")
        },
    }
    response = client.put(base + "/dataset", json=body)
    assert response.status_code == 200, response.text
    assert client.put(base + "/dataset", json=body).status_code == 409
    body["expected_revision"] = response.json()["revision"]
    body["sources"]["train_h5"]["path"] = "../escape.h5"
    assert client.put(base + "/dataset", json=body).status_code == 400


def test_configuration_remains_editable_when_inspection_unavailable(platform, monkeypatch):
    import ai4e_task

    client, project, record, _, _ = platform

    def unavailable(*args, **kwargs):
        raise ValueError("component temporarily unavailable")

    monkeypatch.setattr(ai4e_task, "inspect_task", unavailable)
    response = client.get(
        f"/api/v1/projects/{project}/tasks/{record['id']}/configuration?stage=train"
    )
    assert response.status_code == 200
    assert "max_epochs" in response.json()["values"]
    assert (
        response.json()["capabilities"]["unavailable_reason"] == "component temporarily unavailable"
    )


def test_shared_workflow_metrics_read_real_physical_report(tmp_path, monkeypatch):
    import json

    from ai4e_task.tasks import query
    from ai4e_task.tasks.artifacts import read_run_metrics

    folder = tmp_path / "artifacts"
    folder.mkdir()
    metrics = {"surface.pressure": {"mse": 1.25, "mae": 0.8, "relative_l2": 0.2}}
    (folder / "physical-predictions.json").write_text(
        json.dumps({"status": "succeeded", "metrics": metrics})
    )
    monkeypatch.setattr(
        query, "get_run", lambda *args: {"status": "succeeded", "run_dir": str(tmp_path)}
    )
    assert read_run_metrics(tmp_path, "actual")["evaluation"]["metrics"] == metrics


def test_shutdown_reaps_auxiliary_process_and_preserves_task_run(platform, tmp_path):
    import subprocess
    import sys

    import ai4e_task as task
    from ai4e_server.modules.visualization import application

    from tests.integration.test_task_management import recipe

    client, project, _, _, settings = platform
    base = client.app.state.services.project(project)
    fixture_root = tmp_path / "research-fixture"
    fixture_root.mkdir()
    record = task.new_task(base, "shutdown-research", source=recipe(fixture_root))
    run = task.submit_run(base, record["id"], overrides=["delay=1"])
    auxiliary = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        with TestClient(create_app(settings)) as service_client:
            service = service_client.app.state.services
            identity = "shutdown-process-fixture"
            output = settings.root / "display" / identity
            output.mkdir(parents=True)
            (output / "partial.bin").write_bytes(b"partial")
            service.store.put(
                "operation",
                identity,
                {
                    "operation_id": identity,
                    "project_id": project,
                    "status": "running",
                    "event_cursor": 0,
                },
            )
            application._PROCESSES[identity] = auxiliary
        assert auxiliary.poll() is not None
        assert not output.exists()
        assert application._PROCESSES.get(identity) is None
        assert task.wait_run(base, run["id"])["status"] == "succeeded"
        with TestClient(create_app(settings)) as restarted:
            assert restarted.get(f"/api/v1/projects/{project}/runs/{run['id']}").status_code == 200
    finally:
        if auxiliary.poll() is None:
            auxiliary.kill()
        auxiliary.wait(timeout=2)


def test_shared_real_viz_subscriptions_last_cancel_and_cache(platform):
    import torch
    from ai4e_server.modules.visualization import application

    client, project, _, data, _ = platform
    torch.save(torch.arange(1000), data / "shared.pt")
    base = f"/api/v1/projects/{project}"
    ref = client.post(base + "/assets", json={"root": "data0", "path": "shared.pt"}).json()
    forbidden = client.post(
        base + "/previews/operations",
        json={
            "source": ref,
            "operation": "inspect",
            "options": {"coordinate_space": {"id": "invented", "unit": "m"}},
        },
    )
    assert forbidden.status_code == 400
    application._CAPACITY.acquire()
    try:
        first = client.post(
            base + "/previews/operations", json={"source": ref, "operation": "inspect"}
        ).json()
        second = client.post(
            base + "/previews/operations",
            json={
                "source": {**ref, "name": "another display label"},
                "operation": "inspect",
                "idempotency_key": "second-viewer",
            },
        ).json()
        assert first["operation_id"] == second["operation_id"]
        assert first["subscription_id"] != second["subscription_id"]
    finally:
        application._CAPACITY.release()
    identity = first["operation_id"]
    deadline = time.monotonic() + 5
    while identity not in application._PROCESSES and time.monotonic() < deadline:
        time.sleep(0.005)
    process = application._PROCESSES[identity]
    canceled = client.post(
        base + f"/operations/{identity}/cancel", json={"subscription_id": first["subscription_id"]}
    )
    assert canceled.json()["status"] in {"queued", "running"}
    assert process.poll() is None
    canceled = client.post(
        base + f"/operations/{identity}/cancel", json={"subscription_id": second["subscription_id"]}
    )
    assert canceled.json()["status"] == "canceled"
    assert process.poll() is not None
    third = client.post(
        base + "/previews/operations", json={"source": ref, "operation": "inspect"}
    ).json()
    deadline = time.monotonic() + 30
    while third["status"] not in application.TERMINAL and time.monotonic() < deadline:
        time.sleep(0.05)
        third = client.get(base + "/operations/" + third["operation_id"]).json()
    assert third["status"] == "succeeded", third
    cached = client.post(
        base + "/previews/operations", json={"source": ref, "operation": "inspect"}
    ).json()
    assert cached["operation_id"] == third["operation_id"]
    torch.save(torch.arange(2), data / "shared.pt")
    assert (
        client.post(
            base + "/previews/operations", json={"source": ref, "operation": "inspect"}
        ).status_code
        == 409
    )


def test_version_stage_details_remain_creation_snapshot(platform):
    client, project, record, _, _ = platform
    base = f"/api/v1/projects/{project}"
    original = client.get(base + "/lineage/" + record["version_id"])
    assert original.status_code == 200, original.text
    original = original.json()
    assert original["source"] == "creation_snapshot"
    config = client.get(base + f"/tasks/{record['id']}/configuration").json()
    changed = client.put(
        base + f"/tasks/{record['id']}/configuration",
        json={
            "stage": "train",
            "expected_revision": config["revision"],
            "values": {"max_epochs": 99},
        },
    )
    assert changed.status_code == 200, changed.text
    current = client.get(base + "/lineage/" + record["version_id"]).json()
    assert current == original
    compared = client.post(
        base + "/compare",
        json={
            "mode": "versions",
            "left": record["version_id"],
            "right": record["version_id"],
            "parameter": "train.max_epochs",
        },
    ).json()
    assert compared["parameter_comparison"]["source"] == "creation_snapshot"
    assert compared["parameter_comparison"]["left"]["value"] != 99
    assert (
        next(s for s in current["stages"] if s["stage"] == "train")["configuration"]["max_epochs"]
        != 99
    )
