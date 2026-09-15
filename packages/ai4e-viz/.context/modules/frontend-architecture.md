# 前端 App 与 Infrastructure 文件索引

业务文件逐模块见 [总索引](../index.md)。App 只组合模块公开门面；Infrastructure 只提供无业务含义的基座，不反向导入业务模块。

## 应用入口

| 文件 | 作用 |
| --- | --- |
| [`src/main.jsx`](../../frontend/src/main.jsx) | React DOM 启动入口 |
| [`src/App.jsx`](../../frontend/src/App.jsx) | 应用壳、HashRouter 与模块页面装配；不硬编码报告等业务数量 |
| [`src/qoder-design-runtime.jsx`](../../frontend/src/qoder-design-runtime.jsx) | 设计画布运行时桥接 |
| [`src/styles.css`](../../frontend/src/styles.css) | 应用级基础样式与主题覆盖 |
| [`app/moduleRegistry.js`](../../frontend/src/app/moduleRegistry.js) | 只消费一级模块 `index.js` 的注册表；包含dataAssets与visDatasets独立条目 |
| [`app/workspace.js`](../../frontend/src/app/workspace.js) | 工作区级无业务状态组合 |

## 公共 Components、Hooks 与 HTTP

| 文件 | 作用 |
| --- | --- |
| [`components/ConnectionStatus.jsx`](../../frontend/src/infrastructure/components/ConnectionStatus.jsx) | 无业务连接状态反馈 |
| [`components/PageTitle.jsx`](../../frontend/src/infrastructure/components/PageTitle.jsx) | 通用页面标题布局 |
| [`hooks/useRemoteSnapshot.js`](../../frontend/src/infrastructure/hooks/useRemoteSnapshot.js) | 通用远端快照/轮询 Hook |
| [`http/client.js`](../../frontend/src/infrastructure/http/client.js) | 统一 HTTP 请求、错误和响应处理 |

## Rendering

| 文件 | 作用 |
| --- | --- |
| [`renderers/EChartsRenderer.jsx`](../../frontend/src/infrastructure/rendering/renderers/EChartsRenderer.jsx) | 通用 ECharts 技术适配 |
| [`renderers/PlotlyRenderer.jsx`](../../frontend/src/infrastructure/rendering/renderers/PlotlyRenderer.jsx) | 通用 Plotly 技术适配 |
| [`renderers/ReactFlowRenderer.jsx`](../../frontend/src/infrastructure/rendering/renderers/ReactFlowRenderer.jsx) | 通用 React Flow 技术适配 |
| [`renderers/VegaRenderer.jsx`](../../frontend/src/infrastructure/rendering/renderers/VegaRenderer.jsx) | 通用 Vega/Vega-Lite 技术适配 |

## 测试文件

| 文件 | 作用 |
| --- | --- |
| [`src/test/setup.js`](../../frontend/src/test/setup.js) | Vitest/jsdom 公共初始化 |
| [`src/test/contracts.test.jsx`](../../frontend/src/test/contracts.test.jsx) | 模块页面、公开门面和交互契约 |
| [`scripts/check-architecture.mjs`](../../frontend/scripts/check-architecture.mjs) | 模块边界、二级禁止项和中文注释门禁 |
| [`e2e/upload-recommend-draw.spec.js`](../../frontend/e2e/upload-recommend-draw.spec.js) | 三服务桌面/移动业务链路 |
| [`e2e/excel-implemented-features.spec.js`](../../frontend/e2e/excel-implemented-features.spec.js) | 按Excel序号验证O3DV、数据预览、图片、物理场和报告的桌面/移动用户链路 |

路由、页面、共享组件或 Renderer 变化时同步目标模块索引、本文件、相关 PRD/变更记录和测试；错误写根 [`error.log`](../../error.log)。

## Dojo 独立应用适配文件

- `frontend/src/app/StorageScopeProvider.jsx`：会话级目标任务上下文，图表与物理工作区共用。
- `frontend/src/infrastructure/embed/communicator.js`：核对消息来源、frame身份并清理监听。
