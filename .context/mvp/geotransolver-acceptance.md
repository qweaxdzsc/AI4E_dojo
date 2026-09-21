# GeoTransolver core 优先工程迁移验收

状态：本次 core 优先工程迁移范围已交付，真实成对短训、完整评价、实际安装、双案例/扩展、恢复及资产搬移通过。相关兼容性回归通过，现存其他案例问题单列如下。论文精度未复现。本期仅 Python / recipe / Task，不登记 Web，未操作正式 8000 / 5173 或重装其环境。

## 来源与归属

参考 PhysicsNeMo 固定提交 `aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1`。参考工具独立提取并执行上游数值定义，与提交逐字核验；不导入 Dojo 数值实现。设备、时间字段修正和实验身份见 `tools/verification/geotransolver/reference_patches.md`。

实际计算落在 core：MAT/时间字段、实体校验、PT/VTKHDF/缓存、统计与布局变换、规则采样、半径查询、投影/切片/GALE/上下文/局部编码、损失、参数划分、组合优化器、调度与恢复、具名预测、逐帧评价、绘图和报告。核心类可用普通张量及无关小网络独立调用，core 无反向 contrib 导入。

contrib 仅保留 GeoTransolver 网络组合、模型参数与优化策略选择，以及 Darcy/保险杠文件字段与科学语义绑定。领域 application 增加具名场与轨迹入口，保留原 u/f 函数。普通组件无需继承新协议。

core 和 contrib wheel 分别包含来源许可及摘要；本次 `source.json` 的目标摘要与最终迁入文件核验。贡献包现有 Notice 是文件，因此模型许可放在 `ability/model/geotransolver/LICENSE`，没有把原 Notice 改为目录。

## 数据与固定实验

原始来源只读：`/Users/zonghui/work/datasets/darcy_flow/` 和 `bumper_beam_crash/`。全部运行、准备、检查点、预测和验收记录位于 `/Users/zonghui/work/project_simulation/dojo_train/geotransolver/`。

- Darcy：smooth1 前 1000 训练、smooth2 前 200 评价。物理准备保留 421×421 原始数组精度和二维拓扑，模型准备统一采样到 85×85，保持上游 xy 坐标顺序。4 层、hidden 128、4 heads、64 slices。每侧 5 轮 / 1250 更新，batch 4。
- 保险杠：公开分片 124 训练 / 7 验证，13676 个节点。共同 11 帧 0–100 ms，预测后续 10 帧；来源中额外 110 ms 帧仍保留在物理准备。6 层、基础 hidden 256、多尺度后 320、8 heads、128 slices，半径 0.05/0.25、邻居 8/32。每侧 5 轮 / 620 更新，batch 1。
- 正式全网络、完整网格测速后冻结两侧相同预算，保留 50% 余量；未通过削减网络、节点或评价样本达成时间目标。MPS float32 学习，CPU float64 复算最终物理指标。
- PT、VTKHDF、点/单元身份与相对网格清单同时交付；转点场、采样和邻域仅属于模型准备。VTKHDF 使用稳定字段键，清单保留原科学字段名，避免时间字段中的小数点被改名。
- 两个数据集全部样本的输入、目标与独立原读取器/统计实现逐值一致。保险杠上游读取器漏帧修正先于模型对比。

实测存储：Darcy 原始归档与解压副本约 6.3 GiB，保险杠约 15 GiB，分别低于 20 GB 量级要求；展开的 PT/VTKHDF、检查点、保留的失败数据与多次 Task 复制验收共约 **109 GiB**。20 GB 原始数据约束不等于完整实验工作目录大小。后续训练/推理优先直接绑定已有准备清单，不重复运行 rawprep。

固定配置及准备路径：外部工作根的 `implementation/frozen-protocol.json`、`implementation/preparations.json`。失败的初版 Darcy 坐标准备、VTKHDF 字段读取及其他失败记录均保留，不能用作最终科学证据。

## 数值结果

Darcy 200 例完整评价：平均物理逐样本相对 L2 **0.04817357948490411**，物理 MSE `1.1610311724311282e-07`。训练首/末损失 0.5576279163 / 0.0453246087。参考与 Dojo 最终权重、完整损失历史、全部预测最大差值均 **0**。证据 `darcy/comparison.json`。

保险杠 7 例完整评价：参考归一化 MSE **0.08361096600336689**，训练首/末损失 0.9317142963 / 0.0757355243。参考与 Dojo 最终权重、完整损失历史、全部预测最大差值均 **0**。证据 `bumper_beam/comparison.json`。后处理另按位置、应变、应力分别交付物理单位指标；跨通道整体 MSE 混合单位，不作为单一物理精度结论。

完整模型结构的小空间 CPU float32 前向、逐块中间量、梯度及 Muon/AdamW 单步更新对照差值均为 0；固定容差 `atol=1e-6, rtol=1e-5` 未放宽。上述与学习效果是工程证据，**不等于论文复现**：原 Transolver Darcy 0.0057 不是本次短训通过线，公开 131 例保险杠也不同于论文 135 例设置。

## 公开入口、安装与资产

`recipes/geotransolver/{darcy,bumper_beam}` 与对应 examples 均为九文件完整流程。Python 决定阶段连接，YAML 仅提供参数。扩展示例真实替换损失、保存 signed_error，并由独立 post 读回。Task 沿现有案例发现和执行，不增加模型分支。

真实构建并安装 spec/core/contrib/task 四个 wheel 到独立 `installed/venv`；复用本机第三方依赖，四个 Dojo 包均来自该环境的 wheel，不读取仓库源码包。控制器与实际 worker 的解释器/模块位置存入验收记录。网络无需 PhysicsNeMo 安装。

最终复制案例记录在 `installed-replay-final/{darcy,bumper_beam,darcy-extension}/acceptance.json`：两步 direct-core/Task 的模型、优化器、调度器、随机样本游标、损失与全量预测一致；两步恢复到三步并与连续三步比较；固定结果整体复制后隐藏原目录，独立 post 仍成功，不运行模型。扩展数值变化见 `installed-replay-final/extension-comparison.json`。

真实 Task 资产额外覆盖：trainprep worker 交付完整准备；share_run_asset 复制 bundle；fork_task 复制准备与检查点；隐藏来源后子任务推理；共享固定结果并再次隐藏原结果，post 单独消费。记录为各案例 `asset-acceptance.json`。

此过程修复通用 Task 输入改绑问题：当继承引用已不指向当前路径时先清除旧候选，重新匹配共享资产，保留新 bundle 的完整依赖。未新增 GeoTransolver 判断，也不批量改写历史任务。旧验收脚本与本轮新增 cache_spec 参数不匹配的失败记录保留，最终验证重新从当前 wheel 复制案例。

## 验证与预算

最终集合：`test_geotransolver_*.py`（33 项全部通过），以及共享训练执行/策略扩展、固定用户源码与实际 wheel、Task 资产/执行、案例契约与 Agent Help。完整一轮 74 项得到 72 通过、2 失败、0 跳过；日志 `implementation/final-tests.txt`。

- GeoTransolver 全部 33 项已通过，真实 Task/安装门禁已显式提供实际产物，没有 skip。Task 改绑回归与完整来源隔离实跑均通过。
- WDNO 安装策略回归首轮因主环境缺少可选 `pytorch_wavelets` 失败，使用现有 PCNO 隔离解释器补跑，不修改主环境，补验 **1 项通过**，结果见 `implementation/wdno-regression.txt`。因此合计 73 个唯一用例通过，1 个现存其他案例用例失败，0 跳过。
- 唯一剩余的其他案例问题为 `test_declared_recipe_stage_files_are_byte_identical`：当前工作区 `aero_cfd.nasa_crm_meshgraphnet/rawprep.py` 与它声明的公共模板不同。本次未改写该并行工作；GeoTransolver 两套九文件副本的一致性单独验收通过。因此不能声明全仓或全部案例验收通过。
- 106 个本次 Python 文件 ruff 检查与格式检查通过；Task 小范围修改另经 ruff。453 个帮助生成文件当前性及嵌套案例关联测试通过。固定用户源码基线未改。未运行全仓 pytest/mypy/Sphinx 或 Web 验收。

最终累计计算 **2071.86 秒（34.53 分钟）**，小于 180 分钟上限。计算账本 `compute-budget.json` 统一包含准备、审计、测速、参考/Dojo 训练、失败重试、安装后计算、资产复制和测试；写代码时间不计数。160 分钟后禁止新训练，180 分钟硬截止；假时钟覆盖失败、重试、孤儿记录、取消和截止。未给每个案例或每侧重新分配三小时。

## 使用入口与边界

使用说明：`docs/agent-help/workflows/geotransolver.md`。运行默认 20 更新 / 120 秒，科学设置与本次完整五轮验证分别记录。恢复使用累计 `train.updates` 与 `inputs.train.resume`。独立 post 只需固定结果清单，来源数组/网格可整体搬移。

首期支持普通 PyTorch GALE、CPU/MPS float32 和二维结构路径。TE、plus、concrete dropout、GALE_FA、时间输入、激活检查点及三维结构分支明确拒绝。CUDA、其他优化分支、平台页面和论文精度均不在本期验收范围。


## 2026-09-21 用户授权的磁盘清理

清理两套 installed-replay 测试项目、pytest 临时目录、临时安装 venv，以及已替代的 Darcy 初版与保险杠失败准备，共减少约 **73.55 GiB**，实验目录剩余约 **35.41 GiB**。原始 datasets、正确物理/模型准备、参考与 Dojo 五轮权重、正式固定预测及报告保留，相关数组和检查点存在性已核验。

删除前轻量证据按原相对路径归档到 `/Users/zonghui/work/project_simulation/dojo_train/geotransolver/cleanup-20260921/test-evidence.tar.gz`（6235 文件，逐项 SHA256 校验）；删除清单见同目录 `cleanup.json`。本页上方及 delivery.json 保留历史验收事实；被清理的测试目录和临时解释器已不可直接重放，需重新安装/物化。该归档只保存轻量证据，不保存已清理的测试张量/网格。未更改模型源码、原始数据、其他模型实验或正式服务。


### 同日追加：仅保留平台与可复用资产

按用户追加要求，进一步删除外部实验目录中的参考训练权重、旧推理副本、对照/预算记录、安装wheel、测试归档、清理脚本及一次性论文提取文本。第一轮清理归档和上述历史证据路径现已删除，不再宣称其仍可读取；平台源码和 datasets 原始数据未动。

当前实验目录仅保留正确物理/模型准备、最终Dojo五轮检查点及其配置/训练摘要、固定预测和报告。可用路径统一见 `/Users/zonghui/work/project_simulation/dojo_train/geotransolver/reusable.json`，使用说明见同目录 README.md。保留的分片数组、检查点及预测数组存在性已检查。此次再减少约0.70 GiB，目录剩余约34.71 GiB，主要为可复用的PT/VTKHDF及模型准备；不改写冻结产物内容或原路径。
