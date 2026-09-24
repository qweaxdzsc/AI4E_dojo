# Aero CFD 全流程 Recipe

本模板明确使用 AB-UPT 锚点准备、训练和推理。可选拓扑只服务图缓存。独立阶段引用使用 `inputs.train.preparation`、`inputs.infer.checkpoint/preparation` 和 `inputs.post.results`；post 只读固定结果。

安装仓库 workspace 后，可将本目录整体复制到任意工作目录；模板无需安装。

```bash
uv sync
uv run python pipeline.py --config config.yaml
uv run python rawprep.py --config config.yaml --check
```

在仓库外使用时，以已安装 ai4e-core/ai4e-contrib 的 Python 环境运行；uv 可用 `--active` 使用该环境。脚本默认读取旁边的 config.yaml，不依赖当前工作目录。

先修改 `inputs.rawprep.source`（原始数据）、`data_root`（产物）、`run_root`（运行记录）。`${data_root}/train` 等路径支持任意配置变量插值；各分片可单独改为绝对路径，相对路径以配置文件为基准。

`dataset.samples: all` 使用已选分片的全部样本，也可填样本 ID 列表。`dataset.partition: official` 使用官方名单，也可填 `train: [param0/...]`、`test: [...]` 映射或名单 YAML 路径。仅处理 test 时将 rawprep.statistics.mode 改为 reference 或 none；fit 要求非空完整 train。

`rawprep.fields` 选择特征与 components，可覆盖 array/association；精确字段与来源见 contrib/application/datasets/shapenet_car/manifest.yaml。`rawprep.geometry`、`rawprep.filters` 和 `rawprep.save_fields` 显示实验选择。未知字段或维度报错，不猜数组。

`--set data_root=/shared/data/new` 覆盖配置；`--overwrite` 显式允许替换；`--continue-on-error` 继续处理剩余样本但仍返回失败。默认不覆盖已有产物。覆盖前撤下旧完整清单并保留备份，部分失败后不能将旧清单当成完整有效版本。

实际 .pt 在 train/test 子目录；统计在 train/statistics.yaml；数据根的 manifest.json 是读盘入口。运行记录独立，inputs/config.yaml 为唯一的最终生效配置，logs/run.log 是能力和进度日志，异常堆栈见 errors.log。训练启动另写 code.tar.gz 源码快照。额外的用户组件模块通过 `snapshot_modules` 显式列出，以收入同次源码快照。normalize 路径保存冻结变换记录；仅 trainprep.normalization.materialize=true 时生成归一化张量。

几何可使用能力列表，也可写参数映射，例如 `nearest_vertex: {epsilon: 1.0e-6}`；未启用的能力不计算，未知参数拒绝。法向、点到面和最近顶点的 epsilon 允许显式设置。

## 准备与训练实施状态

默认 pipeline 依次执行 rawprep、trainprep、train、post。各脚本也可分别运行；train 默认实际拟合。rawprep 调用库既有 datapre 业务方法，文件名不约束库接口。trainprep 写出准备引用，冻结归一化和数据内容摘要，train 消费前校验；每次训练迭代仍动态采样。默认与官方 ShapeNet-Car 预设一致，保留未激活的特征投影参数，以保证初始化随机流一致。旧阶段名 `pre` 已移除，请改用 `rawprep`。

配置只描述用户输入和实验选择：无需预填统计数值、准备摘要、将来的检查点或预测文件名。完整 pipeline 自动交接这些结果；独立运行 train/infer/post 时，分别用 `inputs.train.preparation`、`inputs.infer.checkpoint` 与 `inputs.infer.preparation`、`inputs.post.results` 指向已有产物。`model.data_specs.output_dims` 是要预测什么的任务声明，不是要求填写未来预测值。

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

当前案例配置使用 `model.data_specs`、`model.supervision`、`trainprep` 和 `model.sampling.domains`。`infer.py` 消费准备与检查点，生成完整具名物理结果；`post.py` 只消费已经保存的结果。现有 pipeline 按 trainprep → train → infer → post 顺序交接；rawprep 独立执行或按需要加入阶段名单。

```bash
uv run python infer.py --set infer.checkpoint=/path/to/last.pt --set infer.preparation=/path/to/preparation.json
uv run python post.py --set post.results=/path/to/physical-predictions.json --set post.analysis_enabled=true
```

分析保存的图片、网格、采样和指标在 `paths.datasets.post`，运行记录由 writer 保存。`post.figures` 决定是否出图，空列表仅评价；切片、流线、剖面等参数在下方“脚本物理场分析”说明。失败保留已提交样本并发布 partial 清单，不把部分成功当作完整交付。再次分析默认拒绝覆盖，可选择新输出目录或明确设置 `post.overwrite_analysis=true`。

历史锚点预测、`sample_XXXX.pt` 与点云导出的证据见 [原端到端验收](../../.context/mvp/abupt-end-to-end-acceptance.md)，这些历史文件保持原样，不能当成当前 post 的执行说明。

`feature_dim` 是布局声明；`trainprep.use_physics_features: false` 表示默认案例不输入物理特征。协议文件由运行生成，不是启动前要用户填写的内容。跨框架验证必须选择产物契约、同权重推理或独立训练目的，并检查实际数据、权重及几何/锚点输入；历史产物没有协议时只能确认有证据的契约，不能据此宣布数值等价。

## 配置与运行事实

configuration.py 读取五段配置，合并覆盖、展开组件默认值并解析路径。阶段函数只提取原业务接口要求的参数；库不认识五段 YAML 布局。顶层旧 sources/fields/geometry/save_fields/filters/statistics/vtkhdf/sampling/normalization、旧 pre/datapre 阶段及新旧混用均拒绝。

run.launch 的 config_loader 接收案例加载函数；run 在执行前保存一份五段 inputs/config.yaml。运行中参数副本不回写快照，检查点 effective_config 与快照一致。实际来源与分片保存在 summary.reports.dataset；准备引用、检查点、实际设备与推理随机协议保存在已有报告及产物，不要求用户预填。

仅测试分片时 rawprep.statistics.mode 可选 reference/none。保存预检通过显式 settings 接收案例提取的统计策略，不从五段快照猜字段。补跑继续使用原检查点和覆盖保护，不新增版本门禁。

## 物理 PT 跨模型实验

七个独立配置见 `examples/aero_cfd`。原五例保留锚点准备、训练和推理数值路径；ShapeNet-Car 与 NASA CRM 的 MeshGraphNet 案例在同一阶段脚本中通过 `trainprep.topology` 选择图准备、静态图训练和完整分区拼回。`components.model` 选择模型，配合字段绑定与模型参数切换实验。已准备平台数据时配置 `inputs.trainprep.dataset`，从 trainprep 开始；图案例只消费 manifest 声明的逐场 PT、VTKHDF 和实体身份，不读取原始 VTK、HDF5 或 connectivity。

图拓扑不会写回共享平台数据。trainprep 校验 PT 原点 ID 与 VTKHDF 坐标，从真实单元
派生边和诱导子图，并在准备目录缓存拓扑摘要、核心分区与 halo；删除缓存后可从平台
资产重建。ShapeNet-Car 使用表面和体积两个独立子网络，NASA CRM 使用表面子网络并
广播六维工况。两例是工程扩展，不对应 MeshGraphNets 论文精度。

每个 example 一个模型实例。训练准备在 artifacts 中冻结，独立 train 用 `train.preparation`，独立 infer 用 `infer.checkpoint` 指定最后权重，post 用 `post.results` 消费固定结果；默认使用相邻运行目录的冻结准备。比较入口在 `tools/verification/cross_model`，报告写独立输出目录，不增加 recipe。

平台配置新增：采样统一放在 `model.sampling`；旧 `trainprep.sampling` 单键仍可读取，但不能同时填写。阶段 `rawprep.format` 选择 `pt` 或 `zarr`，两者直接进入清单读盘；字段输出容器使用 `rawprep.extraction`，成员不要求同形状。

## 怎样修改流程

打开 rawprep.py 依次查看来源、提取、几何、选择、校验、过滤、编码、执行、统计和发布；Dataset 步骤在 run.execute 前只登记处理方式。trainprep.py 显示字段绑定、冻结变换、采样与拼批；采样在每个训练迭代实际调用。train.py 显示模型、目标、优化、评估、恢复和执行；infer.py 显示恢复、预测、物理输出及交付；post.py 读取固定结果。pipeline.py 只选择阶段并传递返回引用。

改预算和参数使用对应 YAML 块或 --set；插入方法在对应 Python 步骤间接收并传递返回值。无参数步骤无需空配置；额外参数通过 configuration.py 的 STEP_PARAMETERS 在案例本地校验。target/parameters 由所属步骤解析，直接 operation=callable 使用同一调用契约。来源模块要随复制目录或已安装研究包提供；不要使用不可重建闭包作为持久化采样。

完整字段示例见 `examples/recipe_extensions/field_mapping`，采样示例见 `examples/recipe_extensions/sampling`。新字段不能只算出数组：还要声明实体身份与单位、添加 save_fields/statistics/normalization/trainprep 绑定和模型 feature_dim。map_fields 不承担跨网格映射，筛选走同步字段/身份接口。

普通锚点预测返回归一化映射；五例物理预测返回完整物理字段，不能重复反归一化。两类接口按模型契约分别校验。历史产物不改写；默认方法不变时保持原消费语义，能力或字段语义改变时需要重新准备，相关训练或比较契约冲突会明确失败。检查报告不作为下游产物。Web 继续保留标准编辑和未编辑扩展配置，不增加通用能力编辑页。

## 独立推理

`infer.py` 显式配置恢复、预测、评价与保存。设置 `infer.checkpoint`、`infer.preparation`、`infer.samples` 后执行 `uv run python infer.py`；调用 pipeline 时选择包含 infer 的阶段名单。当前 post-only 需要固定结果；历史预测 API 保留兼容，新 post 不含模型调用。

原生 infer 只解释 infer 参数；后处理以 `post.results` 或 `infer.results` 指向已经完成的 `physical-predictions.json`，不会再次预测。完整物理场五例交付同形预测与物理指标；旧锚点模板保留独立兼容结果，不冒充同一比较口径。进度为 `inference-progress.json`，所有运行文件由 writer 提交，数组写配置指定数据目录。

派生字段例子见 `examples/recipe_extensions/inference_fields/`；详细功能约定见 `docs/PRD/recipes/aero_cfd/PRD.md`。

### 推理字段与指标选择

`infer.fields` 使用 `域:字段:分量`，默认全部真实输出；显式空列表拒绝。`infer.metrics` 默认相对L2、MAE、RMSE、Max Error、R²。选择向量的部分分量仅限制评价，保存保留完整向量。`save_predictions=false`时需关闭`export_vtk`，仍交付轻量指标；新`inference-results.json`与旧结果保持可读，新post不重跑模型。研究者可在物理输出后显式登记派生字段及选择，再配置评价和保存。

普通用户逐场评价扩展示例见 `examples/recipe_extensions/inference_metrics/`。原生后处理缺少固定结果时拒绝；旧计算 API 保留；平台按公开操作声明调用，源码摘要仅作来源记录，不改写历史证据。

## 脚本物理场分析

安装 `ai4e-core[post]`。在已有固定推理结果上设置 `post.analysis_enabled: true`，`paths.datasets.post` 为独立输出根。`post.figures: []` 只算指标；选择 `surface/slice/clip/vectors/streamlines/contour/profile` 生成对应图片和网格。流线须设置 `streamline_seeds`，剖面须设置端点，等值面须设置值列表。

`post.py` 的 `analyze_sample` 是可编辑流程正文，可插入步骤或替换绘图。训练中设置 `post.snapshot_every` 和 `post.snapshot_sample`；默认 0 不执行。数据按来源摘要及样本隔离，重复出图需选择新输出根或显式 `overwrite_analysis: true`。自定义函数和保存读回示例见 `examples/recipe_extensions/physical_visualization`。

指标 JSON/CSV、剖面 CSV、PNG、VTP/VTU 和 manifest 均在数据目录。图形与原数值独立，原始结果只读；不需要启动 Web。

## Task 项目共享交接

通过 Task 托管时，原始处理正式产物归项目 shared，先填写 `dataset.processed_name`。新任务可绑定该名称后仅执行 trainprep/train/infer，无需重复 rawprep；同名重做必须在本次提交显式指定覆盖。独立运行 Python 脚本仍按原配置的输出路径执行。

处理步骤仍在 rawprep.py 中可编辑。新增字段要完成声明、保存、共享清单读回和另一任务的字段绑定；采样和归一化不写回共享物理数据。扩展示例的 Task 入口声明共享输出与阶段输入，字段扩展通过两任务和仓库外 wheel 实跑验收。


## Example 与 Agent 交接

本目录是仓库内 recipe 维护源；可复制的完整研究目录位于对应 `examples/` standalone。公共阶段脚本由案例清单声明并逐文件核对，配置、数据根和研究预算可以不同，但阶段顺序、输入键、恢复交接和产物语义不能漂移。Agent 先在复制目录通过 `ai4e_core.run.launch` 直接运行，再按需用同一目录调用 `ai4e_task` Python API；CLI 只是便利方式。
