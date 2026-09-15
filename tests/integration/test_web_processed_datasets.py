"""平台已处理数据集登记、同名冲突与跨项目可见。"""

from pathlib import Path

import ai4e_task as task
import pytest

from tests.integration.test_web_dataset_binding import binding_platform, create, sources


def _manifest(path: Path, payload: str = "sample") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"version": 1, "state": "physical", "payload": "%s"}' % payload)
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
        if item["binding"] == "train.manifest" and item.get("origin") == "platform"
    ]
    assert "shapenet_car" in names
    chosen = next(item for item in inputs if item.get("processed_name") == "shapenet_car")
    assert chosen["ref"] and chosen["compatibility"]["status"] != "invalid"
    manifest_ids = [
        item["ref"]["asset_id"]
        for item in inputs
        if item["binding"] == "train.manifest" and item.get("ref")
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
    manifests = [item for item in inputs if item["binding"] == "train.manifest" and item.get("ref")]
    assert len(manifests) == 1
    assert manifests[0]["origin"] == "platform"
    assert manifests[0]["processed_name"] == "shapenet_car"
    assert not any(
        item.get("origin") == "run"
        for item in inputs
        if item["binding"] == "train.manifest"
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
        {**read_json(settings.root / "datasets" / "zeta_old" / "dataset.json"), "created_at": "2026-01-01T00:00:00+00:00"},
    )
    write_json(
        settings.root / "datasets" / "alpha_new" / "dataset.json",
        {**read_json(settings.root / "datasets" / "alpha_new" / "dataset.json"), "created_at": "2026-09-15T12:00:00+00:00"},
    )
    names = [
        item.get("processed_name")
        for item in client.get(base + "/tasks/" + created["id"] + "/stage-inputs").json()
        if item.get("origin") == "platform"
    ]
    assert "alpha_new" in names and "zeta_old" in names
    assert names.index("alpha_new") < names.index("zeta_old")
    public = [item["name"] for item in client.get("/api/v1/datasets").json()]
    assert public.index("alpha_new") < public.index("zeta_old")


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
    task.register_processed_dataset(
        workspace, "NASA_CRM", manifest_path=first, digest=task.manifest_digest(first)
    )


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
    parallel = task.processed_claim(
        {**base, "rawprep": {**base["rawprep"], "workers": 10}}
    )
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
    assert "processed_dataset_name_conflict" in rejected.text
    assert "换一个名称" in rejected.json()["error"]["message"]


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
    assert any(item["name"] == "shapenet_car" and item["status"] == "unavailable" for item in listed)
    inputs = client.get(
        "/api/v1/projects/" + other.json()["id"] + "/tasks/" + child["id"] + "/stage-inputs"
    ).json()
    item = next(row for row in inputs if row.get("processed_name") == "shapenet_car")
    assert item["ref"] is None
    assert item["compatibility"]["status"] == "invalid"


def test_resolved_formats_reject_empty_and_conflict():
    from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_formats

    assert resolved_formats({}) == ["pt"]
    assert resolved_formats({"format": "zarr"}) == ["zarr"]
    assert resolved_formats({"formats": ["pt", "zarr"]}) == ["pt", "zarr"]
    with pytest.raises(ValueError, match="formats"):
        resolved_formats({"formats": []})
    with pytest.raises(ValueError, match="同时"):
        resolved_formats({"format": "pt", "formats": ["zarr"]})
