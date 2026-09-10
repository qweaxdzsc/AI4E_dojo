"""数组数据产物原子写入；不负责运行日志或运行配置。"""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import numpy as np


@contextmanager
def atomic_path(path):
    """同文件系统暂存后提升；异常清理临时文件并保留既有成品。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=path.suffix, dir=path.parent)
    os.close(fd)
    temporary = Path(filename)
    try:
        yield temporary
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_npy(path, values) -> None:
    """禁止对象数组，原子保存可独立读取的数值数组。"""
    with atomic_path(path) as temporary, temporary.open("wb") as stream:
        np.save(stream, values, allow_pickle=False)


def save_json(path, value) -> None:
    """保存稳定 JSON 数据清单；仅用于数据目录。"""
    with atomic_path(path) as temporary:
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
