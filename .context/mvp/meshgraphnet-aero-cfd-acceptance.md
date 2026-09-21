# MeshGraphNet 静态外流案例验收

日期：2026-09-20

## 范围

本轮把 MeshGraphNet 扩展到两个 Python standalone：ShapeNet-Car 的表面压力/体积速度
双域网络，以及 NASA CRM 的表面 Cp/Cf 网络。两例消费平台逐场 PT、VTKHDF、实体身份
与 manifest；图边、诱导子图、核心分区和 halo 在 trainprep 派生。现有 CylinderFlow
Recipe 保持时空轨迹边界，Task 未增加模型分支，Server 模型选择器未登记新模型。

## 已完成的实现

- manifest 可解析已声明的样本网格资产，内容摘要覆盖 PT、VTKHDF 和身份文件；
  `PhysicalView` 向域公开规范网格引用。
- NASA CRM manifest 的 VTKHDF 能力与默认值为 true；rawprep 使用官方 connectivity 与
  每样本坐标写 `surface.vtkhdf`。
- core 提供混合 VTK 单元真实边、诱导子图、稳定 BFS 核心分区、指定跳数 halo，以及
  PT ID/坐标与 VTKHDF 对齐、拓扑摘要缓存和删除后重建。
- contrib 提供静态单域/多域 MeshGraphNet；外流连接负责三维边特征、工况广播、核心
  节点监督、多域损失和无重复完整拼回。
- `aero_cfd` Recipe 由 `trainprep.topology` 选择图路径；缺少该配置的原五例保留原准备、
  训练和锚点推理路径。两个新案例已登记为 standalone。

## 工程证据

证据根目录：

`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_aero_cfd/`

- `shape-smoke/`：仓库外复制案例完成 trainprep、1 epoch 训练、双域完整推理和固定 post。
- `nasa-smoke/`：仓库外复制案例完成 trainprep、1 epoch 训练、表面分区推理和固定 post。
- `shape-independent/`：独立 infer 使用固定准备与检查点成功。
- `shape-post-only/`：临时移走训练检查点后，post 仅凭固定结果成功。
- `shape-resume/` 与 `shape-continuous/`：1→2 恢复与连续两轮的模型、优化器、调度、
  epoch 和 updates 逐值一致。
- `wheel-copy-final-20260920-2/`：隔离 Python 3.12 环境从最终 core/contrib wheel 加载，
  ShapeNet 与 NASA 两个复制案例均完成 trainprep、train、infer、post；平台数据也复制到
  该目录，core 与 contrib 的导入路径均指向隔离 wheel site-packages。修复真实 rawprep
  暴露的 manifest 网格映射后，最终 wheel 位于 `wheels-final-20260920-3/`：core SHA-256
  为 `f9c79df117a66e84c32de53c86f09d403b40bd91b09c5175b60b0711e4c7e644`，contrib 为
  `61baf064da907d0f0f7e206fb005cd4002d3a4e58821d29e3093790bb6610b8c`。

真实数据证据位于 `real-final-20260920-2/`：

- ShapeNet-Car 使用 1 个官方训练样本和 1 个官方测试样本；rawprep 为每个样本交付
  3,586 个表面点、28,504 个体积点、逐场 PT、`surface.vtkhdf`、`volume.vtkhdf` 和
  manifest `meshes` 映射。1 轮短训 1 次更新，随后完整双域推理与固定 post 成功。
- NASA CRM 使用 `Sample002`、`Sample004` 训练，`Sample001` 测试；三个样本均为
  454,404 点并交付 `surface.vtkhdf`。trainprep 从平台资产构图耗时 367.972 秒；1 轮
  训练 2 次样本更新，阶段耗时 851.234 秒、优化计算 568.407 秒、峰值内存约 1.13 GB；
  测试样本完整分区推理耗时 562.321 秒。固定结果 ID 为 0..454,403，唯一值 454,404
  个，Cp/Cf 预测形状分别为 `[454404, 1]`、`[454404, 3]` 且全部有限。

正式 Web 与全表面缓存证据位于
`.context/mvp/meshgraphnet-aero-cfd-results/formal-web/`，完整运行副本位于
`/Users/zonghui/work/project_simulation/dojo_train/meshgraphnet_aero_cfd/formal-web-20260920/`：

- 正式 5173 的 NASA CRM 任务识别 149 个绑定样本，VTKHDF 默认开启，保存后重开保持开启；
  页面可见正式 run `deb40c30c97e45f09216f0b32c820f77`。
- 正式 8000 对 `Sample002` 完成真实 rawprep，产出 8 个独立 PT、`surface_ids.pt`、
  `surface.vtkhdf` 和 manifest `meshes.surface`；网格含 454,404 点、455,304 个单元，
  `ai4e_point_id` 为 0..454,403，全部 PT 数值有限。
- 最终 core 对 454,404 点、1,819,400 条有向边执行 16,384 点核心块与 2 跳 halo：
  28 个核心分区恰好覆盖全部原点，train/infer 相同预算只计算一次；首次 263.497 秒，
  持久缓存重载 0.029 秒，重载结果和两角色结果一致。
- 正式页面首次复验时 5173 已停止，浏览器返回 `ERR_CONNECTION_REFUSED`；按本轮授权恢复
  5173 后在实际 5173/8000 重新通过。8000 使用最终重装的 core/contrib 安装副本。

合成案例只证明连接、更新、恢复、全点覆盖和产物合同，不证明真实数据学习效果。

## 测试状态

通过：

- 最终 MeshGraphNet、平台图准备、两个外流案例及受影响 Transolver/NASA 当前合同：
  56 项；其中旧夹具已区分冻结历史配置与当前 `inputs.<stage>` 配置，阶段产物从公开
  `paths.datasets.*` 读取，未恢复已废弃键。
- Task 资产、执行、Recipe、安装、案例合同及 MeshGraphNet Task：18 项；
- 外流准备、跨模型训练、评价、post 和两个新案例：35 项；
- Web 生产构建通过；`rawprep-consistency.spec.ts` 8 项通过，包括刷新失败不显示成功和
  缺 VTKHDF 键时默认开启。
- 文档导航与案例合同 16 项通过；NASA MeshGraphNet 的 HDF 物理 rawprep 已从共享阶段
  清单移除，未用通用 VTK 目录 rawprep 覆盖它。
- 正式 5173/8000 浏览器冒烟通过，真实平台产物和全表面缓存均已独立读回核验；
- 受影响 Python 文件 Ruff 与 `git diff --check` 通过。

最终 wheel 的首次 ShapeNet 合成运行仍带正式样本名单，因与复制平台样本身份不符而失败；
仅修改该隔离副本的 infer 样本后重跑成功，失败运行保留在同一证据目录。VTK 9.6 的
`SetCells` 弃用警告仍存在，但圈定测试没有 skip 或失败。

## 分层结论

| 证据层 | 状态 | 结论 |
| --- | --- | --- |
| 平台 PT+VTKHDF 契约 | 合成通过 | 网格引用、摘要、复制独立消费和缓存重建已验证 |
| 静态模型与完整拼回 | 合成通过 | ShapeNet 双域和 NASA 表面无遗漏、无重复 |
| 短训与恢复 | 合成通过 | 权重更新；ShapeNet 1→2 状态与连续训练一致 |
| direct-core / 复制 / Task | 通过 | 两复制案例和两项 Task 用例成功 |
| wheel 安装副本 | 通过 | 两案例从隔离 wheel 目录运行 |
| 真实 ShapeNet/NASA 数据 | 通过 | 两例均完成平台 rawprep、短训、完整推理和固定 post |
| NASA 454,404 点推理 | 通过 | 原 ID 无重复无遗漏，Cp/Cf 全部有限，耗时与内存已记录 |
| 生产精度/论文复现 | 未完成 | 论文没有两数据集对应 MeshGraphNet 指标 |
| 正式 Web rawprep | 通过 | 正式安装副本、8000/5173、149 样本、保存重开及真实 PT+VTKHDF 已核验 |
| Web MeshGraphNet train/infer | 未开放 | Server 模型选择器没有登记 MeshGraphNet，本轮仍通过 Python 入口运行 |

## 发布边界

本轮按用户当次授权，以完整 `dev + visualization` 组重装受影响的 core/contrib，更新正式
8000，并在实际 5173 页面完成 NASA rawprep 冒烟；5173 中途停止后也按同一授权恢复并
再次复验。正式 Web 的已验范围是数据绑定、VTKHDF 配置和真实 rawprep 产物。Server 尚未
登记 MeshGraphNet 模型，因此没有从 Web 执行这两个新案例的 trainprep、train 或 infer；
这些阶段的工程证据来自 direct-core、复制案例、Task 和隔离 wheel。生产精度与论文复现
仍未完成。
