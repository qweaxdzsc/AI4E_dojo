"""平台依赖已连接的操作，用户脚本无需匹配官方代码结构。"""

import hashlib
import json
from pathlib import Path

import pytest

from tests.integration.test_web_project_task import platform as _platform

platform = _platform
LEGACY = Path(__file__).resolve().parents[1] / "fixtures/rawprep_legacy/configuration.py"


def digest_tree(root):
    """跳过解释器缓存，仅核对案例交付文件。"""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def save_body(value):
    """保存请求不含读取回传的名称状态。"""
    body = dict(value)
    body.pop("processed_name_status", None)
    return body


@pytest.mark.parametrize("change", ["additional", "implementation", "format"])
def test_user_recipe_changes_do_not_disable_platform(platform, change):
    """新增能力与修改步骤不由模板 AST 决定可用性；原有描述操作仍可调用。"""
    client, project, item, _, _ = platform
    folder = client.app.state.services.project(project) / "tasks" / item["id"] / "recipe"
    if change == "additional":
        (folder / "user_component.py").write_text("def scale(x): return x * 2\n")
    else:
        target = folder / "rawprep.py"
        target.write_text(
            target.read_text()
            + ("\nUSER_EXTENSION = True\n" if change == "implementation" else "\n# 用户注释\n")
        )
    before = {p.name: p.read_bytes() for p in folder.glob("*.py")}
    url = f"/api/v1/projects/{project}/tasks/{item['id']}/rawprep"
    value = client.get(url).json()
    value["processed_name"] = "custom_recipe"
    saved = client.put(url, json=save_body(value))
    assert saved.status_code == 200, saved.text
    assert {p.name: p.read_bytes() for p in folder.glob("*.py")} == before


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


def test_legacy_loader_requires_explicit_migration_without_rewriting_task(platform):
    """旧加载器不再由Task隐式适配；真实提交保留失败及原件。"""
    import ai4e_task as task
    import torch

    from ai4e_core.applications.aero_cfd.rawprep.catalog import sample_key
    from tests.integration.test_web_rawprep_handoff import SAMPLE, copy_real

    client, project, item, root, _ = platform
    copy_real(root)
    base = client.app.state.services.project(project)
    folder = base / "tasks" / item["id"] / "recipe"
    url = f"/api/v1/projects/{project}/tasks/{item['id']}"
    binding = client.get(url + "/dataset").json()
    assert "revision" in binding, binding
    bound = client.put(
        url + "/dataset",
        json={
            "expected_revision": binding["revision"],
            "sources": {"root": {"root": "data0", "path": ""}},
        },
    )
    assert bound.status_code == 200, bound.text
    (folder / "configuration.py").write_bytes(LEGACY.read_bytes())
    captured = task.read_configuration(base, item["id"])
    task.save_configuration(
        base,
        item["id"],
        {"rawprep": {}},
        revision=captured["revision"],
        replace_sections=("rawprep",),
    )
    shown = client.get(url + "/rawprep")
    assert shown.status_code == 200, shown.text
    config = shown.json()
    config["processed_name"] = "legacy_real"
    config["rawprep"]["workers"] = 10
    saved = client.put(url + "/rawprep", json=save_body(config))
    assert saved.status_code == 200, saved.text
    before = digest_tree(folder)
    selection = {
        "revision": saved.json()["revision"],
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
    assert run["status"] == "failed", run
    assert run["error"]  # 加载器在core会话之前失败，错误在worker收据中。
    assert task.run_physical_manifest(base, run) is None
    assert digest_tree(folder) == before


def test_official_cases_declare_visible_field_scale():
    import yaml

    root = Path(__file__).resolve().parents[2] / "examples/aero_cfd"
    abupt = yaml.safe_load((root / "shapenet_car_abupt/config.yaml").read_text())
    assert abupt["trainprep"]["normalization"]["fields"]["surface_position"]["scale"] == 1000
    nasa = yaml.safe_load((root / "nasa_crm_abupt/config.yaml").read_text())
    assert nasa["trainprep"]["normalization"]["fields"]["surface_position"]["scale"] == 1000
    transolver = yaml.safe_load((root / "shapenet_car_transolver3_surface/config.yaml").read_text())
    assert transolver["trainprep"]["normalization"]["fields"]["surface_position"]["scale"] == 1
