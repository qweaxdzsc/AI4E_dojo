"""新公开配置操作保持未知段，拒绝并发旧修订且不增加版本。"""

import ai4e_task as task
import pytest

from tests.integration.test_task_management import recipe
from tests.integration.test_web_project_task import platform as _platform

platform = _platform


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


def test_replace_model_sections_removes_incompatible_old_tree(tmp_path):
    """显式替换先移除旧树；普通保存仍保留用户扩展与未编辑段。"""
    p = tmp_path / "p"
    task.create_project(p)
    t = task.new_task(p, "replace", source=recipe(tmp_path))
    first = task.read_configuration(p, t["id"])
    old = task.save_configuration(
        p,
        t["id"],
        {
            "model": {"parameters": [1, 2], "old_model_key": True},
            "train": {"old_optimizer_key": 1},
            "trainprep": {"old_role": 1},
            "user_extension": {"keep": True},
        },
        revision=first["revision"],
    )
    patch = {
        "model": {"parameters": {"n_hidden": 64}},
        "train": {"optimizer": "adamw"},
        "trainprep": {"domains": {}},
    }
    saved = task.save_configuration(
        p,
        t["id"],
        patch,
        revision=old["revision"],
        replace_sections=("model", "train", "trainprep"),
    )
    for key, value in patch.items():
        assert saved["config"][key] == value
    assert saved["config"]["user_extension"] == {"keep": True}
    with pytest.raises(ValueError, match="unsupported_configuration_replacement"):
        task.save_configuration(
            p, t["id"], {"dataset": {}}, revision=saved["revision"], replace_sections=("dataset",)
        )
    with pytest.raises(ValueError, match="conflict"):
        task.save_configuration(
            p, t["id"], patch, revision=old["revision"], replace_sections=("model",)
        )
    assert task.read_configuration(p, t["id"]) == saved
    assert len(task.get_lineage(p)) == 1


def test_inspection_failure_keeps_keyerror_field_name():
    """检查子进程 KeyError 保留字段名，页面不再只看到单独的 'dataset'。"""
    from ai4e_task.tasks.inspections import inspection_failure_message

    assert inspection_failure_message("Traceback\nKeyError: 'dataset'\n") == "检查缺少必要字段 'dataset'"
    assert inspection_failure_message("ValueError: train.manifest: 需要已有物理数据清单") == (
        "train.manifest: 需要已有物理数据清单"
    )


def test_candidate_configuration_cannot_execute(tmp_path):
    """候选描述入口不允许借用检查接口执行未保存配置。"""
    p = tmp_path / "p"
    task.create_project(p)
    t = task.new_task(p, "candidate", source=recipe(tmp_path))
    captured = task.read_configuration(p, t["id"])
    with pytest.raises(ValueError, match="candidate_configuration_requires_description"):
        task.inspect_task(
            p,
            t["id"],
            "trace_model",
            revision=captured["revision"],
            output_dir=str(tmp_path / "inspection"),
            configuration={},
        )
    assert task.read_configuration(p, t["id"]) == captured


def test_export_model_preset_is_reusable_on_same_dataset(platform):
    """导出后同数据集另一任务可选用，不含权重路径。"""
    from copy import deepcopy

    c, p, t, _, _ = platform
    source = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "export-source", "case_id": "shapenet_car_abupt"},
    ).json()
    url = f"/api/v1/projects/{p}/tasks/{source['id']}"
    cfg = c.get(url + "/configuration?stage=model").json()
    values = deepcopy(cfg["values"])
    values["parameters"]["dim"] = 88
    saved = c.put(
        url + "/configuration",
        json={"stage": "model", "expected_revision": cfg["revision"], "values": values},
    )
    assert saved.status_code == 200, saved.text
    exported = c.post(
        url + "/model-presets",
        json={"expected_revision": saved.json()["revision"], "name": "我的汽车表面"},
    )
    assert exported.status_code == 200, exported.text
    other = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "export-target", "case_id": "shapenet_car_abupt"},
    ).json()
    other_url = f"/api/v1/projects/{p}/tasks/{other['id']}"
    options = c.get(other_url + "/model-options").json()
    preset = next(item for item in options["presets"] if item["name"] == "我的汽车表面")
    applied = c.put(
        other_url + "/configuration",
        json={
            "stage": "model",
            "expected_revision": options["revision"],
            "target_preset": preset["id"],
            "values": deepcopy(preset["model"]),
        },
    )
    assert applied.status_code == 200, applied.text
    actual = applied.json()["config"]
    assert actual["model"]["parameters"]["dim"] == 88
    assert actual["train"].get("resume") in {None, ""}
    assert "preparation" not in actual["train"] or actual["train"]["preparation"] in {None, ""}
    assert not any(
        isinstance(actual["train"].get(key), str) and actual["train"][key].endswith(".pt")
        for key in actual["train"]
    )


def test_export_model_preset_rejects_empty_duplicate_and_stale(platform):
    """空名、重名和修订冲突都不落盘。"""
    c, p, t, _, _ = platform
    created = c.post(
        f"/api/v1/projects/{p}/tasks",
        json={"name": "export-reject", "case_id": "shapenet_car_abupt"},
    ).json()
    url = f"/api/v1/projects/{p}/tasks/{created['id']}"
    revision = c.get(url + "/configuration").json()["revision"]
    empty = c.post(url + "/model-presets", json={"expected_revision": revision, "name": "  "})
    assert empty.status_code == 400 and "model_preset_name_required" in empty.text
    reserved = c.post(url + "/model-presets", json={"expected_revision": revision, "name": "abupt"})
    assert reserved.status_code == 400 and "model_preset_name_reserved" in reserved.text
    first = c.post(
        url + "/model-presets", json={"expected_revision": revision, "name": "同名预设"}
    )
    assert first.status_code == 200, first.text
    before = c.get(f"/api/v1/projects/{p}/tasks/{created['id']}/model-options").json()["presets"]
    duplicate = c.post(
        url + "/model-presets", json={"expected_revision": revision, "name": "同名预设"}
    )
    assert duplicate.status_code == 400 and "model_preset_name_taken" in duplicate.text
    stale = c.post(
        url + "/model-presets", json={"expected_revision": "stale", "name": "另一份"}
    )
    assert stale.status_code == 409
    c.patch(url, json={"archived": True})
    archived = c.post(
        url + "/model-presets", json={"expected_revision": revision, "name": "归档后"}
    )
    assert archived.status_code == 400 and "task_archived" in archived.text
    after = c.get(
        f"/api/v1/projects/{p}/tasks/{t['id']}/model-options"
    ).json()["presets"]
    assert {item["name"] for item in after} == {item["name"] for item in before}
