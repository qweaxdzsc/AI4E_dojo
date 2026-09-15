# ai4e-task 模块索引

本地可安装 Python 包，依赖 spec/core；不采用 DDD、不导入 recipes。正式版本仅由 new/fork 创建。完整架构见唯一架构文档第 10、19.11 节。

## 目录与文档

- `packages/ai4e-task/cli/`：命令解析、JSON/文本输出、项目/任务/模板/版本命令；产品说明 `docs/PRD/ai4e-task/cli/PRD.md`。
- `packages/ai4e-task/projects/`：项目创建、打开、恢复及共享资产来源；产品说明 `docs/PRD/ai4e-task/projects/PRD.md`。
- `packages/ai4e-task/tasks/`：new/fork、资产复制、本地执行、状态查询和导入；产品说明 `docs/PRD/ai4e-task/tasks/PRD.md`。
- `packages/ai4e-task/versions/`：正式版本、单父树和三类比较；产品说明 `docs/PRD/ai4e-task/versions/PRD.md`。
- `packages/ai4e-task/templates/`：本地模板目录与 task-entry.json 展开；产品说明 `docs/PRD/ai4e-task/templates/PRD.md`。
- `packages/ai4e-task/storage/`：SQLite、布局、原子文件、快照和只读运行记录；`processed_datasets.py` 按名称登记工作区已处理数据集，列出按登记时间倒序，声明指纹不含 `rawprep.workers`；产品说明 `docs/PRD/ai4e-task/storage/PRD.md`。

## 验收与使用

- `.context/mvp/task-acceptance.md`：实际测试范围与证据。
- `.cursor/rules/ai4e-task-architecture.mdc`：代码边界。
- `packages/ai4e-task/README.md`：Python 与 CLI 用法。
- `recipes/aero_cfd/task-entry.json`：案例入口、输入输出与指标语义。
- `docs/adr/0003-task-local-package.md`：当前决策。

## 包内文件职责

- `cli/main.py` 注册命令；`project/task/version/template.py` 转换各类命令；`output.py` 输出文本／JSON。
- `projects/project.py` 创建、打开、清理中断项目；`shared.py` 共享引用及来源；`models.py` 项目类型。
- `tasks/create.py` 编排 new/fork；`assets.py` 核验及复制，共享资产 `kind` 含 `model_preset`；`query.py` 运行查询／导入；`execution.py` 调度；`local.py` 进程身份；`worker.py` 执行；`models.py` 记录类型。
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

- `tasks/inspections.py`、`tasks/inspection_worker.py`：固定配置的公开检查及独立算法进程；失败文案保留 KeyError 字段名。
- `tasks/artifacts.py`：成功正式运行的物理清单、准备记录和检查点候选；排除试跑。可见根内文件即可，不限项目相对路径。
- `tasks/execution.py`：事务内核对预期配置修订，管理记录保存正式或试跑模式。

`versions/details.py`：校验创建快照的固定分阶段参数与明确运行身份摘要，公开门面 `read_version_details`；当前编辑不替代创建参数。

## 平台阶段事实查询

- `tasks/query.py` 的 `get_stage_summary` 由包公开门面导出；只汇总正式运行事实，多阶段失败无逐阶段证据时为 unknown，不由浏览位置或试跑推断完成。
- `docs/PRD/ai4e-task/tasks/PRD.md` 的执行和停止功能记录上述语义；配置修订与检查有效性由各自事实来源保留。
- 新增圈定 `tests/integration/test_web_stage_consistency.py`；与任务查询、执行和平台运行回归联合验证。

## 独立可视化任务交接

- `packages/ai4e-task/tasks/visualizations.py`：公开任务可视化存储区域，检查归档与路径范围。

## 声明驱动原始处理

tasks/rawprep.py 提供 describe_rawprep、initialize_rawprep、validate_rawprep_configuration；配置按修订完整保存 rawprep，描述同修订缓存，但 `processed_name` 每次从当前配置读取，不用来源标识或过期缓存冒充。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

默认展开在 tasks/create.py 创建版本快照前调用 tasks/rawprep.py 的独立检查进程完成，刚创建的工作目录与版本配置一致；ShapeNet 官方案例展开后 `rawprep.vtkhdf` 为开，NASA 为关；fork 与已保存关闭保持原值。

## 显式配置替换与候选描述

- `tasks/configuration.py`：replace_sections 支持受控 rawprep/model/train/trainprep，旧树不参与合并；普通保存保持局部语义。
- `tasks/inspections.py`：inspect_task 的 configuration 参数仅用于 describe_case 候选描述，核对现行修订但不保存候选。
- 长期说明归任务 PRD；测试 `test_task_configuration.py`、`test_web_stage_consistency.py` 覆盖配置替换、模型预设导出与结构跟踪来源，外部扩展回归 `test_recipe_extensions.py`；专项见 `mvp/model-picker-acceptance.md`。

## 独立推理批次

- `tasks/checkpoints.py`：训练中完整候选、来源检查、完整字节摘要及任务 assets 固定副本。
- `tasks/inference_inspection.py`：独立进程调用公开 infer 元信息、准备、设备和比较门面，管理进程不加载模型。
- `tasks/inference.py`：任务级预检、设备选择、捕获请求与代码、批次提交/读取/取消/重试/恢复。
- `tasks/inference_worker.py`：同任务串行锁、每检查点子运行、真实样本进度及协调进程收据。
- `tasks/inference_results.py`：按完整报告或已提交账本读取成员；不扫描残留文件猜测交付。
- `tasks/execution.py`：原公开执行与捕获交接；`tasks/query.py`：将推理目的运行映射为 infer 事实，浏览不改变状态。
- `__init__.py`：公开检查点、批次和结果操作；存储位置沿 `storage/layout.py` 的任务范围门禁。
- 文档：`docs/PRD/ai4e-task/tasks/PRD.md` 第三章、`docs/PRD/ai4e-task/storage/PRD.md` 第三章。圈定入口与未决兼容见 `.context/mvp/inference-acceptance.md`，不据文件存在宣称计算或安装通过。

推理圈定测试：`tests/integration/test_task_infer_checkpoints.py`（实际字节与来源）、`test_task_infer_batches.py`（串行、取消、重试/幂等固定输入）、`test_infer_devices.py`（设备交接）、`test_infer_results.py`（固定结果）、`test_infer_installation.py`（真实安装及复制入口）。`tools/verification/inference_acceptance.py` 提供隔离真实 CFD 身份，执行证据统一见推理验收记录。

## 后处理三页签与固定结果评价

- `tasks/post_results.py`：评价目录只读清单；`list_post_result_files` 按层列举结果树，提交评价时 `freeze_result_item` 才做内容修订。不读数组。
- `tasks/post_metrics.py`：公开提交、查询、取消、幂等及导出；`post_metrics_worker.py`：独立core调用。
- `tasks/inference_inspection.py` 扩展指标目录和固定修订的张量头部检查，`__init__.py` 导出公开门面。
- task/tasks及storage PRD记录所有权；圈定 `test_task_post_results.py`、`test_task_post_metrics.py`。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

## 推理工作台选择与统计

`tasks/{inference,inference_worker,inference_results,inference_exports,query,artifacts,post_results}.py`：检查点×分片、批次终态、只评价目录、导出登记和固定来源；不新增版本。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

- `tests/integration/test_task_infer_partitions.py`：跨分片同名、最后成功不掩盖失败、只评价、继承成功来源重试与取消的实际子进程验收。
