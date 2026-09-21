# ShapeNet-Car + MeshGraphNet

本案例复用外流 CFD 的完整物理流程。平台数据以独立 PT 和表面/体积 VTKHDF 交付，`trainprep` 从网格派生两个互不连接的图；表面网络预测压力，体积网络预测速度。正式默认隐藏宽度 128、15 层，短训请通过配置同时覆盖 `processor_layers` 与 `halo_hops`。

这是工程扩展案例，不对应 MeshGraphNets 论文指标。
