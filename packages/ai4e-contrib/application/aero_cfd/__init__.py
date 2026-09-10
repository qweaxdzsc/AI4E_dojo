"""案例组件选择；配置提供全限定路径，不承载算法或训练循环。"""

from importlib import import_module
from types import SimpleNamespace

DEFAULTS = {
    "workflow": "ai4e_core.applications.aero_cfd.anchor_workflow",
    "dataset": "ai4e_contrib.application.datasets.shapenet_car",
    "model": "ai4e_contrib.ability.model.abupt.component",
}


def load(cfg):
    """解析组件模块，缺失声明沿用已发布的汽车案例。"""
    values = {**DEFAULTS, **dict(cfg.get("components", {}))}
    return SimpleNamespace(**{key: import_module(value) for key, value in values.items()})


def resolve_config(config, *, validate=True):
    """由选定模型解析自身默认值，不向另一模型注入参数。"""
    return load(config).model.resolve(config, validate=validate)
