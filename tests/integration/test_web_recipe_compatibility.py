"""页面配置只改变任务副本，原模板及未涉及阶段保持不变。"""

import hashlib
from pathlib import Path

import pytest

from tests.integration.test_web_project_task import RECIPE
from tests.integration.test_web_project_task import platform as _platform

platform = _platform


def digest_tree(root):
    """跳过解释器缓存，仅核对案例交付文件。"""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def test_template_unchanged_and_custom_script_refused(platform):
    c, p, t, _, _ = platform
    before = digest_tree(RECIPE)
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/rawprep"
    cfg = c.get(url).json()
    cfg["processed_name"] = "compatibility_test"
    cfg["rawprep"]["vtkhdf"] = True
    saved = c.put(url, json=cfg)
    assert saved.status_code == 200, saved.text
    assert digest_tree(RECIPE) == before
    base = c.app.state.services.project(p)
    script = base / "tasks" / t["id"] / "recipe/rawprep.py"
    script.write_text(script.read_text() + "\n# user customization\n")
    assert c.put(url, json=saved.json()).status_code == 200
    script.write_text(script.read_text().replace("data = pre.validate_fields(data)", "data = data"))
    rejected = c.put(url, json=saved.json())
    assert rejected.status_code == 400 and "recipe_profile_changed" in rejected.text
    assert "rawprep.py" in rejected.text
    assert digest_tree(RECIPE) == before


LEGACY = Path(__file__).resolve().parents[1] / "fixtures/rawprep_legacy/configuration.py"


@pytest.mark.parametrize("case", [None, "shapenet_car_abupt", "nasa_crm_abupt"])
def test_old_loader_and_formatting_still_save(platform, case):
    """已知旧配置入口不因默认加载新增或格式变化被阻断，用户任务原文保留。"""
    client, project, item, _, _ = platform
    if case:
        response = client.post(
            f"/api/v1/projects/{project}/tasks", json={"name": case, "case_id": case}
        )
        assert response.status_code == 200, response.text
        item = response.json()
    base = client.app.state.services.project(project)
    script = base / "tasks" / item["id"] / "recipe/configuration.py"
    script.write_bytes(LEGACY.read_bytes())
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/rawprep"
    value = client.get(url).json()
    value["processed_name"] = "compatibility_test"
    saved = client.put(url, json=value)
    assert saved.status_code == 200, saved.text
    assert script.read_bytes() == LEGACY.read_bytes()


@pytest.mark.parametrize("change", ["logic", "syntax", "entry", "missing", "additional"])
def test_unknown_profile_change_rejected(platform, change):
    client, project, item, _, _ = platform
    folder = client.app.state.services.project(project) / "tasks" / item["id"] / "recipe"
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/rawprep"
    value = client.get(url).json()
    if change in {"logic", "syntax"}:
        (folder / "configuration.py").write_text(
            LEGACY.read_text() + ("\nx = 1\n" if change == "logic" else "\nif (\n")
        )
    elif change == "entry":
        import json

        entry = json.loads((folder / "task-entry.json").read_text())
        entry["script"] = "rawprep.py"
        (folder / "task-entry.json").write_text(json.dumps(entry))
    elif change == "missing":
        (folder / "rawprep.py").unlink()
    else:
        (folder / "extra.py").write_text("raise RuntimeError('extra')\n")
    result = client.put(url, json=value)
    assert result.status_code == 400 and "recipe_profile_changed" in result.text


def test_legacy_loader_real_sample_executes_without_rewriting_task(platform):
    """旧任务直接执行也消费页面默认值，真实物理 PT 可读回。"""
    import json

    import ai4e_task as task
    import torch

    from tests.integration.test_web_rawprep_handoff import copy_real

    client, project, item, root, _ = platform
    copy_real(root)
    base = client.app.state.services.project(project)
    folder = base / "tasks" / item["id"] / "recipe"
    (folder / "configuration.py").write_bytes(LEGACY.read_bytes())
    url = f"/api/v1/projects/{project}/tasks/{item['id']}"
    binding = client.get(url + "/dataset").json()
    bound = client.put(
        url + "/dataset",
        json={
            "expected_revision": binding["revision"],
            "sources": {"root": {"root": "data0", "path": ""}},
        },
    )
    assert bound.status_code == 200, bound.text
    captured = task.read_configuration(base, item["id"])
    task.save_configuration(
        base,
        item["id"],
        {"rawprep": {}},
        revision=captured["revision"],
        replace_sections=("rawprep",),
    )
    before = digest_tree(folder)
    config = client.get(url + "/rawprep").json()
    config["processed_name"] = "legacy_real"
    saved = client.put(url + "/rawprep", json=config)
    assert saved.status_code == 200, saved.text
    config = saved.json()
    before = digest_tree(folder)
    from ai4e_core.applications.aero_cfd.rawprep.catalog import sample_key
    from tests.integration.test_web_rawprep_handoff import SAMPLE

    selection = {
        "revision": config["revision"],
        "sample_scope": {"mode": "samples", "values": [sample_key("train", SAMPLE)]},
        "idempotency_key": "legacy-profile-real",
    }
    catalog = client.post(url + "/rawprep/catalog", json=selection)
    assert catalog.status_code == 200, catalog.text
    response = client.post(
        url + "/rawprep/execute", json={**selection, "catalog_revision": catalog.json()["revision"]}
    )
    assert response.status_code == 200, response.text
    run = task.wait_run(base, response.json()["id"], timeout=120)
    assert run["status"] == "succeeded", task.read_log(base, run["id"])
    manifest = json.loads((Path(run["data_dir"]) / "manifest.json").read_text())
    assert len(manifest["samples"]) == 1
    record = manifest["samples"][0]
    assert len(record["filemap"]) == 7
    tensor = torch.load(
        Path(record["path"]) / record["filemap"]["surface_pressure"], weights_only=True
    )
    assert isinstance(tensor, torch.Tensor) and len(tensor) > 1000
    assert digest_tree(folder) == before


def test_stage_editor_preserves_existing_recipe_extensions(platform):
    """标准工作台局部保存保留未编辑的用户参数与字段列表。"""
    import ai4e_task as task

    client, project, item, _, _ = platform
    base = client.app.state.services.project(project)
    current = task.read_configuration(base, item["id"])
    extension = {
        "inputs": {"velocity": "volume.velocity"},
        "outputs": {
            "speed": {
                "name": "volume_speed",
                "entity_like": "volume.velocity",
                "components": 1,
                "unit_from": "volume.velocity",
                "state": "physical",
            }
        },
    }
    value = task.save_configuration(
        base,
        item["id"],
        {
            "rawprep": {
                "speed": extension,
                "save_fields": current["config"]["rawprep"]["save_fields"] + ["volume_speed"],
            }
        },
        revision=current["revision"],
    )
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/configuration"
    response = client.put(
        url,
        json={
            "expected_revision": value["revision"],
            "stage": "train",
            "values": {"learning_rate": 0.0003},
        },
    )
    assert response.status_code == 200, response.text
    saved = task.read_configuration(base, item["id"])
    response = client.put(
        url,
        json={
            "expected_revision": saved["revision"],
            "stage": "rawprep",
            "values": {"vtkhdf": True},
        },
    )
    assert response.status_code == 200, response.text
    saved = task.read_configuration(base, item["id"])["config"]
    assert saved["rawprep"]["speed"] == extension
    assert "volume_speed" in saved["rawprep"]["save_fields"]
    assert saved["train"]["learning_rate"] == 0.0003
    assert len(task.get_lineage(base)) == 1
