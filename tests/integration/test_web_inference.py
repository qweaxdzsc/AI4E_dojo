"""推理 HTTP 边界、结果固定引用与任务作用域。"""

import ai4e_task as task

from tests.integration.test_web_project_task import platform as _platform

platform = _platform


def test_catalog_hides_private_paths_and_merges_aliases(platform, monkeypatch):
    client, project, item, _, _ = platform
    monkeypatch.setattr(task, "inference_devices", lambda *_: [{"id": "cpu", "busy": False}])
    candidates = [
        {
            "id": "r:" + name,
            "name": name,
            "run_id": "r",
            "revision": "abc",
            "status": "running",
            "path": "/private/model.pt",
            "contract": {"private": "config"},
            "preparation": {"path": "/private/prep.json", "digest": "d", "revision": "e"},
            "compatibility": {"status": "compatible"},
        }
        for name in ["last.pt", "latest.pt"]
    ]
    monkeypatch.setattr(task, "list_inference_checkpoints", lambda *_: candidates)
    response = client.get(f"/api/v1/projects/{project}/tasks/{item['id']}/inference/checkpoints")
    assert response.status_code == 200, response.text
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["aliases"] == ["latest.pt"]
    assert "/private" not in response.text and "contract" not in response.text


def test_result_uses_fixed_content_reference(platform, monkeypatch):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    data = root / "tasks" / item["id"] / "data" / "run"
    data.mkdir(parents=True)
    output = data / "metrics.csv"
    output.write_text("sample,l2\na,0.1\n")
    monkeypatch.setattr(
        task,
        "inference_results",
        lambda *_: {
            "items": [
                {
                    "run_id": "run",
                    "checkpoint": {"id": "r:last.pt"},
                    "sample": "a",
                    "metrics": {},
                    "files": [
                        {"path": str(output), "name": output.name, "size": output.stat().st_size}
                    ],
                }
            ],
            "comparison": {"status": "insufficient"},
        },
    )
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/inference/batches/b/results"
    response = client.get(url)
    assert response.status_code == 200, response.text
    ref = response.json()["items"][0]["files"][0]["ref"]
    assert str(root) not in response.text
    content = f"/api/v1/projects/{project}/assets/{ref['asset_id']}/content"
    assert client.get(content, params={"revision": ref["revision"]}).content == output.read_bytes()
    output.write_text("changed")
    assert client.get(content, params={"revision": ref["revision"]}).status_code == 409


def test_inference_cannot_bypass_fixed_batch(platform):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    revision = task.read_configuration(root, item["id"])["revision"]
    response = client.post(
        f"/api/v1/projects/{project}/tasks/{item['id']}/stages/infer/operations",
        json={"mode": "execute", "expected_revision": revision},
    )
    assert response.status_code == 400 and "inference_requires_fixed_batch" in response.text
    assert task.list_runs(root, item["id"]) == []


def test_unknown_recipe_is_not_silently_executed(platform):
    client, project, item, _, _ = platform
    from pathlib import Path

    root = client.app.state.services.project(project)
    path = Path(task.get_task(root, item["id"])["directory"]) / "recipe" / "infer.py"
    path.write_text('raise RuntimeError("custom algorithm")')
    response = client.post(
        f"/api/v1/projects/{project}/tasks/{item['id']}/inference/batches",
        json={"expected_revision": "revision", "checkpoints": [{"id": "r:last.pt", "revision": "bytes"}], "samples": ["sample"]}
    )
    assert response.status_code == 400 and "recipe_profile_changed" in response.text
