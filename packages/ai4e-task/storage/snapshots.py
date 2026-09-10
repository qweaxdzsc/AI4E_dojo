"""不可变内容清单与快照；不依赖 Git。"""

import hashlib
import json
from pathlib import Path

from .files import EXCLUDED, copy_content


def inventory(path: str | Path) -> dict[str, str]:
    """按相对文件名计算流式 SHA256，目录与单文件均可。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    paths = sorted(path.rglob("*")) if path.is_dir() else [path]
    result = {}
    for file in paths:
        relative = file.relative_to(path) if path.is_dir() else Path(file.name)
        if any(p in EXCLUDED for p in relative.parts) or file.suffix == ".pyc":
            continue
        if file.is_symlink():
            raise ValueError(f"symlink_not_supported: {file}")
        if file.is_file():
            h = hashlib.sha256()
            with file.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
            result[str(relative)] = h.hexdigest()
    return result


def digest(value: object) -> str:
    """计算排序 JSON 内容摘要。"""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()


def snapshot(source: Path, target: Path) -> dict:
    """复制前后核对来源，拒绝捕获中发生变化的工作目录。"""
    before = inventory(source)
    copy_content(source, target)
    if before != inventory(source) or before != inventory(target):
        raise ValueError("source_changed_during_copy")
    return {"files": before, "digest": digest(before)}
