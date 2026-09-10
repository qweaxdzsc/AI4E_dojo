# AB-UPT ShapeNet-Car 全流程独立验收（2026-09-09）

最新状态：用户随后要求改用 MPS 并修改个人实验参数。该全流程已成功运行，但“与 Noether 严格数值一致”尚未通过。CPU 证据不能用于替代 MPS 结论；见文末 MPS 个人实验验收。


CPU 验收部分：本次按用户要求实际运行 recipe，并修复差异。初始版本未通过：训练已对齐，但完整流水线在真实表面网格验收时报错，独立后处理的采样与 Noether 不同。修正后，锁定 CPU FP32 配置的默认 `datapre → trainprep → train → post` 全流程通过。

这里的“一致”指同输入和执行配置下的数值、字段、类型与拓扑契约；不指运行 ID、耗时、日志、检查点容器或压缩文件字节完全相同。预测和网格已比较值的差异为 0；汇总指标采用预声明的 `rtol=1e-5, atol=1e-6`，保留实际舍入差异，不写成逐位一致。

## 实跑与证据

- 数据：官方 train 789、test 100，原始目录 `/Users/zonghui/work/datasets/shapenet_car_cfd/mlcfd_data/training_data`。889 个样本逐字段与 Noether 实际 `load_simulation_data` 比较；七个字段中体积法向最大绝对误差 `5.960464477539063e-08`，其余为 0。见 [datapre.json](abupt-end-to-end-results/datapre.json)。
- 准备：889 个样本的实际归一化、自然随机采样、模型输入、目标和随机流推进对照通过；报告所列输入/目标最大绝对误差均为 0。见 [trainprep.json](abupt-end-to-end-results/trainprep.json)。
- 正式训练：dim 192、geometry depth 6、`pscscscscsc`、每域 decoder 12、约 18.6M 参数、batch 1、2 epochs、1578 次有效更新，没有缩网或替身。最终全部权重/缓冲区差异为 0；20 项训练/评估指标通过。见 [training-final.json](abupt-end-to-end-results/training-final.json)。
- 后处理：真实调用 Noether `user_project/infer_shapenet_car.py` 和 `post_vtk_shapenet_car.py`。100 个测试样本的压力、速度、两域锚点坐标、兼容张量包和 200 个点云逐值一致；默认第 0 辆车的表面/体积完整网格，坐标、单元连接、场、原始 ID 与数据类型一致，数值差异为 0。表面输出 3586 点/3584 面，体积 29498 点/26112 体单元。六项物理指标通过；例如压力 MSE 为 Dojo `184.8067756652832`、Noether `184.80677795410156`，差别来自汇总舍入。见 [post-final.json](abupt-end-to-end-results/post-final.json)。
- 真实恢复：新进程的正式网络训练在观察到第 20 次更新后发送 SIGTERM，非零退出并保存轮次起始状态；从该检查点恢复并完成两轮。模型、优化器、EMA、调度器、缩放器、训练计数及 Python/NumPy/Torch 随机状态与连续训练精确相同，恢复后也通过官方最终权重与指标对照。见 [recovery.json](abupt-end-to-end-results/recovery.json) 与 [training-resumed.json](abupt-end-to-end-results/training-resumed.json)。
- 测试：先圈定后处理、归一化、分块缓存、配置交接、恢复及物化路径，103 个相关用例通过；补查旧准备查询接口及默认输入配置，4 个用例通过。合计 107 passed；21 个受影响 Python 文件的 Ruff 检查和格式检查通过。未运行全仓 pytest、mypy 或 Sphinx。见 [tests.json](abupt-end-to-end-results/tests.json) 与 [lint.json](abupt-end-to-end-results/lint.json)。

## 修正内容与职责

1. **原子能力归属。** 冻结变换的组合/重建/摘要与恒等变换迁入 `abilities/transform/normalization.py`；点场通道整理及显式零场派生迁入 `abilities/transform/fields.py`；通用缓存分块查询迁入 `abilities/inference/query.py`。application 保留 aero_cfd 字段、统计来源、数据分片、模型注入及业务装配，旧调用入口继续兼容。AB-UPT 网络仍在 contrib 的 ability，ShapeNet 清单/适配在 contrib 的 application；正式包没有 Noether 依赖。
2. **后处理随机流。** 原默认独立样本采样导致最终锚点和预测不同，压力最大绝对差可达 352.02，但比较的点本身也不同，不能把它解释为模型精度退化。现在默认从相同配置种子重建模型并沿 global 流采样；锚点、网格两条分支隔离，打开评估/保存不会改变另一条输出，退出恢复调用方随机状态。旧 independent 模式仍可显式选择。原差异见 [post-before.json](abupt-end-to-end-results/post-before.json)。
3. **真实网格门禁和格式。** ShapeNet 原始表面存在未被单元引用的点，面提取会移除它们。验收改按提取后的点数，不将正常输出误判失败；补齐点云顶点单元、表面原始点/单元 ID，保留数值类型，消除反变换后强制 float64 造成的误差场舍入差异。修正后的张量、点云和网格已实际读回对照。
4. **可直接运行的样板。** 默认 pipeline 包含 post。预测保留按设计号的具名文件，并额外交付兼容的 `sample_XXXX.pt` 和 `vtk/sample_XXXX_{surface,volume}.vtp`；编号和路径由流程生成。单文件张量包由 data/save 原子提交，application 不自行写张量文件。
5. **输入配置。** 模板移除未来 `train.preparation`、`post.checkpoint` 的空占位及重复查询反变换映射。连续流程自动交接；独立运行时才传入已存在的准备引用或权重。统计数值、摘要、样本输出名均由执行产生。数据/运行根目录属于用户选择；`output_dims` 与监督字段属于预测任务声明，不是要求预填未来预测值。旧准备查询接口也已补齐默认反变换推导，并尊重“不启用物理特征”的配置。

相关 PRD、AGENTS 与模块索引已同步。[source-changes.json](abupt-end-to-end-results/source-changes.json) 记录主要文件相对工作开始快照的摘要；Dojo 当前目录没有 `.git`，因此没有伪造 Git diff 或提交号。

## 环境与参考边界

双方共用 Dojo 的 Python 3.12.14、Torch 2.14.0、NumPy 2.5.3、scikit-learn 1.9.0、VTK 9.7.0、PyG 2.6.1、torch-cluster 1.6.3；CPU FP32、1 线程、零加载子进程、seed 42。正式 recipe 从安装后的包运行，没有源码 PYTHONPATH 或 Noether 运行依赖。

参考是本机锁定 Noether 源码，包含此前已存在的 ShapeNet `surface_area` 排除修正，不能称为干净上游。本轮未修改 Noether 源码；与前轮环境证据记录的参考源码摘要逐文件比较无变化。本次重新运行的官方最终权重也与此前官方重复运行精确相同，沿用原先的容差门槛，没有按 Dojo 偏差放宽。见 [environment.json](abupt-end-to-end-results/environment.json) 与 [tolerance.json](abupt-end-to-end-results/tolerance.json)。

CUDA/AMP/MPS、任意扩展域或改动模型配置不在本次实测结论内。训练是正式网络全官方分片的两轮对照，不是论文收敛精度或生产训练成本证明。完整网格范围与 user_project 默认一致，为测试第 0 辆；锚点评估和预测覆盖全部 100 辆。不把 Noether 工作台的人工云图/报告资产计入此次训练脚本输出，也不声称不同框架检查点容器互换。

## 可复现入口

安装环境后复制 `recipes/aero_cfd`；只改已有原始数据根、数据产物根、运行根，确定性对照额外选择 CPU。用户无需提前知道任何新运行目录或未来权重名。

```bash
OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --no-sync python /tmp/dojo-audit-20260909/recipe-fixed/pipeline.py \
  --set dataset.root=/Users/zonghui/work/datasets/shapenet_car_cfd/mlcfd_data/training_data \
  --set data_root=/tmp/dojo-audit-20260909/final-data \
  --set run_root=/tmp/dojo-audit-20260909/final-runs \
  --set train.device=cpu
```

上面是本次实际命令；重复执行请换新的产物/运行根，默认拒绝覆盖。

参考训练使用 `tools/verification/reference_env.py --noether <Noether根> run_noether_reference.py --dataset <官方preprocessed> --output <参考运行根> --run-id reference`。

真实后处理使用相同环境入口调用 `run_noether_post.py --reference-root <Noether根> --dataset <官方preprocessed> --raw-root <原始数据根> --output <参考运行根> --mode anchors` 或 `--mode mesh`。包装器只统一单进程 CPU 和种子，算法与后处理来自 user_project 实际函数。

结果比较入口为 `compare_training.py compare` 与 `compare_post.py --manifest <Dojo数据清单> --dojo-root <预测根> --reference-run <Noether运行目录> --summary <Dojo summary.json> --output <报告.json>`。均通过 `uv run --no-sync python` 执行；完整参数路径已保存于 JSON 报告。

## 本次产物

- 成功全流程运行：`/tmp/dojo-audit-20260909/final-runs/2026-09-09T10-09-24_1b3717`。
- 模型权重：上述目录的 `checkpoints/last.pt`；配置、源码快照、训练历史及 post 摘要均在同一运行目录。
- 预测及网格：`/tmp/dojo-audit-20260909/final-data/predictions`。
- 参考运行：`/tmp/dojo-audit-20260909/noether-runs/reference`。
- 恢复训练：`/tmp/dojo-audit-20260909/recovery-runs/2026-09-09T10-15-02_01929f`。
- 首次失败与后续诊断、日志、工作前快照保留在 `/tmp/dojo-audit-20260909`；精简验收证据已持久化至本文件旁的 `abupt-end-to-end-results/`，不只依赖临时目录。


## MPS 个人实验验收（2026-09-09）

结论：**复制、改参数、全流程运行已通过；严格数值一致未通过。** 当前不能把这次结果称为与 Noether 完全等价，也不能把两轮闭环验收称为模型已经收敛或达到论文精度。

### 实际用户操作与运行

从 `recipes/aero_cfd/` 复制到 `/tmp/dojo-mps-research-20260909/recipe/`，直接编辑复制目录的 `config.yaml`。除原始数据根、数据输出根与运行根外，实际改动如下：

- `train.device: mps`，`sampling.seed: 17`。
- 学习率 `8e-5`，权重衰减 `0.02`。
- 几何超节点 256，表面锚点 128，体积锚点 192。
- 正式 dim 192、6 层几何、`pscscscscsc`、两域各 12 decoder；两轮、batch 1。
- 后处理选择第 0、7 个测试样本作完整网格查询，块长 4096；所有 100 个测试样本仍做锚点评估、预测保存及点云导出。

复制配置留存于 [user-config.yaml](abupt-mps-results/user-config.yaml)，实际 Noether 参数配对和自动产物交接检查见 [config-check.json](abupt-mps-results/config-check.json)。运行命令为：

```bash
UV_CACHE_DIR=/tmp/dojo-uv-cache uv run --no-sync python /tmp/dojo-mps-research-20260909/recipe/pipeline.py
```

这里使用已安装的 Dojo wheel，不通过额外源码 PYTHONPATH 注入运行。MPS 在桌面沙箱内不可见，实际训练进程在获准访问 Apple GPU 的沙箱外执行；PyTorch 2.14.0、Python 3.12.14、macOS 26.6.2。没有将训练切为 CPU。邻域图检索仍使用 CPU 后端，网络前向、反向及 RoPE 在 MPS；检查点原始 storage 设备也记录了 MPS。

完整成功运行目录：`/tmp/dojo-mps-research-20260909/final-runs/2026-09-09T12-31-02_a4366e`。789 train + 100 test 共 889 样本，1578 次更新。模型权重与缓冲合计 18,641,934 个元素。全流程约 344 秒，训练约 249 秒；该计时不是专用性能基准。见 [运行摘要](abupt-mps-results/run-summary.json)、[训练记录](abupt-mps-results/training.json)、[完整日志](abupt-mps-results/dojo-final.log) 与 [环境及源码指纹](abupt-mps-results/environment.json)。

### 实际差异与修复归属

初次 MPS 训练已完成两轮，但完整网格 post 失败：查询点仍在 CPU，模型在 MPS。修复后重新从原始数据开始跑完整 pipeline 成功。

- **abilities / contrib ability**：补齐检查点的 MPS RNG；独立推理、评估与分支隔离保护 MPS RNG。移除过时的 RoPE CPU 强制迁移，频率和旋转保持模型设备，实际 GPU 前后向已验。旧检查点未记录 MPS RNG，不能追溯补出历史随机状态。
- **aero_cfd application**：原始网格查询坐标随模型设备传递；兼容查询入口同时搬运输入、坐标和可选特征。业务装配复用通用设备搬运与随机保护，不把算法放入 recipe。
- **recipe**：保留薄阶段编排；完善复制后修改个人参数与 MPS 边界说明。YAML 只要求输入、实验选择和输出根；未来统计值、准备摘要、检查点文件名与逐样本结果由流程生成。同权重诊断的 standalone post 才显式传入已存在的检查点。

### 与 Noether 的实测比较

重新读取本次实际产出的 889 个样本，与 Noether 实际原始数据处理器逐字段比较，通过既定容差；仅体积法向最大差 `5.960464477539063e-8`，其余字段为 0。个人采样预算下 889 个样本的归一化、几何超节点索引、两域锚点和监督目标逐项通过，所列输入/目标差为 0，并校验随机流推进。见 [前处理](abupt-mps-results/datapre.json) 与 [准备对照](abupt-mps-results/trainprep.json)。这两个环节本来处理 CPU 数据，不涉及把模型训练改为 CPU。

Noether 使用相同正式模型、个人种子、优化参数、采样预算、两轮及 MPS；未修改参考仓库源码，调用其真实训练与 user_project 后处理。验收工具仅增加配置映射、零数据读取子进程及公开查询块长参数绑定。训练及后处理各在独立进程执行。

1. **Noether 自身重复训练不精确复现。** 两次第二轮在线损失分别为 `0.1931834221`、`0.1911409944`，最终权重最大绝对差 `0.1201690137`。见 [参考训练重复](abupt-mps-results/reference-repeat.json)。严格确定性模式运行直接在 `scatter_reduce_mps` 报错，明确没有确定性实现，见 [确定性失败原始日志](abupt-mps-results/noether-deterministic.log)。没有关闭错误或采用 warn-only 冒充确定性。
2. **独立训练最终结果未达到严格一致。** Dojo 第二轮在线损失 `0.1896246312`；相对第一份参考的最终权重最大差 `0.1201098040`。独立 post 压力 MSE：Dojo `219.9300986`、Noether `221.4880829`；速度 MSE：Dojo `0.65899768`、Noether `0.64251322`。锚点场的最大压力/速度差分别约 `40.6261` / `3.83683`。这些不是逐点舍入级差异，不能宣称模型结果相同。见 [独立权重](abupt-mps-results/independent-weights.json) 与 [独立训练后处理](abupt-mps-results/independent-post.json)。两份参考不足以证明统计精度等价，也不能据此把所有训练差异都归因于设备。
3. **同一权重的推理功能对照。** 仅在验收工具中把 Noether 权重映射进 Dojo 检查点，使用独立 post recipe；此控制实验不替代 Dojo 自己训练出的权重。100 样本锚点坐标、两辆完整网格坐标/拓扑/原始身份与数据类型一致。压力最大绝对差 `7.62939453125e-5`，速度 `7.62939453125e-6`；六项汇总指标均通过原先 `rtol=1e-5, atol=1e-6`，但部分近零点不通过，严格逐点验收仍标记失败。见 [同权重后处理](abupt-mps-results/same-weights-post.json)。
4. **参考自身同权重推理也有逐点波动。** 100 样本重复推理压力最大差 `7.62939453125e-5`，速度 `9.5367431640625e-6`，坐标差为 0；相同容差下 23 个样本字段比较失败。见 [参考同权重重复](abupt-mps-results/reference-inference-repeat.json)。这是差异诊断证据，不是事后放宽容差的通过依据。

### 验收范围

实际 Apple GPU 上 4 个新增相关用例通过：检查点 RNG 恢复、异常退出 RNG 保护、RoPE 设备内前后向、MPS 训练后完整网格查询。另有 39 个相关回归用例通过，4 个硬件用例在沙箱内跳过后已由上述真实 GPU 执行补验。见 [MPS 测试](abupt-mps-results/mps-tests.log)、[相关回归](abupt-mps-results/regression.log)。16 个受影响 Python 文件的 Ruff 检查和格式检查通过，见 [代码检查](abupt-mps-results/lint.json)。本次没有跑全仓测试，也没有把 MPS RNG 单测视为生产规模中断恢复或训练轨迹逐位复现证明。

本轮可确认 MPS 用户流程及上述缺陷已修复；不能签署“独立训练后与 Noether 没有不同”。严格配对还受未提供确定性实现的参考 MPS 池化限制；仅修改 Dojo 的池化算法会改变与原 Noether 的计算路径，因此不能据此宣称已经复现原参考。
