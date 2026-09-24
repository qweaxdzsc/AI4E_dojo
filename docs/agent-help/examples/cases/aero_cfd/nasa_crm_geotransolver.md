<!-- dojo-help: {"case_ids": ["aero_cfd.nasa_crm_geotransolver"], "domain": "aero_cfd", "kind": "case", "layer": "example", "summary": "外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。", "tasks": ["mesh", "point_fields", "dataset", "model", "application"], "title": "aero_cfd.nasa_crm_geotransolver", "topic_id": "case:aero_cfd.nasa_crm_geotransolver"} -->
# `aero_cfd.nasa_crm_geotransolver`

- 类型：`standalone`
- 用途：NASA CRM 表面 Cp 与 Cf 条件点场预测
- 资源路径：`examples/aero_cfd/nasa_crm_geotransolver`

外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：dataset, model, application
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`GeoTransolver`
- 数据集：`nasa_crm`
- 入口：`pipeline.py`
- Recipe 来源：`geotransolver/nasa_crm`
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

来源：案例 README；SHA256 `09c63643b143d7a1393655f4a4619aec47d33e4fc81c884e6bfee7861f2e9c09`。

### GeoTransolver — nasa_crm

普通 PyTorch GALE 的外流基础案例，4 层/128 宽/4 头/64 切片，无局部邻域编码；非论文精度复现。

将 inputs.trainprep.dataset 指向已有物理 manifest；或配置 rawprep 输入并在 pipeline.stages 前加入 rawprep。物理输入必须有逐场 PT、VTKHDF 和实体身份。run_root 与 data_root 指向研究目录，原始数据只读。

通过 `uv run --no-sync python pipeline.py --config config.yaml` 运行；独立阶段使用对应脚本。训练恢复设置 inputs.train.resume；独立 infer 设置 inputs.infer.preparation/checkpoint；post 只需 inputs.post.results。

默认完整分片；本机验收的 2 train/1 test 由外部配置固定。训练每域最多8192查询点，几何最多8192点，推理分块8192、种子42，全点回贴但不等价于全场一次前向。分块与几何预算属于实验设置。

修改 model.supervision 或在 train.py 注入损失；几何/查询配置位于 model.sampling。网络条件与输出顺序由 model.data_specs、trainprep 明确绑定。逐样本物理指标和固定网格由 infer 交付；post 只读结果生成报告和图片。

包入口 ai4e_contrib.application.aero_cfd.geotransolver。Python/Task 可运行，不表示平台模型页登记。

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
