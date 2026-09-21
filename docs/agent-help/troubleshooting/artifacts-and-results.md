<!-- dojo-help: {"domain": "errors", "errors": ["资产损坏", "指标不可比"], "kind": "troubleshooting", "layer": "help", "summary": "定位残留文件、未登记资产、清单不完整和指标不可比。", "tasks": ["错误定位"], "title": "产物与结果错误", "topic_id": "troubleshooting:artifacts-results"} -->
# 产物与结果错误

以 `assets.json`、`metrics.json` 和阶段报告为权威入口，不扫描残留文件猜测成功。部分样本失败不能发布完整清单。指标比较需要相同字段、单位、split、statistic 和 data_identity；条件缺失时判不可比。
