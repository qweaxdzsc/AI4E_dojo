<!-- dojo-help: {"case_ids": ["classic_networks.shapenet_volume"], "domain": "classic_networks", "kind": "case", "layer": "example", "summary": "三维规则格体速度；保留原始物理输入、训练分片统计和固定结果消费。", "tasks": ["regular_grid", "mesh", "point_fields", "model", "derived", "consume"], "title": "classic_networks.shapenet_volume", "topic_id": "case:classic_networks.shapenet_volume"} -->
# `classic_networks.shapenet_volume`

- 类型：`standalone`
- 用途：三维规则格体速度的经典基础结构研究
- 资源路径：`examples/classic_networks/shapenet_volume`

三维规则格体速度；保留原始物理输入、训练分片统计和固定结果消费。

- 数据形态：regular_grid, mesh, point_fields
- 训练机制：iteration
- 替换入口：model, derived, consume
- 限制：当前源码和非训练检查范围；真实训练、安装及完整流程待统一验收。
- 限制：小样本结构集成，不表示论文复现、生产精度或Web模型开放。
- 模型：`MLP/CNN/ResNet/U-Net/Transformer/GNN`
- 数据集：`shapenet_volume`
- 入口：`pipeline.py`
- Recipe 来源：`classic_networks/shapenet_volume`
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

来源：案例 README；SHA256 `24df8481d2823901f4f2ce6c51ff88dfe453c8160b68f86e635292f114abf922`。

### 经典网络：shapenet_volume

从GeoTransolver Darcy完整案例复制后改写。模型与数据连接由贡献层提供，公共block、网络阶段、完整网络和训练由core提供。

配置中显式填写inputs.rawprep.source以及run_root/data_root；所有新数据和训练资产使用独立研究目录。用 `uv run --no-sync python pipeline.py --config config.yaml` 运行；`--set pipeline.stages=[train]` 可选择独立阶段，其inputs需明确绑定。

model.family和model.parameters选择经典结构；components.model可换成本地普通构造函数。构造函数接收model字典并返回普通PyTorch网络。卷积族使用通道在前布局，其他布局由贡献层显式连接。

先集成与非训练检查，主控归并后串行训练；默认100次更新并非论文复现。每组合全部校验累计不超过3小时，测速/两侧/恢复/推理/失败重试共用账本。

修改参数后使用新运行目录；不相容检查点禁止静默部分加载。infer保存反归一化预测、真值、实体和有效域，post只消费固定结果。components.derived与consume允许插入派生数组及独立消费，见network_composition扩展。

运行摘要、检查点和逐字段指标记录本次实际范围；本案例用于小数据结构与功能验证，不声明论文精度或生产精度。

数据使用官方名单排序后的8个训练样本和2个测试样本，各自插值到32³物理包围盒。输入为xyz、原体顶点无符号面距离的线性插值近似及valid；速度三分量是目标。无效格点不参加统计、损失与误差。准备内physical快照保留原网格PT/VTKHDF和身份，不依赖原始来源目录。

推理同时保存规则格结果，以及拼接的original_prediction/target/valid/entity_ids/coordinates与original_offsets。回贴只使用八顶点全部有效的网格单元；post按原样本报告有效支撑区域误差及覆盖率，不把未覆盖点宣称为全点预测。固定结果可独立搬移后评价。
