# 模块组：报告中心与报告编排

## 独立限界上下文

- [`reportManage`](../../backend/modules/reportManage/)：报告实体、列表/读取、不可变版本、复制、导出任务、Quarto/Playwright 适配与下载。
- [`reportDesigner`](../../backend/modules/reportDesigner/)：ReportDocument 领域规则、草稿读取/替换、布局和乐观锁；不拥有报告导出任务。

`reportManage` 需要冻结或读取草稿时，只调用 `reportDesigner.__init__` 的公开接口。内置 G-S 与 Miller 报告属于报告中心适配器，但其原始数据仍由 `fixtures/`、`resources/` 和数据集模块拥有。

## 前端指针

- [`frontend/src/modules/reportManage/`](../../frontend/src/modules/reportManage/)：报告中心、阅读页和导出状态。
- [`frontend/src/modules/reportDesigner/`](../../frontend/src/modules/reportDesigner/)：编辑页与纯 ReportDocument 规则。

## 测试入口

- `backend/tests/modules/test_report_manage.py`
- `backend/tests/modules/test_report_designer.py`
- `backend/tests/test_quarto_export.py`、`test_quarto_project.py`
- Playwright 覆盖草稿恢复、冻结可视化引用、HTML/PDF 和 G-S/Miller 阅读。

修改文档 Schema 时同步 Designer Domain、Repository、前端 Model、冻结读取和导出测试；修改导出路径时保持 `var/exports/reports`、日志可追溯和冻结来源 hash。
