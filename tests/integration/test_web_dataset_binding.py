"""数据源绑定 HTTP 契约；空目录/假 H5 仅作范围和类型夹具，不作算法验收。"""

from pathlib import Path

import pytest
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
CASES = (
    "shapenet_car_abupt",
    "shapenet_car_transolver3_surface",
    "nasa_crm_abupt",
    "nasa_crm_transolver3",
)


@pytest.fixture
def binding_platform(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "cars").mkdir()
    for name in ("train_h5", "test_h5", "connectivity_h5"):
        (raw / (name + ".h5")).write_text("interface fixture, not scientific data")
    settings = Settings(tmp_path / "platform", RECIPE, [raw])
    with TestClient(create_app(settings)) as client:
        response = client.post("/api/v1/projects", json={"name": "binding fixtures"})
        assert response.status_code == 200, response.text
        yield client, "/api/v1/projects/" + response.json()["id"], raw, settings


def create(client, base, case):
    response = client.post(base + "/tasks", json={"name": case, "case_id": case})
    assert response.status_code == 200, response.text
    return response.json()


def sources(case):
    if case.startswith("shapenet"):
        return {"root": {"root": "data0", "path": "cars"}}
    return {
        key: {"root": "data0", "path": key + ".h5"}
        for key in ("train_h5", "test_h5", "connectivity_h5")
    }


@pytest.mark.parametrize("case", CASES)
def test_four_cases_bind_with_revision_and_no_new_version(binding_platform, case):
    client, base, _, _ = binding_platform
    catalog = client.get(base + "/tasks/cases").json()
    declaration = next(item for item in catalog if item["id"] == case)
    assert declaration["dataset_id"] == ("nasa_crm" if case.startswith("nasa") else "shapenet_car")
    assert declaration["model_id"] == ("abupt" if "abupt" in case else "transolver3")
    assert declaration["binding_mode"] == ("files" if case.startswith("nasa") else "directory")
    task = create(client, base, case)
    url = base + "/tasks/" + task["id"] + "/dataset"
    response = client.get(url)
    assert response.status_code == 200, response.text
    initial = response.json()
    assert initial["status"] == "unbound"
    assert initial["dataset_id"] == declaration["dataset_id"]
    assert initial["binding_mode"] == declaration["binding_mode"]
    request = {"expected_revision": initial["revision"], "sources": sources(case)}
    saved = client.put(url, json=request)
    assert saved.status_code == 200, saved.text
    value = saved.json()
    assert value["status"] == "valid" and value["errors"] == []
    assert value["sources"] == sources(case)
    assert value["revision"] != initial["revision"]
    assert client.get(url).json() == value
    assert client.put(url, json=request).status_code == 409
    assert len(client.get(base + "/lineage").json()) == 1
    assert client.get(base + "/tasks/" + task["id"]).json()["version_id"] == task["version_id"]


def test_shapenet_restart_fork_and_management_keep_binding(binding_platform):
    client, base, _, settings = binding_platform
    case = CASES[0]
    task = create(client, base, case)
    url = base + "/tasks/" + task["id"]
    initial = client.get(url + "/dataset").json()
    response = client.put(
        url + "/dataset", json={"expected_revision": initial["revision"], "sources": sources(case)}
    )
    assert response.status_code == 200, response.text
    saved = response.json()
    assert client.patch(url, json={"name": "renamed"}).status_code == 200
    assert len(client.get(base + "/lineage").json()) == 1
    fork = client.post(url + "/fork", json={"name": "derived"})
    assert fork.status_code == 200, fork.text
    assert fork.json()["parent_version_id"] == task["version_id"]
    child = client.get(base + "/tasks/" + fork.json()["id"] + "/dataset").json()
    assert child["status"] == "valid" and child["sources"] == saved["sources"]
    with TestClient(create_app(settings)) as restarted:
        assert restarted.get(url + "/dataset").json() == saved
        assert len(restarted.get(base + "/lineage").json()) == 2


@pytest.mark.parametrize(
    "bad",
    [
        {"root": {"root": "data0", "path": "../outside"}},
        {"root": {"root": "data0", "path": "/tmp"}},
        {"root": {"root": "project", "path": ""}},
        {"root": {"root": "data0", "path": "train_h5.h5"}},
        {"root": {"root": "data0", "path": "escape"}},
    ],
)
def test_controlled_directory_rejects_escape_and_files(binding_platform, bad):
    client, base, raw, _ = binding_platform
    outside = raw.parent / "outside"
    outside.mkdir()
    (raw / "escape").symlink_to(outside, target_is_directory=True)
    task = create(client, base, CASES[0])
    url = base + "/tasks/" + task["id"] + "/dataset"
    before = client.get(url).json()
    response = client.put(url, json={"expected_revision": before["revision"], "sources": bad})
    assert 400 <= response.status_code < 500, response.text
    assert client.get(url).json() == before


def test_nasa_requires_all_files_and_refresh_reports_missing(binding_platform):
    client, base, raw, _ = binding_platform
    case = CASES[2]
    task = create(client, base, case)
    url = base + "/tasks/" + task["id"] + "/dataset"
    before = client.get(url).json()
    incomplete = sources(case)
    del incomplete["connectivity_h5"]
    response = client.put(
        url, json={"expected_revision": before["revision"], "sources": incomplete}
    )
    assert 400 <= response.status_code < 500, response.text
    assert client.get(url).json() == before
    saved = client.put(
        url, json={"expected_revision": before["revision"], "sources": sources(case)}
    )
    assert saved.status_code == 200, saved.text
    (raw / "connectivity_h5.h5").unlink()
    invalid = client.get(url).json()
    assert invalid["status"] == "invalid" and invalid["errors"]
    assert invalid["revision"] == saved.json()["revision"]


def test_history_recipe_without_components_can_bind_directory(binding_platform):
    client, base, _, settings = binding_platform
    created = client.post(base + "/tasks", json={"name": "history recipe"})
    assert created.status_code == 200, created.text
    task = created.json()
    matches = list(settings.root.rglob("tasks/" + task["id"] + "/recipe/config.yaml"))
    assert len(matches) == 1
    config = matches[0]
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(config)
    assert "components" in cfg
    del cfg["components"]
    OmegaConf.save(cfg, config)
    assert "components" not in OmegaConf.load(config)
    url = base + "/tasks/" + task["id"] + "/dataset"
    initial = client.get(url)
    assert initial.status_code == 200, initial.text
    value = initial.json()
    assert value["dataset_id"] == "shapenet_car"
    assert value["binding_mode"] == "directory"
    assert value["status"] in {"unbound", "invalid"}
    saved = client.put(
        url, json={"expected_revision": value["revision"], "sources": sources(CASES[0])}
    )
    assert saved.status_code == 200, saved.text
    assert saved.json()["status"] == "valid"


def test_legacy_creation_accepts_bound_directory(binding_platform):
    client, base, _, _ = binding_platform
    response = client.post(
        base + "/tasks", json={"name": "legacy bound", "data_root": "data0", "data_path": "cars"}
    )
    assert response.status_code == 200, response.text
    binding = client.get(base + "/tasks/" + response.json()["id"] + "/dataset").json()
    assert binding["status"] == "valid"
    assert binding["sources"] == sources(CASES[0])


@pytest.mark.parametrize("state", ["unbound", "invalid"])
def test_binding_gate_prevents_preflight_and_execution(binding_platform, state):
    client, base, raw, _ = binding_platform
    task = create(client, base, CASES[0])
    url = base + "/tasks/" + task["id"]
    binding = client.get(url + "/dataset").json()
    if state == "invalid":
        response = client.put(
            url + "/dataset",
            json={"expected_revision": binding["revision"], "sources": sources(CASES[0])},
        )
        assert response.status_code == 200, response.text
        (raw / "cars").rmdir()
        binding = client.get(url + "/dataset").json()
    assert binding["status"] == state
    payload = {
        "revision": binding["revision"],
        "root": "data0",
        "files": ["train_h5.h5"],
        "all_selected": True,
    }
    for operation in ("preflight", "execute"):
        rejected = client.post(url + "/rawprep/" + operation, json=payload)
        assert rejected.status_code == 400, rejected.text
        assert "dataset_binding_" + state in rejected.text
    assert client.get(base + "/runs").json() == []


def test_selection_inside_allowed_root_but_outside_binding_rejected(binding_platform):
    client, base, raw, _ = binding_platform
    task = create(client, base, CASES[0])
    url = base + "/tasks/" + task["id"]
    before = client.get(url + "/dataset").json()
    saved = client.put(
        url + "/dataset",
        json={"expected_revision": before["revision"], "sources": sources(CASES[0])},
    )
    assert saved.status_code == 200, saved.text
    # 普通文件存在且位于授权根内；绑定范围必须先于算法格式检查拒绝。
    outside = raw / "other-car"
    outside.mkdir()
    (outside / "quadpress_smpl.vtk").write_text("binding-only fixture")
    payload = {
        "revision": saved.json()["revision"],
        "root": "data0",
        "files": ["other-car/quadpress_smpl.vtk"],
        "all_selected": True,
    }
    for operation in ("preflight", "execute"):
        rejected = client.post(url + "/rawprep/" + operation, json=payload)
        assert rejected.status_code == 400, rejected.text
        assert "dataset_selection_outside_binding" in rejected.text
    assert client.get(base + "/runs").json() == []


def test_legacy_bound_path_disappears_is_invalid(binding_platform):
    client, base, raw, _ = binding_platform
    response = client.post(
        base + "/tasks",
        json={"name": "legacy path disappears", "data_root": "data0", "data_path": "cars"},
    )
    assert response.status_code == 200, response.text
    url = base + "/tasks/" + response.json()["id"] + "/dataset"
    before = client.get(url).json()
    assert before["status"] == "valid"
    (raw / "cars").rmdir()
    after = client.get(url).json()
    assert after["status"] == "invalid" and after["errors"]
    assert after["revision"] == before["revision"]
