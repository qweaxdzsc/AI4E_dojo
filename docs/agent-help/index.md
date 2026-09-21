<!-- dojo-help: {"artifacts": ["summary.json", "assets.json", "metrics.json"], "domain": "all", "kind": "entry", "layer": "help", "summary": "研究 Agent 查找公开 API、工作流、组件写法和完整案例的唯一帮助正文。", "tasks": ["研究起步", "API 检索", "案例选择"], "title": "Dojo Agent 帮助中心", "topic_id": "agent-help:index"} -->
# Dojo Agent 帮助中心

先按要完成的工作选择下面的能力分支。每个分支给出现有 API、输入输出、可执行小例子和适用边界；不知道函数名也能直接进入。

## 能力直达

<!-- capability-menu:start -->
- **[数据读取、预处理与归一化](capabilities/data.md)**：读取、字段提取、身份校验、筛选、保存、统计及正反归一化。主题 `capability:data`。
- **[几何与采样](capabilities/sampling.md)**：网格、坐标、法向、距离和一致采样，保留实体身份。主题 `capability:sampling`。
- **[网络与模型组件](capabilities/model.md)**：构造普通网络，复用网络模块并检查参数与输入输出。主题 `capability:model`。
- **[损失与物理约束](capabilities/loss.md)**：监督项、权重、可微比较和自定义物理残差。主题 `capability:loss`。
- **[训练、优化与恢复](capabilities/training.md)**：已有模型接入训练循环、调度、梯度累积、检查点及恢复。主题 `capability:training`。
- **[推理与多步滚动](capabilities/inference.md)**：无梯度推理、模式与随机状态保护、滚动预测和设备同步计时。主题 `capability:inference`。
- **[评价与误差指标](capabilities/evaluation.md)**：具名样本、物理帧和字段的 FP64 误差，显式定义聚合。主题 `capability:evaluation`。
- **[后处理、图表与结果导出](capabilities/post.md)**：固定预测读回、误差曲线、物理场图、差值和网格导出。主题 `capability:post`。
- **[运行记录与 Task 管理](capabilities/run-task.md)**：direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较。主题 `capability:run-task`。
<!-- capability-menu:end -->

## 三种接入方式

- 单个工具：普通数组、张量或对象直接调用，不要求完整案例或 Task。
- 已有研究代码：保留 PyTorch 模型和科学目标，按需接入数据处理、train_model、推理和评价。只写输入输出适配；具体缺口再自定义。
- 完整流程：选择 standalone，物化 extension，阅读案例正文后 direct-core 运行；有管理需求再用同目录 Task。

复用前核对数值定义、输入输出、设备和恢复状态。科学语义相容时优先复用，局部不相容时明确适配；不存在适用能力时保留自定义路径并说明原因。没有搜索命中不能证明能力缺失。

## 读取与核对

```python
import ai4e_task as task
print(task.help_info())
print(task.read_help_topic("capability:training")["content"])
api = task.describe_help_symbol("ai4e_core.applications.base.iteration_training.train_model")
print(api["signature"], api["source_path"])
```

`search_help` 是补充检索。当前 API 页的签名检查只证明可定位符号；实际调用看能力教程或完整案例，不把 inspect.signature 当作功能演示。

## 其他目录

- getting-started：定位安装、选择案例、direct-core 与 Task。
- concepts：ability、application、recipe、example、Task 与产物职责。
- workflows：领域科学流程。
- api：签名、源码和稳定性。
- user-components：网络、损失、字段、采样、优化、推理与 post 扩展。
- examples：完整 standalone 与 extension。
- recipes：阶段正文和可修改位置。
- troubleshooting：故障定位。
- reference：配置、输入、产物及机器索引合同。

学习效果、工程交接、恢复一致性和论文级精度分别给证据。不要将读取资料计为实际组件调用。
