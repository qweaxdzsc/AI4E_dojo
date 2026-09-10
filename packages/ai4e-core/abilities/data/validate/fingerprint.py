"""只读内容摘要：比较输入、权重和来源，不采样、不修改随机流。"""

import hashlib
import json
from pathlib import Path

import torch


def fingerprint(value):
    """对嵌套张量和 JSON 值生成稳定摘要，保留张量形状、类型与序列顺序。"""
    digest = hashlib.sha256()

    def visit(item):
        if isinstance(item, torch.Tensor):
            tensor = item.detach().cpu().contiguous()
            digest.update(json.dumps([str(tensor.dtype), list(tensor.shape)]).encode())
            # 单元素跨步切片也被 torch 视为 contiguous，但字节视图要求步长为 1。
            flat = torch.empty(tensor.numel(), dtype=tensor.dtype)
            flat.copy_(tensor.reshape(-1))
            digest.update(flat.view(torch.uint8).numpy().tobytes())
        elif isinstance(item, dict):
            digest.update(b"dict")
            for key in sorted(item):
                visit(str(key))
                visit(item[key])
        elif isinstance(item, (list, tuple)):
            digest.update(b"sequence" + str(len(item)).encode())
            for child in item:
                visit(child)
        else:
            digest.update(json.dumps(item, ensure_ascii=False, allow_nan=False).encode())
        digest.update(b"\0")

    visit(value)
    return digest.hexdigest()


def file_fingerprint(path):
    """流式计算已有文件摘要。"""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_fingerprint(root):
    """按相对路径汇总 Python 源码，排除缓存及编译产物。"""
    root = Path(root)
    return fingerprint(
        {str(path.relative_to(root)): file_fingerprint(path) for path in sorted(root.rglob("*.py"))}
    )
