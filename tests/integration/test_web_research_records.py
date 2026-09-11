"""真实血缘、工作目录差异和服务报告持久化。"""

from fastapi.testclient import TestClient
from ai4e_server.bootstrap.app import create_app
from tests.integration.test_web_project_task import platform


def test_lineage_compare_report(platform):
    c, p, t, _, settings = platform
    base = f"/api/v1/projects/{p}"
    cfg = c.get(base + f"/tasks/{t['id']}/rawprep").json()
    cfg["rawprep"]["vtkhdf"] = True
    c.put(base + f"/tasks/{t['id']}/rawprep", json=cfg)
    child = c.post(base + f"/tasks/{t['id']}/fork", json={"name": "derived"}).json()
    tree = c.get(base + "/lineage").json()
    assert len(tree) == 2
    assert (
        next(x for x in tree if x["id"] == child["version_id"])["parent_version_id"]
        == t["version_id"]
    )
    for mode, left, right in [
        ("versions", t["version_id"], child["version_id"]),
        ("worktree", t["id"], None),
    ]:
        result = c.post(base + "/compare", json={"mode": mode, "left": left, "right": right})
        assert result.status_code == 200 and result.json()["files"]
    report = {"title": "研究记录", "text": "数据准备已配置", "run_ids": []}
    saved = c.put(base + "/report", json=report)
    assert saved.status_code == 200
    assert c.put(base + "/report", json={**report, "run_ids": ["unknown"]}).status_code == 404
    with TestClient(create_app(settings)) as other:
        assert other.get(base + "/report").json() == saved.json()
