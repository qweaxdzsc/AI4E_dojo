<!-- dojo-help: {"case_ids": ["wdno.burgers_base"], "domain": "wdno", "kind": "case", "layer": "example", "summary": "Burgers时空小波基础预测；可参考网络、目标与局部训练策略替换。", "tasks": ["regular_grid", "field_sequence", "reader", "transform", "network", "objective", "predict", "metrics", "derived"], "title": "wdno.burgers_base", "topic_id": "case:wdno.burgers_base"} -->
# `wdno.burgers_base`

- 类型：`standalone`
- 用途：时空小波预测
- 资源路径：`examples/wdno/burgers_base`

Burgers时空小波基础预测；可参考网络、目标与局部训练策略替换。

- 数据形态：regular_grid, field_sequence
- 训练机制：iteration, diffusion_prediction
- 替换入口：reader, transform, network, objective, predict, metrics, derived
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`WDNO`
- 数据集：`burgers`
- 入口：`pipeline.py`
- Recipe 来源：`wdno`
- 依赖：`ai4e-core`, `ai4e-contrib`

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

来源：案例 README；SHA256 `47cbfe2b6fcc484e57c0705d26d78ed4c3a4626a28e2fa2adcca88983e0e33f3`。

### WDNO Burgers 基础预测案例

本目录可独立复制。公共配置、Task托管、续训、旧配置转换与组件扩展见研究模板（原参考 `../../../维护源/README.md` 未随此帮助交付；实际阶段源码请在复制案例内阅读）；实际数值范围见验收记录（原参考 `../../../运行记录/wdno-acceptance.md` 未随此帮助交付；实际阶段源码请在复制案例内阅读）。

本案例的完整脚本与配置直接复制到研究目录后使用，不需要先从模板替换文件。先填 `inputs.rawprep.source/indices`，分别配置运行和数据目录；CPU小样本验收可显式缩小模型和更新数，默认配置仍保留原基础网络。

可直接执行复制目录的 `pipeline.py`，也可将复制目录传给Task的 `new_task`。分阶段时绑定上一阶段报告给出的文件，不能依赖当前工作目录或“最新文件”查找。当前安装、两个恢复入口及复制品绑定方式见主模板；本例通过 `task_replay --staged --case example` 单独验收，不能以模板成功代替。

#### 统一案例契约

- `example_contract_version=1`，`recipe_contract_version=1`；本目录是可在仓库外复制的完整 standalone。
- 阶段顺序由 `pipeline.py` 的普通 Python 表达，YAML 只提供参数、路径和能力选择。每个阶段脚本都通过公开 `ai4e_core.run.launch` 启动。
- 从目录外运行时使用 `python /path/to/burgers_base/pipeline.py`，单阶段可直接运行同目录阶段脚本；配置中的 `inputs.*`、`run_root` 和 `data_root` 是唯一交接路径。
- 需要代码快照、资产、后台运行、停止、恢复或比较时，把同一目录交给 `ai4e_task` Python API；Task 不复制训练循环，也不要求 `task-entry.json`。
- 修改网络、损失、字段、采样、优化器、调度器或 post 后，必须从阶段报告、配置快照、检查点、预测、指标和 post 结果证明新组件实际被调用。
- 恢复要区分重新初始化和完整状态恢复；结构、数据身份或更新策略变化可能使原检查点失效。smoke 只证明流程接线、参数生效和产物交接，不构成精度或论文复现结论。
#### 输入、阶段与产物

- 模型：`WDNO`；数据集：`burgers`；依赖：`ai4e-core`、`ai4e-contrib`，以及配置中声明的可选模型依赖。
- 阶段顺序：`rawprep → trainprep → train → infer → post`。单阶段入口是同名 `.py` 文件；参数覆盖使用 `--set`，不通过隐藏任务文件传参。
- 外部输入放在 `inputs.<stage>.<name>`；运行摘要、阶段报告、检查点、预测、指标和 post 派生结果分别从 `run_root`/`data_root` 的固定清单读回。
- 恢复使用阶段 README 和配置声明的 `inputs.*.resume` 或 `checkpoint` 键；模型结构、数据身份、采样或更新策略改变时先做兼容性检查。
- 仅凭文件存在、导入成功或短训退出不能宣称科学精度；smoke 证据与论文级结论分开记录。

#### Agent Help Center

本目录是 `完整案例`。Agent 先读取帮助主题 `case:wdno.burgers_base`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:wdno.burgers_base")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

Burgers时空小波基础预测；可参考网络、目标与局部训练策略替换。

数据形态：regular_grid, field_sequence；训练机制：iteration, diffusion_prediction。

##### 具体修改位置

- 数据来源、预算和设备参数先在 `config.yaml` 调整；配置加载规则见 `configuration.py`，步骤调用和返回值交接见 `pipeline.py`。
- 配置已声明的可替换入口：`reader`、`transform`、`network`、`objective`、`predict`、`metrics`、`derived`。读取对应阶段实际消费位置，再替换普通用户函数/对象；名称出现在列表不代表能跳过科学兼容检查。
- 保留原准备引用、训练运行记录与恢复交接；新增输出由计算步骤保存，推理与后处理从明确产物读回，不重写训练循环。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
