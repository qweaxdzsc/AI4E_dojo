"""普通张量包及 JSON 清单的原子保存；仅面向独立数据目录。"""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

import torch


def digest(value):
    """按可序列化声明生成稳定摘要，拒绝非有限 JSON 数值。"""
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def file_digest(path):
    """分块计算文件摘要，不把完整数据载入内存。"""
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_bundle(path, value):
    """原子写张量包，失败不替换已有文件。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        torch.save(value, temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return str(path)


def save_json(path, value):
    """数据目录中的原子 JSON 保存；运行目录请使用 run/writer。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return str(path)


def load_bundle(path):
    """安全读取仅含张量和基本类型的数据包。"""
    return torch.load(path, map_location="cpu", weights_only=True)
