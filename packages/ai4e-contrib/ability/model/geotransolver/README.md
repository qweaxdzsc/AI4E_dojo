# GeoTransolver

网络组合来自 PhysicsNeMo aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1，数值算子在 ai4e_core.abilities.modeling.modules。来源与逐文件摘要见 source.json，许可见 LICENSE。

输入支持单流或多流 local_embedding、geometry、local_positions、global_embedding。首期普通 PyTorch GALE、二维结构网格/无结构点集、CPU/MPS float32。TE、GALE_FA、plus、ConcreteDropout、时间条件和激活检查点明确拒绝。新权重与当前参考键一致；历史键须通过 core 的显式映射入口加载。

数据准备和短训工程验证不能作为论文精度复现。

外流基础分支新增 `forward_stream(local_embedding, *, stream_index, geometry=None, global_embedding=None)`。仅支持无局部编码的非结构点流；复用原投影、块和输出层，不改变权重键。ShapeNet-Car 两流共享计算块，NASA CRM 使用独立全局工况。查询分块覆盖全点，不保证与全场一次前向等价。
