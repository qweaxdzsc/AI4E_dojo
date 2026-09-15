"""脚本持久化边界。

Excel功能目前尚未形成稳定脚本表，本文件先声明表所有权；后续建表和SQL必须留在本
Repository，禁止放入Server或MCP适配器。
"""


def persistence_ready() -> bool:
    """返回当前脚本持久化是否已实现，避免把目录骨架误报为功能完成。"""

    return False
