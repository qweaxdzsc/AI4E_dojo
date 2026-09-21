<!-- dojo-help: {"domain": "errors", "errors": ["检查点不兼容", "恢复失败"], "kind": "troubleshooting", "layer": "help", "summary": "定位缺失、结构不匹配、数据身份变化和不完整恢复。", "tasks": ["错误定位"], "title": "检查点错误", "topic_id": "troubleshooting:checkpoints"} -->
# 检查点错误

核对检查点内容摘要、来源运行、模型结构、字段、归一化、优化器参数组、调度器、EMA、更新步和 RNG。只加载权重时明确标成初始化；完整恢复失败必须保留原失败记录，不能回退成静默重训。
