"""按传入名单列分片，不扫盘冒充官方顺序。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


def load_split_lists(source: str | Path | Mapping[str, Any]) -> dict[str, list[str]]:
    """从映射或 YAML 取出分片相对路径名单，保持原顺序。

    忽略 ``expected`` 等非名单键。名单值必须是字符串序列。

    Args:
        source: 已展开的映射，或 YAML 路径。

    Returns:
        分片名到相对路径列表。

    Raises:
        TypeError: 根节点或名单不是映射/序列。
        FileNotFoundError: YAML 不存在。
    """
    data = _as_mapping(source)
    splits: dict[str, list[str]] = {}
    for key, value in data.items():
        if key == "expected":
            continue
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise TypeError(f"分片 {key} 必须是路径列表")
        splits[str(key)] = [str(item) for item in value]
    return splits


def load_split_expected(source: str | Path | Mapping[str, Any]) -> dict[str, int]:
    """读取分片文件里的期望人数；没有则返回空映射。"""
    data = _as_mapping(source)
    expected = data.get("expected")
    if expected is None:
        return {}
    if not isinstance(expected, Mapping):
        raise TypeError("分片期望人数必须是映射")
    return {str(key): int(value) for key, value in expected.items()}


def require_split_counts(
    splits: Mapping[str, Sequence[str]],
    expected: Mapping[str, int],
) -> None:
    """校验各分片人数。人数不对则失败，不改名单。

    Args:
        splits: 分片名到相对路径。
        expected: 分片名到期望人数。

    Raises:
        ValueError: 某分片人数与期望不符。
        TypeError: 期望表不是映射。
    """
    if not isinstance(expected, Mapping):
        raise TypeError("分片期望人数必须是映射")
    for name, count in expected.items():
        actual = len(splits.get(str(name), ()))
        if actual != int(count):
            raise ValueError(f"分片 {name} 期望 {count} 个样本，实际 {actual}")


def _as_mapping(source: str | Path | Mapping[str, Any]) -> Mapping[str, Any]:
    """文件读成映射，已是映射则原样返回。"""
    if isinstance(source, Mapping):
        return source
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"分片名单不存在: {path.as_posix()}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise TypeError(f"分片名单根节点必须是映射: {path.as_posix()}")
    return loaded
