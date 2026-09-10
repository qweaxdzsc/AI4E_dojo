# Aero CFD 五类业务与模型托管

状态：决定已接受，本期实现与验收已落位。

按业务用途采用 rawprep、trainprep、model、train、post。相邻且共同变化的业务聚合，原子算法仍在 abilities。完整 AB-UPT 由 contrib 托管，recipe 注入构造器；core 不反向依赖 contrib。通用组件提炼必须证明等价并保留来源许可要求。

沿用 session.launch 和唯一 writer；准备与训练通过窄桥接复用会话。归一化记录和可选物化属于数据产物；VTKHDF 独立验收，不阻塞 PT 训练。完整字段系统不作为训练前置。

本次首先迁移 pre 为 rawprep，recipe 脚本与阶段名 pre 不变。逐项执行证据见 `.context/mvp/abupt-acceptance.md`。详细架构仅在权威架构文档维护。
