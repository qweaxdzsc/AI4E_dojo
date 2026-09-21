<!-- dojo-help: {"domain": "errors", "errors": ["FileNotFoundError", "路径污染"], "kind": "troubleshooting", "layer": "help", "summary": "定位 inputs、run_root、data_root、cwd 和固定来源问题。", "tasks": ["错误定位"], "title": "输入与路径错误", "topic_id": "troubleshooting:inputs-paths"} -->
# 输入与路径错误

从案例目录外运行同一脚本。核对 `inputs.<stage>.<name>` 指向已提交的上游来源，`run_root` 与 `data_root` 分离，路径没有仓库根或本机硬编码。同一 pipeline 普通返回值无需伪造成文件；独立阶段必须选择固定来源。
