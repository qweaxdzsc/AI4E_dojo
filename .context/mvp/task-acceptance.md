# Task 本地切片验收（2026-09-09）

## 交付范围

- `ai4e-task` 可安装包及 `ai4e`/`python -m ai4e_task`；六类代码目录，无 DDD 分层。
- 项目、模板、new/fork、单父正式版本树、创建快照与工作目录／运行比较。
- `tasks/<task_id>` 内代码、运行、数据与私有资产；项目 shared 按名称登记内容和来源。
- 数据集／准备产物／检查点复制开关独立，默认引用；复制后更新输入配置；父运行输出按 produced_assets 声明复制到 copied_outputs，保留依赖且不自动加载。显式共享运行产物。
- 本地进程提交、等待、停止、恢复、启动失败、待核对状态与运行导入冲突检查。
- spec `RunContext` 与 core `managed_run`，writer 原子来源及摘要，旧独立入口兼容。

## 执行结果

**62 通过，2 跳过，0 失败**：相关回归 60 通过／2 跳过，wheel 安装 1 通过，Task 文档 1 通过。相关源码 Ruff 检查与格式检查通过。

跳过的是 `test_mps_checkpoint_replays_random_sequence` 和 `test_mps_train_then_complete_mesh_query`；本环境不可访问真实 MPS，不视为硬件验收。

正式案例使用生成的小网格和正式贡献 AB-UPT 的合法小网络配置，CPU 执行一轮：new → datapre/trainprep/train/post → fork 复制数据集并修改学习率 → 第二次四阶段 → 标量比较与共享权重。两次运行成功，两个正式版本，输出独立。不是 889 样本规模验收或新的数值等价性结论。

## 测试与证据

- `tests/integration/test_task_management.py`：创建、当前编辑、多根血缘、幂等及并发、复制失败、路径门禁。
- `tests/integration/test_task_assets.py`：共享引用／复制、内容变化、三类复制开关和输入更新。
- `tests/integration/test_task_execution.py`：执行快照隔离、版本不变、失败停止、待核对、导入冲突。
- `tests/integration/test_task_contracts.py`：共享身份、快照变更拒绝、恢复采用捕获代码、CLI、不可比单位、创建中断清理。
- `tests/integration/test_task_recipe.py`：正式模型四阶段 new/fork 本地闭环。
- `tests/integration/test_task_installation.py`：源码目录之外的新虚拟环境，四个产品包从 wheel 安装；第三方依赖复用现有环境。Python/CLI 路径核对、new/fork 和真实 core 托管运行通过。未使用源码 PYTHONPATH 执行已安装包。
- `tests/integration/test_task_documents.py`：六类 PRD、入口声明和文档存在性。
- `task-results/acceptance.json`：测试计数、跳过节点、源码及 wheel 摘要。
- `task-results/related.xml`、`installation.xml`、`documents.xml`：原始 JUnit 结果。
- `task-results/formal-recipe.json`：两次正式模型运行摘要、来源及检查点清单。

## 复验入口

先同步本地包；当前 Hatchling 单层映射安装的是副本，源码变更后必须重建安装，避免误用旧副本。验收时已经核对 task/core/spec 安装文件与源码一致。

```bash
uv sync --inexact --reinstall-package ai4e-task --reinstall-package ai4e-core --reinstall-package ai4e-spec --reinstall-package ai4e-contrib
uv run pytest tests/integration/test_task_management.py tests/integration/test_task_assets.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py tests/integration/test_task_recipe.py tests/integration/test_task_documents.py
uv run pytest tests/integration/test_train_resolved_config.py tests/integration/test_train_code_snapshot.py tests/integration/test_recipe_logging.py tests/integration/test_recipe_three_stage.py tests/integration/test_train_checkpoint.py tests/integration/test_post_inference.py tests/integration/test_post_mesh.py tests/integration/test_abupt_recipe.py tests/integration/test_web_design_documents.py
uv run pytest tests/integration/test_task_installation.py
```

安装用例默认自行构建 workspace wheel；也可通过 `DOJO_TASK_WHEELS` 指定刚构建、已核对的 wheel 目录。本次构建在 `/tmp/dojo-task-wheels`，未发布 PyPI。

## 当前边界

- 本地进程适配针对 macOS/Linux；无远程队列、批量计划或 Web/Server 实现。
- 工作目录使用显式输入输出声明；自定义代码新增路径需要同步声明。
- 符号链接不作为复制资产；准备文件内引用的依赖不会通过猜测重写，使用前由显式输入与 core 契约验证。
- 项目内记录使用相对定位，但 recipe 中既有绝对输入引用不会在目录迁移后自动修复。
- 数据库仍需备份；运行导入只恢复运行索引，不伪造未执行任务。

## 最终入口与复制复查

工作区并行更新已移除旧 pre 入口并统一 pipeline 到 datapre，保留该更新。三个相关入口用例再次通过。随后补齐父运行已生成的准备产物／检查点复制与创建差异清单，Task 的 13 个用例再次全部通过；原始结果见 task-results/entry-refresh.xml 和 task-results/task-final.xml。
