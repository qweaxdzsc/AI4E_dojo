"""本地 RMHD recipe 配置；公开加载器与用户组件导入，不依赖领域私有配置。"""

from importlib import import_module

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import load_recipe_config


def component(name):
    """按全限定路径加载用户提供的普通函数或类。"""
    module, symbol = name.rsplit(".", 1)
    return getattr(import_module(module), symbol)


def validate(cfg):
    """本实验只接受冻结六场网格与正的训练预算。"""
    if OmegaConf.is_config(cfg):
        cfg = OmegaConf.to_container(cfg, resolve=True)
    if cfg["science"]["fields"] != ["Psi", "u", "zj", "omega", "rho", "T"]:
        raise ValueError("六场顺序改变")
    if cfg["science"]["history"] != 10 or cfg["science"]["future"] != 40:
        raise ValueError("历史或预测帧数改变")
    if cfg["train"]["updates"] < 1 or cfg["train"]["batch_size"] < 1:
        raise ValueError("训练预算非法")
    return cfg


def load_configuration(path, overrides=None):
    """展开点号覆盖；路径相对配置文件解释。"""
    cfg = load_recipe_config(path, overrides)
    return validate(cfg)
