<!-- dojo-help: {"case_ids": ["recipe_extensions.task_labels"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "本地应用显式声明校准标签需求，保留控制流程；先物化完整基案例，再按扩展说明修改。", "tasks": ["field_sequence", "control_trajectory", "application", "input_declaration"], "title": "recipe_extensions.task_labels", "topic_id": "case:recipe_extensions.task_labels"} -->
# `recipe_extensions.task_labels`

- 类型：`extension`
- 用途：本地 application 声明校准标签需求，复用控制完整流程
- 资源路径：`examples/recipe_extensions/task_labels`

本地应用显式声明校准标签需求，保留控制流程；先物化完整基案例，再按扩展说明修改。

- 数据形态：field_sequence, control_trajectory
- 训练机制：iteration, diffusion_control
- 替换入口：application, input_declaration
- 限制：覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 限制：仅声明扩展演示范围，不据此扩大数值精度验收。
- 基案例：`safediffcon.burgers`
- 覆盖文件：
  - `config.yaml`
  - `task_labels_app.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `e07e11adeb2e7ca4364e450836afaf4e6e17dd7561807de850a1dac2394d0dd6`。

### 按标签选择控制准备数据

本扩展以 SafeDiffCon Burgers 完整案例为基础，覆盖配置与本地 `task_labels_app.py`。使用 `ai4e_task.copy_example("recipe_extensions.task_labels", target)` 物化后，仍由原 Python 阶段正文执行训练、校准、推理和固定结果后处理。

本地 application 复用控制描述，为 `inputs.posttrain.preparation_cal` 增加生产者名称 `cal` 条件；同时要求 `control.preparation` 类型和 `cal` 用途。训练和测试记录不会进入该候选，多个校准运行都保留供研究者选择。Task 不认识校准算法，也不会按文件名补标签。

先按基案例 README 绑定真实数据及预算。运行准备后查看 `ai4e_task.list_stage_artifacts(project, task_id)`；显式选择候选路径写入 `inputs`。候选匹配不代替控制应用对数组内容的检查。源码回归使用真实小网络与人工数组验证工程交接，不声明论文精度。

<!-- research-adaptation-details -->
#### 选择与改写说明

本地应用显式声明校准标签需求，保留控制流程；先物化完整基案例，再按扩展说明修改。

数据形态：field_sequence, control_trajectory；训练机制：iteration, diffusion_control。

##### 具体修改位置

- 基案例：`safediffcon.burgers`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`application`、`input_declaration`。
- 覆盖/新增文件：`config.yaml`、`task_labels_app.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。


基案例完整说明：[本地正文](../safediffcon/burgers.md)。
