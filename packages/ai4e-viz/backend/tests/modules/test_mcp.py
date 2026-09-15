"""MCP 模块的协议无关工具描述测试。"""

import pytest

from modules.MCP import tool_descriptor


def test_mcp_builds_descriptor_without_importing_repository() -> None:
    """MCP 只应描述一级模块公开操作，不执行内部持久化。"""

    descriptor = tool_descriptor(
        "list_visualizations",
        "列出已保存的可视化资产",
        {"type": "object", "properties": {"artifact_id": {"type": "string"}}},
    )
    assert descriptor.name == "list_visualizations"
    assert descriptor.input_schema["type"] == "object"
    with pytest.raises(ValueError):
        tool_descriptor("", "缺少名称", {})
