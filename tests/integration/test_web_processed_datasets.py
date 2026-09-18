"""平台已处理数据集登记、同名冲突与跨项目可见。"""

from pathlib import Path

import ai4e_task as task
import pytest

from tests.integration import test_web_dataset_binding as binding_cases

binding_platform = binding_cases.binding_platform
create = binding_cases.create
sources = binding_cases.sources


def _manifest(path: Path, payload: str = "sample") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps({"version": 1, "state": "physical", "payload": payload}))
    return path


def test_register_visible_to_other_project(binding_platform):
    client, base, _, settings = binding_platform
    first = create(client, base, "shapenet_car_abupt")
    project = Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))
    manifest = _manifest(project / "tasks" / first["id"] / "data" / "run" / "manifest.json")
    record = task.register_processed_dataset(
        settings.root,
        "shapenet_car",
        manifest_path=manifest,
        digest=task.manifest_digest(manifest),
        provenance={"task_id": first["id"], "run_id": "run-a"},
    )
    assert record["status"] == "available"
    other = client.post("/api/v1/projects", json={"name": "another"})
    assert other.status_code == 200, other.text
    listed = client.get("/api/v1/datasets").json()
    assert any(item["name"] == "shapenet_car" and item["status"] == "available" for item in listed)
    child = create(client, "/api/v1/projects/" + other.json()["id"], "shapenet_car_abupt")
    inputs = client.get(
        "/api/v1/projects/" + other.json()["id"] + "/tasks/" + child["id"] + "/stage-inputs"
    ).json()
    names = [
        item.get("processed_name") or item["name"]
        for item in inputs
        if item["binding"] == "inputs.trainprep.dataset" and item.get("origin") == "platform"
    ]
    assert "shapenet_car" in names
    chosen = next(item for item in inputs if item.get("processed_name") == "shapenet_car")
    assert chosen["ref"] and chosen["compatibility"]["status"] != "invalid"
    manifest_ids = [
        item["ref"]["asset_id"]
        for item in inputs
        if item["binding"] == "inputs.trainprep.dataset" and item.get("ref")
    ]
    assert len(manifest_ids) == len(set(manifest_ids))


def test_stage_inputs_keep_platform_name_not_run_duplicate(binding_platform, monkeypatch):
    from ai4e_task.tasks import artifacts

    client, base, _, settings = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    project = Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))
    data_dir = project / "tasks" / created["id"] / "data" / "run"
    manifest = _manifest(data_dir / "manifest.json")
    task.register_processed_dataset(
        settings.root,
        "shapenet_car",
        manifest_path=manifest,
        digest=task.manifest_digest(manifest),
        provenance={"task_id": created["id"], "run_id": "b8517271xxxx"},
    )
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "b8517271xxxx",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data_dir),
                "run_dir": str(data_dir / "missing-run"),
            }
        ],
    )
    inputs = client.get(base + "/tasks/" + created["id"] + "/stage-inputs").json()
    manifests = [item for item in inputs if item["binding"] == "inputs.trainprep.dataset" and item.get("ref")]
    assert len(manifests) == 1
    assert manifests[0]["origin"] == "platform"
    assert manifests[0]["processed_name"] == "shapenet_car"
    assert not any(
        item.get("origin") == "run" for item in inputs if item["binding"] == "inputs.trainprep.dataset"
    )


def test_processed_datasets_list_newest_first(tmp_path):
    from ai4e_task.storage.files import read_json, write_json

    workspace = tmp_path / "workspace"
    older = _manifest(tmp_path / "older" / "manifest.json", "older")
    newer = _manifest(tmp_path / "newer" / "manifest.json", "newer")
    task.register_processed_dataset(
        workspace, "zeta_old", manifest_path=older, digest=task.manifest_digest(older)
    )
    task.register_processed_dataset(
        workspace, "alpha_new", manifest_path=newer, digest=task.manifest_digest(newer)
    )
    old_path = workspace / "datasets" / "zeta_old" / "dataset.json"
    new_path = workspace / "datasets" / "alpha_new" / "dataset.json"
    write_json(old_path, {**read_json(old_path), "created_at": "2026-01-01T00:00:00+00:00"})
    write_json(new_path, {**read_json(new_path), "created_at": "2026-09-15T12:00:00+00:00"})
    listed = task.list_processed_datasets(workspace)
    assert [item["name"] for item in listed] == ["alpha_new", "zeta_old"]


def test_processed_datasets_missing_created_at_uses_mtime(tmp_path):
    import os
    import time

    from ai4e_task.storage.files import read_json, write_json

    workspace = tmp_path / "workspace"
    older = _manifest(tmp_path / "older" / "manifest.json", "older")
    newer = _manifest(tmp_path / "newer" / "manifest.json", "newer")
    task.register_processed_dataset(
        workspace, "zeta_old", manifest_path=older, digest=task.manifest_digest(older)
    )
    task.register_processed_dataset(
        workspace, "alpha_new", manifest_path=newer, digest=task.manifest_digest(newer)
    )
    old_path = workspace / "datasets" / "zeta_old" / "dataset.json"
    new_path = workspace / "datasets" / "alpha_new" / "dataset.json"
    for path in (old_path, new_path):
        record = read_json(path)
        record.pop("created_at", None)
        write_json(path, record)
    older_ts = time.time() - 3600
    newer_ts = time.time()
    os.utime(old_path, (older_ts, older_ts))
    os.utime(new_path, (newer_ts, newer_ts))
    listed = task.list_processed_datasets(workspace)
    assert [item["name"] for item in listed] == ["alpha_new", "zeta_old"]


def test_processed_datasets_same_time_sorts_by_name(tmp_path):
    from ai4e_task.storage.files import read_json, write_json

    workspace = tmp_path / "workspace"
    first = _manifest(tmp_path / "first" / "manifest.json", "first")
    second = _manifest(tmp_path / "second" / "manifest.json", "second")
    task.register_processed_dataset(
        workspace, "zeta_old", manifest_path=first, digest=task.manifest_digest(first)
    )
    task.register_processed_dataset(
        workspace, "alpha_new", manifest_path=second, digest=task.manifest_digest(second)
    )
    stamp = "2026-09-15T12:00:00+00:00"
    for name in ("zeta_old", "alpha_new"):
        path = workspace / "datasets" / name / "dataset.json"
        write_json(path, {**read_json(path), "created_at": stamp})
    listed = task.list_processed_datasets(workspace)
    assert [item["name"] for item in listed] == ["alpha_new", "zeta_old"]


def test_stage_inputs_platform_names_newest_first(binding_platform):
    from ai4e_task.storage.files import read_json, write_json

    client, base, _, settings = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    older = _manifest(settings.root / "older" / "manifest.json", "older")
    newer = _manifest(settings.root / "newer" / "manifest.json", "newer")
    task.register_processed_dataset(
        settings.root, "zeta_old", manifest_path=older, digest=task.manifest_digest(older)
    )
    task.register_processed_dataset(
        settings.root, "alpha_new", manifest_path=newer, digest=task.manifest_digest(newer)
    )
    write_json(
        settings.root / "datasets" / "zeta_old" / "dataset.json",
        {
            **read_json(settings.root / "datasets" / "zeta_old" / "dataset.json"),
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )
    write_json(
        settings.root / "datasets" / "alpha_new" / "dataset.json",
        {
            **read_json(settings.root / "datasets" / "alpha_new" / "dataset.json"),
            "created_at": "2026-09-15T12:00:00+00:00",
        },
    )
    inputs = client.get(base + "/tasks/" + created["id"] + "/stage-inputs").json()
    names = [item.get("processed_name") for item in inputs if item.get("origin") == "platform"]
    assert "alpha_new" in names and "zeta_old" in names
    assert names.index("alpha_new") < names.index("zeta_old")
    assert next(
        item["created_at"] for item in inputs if item.get("processed_name") == "alpha_new"
    ).startswith("2026-09-15")
    public = client.get("/api/v1/datasets").json()
    assert [item["name"] for item in public].index("alpha_new") < [
        item["name"] for item in public
    ].index("zeta_old")
    assert next(item["created_at"] for item in public if item["name"] == "alpha_new").startswith(
        "2026-09-15"
    )


def test_describe_does_not_treat_dataset_id_as_saved_name(binding_platform):
    client, base, _, _ = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    cfg = client.get(base + "/tasks/" + created["id"] + "/rawprep").json()
    assert cfg.get("processed_name") in ("", None)
    assert cfg["profile"]["dataset_id"] == "shapenet_car"


def test_empty_name_rejects_execute(binding_platform):
    client, base, _, _ = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={"expected_revision": initial["revision"], "sources": sources("shapenet_car_abupt")},
    )
    assert bound.status_code == 200, bound.text
    cfg = client.get(url + "/rawprep").json()
    rejected = client.post(
        url + "/rawprep/execute",
        json={"revision": cfg["revision"], "sample_scope": {"mode": "all", "values": []}},
    )
    assert rejected.status_code == 400
    assert "processed_dataset_name" in rejected.text


def test_saved_name_passes_name_gate(binding_platform):
    client, base, _, _ = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={"expected_revision": initial["revision"], "sources": sources("shapenet_car_abupt")},
    )
    assert bound.status_code == 200, bound.text
    cfg = client.get(url + "/rawprep").json()
    assert cfg.get("processed_name") in ("", None)
    saved = client.put(
        url + "/rawprep",
        json={
            "revision": cfg["revision"],
            "rawprep": cfg["rawprep"],
            "processed_name": "shapenet_car",
        },
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["processed_name"] == "shapenet_car"
    submitted = client.post(
        url + "/rawprep/execute",
        json={"revision": saved.json()["revision"], "sample_scope": {"mode": "all", "values": []}},
    )
    assert "processed_dataset_name" not in submitted.text


def test_same_name_different_digest_rejected(tmp_path):
    workspace = tmp_path / "workspace"
    first = _manifest(tmp_path / "a" / "manifest.json", "one")
    second = _manifest(tmp_path / "b" / "manifest.json", "two")
    task.register_processed_dataset(
        workspace, "NASA_CRM", manifest_path=first, digest=task.manifest_digest(first)
    )
    with pytest.raises(ValueError, match="processed_dataset_name_conflict"):
        task.register_processed_dataset(
            workspace, "NASA_CRM", manifest_path=second, digest=task.manifest_digest(second)
        )
    replaced = task.register_processed_dataset(
        workspace,
        "NASA_CRM",
        manifest_path=second,
        digest=task.manifest_digest(second),
        overwrite=True,
    )
    assert replaced["digest"] == task.manifest_digest(second)


def test_resolved_rawprep_and_workers_share_claim():
    stored = {
        "components": {"dataset": "ai4e_contrib.application.datasets.shapenet_car"},
        "dataset": {"root": "/data"},
        "rawprep": {
            "sources": ["volume", "surface"],
            "fields": {"surface": {"pressure": {"components": 1, "array": "p"}}},
            "geometry": ["nearest_vertex", "surface_normals"],
            "save_fields": ["surface_pressure", "surface_position"],
            "filters": {"surface": ["mask"]},
            "statistics": {"mode": "none", "fields": ["surface_pressure"]},
            "format": "pt",
            "vtkhdf": False,
            "workers": 1,
        },
    }
    resolved = {
        **stored,
        "rawprep": {
            **stored["rawprep"],
            "sources": ["surface", "volume"],
            "geometry": {"nearest_vertex": {}, "surface_normals": {}},
            "formats": ["pt"],
            "workers": 10,
            "extraction": None,
        },
    }
    assert task.processed_claim(stored)["identity"] == task.processed_claim(resolved)["identity"]
    assert (
        task.processed_claim(stored)["fingerprint"] == task.processed_claim(resolved)["fingerprint"]
    )


def test_vtkhdf_difference_explains_conflict(tmp_path):
    workspace = tmp_path / "workspace"
    origin = tmp_path / "origin" / "tasks" / "task-a" / "recipe"
    origin.mkdir(parents=True)
    (origin / "config.yaml").write_text(
        "dataset:\n  root: /data\nrawprep:\n  vtkhdf: false\n  sources: [surface]\n"
        "  fields:\n    surface:\n      pressure:\n        components: 1\n"
        "  geometry: [nearest_vertex]\n  format: pt\n  workers: 1\n"
    )
    first = _manifest(tmp_path / "a" / "manifest.json", "one")
    closed = {
        "components": {"dataset": "ai4e_contrib.application.datasets.shapenet_car"},
        "dataset": {"root": "/data"},
        "rawprep": {
            "sources": ["surface"],
            "fields": {"surface": {"pressure": {"components": 1}}},
            "geometry": ["nearest_vertex"],
            "format": "pt",
            "vtkhdf": False,
            "workers": 1,
        },
    }
    opened = {
        **closed,
        "rawprep": {**closed["rawprep"], "vtkhdf": True, "workers": 10},
    }
    task.register_processed_dataset(
        workspace,
        "shapenet_car",
        manifest_path=first,
        digest=task.manifest_digest(first),
        claim=task.processed_claim(closed),
        provenance={"project": str(tmp_path / "origin"), "task_id": "task-a"},
    )
    status = task.describe_processed_name(
        workspace, "shapenet_car", claim=task.processed_claim(opened), config=opened
    )
    assert status["status"] == "conflict"
    assert "VTKHDF" in status["message"]
    assert "并行线程" not in status["message"]
    with pytest.raises(ValueError, match="VTKHDF"):
        task.check_processed_name(
            workspace, "shapenet_car", claim=task.processed_claim(opened), config=opened
        )
    allowed = task.check_processed_name(
        workspace,
        "shapenet_car",
        claim=task.processed_claim(opened),
        config=opened,
        overwrite=True,
    )
    assert allowed["name"] == "shapenet_car"
    assert "覆盖" in status["message"]
    data_dir = tmp_path / "next"
    replacement = _manifest(data_dir / "manifest.json", "next")
    run = {
        "id": "run-next",
        "status": "succeeded",
        "operation_mode": "execute",
        "stages": ["rawprep"],
        "data_dir": str(data_dir),
    }
    opened["dataset"]["processed_name"] = "shapenet_car"
    with pytest.raises(ValueError, match="processed_dataset_name_conflict"):
        task.publish_processed_from_run(
            workspace, tmp_path / "origin", "task-a", run, config=opened
        )
    published = task.publish_processed_from_run(
        workspace,
        tmp_path / "origin",
        "task-a",
        run,
        config=opened,
        overwrite=True,
    )
    assert published["digest"] == task.manifest_digest(replacement)
    assert published["claim"]["identity"]["vtkhdf"] is True


def test_workers_do_not_change_processed_claim(tmp_path):
    base = {
        "components": {"dataset": "ai4e_contrib.application.datasets.shapenet_car"},
        "dataset": {"root": "/data"},
        "rawprep": {
            "sources": ["surface"],
            "fields": {"surface": {"pressure": {"components": 1}}},
        },
    }
    sequential = task.processed_claim(base)
    parallel = task.processed_claim({**base, "rawprep": {**base["rawprep"], "workers": 10}})
    assert sequential == parallel
    first = _manifest(tmp_path / "a" / "manifest.json", "one")
    workspace = tmp_path / "workspace"
    task.register_processed_dataset(
        workspace,
        "shapenet_car2",
        manifest_path=first,
        digest=task.manifest_digest(first),
        claim=sequential,
    )
    checked = task.check_processed_name(workspace, "shapenet_car2", claim=parallel)
    assert checked["name"] == "shapenet_car2"
    second = _manifest(tmp_path / "b" / "manifest.json", "two")
    updated = task.register_processed_dataset(
        workspace,
        "shapenet_car2",
        manifest_path=second,
        digest=task.manifest_digest(second),
        claim=parallel,
    )
    assert updated["digest"] == task.manifest_digest(second)


def test_same_claim_updates_pointer(tmp_path):
    workspace = tmp_path / "workspace"
    first = _manifest(tmp_path / "a" / "manifest.json", "one")
    second = _manifest(tmp_path / "b" / "manifest.json", "two")
    claim = {"fingerprint": "same-intent"}
    task.register_processed_dataset(
        workspace,
        "shapenet_car",
        manifest_path=first,
        digest=task.manifest_digest(first),
        claim=claim,
    )
    updated = task.register_processed_dataset(
        workspace,
        "shapenet_car",
        manifest_path=second,
        digest=task.manifest_digest(second),
        claim=claim,
    )
    assert updated["digest"] == task.manifest_digest(second)
    assert Path(updated["manifest_path"]) == second.resolve()


def test_name_conflict_rejects_execute(binding_platform):
    client, base, _, settings = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    project = Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))
    (project / "shared/datasets/shapenet_car").mkdir(parents=True)
    (project / "shared/datasets/shapenet_car/occupied").write_text("occupied")
    occupied = _manifest(settings.root / "occupied" / "manifest.json", "other")
    task.register_processed_dataset(
        settings.root,
        "shapenet_car",
        manifest_path=occupied,
        digest=task.manifest_digest(occupied),
        claim={"fingerprint": "foreign"},
    )
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={"expected_revision": initial["revision"], "sources": sources("shapenet_car_abupt")},
    )
    assert bound.status_code == 200, bound.text
    cfg = client.get(url + "/rawprep").json()
    saved = client.put(
        url + "/rawprep",
        json={
            "revision": cfg["revision"],
            "rawprep": cfg["rawprep"],
            "processed_name": "shapenet_car",
        },
    )
    assert saved.status_code == 200, saved.text
    rejected = client.post(
        url + "/rawprep/execute",
        json={"revision": saved.json()["revision"], "sample_scope": {"mode": "all", "values": []}},
    )
    assert rejected.status_code == 409
    assert "shared_dataset_exists" in rejected.text
    assert "确认是否覆盖" in rejected.json()["error"]["message"]
    shown = client.get(url + "/rawprep").json()
    assert shown["processed_name_status"]["status"] == "conflict"
    assert "覆盖" in shown["processed_name_status"]["message"]
    overwritten = client.post(
        url + "/rawprep/execute",
        json={
            "revision": saved.json()["revision"],
            "sample_scope": {"mode": "all", "values": []},
            "overwrite_processed_name": True,
        },
    )
    assert "processed_dataset_name_conflict" not in overwritten.text


def test_other_project_registry_does_not_reserve_local_name(binding_platform):
    client, base, _, settings = binding_platform
    created = create(client, base, "shapenet_car_abupt")
    url = base + "/tasks/" + created["id"]
    initial = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={"expected_revision": initial["revision"], "sources": sources("shapenet_car_abupt")},
    )
    assert bound.status_code == 200, bound.text
    cfg = client.get(url + "/rawprep").json()
    saved = client.put(
        url + "/rawprep",
        json={
            "revision": cfg["revision"],
            "rawprep": {**cfg["rawprep"], "workers": 1},
            "processed_name": "shapenet_car",
        },
    )
    assert saved.status_code == 200, saved.text
    project = Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))
    stored = task.read_configuration(project, created["id"])["config"]
    occupied = _manifest(settings.root / "occupied" / "manifest.json", "same")
    task.register_processed_dataset(
        settings.root,
        "shapenet_car",
        manifest_path=occupied,
        digest=task.manifest_digest(occupied),
        claim=task.processed_claim({**stored, "rawprep": saved.json()["rawprep"]}),
    )
    parallel = client.put(
        url + "/rawprep",
        json={
            "revision": saved.json()["revision"],
            "rawprep": {**saved.json()["rawprep"], "workers": 8},
            "processed_name": "shapenet_car",
        },
    )
    assert parallel.status_code == 200, parallel.text
    assert parallel.json()["processed_name_status"]["status"] == "available"
    submitted = client.post(
        url + "/rawprep/execute",
        json={
            "revision": parallel.json()["revision"],
            "sample_scope": {"mode": "all", "values": []},
        },
    )
    assert submitted.status_code != 409
    assert "processed_dataset_name_conflict" not in submitted.text


def test_missing_manifest_is_unavailable(tmp_path):
    workspace = tmp_path / "workspace"
    manifest = _manifest(tmp_path / "keep" / "manifest.json")
    task.register_processed_dataset(
        workspace, "shapenet_car", manifest_path=manifest, digest=task.manifest_digest(manifest)
    )
    manifest.unlink()
    listed = task.list_processed_datasets(workspace)
    assert listed[0]["status"] == "unavailable"
    assert listed[0]["reason"] == "binding_file_missing"


def test_unavailable_dataset_cannot_be_selected(binding_platform):
    client, base, _, settings = binding_platform
    first = create(client, base, "shapenet_car_abupt")
    project = Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))
    manifest = _manifest(project / "tasks" / first["id"] / "data" / "run" / "manifest.json")
    task.register_processed_dataset(
        settings.root,
        "shapenet_car",
        manifest_path=manifest,
        digest=task.manifest_digest(manifest),
        provenance={"task_id": first["id"], "run_id": "run-a"},
    )
    manifest.unlink()
    other = client.post("/api/v1/projects", json={"name": "consumer"})
    child = create(client, "/api/v1/projects/" + other.json()["id"], "shapenet_car_abupt")
    listed = client.get("/api/v1/datasets").json()
    assert any(
        item["name"] == "shapenet_car" and item["status"] == "unavailable" for item in listed
    )
    inputs = client.get(
        "/api/v1/projects/" + other.json()["id"] + "/tasks/" + child["id"] + "/stage-inputs"
    ).json()
    item = next(row for row in inputs if row.get("processed_name") == "shapenet_car")
    assert item["ref"] is None
    assert item["compatibility"]["status"] == "invalid"


def test_resolved_formats_reject_empty_and_platform_overrides():
    from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_formats

    assert resolved_formats({}) == ["pt"]
    assert resolved_formats({"format": "zarr"}) == ["zarr"]
    assert resolved_formats({"formats": ["pt", "zarr"]}) == ["pt", "zarr"]
    with pytest.raises(ValueError, match="formats"):
        resolved_formats({"formats": []})
    assert resolved_formats({"format": "pt", "formats": ["zarr"]}) == ["zarr"]


def test_task_offline_shared_publication_and_cross_project_names(binding_platform, tmp_path):
    """Task 不调用服务发布；服务后查询自动登记，同名不同项目互不占用。"""
    from tests.integration.test_task_shared_execution import run_success, shared_recipe

    client, base, _, _settings = binding_platform
    (tmp_path / "offline").mkdir()
    source = shared_recipe(tmp_path / "offline")
    projects = [Path(client.app.state.services.project(base.rsplit("/", 1)[-1]))]
    other = client.post("/api/v1/projects", json={"name": "other-shared"}).json()
    projects.append(Path(client.app.state.services.project(other["id"])))
    for project in projects:
        item = task.new_task(project, "offline-producer", source=source)
        run_success(project, item)
    listed = client.get("/api/v1/datasets").json()
    shared = [x for x in listed if x["name"] == "sample_data"]
    assert len(shared) == 2
    assert len({x["shared_asset_id"] for x in shared}) == 2
    assert len({x["source_project"] for x in shared}) == 2
    assert all(x["status"] == "available" for x in shared)
