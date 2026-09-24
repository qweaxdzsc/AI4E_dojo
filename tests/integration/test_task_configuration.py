"""新公开配置操作保持未知段，拒绝并发旧修订且不增加版本。"""

from pathlib import Path

import ai4e_task as task
import pytest
from ai4e_server.modules.capabilities import official_scripts as catalog_scripts

from tests.integration.test_task_management import recipe
from tests.integration.test_web_project_task import platform as _platform

platform = _platform


def test_configuration_and_explicit_scripts_rollback_together(tmp_path, monkeypatch):
    """源码替换失败时配置、先替换脚本与任务记录一同恢复。"""
    import hashlib

    from ai4e_task.storage import script_replacement

    project = tmp_path / "p"
    task.create_project(project)
    item = task.new_task(project, "atomic", source=recipe(tmp_path))
    folder = Path(task.get_task(project, item["id"])["directory"]) / "recipe"
    (folder / "stage.py").write_text("VALUE = 1\n")
    originals = {name: (folder / name).read_bytes() for name in ("pipeline.py", "stage.py")}
    replacement = tmp_path / "replacement.py"
    replacement.write_text("VALUE = 2\n")
    planned = {name: {"source": str(replacement), "revision": hashlib.sha256(data).hexdigest()}
               for name, data in originals.items()}
    before = task.read_configuration(project, item["id"])
    original_replace = script_replacement._replace_bytes
    calls = 0

    def failing(path, payload):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected script replacement failure")
        original_replace(path, payload)

    monkeypatch.setattr(script_replacement, "_replace_bytes", failing)
    with pytest.raises(OSError, match="injected"):
        task.replace_configuration(project, item["id"], {**before["config"], "score": 9},
                                   revision=before["revision"], script_replacements=planned)
    assert task.read_configuration(project, item["id"]) == before
    for name, data in originals.items():
        assert (folder / name).read_bytes() == data
    assert task.get_task(project, item["id"])["version_id"] == item["version_id"]


def test_preserve_configuration_and_task_record(tmp_path):
    p = tmp_path / "p"
    task.create_project(p)
    t = task.new_task(p, "name", source=recipe(tmp_path))
    cfg = task.read_configuration(p, t["id"])
    saved = task.save_configuration(p, t["id"], {"score": 9}, revision=cfg["revision"])
    assert saved["config"]["inputs"] == cfg["config"]["inputs"]
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
    saved = task.save_configuration(
        p, t["id"], {"dataset": {}}, revision=saved["revision"], replace_sections=("dataset",)
    )
    assert saved["config"]["dataset"] == {}
    with pytest.raises(ValueError, match="unsupported_configuration_replacement"):
        task.save_configuration(
            p, t["id"], {}, revision=saved["revision"], replace_sections=("missing",)
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

    assert (
        inspection_failure_message("Traceback\nKeyError: 'dataset'\n")
        == "检查缺少必要字段 'dataset'"
    )
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

    c, p, _t, _, _ = platform
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
    first = c.post(url + "/model-presets", json={"expected_revision": revision, "name": "同名预设"})
    assert first.status_code == 200, first.text
    before = c.get(f"/api/v1/projects/{p}/tasks/{created['id']}/model-options").json()["presets"]
    duplicate = c.post(
        url + "/model-presets", json={"expected_revision": revision, "name": "同名预设"}
    )
    assert duplicate.status_code == 400 and "model_preset_name_taken" in duplicate.text
    stale = c.post(url + "/model-presets", json={"expected_revision": "stale", "name": "另一份"})
    assert stale.status_code == 409
    c.patch(url, json={"archived": True})
    archived = c.post(
        url + "/model-presets", json={"expected_revision": revision, "name": "归档后"}
    )
    assert archived.status_code == 400 and "task_archived" in archived.text
    after = c.get(f"/api/v1/projects/{p}/tasks/{t['id']}/model-options").json()["presets"]
    assert {item["name"] for item in after} == {item["name"] for item in before}


def test_migrate_official_aero_scripts_replaces_old_wrapper_only(tmp_path):
    """只替换可识别的旧官方包装，用户加过函数的脚本保持不动。"""
    from pathlib import Path

    official = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
    p = tmp_path / "p"
    task.create_project(p)
    created = task.new_task(p, "official", source=official)
    recipe = Path(task.get_task(p, created["id"])["directory"]) / "recipe"
    old = (
        Path(__file__).resolve().parents[2]
        / ".context/mvp/recipe-task-conventions-results/original-examples/"
        / "aero_cfd/shapenet_car_abupt/train.py"
    )
    recipe.joinpath("train.py").write_text(old.read_text())
    rewritten = (
        "from ai4e_core.applications.aero_cfd.trainprep import physical as prep\n"
        "def trainprep(cfg, dataset=None):\n    return prep\n"
        "def extra_hook():\n    return 1\n"
    )
    recipe.joinpath("trainprep.py").write_text(rewritten)
    import hashlib

    with pytest.raises(ValueError, match="verified_sources_required"):
        catalog_scripts.migrate_official_aero_scripts(p, created["id"], official)
    result = catalog_scripts.migrate_official_aero_scripts(
        p,
        created["id"],
        official,
        expected_sources={"train.py": hashlib.sha256(old.read_bytes()).hexdigest()},
    )
    assert (Path(result["backup"]) / "original/train.py").read_bytes() == old.read_bytes()
    assert result["replaced"] == ["train.py"]
    assert (
        "from ai4e_core.applications.aero_cfd.train import fitting"
        in recipe.joinpath("train.py").read_text()
    )
    assert recipe.joinpath("trainprep.py").read_text() == rewritten


def test_verified_old_sources_skip_current_and_match_originals(tmp_path):
    """现行模板没有核验摘要；只有原包装正文才进入替换名单。"""
    official = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
    assert catalog_scripts.verified_old_sources(official) == {}
    folder = tmp_path / "recipe"
    folder.mkdir()
    old = (
        Path(__file__).resolve().parents[2]
        / ".context/mvp/recipe-task-conventions-results/original-examples/"
        / "aero_cfd/shapenet_car_abupt/train.py"
    )
    (folder / "train.py").write_text(old.read_text())
    (folder / "trainprep.py").write_text("def extra():\n    return 1\n")
    assert list(catalog_scripts.verified_old_sources(folder)) == ["train.py"]


def test_save_configuration_refreshes_live_entry(tmp_path):
    """保存后任务入口跟随 config.yaml 的公共 inputs，不保留创建时旧键。"""
    p = tmp_path / "p"
    task.create_project(p)
    created = task.new_task(p, "entry", source=recipe(tmp_path))
    record = task.get_task(p, created["id"])
    record["entry"] = {
        **record.get("entry", {}),
        "inputs": {"dataset.root": "dataset", "train.manifest": "dataset"},
    }
    record["assets"] = {
        "train.manifest": {"id": "legacy", "consumer_binding": "train.manifest"},
    }
    from ai4e_task.storage.database import transaction
    from ai4e_task.storage.records import put

    with transaction(p) as db:
        put(db, "task", record, replace=True)
    current = task.read_configuration(p, created["id"])
    task.save_configuration(p, created["id"], {}, revision=current["revision"])
    live = task.recipe_entry(p, created["id"])
    stored = task.get_task(p, created["id"])
    assert stored["entry"]["inputs"] == live["inputs"]
    assert "dataset.root" not in stored["entry"]["inputs"]
    assert "train.manifest" not in stored.get("assets", {})


def test_complete_configuration_does_not_merge_or_migrate(tmp_path):
    """完整保存不恢复删除字段，且不把采样规则放入任务层。"""
    p = tmp_path / "complete"
    task.create_project(p)
    t = task.new_task(p, "complete", source=recipe(tmp_path))
    before = task.read_configuration(p, t["id"])
    config = {**before["config"], "model": {"sampling": {}}, "trainprep": {"sampling": {"seed": 2}}}
    config.pop("score", None)
    saved = task.replace_configuration(p, t["id"], config, revision=before["revision"])
    assert saved["config"] == config
    assert task.read_configuration(p, t["id"])["config"] == config
    assert len(task.get_lineage(p)) == 1
    with pytest.raises(ValueError, match="conflict"):
        task.replace_configuration(p, t["id"], {}, revision=before["revision"])
    assert task.read_configuration(p, t["id"]) == saved


def test_official_migration_failure_restores_all_replaced_files(tmp_path, monkeypatch):
    """第二个阶段写入失败也不能留下混合新旧流程。"""
    import hashlib
    import json

    from ai4e_task.storage import script_replacement as official_scripts

    official = Path(__file__).resolve().parents[2] / "examples/aero_cfd/nasa_crm_transolver3"
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "migration", source=official)
    folder = Path(task.get_task(project, item["id"])["directory"])
    names = ["train.py", "infer.py"]
    originals = {name: (folder / "recipe" / name).read_bytes() for name in names}
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    for name in names:
        (candidate / name).write_bytes(originals[name] + b"\n# candidate\n")
    record = (folder / "task.json").read_bytes()
    replace = official_scripts._replace_bytes
    failed = False

    def fail_once(path, payload):
        nonlocal failed
        if path.name == "infer.py" and not failed:
            failed = True
            raise OSError("injected write failure")
        return replace(path, payload)

    monkeypatch.setattr(official_scripts, "_replace_bytes", fail_once)
    with pytest.raises(OSError, match="injected"):
        catalog_scripts.migrate_official_aero_scripts(
            project,
            item["id"],
            candidate,
            expected_sources={
                name: hashlib.sha256(raw).hexdigest() for name, raw in originals.items()
            },
        )
    assert {name: (folder / "recipe" / name).read_bytes() for name in names} == originals
    assert (folder / "task.json").read_bytes() == record
    receipt = next((folder / ".dojo/script-migrations").glob("*/receipt.json"))
    assert json.loads(receipt.read_text())["status"] == "rolled_back"


@pytest.mark.parametrize(
    "case_name", ["nasa_crm_transolver3", "shapenet_car_transolver3_volume", "nasa_crm_abupt"]
)
def test_platform_migration_selects_matching_case(tmp_path, case_name):
    """平台选择领域正文，不把官方旧包装统一换成 AB-UPT 专用流程。"""
    from types import SimpleNamespace

    from ai4e_server.modules.stages.application import _migrate_official_scripts

    root = Path(__file__).resolve().parents[2]
    source = root / "examples/aero_cfd" / case_name
    original = (
        root / ".context/mvp/recipe-task-conventions-results/original-examples/aero_cfd" / case_name
    )
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "migration", source=source)
    folder = Path(task.get_task(project, item["id"])["directory"]) / "recipe"
    for name in ("train.py", "trainprep.py", "infer.py", "post.py"):
        (folder / name).write_bytes((original / name).read_bytes())
    expected = catalog_scripts.verified_old_sources(folder)
    assert expected
    before = task.read_configuration(project, item["id"])
    service = SimpleNamespace(settings=SimpleNamespace(template=root / "recipes/aero_cfd"))
    _migrate_official_scripts(service, project, item["id"])
    for name in expected:
        assert (folder / name).read_bytes() == (source / name).read_bytes()
    assert task.read_configuration(project, item["id"]) == before
    assert len(task.get_lineage(project)) == 1
