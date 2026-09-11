# ai4e-task 模块索引

本地可安装 Python 包，依赖 spec/core；不采用 DDD、不导入 recipes。正式版本仅由 new/fork 创建。完整架构见唯一架构文档第 19.5 节。

## 目录与文档

- `packages/ai4e-task/cli/`：命令解析、JSON/文本输出、项目/任务/模板/版本命令；产品说明 `docs/PRD/ai4e-task/cli/PRD.md`。
- `packages/ai4e-task/projects/`：项目创建、打开、恢复及共享资产来源；产品说明 `docs/PRD/ai4e-task/projects/PRD.md`。
- `packages/ai4e-task/tasks/`：new/fork、资产复制、本地执行、状态查询和导入；产品说明 `docs/PRD/ai4e-task/tasks/PRD.md`。
- `packages/ai4e-task/versions/`：正式版本、单父树和三类比较；产品说明 `docs/PRD/ai4e-task/versions/PRD.md`。
- `packages/ai4e-task/templates/`：本地模板目录与 task-entry.json 展开；产品说明 `docs/PRD/ai4e-task/templates/PRD.md`。
- `packages/ai4e-task/storage/`：SQLite、布局、原子文件、快照和只读运行记录；产品说明 `docs/PRD/ai4e-task/storage/PRD.md`。

## 验收与使用

- `.context/mvp/task-acceptance.md`：实际测试范围与证据。
- `.cursor/rules/ai4e-task-architecture.mdc`：代码边界。
- `packages/ai4e-task/README.md`：Python 与 CLI 用法。
- `recipes/aero_cfd/task-entry.json`：案例入口、输入输出与指标语义。
- `docs/adr/0003-task-local-package.md`：当前决策。

## 包内文件职责

- `cli/main.py` 注册命令；`project/task/version/template.py` 转换各类命令；`output.py` 输出文本／JSON。
- `projects/project.py` 创建、打开、清理中断项目；`shared.py` 共享引用及来源；`models.py` 项目类型。
- `tasks/create.py` 编排 new/fork；`assets.py` 核验及复制；`query.py` 运行查询／导入；`execution.py` 调度；`local.py` 进程身份；`worker.py` 执行；`models.py` 记录类型。
- `versions/records.py` 正式版本校验；`tree.py` 子树；`compare.py` 三类差异；`models.py` 版本类型。
- `templates/catalog.py` 模板登记；`materialize.py` 展开和输入定位；`models.py` 入口类型。
- `storage/database.py` SQLite；`records.py` 持久化及幂等；`layout.py` 路径门禁；`files.py` 原子 JSON 与复制；`snapshots.py` 摘要；`artifacts.py` 只读产物。
- 旧 `difftree/`、`backend/` 空占位已移除，由 versions 和 tasks 承接实际功能。
- `.context/mvp/task-results/`：本次实际测试和正式案例的证据文件。

## 五段配置与快照职责（2026-09-09）

versions/compare.py 对全部已声明 quantity_config 条件检查缺失；新模板使用五段配置选择器。

## 本机平台接入（2026-09-10）

- `packages/ai4e-task/tasks/configuration.py`：稳定检查或管理配置公开操作。
- `packages/ai4e-task/tasks/management.py`：稳定检查或管理配置公开操作。
- `.context/mvp/web-rawprep-acceptance.md`：平台接入验收记录。
- `tasks/create.py`、`tasks/assets.py`：创建时允许待绑定输入的最小缺陷修复；执行捕获仍严格。管理字段保持旧 JSON schema 兼容。

## 平台阶段交接

- `tasks/inspections.py`、`tasks/inspection_worker.py`：固定配置的公开检查及独立算法进程。
- `tasks/artifacts.py`：成功正式运行的物理清单、准备记录和检查点候选；排除试跑。
- `tasks/execution.py`：事务内核对预期配置修订，管理记录保存正式或试跑模式。

`versions/details.py`：校验创建快照的固定分阶段参数与明确运行身份摘要，公开门面 `read_version_details`；当前编辑不替代创建参数。
