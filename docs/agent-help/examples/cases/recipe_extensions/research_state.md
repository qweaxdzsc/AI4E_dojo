<!-- dojo-help: {"case_ids": ["recipe_extensions.research_state"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "基于Darcy完整案例留出验证分片，比较普通/EMA权重并配对恢复最佳快照。", "tasks": ["regular_grid", "scalar_field", "state_bindings", "evaluate", "ema", "objective"], "title": "recipe_extensions.research_state", "topic_id": "case:recipe_extensions.research_state"} -->
# `recipe_extensions.research_state`

- 类型：`extension`
- 用途：基于Darcy完整案例留出验证分片，比较普通/EMA权重并配对恢复最佳快照。
- 资源路径：`examples/recipe_extensions/research_state`

基于Darcy完整案例留出验证分片，比较普通/EMA权重并配对恢复最佳快照。

- 数据形态：regular_grid, scalar_field
- 训练机制：iteration, validation_selection
- 替换入口：state_bindings, evaluate, ema, objective
- 限制：仅小规模机制验收，不代表Darcy或其他数据集科学精度。
- 限制：先物化完整基案例；数据来源、输出路径和科学参数由用户声明。
- 基案例：`geotransolver.darcy`
- 覆盖文件：
  - `config.yaml`
  - `configuration.py`
  - `rawprep.py`
  - `train.py`
  - `local_components.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `d28036f73556a5f2f2652a7b37b88ff071c67b6a2d6cb0a8867ebf181c6bba9e`。

### 可恢复研究状态与验证选优扩展

`base_case`: `geotransolver.darcy`。先通过 `ai4e_task.copy_example("recipe_extensions.research_state", target)` 物化，按随复制目录交付的基案例说明配置原数据。本扩展沿用五阶段、GeoTransolver、公开 `train_model`、固定infer/post，展示普通用户状态如何随完整检查点恢复。

#### 数据与阶段交接

`rawprep.py` 从原训练名单末尾显式留出 `train.validation_count` 条轨迹/样本，原测试分片不变，保留来源行号。原trainprep自动处理新增validation分片，归一化统计只拟合剩余train。使用外部准备时必须已有独立validation分片且共享训练统计；不回退到test选优。此留出规则是演示策略，应按研究协议替换。

训练采用可恢复尾批流，分别以 `train.evaluate_every` 和 `train.checkpoint_every` 控制验证、完整保存。一次验证按相同objective评价raw和EMA，已有 `BestMetric` 比较、writer成功写入后提交选择；评价受模式和RNG保护。检查点中的 `user_state` 保存选择值、来源、更新位置、验证历史以及真正受评权重的独立快照，不能只记录可能失效的best路径。

#### 修改位置与保留流程

- `configuration.py`：只增加本地 `evaluate_every/ema_decay/validation_count` 校验，基配置继续复用原校验器。
- `local_components.py::ResearchSelection`：普通对象提供save/validate/load，聚合selector与selected权重；不继承框架基类、不写训练循环。改变选择目标须更新合同。
- `train.py`：显式装配验证回调、EMA和 `state_bindings`；共享训练入口负责更新、周期与恢复。算法state仍是静态兼容声明。
- 网络配置、`components.loss/derived/consume` 保持基案例改写方式。把新计算放入本地组件，保留writer、可恢复流及固定结果交接。

#### 运行、恢复与结果

设置数据路径后运行 `uv run --no-sync python pipeline.py --config config.yaml`，或用物化目录创建Task。首个短训可设 `train.updates=4`，再增至6并设置 `inputs.train.resume`。

**恢复必须使用训练报告的 `resume_checkpoint`（latest完整状态）；报告的 `checkpoint` 是选定权重，只供infer。** 两者职责不同。独立infer消费选定权重，独立post只消费固定结果；pipeline自动连接。恢复到新run时会重新交付此前最佳快照，无需旧best文件仍在。

validation只决定权重选择，test只用于固定方案评价。本扩展验证状态/权重/输入流连续性，不表示该策略在科学上更优，不代表论文精度。完整数值验收应同时比较连续训练与同相位分段恢复；若在额外终点做了一次验证，验证历史会如实多一项。


基案例完整说明：[本地正文](../geotransolver/darcy.md)。
