"""显式真实安装证据验收，不把不存在的证据计为通过。"""

import json
import os
from pathlib import Path

import pytest


def test_real_installed_direct_task_and_extension():
    path = os.environ.get("DOJO_PCNO_CYLINDER_INSTALLATION")
    if path is None:
        pytest.skip("需显式提供真实wheel运行报告")
    report = json.loads(Path(path).read_text())
    assert report["passed"] and report["max_weight_difference"] == 0
    assert report["extension_updates"] == 8 and report["derived_windows"] > 0
    assert report["task"]["status"] == "succeeded"
    assert all("site-packages" in v and "/packages/" not in v for v in report["installed"].values())
