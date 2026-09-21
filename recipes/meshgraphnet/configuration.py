"""MeshGraphNet 可复制 Recipe 的配置加载和校验。"""

from __future__ import annotations

from pathlib import Path

import yaml
from omegaconf import OmegaConf

from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.configuration import resolve


def load_configuration(path: str | Path, overrides=None) -> dict:
    """读取 YAML、应用点号覆盖并交给贡献应用补全默认值。"""
    path = Path(path).resolve()
    config = yaml.safe_load(path.read_text()) or {}
    config = OmegaConf.to_container(
        OmegaConf.merge(config, OmegaConf.from_dotlist(overrides or [])), resolve=True
    )
    config["_config_path"] = str(path)
    return resolve(config)


def validate(config: dict) -> dict:
    """校验一份已加载或程序传入的 Recipe 配置。"""
    return resolve(config)
