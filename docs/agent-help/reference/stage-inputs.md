<!-- dojo-help: {"domain": "reference", "kind": "reference", "layer": "help", "summary": "rawprep 到 post 的常见输入和交接原则。", "title": "阶段输入参考", "topic_id": "reference:stage-inputs"} -->
# 阶段输入参考

rawprep 读取绑定源或生成数据；trainprep 消费已处理数据并生成准备记录；train 消费数据、准备和可选恢复；infer 消费数据、准备与检查点；post 只消费固定推理结果。

每一步只校验自己的输入。用户配置可拒绝旧格式，历史冻结产物只按其导入合同判断，不能用后续默认值阻塞当前步骤。
