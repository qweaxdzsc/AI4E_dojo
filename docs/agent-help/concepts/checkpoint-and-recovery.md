<!-- dojo-help: {"domain": "all", "kind": "concept", "layer": "concept", "summary": "区分初始化、权重加载和完整状态恢复。", "title": "检查点与恢复", "topic_id": "concept:checkpoint-recovery"} -->
# 检查点与恢复

重新初始化、只加载网络权重、恢复模型加优化器/调度器/EMA/RNG 是不同操作。网络结构、字段、数据身份、采样、归约或更新策略变化可能使旧检查点失效。

恢复必须记录原检查点内容摘要和来源运行；结构不匹配应明确失败，不能删除错误后伪装成新训练成功。
