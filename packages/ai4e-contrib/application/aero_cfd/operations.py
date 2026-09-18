"""可选领域操作公开模块；普通 recipe 执行不依赖平台操作。"""

from ai4e_core.applications.aero_cfd.post import export_evaluation as export
from ai4e_core.applications.aero_cfd.post import run_evaluation as evaluate

__all__ = ["evaluate", "export", "infer", "inspect"]


def inspect(request: dict) -> dict:
    """在领域边界转换公共配置；旧配置由离线工具显式迁移。"""
    from copy import deepcopy

    from ai4e_core.applications.aero_cfd.inspection import execute
    from ai4e_core.base.config.conventions import normalize_recipe_config

    from .inputs import bind_inputs, public_inputs

    value = deepcopy(request)
    config = value.get("config")
    if config:
        bound = bind_inputs(
            normalize_recipe_config(config, base=value.get("config_dir", "."))
        )
        value["config"] = bound
    result = execute(value)
    if isinstance(result.get("configuration"), dict):
        result["configuration"] = public_inputs(result["configuration"])
    return result


def infer(request: dict) -> dict:
    """推理检查消费同一公共配置连接，Task不解读模型输入树。"""
    from copy import deepcopy

    from ai4e_core.applications.aero_cfd.infer import inspect_artifacts
    from ai4e_core.base.config.conventions import normalize_recipe_config

    from .inputs import bind_inputs

    value = deepcopy(request)
    arguments = value.get("arguments", {})
    if "config" in arguments:
        arguments["config"] = bind_inputs(normalize_recipe_config(
            arguments["config"], base=arguments.get("config_dir", ".")
        ))
    return inspect_artifacts(value)
