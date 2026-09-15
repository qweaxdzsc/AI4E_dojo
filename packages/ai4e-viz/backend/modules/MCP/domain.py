"""MCP工具描述领域对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPToolDescriptor:
    """一个可从一级模块公开操作生成的MCP工具定义。"""

    name: str
    description: str
    input_schema: dict
