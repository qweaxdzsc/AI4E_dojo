# AI4E Dojo Agent 启动指南

Dojo 已有数据处理、训练恢复、推理评价和后处理工具。**先选下面的能力分支，直接阅读可执行例子；不用先猜搜索词。** 可以只用一个工具，也可以保留自己的 PyTorch 模型并接入训练装配，或复制完整案例。

本页是无 Agent Skills 环境的启动入口；支持 skills 时使用 `dojo-research`。详细 API、输入输出和边界统一维护于 [Dojo Agent Help Center](docs/agent-help/index.md)。

## 现有能力与直接入口

<!-- capability-menu:start -->
- **[数据读取、预处理与归一化](docs/agent-help/capabilities/data.md)**：读取、字段提取、身份校验、筛选、保存、统计及正反归一化。主题 `capability:data`。
- **[几何与采样](docs/agent-help/capabilities/sampling.md)**：网格、坐标、法向、距离和一致采样，保留实体身份。主题 `capability:sampling`。
- **[网络与模型组件](docs/agent-help/capabilities/model.md)**：构造普通网络，复用网络模块并检查参数与输入输出。主题 `capability:model`。
- **[损失与物理约束](docs/agent-help/capabilities/loss.md)**：监督项、权重、可微比较和自定义物理残差。主题 `capability:loss`。
- **[训练、优化与恢复](docs/agent-help/capabilities/training.md)**：已有模型接入训练循环、调度、梯度累积、检查点及恢复。主题 `capability:training`。
- **[推理与多步滚动](docs/agent-help/capabilities/inference.md)**：无梯度推理、模式与随机状态保护、滚动预测和设备同步计时。主题 `capability:inference`。
- **[评价与误差指标](docs/agent-help/capabilities/evaluation.md)**：具名样本、物理帧和字段的 FP64 误差，显式定义聚合。主题 `capability:evaluation`。
- **[后处理、图表与结果导出](docs/agent-help/capabilities/post.md)**：固定预测读回、误差曲线、物理场图、差值和网格导出。主题 `capability:post`。
- **[运行记录与 Task 管理](docs/agent-help/capabilities/run-task.md)**：direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较。主题 `capability:run-task`。
<!-- capability-menu:end -->

## 按你已有的工作选择路线

- **已有数组、模型或预测，只需局部工具**：打开对应分支，核对签名后直接调用，不要求 Task 或完整案例。
- **已有 PyTorch 训练任务**：先读训练分支，保留自己的模型、科学目标和数据；通过 batch/objective 接入共享训练与恢复，也可仅采用需要的局部能力。输入、数值或性能不适配时明确记录缺口，不强行套模板。
- **从完整案例开始**：选择 standalone；extension 通过 copy_example 物化基案例。阅读 README、配置、pipeline 与阶段脚本，在独立目录修改并先用 `ai4e_core.run.launch` 直接运行。需要版本、资产、后台运行、停止、恢复或比较时再使用同目录 `ai4e_task`。

复用前核对输入输出、单位/轴、设备及状态恢复语义；适配成本小且语义一致时优先复用。只有具体缺口需要新实现，不能仅因为搜索无结果就判断能力不存在。是否使用及使用范围服从用户任务，不强制全部框架组件。

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

安装定位看 getting-started；层次职责看 concepts；领域流程看 workflows；API 签名看 api；用户扩展看 user-components；完整案例看 examples；错误看 troubleshooting；配置键、阶段输入、产物与稳定性看 reference。也可离线读取 manifest.json 和 indexes 下的机器索引。

Python 决定流程，YAML 只提供所选案例的参数。普通函数无须统一基类；跨独立阶段沿用案例 inputs、run_root 和 data_root 合同。权重初始化与完整恢复分开；post 消费固定结果。实际运行和数值读回才证明使用生效，导入成功或读过指南不代表训练框架已使用。CLI 是可选便利入口。
