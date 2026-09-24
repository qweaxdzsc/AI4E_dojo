"""已安装wheel外复制与Task真实重放证据核验，运行由统一串行调度器负责。"""

import json
import os
from pathlib import Path

import pytest

from tools.verification.classic_networks.run_installed import CASES


@pytest.mark.parametrize("identity,case,budget", CASES)
def test_installed_recipe_recovery_task_and_relocation(identity, case, budget):
    value = os.environ.get("DOJO_CLASSIC_EVIDENCE")
    if not value:
        pytest.skip("需要真实wheel重放证据；不以跳过声明安装成功")
    root = Path(value)
    summary = json.loads((root / "evidence/installed.json").read_text())[identity]
    assert summary["status"] == "passed"
    report = json.loads(Path(summary["report"]).read_text())
    assert report["status"] == "passed"
    assert report["task"]["finished"]["status"] == "succeeded"
    assert report["runtime"]["pid"] != report["task"]["runtime"]["pid"]
    for runtime in (report["runtime"], report["task"]["runtime"]):
        assert all(Path(p).is_relative_to(root / "installed") for p in runtime["modules"].values())
    assert report["phases"]["direct"]["updates"] == 1
    assert report["phases"]["resumed"]["updates"] == 2
    assert report["phases"]["task"]["updates"] == 1
    assert report["phases"]["independent_post"]["post"] == report["phases"]["resumed"]["post"]
    assert report["relocations"]
    assert report["budget_identity"] == budget
    assert report["phases"]["resumed"]["post"]["case"] == case
    if "network_composition" in identity:
        assert report["phases"]["resumed"]["post"]["derived"]
