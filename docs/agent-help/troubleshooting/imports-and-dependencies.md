<!-- dojo-help: {"domain": "errors", "errors": ["ModuleNotFoundError", "ImportError"], "kind": "troubleshooting", "layer": "help", "summary": "区分帮助可查、核心安装和案例可选依赖。", "tasks": ["错误定位"], "title": "导入与依赖错误", "topic_id": "troubleshooting:imports"} -->
# 导入与依赖错误

`search_help` 不导入模型，因此帮助可查不代表案例依赖已安装。用 `source_location` 核对当前解释器中的 core、task 和可选 contrib；再读取案例 `dependencies`。禁止通过把仓库根加入 `sys.path` 掩盖安装问题。
