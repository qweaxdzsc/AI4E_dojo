"""受控文件、进程间锁和原子提交；不包含可视化业务语义。"""

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def identity(value: str) -> str:
    """拒绝可被解释成路径的标识。"""
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ValueError("invalid_identity")
    return value


def contained(root: str | Path, relative: str) -> Path:
    """解析根内路径，并拒绝父路径和符号链接逃逸。"""
    root = Path(root).resolve()
    rel = Path(relative)
    result = (root / rel).resolve()
    if rel.is_absolute() or ".." in rel.parts or result == root or not result.is_relative_to(root):
        raise ValueError("storage_path_escape")
    return result


def canonical(value: object) -> bytes:
    """规范 JSON 拒绝非有限值，以产生稳定配置摘要。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: object) -> str:
    """计算声明内容摘要。"""
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path: Path) -> dict:
    """读取 JSON 文件，不触发目录初始化。"""
    return json.loads(path.read_text())


def write_json(path: Path, value: object) -> None:
    """同目录临时文件、fsync 后提升；异常不破坏已提交文件。"""
    raw = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def file_lock(root: Path, name: str):
    """跨进程串行提交；锁位于可清理运行区，不是配置真源。"""
    path = contained(root, f".runtime/locks/{identity(name)}.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
