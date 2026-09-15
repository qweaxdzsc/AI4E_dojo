"""评价协议、私有上下文隔离和请求校验。"""

import ai4e_task as task

from tests.integration.test_web_project_task import (
    platform as platform,  # noqa: PLC0414 - pytest跨模块夹具
)


def test_job_protocol_hides_paths(platform, monkeypatch):
    c, p, t, _, _ = platform
    monkeypatch.setattr(
        task,
        "submit_post_metrics",
        lambda *_: {
            "id": "j",
            "run_dir": "/secret/run",
            "data_dir": "/secret/data",
            "inputs": [{"manifest": "/secret"}],
            "pid": 1,
            "rows": [{"id": "row", "values": {"mse": 1}}],
            "status": "succeeded",
        },
    )
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/post/metric-jobs"
    body = {
        "results": [{"id": "r", "revision": "v"}],
        "fields": ["f"],
        "metrics": ["mse"],
        "idempotency_key": "once",
    }
    response = c.post(url, json=body)
    assert response.status_code == 200, response.text
    assert "/secret" not in response.text and "pid" not in response.json()
    assert response.json()["row_count"] == 1
    assert c.post(url, json={**body, "path": "/tmp/out"}).status_code == 422
    assert c.post(url, json={**body, "fields": []}).status_code == 422
