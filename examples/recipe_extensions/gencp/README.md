# GenCP 条件与输出扩展

将 `recipes/gencp` 复制到仓库外，再把本目录的三个 Python 文件放在旁边。选择 NTcouple 配置，明确填写现有准备与权重组，并使用新的输出目录。运行 `uv run python extension.py --config config.yaml`。

本例把固体两列温度条件改成平均后广播，真实执行耦合推理。固定结果另外导出速度模长，再从 NPY 读回评价、绘图。变体输出、来源摘要和指标独立保存；不把它计入参考精度验收。

`uv run python retrain.py --config config.yaml --set fields.fluid.updates=500` 只训练流体场，复用原中子/固体权重，生成新组后执行耦合预测和 post。训练预算或学习率改变时从头训练这个场，清空其 `train.resume.fluid`；精确恢复要求原训练契约不变。原模型组保持可用，新组明确记录各场不同的更新次数。
