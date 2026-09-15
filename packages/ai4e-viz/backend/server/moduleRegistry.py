"""后端一级模块注册表。

当前重构阶段保留旧FastAPI路由实现以确保接口不变；注册表先固定模块边界，后续路由
逐项搬入模块 ``api.py`` 时无需再次修改Server入口。
"""

from __future__ import annotations

from dataclasses import dataclass

from modules import MODULE_NAMES


@dataclass(frozen=True)
class BackendModule:
    """一级模块的稳定注册信息。"""

    name: str
    has_frontend: bool
    has_persistence: bool


_NO_FRONTEND = {"visConvertor", "MCP", "visEngine"}
_PERSISTENT = {"dataAssets", "visTaskManage", "visPhysField", "visIO", "automation", "reportManage", "reportDesigner"}

MODULE_REGISTRY = tuple(
    BackendModule(name=name, has_frontend=name not in _NO_FRONTEND, has_persistence=name in _PERSISTENT)
    for name in MODULE_NAMES
)


def module_names() -> tuple[str, ...]:
    """返回按架构约定排序的十三级模块名，供健康检查和测试使用。"""

    return tuple(module.name for module in MODULE_REGISTRY)
