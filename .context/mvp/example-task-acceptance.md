# Example / Task 资源与 Agent 工作流验收

## 已验证

- 清单包含 21 个 `standalone` 与 10 个 `extension`，没有第三种案例类型或状态；新增的 MeshGraphNet 外流案例沿用同一 contract 和帮助索引。
- 每个 standalone 的 required files、README、contract、阶段入口和路径污染门禁通过。
- `uv build packages/ai4e-task --wheel` 成功；wheel 包含完整清单、案例、guide 与 skill，未包含 `recipes/`、`.context` 或缓存。
- wheel 外部安装后，`list`、`check`、standalone 复制、extension base-plus-overlay 物化、provenance、guide export 和源码定位通过；guide export 未创建 `AGENTS.md`。
- Agent 入口关系已固化：支持 Agent Skills 时以 `dojo-research/SKILL.md` 为主入口并按需读取 guide；不支持 skills 时以 guide 为主入口；两者都继续读取具体 standalone README 和清单记录。
- 安装 guide 已补齐可执行 Python API：资源发现/复制、`run.launch`/`run.stage`/`TrainingRun`、领域 application 定位、Task new/submit/wait/stop/resume/fork/compare、配置 revision、固定产物和错误边界；skill 明确要求 Agent 在运行前指出实际函数、输入、返回值和读回产物。
- Neumann 外部 wheel 复制目录显式生成 train 2 / test 1 / 7×7 CPU 数据；direct-core 完成 rawprep、trainprep、1 轮短训、infer、post，随后用真实准备记录和 `latest.pt` 恢复到第 2 轮。运行摘要、检查点、预测和指标均成功读回。
- 同一 2/1、7×7 复制目录通过 `ai4e_task` Python API 分阶段完成 preparation、两轮 train、从第一轮 `best.pt` 恢复到第二轮、独立 infer 和独立 post。恢复固定第一次 preparation，未重新执行 trainprep；终态均为 `succeeded`，并读回 `last.pt`、`predictions.json`、post `metrics.json` 与 summary。
- 定向测试覆盖 `test_example_contract.py`、`test_example_task_runs.py`、`test_example_core_runs.py`、Task 管理/资产/执行/合同、资源门面、帮助覆盖与 recipe extension；当前合并结果和显式 smoke 见 `agent-help-acceptance.md`。资源与帮助测试使用隔离 wheel 路径，并断言静态查询不加载训练栈。
- `test_task_recipe.py::test_formal_recipe_new_fork_train_post` 已按现行资产契约更新：带共享数据和统计绝对引用的 preparation 明确拒绝单文件复制，派生任务保留引用；无外部依赖的检查点允许显式复制。该修复不放松 `asset_copy_not_portable` 门禁。
- 修复后圈定回归：正式 recipe、Task 资产、数组 bundle 与 Agent 资源契约共 13 项通过；API guide 修订后的源码契约 7 项通过，新建 `ai4e-task` wheel 安装到独立目录后的资源门面与公开 API 存在性 6 项通过。当前 `.venv` 未重装，不把独立安装证据写成正式安装副本已更新。

## 未宣称

本记录不宣称 21 个案例都完成真实数据训练，也不宣称论文级精度、生产预算或 Web 验收。Neumann smoke 只证明公开入口、参数接线、固定 preparation、Task 恢复和产物交接；其他案例数值实跑仍需在各自依赖和数据准备齐全后按清单追加证据。

## 2026-09-22 公开案例配置与安装资源一致性

源码清单现为 41 个案例（27 standalone、14 extension）。九个 aero_cfd 配置已统一把原始输入、已处理数据、数据产物和运行记录放在复制目录的 `../inputs`、`../datasets`、`../data/<case-id>`、`../runs/<case-id>`，并保留源码已支持的 `infer.seed`。配置回归不再首错停止，会汇总全部公开 aero 案例并检查四类路径、领域默认值及 seed 透传。

本轮新建的 Task wheel 在仓库外安装后，完整比较源码与安装后的 41 个案例 ID，逐例 `check_example`，并实际复制全部 standalone/extension 到空目录；安装测试 1 项通过。生成 Help 已两次按并行源码变化重建，最终 `--check` 为 492 个生成文件无漂移，帮助/能力/Task 文档组 20 项通过。

当前主 `.venv` 的 Task 安装副本仍少 `pcno.double_cylinder`、`aero_cfd.shapenet_car_geotransolver`、`aero_cfd.nasa_crm_geotransolver`，旧 Core 安装副本仍拒绝两个 GeoTransolver 的 `infer.seed`；这些正是未发布证据，不以隔离 wheel 通过掩盖。主环境重装和正式 Web 冒烟待单独授权。

并行 Task 源码随后新增了对现行 Spec `task_operations` 的公开导入；只安装新 Task wheel、复用主环境旧 Spec 的能力测试因此明确失败。四个现行 Spec/Core/Contrib/Task wheel 一起安装的本轮交付测试仍通过，说明失败属于主安装副本版本混用，不能据此省略完整重装。
