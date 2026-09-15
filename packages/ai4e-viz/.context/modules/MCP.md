# MCP 文件索引

职责：把一级模块公开操作描述为 MCP 工具；当前无前端模块和独立 HTTP Router。PRD：[`MCP.md`](../../docs/PRD/MCP.md)。

## 模块设计

`MCP`是协议防腐和工具编排限界上下文，不复制被封装模块的业务规则。工具Schema映射到一级模块`__init__.py`公开用例，鉴权、校验、错误语义仍由所属业务模块负责；禁止直接暴露Repository、SQL或`visEngine`内核。MCP Server是否落地属于本模块协议适配，不在FastAPI Router中伪装。

| 后端文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/MCP/__init__.py) | MCP 工具描述公开门面 |
| [`api.py`](../../backend/modules/MCP/api.py) | MCP 协议适配边界，不承载业务 Router |
| [`application.py`](../../backend/modules/MCP/application.py) | 工具 Schema 与一级模块公开用例编排 |
| [`domain.py`](../../backend/modules/MCP/domain.py) | 工具描述和值对象规则 |

测试：[`test_mcp.py`](../../backend/tests/modules/test_mcp.py)。Excel逐功能矩阵将当前能力标记为`demo_only`，因为只有描述符而没有可连接的MCP Server和真实调用。禁止直接访问其他模块 Repository 或把 `visEngine` 内核绕过业务校验暴露出去。


## Dojo 当前实现文件

- `backend/modules/MCP/__init__.py`：MCP一级模块公开门面。
- `backend/modules/MCP/api.py`：MCP协议适配边界。
- `backend/modules/MCP/application.py`：把一级模块公开操作描述为MCP工具。
- `backend/modules/MCP/domain.py`：MCP工具描述领域对象。
