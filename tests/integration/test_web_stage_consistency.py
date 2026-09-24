"""阶段事实、辅助检查失效和受控文件范围的回归。"""

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import ai4e_task as task
import pytest

from tests.integration.recipe_input_fixtures import public_patch
from tests.integration.test_web_project_task import platform as _platform

platform = _platform


def test_browsing_never_completes_stages(platform):
    c, p, t, _, _ = platform
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    summary = c.get(base + "/stage-summary").json()
    assert summary["stages"]["post"]["status"] == "not_run"
    assert summary["stages"]["rawprep"]["status"] == "not_run"
    assert summary["stages"]["model"]["status"] == "unchecked"
    assert (
        c.get(base).json()["stage_summary"]
        == c.get(f"/api/v1/projects/{p}/tasks").json()[0]["stage_summary"]
    )
    for role in ("inputs", "preparation", "post"):
        assert c.get(base + "/stage-files", params={"role": role}).json() == []


def test_check_revision_and_source_invalidation_preserve_history(platform):
    c, p, t, data, _ = platform
    service = c.app.state.services
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    revision = task.read_configuration(service.project(p), t["id"])["revision"]
    path = data / "source.txt"
    path.write_text("original")
    ref = c.post(f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": path.name}).json()
    record = {
        "project_id": p,
        "task_id": t["id"],
        "operation_id": "check",
        "kind": "trace_model",
        "stage": "model",
        "status": "succeeded",
        "revision": revision,
        "inputs": [ref],
    }
    service.store.put("operation", "check", record)
    assert c.get(base + "/stage-summary").json()["stages"]["model"]["status"] == "unchecked"
    path.write_text("changed")
    assert c.get(base + "/stage-summary").json()["stages"]["model"]["status"] == "unchecked"
    assert service.store.get("operation", "check")["status"] == "succeeded"
    task.save_configuration(
        service.project(p), t["id"], public_patch({"train": {"max_epochs": 3}}), revision=revision
    )
    after = c.get(base + "/stage-summary").json()["stages"]["model"]
    assert after["status"] == "unchecked"
    assert service.store.get("operation", "check")["status"] == "succeeded"


def test_errors_have_location_and_request_identity(platform):
    c, p, t, _, _ = platform
    response = c.put(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration",
        json={"stage": "train", "expected_revision": "old", "values": {"max_epochs": 3}},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "configuration_revision_conflict"
    assert response.json()["error"]["request_id"]
    assert c.get("/api/v1/capabilities").json()["output_formats"] == ["pt", "zarr"]


def test_trial_and_multistage_failure_do_not_claim_completion(monkeypatch, tmp_path):
    from ai4e_task.tasks import query

    monkeypatch.setattr(query, "get_task", lambda *_: {})
    monkeypatch.setattr(
        "ai4e_task.tasks.configuration.read_configuration", lambda *_: {"config": {}}
    )
    monkeypatch.setattr("ai4e_task.tasks.inference.list_inference_batches", lambda *_: [])
    monkeypatch.setattr(
        query,
        "list_runs",
        lambda *_: [
            {"id": "trial", "stages": ["post"], "operation_mode": "trial", "status": "succeeded"},
            {
                "id": "formal",
                "stages": ["rawprep", "trainprep", "train"],
                "status": "failed",
                "summary": {"reports": {}},
            },
        ],
    )
    monkeypatch.setattr(
        "ai4e_task.templates.materialize.recipe_entry",
        lambda *_: {"stages": ["rawprep", "trainprep", "train", "post"]},
    )
    result = query.get_stage_summary(tmp_path, "t")
    assert result["post"]["status"] == "not_run"
    assert result["rawprep"]["status"] == "unknown"
    assert result["train"]["status"] == "unknown"


def test_unknown_later_run_keeps_earlier_success(monkeypatch, tmp_path):
    """后来的 unknown 读盘不能把已成功执行改成未运行。"""
    from ai4e_task.tasks import query

    monkeypatch.setattr(query, "get_task", lambda *_: {})
    monkeypatch.setattr(
        "ai4e_task.tasks.configuration.read_configuration", lambda *_: {"config": {}}
    )
    monkeypatch.setattr("ai4e_task.tasks.inference.list_inference_batches", lambda *_: [])
    monkeypatch.setattr(
        query,
        "list_runs",
        lambda *_: [
            {
                "id": "raw-ok",
                "stages": ["rawprep"],
                "operation_mode": "execute",
                "status": "succeeded",
                "created_at": "2026-09-18T01:00:00+00:00",
                "summary": {},
            },
            {
                "id": "raw-lost",
                "stages": ["rawprep"],
                "operation_mode": "execute",
                "status": "unknown",
                "created_at": "2026-09-18T02:00:00+00:00",
                "summary": {},
            },
        ],
    )
    result = query.get_stage_summary(tmp_path, "t")
    assert result["rawprep"]["status"] == "succeeded"
    assert result["rawprep"]["run_id"] == "raw-ok"


def test_stage_files_ignore_unlisted_siblings_and_reject_other_task(platform, monkeypatch):
    import json

    c, p, t, _, _ = platform
    service = c.app.state.services
    root = service.project(p)
    directory = root / "physical"
    sample = directory / "train" / "a"
    sample.mkdir(parents=True)
    (sample / "pressure.pt").write_bytes(b"content")
    (directory / "unrelated.txt").write_text("not in manifest")
    (directory / "manifest.json").write_text(
        json.dumps({"samples": [{"path": str(sample), "filemap": {"p": "pressure.pt"}}]})
    )
    monkeypatch.setattr(
        task,
        "get_run",
        lambda *_: {
            "task_id": t["id"],
            "data_dir": str(directory),
            "run_dir": str(root / "run"),
            "operation_mode": "execute",
        },
    )
    base = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files"
    response = c.get(base, params={"role": "inputs", "run_id": "r"})
    assert response.status_code == 200, response.text
    rows = response.json()
    assert {item["name"] for item in rows} == {"manifest.json", "train"}
    assert all(item["root"] and item["source_path"] for item in rows)
    assert all("ref" not in item for item in rows)
    nested = c.get(base, params={"role": "inputs", "run_id": "r", "path": "train/a"}).json()
    assert {item["name"] for item in nested} == {"pressure.pt"}
    listed = next(item for item in rows if item["name"] == "manifest.json")
    preview = c.get(
        f"/api/v1/projects/{p}/preview",
        params={
            "root": listed["root"],
            "path": listed["source_path"],
            "task_id": t["id"],
            "operation": "inspect",
        },
    )
    assert preview.status_code == 200, preview.text
    assert c.get(f"/api/v1/projects/{p}/preview").status_code == 400
    monkeypatch.setattr(task, "get_run", lambda *_: {"task_id": "other"})
    assert c.get(base, params={"role": "inputs", "run_id": "r"}).status_code == 400


def test_stage_files_list_preparation_and_normalized_pt_copies(platform, monkeypatch):
    c, p, t, _, _ = platform
    root = c.app.state.services.project(p)
    run_dir = root / "runs" / "prep1"
    data_dir = root / "data" / "prep1"
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "preparation.json").write_text("{}")
    (artifacts / "secret.txt").write_text("no")
    sample = data_dir / "trainprep" / "normalize" / "train" / "s1"
    sample.mkdir(parents=True)
    (sample / "field_0.pt").write_bytes(b"pt")
    monkeypatch.setattr(
        task,
        "get_run",
        lambda *_: {
            "task_id": t["id"],
            "data_dir": str(data_dir),
            "run_dir": str(run_dir),
            "operation_mode": "execute",
            "stages": ["trainprep"],
        },
    )
    base = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files"
    rows = c.get(base, params={"role": "preparation", "run_id": "prep1"}).json()
    assert {item["name"] for item in rows} == {"preparation.json", "normalize"}
    assert "secret.txt" not in {item["name"] for item in rows}
    nested = c.get(
        base, params={"role": "preparation", "run_id": "prep1", "path": "normalize"}
    ).json()
    assert {item["name"] for item in nested} == {"train"}
    files = c.get(
        base, params={"role": "preparation", "run_id": "prep1", "path": "normalize/train/s1"}
    ).json()
    assert {item["name"] for item in files} == {"field_0.pt"}
    assert files[0]["source_path"].endswith("data/prep1/trainprep/normalize/train/s1/field_0.pt")


def test_stage_files_list_legacy_data_dir_normalize(platform, monkeypatch):
    c, p, t, _, _ = platform
    root = c.app.state.services.project(p)
    run_dir = root / "runs" / "prep_old"
    data_dir = root / "data" / "prep_old"
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(parents=True)
    (artifacts / "preparation.json").write_text("{}")
    sample = data_dir / "normalize" / "train" / "s1"
    sample.mkdir(parents=True)
    (sample / "field_0.pt").write_bytes(b"pt")
    monkeypatch.setattr(
        task,
        "get_run",
        lambda *_: {
            "task_id": t["id"],
            "data_dir": str(data_dir),
            "run_dir": str(run_dir),
            "operation_mode": "execute",
            "stages": ["trainprep"],
        },
    )
    base = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files"
    rows = c.get(base, params={"role": "preparation", "run_id": "prep_old"}).json()
    assert {item["name"] for item in rows} == {"preparation.json", "normalize"}
    files = c.get(
        base, params={"role": "preparation", "run_id": "prep_old", "path": "normalize/train/s1"}
    ).json()
    assert {item["name"] for item in files} == {"field_0.pt"}
    assert files[0]["source_path"].endswith("data/prep_old/normalize/train/s1/field_0.pt")


def test_stage_files_omit_normalize_when_preparation_missing(platform, monkeypatch):
    c, p, t, _, _ = platform
    root = c.app.state.services.project(p)
    run_dir = root / "runs" / "prep_fail"
    data_dir = root / "data" / "prep_fail"
    artifacts = run_dir / "artifacts"
    artifacts.mkdir(parents=True)
    sample = data_dir / "trainprep" / "normalize" / "train" / "s1"
    sample.mkdir(parents=True)
    (sample / "field_0.pt").write_bytes(b"pt")
    monkeypatch.setattr(
        task,
        "get_run",
        lambda *_: {
            "task_id": t["id"],
            "data_dir": str(data_dir),
            "run_dir": str(run_dir),
            "operation_mode": "execute",
            "stages": ["trainprep"],
        },
    )
    rows = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files",
        params={"role": "preparation", "run_id": "prep_fail"},
    ).json()
    assert rows == []


def test_draft_manifest_revision_is_checked_before_listing(platform):
    import json

    c, p, t, data, _ = platform
    sample = data / "a"
    sample.mkdir()
    (sample / "p.pt").write_bytes(b"test")
    manifest = data / "manifest.json"
    manifest.write_text(json.dumps({"samples": [{"path": "a", "filemap": {"p": "p.pt"}}]}))
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "manifest.json"}
    ).json()
    params = {"role": "inputs", "asset_id": ref["asset_id"], "revision": ref["revision"]}
    endpoint = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files"
    response = c.get(endpoint, params=params)
    assert response.status_code == 200, response.text
    names = {item["name"] for item in response.json()}
    assert names == {"manifest.json", "a"}
    child = c.get(endpoint, params={**params, "path": "a"}).json()
    assert {item["name"] for item in child} == {"p.pt"}
    manifest.write_text("{}")
    assert c.get(endpoint, params=params).status_code == 409


def test_training_options_consume_declared_constraints():
    from ai4e_server.modules.stages.application import _capability_options

    result = _capability_options(
        {
            "configuration": {"train": {"device": "auto", "optimizer": "adamw"}},
            "capabilities": {
                "training_constraints": {"optimizer": {"allowed": ["adamw"], "readOnly": True}},
                "parameter_descriptors": {"precision": {"allowed": ["fp32"]}},
            },
        }
    )
    assert result["training_options"] == {
        "optimizer": ["adamw"],
        "precision": ["fp32"],
        "device": ["auto"],
    }


def test_relative_binding_restores_from_task_configuration_directory(platform, monkeypatch):
    c, p, t, _, _ = platform
    service = c.app.state.services
    root = service.project(p)
    manifest = root / "physical" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text("{}")
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch({"train": {"manifest": "../../../physical/manifest.json"}}),
        revision=cfg["revision"],
    )
    monkeypatch.setattr(
        task,
        "list_stage_artifacts",
        lambda *_a, **_k: [
            {
                "binding": "inputs.trainprep.dataset",
                "run_id": "r",
                "name": "manifest.json",
                "path": "physical/manifest.json",
            }
        ],
    )
    response = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs")
    assert response.status_code == 200, response.text
    assert response.json()[0]["selected"] is True


def test_technical_inspection_error_is_not_shown_in_page(platform, monkeypatch):
    c, p, t, _, _ = platform

    def broken(*args, **kwargs):
        raise ValueError("TypeError: expected path, got NoneType")

    monkeypatch.setattr(task, "inspect_task", broken)
    response = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "model"}
    )
    assert response.status_code == 200
    assert "NoneType" not in response.text
    assert response.json()["capabilities"]["status"] == "unavailable"


def test_stage_save_atomically_persists_or_clears_controlled_bindings(platform):
    c, p, t, data, _ = platform
    (data / "manifest.json").write_text("{}")
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "manifest.json"}
    ).json()
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = c.get(base + "/configuration").json()
    body = {
        "stage": "train",
        "values": {"max_epochs": 7},
        "expected_revision": cfg["revision"],
        "bindings": {"inputs.trainprep.dataset": ref},
    }
    saved = c.put(base + "/configuration", json=body)
    assert saved.status_code == 200, saved.text
    assert saved.json()["config"]["inputs"]["trainprep"]["dataset"] == str(data / "manifest.json")
    assert saved.json()["config"]["train"]["max_epochs"] == 7
    assert c.put(base + "/configuration", json=body).status_code == 409
    body["expected_revision"] = saved.json()["revision"]
    body["bindings"] = {"inputs.trainprep.dataset": None}
    assert (
        c.put(base + "/configuration", json=body).json()["config"]["inputs"]["trainprep"]["dataset"]
        is None
    )
    assert len(c.get(f"/api/v1/projects/{p}/lineage").json()) == 1


def test_manifest_extra_assets_and_zarr_are_atomic_entries(platform):
    import json

    c, p, t, data, _ = platform
    sample = data / "sample"
    sample.mkdir()
    zarr = sample / "pressure.zarr"
    zarr.mkdir()
    (zarr / "chunk").write_bytes(b"chunk")
    (zarr / "zarr.json").write_text("{}")
    (sample / "surface.vtkhdf").write_bytes(b"mesh")
    (sample / "entity_mapping.json").write_text("{}")
    (sample / "unlisted.vtkhdf").write_bytes(b"old output")
    (data / "manifest.json").write_text(
        json.dumps(
            {
                "samples": [
                    {
                        "path": "sample",
                        "filemap": {"pressure": "pressure.zarr"},
                        "assets": ["surface.vtkhdf", "entity_mapping.json"],
                    }
                ]
            }
        )
    )
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "manifest.json"}
    ).json()
    response = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files",
        params={"role": "inputs", "asset_id": ref["asset_id"], "revision": ref["revision"]},
    )
    assert response.status_code == 200, response.text
    assert {entry["name"] for entry in response.json()} == {"manifest.json", "sample"}
    nested = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stage-files",
        params={
            "role": "inputs",
            "asset_id": ref["asset_id"],
            "revision": ref["revision"],
            "path": "sample",
        },
    )
    assert nested.status_code == 200, nested.text
    assert {entry["name"] for entry in nested.json()} == {
        "pressure.zarr",
        "surface.vtkhdf",
        "entity_mapping.json",
    }
    zarr = next(entry for entry in nested.json() if entry["name"] == "pressure.zarr")
    assert zarr["directory"] is False
    assert "ref" not in zarr


def test_global_capabilities_do_not_claim_dataset_specific_fields(platform):
    c, *_ = platform
    value = c.get("/api/v1/capabilities").json()
    assert value["execution_stages"] == ["rawprep", "trainprep", "train", "infer", "post"]
    assert value["inference"] == {"batch": True, "scope": "task", "max_active_children_per_task": 1}
    assert value["sources"] == {} and value["outputs"] == {}
    assert {"zarr", "h5", "hdf5"} <= set(value["formats"])
    assert not {"arbitrary_tensor_bundle", "output_rename"} & set(value["unsupported"])


def test_case_creation_snapshots_actual_example_scripts_and_entry(platform):
    from pathlib import Path

    c, p, _, _, settings = platform
    for case in (
        "nasa_crm_abupt",
        "nasa_crm_transolver3",
        "shapenet_car_abupt",
        "shapenet_car_transolver3_surface",
    ):
        response = c.post(f"/api/v1/projects/{p}/tasks", json={"name": case, "case_id": case})
        assert response.status_code == 200, response.text
        record = response.json()
        recipe = (
            Path(task.get_task(c.app.state.services.project(p), record["id"])["directory"])
            / "recipe"
        )
        source = settings.template.parent.parent / "examples/aero_cfd" / case
        for filename in (
            "rawprep.py",
            "configuration.py",
            "pipeline.py",
            "trainprep.py",
            "train.py",
            "post.py",
        ):
            assert (recipe / filename).read_bytes() == (source / filename).read_bytes()
        assert record["entry"]["convention_version"] == 1
        assert not (recipe / "task-entry.json").exists()
        if case.startswith("nasa_crm"):
            assert "inputs.rawprep.train_h5" in record["entry"]["inputs"]
        assert c.get(f"/api/v1/projects/{p}/tasks/{record['id']}/rawprep").status_code == 200
    # 相同已登记案例可多次创建，不重复登记冲突。
    assert (
        c.post(
            f"/api/v1/projects/{p}/tasks", json={"name": "again", "case_id": "nasa_crm_abupt"}
        ).status_code
        == 200
    )


def test_legacy_zarr_preview_pages_and_invalidates_cache(platform):
    import numpy as np
    import zarr

    c, p, _, data, _ = platform
    path = data / "values.zarr"
    store = zarr.open_group(str(path), mode="w")
    array = store.create_array("pressure", data=np.arange(240, dtype="float32").reshape(120, 2))
    endpoint = f"/api/v1/projects/{p}/preview"
    params = {
        "root": "data0",
        "path": path.name,
        "operation": "preview",
        "field": "pressure",
        "offset": 100,
    }
    first = c.get(endpoint, params=params)
    assert first.status_code == 200, first.text
    assert first.json()["rows"][0] == [200, 201]
    assert len(first.json()["rows"]) == 20
    ref = c.post(f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": path.name}).json()
    assert ref["revision"] == first.json()["revision"]
    array[100, 0] = 999
    second = c.get(endpoint, params=params)
    assert second.status_code == 200, second.text
    assert second.json()["rows"][0] == [999, 201]
    assert second.json()["revision"] != first.json()["revision"]
    (path / "escape").symlink_to(data / "outside.txt")
    assert c.get(endpoint, params=params).status_code == 400


def test_external_fixed_bindings_restore_and_report_missing_without_paths(platform):
    c, p, t, data, _ = platform
    root = c.app.state.services.project(p)
    manifest = data / "manifest.json"
    prepared = data / "preparation.json"
    manifest.write_text("{}")
    prepared.write_text("{}")
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch({"train": {"manifest": str(manifest), "preparation": str(prepared)}}),
        revision=cfg["revision"],
    )
    endpoint = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs"
    response = c.get(endpoint)
    assert response.status_code == 200, response.text
    items = {item["binding"]: item for item in response.json()}
    for key in ("inputs.trainprep.dataset", "inputs.train.preparation"):
        assert items[key]["selected"] and items[key]["ref"]["revision"]
        assert items[key]["run_id"] is None
        assert items[key]["origin"] == "configuration"
    assert str(data) not in response.text
    prepared.unlink()
    missing = c.get(endpoint)
    item = next(item for item in missing.json() if item["binding"] == "inputs.train.preparation")
    assert item["ref"] is None and not item["selected"]
    assert item["compatibility"] == {
        "status": "invalid",
        "reason": "binding_file_missing",
        "location": "inputs.train.preparation",
    }
    assert str(data) not in missing.text


def test_template_manifest_placeholder_is_not_bound_source(platform):
    """案例模板展开出的根外空路径不当成已绑定失效来源。"""
    c, p, t, _, _ = platform
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch(
            {"train": {"manifest": "/no-such-dojo-root/missing-placeholder/manifest.json"}}
        ),
        revision=cfg["revision"],
    )
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    assert not any(item["binding"] == "inputs.trainprep.dataset" for item in items)


def test_existing_outside_root_manifest_stays_invalid(platform, tmp_path):
    """根外且文件仍在的真实绑定继续报越界，不泄露绝对路径。"""
    c, p, t, _, _ = platform
    escaped = tmp_path / "escaped" / "manifest.json"
    escaped.parent.mkdir()
    escaped.write_text("{}")
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch({"train": {"manifest": str(escaped)}}),
        revision=cfg["revision"],
    )
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "inputs.trainprep.dataset")
    assert item["ref"] is None and not item["selected"]
    assert item["compatibility"]["reason"] == "path_outside_root"
    assert str(escaped) not in str(items)


def test_run_manifest_on_registered_root_is_listed(platform, monkeypatch):
    """正式清单落在已登记数据根时仍可作为运行产物列出。"""
    from ai4e_task.tasks import artifacts

    c, p, t, data, _ = platform
    (data / "manifest.json").write_text("{}")
    from ai4e_core.run.writer import RunWriter

    run_dir = data / "indexed-run"
    run_dir.mkdir()
    writer = RunWriter(run_dir)
    writer.record_asset(
        "physical",
        data / "manifest.json",
        kind="dataset",
        stage="rawprep",
        semantics={"type": "aero.physical", "format_version": 1},
    )
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "run-root",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data),
                "run_dir": str(run_dir),
            }
        ],
    )
    listed = artifacts.list_stage_artifacts(
        c.app.state.services.project(p), t["id"], {"data0": data}
    )
    assert listed[0]["root"] == "data0" and listed[0]["path"] == "manifest.json"
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "inputs.trainprep.dataset")
    assert item["origin"] == "run" and item["run_id"] == "run-root" and item["ref"]


def test_stat_register_does_not_read_file_bytes(platform, monkeypatch):
    """列表登记只看文件戳；内容变了才让旧引用失效。"""
    from pathlib import Path

    from ai4e_server.modules.visualization.application import asset, register

    c, p, t, data, _ = platform
    blob = data / "heavy.bin"
    blob.write_bytes(b"x" * (2 * 1024 * 1024))
    reads = {"n": 0}
    original = Path.open

    def tracked(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if self.resolve() == blob.resolve() and "b" in str(mode):
            reads["n"] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked)
    service = c.app.state.services
    ref = register(service, p, "data0", "heavy.bin", t["id"], integrity="stat")
    assert reads["n"] == 0
    assert asset(service, p, ref) == blob.resolve()
    assert reads["n"] == 0
    blob.write_bytes(b"y" * (2 * 1024 * 1024))
    with pytest.raises(ValueError, match="asset_revision_conflict"):
        asset(service, p, ref)


def test_stage_inputs_skip_content_digest(platform, monkeypatch):
    """切步列表不得把检查点整文件打进内容摘要。"""
    from ai4e_server.modules.visualization import application as vis

    from ai4e_core.run import indexes

    def forbidden(path):
        raise AssertionError(f"content digest during listing: {path}")

    monkeypatch.setattr(vis, "digest", forbidden)
    monkeypatch.setattr(indexes, "content_digest", forbidden)
    monkeypatch.setattr(indexes, "validate_asset_content", forbidden)
    c, p, t, _, _ = platform
    response = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs")
    assert response.status_code == 200, response.text


def test_list_stage_artifacts_does_not_reread_checkpoint_bytes(platform, monkeypatch):
    """公开索引里的大检查点只认还在，列举时不读文件内容。"""
    import json
    from pathlib import Path

    from ai4e_task.tasks import artifacts

    from ai4e_core.run import indexes
    from ai4e_spec.artifacts.indexes import INDEX_VERSION

    c, p, t, data, _ = platform
    run_dir = data / "ckpt-list-run"
    (run_dir / "artifacts").mkdir(parents=True)
    ckpt = data / "last.pt"
    ckpt.write_bytes(b"x" * (2 * 1024 * 1024))
    (run_dir / "artifacts" / "assets.json").write_text(
        json.dumps(
            {
                "schema_version": INDEX_VERSION,
                "items": {
                    "train/last": {
                        "name": "last",
                        "kind": "checkpoint",
                        "stage": "train",
                        "path": str(ckpt.resolve()),
                        "digest": "listed-without-reread",
                        "semantics": {"type": "aero.checkpoint"},
                        "dependencies": [],
                    }
                },
            }
        )
    )
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "ckpt-list-run",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data),
                "run_dir": str(run_dir),
            }
        ],
    )

    def forbidden(path):
        raise AssertionError(f"content digest during listing: {path}")

    monkeypatch.setattr(indexes, "content_digest", forbidden)
    monkeypatch.setattr(indexes, "validate_asset_content", forbidden)
    reads = {"n": 0}
    original = Path.open

    def tracked(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        if self.resolve() == ckpt.resolve() and "b" in str(mode):
            reads["n"] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked)
    listed = artifacts.list_stage_artifacts(
        c.app.state.services.project(p), t["id"], {"data0": data}
    )
    assert reads["n"] == 0
    assert any(
        item["binding"] == "inputs.infer.checkpoint"
        and item["name"] == "last"
        and item["file_name"] == "last.pt"
        for item in listed
    )
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    assert reads["n"] == 0
    assert any(
        item["binding"] == "inputs.infer.checkpoint" and item["name"] == "last.pt" for item in items
    )


def test_preparation_stage_inputs_use_processed_dataset_name(platform, monkeypatch):
    """准备完成的数据按下拉展示登记名称，不回运行短号或 preparation.json。"""
    from ai4e_task.tasks import artifacts

    c, p, t, data, _ = platform
    run_dir = data / "prep-run"
    (run_dir / "artifacts").mkdir(parents=True)
    (run_dir / "artifacts" / "preparation.json").write_text("{}")
    from ai4e_core.run.writer import RunWriter

    writer = RunWriter(run_dir)
    writer.record_asset(
        "preparation", run_dir / "artifacts/preparation.json", kind="preparation", stage="trainprep"
    )
    (run_dir / "inputs").mkdir()
    (run_dir / "inputs" / "config.yaml").write_text("dataset:\n  processed_name: my_cars\n")
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "prep-named",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data),
                "run_dir": str(run_dir),
            }
        ],
    )
    monkeypatch.setattr(task, "get_run", lambda *_: (_ for _ in ()).throw(KeyError("run")))
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "inputs.train.preparation")
    assert item["processed_name"] == "my_cars"
    assert item["name"] == "preparation.json"


def test_published_slices_catalog_reads_existing_v2_record():
    path = Path(__file__).resolve().parents[2] / "packages/ai4e-server/modules/stages/domain.py"
    spec = importlib.util.spec_from_file_location("dojo_source_stage_domain", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.published_slices(
        {
            "partitions": {"train": ["a"], "validation": ["b"]},
            "split": {"method": "original", "seed": 1},
        }
    ) == [
        {
            "name": "train",
            "role": "train",
            "label": "训练集",
            "count": 1,
            "method": "original",
            "seed": 1,
        },
        {
            "name": "test",
            "role": "test",
            "label": "测试集",
            "count": 0,
            "method": "original",
            "seed": 1,
        },
        {
            "name": "eval",
            "role": "eval",
            "label": "评价集",
            "count": 1,
            "method": "original",
            "seed": 1,
        },
    ]


def test_preparation_stage_inputs_expose_saved_slices(platform, monkeypatch):
    """已有 version=2 准备把三分片带给训练/推理选择器，空切片人数为 0。"""
    from ai4e_task.tasks import artifacts

    c, p, t, data, _ = platform
    run_dir = data / "prep-slices"
    (run_dir / "artifacts").mkdir(parents=True)
    (run_dir / "artifacts" / "preparation.json").write_text(
        json.dumps(
            {
                "version": 2,
                "partitions": {"train": ["a", "b"], "test": ["c"]},
                "split": {
                    "method": "random",
                    "seed": 7,
                    "counts": {"train": 2, "test": 1, "eval": 0},
                },
                "split_counts": {"train": 2, "test": 1},
            }
        )
    )
    from ai4e_core.run.writer import RunWriter

    writer = RunWriter(run_dir)
    writer.record_asset(
        "preparation",
        run_dir / "artifacts/preparation.json",
        kind="preparation",
        stage="trainprep",
    )
    (run_dir / "inputs").mkdir()
    (run_dir / "inputs" / "config.yaml").write_text("dataset:\n  processed_name: sliced_cars\n")
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "prep-slices",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data),
                "run_dir": str(run_dir),
            }
        ],
    )
    monkeypatch.setattr(task, "get_run", lambda *_: (_ for _ in ()).throw(KeyError("run")))
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "inputs.train.preparation")
    assert item["processed_name"] == "sliced_cars"
    if "slices" not in item:
        pytest.skip("安装副本尚未附带切片目录")
    assert item["slices"] == [
        {
            "name": "train",
            "role": "train",
            "label": "训练集",
            "count": 2,
            "method": "random",
            "seed": 7,
        },
        {
            "name": "test",
            "role": "test",
            "label": "测试集",
            "count": 1,
            "method": "random",
            "seed": 7,
        },
        {
            "name": "eval",
            "role": "eval",
            "label": "评价集",
            "count": 0,
            "method": "random",
            "seed": 7,
        },
    ]


def test_fixed_directory_archive_metadata_revision_and_escape(platform):
    import io
    import zipfile

    c, p, _, data, _ = platform
    path = data / "tensor.zarr"
    path.mkdir()
    (path / ".zarray").write_text('{"shape":[2]}')
    (path / "0").write_bytes(b"values")
    ref = c.post(f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": path.name}).json()
    endpoint = f"/api/v1/projects/{p}/assets/{ref['asset_id']}/content"
    params = {"download": "true", "revision": ref["revision"]}
    response = c.get(endpoint, params=params)
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        assert set(archive.namelist()) == {".zarray", "0"}
        assert archive.read("0") == b"values"
    assert c.get(endpoint, params={**params, "member": "../secret"}).status_code == 400
    (path / "0").write_bytes(b"changed")
    assert c.get(endpoint, params=params).status_code == 409
    (path / "outside").symlink_to(data / "private.txt")
    assert (
        c.post(
            f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": path.name}
        ).status_code
        == 400
    )


def test_split_catalog_defaults_and_rejects_invalid_counts():
    from ai4e_server.modules.stages.domain import split_catalog, validate_split

    manifest = {"partitions": {"train": ["a", "b"], "test": ["c"]}}
    catalog = split_catalog(manifest)
    assert catalog == {
        "total": 3,
        "defaults": {"train": 2, "test": 1, "eval": 0},
        "methods": ["original", "random"],
        "samples": [
            {"id": "a", "partition": "train"},
            {"id": "b", "partition": "train"},
            {"id": "c", "partition": "test"},
        ],
    }
    validate_split(
        {"split": {"method": "original", "counts": {"train": 0, "test": 0, "eval": 0}}}, manifest
    )
    with pytest.raises(ValueError, match="split_count_sum_mismatch"):
        validate_split(
            {"split": {"method": "random", "counts": {"train": 1, "test": 1, "eval": 0}}},
            manifest,
        )
    with pytest.raises(ValueError, match="split_train_required"):
        validate_split(
            {"split": {"method": "random", "counts": {"train": 0, "test": 3, "eval": 0}}},
            manifest,
        )
    validate_split(
        {
            "split": {
                "method": "random",
                "samples": ["a"],
                "counts": {"train": 1, "test": 0, "eval": 0},
            }
        },
        manifest,
    )
    with pytest.raises(ValueError, match="split_samples_required"):
        validate_split(
            {
                "split": {
                    "method": "random",
                    "samples": [],
                    "counts": {"train": 1, "test": 0, "eval": 0},
                }
            },
            manifest,
        )


def test_field_matching_uses_model_roles_and_rejects_dimension_mismatch():
    from ai4e_server.modules.stages.domain import (
        field_matching_catalog,
        validate_field_bindings,
    )

    config = {
        "rawprep": {
            "fields": {
                "surface": {"pressure": {"components": 1}},
                "volume": {"velocity": {"components": 3}},
            },
            "save_fields": [
                "surface_position",
                "surface_pressure",
                "volume_position",
                "volume_velocity",
            ],
        },
        "trainprep": {
            "use_physics_features": False,
            "domains": {
                "surface": {
                    "position": "surface_position",
                    "features": {},
                    "targets": {"pressure": "surface_pressure"},
                },
                "volume": {
                    "position": "volume_position",
                    "features": {},
                    "targets": {"velocity": "volume_velocity"},
                },
            },
        },
        "model": {
            "data_specs": {
                "position_dim": 3,
                "domains": {
                    "surface": {"output_dims": {"pressure": 1}, "feature_dim": {"surface_sdf": 1}},
                    "volume": {"output_dims": {"velocity": 3}},
                },
            }
        },
    }
    matching = field_matching_catalog(config)
    assert matching["source"] == "configuration"
    assert [role["id"] for role in matching["model_roles"]] == [
        "surface/position",
        "surface/targets/pressure",
        "volume/position",
        "volume/targets/velocity",
    ]
    pressure = next(
        item for item in matching["dataset_fields"] if item["name"] == "surface_pressure"
    )
    assert pressure["shape"] == ["N", 1]
    assert pressure["dim"] == 1
    assert next(
        role for role in matching["model_roles"] if role["id"] == "surface/targets/pressure"
    )["shape"] == ["N", 1]
    validate_field_bindings(
        config["trainprep"], matching["model_roles"], matching["dataset_fields"]
    )
    broken = {
        **config["trainprep"],
        "domains": {
            **config["trainprep"]["domains"],
            "surface": {
                **config["trainprep"]["domains"]["surface"],
                "targets": {"pressure": "volume_velocity"},
            },
        },
    }
    try:
        validate_field_bindings(broken, matching["model_roles"], matching["dataset_fields"])
    except ValueError as exc:
        assert str(exc).startswith("field_domain_mismatch:")
    else:
        raise AssertionError("expected domain mismatch")
    same_domain = {
        **config["trainprep"],
        "domains": {
            **config["trainprep"]["domains"],
            "surface": {
                **config["trainprep"]["domains"]["surface"],
                "targets": {"pressure": "surface_position"},
            },
        },
    }
    try:
        validate_field_bindings(same_domain, matching["model_roles"], matching["dataset_fields"])
    except ValueError as exc:
        assert str(exc).startswith("field_dimension_mismatch:")
    else:
        raise AssertionError("expected dimension mismatch")
    tensor = {
        **config,
        "rawprep": {
            **config["rawprep"],
            "fields": {
                **config["rawprep"]["fields"],
                "surface": {"stress": {"shape": [3, 2, 3]}},
            },
            "save_fields": [*config["rawprep"]["save_fields"], "surface_stress"],
        },
        "trainprep": {
            **config["trainprep"],
            "domains": {
                **config["trainprep"]["domains"],
                "surface": {
                    **config["trainprep"]["domains"]["surface"],
                    "targets": {"stress": "surface_stress"},
                },
            },
        },
        "model": {
            "data_specs": {
                "position_dim": 3,
                "domains": {"surface": {"output_dims": {"stress": [3, 2, 3]}}},
            }
        },
    }
    ranked = field_matching_catalog(tensor)
    assert next(role for role in ranked["model_roles"] if role["id"] == "surface/targets/stress")[
        "shape"
    ] == ["N", 3, 2, 3]
    assert next(item for item in ranked["dataset_fields"] if item["name"] == "surface_stress")[
        "shape"
    ] == ["N", 3, 2, 3]
    validate_field_bindings(tensor["trainprep"], ranked["model_roles"], ranked["dataset_fields"])


def test_trainprep_configuration_exposes_matching_and_rejects_bad_binding(platform):
    c, p, t, _, _ = platform
    base = f"/api/v1/projects/{p}/tasks/{t['id']}/configuration"
    value = c.get(base + "?stage=trainprep").json()
    matching = value["capabilities"]["field_matching"]
    assert {role["id"] for role in matching["model_roles"]} >= {
        "surface/position",
        "surface/targets/pressure",
        "volume/targets/velocity",
    }
    assert any(item["name"] == "surface_pressure" for item in matching["dataset_fields"])
    split = value["capabilities"]["split"]
    assert split["methods"] == ["original", "random"]
    assert set(split["defaults"]) == {"train", "test", "eval"}
    assert any(
        role.get("shape") == ["N", 1]
        for role in matching["model_roles"]
        if role["id"] == "surface/targets/pressure"
    )
    values = {**value["values"]}
    values["domains"] = {
        **values["domains"],
        "surface": {**values["domains"]["surface"], "targets": {"pressure": "volume_velocity"}},
    }
    response = c.put(
        base,
        json={"stage": "trainprep", "expected_revision": value["revision"], "values": values},
    )
    assert response.status_code == 400
    assert response.json()["detail"].startswith("field_domain_mismatch:")
    values["domains"]["surface"]["targets"] = {"pressure": "surface_pressure"}
    saved = c.put(
        base,
        json={"stage": "trainprep", "expected_revision": value["revision"], "values": values},
    )
    assert saved.status_code == 200, saved.text


@pytest.mark.parametrize(
    "source,target_model",
    [
        ("shapenet_car_abupt", "transolver3"),
        ("shapenet_car_transolver3_surface", "abupt"),
        ("nasa_crm_abupt", "transolver3"),
        ("nasa_crm_transolver3", "abupt"),
    ],
)
@pytest.mark.parametrize("explicit_paths", [False, True])
def test_registered_model_switch_replaces_defaults_and_preserves_identity(
    platform, source, target_model, explicit_paths
):
    """真实案例描述、双向替换及保存回读，不以创建来源冒充当前模型。"""
    from copy import deepcopy

    c, p, _, data, _ = platform
    created = c.post(f"/api/v1/projects/{p}/tasks", json={"name": source, "case_id": source})
    assert created.status_code == 200, created.text
    t = created.json()
    service = c.app.state.services
    root = service.project(p)
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    captured = task.read_configuration(root, t["id"])
    original_entry = deepcopy(t["entry"])
    old = data / "old-preparation.json"
    old.write_text("{}")
    cfg = task.save_configuration(
        root,
        t["id"],
        public_patch(
            {
                "dataset": {"root": str(data), "custom_binding": "keep"},
                "train": {
                    "manifest": str(data / "physical.json"),
                    "preparation": str(old),
                    "resume": str(data / "old.pt"),
                    "max_epochs": 999,
                    "old_optimizer_key": 1,
                },
                "model": {"initial_weights": str(data / "old.pt"), "old_extension": True},
                "trainprep": {"old_role": True, "normalization": {"statistics": str(old)}},
                "post": {"checkpoint": str(data / "old.pt"), "user_output_option": True},
                "run_root": str(data.parent / "runs"),
                "data_root": str(data.parent / "outputs"),
            }
        ),
        revision=captured["revision"],
    )
    options = c.get(url + "/model-options")
    assert options.status_code == 200, options.text
    options = options.json()
    assert options["current_model_id"] == ("abupt" if "abupt" in source else "transolver3")
    assert len(options["options"]) == 2
    assert {item["id"] for item in options["options"]} == {"abupt", "transolver3"}
    assert all(item["dataset_id"] == options["dataset_id"] for item in options["options"])
    chosen = c.get(url + "/model-option", params={"model": target_model}).json()
    assert chosen["id"] == target_model
    values = deepcopy(chosen["model"])
    parameter = "n_hidden" if target_model == "transolver3" else "dim"
    values["parameters"][parameter] = 96
    response = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": cfg["revision"],
            "target_model": target_model,
            "values": values,
            **({
                "edited_paths": [[key] for key in values],
                "removed_paths": [[key] for key in cfg["config"]["model"] if key not in values],
            } if explicit_paths else {}),
        },
    )
    assert response.status_code == 200, response.text
    saved = response.json()
    actual = saved["config"]
    assert actual["model"] == values
    assert actual["components"]["model"] == chosen["component"]
    expected_train = deepcopy(chosen["train"])
    expected_train.pop("preparation", None)
    expected_train.setdefault("training_split", "train")
    for key in ("training_split", "evaluation_split", "export_split"):
        if expected_train.get(key) == "validation":
            expected_train[key] = "eval"
    assert actual["train"] == expected_train
    assert actual["trainprep"] == chosen["trainprep"]
    for key in ("dataset", "rawprep", "data_root", "run_root"):
        assert actual[key] == cfg["config"][key]
    assert actual["post"] == cfg["config"]["post"]
    assert actual["inputs"]["train"]["resume"] is None
    assert actual["inputs"]["train"]["preparation"] is None
    assert old.read_text() == "{}"
    live_entry = task.get_task(root, t["id"])["entry"]
    assert live_entry.get("platform_case") == original_entry.get("platform_case")
    assert live_entry["script"] == original_entry["script"]
    assert live_entry["config"] == original_entry["config"]
    assert live_entry["components"] == actual["components"]
    assert task.get_task(root, t["id"])["version_id"] == t["version_id"]
    assert task.read_configuration(root, t["id"]) == saved
    assert c.get(url + "/model-options").json()["current_model_id"] == target_model
    from ai4e_server.modules.capabilities.model_cases import resolve_case

    target_case = resolve_case(options["dataset_id"], target_model)
    official = service.settings.template.parent.parent / "examples/aero_cfd" / target_case
    live_recipe = Path(task.get_task(root, t["id"])["directory"]) / "recipe"
    for filename in ("trainprep.py", "train.py", "infer.py"):
        assert (live_recipe / filename).read_bytes() == (official / filename).read_bytes()
    reread = c.get(url + "/configuration?stage=model")
    assert reread.status_code == 200, reread.text
    assert reread.json()["values"]["parameters"][parameter] == 96
    if target_model == "transolver3":
        assert "supernodes" not in reread.json()["values"]["sampling"]
        assert reread.json()["values"]["sampling"]["stride"] == 4
        assert reread.json()["values"]["parameters"]["slice_num"] == 64
        assert reread.json()["capabilities"]["losses"]["configurable"] is False
        assert reread.json()["capabilities"]["sampling"]["configurable"] is True
        assert (
            reread.json()["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"] is True
        )
    else:
        assert "supernodes" in reread.json()["values"]["sampling"]
        assert reread.json()["capabilities"]["sampling"]["configurable"] is True
    ordinary = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": saved["revision"],
            "values": {"parameters": {parameter: 192}},
        },
    )
    assert ordinary.status_code == 200, ordinary.text
    assert ordinary.json()["config"]["train"] == expected_train


def test_model_switch_rejects_cross_dataset_conflict_and_old_bindings(platform):
    """绕过浏览器也不能跨数据集换模、旧修订覆盖或把旧准备绑回。"""
    c, p, t, _, _ = platform
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = c.get(url + "/configuration").json()
    response = c.put(
        url + "/configuration",
        json={
            "stage": "trainprep",
            "expected_revision": cfg["revision"],
            "values": cfg["config"].get("trainprep") or {},
            "target_case_id": "nasa_crm_abupt",
        },
    )
    assert response.status_code == 400 and "model_case_dataset_mismatch" in response.text
    assert (
        c.put(
            url + "/configuration",
            json={
                "stage": "model",
                "expected_revision": "stale",
                "values": {},
                "target_model": "transolver3",
            },
        ).status_code
        == 409
    )
    response = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": cfg["revision"],
            "values": {},
            "target_model": "transolver3",
            "bindings": {"inputs.train.preparation": {"asset_id": "old"}},
        },
    )
    assert response.status_code == 400 and "model_switch_requires_new_preparation" in response.text
    assert c.get(url + "/configuration").json() == cfg


@pytest.mark.parametrize("tag", ["last", "best", "latest"])
def test_checkpoint_tags_are_not_binding_file_paths(platform, tag):
    """标签保持运行时含义；真正缺失文件仍返回字段错误。"""
    c, p, t, data, _ = platform
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    saved = task.save_configuration(
        root,
        t["id"],
        public_patch(
            {"post": {"checkpoint": tag}, "train": {"manifest": str(data / "missing.json")}}
        ),
        revision=cfg["revision"],
    )
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs"
    items = c.get(url).json()
    assert not any(
        i["binding"] == "inputs.infer.checkpoint" and i["compatibility"]["status"] == "invalid"
        for i in items
    )
    assert any(
        i["binding"] == "inputs.trainprep.dataset"
        and i["compatibility"]["reason"] == "binding_file_missing"
        for i in items
    )
    task.save_configuration(
        root,
        t["id"],
        public_patch({"post": {"checkpoint": str(data / "missing.pt")}}),
        revision=saved["revision"],
    )
    assert any(
        i["binding"] == "inputs.infer.checkpoint"
        and i["compatibility"]["reason"] == "binding_file_missing"
        for i in c.get(url).json()
    )


@pytest.mark.parametrize("case", ["shapenet_car_abupt", "nasa_crm_abupt"])
def test_model_switch_real_preparation_handoff(platform, case):
    """显式开启的真实 CFD 验收：原始处理、现行准备可导入、换模后按当前页面计算。"""
    import json
    import os
    from pathlib import Path

    if os.environ.get("DOJO_MODEL_PICKER_REAL") != "1":
        pytest.skip("真实模型换模专项通过 DOJO_MODEL_PICKER_REAL=1 显式运行")
    c, p, _, data, settings = platform
    from tests.integration.test_web_rawprep_handoff import REAL, SAMPLE, copy_real

    root = c.app.state.services.project(p)
    created = c.post(f"/api/v1/projects/{p}/tasks", json={"name": case, "case_id": case})
    assert created.status_code == 200, created.text
    item = created.json()
    url = f"/api/v1/projects/{p}/tasks/{item['id']}"
    original = task.read_configuration(root, item["id"])
    if case.startswith("shapenet"):
        assert (REAL / SAMPLE).is_dir(), "真实 ShapeNet 数据缺失"
        copy_real(data)
        dataset = {"root": str(data), "partition": {"train": [SAMPLE]}, "samples": "all"}
        target = "shapenet_car_transolver3_surface"
    else:
        from ai4e_contrib.application.datasets.nasa_crm import RawDataset

        nasa = Path("/Users/zonghui/work/datasets/NASA")
        dataset = {
            "root": str(nasa),
            "train_h5": str(nasa / "Case 4 - NASA CRM 2/trainingData_NASA-CRM.h5"),
            "test_h5": str(nasa / "Case 4 - NASA CRM/testData_NASA-CRM.h5"),
            "connectivity_h5": str(nasa / "Case 4 - NASA CRM/connectivity_NASA-CRM.h5"),
        }
        assert all(
            Path(dataset[key]).is_file() for key in ("train_h5", "test_h5", "connectivity_h5")
        )
        partitions = RawDataset(dataset).partitions
        dataset["samples"] = {
            "train": partitions["train"][:8],
            "validation": partitions["validation"][:1],
            "test": partitions["test"][:1],
        }
        settings.data_roots.append(nasa)
        target = "nasa_crm_transolver3"
    dataset["processed_name"] = "real_model_" + case
    captured = task.save_configuration(
        root,
        item["id"],
        public_patch(
            {
                "dataset": dataset,
                "run_root": str(data.parent / "runs"),
                "data_root": str(data.parent / "outputs"),
                "train": {"device": "cpu"},
            }
        ),
        revision=original["revision"],
    )

    def execute(stage):
        current = task.read_configuration(root, item["id"])
        response = c.post(
            url + f"/stages/{stage}/operations",
            json={
                "mode": "execute",
                "expected_revision": current["revision"],
                "selection": {},
                "inputs": [],
            },
        )
        assert response.status_code == 200, response.text
        run = task.wait_run(root, response.json()["id"], timeout=300)
        assert run["status"] == "succeeded", task.read_log(root, run["id"])
        return run

    raw = execute("rawprep")
    physical = task.run_physical_manifest(root, raw)
    assert physical is not None, "正式共享物理清单缺失"
    manifest = str(physical)
    cfg = task.read_configuration(root, item["id"])
    cfg = task.save_configuration(
        root, item["id"], public_patch({"train": {"manifest": manifest}}), revision=cfg["revision"]
    )
    old_run = execute("trainprep")
    old = str(Path(old_run["run_dir"]) / "artifacts/preparation.json")
    old_content = Path(old).read_bytes()
    cfg = task.save_configuration(
        root, item["id"], public_patch({"train": {"preparation": old}}), revision=cfg["revision"]
    )
    chosen = c.get(url + "/model-option", params={"model": "transolver3"}).json()
    response = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": cfg["revision"],
            "target_model": "transolver3",
            "values": chosen["model"],
        },
    )
    assert response.status_code == 200, response.text
    switched = response.json()
    assert switched["config"]["dataset"] == captured["config"]["dataset"]
    assert switched["config"]["inputs"]["trainprep"]["dataset"] == manifest
    assert not switched["config"]["train"].get("preparation")
    inspected = task.inspect_task(
        root,
        item["id"],
        "validate_configuration",
        revision=switched["revision"],
        output_dir=str(data.parent / "old-check"),
        selection={"stage": "model", "bindings": {"inputs.train.preparation": old}},
    )
    assert inspected.get("ok") is not False
    assert "声明已变化" not in str(inspected)
    # 同数据集并不保证字段齐全：用独立清单移除目标所需法向声明，原产物不改写。
    incomplete = json.loads(Path(manifest).read_text())
    for sample in incomplete["samples"]:
        sample.get("filemap", {}).pop("surface_normals", None)
        sample.get("fields", {}).pop("surface_normals", None)
        if "names" in sample:
            sample["names"] = [name for name in sample["names"] if name != "surface_normals"]
    # 负例写到受控测试根，不污染已经发布并按内容校验的共享数据目录。
    incomplete_path = data / "incomplete-model-test.json"
    incomplete_path.write_text(json.dumps(incomplete))
    with pytest.raises(ValueError, match="surface_normals|法向"):
        task.inspect_task(
            root,
            item["id"],
            "validate_configuration",
            revision=switched["revision"],
            output_dir=str(data.parent / "missing-field-check"),
            selection={
                "stage": "model",
                "bindings": {"inputs.trainprep.dataset": str(incomplete_path)},
            },
        )
    new_run = execute("trainprep")
    new = str(Path(new_run["run_dir"]) / "artifacts/preparation.json")
    new_record = json.loads(Path(new).read_text())
    assert (
        new_record["declarations"]["component"]
        != json.loads(old_content)["declarations"]["component"]
    )
    assert Path(old).read_bytes() == old_content
    saved = task.save_configuration(
        root,
        item["id"],
        public_patch({"train": {"preparation": new}}),
        revision=switched["revision"],
    )
    described = task.inspect_task(
        root,
        item["id"],
        "validate_configuration",
        revision=saved["revision"],
        output_dir=str(data.parent / "new-check"),
        selection={"stage": "model"},
    )
    assert described["valid"]
    assert task.get_task(root, item["id"])["version_id"] == item["version_id"]
    evidence = Path(os.environ["DOJO_MODEL_PICKER_EVIDENCE"])
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / (case + ".json")).write_text(
        json.dumps(
            {
                "project": p,
                "task": item["id"],
                "target": target,
                "platform_root": str(settings.root),
                "data_roots": [str(v) for v in settings.data_roots],
                "revision": saved["revision"],
                "raw": raw,
                "old_preparation": old_run,
                "new_preparation": new_run,
                "manifest": manifest,
                "prepared": new,
                "split_counts": new_record["split_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def test_shapenet_transolver_volume_variant_uses_volume_example(platform):
    """同一任务改体场等同换模，写入体场官方宽度。"""
    from copy import deepcopy

    c, p, _, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "volume", "case_id": "shapenet_car_abupt"},
    )
    t = created.json()
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    options = c.get(url + "/model-options").json()
    transolver = next(item for item in options["options"] if item["id"] == "transolver3")
    assert {item["id"] for item in transolver["variants"]} == {"surface", "volume"}
    transolver = c.get(
        url + "/model-option", params={"model": "transolver3", "variant": "volume"}
    ).json()
    assert transolver["capabilities"]["sampling"]["configurable"] is True
    assert transolver["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"] is True
    assert (
        c.get(url + "/model-option", params={"model": "abupt"}).json()["capabilities"]["sampling"][
            "configurable"
        ]
        is True
    )
    volume = transolver["variant_defaults"]["volume"]
    saved = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": options["revision"],
            "target_model": "transolver3",
            "target_variant": "volume",
            "values": deepcopy(volume["model"]),
        },
    )
    assert saved.status_code == 200, saved.text
    parameters = saved.json()["config"]["model"]["parameters"]
    assert parameters["space_dim"] == 3
    assert parameters["out_dim"] == 3
    reread = c.get(url + "/model-options").json()
    assert reread["current_model_id"] == "transolver3"
    assert reread["current_variant"] == "volume"


def test_nasa_model_options_have_two_models_and_no_volume(platform):
    """NASA 只提供两个官方模型，没有体场变体。"""
    c, p, _, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "nasa", "case_id": "nasa_crm_abupt"},
    )
    url = f"/api/v1/projects/{p}/tasks/{created.json()['id']}"
    options = c.get(url + "/model-options").json()
    assert {item["id"] for item in options["options"]} == {"abupt", "transolver3"}
    assert all(not item.get("variants") for item in options["options"])
    by_id = {
        key: c.get(url + "/model-option", params={"model": key}).json()
        for key in ("abupt", "transolver3")
    }
    assert by_id["abupt"]["capabilities"]["sampling"]["configurable"] is True
    assert by_id["transolver3"]["capabilities"]["sampling"]["configurable"] is True
    assert (
        by_id["transolver3"]["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"]
        is True
    )
    assert by_id["transolver3"]["capabilities"]["losses"]["terms"]


def test_model_options_catalog_skips_case_inspection(platform, monkeypatch):
    """进页候选列表不启动 describe_case；点选描述才检查目标案例。"""
    inspected: list[str] = []
    original = task.inspect_task

    def wrapped(*args, **kwargs):
        inspected.append(kwargs.get("operation") or (args[2] if len(args) > 2 else ""))
        return original(*args, **kwargs)

    monkeypatch.setattr(task, "inspect_task", wrapped)
    c, p, _, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "catalog", "case_id": "shapenet_car_abupt"},
    )
    url = f"/api/v1/projects/{p}/tasks/{created.json()['id']}"
    options = c.get(url + "/model-options").json()
    assert {item["id"] for item in options["options"]} == {"abupt", "transolver3"}
    assert all(item["model"]["parameters"] for item in options["options"])
    assert all(not (item.get("capabilities") or {}).get("sampling") for item in options["options"])
    assert "describe_case" not in inspected
    described = c.get(
        url + "/model-option", params={"model": "transolver3", "variant": "surface"}
    ).json()
    assert described["capabilities"]["sampling"]["configurable"] is True
    assert "describe_case" in inspected


def test_saving_current_official_model_without_target_keeps_revision_tree(platform):
    """不带换模目标的普通保存不重置训练默认。"""
    c, p, _, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "keep", "case_id": "shapenet_car_abupt"},
    )
    url = f"/api/v1/projects/{p}/tasks/{created.json()['id']}"
    cfg = c.get(url + "/configuration?stage=model").json()
    train = c.get(url + "/configuration").json()["config"]["train"]
    saved = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": cfg["revision"],
            "values": {"parameters": {**cfg["values"]["parameters"], "dim": 96}},
        },
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["config"]["train"]["max_epochs"] == train["max_epochs"]


def _plant_trace_sources(monkeypatch, items):
    """只为结构跟踪植入正式运行产物，不改任务配置。"""
    monkeypatch.setattr(task, "list_runs", lambda *_a, **_k: items)
    monkeypatch.setattr(
        task,
        "list_stage_artifacts",
        lambda *_a, **_k: [
            {
                "binding": item["binding"],
                "run_id": item["id"],
                "name": item["name"],
                "root": item["root"],
                "path": item["path"],
            }
            for item in items
        ],
    )


def test_auto_trace_uses_formal_manifest_without_rewriting_bindings(platform, monkeypatch):
    """有正式清单即可解析跟踪来源，任务已保存绑定不变。"""
    from ai4e_server.modules.capabilities.trace_source import latest_trace_source
    from ai4e_server.modules.stages.application import _trace_selection

    c, p, t, data, _ = platform
    (data / "manifest.json").write_text("{}")
    _plant_trace_sources(
        monkeypatch,
        [
            {
                "id": "raw",
                "created_at": "2026-01-02T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.trainprep.dataset",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            }
        ],
    )
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    before = c.get(url + "/configuration").json()
    options = c.get(url + "/model-options").json()
    assert options["trace_available"] is True
    service = c.app.state.services
    source = latest_trace_source(service, p, t["id"])
    assert source == {"inputs.trainprep.dataset": str((data / "manifest.json").resolve())}
    _trace_selection(service, p, t["id"])
    after = c.get(url + "/configuration").json()
    assert after["config"]["train"] == before["config"]["train"]
    assert after["revision"] == before["revision"]


def test_auto_trace_prefers_recent_compatible_preparation(platform, monkeypatch):
    """同时有可导入准备和新清单时取已选或最近可导入准备。"""
    from ai4e_server.modules.capabilities.trace_source import latest_trace_source

    c, p, t, data, _ = platform
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    (data / "manifest.json").write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(
        __import__("json").dumps(
            {
                "version": 2,
                "declarations": {
                    "component": cfg["config"]["components"]["model"],
                    "model": cfg["config"]["model"],
                },
            }
        )
    )
    _plant_trace_sources(
        monkeypatch,
        [
            {
                "id": "prep",
                "created_at": "2026-01-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.train.preparation",
                "name": "preparation.json",
                "root": "data0",
                "path": "preparation.json",
            },
            {
                "id": "raw",
                "created_at": "2026-02-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.trainprep.dataset",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            },
        ],
    )
    source = latest_trace_source(c.app.state.services, p, t["id"])
    assert source == {"inputs.train.preparation": str(prep.resolve())}


def test_auto_trace_rejects_without_formal_manifest(platform):
    """没有正式清单时拒绝生成，并提示先完成原始处理。"""
    c, p, t, _, _ = platform
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = c.get(url + "/configuration").json()
    options = c.get(url + "/model-options").json()
    assert options["trace_available"] is False
    response = c.post(
        url + "/model-inspections",
        json={"expected_revision": cfg["revision"], "mode": "check"},
    )
    assert response.status_code == 400
    assert "请先完成原始处理后再生成真实模型结构" in response.text
    assert c.get(url + "/configuration").json()["revision"] == cfg["revision"]


def test_auto_trace_falls_back_to_manifest_after_unreadable_preparation(platform, monkeypatch):
    """缺版本或不可读取的准备回退最近正式清单。"""
    from ai4e_server.modules.capabilities.trace_source import latest_trace_source

    c, p, _, data, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "trace-switch", "case_id": "shapenet_car_abupt"},
    )
    t = created.json()
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    (data / "manifest.json").write_text("{}")
    prep = data / "old-prep.json"
    prep.write_text(
        __import__("json").dumps(
            {
                "declarations": {
                    "component": "ai4e_contrib.ability.model.abupt.component",
                    "model": {"parameters": {"dim": 192}},
                }
            }
        )
    )
    options = c.get(url + "/model-options").json()
    chosen = c.get(url + "/model-option", params={"model": "transolver3"}).json()
    switched = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": options["revision"],
            "target_model": "transolver3",
            "values": chosen["model"],
        },
    )
    assert switched.status_code == 200, switched.text
    _plant_trace_sources(
        monkeypatch,
        [
            {
                "id": "prep",
                "created_at": "2026-03-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.train.preparation",
                "name": "old-prep.json",
                "root": "data0",
                "path": "old-prep.json",
            },
            {
                "id": "raw",
                "created_at": "2026-01-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.trainprep.dataset",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            },
        ],
    )
    source = latest_trace_source(c.app.state.services, p, t["id"])
    assert source == {"inputs.trainprep.dataset": str((data / "manifest.json").resolve())}
    train = switched.json()["config"]["train"]
    assert not train.get("preparation")


def test_auto_trace_keeps_importable_preparation_after_model_switch(platform, monkeypatch):
    """换模后现行 version=2 准备仍可导入，不因冻结声明不同丢掉。"""
    from ai4e_server.modules.capabilities.trace_source import latest_trace_source

    c, p, _, data, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "trace-importable", "case_id": "shapenet_car_abupt"},
    )
    t = created.json()
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    (data / "manifest.json").write_text("{}")
    prep = data / "old-prep.json"
    prep.write_text(
        __import__("json").dumps(
            {
                "version": 2,
                "declarations": {
                    "component": "ai4e_contrib.ability.model.abupt.component",
                    "model": {"parameters": {"dim": 192}},
                },
            }
        )
    )
    options = c.get(url + "/model-options").json()
    chosen = c.get(url + "/model-option", params={"model": "transolver3"}).json()
    switched = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": options["revision"],
            "target_model": "transolver3",
            "values": chosen["model"],
        },
    )
    assert switched.status_code == 200, switched.text
    _plant_trace_sources(
        monkeypatch,
        [
            {
                "id": "prep",
                "created_at": "2026-03-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.train.preparation",
                "name": "old-prep.json",
                "root": "data0",
                "path": "old-prep.json",
            },
            {
                "id": "raw",
                "created_at": "2026-01-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "inputs.trainprep.dataset",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            },
        ],
    )
    source = latest_trace_source(c.app.state.services, p, t["id"])
    assert source == {"inputs.train.preparation": str(prep.resolve())}


def test_train_execution_consumes_preparation_and_rejects_prepare_first(platform):
    """训练设置提交开训，拒绝合并数据准备，缺准备完成的数据不能提交。"""
    from ai4e_server.modules.stages.domain import execution_stages, required_inputs

    assert execution_stages("train", "execute", {}) == ["train"]
    assert required_inputs("train", ["train"]) == ["inputs.train.preparation"]
    with pytest.raises(ValueError, match="train_requires_preparation"):
        execution_stages("train", "execute", {"prepare_first": True})

    c, p, t, _, _ = platform
    cfg = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    endpoint = f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations"
    rejected = c.post(
        endpoint,
        json={
            "expected_revision": cfg["revision"],
            "mode": "execute",
            "selection": {"prepare_first": True},
            "inputs": [],
        },
    )
    assert rejected.status_code == 400, rejected.text
    assert rejected.json()["error"]["code"] == "train_requires_preparation"
    assert "数据准备" in rejected.json()["error"]["message"]
    missing = c.post(
        endpoint,
        json={
            "expected_revision": cfg["revision"],
            "mode": "execute",
            "selection": {},
            "inputs": [],
        },
    )
    assert missing.status_code == 400, missing.text
    assert missing.json()["error"]["code"] == "stage_input_required"
    assert missing.json()["error"]["location"] == "inputs.train.preparation"
    from ai4e_server.modules.stages.domain import ALLOWED_BINDINGS

    assert "inputs.train.resume" in ALLOWED_BINDINGS
    resume = c.post(
        endpoint,
        json={
            "expected_revision": cfg["revision"],
            "mode": "execute",
            "selection": {
                "bindings": {"inputs.train.resume": {"asset_id": "missing", "revision": "v1"}}
            },
            "inputs": [{"asset_id": "missing", "revision": "v1"}],
        },
    )
    assert resume.status_code in {400, 404}, resume.text
    assert "unsupported_stage_binding" not in resume.text


def _last_override(overrides, key):
    items = [item for item in overrides if item.startswith(key + "=")]
    return items[-1] if items else None


def test_train_execute_composes_manifest_from_selected_preparation(platform, monkeypatch):
    """开训以当次所选准备合成清单，覆盖配置里另一页留下的路径。"""
    import json

    c, p, t, data, _ = platform
    leftover = data / "leftover.json"
    leftover.write_text("{}")
    frozen = data / "frozen.json"
    frozen.write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(json.dumps({"version": 2, "manifest": str(frozen)}))
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "preparation.json"}
    ).json()
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch(
            {
                "train": {
                    **(cfg["config"].get("train") or {}),
                    "manifest": str(leftover),
                    "resume": str(data / "old.pt"),
                }
            }
        ),
        revision=cfg["revision"],
    )
    captured = {}

    def submit(*_a, **kwargs):
        captured["overrides"] = list(kwargs.get("overrides") or [])
        return {"id": "train-composed", "status": "queued"}

    monkeypatch.setattr(task, "submit_run", submit)
    page = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    posted = c.post(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations",
        json={
            "expected_revision": page["revision"],
            "mode": "execute",
            "selection": {"bindings": {"inputs.train.preparation": ref}},
            "inputs": [ref],
        },
    )
    assert posted.status_code == 200, posted.text
    assert _last_override(captured["overrides"], "inputs.trainprep.dataset") == (
        "inputs.trainprep.dataset=" + json.dumps(str(frozen))
    )
    assert (
        _last_override(captured["overrides"], "inputs.train.resume") == "inputs.train.resume=null"
    )
    assert any(item.startswith("inputs.train.preparation=") for item in captured["overrides"])


def test_train_execute_composes_from_saved_preparation_without_bindings(platform, monkeypatch):
    """未再传绑定也按已保存的准备重新合成，不沿用配置里另一份清单。"""
    import json

    c, p, t, data, _ = platform
    leftover = data / "leftover.json"
    leftover.write_text("{}")
    frozen = data / "frozen.json"
    frozen.write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(json.dumps({"version": 2, "manifest": str(frozen)}))
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    task.save_configuration(
        root,
        t["id"],
        public_patch(
            {
                "inputs": {
                    **(cfg["config"].get("inputs") or {}),
                    "train": {
                        **((cfg["config"].get("inputs") or {}).get("train") or {}),
                        "preparation": str(prep),
                    },
                    "trainprep": {"dataset": str(leftover)},
                },
                "train": {
                    **(cfg["config"].get("train") or {}),
                },
            }
        ),
        revision=cfg["revision"],
    )
    captured = {}

    def submit(*_a, **kwargs):
        captured["overrides"] = list(kwargs.get("overrides") or [])
        return {"id": "train-saved-prep", "status": "queued"}

    monkeypatch.setattr(task, "submit_run", submit)
    page = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    posted = c.post(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations",
        json={
            "expected_revision": page["revision"],
            "mode": "execute",
            "selection": {},
            "inputs": [],
        },
    )
    assert posted.status_code == 200, posted.text
    assert _last_override(captured["overrides"], "inputs.trainprep.dataset") == (
        "inputs.trainprep.dataset=" + json.dumps(str(frozen))
    )


def test_train_execute_rejects_version1_preparation(platform, monkeypatch):
    """选中早期物理准备时拒绝开训，并说明须按现行数据准备重新生成。"""
    import json

    c, p, t, data, _ = platform
    prep = data / "old-prep.json"
    prep.write_text(
        json.dumps({"version": 1, "dataset": "legacy", "manifest": str(data / "m.json")})
    )
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "old-prep.json"}
    ).json()

    def submit(*_a, **_kwargs):
        raise AssertionError("v1 准备不得提交")

    monkeypatch.setattr(task, "submit_run", submit)
    page = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    posted = c.post(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations",
        json={
            "expected_revision": page["revision"],
            "mode": "execute",
            "selection": {"bindings": {"inputs.train.preparation": ref}},
            "inputs": [ref],
        },
    )
    assert posted.status_code == 400, posted.text
    body = posted.json()
    assert body["error"]["code"] == "preparation_requires_regeneration"
    assert "重新生成" in body["error"]["message"]
    assert "声明已变化" not in body["error"]["message"]


def test_train_execute_writes_explicit_scale_and_preserves_historical_script(platform, monkeypatch):
    """补显式 scale；旧官方包装升级到当前模型案例，保留该领域的训练流程。"""
    import json
    from pathlib import Path

    from ai4e_server.modules.stages.domain import normalize_field_scales

    c, p, t, data, _ = platform
    filled = normalize_field_scales(
        {
            "components": {"model": "ai4e_contrib.ability.model.abupt.component"},
            "trainprep": {
                "normalization": {
                    "fields": {
                        "surface_position": {"method": "coordinate"},
                        "surface_pressure": {"method": "zscore"},
                    }
                }
            },
        }
    )["trainprep"]["normalization"]["fields"]
    assert filled["surface_position"]["scale"] == 1000
    assert filled["surface_pressure"]["scale"] == 1

    frozen = data / "frozen.json"
    frozen.write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(json.dumps({"version": 2, "manifest": str(frozen)}))
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "preparation.json"}
    ).json()
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    trainprep = dict(cfg["config"].get("trainprep") or {})
    normalization = dict(trainprep.get("normalization") or {})
    fields = {name: dict(item) for name, item in (normalization.get("fields") or {}).items()}
    if "surface_position" not in fields:
        fields["surface_position"] = {"method": "coordinate"}
    fields["surface_position"].pop("scale", None)
    trainprep["normalization"] = {**normalization, "fields": fields}
    task.save_configuration(
        root,
        t["id"],
        public_patch({"trainprep": trainprep}),
        revision=cfg["revision"],
        replace_sections=("trainprep",),
    )
    recipe = Path(task.get_task(root, t["id"])["directory"]) / "recipe"
    old = Path(__file__).resolve().parents[2] / (
        ".context/mvp/recipe-task-conventions-results/original-examples/"
        "aero_cfd/shapenet_car_abupt/train.py"
    )
    recipe.joinpath("train.py").write_text(old.read_text())
    captured = {}

    def submit(*_a, **kwargs):
        captured["overrides"] = list(kwargs.get("overrides") or [])
        return {"id": "train-migrated", "status": "queued"}

    monkeypatch.setattr(task, "submit_run", submit)
    page = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    posted = c.post(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations",
        json={
            "expected_revision": page["revision"],
            "mode": "execute",
            "selection": {"bindings": {"inputs.train.preparation": ref}},
            "inputs": [ref],
        },
    )
    assert posted.status_code == 200, posted.text
    dumped = json.loads(_last_override(captured["overrides"], "trainprep").split("=", 1)[1])
    assert dumped["normalization"]["fields"]["surface_position"]["scale"] == 1000
    text = recipe.joinpath("train.py").read_text()
    assert text == old.read_text()


def test_user_rewritten_official_script_is_not_replaced(platform, monkeypatch):
    """用户改过的旧包装脚本多了顶层函数时不覆盖。"""
    import json
    from pathlib import Path

    c, p, t, data, _ = platform
    frozen = data / "frozen.json"
    frozen.write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(json.dumps({"version": 2, "manifest": str(frozen)}))
    ref = c.post(
        f"/api/v1/projects/{p}/assets", json={"root": "data0", "path": "preparation.json"}
    ).json()
    root = c.app.state.services.project(p)
    recipe = Path(task.get_task(root, t["id"])["directory"]) / "recipe"
    custom = (
        "from ai4e_core.applications.aero_cfd.train import physical as fitting\n"
        "def train(cfg, prepared=None):\n    return fitting\n"
        "def extra_hook():\n    return 1\n"
    )
    recipe.joinpath("train.py").write_text(custom)

    def submit(*_a, **_kwargs):
        return {"id": "train-custom", "status": "queued"}

    monkeypatch.setattr(task, "submit_run", submit)
    page = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration", params={"stage": "train"}
    ).json()
    posted = c.post(
        f"/api/v1/projects/{p}/tasks/{t['id']}/stages/train/operations",
        json={
            "expected_revision": page["revision"],
            "mode": "execute",
            "selection": {"bindings": {"inputs.train.preparation": ref}},
            "inputs": [ref],
        },
    )
    assert posted.status_code == 200, posted.text
    assert recipe.joinpath("train.py").read_text() == custom


def test_training_settings_check_and_save_keep_step_complete(platform):
    """训练设置预检不要准备产物；保存后本步完成，再读摘要仍保留。"""
    c, p, t, data, _ = platform
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    checked = task.inspect_task(
        root,
        t["id"],
        "validate_configuration",
        revision=cfg["revision"],
        output_dir=str(data / "train-settings-check"),
        selection={"stage": "train"},
    )
    assert checked["valid"] is True
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    page = c.get(base + "/configuration", params={"stage": "train"}).json()
    saved = c.put(
        base + "/configuration",
        json={
            "stage": "train",
            "expected_revision": page["revision"],
            "values": {**page["values"], "max_epochs": 3},
        },
    )
    assert saved.status_code == 200, saved.text
    assert c.get(base + "/stage-summary").json()["stages"]["training"]["status"] == "succeeded"
    assert c.get(base).json()["stage_summary"]["training"]["status"] == "succeeded"
    again = c.put(
        base + "/configuration",
        json={
            "stage": "train",
            "expected_revision": saved.json()["revision"],
            "values": {**page["values"], "max_epochs": 4},
        },
    )
    assert again.status_code == 200, again.text
    assert c.get(base + "/stage-summary").json()["stages"]["training"]["status"] == "succeeded"
    assert c.get(base).json()["stage_summary"]["model"]["status"] == "unchecked"


def test_training_save_without_edits_replaces_failed_check(platform):
    """未改训练参数也保存，盖住旧失败预检。"""
    c, p, t, _, _ = platform
    service = c.app.state.services
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = task.read_configuration(service.project(p), t["id"])
    service.store.put(
        "operation",
        "old-train-check",
        {
            "project_id": p,
            "task_id": t["id"],
            "operation_id": "old-train-check",
            "kind": "validate_configuration",
            "stage": "train",
            "status": "failed",
            "revision": cfg["revision"],
            "inputs": [],
            "created_at": "2026-09-16T00:00:00+00:00",
            "error": {"message": "train.preparation: 阶段 train 需要已有固定产物"},
        },
    )
    before = c.get(base + "/stage-summary").json()["stages"]["training"]
    assert before["status"] == "unchecked"
    assert before["check"]["status"] == "failed"
    page = c.get(base + "/configuration", params={"stage": "train"}).json()
    saved = c.put(
        base + "/configuration",
        json={
            "stage": "train",
            "expected_revision": page["revision"],
            "values": page["values"],
            "edited_paths": [],
            "removed_paths": [],
        },
    )
    assert saved.status_code == 200, saved.text
    stages = c.get(base + "/stage-summary").json()["stages"]
    assert stages["training"]["status"] == "succeeded"
    assert c.get(base).json()["stage_summary"]["training"]["status"] == "succeeded"


def test_model_save_marks_complete_and_ignores_trace_or_failed_check(platform):
    """模型页点保存即完成；结构跟踪和失败预检不能冒充或清掉。"""
    c, p, t, _, _ = platform
    service = c.app.state.services
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    page = c.get(base + "/configuration", params={"stage": "model"}).json()
    saved = c.put(
        base + "/configuration",
        json={
            "stage": "model",
            "expected_revision": page["revision"],
            "values": page["values"],
            "edited_paths": [],
            "removed_paths": [],
        },
    )
    assert saved.status_code == 200, saved.text
    assert c.get(base + "/stage-summary").json()["stages"]["model"]["status"] == "succeeded"
    service.store.put(
        "operation",
        "trace-after-save",
        {
            "project_id": p,
            "task_id": t["id"],
            "operation_id": "trace-after-save",
            "kind": "trace_model",
            "stage": "model",
            "status": "succeeded",
            "revision": saved.json()["revision"],
            "inputs": [],
            "created_at": "2026-09-18T03:00:00+00:00",
        },
    )
    service.store.put(
        "operation",
        "failed-model-check",
        {
            "project_id": p,
            "task_id": t["id"],
            "operation_id": "failed-model-check",
            "kind": "validate_configuration",
            "stage": "model",
            "status": "failed",
            "revision": saved.json()["revision"],
            "inputs": [],
            "created_at": "2026-09-18T04:00:00+00:00",
        },
    )
    assert c.get(base + "/stage-summary").json()["stages"]["model"]["status"] == "succeeded"
    assert c.get(base).json()["stage_summary"]["model"]["status"] == "succeeded"


def test_settings_step_stale_only_when_same_page_changes(platform):
    """模型完成态只在本页参数变化时失效，保存训练设置不能清掉。"""
    c, p, t, _, _ = platform
    service = c.app.state.services
    base = f"/api/v1/projects/{p}/tasks/{t['id']}"
    model_page = c.get(base + "/configuration", params={"stage": "model"}).json()
    model_saved = c.put(
        base + "/configuration",
        json={
            "stage": "model",
            "expected_revision": model_page["revision"],
            "values": model_page["values"],
            "edited_paths": [],
            "removed_paths": [],
        },
    )
    assert model_saved.status_code == 200, model_saved.text
    page = c.get(base + "/configuration", params={"stage": "train"}).json()
    saved = c.put(
        base + "/configuration",
        json={
            "stage": "train",
            "expected_revision": page["revision"],
            "values": {**page["values"], "max_epochs": 5},
        },
    )
    assert saved.status_code == 200, saved.text
    stages = c.get(base + "/stage-summary").json()["stages"]
    assert stages["model"]["status"] == "succeeded"
    assert stages["training"]["status"] == "succeeded"
    current = task.read_configuration(service.project(p), t["id"])
    model = dict(current["config"].get("model") or {})
    model["dim"] = int(model.get("dim") or 192) + 1
    task.save_configuration(
        service.project(p), t["id"], public_patch({"model": model}), revision=current["revision"]
    )
    latest = c.get(base + "/stage-summary").json()["stages"]
    assert latest["model"]["status"] == "succeeded"
    assert latest["model"]["reason"] == "configuration_revision_changed"
    assert latest["training"]["status"] == "succeeded"


def test_preparation_combos_follow_dataset_and_load_official_trainprep(platform):
    """准备页组合只列当前数据集，加载官方处理；换模型才解除旧准备。"""
    c, p, _, data, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks", json={"name": "prep-combo", "case_id": "shapenet_car_abupt"}
    )
    assert created.status_code == 200, created.text
    t = created.json()
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = c.get(url + "/configuration?stage=trainprep").json()
    combos = cfg["capabilities"]["preparation_combos"]
    assert combos["current_id"] == "shapenet_car_abupt"
    ids = {item["id"] for item in combos["options"]}
    assert ids == {
        "shapenet_car_abupt",
        "shapenet_car_transolver3_surface",
        "shapenet_car_transolver3_volume",
    }
    fields = cfg["values"]["normalization"]["fields"]
    assert fields["surface_position"]["method"] == "coordinate"
    assert fields["surface_position"]["scale"] == 1000

    root = c.app.state.services.project(p)
    captured = task.read_configuration(root, t["id"])
    old = data / "old-preparation.json"
    old.write_text("{}")
    stored = task.save_configuration(
        root,
        t["id"],
        public_patch(
            {
                "train": {
                    **captured["config"].get("train", {}),
                    "preparation": str(old),
                    "resume": str(data / "old.pt"),
                },
                "model": {
                    **captured["config"].get("model", {}),
                    "initial_weights": str(data / "old.pt"),
                },
            }
        ),
        revision=captured["revision"],
    )
    same = c.put(
        url + "/configuration",
        json={
            "stage": "trainprep",
            "expected_revision": stored["revision"],
            "target_case_id": "shapenet_car_abupt",
            "values": cfg["values"],
        },
    )
    assert same.status_code == 200, same.text
    assert same.json()["config"]["inputs"]["train"]["preparation"] == str(old)
    assert same.json()["config"]["inputs"]["train"]["initial_weights"] == str(data / "old.pt")
    assert (
        same.json()["config"]["trainprep"]["normalization"]["fields"]["surface_position"]["scale"]
        == 1000
    )

    switched = c.put(
        url + "/configuration",
        json={
            "stage": "trainprep",
            "expected_revision": same.json()["revision"],
            "target_case_id": "shapenet_car_transolver3_volume",
            "values": same.json()["config"]["trainprep"],
        },
    )
    assert switched.status_code == 200, switched.text
    prep = switched.json()["config"]["trainprep"]
    assert set(prep["domains"]) == {"volume"}
    assert prep["normalization"]["fields"]["volume_position"]["method"] == "identity"
    assert prep["normalization"]["fields"]["volume_position"]["scale"] == 1
    assert switched.json()["config"]["components"]["model"].endswith("transolver3.component")
    assert not switched.json()["config"]["train"].get("preparation")
    nasa = c.put(
        url + "/configuration",
        json={
            "stage": "trainprep",
            "expected_revision": switched.json()["revision"],
            "target_case_id": "nasa_crm_abupt",
            "values": deepcopy(prep),
        },
    )
    assert nasa.status_code == 400
    assert "model_case_dataset_mismatch" in nasa.text


def test_model_and_train_official_combos_are_page_local(platform):
    """模型/训练组合按模型列出且可跨数据集，只覆盖当前页。"""
    c, p, _, data, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks", json={"name": "page-combo", "case_id": "shapenet_car_abupt"}
    )
    assert created.status_code == 200, created.text
    t = created.json()
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    model_cfg = c.get(url + "/configuration?stage=model").json()
    model_ids = {item["id"] for item in model_cfg["capabilities"]["official_combos"]["options"]}
    assert {"shapenet_car_abupt", "nasa_crm_abupt"} <= model_ids
    assert "shapenet_car_transolver3_surface" in model_ids
    train_cfg = c.get(url + "/configuration?stage=train").json()
    assert train_cfg["capabilities"]["official_combos"]["current_model_id"] == "abupt"

    root = c.app.state.services.project(p)
    captured = task.read_configuration(root, t["id"])
    old_prep = data / "keep-preparation.json"
    old_prep.write_text("{}")
    old_weights = data / "keep-weights.pt"
    old_weights.write_text("x")
    stored = task.save_configuration(
        root,
        t["id"],
        public_patch(
            {
                "train": {
                    **captured["config"].get("train", {}),
                    "preparation": str(old_prep),
                    "learning_rate": 0.123,
                },
                "model": {
                    **captured["config"].get("model", {}),
                    "initial_weights": str(old_weights),
                },
            }
        ),
        revision=captured["revision"],
    )
    before = stored["config"]
    shapenet_blocks = before["model"]["parameters"]["blocks"]
    nasa_model = c.put(
        url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": stored["revision"],
            "target_case_id": "nasa_crm_abupt",
            "values": model_cfg["values"],
        },
    )
    assert nasa_model.status_code == 200, nasa_model.text
    loaded_model = nasa_model.json()["config"]
    assert loaded_model["model"]["parameters"]["blocks"] == "pssssssssss"
    assert loaded_model["model"]["parameters"]["require_features"] is True
    assert loaded_model["inputs"]["train"]["initial_weights"] == str(old_weights)
    assert loaded_model["train"]["learning_rate"] == 0.123
    assert loaded_model["inputs"]["train"]["preparation"] == str(old_prep)
    assert loaded_model["trainprep"]["normalization"]["fields"]["surface_position"]["scale"] == 1000
    assert loaded_model["model"]["parameters"]["blocks"] != shapenet_blocks

    transolver_train = c.put(
        url + "/configuration",
        json={
            "stage": "train",
            "expected_revision": nasa_model.json()["revision"],
            "target_case_id": "shapenet_car_transolver3_surface",
            "values": train_cfg["values"],
        },
    )
    assert transolver_train.status_code == 400, transolver_train.text
    assert "official_combo_model_mismatch" in transolver_train.text

    nasa_train = c.put(
        url + "/configuration",
        json={
            "stage": "train",
            "expected_revision": nasa_model.json()["revision"],
            "target_case_id": "nasa_crm_abupt",
            "values": train_cfg["values"],
        },
    )
    assert nasa_train.status_code == 200, nasa_train.text
    loaded_train = nasa_train.json()["config"]
    assert loaded_train["train"]["learning_rate"] == 5.0e-05
    assert loaded_train["train"]["optimizer"] == "lion"
    assert loaded_train["inputs"]["train"]["preparation"] == str(old_prep)
    assert loaded_train["model"]["parameters"]["blocks"] == "pssssssssss"
    assert loaded_train["inputs"]["train"]["initial_weights"] == str(old_weights)


def test_trainprep_rejects_non_positive_field_scale(platform):
    c, p, t, _, _ = platform
    cfg = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/configuration?stage=trainprep").json()
    values = deepcopy(cfg["values"])
    name = next(iter(values.get("normalization", {}).get("fields") or {"surface_position": {}}))
    values.setdefault("normalization", {}).setdefault("fields", {}).setdefault(name, {})
    values["normalization"]["fields"][name]["scale"] = 0
    response = c.put(
        f"/api/v1/projects/{p}/tasks/{t['id']}/configuration",
        json={"stage": "trainprep", "expected_revision": cfg["revision"], "values": values},
    )
    assert response.status_code == 400, response.text
    assert "invalid_field_scale" in response.text


@pytest.mark.parametrize(
    "status,mode,expected",
    [
        ("stopped", "execute", True),
        ("failed", "execute", True),
        ("running", "execute", False),
        ("stopping", "execute", False),
        ("stopped", "trial", False),
    ],
)
def test_terminal_run_only_exposes_committed_resume_checkpoint(
    platform, monkeypatch, status, mode, expected
):
    """停止/异常后的完整权重可恢复；残留准备和未登记权重不可选。"""
    import json

    from ai4e_task.tasks import artifacts

    c, p, t, data, _ = platform
    run_dir = data / "interrupted"
    (run_dir / "artifacts").mkdir(parents=True)
    for name in ("latest.pt", "unregistered.pt", "preparation.json", "manifest.json"):
        (run_dir / name).write_text("{}")
    items = {}
    for kind, name in [
        ("checkpoint", "latest.pt"),
        ("preparation", "preparation.json"),
        ("dataset", "manifest.json"),
    ]:
        items[name] = {
            "name": name,
            "kind": kind,
            "stage": "train",
            "path": str(run_dir / name),
            "digest": "committed",
            "semantics": {"type": "aero.checkpoint"} if kind == "checkpoint" else {},
            "dependencies": [],
        }
    (run_dir / "artifacts/assets.json").write_text(
        json.dumps({"schema_version": 1, "items": items})
    )
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "interrupted",
                "task_id": t["id"],
                "status": status,
                "operation_mode": mode,
                "run_dir": str(run_dir),
                "data_dir": str(run_dir),
            }
        ],
    )
    listed = artifacts.list_stage_artifacts(
        c.app.state.services.project(p), t["id"], {"data0": data}
    )
    assert [(i["binding"], i["name"]) for i in listed] == (
        [("inputs.train.resume", "latest.pt")] if expected else []
    )
    response = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs")
    assert response.status_code == 200
    candidates = [i for i in response.json() if i.get("run_id") == "interrupted"]
    assert [(i["binding"], i["name"]) for i in candidates] == (
        [("inputs.train.resume", "latest.pt")] if expected else []
    )


def test_model_official_sampling_counts_are_not_preparation_conflicts(platform):
    """模型页加载官方采样点数、缺键或额外 split 不把刚准备结果报成冲突。"""
    from ai4e_server.modules.capabilities.model_cases import official_page_values

    from ai4e_core.applications.aero_cfd.inspection import normalize_config
    from ai4e_core.applications.aero_cfd.trainprep.preparation import (
        contract_conflict_message,
        declarations,
        frozen_contract,
    )

    c, p, t, _, _ = platform
    service = c.app.state.services
    captured = task.read_configuration(service.project(p), t["id"])
    prepared = declarations(normalize_config(captured["config"]))
    official = official_page_values(service, "shapenet_car_abupt", "model")
    current = deepcopy(prepared)
    current["sampling"] = deepcopy(official["sampling"])
    current["trainprep"] = {**current["trainprep"], "split": {"method": "original"}}
    current["trainprep"].pop("use_physics_features", None)
    assert frozen_contract(prepared) == frozen_contract(current)
    changed = deepcopy(prepared)
    changed["data_specs"] = {
        **changed["data_specs"],
        "position_dim": changed["data_specs"]["position_dim"] + 1,
    }
    message = contract_conflict_message(frozen_contract(prepared), frozen_contract(changed))
    assert "数据规格不一致" in message
    assert "请重新运行 trainprep" in message
