# MeshGraphNets / CylinderFlow 接入验收

日期：2026-09-20

## 范围与结论

本轮完成固定二维网格 CylinderFlow 的代码工程闭环：官方 TFRecord 解码、轨迹准备、
MeshGraphNet 训练、检查点恢复、多步 rollout、DeepMind 名称的累计 MSE、固定结果 post，
以及直接 Recipe 和现有 Task 托管。没有接入 Web/Server 模型分支，也没有操作正式
8000/5173。

当前结论只覆盖工程连通性、安装包、真实单条官方轨迹解析和合成小样本短训。DeepMind
TensorFlow 权重逐值对照、原实现完整训练、完整 CylinderFlow 分片、多轨迹论文评价及
论文表格精度均未完成，不能称为论文复现。

## 参考身份

- DeepMind 仓库 master 在核对时的 commit：
  `f5de0ede8430809180254ee957abf36ed62579ef`。
- 锁定核对 `core_model.py`、`cfd_model.py`、`cfd_eval.py`、`dataset.py`、
  `normalization.py`；文件摘要写入模型 `source.json`。
- PhysicsNeMo 本地参考 commit：
  `aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1`。只用于 PyTorch 结构核对，
  不作为 Dojo 运行依赖或 DeepMind 数值等价证明。
- DeepMind CFD 默认协议：隐藏宽度 128、两层隐藏 MLP、15 个消息传递 block、
  sum 聚合、ReLU、LayerNorm、batch 2、Normal 节点速度噪声 0.02、前 1000 步
  只累计统计、总目标一千万步。

## 工程与科学口径

- core 提供 TFRecord framing/CRC、bytes feature、三角形双向边、sender-receiver
  边特征、变长图收批、边后节点消息传递、在线归一化、噪声、masked loss、rollout
  和累计 horizon MSE，不认识 CylinderFlow 或 MeshGraphNet。
- contrib 模型保存 Encoder/Processor/Decoder；CylinderFlow adapter 解释官方
  meta/字段、九类节点和固定轨迹；领域连接绑定完整 11 维节点归一化、Normal 噪声、
  Normal/Outflow loss、速度增量及边界保持。
- `mse_H_steps` 按 DeepMind `cfd_eval.py` 对第 1 到 H 个预测帧累计求均值；初始帧
  排除。此前把指标解释为单独第 H 帧的实现已纠正。
- 完整轨迹评价先按 DeepMind `dataset.add_targets` 取原始帧 `1..T-2`，以第 1 帧为
  rollout 初态并在指标中排除；不会把原始第 0 帧误作 CFD 评价初态。
- post 只读 infer 已保存的固定 rollout 与指标，不重新运行模型或重新评价。

## 真实数据证据

从官方 CylinderFlow train TFRecord 以 HTTP range 保存首条完整记录：

- 路径：`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_real_one/`
- TFRecord 大小：13,572,077 bytes；SHA-256：
  `7b067317f6cf3f72cc950b3ebe9b5325ec0d7d68ed1be728fd8202d04a5c89b1`
- 解码结果：600 帧、1876 节点、3518 个三角形、10788 条双向边。
- 以 16 隐宽、1 个 processor block 完成一个真实帧前向 loss 和 2 步 rollout，
  输出 shape `(3, 1876, 2)` 且全部有限。

这证明官方记录协议和真实网格可以被当前 adapter 消费，不证明完整数据集吞吐、训练
收敛或论文精度。

## 安装与测试

`ai4e-core` 和 `ai4e-contrib` 由当前源码构建 wheel，并以 `--no-deps` 定点更新 `.venv`
安装副本；没有运行 `uv sync`，没有重启正式服务。wheel 位于：

`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_wheels_20260920_4/`

- `ai4e_core` SHA-256：
  `c7be9ec0735125653525ca419426f934e3c4d5185ed7102135b900c52601e794`
- `ai4e_contrib` SHA-256：
  `30173ddd98a89960f199f328dbc19c6f828e1f01cdd5b9cb26e10ef9bc8a8e56`

仓库外复制安装与五阶段运行目录：

`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_wheel_copy_20260920_4/`

最终圈定测试从 `_4` wheel 隔离安装目录加载 core/contrib，结果为 23 passed，1 个既有
Torch JIT 弃用警告。覆盖 core 图/归一化/
累计指标、TFRecord 和轨迹解码、直接 Recipe、Task 托管、固定 post、检查点 fork 内容
校验及 1→2 更新恢复。

把架构与 Recipe 文档契约加入同一集合后为 30 passed、1 个相同警告。

最终 Task 实跑证据位于
`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_task_20260920_4/REPORT.json`：
run `c2fa8d2fa41f44bda925cb22a657b227` 五阶段成功；writer 登记准备清单、固定检查点、
rollout 结果、rollout 指标及其依赖摘要；fork 后检查点为 `portable=true`、
`external=false`，并已由圈定测试逐字节比较。

扩大 Task 公共回归结果为 30 passed、1 failed；失败是既有外流用例
`test_formal_recipe_new_fork_train_post` 的 `asset_copy_not_portable: use reference fork`，
不经过 MeshGraphNet 代码。本轮没有修改该并行工作。时空/控制回归结果为 55 passed、
2 skipped、6 failed、4 errors；未通过项均在收集或导入阶段缺少主环境可选依赖
`ema_pytorch` 或 `pytorch_wavelets`，没有为此运行 `uv sync`，因此这些回归不能记为通过。

## 分层状态

| 证据层 | 状态 | 当前证据 |
| --- | --- | --- |
| 工程连通性 | 通过 | 五阶段直接 Recipe 与 Task 托管 |
| 安装和复制 | 通过 | core/contrib wheel 安装；Task 从复制 Recipe 运行 |
| 官方数据协议 | 部分通过 | 官方 train 首条完整轨迹解析与短 rollout |
| 固定输入状态/预测对照 | 未完成 | 未运行 DeepMind TensorFlow 与 Dojo 同权重逐值对照 |
| 短训学习效果 | 未评价 | smoke 只执行极少更新，不推断学习效果 |
| 连续训练和恢复 | 工程通过 | 合成小样本 1→2 更新恢复；未做长程状态对照 |
| 多步 rollout | 工程通过 | 合成 Recipe 和真实单轨迹 2 步有限输出 |
| 论文指标口径 | 实现对齐 | `cfd_eval.py` 累计 horizon 定义；未跑完整评价集 |
| 论文级完整复现 | 未完成 | 原实现完整训练、同数据足够预算与论文 RMSE 均未执行 |

## 未运行和限制

- 未下载约 16.4 GB 完整 CylinderFlow 数据集；未运行 train/valid/test 全分片。
- 未安装 TensorFlow 1/Sonnet 参考环境，未运行原 DeepMind 固定输入或权重对照。
- 未运行一千万更新、十条 rollout 或论文误差条；论文表格指标没有达成证据。
- 未把 PhysicsNeMo 压力输出或预计算统计迁入 Dojo。
- 训练流采用可恢复的全排列，不逐步复刻 TensorFlow `shuffle(10000)`；因此即使其他参数
  相同，也不能声称与 DeepMind 原训练随机状态逐步一致。
- 未运行 Web/Server/e2e；本期没有对应消费链。
