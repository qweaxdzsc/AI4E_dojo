# GenCP 缩小实验接入验收

当前状态：2026-09-16，六组缩小实验接入与圈定验收完成。用户明确授权每组参考程序与 Dojo 合计三小时内的缩小实验；此范围不改变通用集成 skill 的完整论文复现目标。工程迁移通过，论文精度复现未完成。

## 范围与输入

原仓库 `/Users/zonghui/work/new_code_project/GenCP`，提交 `1b0522338cf139b615e1395e8e9da82d3edabbe9`；源码摘要随 contrib 模型保存。论文为 arXiv 2601.19541v1，表 2–4。完整论文配置保留于六例 source-config.yaml。

三个数据集完整物化在 `/Users/zonghui/work/project_simulation/dojo_train/gencp/raw`。原数据只读；缺失的 NTcouple 与 Double Cylinder 文件从官方 Google Drive 恢复，逐文件 SHA256 与此前 ZIP 审计核对。FSI 原统计量来源未独立重算，核热没有额外逐行物理 ID，以官方行号/帧号配对。

六例保留原网格、时间窗口；每场 256 训练、16 单场及耦合验证、batch 2、FP32、1,000 次更新。CNO 两层、倍率 4、瓶颈残差 1、提升投影 16；SiT hidden 64/depth 2/heads 4/modes 4，patch 依案例为 8×8、6×8、4×2。FSI 耦合 10 步；NT 耦合 100 步，单场 100 网格点/99 次积分更新。

## 实验语义与差异

- 参考入口提取原 Trainer 的 train_step/sample 和原耦合函数，原模型类独立导入，不调用 Dojo 数值计算。绕过缺失但未使用的 FNO 导入；NT 推理修复缺失 print 语法，数据白名单加入实际 decouple_train/val。原仓库不修改。
- FSI 保留当前 Jacobi 同步更新；原 Lie 分支通道错误不作为基线。核热按中子→固体→流体，主入口中子边界回填开启；边界依赖真值明确记录。
- 优化器沿用源码 Adam，NT betas 0.9/0.99，FSI 0.9/0.999；cosine 终点改为缩小预算 1,000，是本实验显式缩小。主权重做最终对照，EMA 参数平均、缓冲复制另行比较。
- 缩小实验使用 seed=42 的独立 CPU 批次排列发生器，训练样本从原分片固定抽取；原模型和训练单步保留。这不是原 Trainer 完整训练调度的逐字运行。验证隔离训练随机流，固定 16 样本。FSI 流体 u、结构 SDF 单场物理指标选优；核热分量分别评价后平均。单场最佳不能替代耦合最佳。
- 论文与源码的优化器/调度、CNO 倍率/激活、patch、FSI 顺序分裂仍有协议差异。当前不能宣称论文最终训练配置已恢复。原 autoregressive 函数不推进历史，不宣称长时间预测。

论文目标（相对 L2 比值）：Turek CNO u/v/p/SDF 为 .0388/.1821/.2166/.0183，SiT 为 .0396/.1678/.1897/.0081；Double CNO .0279/.1150/.6208/.0055，SiT .0522/.2397/.3987/.0061；NT CNO neutron/fuel/fluid .0044/.0105/.0330，SiT .0085/.0364/.0270。来源 https://arxiv.org/html/2601.19541v1 。完整训练、其他论文基线与消融不在本轮范围。

## 代码与验收入口

- `packages/ai4e-core/applications/coupled_physics/{contracts,rawprep,trainprep,model,train,infer,post}.py`：局部领域交接。
- `packages/ai4e-contrib/ability/**/gencp/`：网络、条件、边界、变换、目标、参考处理。
- `packages/ai4e-contrib/application/{datasets,coupled_physics}/gencp/`：数据描述、配置与能力连接。
- `recipes/gencp/`：独立阶段、单场、耦合和 post；`examples/gencp/` 六例；`examples/recipe_extensions/gencp/` 条件替换与速度输出。
- `tools/verification/gencp/reference.py` 独立源码；`budget.py` 同组累计与终止；`compare.py` 明确运行的权重、EMA、损失、单场、耦合与逐分量误差。
- 圈定测试：`uv run pytest tests/integration/test_gencp*.py`，以及能力文档、原训练循环/检查点、原推理状态与固定用户公开 API/安装用例。skip 不计通过。

公开 API 增量：`TrainingRun.checkpoint(label, payload, *, namespace=None)` 与 writer 对应入口，返回仍为实际 Path；旧默认路径不变。namespace 只能为安全单段名称，非法值 ValueError。新分场检查点位于 `checkpoints/<field>/`；旧 epoch 检查点不能被视为精确 iteration 恢复。不改历史基线摘要。

## 实际证据（持续更新）

运行产物根 `/Users/zonghui/work/project_simulation/dojo_train/gencp/`。每组独立 reference、dojo、budget.json 与 comparison.json。账本包含恢复/失败重试，不能把失败输出当成功。

六组均完成每场 1,000 次更新。原与 Dojo 的损失序列、全部主权重、EMA 和单场预测逐值一致；两个 FSI 案例的耦合物理预测逐值一致，NT 耦合反变换有 FP32 舍入差且在已冻结容差内。所有逐物理量相对 L2 均满足不高于参考 1.05 倍的门槛。

累计账本包含原参考、Dojo、失败重试、评价、准备/恢复补记，并向每组保守重复计入 10 分钟共享工程验证预留；预留不是实测训练时间。六组均小于三小时：双圆柱 CNO **113.42 分钟**、双圆柱 SiT **22.77 分钟**、Turek CNO **77.22 分钟**、Turek SiT **19.83 分钟**、NT CNO **49.61 分钟**、NT SiT **31.78 分钟**。明细见实验根 `budget-credit.json` 及每组 `budget.json`，没有清除失败或重置账本。

最终 **107 项通过，0 失败、0 跳过**：101 项工程/兼容集合加显式开启的六组真实结果门禁。`engineering-tests.xml` 与 `scientific-tests.xml` 保留两次实际执行，合并索引为 `targeted-tests.xml`。新增代码的圈定 Ruff 检查与格式检查通过，上游保留算术的网络文件按精确目录排除自动改写。

完整物理指标、训练前后验证变化、明确运行目录、环境与边界见 [实验报告](/Users/zonghui/work/project_simulation/dojo_train/gencp/report.md)。同目录提供 `summary.json`、`source-manifest.json`、`source-snapshot.zip` 和三个实际构建的 wheel。双圆柱 CNO 最终运行 `2026-09-16T16-24-16_f357e8`，包含完整训练、单场、耦合与 post。

Turek CNO 原 Dojo 训练运行 `2026-09-16T15-19-33_78a207` 完成两场各 1,000 次；现验收运行 `2026-09-16T16-02-15_67d03d` 从完整检查点恢复，执行 0 次新更新，重新验证、生成与 post。原训练和恢复均计入账本，保留完整损失与权重，不以恢复运行的短时长替代总预算。

固定验证误差训练前后均改善，但耦合物理误差仍明显高于论文。NT 原始数组为 float64，FP32 训练与物理反变换有小量舍入差；比较保留原始真值并采用已冻结容差，不把归一化往返数值当成原始真值。

## 功能—测试对应

测试按共同夹具合并为八个文件，没有按计划叶子机械拆出空壳模块：

- A 数据、时空变换：`test_gencp_abilities.py` 的原生切片/端点/轴/常量；`test_gencp_reference_alignment.py` 对四组真实 FSI 分片和六组 NT 单场/耦合分片逐值读取对照；`test_gencp_contracts.py` 拒绝身份与时间错配。
- B 目标、网络和训练：`test_gencp_reference_alignment.py` 固定随机量目标/条件/更新；`test_gencp_models.py` 两骨干各场真实前向、梯度和单场生成；`test_gencp_contracts.py` 对照 CPU 和真实 MPS 网络连续/恢复的权重、优化器、EMA、学习率、游标、历史和随机状态。
- C 耦合：`test_gencp_abilities.py` 的解析同步/顺序系统和模型组模式/RNG；`test_gencp_reference_alignment.py` 原条件映射及边界；`test_gencp_contracts.py` 真值非边界隔离、取消/非有限值、替换权重和不兼容准备拒绝。
- D 固定结果：`test_gencp_results.py` 数组摘要与保存读回；`test_gencp_contracts.py` 原 mask/平滑、轴和分量归约；安装用例在取消准备和权重配置后独立 post。
- E 真实研究扩展：`test_gencp_installation.py` 构建安装三个 wheel、仓库外复制、真实 NT CPU 短训练、流体学习率修改、条件替换、速度模长保存读回和评价；另只重训流体并保留其他场固定权重，重新耦合生成与 post，原组不被覆盖。
- F 累计预算和六组结果：`test_gencp_results.py` 失败、缺命令与超时计账；显式 `DOJO_GENCP_ACCEPTANCE=1` 的 `test_gencp_acceptance.py` 检查六份真实对照/学习报告、1,000 次更新与未超过三小时。未设置环境的 skip 不算验收。

兼容回归圈定原训练循环、检查点、post/inference、固定公开 API 实际安装、能力清单和架构文档。最终组合结果、累计时长与测试 JUnit 与 `report.md` 一并保存在实验根；未运行 CUDA，不把 CPU/MPS 结果推广为 CUDA 验收。较早五组结果已保存物理帧索引，最后双圆柱 CNO 还保存 HDF5 实际空间坐标与时间值；元数据增补不改变数值算法。

## 2026-09-17：Task 入口补验未通过

此前验收为直接 Python recipe 和安装复制，不包含 Task。此次使用已安装公开 API 与原样模板，六组均可 new_task 创建空 entry 任务；训练、推理、post 共十八次 submit_run 均在启动前报 `entry_required: task-entry.json`。另六次携带 configuration 新建均报 `entry_required_for_configuration`；没有计算运行启动。

模板缺少 Task 入口声明，阶段选择、输入输出绑定与跨阶段引用尚待接入和真实验收。不能将历史六组算法对照解释为 Task 可用。本次只复核并记录缺项，未新增适配。实际脚本、任务项目及逐项结果见 [复核报告](/Users/zonghui/work/project_simulation/dojo_train/gencp/task_probe_20260917/report.md)。

本次圈定 Task 通用回归 `test_task_management.py`、`test_task_execution.py`：7 项通过、无失败或跳过；GenCP 自身十八次提交失败仍按失败记录，两者不合并为通过。

### 同日原因隔离（未实施正式适配）

仅在仓库外副本补声明，原 post.py 已经 Task 成功执行，固定结果指标与直接运行完全一致，Python 源码未改。总入口的 `only=[pipeline]` 在检查模式覆盖了 train 请求并进入全部阶段；仅绑定 run_root 时 paths.output 仍为外部路径。证据见 [诊断报告](/Users/zonghui/work/project_simulation/dojo_train/gencp/task_diagnosis_20260917/report.md)。这缩小了问题范围，不撤销原模板 Task 缺项结论；训练、推理和恢复尚未在 Task 实跑。
