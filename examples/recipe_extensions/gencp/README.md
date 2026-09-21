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
