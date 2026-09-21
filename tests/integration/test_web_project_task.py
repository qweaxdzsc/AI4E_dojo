"""真实模板创建、配置修订和归档恢复的 HTTP 验收。"""

from pathlib import Path

import ai4e_task as task
import pytest
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"


@pytest.fixture
def platform(tmp_path):
    data = tmp_path / "raw"
    data.mkdir()
    settings = Settings(tmp_path / "platform", RECIPE, [data])
    app = create_app(settings)
    with TestClient(app) as client:
        response = client.post("/api/v1/projects", json={"name": "流场研究"})
        assert response.status_code == 200, response.text
        project = response.json()["id"]
        response = client.post(f"/api/v1/projects/{project}/tasks", json={"name": "baseline"})
        assert response.status_code == 200, response.text
        yield client, project, response.json(), data, settings


def test_projects_tasks_configuration_restart(platform):
    c, p, t, _, settings = platform
    base = f"/api/v1/projects/{p}"
    assert c.patch(base, json={"name": "renamed", "archived": True}).json()["archived"]
    assert c.patch(base, json={"archived": False}).json()["name"] == "renamed"
    cfg = c.get(base + f"/tasks/{t['id']}/rawprep").json()
    cfg["rawprep"]["vtkhdf"] = True
    cfg["processed_name"] = "test_prepared_dataset"
    saved = c.put(
        base + f"/tasks/{t['id']}/rawprep",
        json={k: v for k, v in cfg.items() if k != "processed_name_status"},
    )
    assert saved.status_code == 200, saved.text
    assert (
        c.put(
            base + f"/tasks/{t['id']}/rawprep",
            json={k: v for k, v in cfg.items() if k != "processed_name_status"},
        ).status_code
        == 409
    )
    assert len(c.get(base + "/lineage").json()) == 1
    assert c.patch(base + f"/tasks/{t['id']}", json={"archived": True}).json()["archived"]
    assert (
        c.put(
            base + f"/tasks/{t['id']}/rawprep",
            json={k: v for k, v in saved.json().items() if k != "processed_name_status"},
        ).status_code
        == 400
    )
    c.patch(base + f"/tasks/{t['id']}", json={"archived": False, "name": "changed"})
    child = c.post(base + f"/tasks/{t['id']}/fork", json={"name": "child"}).json()
    assert child["parent_version_id"] == t["version_id"]
    with TestClient(create_app(settings)) as other:
        assert len(other.get(base + "/tasks").json()) == 2
        assert other.get(base + f"/tasks/{t['id']}/rawprep").json() == saved.json()
    project = c.app.state.services.project(p)
    cfg = task.read_configuration(project, t["id"])
    assert cfg["config"]["train"]["max_epochs"] == 2


def test_unbound_template_create_does_not_weaken_execution(platform):
    c, p, t, _, _ = platform
    project = c.app.state.services.project(p)
    with pytest.raises(ValueError, match="processed_dataset_name_required"):
        task.submit_run(project, t["id"])
    with pytest.raises(FileNotFoundError):
        task.submit_run(project, t["id"], overrides=["dataset.processed_name=unbound"])
    assert task.list_runs(project, t["id"]) == []


def test_case_create_clears_template_manifest_placeholder(platform):
    """新建外流案例不把模板数据根上的清单占位带进用户任务。"""
    c, p, _, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "case-manifest", "case_id": "shapenet_car_abupt"},
    )
    assert created.status_code == 200, created.text
    project = c.app.state.services.project(p)
    cfg = task.read_configuration(project, created.json()["id"])
    assert cfg["config"].get("train", {}).get("manifest") in {None, ""}
    items = c.get(f"/api/v1/projects/{p}/tasks/{created.json()['id']}/stage-inputs").json()
    assert not any(item["binding"] == "train.manifest" for item in items)


def test_new_task_vtkhdf_follows_case_capability(platform):
    """新建官方外流案例默认保留来源已有的网格拓扑。"""
    c, p, _, _, _ = platform
    for case_id, enabled in (
        ("shapenet_car_abupt", True),
        ("shapenet_car_transolver3_surface", True),
        ("shapenet_car_transolver3_volume", True),
            ("nasa_crm_abupt", True),
            ("nasa_crm_transolver3", True),
    ):
        created = c.post(
            f"/api/v1/projects/{p}/tasks",
            json={"name": f"vtkhdf-{case_id}", "case_id": case_id},
        )
        assert created.status_code == 200, created.text
        shown = c.get(f"/api/v1/projects/{p}/tasks/{created.json()['id']}/rawprep").json()
        assert shown["profile"]["vtkhdf"] is enabled, case_id
        assert shown["rawprep"]["vtkhdf"] is enabled, case_id
