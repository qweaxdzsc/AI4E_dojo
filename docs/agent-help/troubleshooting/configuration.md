<!-- dojo-help: {"domain": "errors", "errors": ["KeyError", "ValueError"], "kind": "troubleshooting", "layer": "help", "summary": "定位缺键、旧键、覆盖冲突和相对路径问题。", "tasks": ["错误定位"], "title": "配置错误", "topic_id": "troubleshooting:configuration"} -->
# 配置错误

先读取运行目录中的最终 `inputs/config.yaml`，不要只看源 YAML。检查配置加载器是否应用 `--set`、是否以配置文件所在目录解析相对路径、是否拒绝旧键与新旧并存。阶段代码不能用空对象或默认值掩盖已声明但缺失的配置。
