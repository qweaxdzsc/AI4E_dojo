# Aero CFD 全流程 Recipe

安装仓库 workspace 后，可将本目录整体复制到任意工作目录；模板无需安装。

```bash
uv sync
uv run python pipeline.py --config config.yaml
uv run python rawprep.py --config config.yaml --check
```

在仓库外使用时，以已安装 ai4e-core/ai4e-contrib 的 Python 环境运行；uv 可用 `--active` 使用该环境。脚本默认读取旁边的 config.yaml，不依赖当前工作目录。

先修改 `dataset.root`（原始数据）、`data_root`（产物）、`run_root`（运行记录）。`${data_root}/train` 等路径支持任意配置变量插值；各分片可单独改为绝对路径，相对路径以配置文件为基准。

`dataset.samples: all` 使用已选分片的全部样本，也可填样本 ID 列表。`dataset.partition: official` 使用官方名单，也可填 `train: [param0/...]`、`test: [...]` 映射或名单 YAML 路径。仅处理 test 时将 rawprep.statistics.mode 改为 reference 或 none；fit 要求非空完整 train。

`rawprep.fields` 选择特征与 components，可覆盖 array/association；精确字段与来源见 contrib/application/datasets/shapenet_car/manifest.yaml。`rawprep.geometry`、`rawprep.filters` 和 `rawprep.save_fields` 显示实验选择。未知字段或维度报错，不猜数组。

`--set data_root=/shared/data/new` 覆盖配置；`--overwrite` 显式允许替换；`--continue-on-error` 继续处理剩余样本但仍返回失败。默认不覆盖已有产物。覆盖前撤下旧完整清单并保留备份，部分失败后不能将旧清单当成完整有效版本。

实际 .pt 在 train/test 子目录；统计在 train/statistics.yaml；数据根的 manifest.json 是读盘入口。运行记录独立，inputs/config.yaml 为唯一的最终生效配置，logs/run.log 是能力和进度日志，异常堆栈见 errors.log。训练启动另写 code.tar.gz 源码快照。额外的用户组件模块通过 `snapshot_modules` 显式列出，以收入同次源码快照。normalize 路径保存冻结变换记录；仅 trainprep.normalization.materialize=true 时生成归一化张量。

几何可使用能力列表，也可写参数映射，例如 `nearest_vertex: {epsilon: 1.0e-6}`；未启用的能力不计算，未知参数拒绝。法向、点到面和最近顶点的 epsilon 允许显式设置。

## 准备与训练实施状态

默认 pipeline 依次执行 rawprep、trainprep、train、post。各脚本也可分别运行；train 默认实际拟合。rawprep 调用库既有 datapre 业务方法，文件名不约束库接口。trainprep 写出准备引用，冻结归一化和数据内容摘要，train 消费前校验；每次训练迭代仍动态采样。默认与官方 ShapeNet-Car 预设一致，保留未激活的特征投影参数，以保证初始化随机流一致。旧阶段名 `pre` 已移除，请改用 `rawprep`。

配置只描述用户输入和实验选择：无需预填统计数值、准备摘要、将来的检查点或预测文件名。完整 pipeline 自动交接这些结果；独立运行 train/post 时，才用 `train.preparation` / `post.checkpoint` 指向已经存在的产物。`model.data_specs.output_dims` 是要预测什么的任务声明，不是要求填写未来预测值。

模型结构版本 3 修正了 RMSNorm、默认绝对位置编码、联合投影和初始化顺序。旧结构权重不能直接续训。逐阶段和完整参考训练证据见 [参考验收](../../.context/mvp/abupt-reference-acceptance.md)。

## AB-UPT 依赖安装

仓库 uv 下载源采用已验证可用的阿里云镜像。PyG 固定 2.6.1：原网络依赖 torch-cluster，PyG 2.8 已迁移到 pyg-lib 后端。仅 torch-scatter、torch-cluster 关闭构建隔离以复用本环境的 Torch；其他包仍正常隔离构建。

```bash
uv sync --locked --all-packages --all-extras
uv run --locked --all-packages --all-extras pytest tests/integration/test_abupt_components.py tests/integration/test_train_abupt_real.py -q
```

执行 train.py 同样带 `--all-packages --all-extras`，避免默认同步移除未启用的模型可选依赖。当前验证环境为 Python 3.12.14、Torch 2.14.0、macOS ARM。Noether 的 Torch 2.11.0 属于另一虚拟环境，不作为此包的运行依赖。

如需 pip 备用安装，应先完成基础 workspace 安装，再运行：

```bash
uv run --no-sync python -m ensurepip
uv run --no-sync python -m pip install --no-build-isolation 'einops>=0.8' 'torch-geometric==2.6.1' 'torch-scatter==2.1.2' 'torch-cluster==1.6.3'
```

本机 pip 已配置同一镜像；其他机器须自行确认可访问的下载源。

## 逐步运行

在仓库根目录执行（先修改案例数据路径）：

```bash
uv run --no-sync python recipes/aero_cfd/rawprep.py --config /path/to/config.yaml
uv run --no-sync python recipes/aero_cfd/trainprep.py --config /path/to/config.yaml
uv run --no-sync python recipes/aero_cfd/train.py --config /path/to/config.yaml --set train.preparation=/path/to/trainprep-run/artifacts/preparation.json
uv run --no-sync python recipes/aero_cfd/pipeline.py --config /path/to/config.yaml
```

独立运行 rawprep 后，数据清单位于 `${data_root}/manifest.json`。trainprep 的运行摘要给出 `artifacts/preparation.json` 绝对路径。train 的结果位于该次运行的 `artifacts/training.json`，权重与恢复状态位于 `checkpoints/{best,latest,last}.pt`。连续入口把上述引用直接交接；已有数据时可设置 `pipeline.stages=[trainprep,train]`。三个入口的运行目录都在 `run_root` 下，具体子目录在启动日志显示。


`train.device` 默认 `auto`：有 CUDA 用 CUDA，否则 MPS，再否则警告后用 CPU。可显式写成 `cpu`、`cuda`、`mps` 或 `gpu`（映射为 CUDA）；点名设备不可用会失败。

Apple GPU 实验请在复制后的 `config.yaml` 中明确设置 `train.device: mps`，并修改自己的 `sampling.seed`、`train.learning_rate`、`train.weight_decay` 与域采样预算。无需预填将来的检查点、统计值或输出文件名。当前 PyTorch 2.14.0 的 MPS 已实跑完整模型两轮及后处理；邻域检索在 CPU，网络前后向与复数旋转在 MPS。MPS 池化内核不支持确定性执行，同种子训练也可能不同；实验比较须同时记录设备和重复运行结果。详见仓库 `.context/mvp/abupt-end-to-end-acceptance.md` 的 MPS 验收。

post 的 `post.random_stream` 默认 global；每次独立后处理从 `sampling.seed` 开始重建模型和采样，与锁定 Noether 的独立推理一致。锚点分支与网格分支隔离随机状态，打开评估或保存不会改变网格预测，结束后恢复调用方随机状态。需要旧的按样本独立采样时可显式设为 independent。

`train.log_every` 为进度日志的轮次间隔，必须为正；最终轮次始终报告，每轮评估和检查点不受日志频率影响。`train.log_every_updates` 默认为空，不按更新打进度；需要时才写出窗口平均的在线损失。

续训设置 `train.resume` 为可信本地 latest.pt 路径，预热余弦保持最初计划总轮数，恒定调度可将 `train.max_epochs` 设为新的总轮数。默认 best 使用 test；显式 eval 缺分片会失败。`--dry-run` 在 fit 下只进行准备检查，不更新模型或写检查点、归一化资产。

本期逐项结果及完整复跑命令见 [验收记录](../../.context/mvp/abupt-acceptance.md)。

## 多域输入与缓存查询

多域 AB-UPT 使用结构版本 3：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。

新案例配置使用 `model.data_specs`、`model.supervision`、`trainprep`、`sampling.domains`。`post.py` 经现有会话执行：默认对 test 做锚点评估并保存预测，可选写出锚点点云，并按测试下标把预测画回原始网格。`post.checkpoint` 可空（同一 pipeline 下使用本次 `last`）或指向 `best`/`latest`/显式路径。默认只处理 `post.sample_indices=[0]`，查询块长为 `post.query_chunk_size=16384`。完整网格写在数据目录 `predictions/mesh_vtk/`，文件名为 `sample_XXXX_surface.vtp` / `sample_XXXX_volume.vtu`，不覆盖锚点目录。检查模式只核对接得上，不写网格。默认 pipeline 为 rawprep/trainprep/train/post；仅训练时可显式去掉 post。旧五键入口和旧模型检查点已移除。

```bash
uv run --all-packages --all-extras python recipes/aero_cfd/post.py --set post.checkpoint=/path/to/last.pt
```

后处理同时保留按设计号的具名张量，并交付兼容 `sample_XXXX.pt` 张量包和 `vtk/sample_XXXX_{surface,volume}.vtp`。点云含独立顶点单元，无面或体连接；完整表面网格保留原始点/单元 ID，未引用顶点按面提取规则移除。实际全流程对照见 [端到端验收](../../.context/mvp/abupt-end-to-end-acceptance.md)。


后处理失败时，查看运行目录中的 `artifacts/post-progress.json`：评估、预测保存与网格查询分别列出状态、完成数和已提交路径。网格失败仍使整次运行失败，但已完成的锚点不会被抹去。只补网格时，在复制目录运行：

```bash
uv run --no-sync python post.py --set post.checkpoint=/已有运行/checkpoints/last.pt --set post.evaluate=false --set post.save_predictions=false --set post.export_vtk=false --set post.query=true
```

设备继续使用个人 config 中的选择；本命令不启动训练。默认禁止覆盖已有目标，若上次已提交部分网格，应先检查进度，再明确决定是否使用已有的 `post.overwrite` 选项。

`feature_dim` 是布局声明；`trainprep.use_physics_features: false` 表示默认案例不输入物理特征。协议文件由运行生成，不是启动前要用户填写的内容。跨框架验证必须选择产物契约、同权重推理或独立训练目的，并检查实际数据、权重及几何/锚点输入；历史产物没有协议时只能确认有证据的契约，不能据此宣布数值等价。

## 配置与运行事实

configuration.py 读取五段配置，合并覆盖、展开组件默认值并解析路径。阶段函数只提取原业务接口要求的参数；库不认识五段 YAML 布局。顶层旧 sources/fields/geometry/save_fields/filters/statistics/vtkhdf/sampling/normalization、旧 pre/datapre 阶段及新旧混用均拒绝。

run.launch 的 config_loader 接收案例加载函数；run 在执行前保存一份五段 inputs/config.yaml。运行中参数副本不回写快照，检查点 effective_config 与快照一致。实际来源与分片保存在 summary.reports.dataset；准备引用、检查点、实际设备与推理随机协议保存在已有报告及产物，不要求用户预填。

仅测试分片时 rawprep.statistics.mode 可选 reference/none。保存预检通过显式 settings 接收案例提取的统计策略，不从五段快照猜字段。补跑继续使用原检查点和覆盖保护，不新增版本门禁。
