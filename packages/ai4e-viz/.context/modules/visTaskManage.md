# visTaskManage 文件索引

职责：目录、推荐、参数 Schema、示例和 VisualizationSpec 版本。PRD：[`visTaskManage.md`](../../docs/PRD/visTaskManage.md)；变更记录：[`CHANGELOG.md`](../../docs/PRD/CHANGELOG.md)。

## 模块设计

`visTaskManage`以可视化任务/VisualizationSpec为聚合边界，Application组合目录、推荐、参数校验与版本用例，Spec Repository独占不可变版本和乐观锁SQL。它只通过`dataAssets`公开门面读取资产，通过目标渲染模块公开门面组合预览；前端Page负责工作台布局，不直接访问其他模块内部API或状态。

## 后端

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visTaskManage/__init__.py) | 跨模块唯一公开应用门面 |
| [`api.py`](../../backend/modules/visTaskManage/api.py) | 目录、推荐和 VisualizationSpec Router |
| [`application.py`](../../backend/modules/visTaskManage/application.py) | 推荐、示例与 Spec 用例编排 |
| [`domain.py`](../../backend/modules/visTaskManage/domain.py) | 任务和 Spec 领域对象与规则 |
| [`catalog.py`](../../backend/modules/visTaskManage/catalog.py) | 5 类数据家族、19 语义类型和 23 方法目录 |
| [`parameterRegistry.py`](../../backend/modules/visTaskManage/parameterRegistry.py) | 动态参数 Schema、默认值和校验 |
| [`examples.py`](../../backend/modules/visTaskManage/examples.py) | 内置/真实数据示例解析 |
| [`repository.py`](../../backend/modules/visTaskManage/repository.py) | 任务目录相关 SQLite 访问 |
| [`specRepository.py`](../../backend/modules/visTaskManage/specRepository.py) | VisualizationSpec 不可变版本与乐观锁 SQL |

## 前端

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/visTaskManage/index.js) | 跨模块公开门面 |
| [`module.js`](../../frontend/src/modules/visTaskManage/module.js) | 推荐、示例、Spec 和配置器路由元数据 |
| [`model.js`](../../frontend/src/modules/visTaskManage/model.js) | 任务、推荐与 Spec 前端模型 |
| [`api.js`](../../frontend/src/modules/visTaskManage/api.js) | Endpoint、请求和 DTO 转换 |
| [`fallback.js`](../../frontend/src/modules/visTaskManage/fallback.js) | 后端不可用时的内置案例降级数据 |
| [`terminology.js`](../../frontend/src/modules/visTaskManage/terminology.js) | 可视化方法与界面术语映射 |
| [`components/ExamplePreview.jsx`](../../frontend/src/modules/visTaskManage/components/ExamplePreview.jsx) | 按表现类型组合预览组件 |
| [`pages/ExamplePage.jsx`](../../frontend/src/modules/visTaskManage/pages/ExamplePage.jsx) | 示例详情页 |
| [`pages/RecommendationsPage.jsx`](../../frontend/src/modules/visTaskManage/pages/RecommendationsPage.jsx) | 推荐候选页 |
| [`pages/SpecsPage.jsx`](../../frontend/src/modules/visTaskManage/pages/SpecsPage.jsx) | Spec 列表/版本页 |
| [`pages/VisualizationConfiguratorPage.jsx`](../../frontend/src/modules/visTaskManage/pages/VisualizationConfiguratorPage.jsx) | 参数配置与可视化工作台 |

测试：[`test_vis_task_manage.py`](../../backend/tests/modules/test_vis_task_manage.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)、[`contracts.test.jsx`](../../frontend/src/test/contracts.test.jsx)与Playwright主链路/Excel专项。

## Dojo 当前实现文件

- `backend/modules/visTaskManage/__init__.py`：可视化任务管理模块公开入口。
- `backend/modules/visTaskManage/api.py`：可视化任务管理的 HTTP 适配层。
- `backend/modules/visTaskManage/application.py`：可视化任务应用用例门面。
- `backend/modules/visTaskManage/catalog.py`：Canonical data-semantics and visualization-method catalog.
- `backend/modules/visTaskManage/domain.py`：可视化任务、方法推荐和Spec版本的领域规则。
- `backend/modules/visTaskManage/examples.py`：Deterministic, backend-backed examples for every visualization method.
- `backend/modules/visTaskManage/fileSpecRepository.py`：任务目录中的不可变配置修订；所有输入仅允许声明式 JSON。
- `backend/modules/visTaskManage/parameterRegistry.py`：Versioned VisualizationSpec parameter schemas.
- `backend/modules/visTaskManage/repository.py`：可视化任务持久化公开门面。
- `backend/modules/visTaskManage/specRepository.py`：VisualizationSpec表的模块内Repository实现。
- `frontend/src/modules/visTaskManage/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/components/ExamplePreview.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/fallback.js`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/module.js`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/pages/ExamplePage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/pages/RecommendationsPage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/pages/SpecsPage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/pages/VisualizationConfiguratorPage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visTaskManage/terminology.js`：独立应用交互与调用适配。

## 对象工作台新增文件

- `backend/modules/visTaskManage/physicalSpec.py`：物理工作台配置版本转换与布局规则；新增窗口按 1 全幅、2 横排、3 上二下一、4 田字格排列；历史文件始终保持原样。流线缺起点类型按线段读取，命名面对象引用必须已在管线中且无环。`view_overlay_frames` 把布局矩形换成窗体左上角标签位置。
