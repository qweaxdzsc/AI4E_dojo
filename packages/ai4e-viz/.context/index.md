# AI4E_Vis · 全局上下文索引

> 固定读序：[`AGENTS.md`](../AGENTS.md) → 本文件 → 目标模块索引 → 相关 PRD → 源码与测试。产品行为以用户当前要求和 [`docs/PRD/`](../docs/PRD/) 为准。最后核对：2026-08-29。

## 总体架构设计

AI4E_Vis 以十三级一级业务模块作为前后端同名的**限界上下文**。目录先按业务模块切分，再在模块内部按需要做技术分层；目标是让任一一级模块连同前端、后端和持久化边界可整体拆分，而不是建立全局业务 `pages`、`api` 或大而全的共享层。

### 后端：DDD 与端口适配思想

- `backend/modules/<moduleName>` 是领域边界。`api.py` 负责入站 HTTP 适配，`application.py` 负责用例、事务和跨对象编排，`domain.py` 负责实体、值对象、不变量与纯规则，`repository.py` 负责本模块表、SQL和映射；小模块按实际复杂度合并文件，不创建空层。
- `server` 只做进程启动、Router 注册和技术健康；`infrastructure` 只做 SQLite 连接原语、文件存储、配置、日志和埋点等无业务含义能力。依赖方向固定为 `server → module.api → application → domain/repository/adapters → infrastructure`。
- 每个一级模块拥有自己的持久化边界，写操作经过模块 Repository；跨模块只导入目标模块 `__init__.py` 的公开用例，不访问内部 Repository 或表。
- `visPhysField/modules/*` 是一级限界上下文内的二级业务能力，不是独立服务；它们共享一级 Router、Application、Repository、SQLite、Trame 会话和错误/埋点上下文。
- `visEngine` 仅提供无业务语义的 VTK/数值内核、缓存与性能原语，不允许 Router、URL、Trame Server、SQLite 或任务/资产/报告业务进入。

### 前端：模块优先的微领域驱动

- `frontend/src/modules/<moduleName>` 是第一层业务边界。模块可按需拥有 `model.js`、`api.js`、`hooks/`、`components/` 和 `pages/`；`index.js` 是跨模块唯一公开门面，`module.js` 只负责路由、导航和权限元数据。
- `model` 表达前端业务实体和值对象，`api` 合并 Endpoint、HTTP 请求与 DTO 防腐转换，Hook 编排 Query/Command/副作用，业务 Component 通过 Props/事件协作，Page 只组织布局并组合一个或多个公开聚合对象。
- 前端 DDD 只取“围绕业务语义与边界组织代码”的微领域思想，不机械复制后端层级。小模块允许保持少量文件；公共 `infrastructure` 只容纳无业务含义的 HTTP、Renderer、运行时、通用 Hook 和共享 Components。
- `visPhysField/modules/*` 可以拥有二级业务 Model、Hook、Component 和局部样式，但共享一级 API、Provider、Store、路由和 Trame 连接，不建立独立 `api.js`、`module.js` 或 `index.js`。

总体决策、目录模板、持久化和验收边界见 [`architecture.md`](../docs/architecture/architecture.md)；本索引及模块索引描述当前文件事实。

## 运行与公共基座

| 范围 | 文件位置与索引 |
| --- | --- |
| 仓库说明与统一开发入口 | [`README.md`](../README.md)、[`AGENTS.md`](../AGENTS.md)；代码子目录不建立局部`AGENTS.md`，模块约束统一进入本索引及`modules/` |
| FastAPI、模块注册、后端 Infrastructure | [`backend/server/`](../backend/server/)、[`backend/infrastructure/`](../backend/infrastructure/)；逐文件见 [`backend-architecture.md`](modules/backend-architecture.md) |
| React App、前端 Infrastructure | [`frontend/src/app/`](../frontend/src/app/)、[`frontend/src/infrastructure/`](../frontend/src/infrastructure/)；逐文件见 [`frontend-architecture.md`](modules/frontend-architecture.md) |
| HTTP Router | [`backend/server/api.py`](../backend/server/api.py) 与各模块 `api.py`；路径见 [`api-registry.md`](api-registry.md) |
| PRD | [`docs/PRD/README.md`](../docs/PRD/README.md) 与 [`docs/PRD/CHANGELOG.md`](../docs/PRD/CHANGELOG.md) |
| Excel逐功能测试 | [`EXCEL_FEATURE_TEST_MATRIX.md`](../docs/testing/EXCEL_FEATURE_TEST_MATRIX.md)；后端专项与桌面/移动E2E逐项证据见该矩阵 |
| 数据、日志与埋点 | 运行目录 `var/`；规则见 [`storage-observability.md`](modules/storage-observability.md) |

## 十三级一级模块文件入口

| 模块 | 后端位置 | 前端位置 | PRD | 逐文件索引/二级索引 |
| --- | --- | --- | --- | --- |
| `dataAssets` | [`backend/modules/dataAssets/`](../backend/modules/dataAssets/) | [`frontend/src/modules/dataAssets/`](../frontend/src/modules/dataAssets/) | [`dataAssets.md`](../docs/PRD/dataAssets.md) | [`模块索引`](modules/dataAssets.md) |
| `visTaskManage` | [`backend/modules/visTaskManage/`](../backend/modules/visTaskManage/) | [`frontend/src/modules/visTaskManage/`](../frontend/src/modules/visTaskManage/) | [`visTaskManage.md`](../docs/PRD/visTaskManage.md) | [`模块索引`](modules/visTaskManage.md) |
| `visGeometry` | [`backend/modules/visGeometry/`](../backend/modules/visGeometry/) | [`frontend/src/modules/visGeometry/`](../frontend/src/modules/visGeometry/) | [`visGeometry.md`](../docs/PRD/visGeometry.md) | [`模块索引`](modules/visGeometry.md) |
| `visDatasets` | [`backend/modules/visDatasets/`](../backend/modules/visDatasets/) | [`frontend/src/modules/visDatasets/`](../frontend/src/modules/visDatasets/) | [`visDatasets.md`](../docs/PRD/visDatasets.md) | [`模块索引`](modules/visDatasets.md) |
| `visPhysField` | [`backend/modules/visPhysField/`](../backend/modules/visPhysField/) | [`frontend/src/modules/visPhysField/`](../frontend/src/modules/visPhysField/) | [`visPhysField.md`](../docs/PRD/visPhysField.md) | [`模块索引`](modules/visPhysField.md) → [`二级索引`](modules/visPhysField/index.md) |
| `visFigure` | [`backend/modules/visFigure/`](../backend/modules/visFigure/) | 当前无独立前端模块 | [`visFigure.md`](../docs/PRD/visFigure.md) | [`模块索引`](modules/visFigure.md) |
| `visIO` | [`backend/modules/visIO/`](../backend/modules/visIO/) | [`frontend/src/modules/visIO/`](../frontend/src/modules/visIO/) | [`visIO.md`](../docs/PRD/visIO.md) | [`模块索引`](modules/visIO.md) |
| `visConvertor` | [`backend/modules/visConvertor/`](../backend/modules/visConvertor/) | 当前无独立前端模块 | [`visConvertor.md`](../docs/PRD/visConvertor.md) | [`模块索引`](modules/visConvertor.md) |
| `automation` | [`backend/modules/automation/`](../backend/modules/automation/) | 当前无独立前端模块 | [`automation.md`](../docs/PRD/automation.md) | [`模块索引`](modules/automation.md) |
| `MCP` | [`backend/modules/MCP/`](../backend/modules/MCP/) | 当前无独立前端模块 | [`MCP.md`](../docs/PRD/MCP.md) | [`模块索引`](modules/MCP.md) |
| `reportManage` | [`backend/modules/reportManage/`](../backend/modules/reportManage/) | [`frontend/src/modules/reportManage/`](../frontend/src/modules/reportManage/) | [`reportManage.md`](../docs/PRD/reportManage.md) | [`模块索引`](modules/reportManage.md) |
| `reportDesigner` | [`backend/modules/reportDesigner/`](../backend/modules/reportDesigner/) | [`frontend/src/modules/reportDesigner/`](../frontend/src/modules/reportDesigner/) | [`reportDesigner.md`](../docs/PRD/reportDesigner.md) | [`模块索引`](modules/reportDesigner.md) |
| `visEngine` | [`backend/modules/visEngine/`](../backend/modules/visEngine/) | 当前无前端模块 | [`visEngine.md`](../docs/PRD/visEngine.md) | [`模块索引`](modules/visEngine.md) |

## 跨模块专题

- 任务、数据和可视化资产链路：[`task-data-io.md`](modules/task-data-io.md)
- 几何、图片和转换链路：[`geometry-figure-convertor.md`](modules/geometry-figure-convertor.md)
- 物理场与内核边界：[`physical-field-engine.md`](modules/physical-field-engine.md)
- 报告链路：[`reporting.md`](modules/reporting.md)
- automation/MCP：[`automation-mcp.md`](modules/automation-mcp.md)
- SQLite、文件与可观测性：[`storage-observability.md`](modules/storage-observability.md)

## 修改联动与测试

每次修改必须同步目标模块索引、相关 PRD/变更记录和测试；错误写入 [`error.log`](../error.log)。新增、删除或移动模块文件时，架构测试会检查其是否出现在对应模块索引。仓库只允许根`AGENTS.md`，模块局部约束必须写入对应`.context/modules/*.md`和前后端rules。后端先跑 `backend/tests/modules/test_<module>.py`，再跑契约/架构；前端跑架构检查、Vitest、build，跨页面链路补 Playwright。

规则入口：[后端](../.cursor/rules/ai4e-vis-backend.mdc) · [前端](../.cursor/rules/ai4e-vis-frontend.mdc) · [计划](../.cursor/rules/plan-business-alignment.mdc)。总体设计见 [`architecture.md`](../docs/architecture/architecture.md)，重构执行证据见 [`MODULAR_REFACTOR_PLAN.md`](../docs/migration/MODULAR_REFACTOR_PLAN.md)。

## Dojo 迁入与独立工作台

- `cli.py`：安装入口；`backend/server/{api,runtime,dev}.py`：应用、可信上下文和源码调试启动。
- `backend/infrastructure/{storage,process,web}`：文件事务、进程隔离、代理。
- 新资产真源为注入任务目录；旧 `var/` 仅是历史布局名，默认缓存现位于用户缓存根。
- `docs/migration/source-manifest.json` 与 `docs/migration/dojo-integration.md`：来源与实际验证。

## 2026-09-14 迁移验收导航

- [接入与安装](../docs/migration/dojo-integration.md)、[全文件目录](../docs/migration/file-inventory.md)、[来源清单](../docs/migration/source-manifest.json)。
- [Dojo圈定验收](../../../.context/mvp/vis-migration-acceptance.md)：完整迁入、配置资产、三维功能三类结论。

对象工作台：物理配置版本 2、具名分析对象、即时显示、1–4 视图、固定空间 Probe 和时序导出。文件与验收导航见 `modules/visPhysField.md`；配置转换见 `modules/visTaskManage.md`。

工作台参考图样式：`modules/visPhysField.md` 索引图标、紧凑属性与嵌入外壳；根 `tests/integration/viz_visual_browser.cjs` 保留真实结果的四尺寸截图。

后处理Tab保持：`worker.py`在IPC前stash草稿；`trameUI/controller.py`接受visibility暂停/重绘，`client/bridge.js`接收直接同源宿主尺寸通知；React `PhysFieldWorkspacePage.jsx`与`usePhysField.js`校验并转交。宿主验收见根 `e2e/post-session.spec.ts`、`post-real.spec.ts` 与 `.context/mvp/post-workspace-acceptance.md`。
