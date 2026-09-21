# Seatbelt 平台策略来源

`base.sbpl`、`platform.sbpl`、`network.sbpl` 从 OpenAI Codex 仓库 `codex-rs/sandboxing/seatbelt_{base_policy,read_only_platform_defaults,network_policy}.sbpl` 获取（2026-09-20）。原代码按 Apache-2.0 许可交付，完整许可见 LICENSE。上游：https://github.com/openai/codex/tree/main/codex-rs/sandboxing 。

本工具额外由主控生成本组读写、系统工具只读与本机网络拒绝规则。策略不从实验组可写文件加载。
