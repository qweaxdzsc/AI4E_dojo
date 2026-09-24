---
name: dojo-research
description: 开展训练与科学机器学习研究：复制最接近的 Dojo 完整案例，按 recipe 与训练框架改写，通过用户组件表达变体；结合外部资料选择能力。
---

# Dojo 研究工作流

本 skill 规定研究时的决策顺序；[GUIDE](../../../DOJO_AGENT_GUIDE.md) 说明有什么，[Dojo Agent Help Center](../../../docs/agent-help/index.md) 保存唯一详细 API 和可执行例子。

**完整新训练任务先选择并复制最接近的 standalone example，按 Dojo 的 recipe 和训练框架写法改写。** 接近程度按数据交接、训练目标和执行流程判断，不只看案例或模型名称。保留用户的模型、科学目标和实验约束；不要求采用某个固定算法工具，超出现有能力的部分通过 Dojo 支持的用户组件与公开扩展点实现。只有网络源码不等于已有完整训练工程。

选择时先读 `list_examples` 返回的 `research` 用途、数据形态、训练机制、替换点与限制，再读候选案例的 README/帮助主题及阶段正文。可用 query、data_form、training_pattern 缩小范围；标签只帮助定位，适用性仍需核对。参考 extension 时同时读其差异和 base_case；复制后从返回的 `documentation.entry` 进入本地两层说明，再按下方原有改写流程继续。

先用 `list_examples/check_example/copy_example` 检查并复制完整目录，保留来源记录；参考 `extension` 时物化其 `base_case`。阅读复制品的 README、配置、pipeline 和阶段脚本，以及[用户组件写法](../../../docs/agent-help/user-components/overview.md)。明确哪些流程保留、哪些能力替换、哪些接口需本地转换，然后再实现。领域差异大时仍从最接近案例改写框架，不沿用不相容的科学设置，也不以整段自写脚本取代 recipe。

recipe 负责可读的步骤、参数来源和结果交接；算法、采样、损失及业务适配放在实际本地组件中，通过普通函数/对象或全限定 import 路径连接。框架承担适合的更新、运行记录、检查点与恢复；不得把完整自写流程藏进一个组件后整段转发，或只包一层 `launch` 就声称使用了训练框架。

## 改写顺序：先框架与外部研究，再选工具，最后复核

在编写或实质修改数据、训练、恢复、推理、评价、后处理代码前，按以下顺序推进；已有派生案例的后续迭代只检查本次变化。

1. **参考框架和 Web，形成改写初案。** 先阅读所选 example 的流程正文、[训练框架](../../../docs/agent-help/capabilities/training.md)及[运行记录](../../../docs/agent-help/capabilities/run-task.md)，理解步骤、更新、验证、检查点与恢复如何连接。同时进行相关 Web 检索，阅读适用的官方文档、论文或可靠实现，补充方法、科学语义、设备与性能的考虑。以 Dojo 框架组织改写初案，明确保留的流程、研究差异和用户组件边界；此时先确定职责与交接，不急于逐个挑选原子工具。
2. **按初案检索能力，替换进计划。** 有了改写初案，再按其中的具体职责进入下方能力分支或搜索框架，读取现行签名、适用范围和例子。把适用的既有能力替换进计划；能用参数、局部适配或用户组件表达的差异，不重写整段流程。保留必要的自定义，写清查过的能力、具体不匹配处及外部依据。更新初案，形成可执行的改写计划。
3. **复核框架写法，再实施与验证。** Agent 对更新后的计划核对所选 example 与用户组件说明：recipe 是否明确表达步骤、参数来源和交接，算法是否放在合适组件中，训练更新、状态、检查点与恢复是否仍由所选框架路径承担，是否因工具选择改变科学定义。先修正偏差再编码；实现后对实际代码再做同样检查，并验证真实输入输出及阶段交接，不能只检查计划。

这三个步骤是 Agent 内部推进顺序，不要求每步等待用户批准。一个简短计划可以覆盖同一目的的一组文件修改；不要以反复写计划替代实施。已有仍适用的 Web 资料可引用原检索记录，新方法或新约束再补检索；网络不可用时记录失败与证据缺口，不伪称查阅完成。

按实际职责拆分适配判断：读文件、校验、统计、正反变换并不等同；某个滚动函数不合适，也不代表推理执行与计时工具都不合适。外部参考保留来源及实际读到的结论，只有下载成功、页面标题或重定向页不算已理解。适配失败只处理受影响的局部，不因某项工具缺失重写整个训练框架。

## 已有能力：按要完成的工作直接进入

<!-- capability-menu:start -->
- **[数据读取、预处理与归一化](../../../docs/agent-help/capabilities/data.md)**：读取、身份校验、保存、统计、正反归一化及普通拟合状态读回。主题 `capability:data`。
- **[几何与采样](../../../docs/agent-help/capabilities/sampling.md)**：网格、坐标、法向、距离和一致采样，保留实体身份。主题 `capability:sampling`。
- **[网络与模型组件](../../../docs/agent-help/capabilities/model.md)**：经典网络、DeepONet/FNO 与传统代理模型；按 block、可复用阶段和完整架构组合。主题 `capability:model`。
- **[损失与物理约束](../../../docs/agent-help/capabilities/loss.md)**：监督项、权重、可微比较和独立于模型的物理残差。主题 `capability:loss`。
- **[训练、优化与恢复](../../../docs/agent-help/capabilities/training.md)**：神经网络优化与恢复，以及 POD、RSM/RBF、Kriging、LightGBM 非梯度拟合。主题 `capability:training`。
- **[推理与多步滚动](../../../docs/agent-help/capabilities/inference.md)**：神经网络执行上下文、普通对象分批预测、多步滚动和设备同步计时。主题 `capability:inference`。
- **[评价与误差指标](../../../docs/agent-help/capabilities/evaluation.md)**：具名样本、物理帧和字段的 FP64 误差，显式定义聚合。主题 `capability:evaluation`。
- **[后处理、图表与结果导出](../../../docs/agent-help/capabilities/post.md)**：固定预测读回、误差曲线、物理场图、差值和网格导出。主题 `capability:post`。
- **[运行记录与 Task 管理](../../../docs/agent-help/capabilities/run-task.md)**：direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较。主题 `capability:run-task`。
<!-- capability-menu:end -->

## 根据任务选择接入方式

- **新训练任务或重建训练流程**：先复制完整案例，保留明确的 pipeline、配置和阶段交接，按需替换本地组件。训练和运行分支提供迭代、epoch、验证、检查点与恢复连接；选择与科学语义相符的公开路径，不锁定某个具体训练函数。通过 `ai4e_core.run.launch` 与 `TrainingRun` 运行并读回，再按需使用 Task。
- **用户已有稳定训练项目**：评估迁移收益与成本，优先接入可兼容的步骤；仅修局部问题可保留原循环，注明范围。
- **用户只需要一个工具**：直接进入对应分支，无需 Task、完整训练流程或案例。完整训练任务不能因为选择了一个评价函数就被归类为单工具任务。
- **已有本组派生案例的后续优化**：继续修改同一 recipe 的配置或用户组件；不为每轮重复复制。新算法、数据交接或生命周期变化重新核对相应能力和外部依据。Task 管理可选，recipe 与训练框架写法仍保留。

## 复用与变体的边界

涉及初始化、权重键映射或恢复时，分别核对[模型权重工具](../../../docs/agent-help/api/core/abilities/modeling/weights.md)与训练恢复分支。模型构造、权重加载、结构特有的状态变换和完整续训是不同职责；不能因为需要自写结构变换就跳过现有加载/映射工具的适配评估，也不能将构造工具的使用算作这些职责均已复用。

处理多场或时序数据时，将来源摘要检查与通用校验分开评估：先看[布局与跨场配对](../../../docs/agent-help/api/core/abilities/data/validate/trajectory.md)，涉及时间或实体身份再看[时间序列校验](../../../docs/agent-help/api/core/abilities/data/validate/time_series.md)。它们独立于文件读取器；只在实际输入能提供相应身份与轴语义时连接，不能为调用工具虚构物理时间或实体身份。源格式特有的检查仍由局部适配负责。

输入输出、数值定义、设备和状态语义相容时优先复用；字段/轴转换、特殊采样和科学损失用局部连接。通过公开 batch、objective、stream、evaluate、update 等扩展点表达研究差异，框架继续承担适合它的职责。核对默认值，不能因接入改变梯度裁剪、归约、训练模式或恢复设置；例如原方案无裁剪时显式传 `max_grad_norm=None`。

用户组件允许有具体原因：未覆盖的科学语义、实测性能不符或接口限制。记录检查过哪个入口、差异及验证证据；“更灵活”“不熟悉”或没有搜索命中不足以证明缺失。组件没有现成实现不等于训练框架不能承接；先验证公开扩展点。若公开接口确实无法表达，报告最小失败证据与需要的框架扩展，不绕过框架后冒充完成。用户明确要求优先于本 skill。

代码量统计是**默认可选的附属能力**，不作为研究主流程、每次交付要求或优化目标。用户需要时，可报告源码复用、净新增/改写量及调用占比；若衡量 import 背后的实现，另追踪实际使用的库代码并去重，不能将导入行数当作全部复用量，也不能把整包无关源码算成节省量。计数包含用户组件，区分既有实现与本次新增，不以无用复制、空调用或移出分母提高比例。
新模型正式集成使用可用的 `dojo-integrate-model`；自定义研究网络不自动扩大为框架开发。不得读取私有会话字典，不另复制已选择框架的管理实现。

## 定位及按需核对

```python
import ai4e_task as task
print(task.help_info())
print(task.read_help_topic("capability:training")["content"])
api = task.describe_help_symbol("ai4e_core.applications.base.iteration_training.train_model")
print(api["signature"], api["source_path"])
```

首次使用或改变生命周期连接时，先以最小实际输入贯通新增边界（如验证回调、检查点保存和读回），再启动完整训练。签名中的 str 或 dict 不代表任意取值都可用；确认允许的名称、状态内容和恢复前提。已验证且未变更的边界无需每轮重测。

调用前明确签名、输入轴/单位、返回值、副作用、稳定性及当前版本源码；能力教程提供小例子，完整领域交接再读案例。帮助与安装签名不一致时报告漂移，以当前安装源码为准。`search_help` 用于进一步细查，不是发现能力大类的前置步骤。

其他帮助：`getting-started` 安装定位；`concepts` 层次边界；`workflows` 领域流程与 recipe；`api` 签名；`user-components` 自定义连接；`examples` 案例；`troubleshooting` 故障；`reference` 配置/阶段/产物合同。离线读取 manifest 与 indexes；CLI 只是 Python API 的可选包装。

## 按需管理和交付

- Task：`ai4e_task.create_project/new_task/submit_run`，再用 `ai4e_task.wait_run`；按需 stop_run、resume_run、fork_task、compare_runs。使用 Task 时等待终态并核对实际产物。
- 配置：read_configuration 后带 revision 保存；临时覆盖用 submit_run(overrides=[...])。普通函数不要求采用官方配置树。
- 独立阶段按已选择案例使用 `inputs.<stage>.<name>`，运行与数据分别用 `run_root`、`data_root`；纯能力通过普通返回值交接。
- 验证实际调用、输入输出、数值和产物读回；恢复须验证状态，post 只消费固定预测。改变结构、字段、数据身份或更新策略时检查旧 checkpoint 兼容性。
- 区分工程接线、状态/预测一致性、学习效果和论文精度，保留失败、重试及恢复来源。读取文档不等于实际使用 Dojo。
