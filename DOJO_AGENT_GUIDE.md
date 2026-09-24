# AI4E Dojo Agent 启动指南

本指南说明 Dojo **有什么、适合做什么、从哪里读**。研究行动顺序由 [dojo-research Skill](.agents/skills/dojo-research/SKILL.md) 说明；不支持自动加载 skills 的环境也可直接阅读该文件。详细 API、输入输出和例子统一维护于 [Dojo Agent Help Center](docs/agent-help/index.md)。

Dojo 提供可复制的完整研究案例、可替换的基础工具和可组合训练框架。完整案例包含配置、pipeline 与阶段交接；自有 PyTorch 网络、数据适配和科学目标可以通过[用户组件](docs/agent-help/user-components/overview.md)连接，保留框架的迭代更新、验证、检查点与恢复。完整新任务如何选例、复制和改写由 Skill 指明；已有单工具需求也可独立调用。Task 提供可选管理功能。

## 现有能力与直接入口

<!-- capability-menu:start -->
- **[数据读取、预处理与归一化](docs/agent-help/capabilities/data.md)**：读取、身份校验、保存、统计、正反归一化及普通拟合状态读回。主题 `capability:data`。
- **[几何与采样](docs/agent-help/capabilities/sampling.md)**：网格、坐标、法向、距离和一致采样，保留实体身份。主题 `capability:sampling`。
- **[网络与模型组件](docs/agent-help/capabilities/model.md)**：经典网络、DeepONet/FNO 与传统代理模型；按 block、可复用阶段和完整架构组合。主题 `capability:model`。
- **[损失与物理约束](docs/agent-help/capabilities/loss.md)**：监督项、权重、可微比较和独立于模型的物理残差。主题 `capability:loss`。
- **[训练、优化与恢复](docs/agent-help/capabilities/training.md)**：神经网络优化与恢复，以及 POD、RSM/RBF、Kriging、LightGBM 非梯度拟合。主题 `capability:training`。
- **[推理与多步滚动](docs/agent-help/capabilities/inference.md)**：神经网络执行上下文、普通对象分批预测、多步滚动和设备同步计时。主题 `capability:inference`。
- **[评价与误差指标](docs/agent-help/capabilities/evaluation.md)**：具名样本、物理帧和字段的 FP64 误差，显式定义聚合。主题 `capability:evaluation`。
- **[后处理、图表与结果导出](docs/agent-help/capabilities/post.md)**：固定预测读回、误差曲线、物理场图、差值和网格导出。主题 `capability:post`。
- **[运行记录与 Task 管理](docs/agent-help/capabilities/run-task.md)**：direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较。主题 `capability:run-task`。
<!-- capability-menu:end -->

## 新增基础模型从哪里进入

[建模能力](docs/agent-help/capabilities/model.md)覆盖 MLP、CNN、ResNet、U-Net、Transformer、GNN、RNN、DeepONet、FNO，以及 POD、RSM、RBF、Kriging、LightGBM，按计算 block → 可复用阶段 → 完整架构给出公开 API、替换点和案例入口。这是 core modeling 内的组合尺度。

神经网络优化和传统模型非梯度拟合共同从[训练能力](docs/agent-help/capabilities/training.md)分流；普通对象走[分批预测](docs/agent-help/capabilities/inference.md)与[拟合状态保存/重建](docs/agent-help/capabilities/data.md)。POD 需连接系数预测器；物理损失属于独立[约束能力](docs/agent-help/capabilities/loss.md)，不另设 PINN 模型。

## 接口覆盖范围

- **基础工具**：普通数组、张量和对象可调用，单工具不依赖完整案例或 Task。
- **模型权重**：[初始化、冻结参数与权重键映射](docs/agent-help/api/core/abilities/modeling/weights.md)有独立工具；训练分支另提供完整状态恢复。结构专属的参数变换由研究连接表达。
- **训练装配**：训练分支覆盖 `train_model`、迭代与 epoch 路线；研究者提供模型、损失、批次和必要局部策略。运行分支介绍 `ai4e_core.run.launch` 与 `TrainingRun`。
- **完整案例与变体**：`standalone` 是完整目录；`extension` 通过 `copy_example` 物化基案例。案例包含 README、配置、pipeline 和步骤。案例名不是能力边界：可保留流程，替换网络、读取、采样、目标或局部更新组件，具体连接见[用户组件总览](docs/agent-help/user-components/overview.md)。

案例列表提供 `research` 基础说明（用途、数据形态、训练机制、替换点与限制），支持 `list_examples(query=..., data_form=..., training_pattern=...)` 筛选。`read_help_topic("case:<案例ID>")` 包含由 README 生成的详细正文；复制结果的 `documentation.entry` 指向本地完整说明，extension同时交付基案例与变体说明。选择和改写顺序仍由Skill说明。
- **边界**：某个通用工具存在不代表覆盖所有科学协议；字段、轴、设备、性能、恢复及默认值以当前 API 与实际验证为准。

## 定位当前安装的资料

```python
import ai4e_task as task
info = task.guide_info()
print(info["help_entry"], info["help_manifest"], info["examples"])
print(task.read_help_topic("capability:training")["content"])
api = task.describe_help_symbol("ai4e_core.applications.base.iteration_training.train_model")
print(api["signature"], api["source_path"])
```

需要离线资料时调用 `task.export_guide("./dojo-help")`，一并导出指南、skill 和完整帮助，保持链接有效。只导出帮助正文可以用 export_help。`search_help` 用于分支内部进一步查找，不是发现能力的前置步骤；帮助读取与搜索不加载模型或训练栈。

## 其他帮助与使用边界

安装定位看 getting-started；层次职责看 concepts；领域流程与 recipe 看 workflows；API 签名看 api；用户扩展看 user-components；完整案例看 examples；错误看 troubleshooting；配置键、阶段输入、产物与稳定性看 reference。也可离线读取 manifest.json 和 indexes 下的机器索引。

Python 决定流程，YAML 只提供所选案例的参数。普通函数无须统一基类；跨独立阶段沿用案例 inputs、run_root 和 data_root 合同。权重初始化与完整恢复分开；post 消费固定结果。实际运行和数值读回才证明使用生效，导入成功或读过指南不代表训练框架已使用。CLI 是可选便利入口。
