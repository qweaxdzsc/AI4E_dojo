<!-- dojo-help: {"case_ids": ["aero_cfd.nasa_crm_meshgraphnet"], "domain": "aero_cfd", "kind": "case", "layer": "example", "summary": "外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。", "tasks": ["mesh", "point_fields", "dataset", "model", "application"], "title": "aero_cfd.nasa_crm_meshgraphnet", "topic_id": "case:aero_cfd.nasa_crm_meshgraphnet"} -->
# `aero_cfd.nasa_crm_meshgraphnet`

- 类型：`standalone`
- 用途：NASA CRM 表面 Cp 与 Cf 分区图预测
- 资源路径：`examples/aero_cfd/nasa_crm_meshgraphnet`

外流网格和逐点物理场；保留准备、训练、固定推理与后处理交接。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：dataset, model, application
- 限制：数据字段、科学目标与检查点兼容性按本案例定义；不能直接套到另一任务。
- 限制：工程运行、缩小预算与论文精度范围以案例正文和对应证据为准。
- 模型：`MeshGraphNet`
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

来源：案例 README；SHA256 `7497e61ce275246d509ae8b08cc9f151dd5e9c798b4e2a0aaa0c5fb8d2861687`。

### NASA CRM + MeshGraphNet

本案例把 NASA 官方 connectivity 在 rawprep 中固化为 `surface.vtkhdf`，后续 `trainprep` 只消费平台 PT、VTKHDF 和实体身份。一个表面 MeshGraphNet 预测 Cp 与三分量 Cf；默认核心块 16,384 点、15 层 Processor 和 15 跳 halo。

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
