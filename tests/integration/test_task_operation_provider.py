"""平台操作通过任务连接普通函数，不要求组件实现统一模型协议。"""

import json

import ai4e_task as task
import pytest
from omegaconf import OmegaConf

from tests.integration.test_task_management import recipe


def _write_entry(folder, **fields):
    (folder / "task-entry.json").write_text(json.dumps(fields))


def test_application_component_resolves_inspect(tmp_path):
    """现行配置声明领域模块后，检查入口按模块名拼接。"""
    source = recipe(tmp_path)
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.components = {"application": "user_adapter"}
    OmegaConf.save(cfg, source / "config.yaml")
    (source / "user_adapter.py").write_text(
        "def inspect(request):\n"
        '    return {"user_value": request["config"]["score"] * 3, '
        '"operation": request["operation"]}\n'
    )
    assert task.operation_target(source, "inspect") == "user_adapter.inspect"


def test_user_operation_runs_without_model_or_template_registration(tmp_path):
    """外部模块使用自己的配置和返回值；检查 worker 不导入固定领域。"""
    source = recipe(tmp_path)
    cfg = OmegaConf.load(source / "config.yaml")
    cfg.components = {"application": "user_adapter"}
    OmegaConf.save(cfg, source / "config.yaml")
    (source / "user_adapter.py").write_text(
        "def inspect(request):\n"
        '    return {"user_value": request["config"]["score"] * 3, '
        '"operation": request["operation"]}\n'
    )
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "free", source=source)
    captured = task.read_configuration(project, item["id"])
    result = task.inspect_task(
        project,
        item["id"],
        "user_check",
        revision=captured["revision"],
        output_dir=str(tmp_path / "inspection"),
    )
    assert result == {"user_value": 6, "operation": "user_check"}


def test_missing_optional_operation_does_not_prevent_normal_run(tmp_path):
    """未接平台检查的普通案例仍能执行，只有检查操作明确不可用。"""
    source = recipe(tmp_path)
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "free", source=source)
    captured = task.read_configuration(project, item["id"])
    with pytest.raises(ValueError, match="operation_unavailable"):
        task.inspect_task(
            project,
            item["id"],
            "inspect",
            revision=captured["revision"],
            output_dir=str(tmp_path / "inspection"),
        )
    submitted = task.submit_run(project, item["id"])
    assert task.wait_run(project, submitted["id"])["status"] == "succeeded"


def test_explicit_empty_operations_do_not_restore_creation_defaults(tmp_path):
    """显式取消平台接入后，创建快照不能悄悄把操作重新启用。"""
    source = recipe(tmp_path)
    _write_entry(source, operations={"inspect": {"target": "user_adapter.inspect"}})
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "free", source=source)
    copied = project / "tasks" / item["id"] / "recipe"
    _write_entry(copied, operations={})
    with pytest.raises(ValueError, match="operation_unavailable"):
        task.operation_target(copied, "inspect")


def test_missing_current_operations_do_not_reuse_creation_snapshot(tmp_path):
    """历史任务描述与创建快照都不能暗中恢复已移除的连接。"""
    source = recipe(tmp_path)
    _write_entry(source, operations={"inspect": {"target": "user_adapter.inspect"}})
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "free", source=source)
    copied = project / "tasks" / item["id"] / "recipe"
    (copied / "task-entry.json").unlink()
    with pytest.raises(ValueError, match="operation_unavailable"):
        task.operation_target(copied, "inspect")


def test_unknown_model_is_not_described_as_official_abupt():
    """用户组件不因结构相似被服务默认为另一模型；普通运行不受此目录限制。"""
    from ai4e_server.modules.capabilities.model_cases import model_id

    with pytest.raises(ValueError, match="unsupported_model_binding"):
        model_id({"components": {"model": "research.own_model"}})


@pytest.mark.parametrize("operations", [None, [], "inspect"])
def test_invalid_operation_declaration_has_explicit_error(tmp_path, operations):
    """错误声明在加载用户代码前定位，不能以 AttributeError 泄漏内部实现。"""
    source = recipe(tmp_path)
    _write_entry(source, operations=operations)
    with pytest.raises(ValueError, match="operation_unavailable"):
        task.operation_target(source, "inspect")
