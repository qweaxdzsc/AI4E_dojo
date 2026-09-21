<!-- dojo-help: {"domain": "reference", "kind": "reference", "layer": "help", "summary": "机器索引字段、版本和解析方式。", "title": "帮助索引合同", "topic_id": "reference:help-index-schema"} -->
# 帮助索引合同

根 `manifest.json` 给出 `help_contract_version` 和四个索引。topic 包含 ID、类型、层级、领域、标题、摘要、路径、锚点、符号、任务、输入、输出、产物、错误、案例、recipe、稳定性和源码位置。

`symbols.jsonl` 每行一个完整符号记录；`source-map.jsonl` 提供精确源码定位；`cases.json` 是构建时案例清单快照。未知 schema 版本必须明确拒绝。
