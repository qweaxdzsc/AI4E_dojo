# GenCP 条件与输出扩展

将 `维护源` 复制到仓库外，再把本目录的三个 Python 文件放在旁边。选择 NTcouple 配置，明确填写现有准备与权重组，并使用新的输出目录。运行 `uv run python extension.py --config config.yaml`。

本例把固体两列温度条件改成平均后广播，真实执行耦合推理。固定结果另外导出速度模长，再从 NPY 读回评价、绘图。变体输出、来源摘要和指标独立保存；不把它计入参考精度验收。

`uv run python retrain.py --config config.yaml --set fields.fluid.updates=500` 只训练流体场，复用原中子/固体权重，生成新组后执行耦合预测和 post。训练预算或学习率改变时从头训练这个场，清空其 `train.resume.fluid`；精确恢复要求原训练契约不变。原模型组保持可用，新组明确记录各场不同的更新次数。

## 物化说明

- `base_case`: `gencp.double_cylinder_cno`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.gencp`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.gencp")["content"])
```

<!-- research-adaptation-details -->
## 选择与改写说明

耦合条件替换、派生输出和单场重训；先物化完整基案例，再按扩展说明修改。

数据形态：field_sequence, coupled_fields；训练机制：iteration, flow_matching。

### 具体修改位置

- 基案例：`gencp.double_cylinder_cno`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`condition`、`post`、`field_retraining`。
- 覆盖/新增文件：`custom.py`、`retrain.py`、`extension.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
