<!-- dojo-help: {"domain": "errors", "errors": ["failed", "stopped", "timeout"], "kind": "troubleshooting", "layer": "help", "summary": "区分提交、运行终态、core 摘要和产物状态。", "tasks": ["错误定位"], "title": "Task 运行错误", "topic_id": "troubleshooting:task-runs"} -->
# Task 运行错误

`submit_run` 返回只代表登记或启动。用 `wait_run/get_run` 读取终态，再检查 `summary`、日志、阶段事件和资产索引。停止需要真实收据；未知运行不能重复启动。运行进程成功但目标阶段未交付固定产物时，研究仍未完成。
