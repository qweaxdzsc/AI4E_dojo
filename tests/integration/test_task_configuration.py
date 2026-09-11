"""新公开配置操作保持未知段，拒绝并发旧修订且不增加版本。"""

import ai4e_task as task
import pytest
from tests.integration.test_task_management import recipe


def test_preserve_configuration_and_task_record(tmp_path):
    p = tmp_path / "p"
    task.create_project(p)
    t = task.new_task(p, "name", source=recipe(tmp_path))
    cfg = task.read_configuration(p, t["id"])
    saved = task.save_configuration(p, t["id"], {"score": 9}, revision=cfg["revision"])
    assert saved["config"]["dataset"] == cfg["config"]["dataset"]
    with pytest.raises(ValueError, match="conflict"):
        task.save_configuration(p, t["id"], {"score": 10}, revision=cfg["revision"])
    assert len(task.get_lineage(p)) == 1
    assert task.get_task(p, t["id"])["updated_at"] >= t["created_at"]
    task.update_task(p, t["id"], archived=True, name="archived")
    with pytest.raises(ValueError, match="archived"):
        task.save_configuration(p, t["id"], {}, revision=saved["revision"])
    assert task.get_task(p, t["id"])["name"] == "archived"
    task.update_task(p, t["id"], archived=False)
