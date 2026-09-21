# MeshGraphNet

这是 MeshGraphNets 的模型本体。图构造、变长收批、mask、rollout、静态图分区和评价
使用 `ai4e-core` 的中立能力；CylinderFlow 字段、节点类别及静态外流字段由对应
application 连接。

实现对照 DeepMind `deepmind-research` commit
`f5de0ede8430809180254ee957abf36ed62579ef`，来源代码采用 Apache-2.0。当前目录是
Dojo 的 PyTorch 重建，不是 TensorFlow/Sonnet 权重的逐值等价证明；具体文件摘要与
PhysicsNeMo 参考版本见 `source.json`。

`network.py` 保留共享 Encoder/Processor/Decoder；`static.py` 用多个彼此独立的子网络
表达单域或多域静态网格。该静态外壳是 Dojo 对 ShapeNet-Car 与 NASA CRM 的工程扩展，
不属于 DeepMind CylinderFlow 论文案例，也不表示这些数据集已有论文或生产精度结论。
