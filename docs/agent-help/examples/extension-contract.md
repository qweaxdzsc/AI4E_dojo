<!-- dojo-help: {"domain": "extension", "kind": "reference", "layer": "example", "summary": "基案例加声明覆盖文件的参考变体。", "title": "Extension 合同", "topic_id": "example:extension-contract"} -->
# Extension 合同

extension 记录 `base_case`、`override_files`、修改目的和不可直接比较部分。复制时先物化完整 standalone，再叠加覆盖；未声明冲突直接失败并写 provenance。

extension 原目录不是独立流程。物化后 Agent 可继续修改、direct-core 运行或交给 Task，但需要重新核对配置、输入和恢复兼容性。
