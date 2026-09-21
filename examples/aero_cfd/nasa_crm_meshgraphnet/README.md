# NASA CRM + MeshGraphNet

本案例把 NASA 官方 connectivity 在 rawprep 中固化为 `surface.vtkhdf`，后续 `trainprep` 只消费平台 PT、VTKHDF 和实体身份。一个表面 MeshGraphNet 预测 Cp 与三分量 Cf；默认核心块 16,384 点、15 层 Processor 和 15 跳 halo。

这是工程扩展案例，不对应 MeshGraphNets 论文指标。
