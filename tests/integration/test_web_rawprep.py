"""页面不能静默提交超出现有 recipe 的配置。"""

from copy import deepcopy
from tests.integration.test_web_project_task import platform


def test_invalid_mapping_and_manual_count(platform):
    c, p, t, root, _ = platform
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/rawprep"
    original = c.get(url).json()
    mutations = [
        ("fields", {"surface": {"renamed": {"components": 1}}}),
        ("save_fields", ["custom_bundle"]),
        ("geometry", []),
        ("vtkhdf", "yes"),
    ]
    for key, value in mutations:
        cfg = deepcopy(original)
        cfg["rawprep"][key] = value
        rejected = c.put(url, json=cfg)
        assert rejected.status_code == 400 and "rawprep." in rejected.text
        assert c.get(url).json() == original
    selection = {
        "revision": original["revision"],
        "root": "data0",
        "files": [],
        "all_selected": False,
        "count": 1,
    }
    assert c.post(url + "/execute", json=selection).status_code == 400
    assert c.get(f"/api/v1/projects/{p}/runs").json() == []
