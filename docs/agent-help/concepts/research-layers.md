<!-- dojo-help: {"domain": "all", "kind": "concept", "layer": "concept", "summary": "Dojo 各层在研究流程中的职责。", "title": "研究层次", "topic_id": "concept:research-layers"} -->
# 研究层次

Dojo 的组合顺序是：原子 **ability** 提供计算；领域 **application** 绑定数据和步骤语义；可读 **recipe** 明确阶段顺序和参数来源；可复制 **example** 形成仓库外研究目录；`run` 管理会话、日志、产物和检查点；**Task** 管理版本、后台运行、停止、恢复、资产和比较。

Agent 可以自由组合算法函数，但不能绕过公开边界读取私有会话状态，也不应复制训练循环、writer 或 Task worker。
