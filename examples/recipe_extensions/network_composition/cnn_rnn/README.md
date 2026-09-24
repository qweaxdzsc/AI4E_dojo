# 逐帧卷积与真实时间循环预测下一帧

本扩展从完整案例 classic_networks.double_cylinder 改写，只覆盖配置与普通用户组件，准备、共享训练、固定推理和后处理沿用基案例。当前只完成源码与非训练组件检查；真实数据训练、恢复和安装后的完整流程等待统一验收，不表示论文精度。

先物化完整案例，不能只复制此覆盖目录后直接运行：

```python
from ai4e_task import copy_example

copy_example("recipe_extensions.network_composition.cnn_rnn", "./cnn_rnn_study")
```

进入物化目录，填写config.yaml中的inputs.rawprep.source、run_root、data_root。来源和输出均应指向用户明确的独立研究目录。模型结构在model.parameters修改，components.model选择cnn_rnn.build_model；不要把本地绝对路径写进公共配置。

```bash
uv run --no-sync python pipeline.py --config config.yaml
```

输入[B,T,H,W,C]沿真实时间T处理；每个空间位置进入循环批轴，输出[B,H,W,4]。family=custom保留完整网格历史，sample_points=null，不走基础RNN点采样连接。每次forward从零状态开始；forward_with_state仅用于空间身份相同的序列续接。

推理将反归一化prediction交给user_outputs.derive，保存prediction_norm及单位、实体、mask声明；post从固定结果重新读回，再用user_outputs.consume核对形状和有效域。此示例计算末轴通道范数，来源没有共同单位声明时保留unknown；Darcy标量为绝对值，双圆柱混合分量范数不是物理速度。若研究目标需要速度模长，应显式选速度分量、声明单位并改写本地派生组件。

独立恢复需选择train阶段并绑定inputs.train.preparation和inputs.train.resume；train.updates表示累计目标。独立infer需绑定准备和检查点，独立post仅需inputs.post.results。模型结构或统计变化时不能继续旧检查点；修改结构后使用新的运行目录。

默认100次更新只是可编辑研究起点。所有训练由主控统一串行执行，每个模型与数据组合的测速、参考、Dojo、重试、恢复和评价合计不超过3小时；train.seconds仅约束这次训练，不能代替组合总账本。
