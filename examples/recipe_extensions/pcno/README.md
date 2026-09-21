# PCNO 温降扩展

将本目录文件覆盖到 `geothermal.pcno` 完整案例的副本，再在该副本运行。保留基础配置的数据绑定与输出根，将 `components.network` 改为 `local_components.build_model`。该构造器实际改变网络初值；使用原检查点推理时仍由已加载权重决定结果。

新 pipeline 在推理后插入温降分析：计算每例第1年至20年的平均温降，保存带样本身份和K单位的 `temperature_drop.npy`，独立 post 核对摘要并读回统计。基础固定结果保持不变。可同时修改更新次数和经济参数验证配置实际生效。
