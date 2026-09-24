# GeoTransolver bumper_beam

可复制的五阶段 Python 研究案例。设置 `inputs.rawprep.source`、`run_root` 和 `data_root` 后，以 `uv run --no-sync python pipeline.py --config config.yaml` 执行。原始数据只读，所有输出使用独立数据根。

保险杠124训练/7验证；共同11帧，预测10帧全部节点；6层基础256宽，多尺度后320宽。

默认20更新及120秒用于短检查，超过阶段预算会保存检查点并失败；恢复设置 `inputs.train.resume` 和累计目标 `train.updates`。调度沿原实验总轮次，短训不压缩日程。论文精度未复现。

独立 post 仅设置 `inputs.post.results` 并选择 `[post]`，无需原数据或网络；可在 `components.loss/derived/consume` 替换普通函数。安装依赖选择 `ai4e-contrib[geotransolver]`，运行不依赖 PhysicsNeMo。

<!-- research-adaptation-details -->
## 选择与改写说明

保险杠节点轨迹；保留实体、坐标和条件字段的交接。

数据形态：point_fields, field_sequence；训练机制：iteration。

### 具体修改位置

- 数据来源、预算和设备参数先在 `config.yaml` 调整；配置加载规则见 `configuration.py`，步骤调用和返回值交接见 `pipeline.py`。
- 配置已声明的可替换入口：`loss`、`derived`、`consume`。读取对应阶段实际消费位置，再替换普通用户函数/对象；名称出现在列表不代表能跳过科学兼容检查。
- 保留原准备引用、训练运行记录与恢复交接；新增输出由计算步骤保存，推理与后处理从明确产物读回，不重写训练循环。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
