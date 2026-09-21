<!-- dojo-help: {"domain": "standalone", "kind": "reference", "layer": "example", "summary": "完整案例的文件、入口、路径、运行和证据合同。", "title": "Standalone 合同", "topic_id": "example:standalone-contract"} -->
# Standalone 合同

standalone 至少包含 README、config、configuration 和 pipeline，以及领域声明的阶段脚本。所有脚本能从案例目录外按绝对脚本路径启动，不依赖 cwd、仓库根、recipe 目录或隐式 `sys.path`。

Python 决定顺序，YAML 提供参数。direct-core 与 Task 使用同一目录。README 必须声明输入、依赖、阶段、单阶段入口、恢复键、检查点失效边界、产物和组件调用证明。
