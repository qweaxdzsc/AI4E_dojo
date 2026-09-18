"""任务声明的操作连接；管理进程只读声明，子进程才加载用户实现。"""

from importlib import import_module
from pathlib import Path

from ..templates.materialize import read_entry

_OPTIONAL = frozenset({"inspect", "infer", "evaluate", "export"})


def operation_target(recipe: str | Path, name: str) -> str:
    """由公共配置指定领域连接；缺少连接只使该项管理操作不可用。"""
    if name not in _OPTIONAL:
        raise ValueError(f"operation_unavailable: {name}")
    folder = Path(recipe)
    module = read_entry(folder).get("components", {}).get("application")
    if isinstance(module, str) and module.strip():
        return _qualified(f"{module.strip()}.{name}", name)
    raise ValueError(f"operation_unavailable: {name}")


def load_operation(target: str):
    """在执行子进程加载已捕获的入口，不推测模型或组件类型。"""
    module, name = target.rsplit(".", 1)
    operation = getattr(import_module(module), name)
    if not callable(operation):
        raise TypeError(f"任务操作不可调用: {target}")
    return operation


def _qualified(target: str, name: str) -> str:
    if "." not in target or not all(part.isidentifier() for part in target.split(".")):
        raise ValueError(f"任务操作入口无效: {name}")
    return target
