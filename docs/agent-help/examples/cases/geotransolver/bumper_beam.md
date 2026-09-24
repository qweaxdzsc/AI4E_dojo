<!-- dojo-help: {"case_ids": ["geotransolver.bumper_beam"], "domain": "geotransolver", "kind": "case", "layer": "example", "summary": "保险杠节点轨迹；保留实体、坐标和条件字段的交接。", "tasks": ["point_fields", "field_sequence", "loss", "derived", "consume"], "title": "geotransolver.bumper_beam", "topic_id": "case:geotransolver.bumper_beam"} -->
# `geotransolver.bumper_beam`

- 类型：`standalone`
- 用途：具名网格场/轨迹预测工程对照
- 资源路径：`examples/geotransolver/bumper_beam`

保险杠节点轨迹；保留实体、坐标和条件字段的交接。

- 数据形态：point_fields, field_sequence
- 训练机制：iteration
- 替换入口：loss, derived, consume
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`GeoTransolver`
- 数据集：`bumper_beam`
- 入口：`pipeline.py`
- Recipe 来源：`geotransolver/bumper_beam`
- 依赖：`ai4e-core`, `ai4e-contrib[geotransolver]`

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

来源：案例 README；SHA256 `91b1eba08cdac4b8de2d8a45ff02bb0fca8a1b66213ac4f3f0f820bed054c3aa`。

### GeoTransolver bumper_beam

可复制的五阶段 Python 研究案例。设置 `inputs.rawprep.source`、`run_root` 和 `data_root` 后，以 `uv run --no-sync python pipeline.py --config config.yaml` 执行。原始数据只读，所有输出使用独立数据根。

保险杠124训练/7验证；共同11帧，预测10帧全部节点；6层基础256宽，多尺度后320宽。

默认20更新及120秒用于短检查，超过阶段预算会保存检查点并失败；恢复设置 `inputs.train.resume` 和累计目标 `train.updates`。调度沿原实验总轮次，短训不压缩日程。论文精度未复现。

独立 post 仅设置 `inputs.post.results` 并选择 `[post]`，无需原数据或网络；可在 `components.loss/derived/consume` 替换普通函数。安装依赖选择 `ai4e-contrib[geotransolver]`，运行不依赖 PhysicsNeMo。

<!-- research-adaptation-details -->
#### 选择与改写说明

保险杠节点轨迹；保留实体、坐标和条件字段的交接。

数据形态：point_fields, field_sequence；训练机制：iteration。

##### 具体修改位置

- 数据来源、预算和设备参数先在 `config.yaml` 调整；配置加载规则见 `configuration.py`，步骤调用和返回值交接见 `pipeline.py`。
- 配置已声明的可替换入口：`loss`、`derived`、`consume`。读取对应阶段实际消费位置，再替换普通用户函数/对象；名称出现在列表不代表能跳过科学兼容检查。
- 保留原准备引用、训练运行记录与恢复交接；新增输出由计算步骤保存，推理与后处理从明确产物读回，不重写训练循环。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
