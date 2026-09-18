"""可复制 GenCP 模板的显式配置连接。"""

from omegaconf import OmegaConf


def plain(cfg):
    """把运行器的配置视图转为普通参数，不解释算法。"""
    return OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else cfg


from ai4e_contrib.application.coupled_physics.gencp.configuration import (
    component,
    load_configuration,
)

__all__ = ["component", "load_configuration", "plain"]
