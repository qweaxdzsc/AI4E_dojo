---
name: dojo-research
description: 使用 Dojo 已有数据处理、训练恢复、推理评价和后处理能力开展研究；支持单个工具、已有 PyTorch 代码和完整案例三种接入。
---

# Dojo 研究工作流

Dojo 提供可组合的研究工具。先在下面选择需要的能力，直接打开对应教程；不必先猜关键词，也不必为了调用一个函数复制完整案例。本 skill 负责行动路由，API 和可执行例子的唯一详细正文在 [Dojo Agent Help Center](../../../docs/agent-help/index.md)。

## 已有能力：按要完成的工作直接进入

<!-- capability-menu:start -->
- **[数据读取、预处理与归一化](../../../docs/agent-help/capabilities/data.md)**：读取、字段提取、身份校验、筛选、保存、统计及正反归一化。主题 `capability:data`。
- **[几何与采样](../../../docs/agent-help/capabilities/sampling.md)**：网格、坐标、法向、距离和一致采样，保留实体身份。主题 `capability:sampling`。
- **[网络与模型组件](../../../docs/agent-help/capabilities/model.md)**：构造普通网络，复用网络模块并检查参数与输入输出。主题 `capability:model`。
- **[损失与物理约束](../../../docs/agent-help/capabilities/loss.md)**：监督项、权重、可微比较和自定义物理残差。主题 `capability:loss`。
- **[训练、优化与恢复](../../../docs/agent-help/capabilities/training.md)**：已有模型接入训练循环、调度、梯度累积、检查点及恢复。主题 `capability:training`。
- **[推理与多步滚动](../../../docs/agent-help/capabilities/inference.md)**：无梯度推理、模式与随机状态保护、滚动预测和设备同步计时。主题 `capability:inference`。
- **[评价与误差指标](../../../docs/agent-help/capabilities/evaluation.md)**：具名样本、物理帧和字段的 FP64 误差，显式定义聚合。主题 `capability:evaluation`。
- **[后处理、图表与结果导出](../../../docs/agent-help/capabilities/post.md)**：固定预测读回、误差曲线、物理场图、差值和网格导出。主题 `capability:post`。
- **[运行记录与 Task 管理](../../../docs/agent-help/capabilities/run-task.md)**：direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较。主题 `capability:run-task`。
<!-- capability-menu:end -->

## 选择接入深度

1. **只复用一个工具**：读对应能力教程，核对 API，直接传普通数组、张量或对象调用；验证结果即可，不要求创建 Task、配置树或 standalone。
2. **已有 PyTorch 模型和研究代码**：优先检查训练分支的 `train_model`、数据变换、推理和评价是否能直接连接。保留网络与科学目标，只写必要的批次/损失适配；需要运行记录时用 `ai4e_core.run.launch` 和 `TrainingRun`。已有循环只缺局部能力时不用整体迁移。
3. **需要一条完整领域流程**：通过 `list_examples/check_example/copy_example` 选择完整 `standalone`；`extension` 必须物化 `base_case`。在仓库外阅读 README、配置、pipeline 和相关阶段正文，先 direct-core，按需再接同目录 Task。

新模型正式集成属于仓库开发，使用可用的 `dojo-integrate-model`；普通研究中的自定义网络无需自动升级为框架集成任务。

## 何时优先复用，何时自己实现

在重写数据处理、训练、恢复、推理或后处理前，先读对应分支的小例子。若输入输出、数值定义、设备和恢复语义相容，优先复用现有能力；只差字段或轴时写局部转换。若存在具体的科学语义、性能或接口缺口，允许自定义并简短记录缺口及验证结果。不要因为搜索没命中就断言 Dojo 没有该能力，也不要为“使用框架”改变实验目标或强制接入全部组件。

选用框架训练装配后，继续复用其循环、writer、检查点及 worker；研究差异通过 objective、batch、update 等公开连接表达。不得另复制一份管理实现，也不得读取私有会话字典。

## 定位及按需核对

```python
import ai4e_task as task
print(task.help_info())
print(task.read_help_topic("capability:training")["content"])
api = task.describe_help_symbol("ai4e_core.applications.base.iteration_training.train_model")
print(api["signature"], api["source_path"])
```

调用前明确签名、输入轴/单位、返回值、副作用、稳定性及当前版本源码；能力教程提供小例子，完整领域交接再读案例。帮助与安装签名不一致时报告漂移，以当前安装源码为准。`search_help` 用于进一步细查，不是发现能力大类的前置步骤。

其他帮助：`getting-started` 安装定位；`concepts` 层次边界；`workflows` 领域流程；`api` 签名；`user-components` 自定义连接；`examples` 案例；`troubleshooting` 故障；`reference` 配置/阶段/产物合同。离线读取 manifest 与 indexes；CLI 只是 Python API 的可选包装。

## 按需管理和交付

- Task：`ai4e_task.create_project/new_task/submit_run/wait_run`；按需 stop_run、resume_run、fork_task、compare_runs。使用 Task 时等待终态并核对实际产物。
- 配置：read_configuration 后带 revision 保存；临时覆盖用 submit_run(overrides=[...])。普通函数不要求采用官方配置树。
- 独立阶段按已选择案例使用 `inputs.<stage>.<name>`，运行与数据分别用 `run_root`、`data_root`；纯能力通过普通返回值交接。
- 验证实际调用、输入输出、数值和产物读回；恢复须验证状态，post 只消费固定预测。改变结构、字段、数据身份或更新策略时检查旧 checkpoint 兼容性。
- 区分工程接线、状态/预测一致性、学习效果和论文精度，保留失败、重试及恢复来源。读取文档不等于实际使用 Dojo。
