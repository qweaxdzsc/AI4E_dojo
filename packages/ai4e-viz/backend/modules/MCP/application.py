"""把一级模块公开操作描述为MCP工具。"""

from .domain import MCPToolDescriptor


def tool_descriptor(name: str, description: str, input_schema: dict) -> MCPToolDescriptor:
    """构造协议无关的工具描述，供未来MCP Server适配器注册。"""

    if not name or not description:
        raise ValueError("MCP工具名称和说明不能为空")
    return MCPToolDescriptor(name=name, description=description, input_schema=input_schema)
