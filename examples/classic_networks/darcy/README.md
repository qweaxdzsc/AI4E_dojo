# 经典网络：darcy

从GeoTransolver Darcy完整案例复制后改写。模型与数据连接由贡献层提供，公共block、网络阶段、完整网络和训练由core提供。

配置中显式填写inputs.rawprep.source以及run_root/data_root；所有新数据和训练资产使用独立研究目录。用 `uv run --no-sync python pipeline.py --config config.yaml` 运行；`--set pipeline.stages=[train]` 可选择独立阶段，其inputs需明确绑定。

model.family和model.parameters选择经典结构；components.model可换成本地普通构造函数。构造函数接收model字典并返回普通PyTorch网络。卷积族使用通道在前布局，其他布局由贡献层显式连接。

先集成与非训练检查，主控归并后串行训练；默认100次更新并非论文复现。每组合全部校验累计不超过3小时，测速/两侧/恢复/推理/失败重试共用账本。

修改参数后使用新运行目录；不相容检查点禁止静默部分加载。infer保存反归一化预测、真值、实体和有效域，post只消费固定结果。components.derived与consume允许插入派生数组及独立消费，见network_composition扩展。

运行摘要、检查点和逐字段指标记录本次实际范围；本案例用于小数据结构与功能验证，不声明论文精度或生产精度。
