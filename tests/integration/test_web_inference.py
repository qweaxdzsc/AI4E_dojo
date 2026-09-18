"""推理 HTTP 边界、结果固定引用与任务作用域。"""

import inspect
from pathlib import Path

import ai4e_task as task
import pytest
from ai4e_server.modules.inference import application as infer_app

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


def test_server_samples_source_keeps_vtk_exports():
    text = (
        Path(__file__).resolve().parents[2]
        / "packages/ai4e-server/modules/inference/application.py"
    ).read_text()
    assert 'if "vtk_exports" in value:' in text
    assert 'result["vtk_exports"] = value["vtk_exports"]' in text


def test_server_options_source_keeps_optional_new_keys():
    text = (
        Path(__file__).resolve().parents[2] / "packages/ai4e-server/modules/inference/api.py"
    ).read_text()
    assert "export_pointcloud: bool | None = None" in text
    assert "export_mesh: bool | None = None" in text
    assert "exclude_unset=True" in text


def test_old_export_vtk_evaluate_only_does_not_materialize_new_keys():
    from ai4e_server.modules.inference.api import InferenceOptionsRequest

    field = InferenceOptionsRequest.model_fields["export_pointcloud"]
    if field.default is not None:
        pytest.skip("安装副本尚未重装 ai4e-server")
    dumped = InferenceOptionsRequest(
        evaluate=True, save_predictions=False, export_vtk=False
    ).model_dump(exclude_unset=True)
    assert "export_pointcloud" not in dumped
    assert "export_mesh" not in dumped
    assert dumped["export_vtk"] is False


def test_sample_catalog_keeps_vtk_exports(platform, monkeypatch):
    if "vtk_exports" not in inspect.getsource(infer_app.samples):
        pytest.skip("安装副本尚未重装 ai4e-server")
    client, project, item, _, _ = platform
    capability = {
        "pointcloud": {"available": True, "include_truth": True},
        "mesh": {
            "available": False,
            "include_truth": True,
            "reason": "训练集没有可还原的 VTK 网格",
        },
    }

    def catalog(*_args, **_kwargs):
        return {
            "partitions": {"test": ["a"]},
            "fields": [],
            "metrics": [],
            "selection_supported": True,
            "preparation": {"digest": "d", "revision": "r"},
            "vtk_exports": capability,
        }

    monkeypatch.setattr(task, "inference_samples", catalog)
    response = client.get(
        f"/api/v1/projects/{project}/tasks/{item['id']}/inference/samples",
        params={"checkpoint_id": "run:last.pt"},
    )
    assert response.status_code == 200, response.text
    assert response.json().get("vtk_exports") == capability


def test_missing_sample_catalog_is_not_data_root_error(platform, monkeypatch):
    client, project, item, _, _ = platform

    def boom(*_args, **_kwargs):
        raise FileNotFoundError("/missing/preparation.json")

    monkeypatch.setattr(task, "inference_samples", boom)
    response = client.get(
        f"/api/v1/projects/{project}/tasks/{item['id']}/inference/samples",
        params={"checkpoint_id": "run:last.pt"},
    )
    assert response.status_code == 400, response.text
    assert "数据根未配置" not in response.text
    assert "准备" in response.text


def test_missing_inference_batch_is_not_data_root_error(platform):
    client, project, item, _, _ = platform
    response = client.get(
        f"/api/v1/projects/{project}/tasks/{item['id']}/inference/batches/missing"
    )
    assert response.status_code == 400, response.text
    assert "数据根未配置" not in response.text
    assert "不存在" in response.text or "清理" in response.text


def test_list_skips_missing_inference_batch_records(platform):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    from ai4e_task.storage.database import transaction
    from ai4e_task.storage.records import put

    with transaction(root) as db:
        put(db, "inference_batch", {"id": "ghost", "task_id": item["id"]})
    response = client.get(f"/api/v1/projects/{project}/tasks/{item['id']}/inference/batches")
    assert response.status_code == 200, response.text
    assert response.json()["items"] == []


def test_user_recipe_still_requires_valid_fixed_inputs(platform):
    client, project, item, _, _ = platform
    from pathlib import Path

    root = client.app.state.services.project(project)
    path = Path(task.get_task(root, item["id"])["directory"]) / "recipe" / "infer.py"
    path.write_text('raise RuntimeError("custom algorithm")')
    response = client.post(
        f"/api/v1/projects/{project}/tasks/{item['id']}/inference/batches",
        json={
            "expected_revision": "revision",
            "checkpoints": [{"id": "r:last.pt", "revision": "bytes"}],
            "samples": ["sample"],
        },
    )
    assert response.status_code in {400, 409}
    assert "recipe_profile_changed" not in response.text
    assert task.list_runs(root, item["id"]) == []
