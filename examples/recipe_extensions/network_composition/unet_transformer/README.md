# 标准注意力阶段替换U-Net瓶颈

本扩展从完整案例 classic_networks.darcy 改写，只覆盖配置与普通用户组件，准备、共享训练、固定推理和后处理沿用基案例。当前只完成源码与非训练组件检查；真实数据训练、恢复和安装后的完整流程等待统一验收，不表示论文精度。

先物化完整案例，不能只复制此覆盖目录后直接运行：

```python
from ai4e_task import copy_example

copy_example("recipe_extensions.network_composition.unet_transformer", "./unet_transformer_study")
```

进入物化目录，填写config.yaml中的inputs.rawprep.source、run_root、data_root。来源和输出均应指向用户明确的独立研究目录。模型结构在model.parameters修改，components.model选择unet_transformer.build_model；不要把本地绝对路径写进公共配置。

```bash
uv run --no-sync python pipeline.py --config config.yaml
```

构造器消费model字典，返回通道在前的二维网络；family=unet由贡献连接显式转换末轴通道网格。编码、瓶颈、解码均复用公共模块，输入85×85保留原尺寸。

推理将反归一化prediction交给user_outputs.derive，保存prediction_norm及单位、实体、mask声明；post从固定结果重新读回，再用user_outputs.consume核对形状和有效域。此示例计算末轴通道范数，来源没有共同单位声明时保留unknown；Darcy标量为绝对值，双圆柱混合分量范数不是物理速度。若研究目标需要速度模长，应显式选速度分量、声明单位并改写本地派生组件。

独立恢复需选择train阶段并绑定inputs.train.preparation和inputs.train.resume；train.updates表示累计目标。独立infer需绑定准备和检查点，独立post仅需inputs.post.results。模型结构或统计变化时不能继续旧检查点；修改结构后使用新的运行目录。

默认100次更新只是可编辑研究起点。所有训练由主控统一串行执行，每个模型与数据组合的测速、参考、Dojo、重试、恢复和评价合计不超过3小时；train.seconds仅约束这次训练，不能代替组合总账本。
