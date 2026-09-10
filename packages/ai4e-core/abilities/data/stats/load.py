"""读入或写出统计量文件。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from ai4e_core.base.events import traced


@traced("统计参数读取")
def load_statistics(path: str | Path) -> dict[str, Any]:
    """从 YAML 或 JSON 读入统计量映射。

    Args:
        path: 已发布或重算后的统计量文件。

    Returns:
        文件中的键值映射。

    Raises:
        FileNotFoundError: 文件不存在。
        ValueError: 扩展名不支持，或内容不是映射。
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"统计量文件不存在: {file_path}")
    text = file_path.read_text(encoding="utf-8")
    suffix = file_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        loaded = yaml.safe_load(text)
    elif suffix == ".json":
        loaded = json.loads(text)
    else:
        raise ValueError(f"不支持的统计量文件类型: {file_path.suffix}")
    if not isinstance(loaded, dict):
        raise TypeError("统计量文件必须是映射")
    return loaded


@traced("统计参数提交")
def write_statistics(path: str | Path, stats: dict[str, Any]) -> Path:
    """把统计量写成 YAML 或 JSON。

    Args:
        path: 目标路径，由扩展名选择格式。
        stats: 要落盘的映射。

    Returns:
        写出后的路径。
    """
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        text = json.dumps(stats, indent=2)
    elif suffix in {".yaml", ".yml"}:
        text = yaml.safe_dump(stats, sort_keys=True, allow_unicode=True)
    else:
        raise ValueError(f"不支持的统计量文件类型: {file_path.suffix}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = file_path.with_name(f".{file_path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(file_path)
    finally:
        temporary.unlink(missing_ok=True)
    return file_path
