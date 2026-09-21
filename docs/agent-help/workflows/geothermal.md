<!-- dojo-help: {"domain": "geothermal", "kind": "workflow", "layer": "recipe", "summary": "PCNO 发布小数据的双场训练、固定预测和独立技术经济评价。", "tasks": ["地热训练", "联合预测", "经济评价"], "title": "地热双场研究", "topic_id": "workflow:geothermal"} -->
# 地热双场研究

从 `geothermal.pcno` standalone 复制完整案例，在 `inputs.rawprep.source` 绑定作者发布目录，再执行 `pipeline.py`。处理、准备、两个分支训练、推理和后处理均在脚本中显式连接。依赖为 `ai4e-contrib[pcno]`；完整用法见案例 README。

默认每分支21次更新，保留完整网格与原250轮损失、学习率日程。训练前按本机实测估算总预算。用 `train.updates` 控制总目标，两个resume输入指定各自完整检查点。原版权重导入仅恢复权重。

`infer.source` 可选训练24例回算、18例新预测、作者18例回放；18例场不具有独立真值，不能报告精度。后处理只消费固定结果清单，MAE、RMSE、MARE与经济评价分别记录。源代码温度训练存在未选黏度分支非法梯度，当前采用明确记录的分支屏蔽修正，对照必须说明该修正。

`extension.pcno` 物化到完整副本后，可替换普通网络构造器，并在推理与后处理之间插入温降步骤；新增K单位数组保存后由后处理核对身份与摘要并读回。Task 托管同一目录，无专属模型管理逻辑。本案例不声明论文9450例复现或生产精度。
