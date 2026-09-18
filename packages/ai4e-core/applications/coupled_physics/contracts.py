"""耦合物理场局部持久化契约，不要求自由组件继承。"""

import hashlib
import json
from pathlib import Path


def digest(value):
    """稳定配置身份，不包含自身摘要。"""
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def file_digest(path):
    """流式计算文件身份，供准备/权重冻结使用。"""
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_record(path, kind):
    """读回自校验领域记录，拒绝手工改变冻结含义。"""
    result = json.loads(Path(path).read_text())
    identity = result.pop("content_id")
    if result.get("kind") != kind or digest(result) != identity:
        raise ValueError("记录类型或内容摘要不匹配")
    result["content_id"] = identity
    return result


def component_identity(operation):
    """记录实际普通函数所在源码摘要；无需全仓组件注册。"""
    import inspect

    source = inspect.getsourcefile(operation)
    return {
        "module": operation.__module__,
        "name": operation.__qualname__,
        "source": source,
        "sha256": file_digest(source) if source else None,
    }
