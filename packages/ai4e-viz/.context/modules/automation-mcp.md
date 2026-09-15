# 模块组：脚本化与 MCP

## `automation`

[`backend/modules/automation/`](../../backend/modules/automation/) 定义脚本化业务模型、应用入口和未来持久化边界。当前未完成的脚本保存/执行能力必须显式返回未就绪，不以空壳或假成功冒充实现。

## `MCP`

[`backend/modules/MCP/`](../../backend/modules/MCP/) 只把十三级一级模块已经公开的应用操作描述为 MCP 工具。它不能直接导入其他模块 Repository、SQL、私有 Domain，也不能把 `visEngine` 内核暴露成绕过业务校验的工具。

两者当前没有独立前端模块，也没有正式 HTTP 路由；未来若增加入口，应先明确是脚本业务、MCP 协议还是 Server 装配，并同步 API 注册表。

## 测试入口

- [`backend/tests/modules/test_automation.py`](../../backend/tests/modules/test_automation.py)：未就绪状态和模块边界。
- [`backend/tests/modules/test_mcp.py`](../../backend/tests/modules/test_mcp.py)：工具 Schema 与公开门面限制。

新增能力必须先实现所属业务模块公开用例，再由 automation/MCP 编排，禁止反向把业务规则写进集成模块。
