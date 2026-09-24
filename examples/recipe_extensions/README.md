# Recipe 扩展示例

- `field_mapping/`：普通 NumPy 函数新增速度模长，经过物理保存、训练统计、归一化及模型输入。
- `sampling/`：配置选择本地采样函数，训练迭代时改变几何点顺序。

上列 field_mapping、sampling 为完整可复制目录；其它目录是否为覆盖文件集以各自 README 为准。输入数据仍由用户配置，不下载数据；正式网络和预算来自原模板。先检查目录路径，再执行独立阶段或 pipeline。验收测试使用真实小网格和同一模型算子，不代表生产精度。

自由连接示例见 `free_wiring/`。完整外流扩展使用 rawprep → trainprep → train → infer → post；在 infer.samples 显式填写样本，独立 post 消费固定结果。配置连接由 contrib 公开适配提供，局部 STEP_PARAMETERS 仍可扩展。

## Task 项目共享交接

通过 Task 托管时，原始处理正式产物归项目 shared，先填写 `dataset.processed_name`。新任务可绑定该名称后仅执行 trainprep/train/infer，无需重复 rawprep；同名重做必须在本次提交显式指定覆盖。独立运行 Python 脚本仍按原配置的输出路径执行。

处理步骤仍在 rawprep.py 中可编辑。新增字段要完成声明、保存、共享清单读回和另一任务的字段绑定；采样和归一化不写回共享物理数据。扩展示例的 Task 入口声明共享输出与阶段输入，字段扩展通过两任务和仓库外 wheel 实跑验收。


## 按研究变化选择

- 换整网/损失：[WDNO](wdno/README.md)，以及既有自由连接与外流替换测试。
- 换内部部件：[AB-UPT 前馈激活](model_block/README.md)。
- 换优化器/调度/更新：[WDNO 局部训练策略](wdno/README.md#只替换训练策略)。
- 加步骤/派生输出：[WDNO 能量审计](wdno/README.md)、[推理字段](inference_fields/README.md)、[推理指标](inference_metrics/README.md)。
- 模型专属研究：[GenCP](gencp/README.md)、[SafeDiffCon](safediffcon/README.md)。
- 训练中观察与可视化：[物理场输出](physical_visualization/README.md)。
- 有限轮次尾批：[tail_batch](tail_batch/README.md)，用户定义有序记录，保留框架训练和精确恢复。
- 独立验证与用户状态：[research_state](research_state/README.md)，训练内留出验证、普通/EMA选优快照与恢复；不改变框架循环。两例均基于 `geotransolver.darcy` 物化，证据为受控小规模连接。

只改研究变化部分，按研究任务导航圈定前向、短训、恢复与固定输出读回。目录存在或导入成功不是数值验收。

## PCNO

`pcno/` 覆盖到完整 `geothermal.pcno` 副本；README说明构造器替换与带单位温降数组的保存读回。
