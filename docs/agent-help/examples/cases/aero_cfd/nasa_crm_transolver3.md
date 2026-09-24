<!-- dojo-help: {"case_ids": ["aero_cfd.nasa_crm_transolver3"], "domain": "aero_cfd", "kind": "case", "layer": "example", "summary": "外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。", "tasks": ["mesh", "point_fields", "dataset", "model", "application"], "title": "aero_cfd.nasa_crm_transolver3", "topic_id": "case:aero_cfd.nasa_crm_transolver3"} -->
# `aero_cfd.nasa_crm_transolver3`

- 类型：`standalone`
- 用途：外流 CFD 表面预测
- 资源路径：`examples/aero_cfd/nasa_crm_transolver3`

外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：dataset, model, application
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`Transolver-3`
- 数据集：`nasa_crm`
- 入口：`pipeline.py`
- Recipe 来源：`aero_cfd`
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

来源：案例 README；SHA256 `88ec2dbee07fa5bc4f598ab146bd9bb3d1eae95026148edf30dcabc776a2618a`。

### nasa_crm_transolver3

本案例明确使用物理准备、物理训练及完整物理推理；无需设置 topology 来选择执行链。可选拓扑只服务图缓存。独立阶段引用使用 `inputs.train.preparation`、`inputs.infer.checkpoint/preparation` 和 `inputs.post.results`；post 只读固定结果。

一个独立模型实例，使用唯一 aero_cfd recipe 的共享阶段入口。复制本目录，修改数据与运行路径后运行。

- 已有物理 PT：配置 `train.manifest` 后执行 `uv run python pipeline.py`。
- 独立训练消费 `train.preparation`；独立后处理指定 `post.checkpoint`，沿用对应准备。
- 一轮完整训练，最后检查点；固定五个测试样本全点评价。前三个样本用于跨运行图表。
- NASA 只有表面场。汽车 Transolver 表面与体积各使用独立 example，复用同一物理数据。

本期交叉实跑已交付；结果与验收边界见仓库 固定结果与证据清单。

#### 独立推理

`infer.py` 显式配置恢复、预测、评价与保存。设置 `infer.checkpoint`、`infer.preparation`、`infer.samples` 后执行 `uv run python infer.py`；调用 pipeline 时选择包含 infer 的阶段名单。原生 post-only 需要固定结果；明确设置 `post.legacy_predict=true` 才进入历史预测兼容模式，页面不会自动开启。

原生 infer 只解释 infer 参数；后处理以 `post.results` 或 `infer.results` 指向已经完成的 `physical-predictions.json`，不会再次预测。完整物理场五例交付同形预测与物理指标；旧锚点模板保留独立兼容结果，不冒充同一比较口径。进度为 `inference-progress.json`，所有运行文件由 writer 提交，数组写配置指定数据目录。

派生字段例子见 `examples/recipe_extensions/inference_fields/`；详细功能约定见 `docs/PRD/维护源/PRD.md`。

##### 推理字段与指标选择

`infer.fields` 使用 `域:字段:分量`，默认全部真实输出；显式空列表拒绝。`infer.metrics` 默认相对L2、MAE、RMSE、Max Error、R²。选择向量的部分分量仅限制评价，保存保留完整向量。`save_predictions=false`时需关闭`export_vtk`，仍交付轻量指标；新`inference-results.json`与旧结果保持可读，新post不重跑模型。研究者可在物理输出后显式登记派生字段及选择，再配置评价和保存。

普通用户逐场评价扩展示例见 `examples/recipe_extensions/inference_metrics/`。原生后处理缺少固定结果时拒绝；旧计算API保留，历史脚本按固定兼容指纹核验，不改写历史证据。

#### 统一案例契约

- `example_contract_version=1`，`recipe_contract_version=1`；本目录是可在仓库外复制的完整 standalone。
- 阶段顺序由 `pipeline.py` 的普通 Python 表达，YAML 只提供参数、路径和能力选择。每个阶段脚本都通过公开 `ai4e_core.run.launch` 启动。
- 从目录外运行时使用 `python /path/to/nasa_crm_transolver3/pipeline.py`，单阶段可直接运行同目录阶段脚本；配置中的 `inputs.*`、`run_root` 和 `data_root` 是唯一交接路径。
- 需要代码快照、资产、后台运行、停止、恢复或比较时，把同一目录交给 `ai4e_task` Python API；Task 不复制训练循环，也不要求 `task-entry.json`。
- 修改网络、损失、字段、采样、优化器、调度器或 post 后，必须从阶段报告、配置快照、检查点、预测、指标和 post 结果证明新组件实际被调用。
- 恢复要区分重新初始化和完整状态恢复；结构、数据身份或更新策略变化可能使原检查点失效。smoke 只证明流程接线、参数生效和产物交接，不构成精度或论文复现结论。
#### 输入、阶段与产物

- 模型：`Transolver-3`；数据集：`nasa_crm`；依赖：`ai4e-core`、`ai4e-contrib`，以及配置中声明的可选模型依赖。
- 阶段顺序：`rawprep → trainprep → train → infer → post`。单阶段入口是同名 `.py` 文件；参数覆盖使用 `--set`，不通过隐藏任务文件传参。
- 外部输入放在 `inputs.<stage>.<name>`；运行摘要、阶段报告、检查点、预测、指标和 post 派生结果分别从 `run_root`/`data_root` 的固定清单读回。
- 恢复使用阶段 README 和配置声明的 `inputs.*.resume` 或 `checkpoint` 键；模型结构、数据身份、采样或更新策略改变时先做兼容性检查。
- 仅凭文件存在、导入成功或短训退出不能宣称科学精度；smoke 证据与论文级结论分开记录。

#### Agent Help Center

本目录是 `完整案例`。Agent 先读取帮助主题 `case:aero_cfd.nasa_crm_transolver3`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:aero_cfd.nasa_crm_transolver3")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。

数据形态：mesh, point_fields；训练机制：epoch。

##### 具体修改位置

- 数据来源、预算和设备参数先在 `config.yaml` 调整；配置加载规则见 `configuration.py`，步骤调用和返回值交接见 `pipeline.py`。
- 配置已声明的可替换入口：`dataset`、`model`、`application`。读取对应阶段实际消费位置，再替换普通用户函数/对象；名称出现在列表不代表能跳过科学兼容检查。
- 保留原准备引用、训练运行记录与恢复交接；新增输出由计算步骤保存，推理与后处理从明确产物读回，不重写训练循环。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
