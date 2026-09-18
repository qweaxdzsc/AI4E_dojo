# visIO 文件索引

职责：可视化预览、冻结资产、保存、查询与导出边界。PRD：[`visIO.md`](../../docs/PRD/visIO.md)。

## 模块设计

`visIO`以可视化资产为聚合边界，负责表现清单、Spec冻结引用、保存冲突和导出状态；`artifact_visualizations`表与SQL只归本模块Repository。它通过公开门面引用`dataAssets`和`visTaskManage`标识，不读取对方表。前端提供保存/选择能力供任务工作台和报告编排组合，当前无独立Page也不建立全局导出API。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visIO/__init__.py) | 可视化资产公开门面 |
| [`api.py`](../../backend/modules/visIO/api.py) | 预览、保存和查询 Router |
| [`application.py`](../../backend/modules/visIO/application.py) | 参数校验、Spec 冻结和资产编排 |
| [`domain.py`](../../backend/modules/visIO/domain.py) | 可视化资产与导出领域规则 |
| [`repository.py`](../../backend/modules/visIO/repository.py) | artifact_visualizations 表和 SQL |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/visIO/index.js) | 保存/查询能力公开门面 |
| [`module.js`](../../frontend/src/modules/visIO/module.js) | 无主导航的模块元数据 |
| [`model.js`](../../frontend/src/modules/visIO/model.js) | 可视化资产与导出状态模型 |
| [`api.js`](../../frontend/src/modules/visIO/api.js) | 预览、冻结和查询 API 防腐层 |

测试：[`test_vis_io.py`](../../backend/tests/modules/test_vis_io.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)与可视化保存/报告引用E2E。

## Dojo 当前实现文件

- `backend/modules/visIO/__init__.py`：可视化资产保存与导出模块公开入口。
- `backend/modules/visIO/api.py`：可视化资产保存、预览和查询 HTTP 接口。
- `backend/modules/visIO/application.py`：可视化资产保存、引用和导出用例门面。
- `backend/modules/visIO/assetRepository.py`：可視化资产索引的任务目录存储；不使用全局资产数据库。
- `backend/modules/visIO/domain.py`：可视化资产表示与导出状态的领域规则。
- `backend/modules/visIO/exportRepository.py`：任务目录导出记录；成功文件与配置摘要分开保存。
- `backend/modules/visIO/exports.py`：显式输出用例；暂存完成后提交，取消与失败均不发布成功清单。
- `backend/modules/visIO/repository.py`：可视化资产Repository实现。
- `backend/modules/visIO/save.py`：统一保存声明式配置；保存不读取/复制源数据，不渲染或自动截图。
- `frontend/src/modules/visIO/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/visIO/components/ExportStatus.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visIO/components/SaveVisualizationDialog.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visIO/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/visIO/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visIO/module.js`：独立应用交互与调用适配。

2026-09-16 显示设置：对应模块 PRD 已更新色标/范围/背景、矢量采样或透明输出职责。专项测试 `backend/tests/modules/test_phys_display_settings.py`；前端透明表单 `frontend/src/test/transparentExport.test.jsx`，真实入口 `tests/integration/viz_interaction_browser.cjs`（Dojo 根）。
