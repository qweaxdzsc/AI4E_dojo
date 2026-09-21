<!-- dojo-help: {"domain": "reference", "kind": "reference", "layer": "help", "summary": "跨案例稳定配置键和职责。", "title": "配置键参考", "topic_id": "reference:configuration-keys"} -->
# 配置键参考

- `run_root`：配置、日志、摘要、资产索引、指标索引和检查点。
- `data_root`：数据处理、预测和 post 等科学文件。
- `pipeline.stages`：本次执行范围，不定义算法顺序。
- `inputs.<stage>.<name>`：独立阶段的固定外部输入。

领域参数保留在所属阶段，不把外流、PDE 或模型参数塞进通用 runner。实际键以所选 standalone 的 config 和 configuration 为准。
