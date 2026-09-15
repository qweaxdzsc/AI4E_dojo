"""E2：真实两样本默认/修改处理、独立 PT、清单和物理读回验收。"""

import json
import os
from pathlib import Path
from uuid import uuid4

import ai4e_task as task
import pytest
import torch
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient

from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.applications.aero_cfd.rawprep.catalog import sample_key

ROOT = Path(__file__).resolve().parents[2]


def ok(response):
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("case", ["shapenet_car_abupt", "nasa_crm_abupt"])
def test_real_default_modified_and_handoff(case):
    parent = os.environ.get("DOJO_MANIFEST_REAL_ROOT")
    assert parent, "必须显式指定 DOJO_MANIFEST_REAL_ROOT，不能跳过真实验收"
    parent = Path(parent)
    inputs = json.loads((parent / "inputs.json").read_text())
    target = parent / "real" / case / uuid4().hex
    roots = [
        Path(inputs["shapenet"]),
        Path(inputs["nasa"]["train_h5"]).parent,
        Path(inputs["nasa"]["test_h5"]).parent,
    ]
    with TestClient(create_app(Settings(target, ROOT / "recipes/aero_cfd", roots))) as client:
        project = ok(client.post("/api/v1/projects", json={"name": "声明驱动真实验收"}))["id"]
        base = f"/api/v1/projects/{project}"
        created = ok(client.post(base + "/tasks", json={"name": case, "case_id": case}))
        identity = created["id"]
        url = base + "/tasks/" + identity
        cfg = ok(client.get(url + "/rawprep"))
        assert cfg["profile"]["outputs"] and cfg["rawprep"]["save_fields"]
        binding = ok(client.get(url + "/dataset"))
        nasa = case.startswith("nasa")
        sources = (
            {
                "train_h5": {"root": "data1", "path": Path(inputs["nasa"]["train_h5"]).name},
                "test_h5": {"root": "data2", "path": Path(inputs["nasa"]["test_h5"]).name},
                "connectivity_h5": {
                    "root": "data2",
                    "path": Path(inputs["nasa"]["connectivity_h5"]).name,
                },
            }
            if nasa
            else {"root": {"root": "data0", "path": ""}}
        )
        ok(
            client.put(
                url + "/dataset",
                json={"expected_revision": binding["revision"], "sources": sources},
            )
        )
        actual_project = client.app.state.services.project(project)
        if not nasa:
            current = task.read_configuration(actual_project, identity)
            task.save_configuration(
                actual_project,
                identity,
                {"dataset": {"partition": inputs["car_samples"]}},
                revision=current["revision"],
            )
        selections = inputs["nasa_samples"] if nasa else inputs["car_samples"]
        scope = (
            {
                "mode": "samples",
                "values": [sample_key(k, n) for k, names in selections.items() for n in names],
            }
            if nasa
            else {"mode": "all", "values": []}
        )
        # 官方全名单发现与实际转换规模分开记录。
        evidence = {"case": case, "project": project, "task": identity, "runs": []}
        for modified in [False, True]:
            cfg = ok(client.get(url + "/rawprep"))
            if modified:
                removed = "surface_area" if nasa else "volume_normals"
                cfg["rawprep"]["save_fields"].remove(removed)
                cfg["rawprep"]["statistics"] = {"mode": "none", "fields": [], "position_fields": []}
                # 同时验证真正的逐场重命名，而非单成员容器。
                rename = "surface_cp" if nasa else "surface_pressure"
                cfg["rawprep"]["extraction"] = {
                    "layout": "fields",
                    "entries": [
                        {
                            "id": "fields",
                            "name": "独立场",
                            "outputs": [
                                {
                                    "id": name,
                                    "name": "selected_pressure" if name == rename else name,
                                    "members": [
                                        {
                                            "source_field": name,
                                            "output_member": name,
                                            "components": next(
                                                x["components"]
                                                for x in cfg["profile"]["outputs"]
                                                if x["name"] == name
                                            ),
                                        }
                                    ],
                                }
                                for name in cfg["rawprep"]["save_fields"]
                            ],
                        }
                    ],
                }
                cfg["rawprep"]["save_fields"] = [
                    "selected_pressure" if x == rename else x for x in cfg["rawprep"]["save_fields"]
                ]
                cfg = ok(client.put(url + "/rawprep", json=cfg))
                assert ok(client.get(url + "/rawprep")) == cfg
            catalog = ok(
                client.post(
                    url + "/rawprep/catalog",
                    json={"revision": cfg["revision"], "sample_scope": scope},
                )
            )
            assert len(catalog["samples"]) == 2 and not catalog["errors"], catalog
            request = {
                "revision": cfg["revision"],
                "sample_scope": scope,
                "catalog_revision": catalog["revision"],
                "idempotency_key": uuid4().hex,
            }
            if not modified:
                stale = client.post(
                    url + "/rawprep/preflight", json={**request, "catalog_revision": "outdated"}
                )
                assert stale.status_code == 400 and "stale" in stale.text
                unknown = client.post(
                    url + "/rawprep/catalog",
                    json={
                        **request,
                        "sample_scope": {"mode": "samples", "values": ["not-declared"]},
                    },
                )
                assert unknown.status_code == 400
            checked = ok(client.post(url + "/rawprep/preflight", json=request))
            assert checked["sample_count"] == 2
            started = ok(client.post(url + "/rawprep/execute", json=request))
            result = task.wait_run(actual_project, started["id"], timeout=300)
            assert result["status"] == "succeeded", task.read_log(actual_project, result["id"])
            manifest = Path(result["data_dir"]) / "manifest.json"
            index = ManifestIndex(manifest)
            baseline = ManifestIndex(parent / "baseline" / case / "data/manifest.json")
            from ai4e_core.abilities.data.source.physical import PhysicalView

            view = PhysicalView(manifest)
            for split, names in index.partitions.items():
                for i, name in enumerate(names):
                    values = index.read(split, i)
                    ref = baseline.read(split, i)
                    record = index.records[(split, name)]
                    for logical, filename in record["filemap"].items():
                        value = torch.load(Path(record["path"]) / filename, weights_only=True)
                        assert isinstance(value, torch.Tensor), logical
                        reference = (
                            rename if modified and logical == "selected_pressure" else logical
                        )
                        torch.testing.assert_close(value, ref[reference], rtol=0, atol=0)
                    if modified:
                        assert removed not in values and removed not in json.dumps(
                            index.describe()["physical_layout"]
                        )
                    sample = view.read(split, i)
                    assert sample["domains"]["surface"]["identity_basis"] == "source"
            from ai4e_core.abilities.data.validate.physical import validate_bindings

            if nasa:
                with pytest.raises(ValueError, match="missing_target"):
                    validate_bindings(
                        view.read("train", 0),
                        {
                            "domains": {
                                "surface": {
                                    "position": "surface_position",
                                    "targets": {"missing": "missing_target"},
                                }
                            }
                        },
                    )
            evidence["runs"].append(
                {
                    "modified": modified,
                    "id": result["id"],
                    "manifest": str(manifest),
                    "samples": 2,
                    "point_sampling": False,
                    "exact_baseline_match": True,
                }
            )
        (target / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
