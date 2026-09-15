# reportDesigner 文件索引

职责：ReportDocument、草稿、布局、历史操作和乐观锁；不拥有报告导出任务。PRD：[`reportDesigner.md`](../../docs/PRD/reportDesigner.md)。

## 模块设计

`reportDesigner`以ReportDocument草稿为聚合边界，Domain维护文档结构与布局不变量，Repository只拥有草稿修订和乐观锁SQL。它不创建报告实体或导出任务；冻结/导出由`reportManage`公开用例编排。前端编辑Page只组合本模块文档操作、`visIO`素材选择和其他公开业务组件。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/reportDesigner/__init__.py) | 草稿和文档公开门面 |
| [`api.py`](../../backend/modules/reportDesigner/api.py) | 草稿读取/替换 Router |
| [`application.py`](../../backend/modules/reportDesigner/application.py) | 草稿修订、校验和事务编排 |
| [`domain.py`](../../backend/modules/reportDesigner/domain.py) | ReportDocument、布局与不变量 |
| [`repository.py`](../../backend/modules/reportDesigner/repository.py) | 草稿修订和乐观锁 SQL |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/reportDesigner/index.js) | 报告编辑能力公开门面 |
| [`module.js`](../../frontend/src/modules/reportDesigner/module.js) | 报告编辑路由元数据 |
| [`model.js`](../../frontend/src/modules/reportDesigner/model.js) | 草稿、布局和编辑状态模型 |
| [`api.js`](../../frontend/src/modules/reportDesigner/api.js) | 草稿 API 与 DTO 转换 |
| [`domain/reportDocument.js`](../../frontend/src/modules/reportDesigner/domain/reportDocument.js) | 前端 ReportDocument 纯规则和操作 |
| [`pages/ReportComposerPage.jsx`](../../frontend/src/modules/reportDesigner/pages/ReportComposerPage.jsx) | 报告编排页面 |

测试：[`test_report_designer.py`](../../backend/tests/modules/test_report_designer.py)、前端契约与Excel第88-90项桌面/移动报告编排E2E。


## Dojo 当前实现文件

- `backend/modules/reportDesigner/__init__.py`：报告编排一级模块公开入口。
- `backend/modules/reportDesigner/api.py`：报告编排草稿的 HTTP 适配层。
- `backend/modules/reportDesigner/application.py`：报告自动保存、草稿读取和布局变更用例门面。
- `backend/modules/reportDesigner/domain.py`：报告编排领域规则：建立文档骨架并校验十二列布局与内容引用。
- `backend/modules/reportDesigner/repository.py`：报告草稿与编排修订的持久化实现。
- `frontend/src/modules/reportDesigner/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportDesigner/domain/reportDocument.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportDesigner/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportDesigner/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportDesigner/module.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportDesigner/pages/ReportComposerPage.jsx`：独立应用交互与调用适配。

迁移补充：domain.py 校验新旧两种固定资产引用；ReportComposerPage.jsx 使用 fixedVisualizationReference，素材库经 visIO 当前上下文查询。test_report_designer.py 验证新引用持久化和非法修订；test_vis_exports.py 验证固定修订输出。
