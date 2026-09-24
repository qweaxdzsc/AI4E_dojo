<!-- dojo-help: {"case_ids": ["recipe_extensions.tail_batch"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "基于Darcy完整案例替换有限轮次数据流，演示尾批、局部目标和精确恢复。", "tasks": ["regular_grid", "scalar_field", "stream", "objective"], "title": "recipe_extensions.tail_batch", "topic_id": "case:recipe_extensions.tail_batch"} -->
# `recipe_extensions.tail_batch`

- 类型：`extension`
- 用途：基于Darcy完整案例替换有限轮次数据流，演示尾批、局部目标和精确恢复。
- 资源路径：`examples/recipe_extensions/tail_batch`

基于Darcy完整案例替换有限轮次数据流，演示尾批、局部目标和精确恢复。

- 数据形态：regular_grid, scalar_field
- 训练机制：iteration, finite_epoch
- 替换入口：stream, objective
- 限制：仅小规模机制验收，不代表Darcy或其他数据集科学精度。
- 限制：先物化完整基案例；数据来源、输出路径和科学参数由用户声明。
- 基案例：`geotransolver.darcy`
- 覆盖文件：
  - `config.yaml`
  - `train.py`
  - `local_components.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `9f756001c172748add16ff29d68caf0b13b8e155faa0333ac40bd798ad55b775`。

### 可恢复尾批扩展

`base_case`: `geotransolver.darcy`。此目录是覆盖文件集，先通过 `ai4e_task.copy_example("recipe_extensions.tail_batch", target)` 物化。它保留基案例原始网格读取、训练统计、GeoTransolver、具名目标、固定推理与独立后处理；只改有序记录收批与轮次调度计数。

#### 适用范围、输入输出与边界

适合样本数不整除批量的监督数组任务。原数据、字段、单位及完整五阶段见物化时交付的基案例说明。默认保留尾批；70/16为16/16/16/16/6，学习率每轮步数采用向上取整。与原来丢尾或要求整除相比，这是明确的研究设置变化，不保证数学轨迹仍相同。不支持多worker预取；只是机制扩展，不是新的科学精度结论。

#### 如何改写

- `train.py`：保留网络、batch、objective、优化器/调度、合同及 writer；改为 `EpochBatchStream` 和公开 `train_model`。没有自写训练循环。
- `local_components.py::epoch_records`：只负责每轮有序记录。可改为先抽窗口再排列，但须同时更新 `source_contract` 的采样声明。
- `config.yaml`：修改 `train.batch_size/updates/checkpoint_every`；修改模型、数据或抽样定义需重新训练，不将不相容状态强行恢复。
- 原 `components.loss/derived/consume` 继续可换普通函数；新增输出先保存，再由独立post读取消费。

#### 运行、恢复与读回

填好 `inputs.rawprep.source`，运行 `uv run --no-sync python pipeline.py --config config.yaml`。已有准备可以设置 `inputs.train.preparation` 和 `inputs.infer.preparation` 并选择 train/infer/post。`inputs.train.resume` 指向 train 报告中的完整 `checkpoint`，`train.updates` 是累计目标。报告增加 `tail_size` 和 `stream_epoch`；检查点持有有序记录与PCG64状态。

独立infer设置准备和固定checkpoint，独立post只填写 `inputs.post.results`。Task创建时直接使用物化目录，仍运行同一pipeline；不需要新任务入口。实际机制验收采用小网格与短预算，不能视为Darcy生产精度。


基案例完整说明：[本地正文](../geotransolver/darcy.md)。
