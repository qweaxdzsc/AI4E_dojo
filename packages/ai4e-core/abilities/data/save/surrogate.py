"""普通拟合状态的自包含保存：JSON结构与校验数组，不执行pickle或动态导入。"""

import hashlib
import json
import math
import shutil
import uuid
from pathlib import Path

import numpy as np

from .array_manifest import read_arrays, save_arrays


def save_state(directory, state, *, context):
    """完整状态先写同级临时目录再发布；拒绝覆盖，返回可搬移清单路径。

    state仅支持字符串键字典、列表、元组、有限标量和实数数组。
    原生树模型文本可作为字符串保存；不保存闭包或任意可执行对象。
    context是调用方显式提供的字段/准备/来源约定，读取方负责比较。
    """
    arrays = {}

    def encode(value):
        if isinstance(value, np.ndarray):
            key = f"array_{len(arrays)}"
            arrays[key] = value
            return ["array", key, value.dtype.str]
        if isinstance(value, np.generic):
            value = value.item()
        if value is None or type(value) in (bool, int, str):
            return ["scalar", value]
        if type(value) is float and math.isfinite(value):
            return ["scalar", value]
        if isinstance(value, dict) and all(isinstance(key, str) for key in value):
            return ["dict", [[key, encode(item)] for key, item in value.items()]]
        if isinstance(value, (list, tuple)):
            return ["tuple" if isinstance(value, tuple) else "list", [encode(v) for v in value]]
        raise TypeError("拟合状态含不支持的对象或非有限标量")

    metadata = {"version": 1, "state": encode(state), "context": encode(context)}
    metadata["content_sha256"] = hashlib.sha256(
        json.dumps(metadata, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()
    directory = Path(directory).resolve()
    if directory.exists():
        raise FileExistsError(directory)
    directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = directory.with_name(f".{directory.name}-{uuid.uuid4().hex}")
    try:
        save_arrays(temporary, arrays, kind="fitted-state-v1", metadata=metadata)
        if directory.exists():
            raise FileExistsError(directory)
        temporary.rename(directory)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return str(directory / "manifest.json")


def read_state(path):
    """核对数组摘要、布局和类型，返回(state, context)，不实例化模型。"""
    record, arrays = read_arrays(path, kind="fitted-state-v1")
    metadata = record["metadata"]
    expected = metadata.pop("content_sha256", None)
    if (
        expected
        != hashlib.sha256(
            json.dumps(metadata, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
        ).hexdigest()
    ):
        raise ValueError("状态文本或上下文摘要改变")
    if metadata["version"] != 1:
        raise ValueError("拟合状态版本不兼容")

    def decode(node):
        kind, value = node[:2]
        if kind == "array":
            array = np.array(arrays[value], copy=True)
            if array.dtype.str != node[2]:
                raise ValueError("状态数组精度改变")
            return array
        if kind == "scalar":
            if value is not None and type(value) not in (bool, int, float, str):
                raise ValueError("状态标量类型非法")
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("状态标量非有限")
            return value
        if kind == "dict":
            if len({key for key, _ in value}) != len(value):
                raise ValueError("状态字典键重复")
            return {key: decode(item) for key, item in value}
        if kind in ("list", "tuple"):
            items = [decode(item) for item in value]
            return tuple(items) if kind == "tuple" else items
        raise ValueError("未知状态节点")

    return decode(metadata["state"]), decode(metadata["context"])
