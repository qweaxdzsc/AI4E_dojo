"""可恢复文件提交、受控目录复制与 JSON 读写。"""

import json
import shutil
from pathlib import Path
from uuid import uuid4

EXCLUDED = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".DS_Store"}


def read_json(path: str | Path) -> dict:
    """读取 UTF-8 JSON 对象。"""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"invalid_record: {path}")
    return value


def write_json(path: str | Path, value: dict) -> None:
    """同级临时文件原子提升，不留下半份 JSON。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temp.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
        )
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def copy_content(source: str | Path, target: str | Path) -> None:
    """复制声明内容；拒绝符号链接，避免隐式越界与可变外部快照。"""
    source, target = Path(source), Path(target)
    if not source.exists():
        raise FileNotFoundError(source)
    if source.is_symlink():
        raise ValueError(f"symlink_not_supported: {source}")
    if source.is_dir():
        target.mkdir(parents=True, exist_ok=False)
        for child in sorted(source.iterdir()):
            if child.name not in EXCLUDED and child.suffix != ".pyc":
                copy_content(child, target / child.name)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
