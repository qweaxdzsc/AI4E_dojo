"""后处理HTTP受控文件与分页，不返回服务器绝对路径。"""

import ai4e_task as task

from tests.integration.test_web_project_task import (
    platform as platform,  # noqa: PLC0414 - pytest跨模块夹具
)


def test_result_catalog_does_not_list_files(platform, monkeypatch):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    monkeypatch.setattr(
        task,
        "post_results",
        lambda *_: {
            "items": [
                {
                    "id": "i",
                    "revision": "r",
                    "batch_id": "b",
                    "run_id": "run",
                    "sample": "a",
                    "fields": [],
                    "evaluable": True,
                    "status": "succeeded",
                    "manifest": str(root / "hidden.json"),
                    "files": [],
                }
            ],
            "batches": [{"id": "b", "name": "批次"}],
            "errors": [],
            "files": [],
        },
    )
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/post/results"
    result = client.get(url)
    assert result.status_code == 200, result.text
    value = result.json()
    assert value["files"] == []
    assert value["items"][0]["id"] == "i"
    assert "manifest" not in value["items"][0]
    assert str(root) not in result.text


def test_result_files_list_and_download(platform, monkeypatch):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    folder = root / "tasks" / item["id"] / "data/post/demo"
    folder.mkdir(parents=True)
    path = folder / "metrics.json"
    path.write_text('{"a":1}')
    monkeypatch.setattr(
        task,
        "list_post_result_files",
        lambda *_args, **_kwargs: {
            "files": [
                {
                    "id": "f",
                    "name": path.name,
                    "tree_path": "指标/demo/metrics.json",
                    "path": str(path),
                    "size": 7,
                }
            ],
            "errors": [],
            "total": 1,
        },
    )
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/post/results"
    result = client.get(url, params={"view": "files"})
    assert result.status_code == 200, result.text
    assert str(root) not in result.text
    file = result.json()["files"][0]
    assert "ref" not in file
    assert file["root"] == "project"
    response = client.get(
        f"/api/v1/projects/{project}/files/download",
        params={"root": file["root"], "path": file["source_path"], "task_id": item["id"]},
    )
    assert response.content == path.read_bytes()
    assert client.get(url, params={"view": "files", "offset": 1}).json()["files"] == []
    assert client.get(url + "?limit=1001").status_code == 422


def test_listing_does_not_register_or_hide_siblings(platform, monkeypatch):
    client, project, item, _, _ = platform
    root = client.app.state.services.project(project)
    folder = root / "tasks" / item["id"] / "data/post/demo"
    folder.mkdir(parents=True)
    good = folder / "good.json"
    good.write_text("{}")
    bad = folder / "bad.json"
    bad.write_text("{}")
    monkeypatch.setattr(
        task,
        "list_post_result_files",
        lambda *_args, **_kwargs: {
            "files": [
                {
                    "id": "bad",
                    "name": "bad.json",
                    "tree_path": "bad.json",
                    "path": str(bad),
                },
                {"id": "good", "name": "good.json", "tree_path": "good.json", "path": str(good)},
            ],
            "errors": [],
            "total": 2,
        },
    )
    value = client.get(
        f"/api/v1/projects/{project}/tasks/{item['id']}/post/results", params={"view": "files"}
    ).json()
    assert [f["id"] for f in value["files"]] == ["bad", "good"]
    assert all("ref" not in f for f in value["files"])
