<!-- dojo-help: {"case_ids": ["aero_cfd.shapenet_car_meshgraphnet"], "domain": "aero_cfd", "kind": "case", "layer": "example", "summary": "外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。", "tasks": ["mesh", "point_fields", "dataset", "model", "application"], "title": "aero_cfd.shapenet_car_meshgraphnet", "topic_id": "case:aero_cfd.shapenet_car_meshgraphnet"} -->
# `aero_cfd.shapenet_car_meshgraphnet`

- 类型：`standalone`
- 用途：汽车表面压力与体积速度图预测
- 资源路径：`examples/aero_cfd/shapenet_car_meshgraphnet`

外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：dataset, model, application
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`MeshGraphNet`
- 数据集：`shapenet_car`
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

来源：案例 README；SHA256 `273278867c18d8b05e1e33f27ac0d922fffa1ea5131f0414c9bf0e24b893285a`。

### ShapeNet-Car + MeshGraphNet

本案例复用外流 CFD 的完整物理流程。平台数据以独立 PT 和表面/体积 VTKHDF 交付，`trainprep` 从网格派生两个互不连接的图；表面网络预测压力，体积网络预测速度。正式默认隐藏宽度 128、15 层，短训请通过配置同时覆盖 `processor_layers` 与 `halo_hops`。

这是工程扩展案例，不对应 MeshGraphNets 论文指标。

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
