"""加载案例配置。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from omegaconf import OmegaConf


def load_config(
    path: str | Path,
    overrides: Mapping[str, Any] | Sequence[str] | None = None,
) -> dict[str, Any]:
    """读取 YAML 案例配置，可选点号覆盖，返回可还原的展开字典。

    Args:
        path: 配置文件路径。
        overrides: 点号键到值的映射，或 ``key=value`` 字符串列表。

    Returns:
        展开后的配置字典，可供还原为 YAML。

    Raises:
        FileNotFoundError: 配置文件不存在。
        TypeError: 根节点不是映射。
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    loaded = OmegaConf.load(config_path)
    if not OmegaConf.is_dict(loaded):
        raise TypeError(f"配置根节点必须是映射: {config_path}")
    return apply_overrides(loaded, overrides)


def apply_overrides(
    config: Any,
    overrides: Mapping[str, Any] | Sequence[str] | None = None,
) -> dict[str, Any]:
    """把覆盖合并进配置树并展开为普通字典。

    Args:
        config: OmegaConf 节点或映射。
        overrides: 点号键映射或 ``key=value`` 列表。

    Returns:
        展开后的配置字典。
    """
    cfg = OmegaConf.create(config)
    if overrides:
        if isinstance(overrides, Mapping):
            for key, value in overrides.items():
                OmegaConf.update(cfg, str(key), value, merge=True)
        else:
            cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(list(overrides)))
    container = OmegaConf.to_container(cfg, resolve=True)
    if not isinstance(container, dict):
        raise TypeError("配置根节点必须是映射")
    return container
