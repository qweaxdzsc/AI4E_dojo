# reportManage 文件索引

职责：报告中心、版本、复制、冻结、导出任务、Quarto 和内置报告。PRD：[`reportManage.md`](../../docs/PRD/reportManage.md)。

## 模块设计

`reportManage`以报告实体、不可变版本和导出任务为聚合边界，Repository独占对应SQL，Quarto是模块专属导出适配器。冻结时通过`reportDesigner`公开用例取得已校验文档，并通过`visIO`公开用例引用可视化资产；不得跨表读取对方内部状态。前端报告中心/阅读Page与编辑Page分属不同模块。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/reportManage/__init__.py) | 报告公开应用门面 |
| [`api.py`](../../backend/modules/reportManage/api.py) | 报告 CRUD、版本、导出和下载 Router |
| [`application.py`](../../backend/modules/reportManage/application.py) | 报告、草稿冻结和导出用例编排 |
| [`repository.py`](../../backend/modules/reportManage/repository.py) | 报告实体、版本和导出任务 SQL |
| [`reportRepository.py`](../../backend/modules/reportManage/reportRepository.py) | 报告/版本/导出持久化，以及从一致性SQLite快照恢复缺失报告 |
| [`quarto.py`](../../backend/modules/reportManage/quarto.py) | 锁定 Quarto 导出、诊断和路径适配 |
| [`builtinReports.py`](../../backend/modules/reportManage/builtinReports.py) | 内置审计报告注册与冻结数据 |
| [`gradShafranovReport.py`](../../backend/modules/reportManage/gradShafranovReport.py) | G-S 报告内容适配 |
| [`millerReport.py`](../../backend/modules/reportManage/millerReport.py) | Miller 报告内容适配 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/reportManage/index.js) | 报告页面/能力公开门面 |
| [`module.js`](../../frontend/src/modules/reportManage/module.js) | 报告中心与阅读页路由 |
| [`model.js`](../../frontend/src/modules/reportManage/model.js) | 报告、版本和导出状态模型 |
| [`api.js`](../../frontend/src/modules/reportManage/api.js) | 报告与导出 API 防腐层 |
| [`fallback.js`](../../frontend/src/modules/reportManage/fallback.js) | 内置报告离线/启动降级数据 |
| [`pages/ReportsPage.jsx`](../../frontend/src/modules/reportManage/pages/ReportsPage.jsx) | 报告中心页面 |
| [`pages/ReportPage.jsx`](../../frontend/src/modules/reportManage/pages/ReportPage.jsx) | 报告阅读与下载页面 |

测试：[`test_report_manage.py`](../../backend/tests/modules/test_report_manage.py) 覆盖生命周期和幂等恢复；另有 [`test_quarto_export.py`](../../backend/tests/test_quarto_export.py)、[`test_quarto_project.py`](../../backend/tests/test_quarto_project.py)与Excel报告管理桌面/移动E2E。


## Dojo 当前实现文件

- `backend/modules/reportManage/__init__.py`：报告中心管理模块公开入口。
- `backend/modules/reportManage/api.py`：报告中心、不可变版本和导出任务的 HTTP 适配层。
- `backend/modules/reportManage/application.py`：报告查询、版本冻结、复制和导出任务的应用门面。
- `backend/modules/reportManage/builtinReports.py`：Readable report fixtures served by the backend API.
- `backend/modules/reportManage/gradShafranovReport.py`：Data-derived report blocks for the portable PINO Grad–Shafranov audit.
- `backend/modules/reportManage/millerReport.py`：Data-derived Miller tokamak time-series report.
- `backend/modules/reportManage/quarto.py`：Quarto project generation and persisted asynchronous exports.
- `backend/modules/reportManage/reportRepository.py`：报告实体、草稿、不可变版本和导出任务的迁移期Repository实现。
- `backend/modules/reportManage/repository.py`：报告实体、不可变版本和导出任务Repository公开门面。
- `frontend/src/modules/reportManage/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/fallback.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/module.js`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/pages/ReportPage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/reportManage/pages/ReportsPage.jsx`：独立应用交互与调用适配。

迁移补充：api.py 和 frontend/src/modules/reportManage/api.js 在导出及重试传context；quarto.py 使用visIO公开固定引用读取，物理素材复用同一PNG生产器。
