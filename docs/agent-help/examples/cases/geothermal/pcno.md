<!-- dojo-help: {"case_ids": ["geothermal.pcno"], "domain": "geothermal", "kind": "case", "layer": "example", "summary": "发布地热双场与技术经济研究；读取案例特定物理字段。", "tasks": ["regular_grid", "coupled_fields", "network", "objective"], "title": "geothermal.pcno", "topic_id": "case:geothermal.pcno"} -->
# `geothermal.pcno`

- 类型：`standalone`
- 用途：发布24例地热双场与技术经济研究
- 资源路径：`examples/geothermal/pcno`

发布地热双场与技术经济研究；读取案例特定物理字段。

- 数据形态：regular_grid, coupled_fields
- 训练机制：iteration
- 替换入口：network, objective
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`PCNO`
- 数据集：`geothermal_cmg`
- 入口：`pipeline.py`
- Recipe 来源：`pcno`
- 依赖：`ai4e-core[geothermal]`, `ai4e-contrib[pcno]`

## 阶段

- `rawprep.py`
- `trainprep.py`
- `train.py`
- `infer.py`
- `post.py`

## 使用流程

1. 用 `check_example` 检查资源，再用 `copy_example` 复制到仓库外空目录。
2. 阅读复制目录的 README、config、pipeline 和全部阶段脚本。
3. 先直接执行 pipeline；需要版本、后台运行或恢复时再把同一目录交给 Task。
4. 按 README 读回配置、阶段摘要、检查点、预测、指标和 post 结果。

目录和文件存在不代表运行成功；当前真实输入、预算和证据边界以案例 README 为准。

## 案例详细说明

来源：案例 README；SHA256 `30686c3c5b7975c03fb5f1d8fb6724a121f8c9c058b7b639197a6b10835c24d5`。

### PCNO 地热双分支研究案例

本目录可复制后直接运行。安装 `ai4e-contrib[pcno]`，在 `inputs.rawprep.source` 绑定 Code Ocean 发布包的 24 例数据目录。数据保持只读；运行记录、检查点与预测写入独立的 `run_root`、`data_root`。

```bash
uv run --no-sync python pipeline.py --set inputs.rawprep.source=/path/to/undergroundwater_CMG_24data
```

Python 正文依次处理、准备、分别训练压力与温度、联合推理、独立经济评价。各阶段也能直接执行对应脚本；独立阶段须绑定 `inputs.<stage>` 的准备清单、双分支检查点清单或结果清单。显式路径与上游返回值冲突会报错。

默认每分支 21 次更新，即一轮、21 例训练与3例轮换验证。保留作者250轮学习率及损失日程，短训不压缩日程：物理损失与井级损失仍计算，但早期权重为零。完整网格为80×80×5×21，四维谱模态均为1、宽度8。开始计算前先按本机实测估算总预算，包含原版对照、两个分支、评价与保存；集成检查优先控制在3小时内。

`train.updates` 是总更新目标；`inputs.train.pres_resume`、`temp_resume` 接受 Dojo 完整检查点，分别恢复权重、优化器、调度、随机状态、分片排列和游标。改变科学配置拒绝精确恢复。原版权重可通过 `ai4e_contrib.ability.model.pcno.import_weights(model, path)` 严格导入，只导入权重，不声称续训。

`infer.source` 可选 `training24`、`demonstration18` 或 `author18`。前两者需要两个分支，后者仅回放发布的18例预测。可用 `sample_ids` 指定清单中的样本身份。后处理只读固定结果，修改经济参数不重新运行网络。

24例回算只说明训练集合效果；轮换验证不是独立测试。18例发布数据中的压力/温度与预存预测相同，不能当作独立真值。作者结果回放用于经济计算一致性；自训的新预测不要求等于作者预存结果。论文9,450例实验与生产精度未复现。

通过 `components.network`、`components.objective` 指向复制目录中的普通函数即可替换能力。新分析步骤可插入 infer 与 post 之间；派生数组须保存、带样本身份和单位，并由 post 读回消费。Task 使用同一目录及 `pipeline.py`，无需模型专属任务协议。

来源：Code Ocean capsule 8000337 v1，作者代码遵循 GPL-3.0；安装包保留完整许可证及源码摘要。算法保持原始数值行为，包括井筒中标量转换、经济评价第一例参考温度与恒定指标评分可能未定义的情况。

数值修正：原版温度训练在第6次更新出现非有限梯度，源于黏度分段公式未选中分支的非法幂。当前仅对未选分支使用安全自变量，保留每段实际公式；同时拒绝非有限梯度和权重。对照应使用记录了同一修正的参考适配，不能称为未经修正原版。

<!-- research-adaptation-details -->
#### 选择与改写说明

发布地热双场与技术经济研究；读取案例特定物理字段。

数据形态：regular_grid, coupled_fields；训练机制：iteration。

##### 具体修改位置

- 数据来源、预算和设备参数先在 `config.yaml` 调整；配置加载规则见 `configuration.py`，步骤调用和返回值交接见 `pipeline.py`。
- 配置已声明的可替换入口：`network`、`objective`。读取对应阶段实际消费位置，再替换普通用户函数/对象；名称出现在列表不代表能跳过科学兼容检查。
- 保留原准备引用、训练运行记录与恢复交接；新增输出由计算步骤保存，推理与后处理从明确产物读回，不重写训练循环。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
