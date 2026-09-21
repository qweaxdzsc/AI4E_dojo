# ai4e-task 模块索引
## 当前职责与本轮变更

cli/projects/tasks/versions/templates/storage 六类功能；任务运行、版本与资产管理。Task 是模型无关的管理层：模型、数据集和科学兼容性由任务声明的 application/provider 解释，Task 只保存不透明引用和通用状态。

- `packages/ai4e-task/tasks/operations.py`：按需操作声明解析与加载；缺声明只使对应操作不可用。
- `packages/ai4e-task/tasks/records.py`：任务查询与进程收据投影；get_run 可能更新管理状态。
- `packages/ai4e-task/tasks/query.py`：日志/离线导入/阶段状态，保留记录查询公开导出。
- `packages/ai4e-task/tasks/worker.py`：执行捕获脚本及显式配置适配。
- `packages/ai4e-task/tasks/post_metrics_worker.py`：加载任务评价/导出连接；由 run 管运行外围。
- `packages/ai4e-task/tasks/official_scripts.py`：只替换摘要已核验的旧官方包装；`verified_old_sources` 列出可迁文件，现行模板和用户改过的脚本不进入。
- `packages/ai4e-task/templates/materialize.py`：`recipe_entry` 按当前 `config.yaml` 投影公共 `inputs.*`，不使用创建时冻结的旧键。
- `packages/ai4e-task/tasks/configuration.py`：保存成功后刷新任务入口，去掉 `dataset.root` / `train.manifest` 旧快照。
- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


本地可安装 Python 包，依赖 spec/core；不采用 DDD、不导入 recipes。正式版本仅由 new/fork 创建。完整架构见唯一架构文档第 0.1、10、19 节；Agent 定位入口见 `../tasks/architecture.md`。

## 目录与文档

- `packages/ai4e-task/cli/`：命令解析、JSON/文本输出、项目/任务/模板/版本命令；产品说明 `docs/PRD/ai4e-task/cli/PRD.md`。
- `packages/ai4e-task/projects/`：项目创建、打开、恢复及共享资产来源；产品说明 `docs/PRD/ai4e-task/projects/PRD.md`。
- `packages/ai4e-task/tasks/`：new/fork、资产复制、本地执行、状态查询和导入；产品说明 `docs/PRD/ai4e-task/tasks/PRD.md`。
- `packages/ai4e-task/versions/`：正式版本、单父树和三类比较；产品说明 `docs/PRD/ai4e-task/versions/PRD.md`。
- `packages/ai4e-task/templates/`：本地模板目录与 pipeline.py/config.yaml 公共结构发现；产品说明 `docs/PRD/ai4e-task/templates/PRD.md`。
- `packages/ai4e-task/storage/`：SQLite、布局、原子文件、快照和只读运行记录；`processed_datasets.py` 按名称登记工作区已处理数据集，列出按登记时间倒序，声明按规范化身份且不含 `rawprep.workers`，未确认覆盖时同名不同声明拒绝，提供 `describe_processed_name` 与覆盖登记；产品说明 `docs/PRD/ai4e-task/storage/PRD.md`。

## 验收与使用

- WDNO通过公共pipeline/config自动发现；新建、分阶段提交和续训由 `tools/verification/wdno/task_replay.py --staged` 使用公开API实际验收。`tests/integration/test_wdno_task.py` 覆盖同入口数值、版本和缺输入失败；无需Task模型专属执行器，证据见 `.context/mvp/wdno-acceptance.md`。

- `recipes/safediffcon/pipeline.py`：控制模板复用new_task/submit_run/wait_run；Burgers、Tokamak真实分阶段任务验收见 `.context/mvp/safediffcon-acceptance.md` 的2026-09-17现行公共约定验收；三目录真实安装新建/CLI和同输入双入口逐值对照，不新增Task专属执行器或平台操作。

- `.context/mvp/task-acceptance.md`：实际测试范围与证据。
- `.cursor/rules/ai4e-task-architecture.mdc`：代码边界。
- `packages/ai4e-task/README.md`：Python 与 CLI 用法。
- `recipes/aero_cfd/config.yaml`：公共 inputs 与可选领域操作；资产指标语义由运行索引交付。
- `docs/adr/0003-task-local-package.md`：当前决策。

## 包内文件职责

- `cli/main.py` 注册命令；`project/task/version/template.py` 转换各类命令；`output.py` 输出文本／JSON。
- `projects/project.py` 创建、打开、清理中断项目；`shared.py` 共享引用及来源；`models.py` 项目类型。
- `tasks/create.py` 编排 new/fork；`assets.py` 核验及复制，共享资产 `kind` 含 `model_preset`；`query.py` 运行查询／导入；`execution.py` 调度；`local.py` 进程身份；`worker.py` 执行；`official_scripts.py` 只替换核验摘要的旧包装；`models.py` 记录类型。
- `versions/records.py` 正式版本校验；`tree.py` 子树；`compare.py` 三类差异；`models.py` 版本类型。
- `templates/catalog.py` 模板登记；`materialize.py` 展开、`recipe_entry` 与输入定位；`models.py` 入口类型。
- `storage/database.py` SQLite；`records.py` 持久化及幂等；`layout.py` 路径门禁；`files.py` 原子 JSON 与复制；`snapshots.py` 摘要。
- `tasks/artifacts.py` 只读运行产物：切步列举只认公开索引结构与文件仍在，不整文件核验检查点；执行与恢复仍核内容修订。
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

- `tasks/inspections.py`、`tasks/inspection_worker.py`、`tasks/operations.py`：固定配置的公开检查及独立算法进程；失败文案保留 KeyError 字段名；入口由 `components.application` 指定，缺失时该操作不可用，不从旧描述或创建快照回填；不猜测领域。`trace_model` 在案例检查取出网络后引用可视化模块出两档结构图。
- `tasks/artifacts.py`：成功正式运行的物理清单、准备记录和检查点候选；停止/失败正式运行仅开放已提交的训练恢复检查点，排除试跑与未登记残留。可见根内文件即可，不限项目相对路径。
- `tasks/execution.py`：事务内核对预期配置修订，管理记录保存正式或试跑模式。

`versions/details.py`：校验创建快照的固定分阶段参数与明确运行身份摘要，公开门面 `read_version_details`；当前编辑不替代创建参数。

## 平台阶段事实查询

- `tasks/query.py` 的 `get_stage_summary` 由包公开门面导出；只汇总正式运行事实，多阶段失败无逐阶段证据时为 unknown，不由浏览位置或试跑推断完成。已成功的正式执行不会被后来的 unknown 读盘改成未运行。
- `docs/PRD/ai4e-task/tasks/PRD.md` 的执行和停止功能记录上述语义；配置修订与检查有效性由各自事实来源保留。
- 新增圈定 `tests/integration/test_web_stage_consistency.py`；与任务查询、执行和平台运行回归联合验证。

## 独立可视化任务交接

- `packages/ai4e-task/tasks/visualizations.py`：公开任务可视化存储区域，检查归档与路径范围。

## 声明驱动原始处理

tasks/rawprep.py 提供 describe_rawprep、initialize_rawprep、validate_rawprep_configuration；配置按修订完整保存 rawprep，描述同修订缓存，但 `processed_name` 每次从当前配置读取，不用来源标识或过期缓存冒充。发布共享数据集只登记输出资产，不回写任务 `dataset.partitions` 或绑定源。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

默认展开在 tasks/create.py 创建版本快照前调用 tasks/rawprep.py 的独立检查进程完成，刚创建的工作目录与版本配置一致；ShapeNet 官方案例展开后 `rawprep.vtkhdf` 为开，NASA 为关；fork 与已保存关闭保持原值。

## 显式配置替换与候选描述

- `tasks/configuration.py`：replace_sections 支持受控 rawprep/model/train/trainprep，旧树不参与合并；普通保存保持局部语义。
- `tasks/inspections.py`：inspect_task 的 configuration 参数仅用于 describe_case 候选描述，核对现行修订但不保存候选。
- 长期说明归任务 PRD；测试 `test_task_configuration.py`、`test_web_stage_consistency.py` 覆盖配置替换、模型预设导出与结构跟踪来源，外部扩展回归 `test_recipe_extensions.py`；专项见 `mvp/model-picker-acceptance.md`。

## 独立推理批次

- `tasks/checkpoints.py`：训练中完整候选、来源检查、完整字节摘要及任务 assets 固定副本；推理样本缺准备改为明确错误，不冒泡成泛化缺文件。
- `tasks/inference_inspection.py`：独立进程调用公开 infer 元信息、准备、设备和比较门面，管理进程不加载模型。
- `tasks/inference.py`：任务级预检、设备选择、捕获请求与代码、批次提交/读取/取消/重试/恢复；缺状态文件的批次明确报不存在，列表跳过空登记。
- `tasks/inference_worker.py`：同任务串行锁、每检查点子运行、真实样本进度及协调进程收据。
- `tasks/inference_results.py`：按完整报告或已提交账本读取成员；不扫描残留文件猜测交付。
- `tasks/execution.py`：原公开执行与捕获交接；`tasks/query.py`：将推理目的运行映射为 infer 事实，浏览不改变状态。
- `__init__.py`：公开检查点、批次和结果操作；存储位置沿 `storage/layout.py` 的任务范围门禁。
- 文档：`docs/PRD/ai4e-task/tasks/PRD.md` 第三章、`docs/PRD/ai4e-task/storage/PRD.md` 第三章。圈定入口与未决兼容见 `.context/mvp/inference-acceptance.md`，不据文件存在宣称计算或安装通过。

推理圈定测试：`tests/integration/test_task_infer_checkpoints.py`（实际字节与来源）、`test_task_infer_batches.py`（串行、取消、重试/幂等固定输入）、`test_infer_devices.py`（设备交接）、`test_infer_results.py`（固定结果）、`test_infer_installation.py`（真实安装及复制入口）。`tools/verification/inference_acceptance.py` 提供隔离真实 CFD 身份，执行证据统一见推理验收记录。

## 后处理三页签与固定结果评价

2026-09-18 结果来源追加：后处理结果文件只列当前训练绑定平台数据集及固定推理结果，checkpoint 无统计状态由推理结果接口保留。

- `tasks/post_results.py`：评价目录只读推理清单；`list_post_result_files` 按层列举本任务平台数据集、推理固定结果与训练运行输出文件夹。有写出则展开 `data_dir` 的预测、网格、导出；无写出仍保留「训练运行 ·」短号文件夹并说明空态。推理样本缺网格时列出「未写出VTK」原因。不列举检查点、日志、原始处理或数据准备副本；提交评价时 `freeze_result_item` 才做内容修订。不读数组。
- `tasks/post_metrics.py`：公开提交、查询、取消、幂等及导出；`post_metrics_worker.py`：独立core调用。
- `tasks/inference_inspection.py` 扩展指标目录和固定修订的张量头部检查，`__init__.py` 导出公开门面。
- task/tasks及storage PRD记录所有权；圈定 `test_task_post_results.py`、`test_task_post_metrics.py`。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

## 推理工作台选择与统计

`tasks/{inference,inference_worker,inference_results,inference_exports,query,artifacts,post_results}.py`：检查点×分片、批次终态、只评价目录、导出登记和固定来源；不新增版本。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

- `tests/integration/test_task_infer_partitions.py`：跨分片同名、最后成功不掩盖失败、只评价、继承成功来源重试与取消的实际子进程验收。


推理结果视图配置更新：`tasks/inference_results.py` 保留全批预期数量；`inference_inspection.py` 在受控子进程调用 `result_views`，交付全部样本聚合与样本明细。专项复用批次/分片/服务测试。 验收见 `.context/mvp/inference-result-views-acceptance.md`。

## 项目共享数据切片

projects/datasets.py 管共享查询与绑定；projects/dataset_migration.py 管历史复制；storage/shared_datasets.py 管生产占用、完整性与发布；tasks/output_bindings.py 管声明解析。execution/worker/records/assets/artifacts/configuration/create/query 交接共享与历史引用。

长期说明见对应包 PRD；当前证据见 `.context/mvp/task-shared-datasets-acceptance.md`。

## 平台配置生成

`packages/ai4e-task/tasks/configuration.py`：新增公开 replace_configuration，完整保存不二次合并；复用普通保存的修订、事务和共享资产维护。

专项证据：`../mvp/platform-configuration-acceptance.md`。

历史登记迁移：`projects/dataset_migration.py::migrate_shared_datasets` 的 sources 参数按名称→正式运行显式选择，避免旧登记名与冻结配置名不同导致错选；`test_task_shared_dataset_migration.py` 覆盖别名、试跑拒绝、原值读回和重复迁移。实跑证据见共享专项中的 registered-migration 记录。

GenCP 原样模板 Task 补验未通过：缺入口声明，六组十八次提交均启动前失败；见 [GenCP 验收](../mvp/gencp-acceptance.md) 的 2026-09-17 记录。

WDNO公共约定使用方：直接发现pipeline.py/config.yaml，阶段输入来自inputs，产物与比较来自公共运行索引；本轮未修改Task通用实现。测试test_wdno_task.py与实验工具task_replay.py，实际范围见WDNO专项。

## 公共约定迁移（实施中）

- `tools/migration/recipe_conventions/configuration.py`：离线公共路径转换。
- `tools/migration/recipe_conventions/transaction.py`：逐文件候选、原件备份、内容漂移检查、原子目录切换及回滚；只在运行器停止后显式应用。
- `tasks/official_scripts.py`：只替换摘要已核验的 train/trainprep/infer/post/rawprep 包装；无核验摘要则不调用迁移。
- `tasks/artifacts.py` 与 `tasks/assets.py`：公共资产及全部依赖内容校验；缺索引只失去发现，损坏不能作为可用输入。
- 验收入口：`../mvp/recipe-task-conventions-acceptance.md`；`test_recipe_migration.py`、`test_recipe_conventions.py`、`test_task_convention_execution.py`。

公共数组资产：`tasks/assets.py` 的 `indexed_asset/copy_bundle` 与 `projects/shared.py` 保留发布者声明的自包含目录，复制共享和fork时原样复制科学文件、重定位管理引用。`tests/integration/test_task_array_bundles.py` 验证删除原件、移动项目和篡改拒绝。`tasks/official_scripts.py` 的阶段事务与平台同案例选择由 `test_task_configuration.py` 覆盖故障恢复与模型差异。

## WDNO最新公共约定补验（2026-09-17）

WDNO使用现有公开new/fork/submit/resume/compare和CLI；task_management.py实跑复制品消费及中断恢复，test_wdno_task_assets覆盖；不修改Task通用实现，平台可选操作不新增。 当前结果以 `.context/mvp/wdno-acceptance.md` 为准。

## 安装资源与案例门面

- `templates/resources.py`：清单读取、standalone 检查/复制、extension base-plus-overlay 物化、provenance、Agent Help Center 检索/读取/导出、guide/skill 导出、源码定位和显式 smoke 数据生成；除 smoke 数据函数外不 import 案例或训练栈。
- `cli/resources.py`：`guide search/topic/symbol/export`、`source`、`example list/copy/check/smoke-data create` 的薄解析层；CLI 不是研究入口。
- `build_hook.py`：把清单允许的 examples、guide、skill 和完整 `docs/agent-help` 构建副本收入 wheel，排除 recipes、.context、缓存和开发路径。
- `case-manifest.json`：仅有 standalone/extension 两类，verification 是证据字段，不是发布状态。
- `docs/agent-help/manifest.json` 与 `indexes/`：帮助合同、主题、符号、案例和源码位置；由 `tools/docs/build_agent_help.py` 使用 AST 和 Markdown 元数据生成并用 `--check` 核对漂移。
- 长期行为见 `docs/PRD/ai4e-task/templates/PRD.md` 与 `docs/PRD/ai4e-task/cli/PRD.md`；圈定覆盖和 wheel 证据见 `../mvp/agent-help-acceptance.md`。

- `tasks/assets.py`：输入槽改绑后重新匹配当前共享资产，保留新准备的依赖闭包及 bundle；覆盖 `test_task_assets.py::test_rebound_shared_bundle_survives_fork`，GeoTransolver 真实复制见 `.context/mvp/geotransolver-acceptance.md`。

- `docs/agent-help/capabilities/`：九类能力的输入输出、真实调用例子和边界；教程元数据生成 skill/GUIDE/帮助首页菜单。`tests/integration/test_agent_capabilities.py` 覆盖链接、符号、九例实跑、查询及离线导出；验收见 `.context/mvp/agent-capabilities-acceptance.md`。
