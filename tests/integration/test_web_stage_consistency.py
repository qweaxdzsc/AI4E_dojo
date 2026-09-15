"""阶段事实、辅助检查失效和受控文件范围的回归。"""

import ai4e_task as task
import pytest

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
    assert c.get(base + "/stage-summary").json()["stages"]["model"]["status"] == "succeeded"
    path.write_text("changed")
    assert (
        c.get(base + "/stage-summary").json()["stages"]["model"]["reason"]
        == "input_revision_changed"
    )
    assert service.store.get("operation", "check")["status"] == "succeeded"
    task.save_configuration(
        service.project(p), t["id"], {"train": {"max_epochs": 3}}, revision=revision
    )
    assert (
        c.get(base + "/stage-summary").json()["stages"]["model"]["reason"]
        == "configuration_revision_changed"
    )


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
    result = query.get_stage_summary(tmp_path, "t")
    assert result["post"]["status"] == "not_run"
    assert result["rawprep"]["status"] == "unknown"
    assert result["train"]["status"] == "unknown"


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
        {"train": {"manifest": "../../../physical/manifest.json"}},
        revision=cfg["revision"],
    )
    monkeypatch.setattr(
        task,
        "list_stage_artifacts",
        lambda *_: [
            {
                "binding": "train.manifest",
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
        "bindings": {"train.manifest": ref},
    }
    saved = c.put(base + "/configuration", json=body)
    assert saved.status_code == 200, saved.text
    assert saved.json()["config"]["train"]["manifest"] == str(data / "manifest.json")
    assert saved.json()["config"]["train"]["max_epochs"] == 7
    assert c.put(base + "/configuration", json=body).status_code == 409
    body["expected_revision"] = saved.json()["revision"]
    body["bindings"] = {"train.manifest": None}
    assert c.put(base + "/configuration", json=body).json()["config"]["train"]["manifest"] is None
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
        assert record["entry"]["platform_case"] == case
        if case.startswith("nasa_crm"):
            assert "dataset.train_h5" in record["entry"]["inputs"]
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
        {"train": {"manifest": str(manifest), "preparation": str(prepared)}},
        revision=cfg["revision"],
    )
    endpoint = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs"
    response = c.get(endpoint)
    assert response.status_code == 200, response.text
    items = {item["binding"]: item for item in response.json()}
    for key in ("train.manifest", "train.preparation"):
        assert items[key]["selected"] and items[key]["ref"]["revision"]
        assert items[key]["run_id"] is None
        assert items[key]["origin"] == "configuration"
    assert str(data) not in response.text
    prepared.unlink()
    missing = c.get(endpoint)
    item = next(item for item in missing.json() if item["binding"] == "train.preparation")
    assert item["ref"] is None and not item["selected"]
    assert item["compatibility"] == {
        "status": "invalid",
        "reason": "binding_file_missing",
        "location": "train.preparation",
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
        {"train": {"manifest": "/no-such-dojo-root/missing-placeholder/manifest.json"}},
        revision=cfg["revision"],
    )
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    assert not any(item["binding"] == "train.manifest" for item in items)


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
        {"train": {"manifest": str(escaped)}},
        revision=cfg["revision"],
    )
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "train.manifest")
    assert item["ref"] is None and not item["selected"]
    assert item["compatibility"]["reason"] == "path_outside_root"
    assert str(escaped) not in str(items)


def test_run_manifest_on_registered_root_is_listed(platform, monkeypatch):
    """正式清单落在已登记数据根时仍可作为运行产物列出。"""
    from ai4e_task.tasks import artifacts

    c, p, t, data, _ = platform
    (data / "manifest.json").write_text("{}")
    monkeypatch.setattr(
        artifacts,
        "list_runs",
        lambda *_a, **_k: [
            {
                "id": "run-root",
                "status": "succeeded",
                "operation_mode": "execute",
                "data_dir": str(data),
                "run_dir": str(data / "missing-run"),
            }
        ],
    )
    listed = artifacts.list_stage_artifacts(
        c.app.state.services.project(p), t["id"], {"data0": data}
    )
    assert listed[0]["root"] == "data0" and listed[0]["path"] == "manifest.json"
    items = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs").json()
    item = next(item for item in items if item["binding"] == "train.manifest")
    assert item["origin"] == "run" and item["run_id"] == "run-root" and item["ref"]


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
    validate_split({"split": {"method": "original", "counts": {"train": 0, "test": 0, "eval": 0}}}, manifest)
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
        {"split": {"method": "random", "samples": ["a"], "counts": {"train": 1, "test": 0, "eval": 0}}},
        manifest,
    )
    with pytest.raises(ValueError, match="split_samples_required"):
        validate_split({"split": {"method": "random", "samples": [], "counts": {"train": 1, "test": 0, "eval": 0}}}, manifest)


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
def test_registered_model_switch_replaces_defaults_and_preserves_identity(
    platform, source, target_model
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
        },
        revision=captured["revision"],
    )
    options = c.get(url + "/model-options")
    assert options.status_code == 200, options.text
    options = options.json()
    assert options["current_model_id"] == ("abupt" if "abupt" in source else "transolver3")
    assert len(options["options"]) == 2
    assert {item["id"] for item in options["options"]} == {"abupt", "transolver3"}
    assert all(item["dataset_id"] == options["dataset_id"] for item in options["options"])
    chosen = next(item for item in options["options"] if item["id"] == target_model)
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
        },
    )
    assert response.status_code == 200, response.text
    saved = response.json()
    actual = saved["config"]
    assert actual["model"] == values
    assert actual["components"]["model"] == chosen["component"]
    expected_train = deepcopy(chosen["train"])
    expected_train["manifest"] = cfg["config"]["train"]["manifest"]
    expected_train.pop("preparation", None)
    expected_train["resume"] = None
    assert actual["train"] == expected_train
    assert actual["trainprep"] == chosen["trainprep"]
    for key in ("dataset", "rawprep", "paths", "data_root", "run_root"):
        assert actual[key] == cfg["config"][key]
    assert actual["post"] == {**cfg["config"]["post"], "checkpoint": "last"}
    assert old.read_text() == "{}"
    assert task.get_task(root, t["id"])["entry"] == original_entry
    assert task.get_task(root, t["id"])["version_id"] == t["version_id"]
    assert task.read_configuration(root, t["id"]) == saved
    assert c.get(url + "/model-options").json()["current_model_id"] == target_model
    reread = c.get(url + "/configuration?stage=model")
    assert reread.status_code == 200, reread.text
    assert reread.json()["values"]["parameters"][parameter] == 96
    if target_model == "transolver3":
        assert "supernodes" not in reread.json()["values"]["sampling"]
        assert reread.json()["values"]["sampling"]["stride"] == 4
        assert reread.json()["values"]["parameters"]["slice_num"] == 64
        assert reread.json()["capabilities"]["losses"]["configurable"] is False
        assert reread.json()["capabilities"]["sampling"]["configurable"] is True
        assert reread.json()["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"] is True
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
    """绕过浏览器也不能跨数据集、旧修订覆盖或把旧准备绑回。"""
    c, p, t, _, _ = platform
    url = f"/api/v1/projects/{p}/tasks/{t['id']}"
    cfg = c.get(url + "/configuration").json()
    base = {
        "stage": "model",
        "expected_revision": cfg["revision"],
        "values": {},
        "target_case_id": "nasa_crm_abupt",
    }
    response = c.put(url + "/configuration", json=base)
    assert response.status_code == 400 and "model_case_dataset_mismatch" in response.text
    base["target_case_id"] = "shapenet_car_transolver3_surface"
    assert (
        c.put(url + "/configuration", json={**base, "expected_revision": "stale"}).status_code
        == 409
    )
    response = c.put(
        url + "/configuration",
        json={**base, "bindings": {"train.preparation": {"asset_id": "old"}}},
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
        {"post": {"checkpoint": tag}, "train": {"manifest": str(data / "missing.json")}},
        revision=cfg["revision"],
    )
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/stage-inputs"
    items = c.get(url).json()
    assert not any(
        i["binding"] == "post.checkpoint" and i["compatibility"]["status"] == "invalid"
        for i in items
    )
    assert any(
        i["binding"] == "train.manifest" and i["compatibility"]["reason"] == "binding_file_missing"
        for i in items
    )
    task.save_configuration(
        root,
        t["id"],
        {"post": {"checkpoint": str(data / "missing.pt")}},
        revision=saved["revision"],
    )
    assert any(
        i["binding"] == "post.checkpoint" and i["compatibility"]["reason"] == "binding_file_missing"
        for i in c.get(url).json()
    )


@pytest.mark.parametrize("case", ["shapenet_car_abupt", "nasa_crm_abupt"])
def test_model_switch_real_preparation_handoff(platform, case):
    """显式开启的真实 CFD 验收：原始处理、旧准备拒绝、新准备与结构输入留档。"""
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
    captured = task.save_configuration(
        root,
        item["id"],
        {
            "dataset": dataset,
            "run_root": str(data.parent / "runs"),
            "data_root": str(data.parent / "outputs"),
            "train": {"device": "cpu"},
        },
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
    manifest = str(Path(raw["data_dir"]) / "manifest.json")
    cfg = task.read_configuration(root, item["id"])
    cfg = task.save_configuration(
        root, item["id"], {"train": {"manifest": manifest}}, revision=cfg["revision"]
    )
    old_run = execute("trainprep")
    old = str(Path(old_run["run_dir"]) / "artifacts/preparation.json")
    old_content = Path(old).read_bytes()
    cfg = task.save_configuration(
        root, item["id"], {"train": {"preparation": old}}, revision=cfg["revision"]
    )
    options = c.get(url + "/model-options").json()
    chosen = next(o for o in options["options"] if o["id"] == "transolver3")
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
    assert switched["config"]["train"]["manifest"] == manifest
    assert not switched["config"]["train"].get("preparation")
    with pytest.raises(ValueError, match="声明已变化|内容或扩展实现不一致"):
        task.inspect_task(
            root,
            item["id"],
            "validate_configuration",
            revision=switched["revision"],
            output_dir=str(data.parent / "old-check"),
            selection={"stage": "model", "bindings": {"train.preparation": old}},
        )
    # 同数据集并不保证字段齐全：用独立清单移除目标所需法向声明，原产物不改写。
    incomplete = json.loads(Path(manifest).read_text())
    for sample in incomplete["samples"]:
        sample.get("filemap", {}).pop("surface_normals", None)
        sample.get("fields", {}).pop("surface_normals", None)
        if "names" in sample:
            sample["names"] = [name for name in sample["names"] if name != "surface_normals"]
    incomplete_path = Path(manifest).with_name("incomplete-model-test.json")
    incomplete_path.write_text(json.dumps(incomplete))
    with pytest.raises(ValueError, match="surface_normals|法向"):
        task.inspect_task(
            root,
            item["id"],
            "validate_configuration",
            revision=switched["revision"],
            output_dir=str(data.parent / "missing-field-check"),
            selection={"stage": "model", "bindings": {"train.manifest": str(incomplete_path)}},
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
        root, item["id"], {"train": {"preparation": new}}, revision=switched["revision"]
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
    assert transolver["capabilities"]["sampling"]["configurable"] is True
    assert transolver["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"] is True
    assert next(item for item in options["options"] if item["id"] == "abupt")["capabilities"][
        "sampling"
    ]["configurable"] is True
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
    options = c.get(f"/api/v1/projects/{p}/tasks/{created.json()['id']}/model-options").json()
    assert {item["id"] for item in options["options"]} == {"abupt", "transolver3"}
    assert all(not item.get("variants") for item in options["options"])
    by_id = {item["id"]: item for item in options["options"]}
    assert by_id["abupt"]["capabilities"]["sampling"]["configurable"] is True
    assert by_id["transolver3"]["capabilities"]["sampling"]["configurable"] is True
    assert by_id["transolver3"]["capabilities"]["sampling"]["constraints"]["stride"]["readOnly"] is True
    assert by_id["transolver3"]["capabilities"]["losses"]["terms"]


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
                "binding": "train.manifest",
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
    assert source == {"train.manifest": str((data / "manifest.json").resolve())}
    _trace_selection(service, p, t["id"])
    after = c.get(url + "/configuration").json()
    assert after["config"]["train"] == before["config"]["train"]
    assert after["revision"] == before["revision"]


def test_auto_trace_prefers_recent_compatible_preparation(platform, monkeypatch):
    """同时有旧相容准备和新清单时取最近相容准备。"""
    from ai4e_server.modules.capabilities.trace_source import latest_trace_source

    c, p, t, data, _ = platform
    root = c.app.state.services.project(p)
    cfg = task.read_configuration(root, t["id"])
    (data / "manifest.json").write_text("{}")
    prep = data / "preparation.json"
    prep.write_text(
        __import__("json").dumps(
            {
                "declarations": {
                    "component": cfg["config"]["components"]["model"],
                    "model": cfg["config"]["model"],
                }
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
                "binding": "train.preparation",
                "name": "preparation.json",
                "root": "data0",
                "path": "preparation.json",
            },
            {
                "id": "raw",
                "created_at": "2026-02-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "train.manifest",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            },
        ],
    )
    source = latest_trace_source(c.app.state.services, p, t["id"])
    assert source == {"train.preparation": str(prep.resolve())}


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


def test_auto_trace_falls_back_to_manifest_after_incompatible_switch(platform, monkeypatch):
    """换模后旧准备不相容则改用最近正式清单。"""
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
    chosen = next(item for item in options["options"] if item["id"] == "transolver3")
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
                "binding": "train.preparation",
                "name": "old-prep.json",
                "root": "data0",
                "path": "old-prep.json",
            },
            {
                "id": "raw",
                "created_at": "2026-01-01T00:00:00",
                "status": "succeeded",
                "operation_mode": "execute",
                "binding": "train.manifest",
                "name": "manifest.json",
                "root": "data0",
                "path": "manifest.json",
            },
        ],
    )
    source = latest_trace_source(c.app.state.services, p, t["id"])
    assert source == {"train.manifest": str((data / "manifest.json").resolve())}
    train = switched.json()["config"]["train"]
    assert not train.get("preparation")
