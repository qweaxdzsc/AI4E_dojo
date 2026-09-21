# ai4e-core 模块索引
## 当前职责与本轮变更

base 通用配置与事件；abilities 原子计算；applications 领域步骤；run 执行与唯一记录写入。

- `packages/ai4e-core/run/__init__.py`：稳定运行门面：launch/stage/TrainingRun/execute_operation/managed_run/configuration_adapter。
- `packages/ai4e-core/run/operation.py`：独立操作的日志、取消、样本循环和 writer 生命周期。
- `packages/ai4e-core/applications/aero_cfd/infer/anchor_stage.py`：锚点预测实现；post 旧导入只保留门面。
- `packages/ai4e-core/applications/aero_cfd/infer/artifact_operations.py`：固定物理结果的局部检查适配，task worker 不解释领域。
- `packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py`：固定结果逐样本评价、增量账本与最终快照。
- `packages/ai4e-core/applications/aero_cfd/train/resolve.py`：通用训练控制默认；模型专属默认在 contrib。
- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。
- `descriptor.reconcile_format_keys`：平台 `formats` 覆盖清单默认和旧 `format`，两键并存不提示用户。
- `abilities/transform/scale.py`：归一化之后的附加放大；坐标方法默认映射到 `[0, 1]`，系数写在场 `scale`。
- `applications/aero_cfd/infer/vtk_capability.py`：按训练集声明判断点云始终可写、网格化能否从 VTK/VTKHDF/连接关系还原；页面置灰与装配跳过共用。
- `abilities/postproc/export/mesh.py`：`mesh_topology_kind` 只按 VTK 对象区分结构化、非结构、表面与点云。
- `applications/aero_cfd/inspection.py`：公开检查与跟踪只消费 version=2 准备，不再分流到 `trainprep.physical`。
- `applications/aero_cfd/train/export.py`：训练结束写出只认现行 version=2 准备，复用独立推理锚点保存正文；旧物理记录拒绝。
- `abilities/training/loop.py`：每个轮次结束覆盖写入 `training.json`，检查模式不写；未开评估时 `best` 写成空，避免指标接口读失败。




## 模块边界

- 状态：可安装。**已交付** Dataset 按需前处理与产物清单、训练清单读盘；数据源下载、路径读取、VTK 家族/NPY 统一 VTK 内存适配、字段提取、有效点 mask、重合点标记、点数对齐、套对齐 mask、具名场编码与按对照表落盘/读回、规范化预处理根与官方分片、打开样本并派生表面距离、统计量读入/累计/重算、点到最近顶点 / 点到网格表面 / 表面法向，外流 pre 的按需装配、几何与单样本落盘，外流 train 选定 AB-UPT 与作业级读盘探测，并支持显式准备和正式训练，最小 Stage / Pipeline，以及 run 开车与唯一写入，以及监督比较方法。物理约束与完整字段契约、内容寻址缓存仍为规划。
- 职责：原子能力、Aero CFD 标准业务装配、训练/推理执行、内容缓存和 run artifact 写入。
- 允许依赖：`ai4e-spec`；本切片第三方依赖为 `huggingface-hub`、NumPy、OmegaConf、PyYAML、Torch、VTK。
- 禁止依赖：ai4e-viz、ai4e-task、ai4e-server、ai4e-web、recipes。
- 写入边界：`run/writer` 是 run 目录唯一写入方；运行数据不得进入包源码目录。
- 结构原则：按 `base / abilities / applications / run / tools` 分组，以高内聚、低耦合代替 DDD 外层目录。

## 基础设施目录

- `packages/ai4e-core/`：包工程根兼源码根；未来由构建配置映射为 `ai4e_core` 导入名。
- `packages/ai4e-core/base/`：不包含数值算法和业务流程的基础设施。
- `packages/ai4e-core/base/registry/`：历史预留空目录，未提供注册发现实现；现行组件由局部配置和普通导入解析。
- `packages/ai4e-core/base/config/`：OmegaConf 读取 YAML，支持点号覆盖并展开为可还原字典。diff 和 explain 仍为规划。

## 原子能力目录

- [Ability 五类简表](../../docs/abilities-summary.md)：20 项业务粒度能力；辅助实现随能力合并，模型内部算子不展开。

- [Ability 源码盘点表](../../docs/abilities-inventory.md)：逐实现模块列出当前 core / contrib 入口与边界；不是新的产品功能正文或拖拽节点定义。
- [合并后的 Ability 清单](../../docs/abilities-merged.md)：v2 提供五阶段主表，明确展开训练更新、优化、恢复、推理、评价和回贴；辅助与嵌套能力分开，原始条目逐项映射。

- `packages/ai4e-core/abilities/`：跨阶段复用的原子能力总入口，不认识具体案例。
- `packages/ai4e-core/abilities/data/`：source/extract/validate/filter/save/stats 六个业务阶段。
- `packages/ai4e-core/abilities/data/source/`：原始数据源访问边界。
- `packages/ai4e-core/abilities/data/source/download/`：HuggingFace 整库/单文件、普通网址、多包解压；不解释数据集内容。
- `packages/ai4e-core/abilities/data/source/read.py`：读取前完成存在性与格式校验；单文件原子入口，多文件/递归循环调用单文件；不读取 YAML。
- `packages/ai4e-core/abilities/data/source/adapter/`：一种格式一个文件。`vtk.py` 支持 `.vtk/.vtp/.vtu/.vtkhdf/.vtkh5` 并返回原生 `vtkDataObject`；`npy.py` 返回以 FieldData 承载数组的 `vtkDataObject`。
- `packages/ai4e-core/abilities/data/extract/`：只从 VTK 内存对象抽出点坐标与具名点/单元标量或矢量；不读文件、不加 meshio。`FieldRecord` 与 `GroupContract` 在 `extract/records.py`，显式声明来源与实体身份。
- `packages/ai4e-core/abilities/data/filter/`：按约定单元类型核对 VTK 单元并生成有效点 mask；`coincident.py` 标与表面坐标精确重合的体积点（`exterior_mask`）；`select.py` 筛普通数组；`records.py` 对字段记录与身份统一筛选，前后校验。不删原数组。
- `packages/ai4e-core/abilities/data/validate/`：`aligned.py` 校验首维；`fields.py` 校验组来源、归属、数量、身份与分量，返回结构化报告；`output.py` 共用输出预检。
- `packages/ai4e-core/abilities/data/save/`：`encode.py` 编码单场；`store.py` 按映射读写张量或打包载荷，临时目录/备份/提升/恢复，不认识 cell 名字；必需项缺失失败，可选性由调用方声明。
- `packages/ai4e-core/abilities/data/source/split.py`：按传入名单列分片并校验人数，不扫盘冒充官方顺序；准备阶段可按 `trainprep.split` 先限定执行样本再重划 train/test/eval，不改张量。阅读准备时固定给出三个切片，空切片人数为 0。旧 `validation` 并进评价集。
- `packages/ai4e-core/abilities/data/stats/`：`load.py` 读写 YAML/JSON；`moments.py` 保留尾维流式累计；`fit.py` 对具名数组流累计，不解释目录或训练分片。支持按冻结记录在训练和推理应用正反变换。
- `packages/ai4e-core/abilities/transform/`：字段变换和可追踪逆变换；`scale.py` 是方法之后的可见放大。
- `packages/ai4e-core/abilities/geometry/`：本切片已交付。`surface.py` 为全二维面门禁、私有表面转换及原 point ID；`nearest.py` 为点到最近表面顶点（只吃坐标）；`mesh_sdf.py` 先校验全部单元为支持的二维面再算有符号距离、面上最近点与方向；`surface_normals.py` 按原点身份回贴法向及有效性 mask，参与面法向非有限/零长度拒绝。不加 sklearn / trimesh / meshio。
- `packages/ai4e-core/abilities/sampling/`：采样策略与采样结果，不绑定具体 recipe。
- `packages/ai4e-core/abilities/modeling/{modules,models}/`：模型模块与框架管理的模型装配；独立 AB-UPT 源码不复制到这里。
- `packages/ai4e-core/abilities/constraint/`：监督比较、严格形状监督、物理残差及边界残差；参数 PDE 已使用。
- `packages/ai4e-core/abilities/training/`：循环、可换优化器、公开调度（`schedule.py`）、累积更新、检查点、诊断（`diagnostics.py`）、分流警告（`split.py`）与信号收尾。
- `packages/ai4e-core/abilities/inference/`：`rebuild.py` 只加载模型权重；含 parameters/data_specs 时只比这两项，不比采样点数。
- `packages/ai4e-core/abilities/eval/`：指标和物理量评估。
- `packages/ai4e-core/abilities/postproc/export/`：`pointcloud.py` 写出带独立顶点单元的锚点 `.vtp`；`mesh.py` 把预测写回原始网格并验收表面 VTP / 体积 VTU。
- `packages/ai4e-core/abilities/report/`：稳定评估结果到报告 artifact 的生成。

## 业务装配与运行目录

- `packages/ai4e-core/applications/`：标准业务装配；只能协调公开能力，不能实现原子算法。
- `packages/ai4e-core/applications/base/`：已交付最小 `Stage` / `Pipeline`（顺序 `ctx = step(ctx)`，按 `pipeline.stages` 选阶段）。DAG、内容缓存和 profile 仍为规划。
- 能力归属原则：来自模型源码的图构造、变长收批、mask、rollout、轨迹评价等先按中立输入输出进入 `abilities`；只有固定模型结构、私有状态或业务字段语义无法中立化时才由 contrib 持有。MeshGraphNet 的通用图原语接入后仍不导入 contrib。
- `abilities/data/source/tfrecord.py`：TFRecord framing、CRC 与 `tf.train.Example` bytes feature 基础解析；dtype/shape 由数据集适配器解释。
- `abilities/geometry/mesh_graph.py`、`modeling/modules/graph_message_passing.py`：三角形双向边、sender→receiver 边特征和先边后节点的中立消息传递。
- `abilities/geometry/mesh_graph.py`、`abilities/sampling/graph.py`：混合 VTK 单元真实边、诱导子图、稳定 BFS 核心分区与指定跳数 halo；组合分区只构造一次邻接表，不解释数据集或模型名称。
- `abilities/training/graph_batch.py`、`transform/{noise,running_normalizer}.py`、`constraint/masked.py`：变长图收批、在线统计、噪声和可选特征归约的 mask 监督。
- `abilities/inference/rollout.py`、`eval/trajectory.py`：边界保持的通用状态推进及累计 horizon MSE；具体节点类型由 contrib 绑定。
- `packages/ai4e-core/applications/aero_cfd/rawprep/`：五模块公开业务步骤：`read.py` 样本发现/读取/提取及域类型；`derive.py` 可选几何装配；`select.py` 选场/组契约校验/筛选；`save.py` 实际路径/编码/提交和轻量结果，`formats` 可同时写 PT/Zarr；`descriptor.py` 合并默认时平台格式选项覆盖旧单键，不报冲突；`stats.py` 训练样本/字段/缺失策略与统计量。无批量循环，不导入 run。
- `packages/ai4e-core/applications/aero_cfd/model/`：贡献模型引用、初始权重、冻结和学习目标装配。
- `packages/ai4e-core/applications/aero_cfd/train/`：`fitting.py` 装配训练、评估、监控与恢复；`resolve.py` 展开默认（设备默认自动选择）并联合校验，写出预测/网格默认关闭；`export.py` 训练成功后按现行 version=2 准备调用独立锚点推理保存正文，不走旧物理准备接口；`__init__.py` 保留旧只读调用的兼容导出，读盘实现位于 trainprep/dataset.py。
- `packages/ai4e-core/applications/aero_cfd/trainprep/topology.py`：从 manifest 声明的 VTKHDF 按 PT 原点身份对齐坐标、派生图，并按当前训练/推理核心块和 halo 预算缓存分区；缓存可删除或在预算变化后重建，共享平台数据保持只读。
- `packages/ai4e-core/applications/aero_cfd/post/`：`stage.py` 按配置串锚点评估/保存/点云与完整网格回贴；`evaluation.py` 复用共享评估；`export.py` 提交具名张量；`mesh.py` 装配下标、原始网格与分块回贴；`inference.py` 保留分块查询，不再作为案例默认产物。
- `packages/ai4e-core/run/`：`session.py` 展开默认、联合校验并映射 `gpu`→`cuda`；`runner.py` 读取配置并驱动管道，不解释业务路径；`execute.py` 顺序批量执行、首错/继续和轻量汇总；`writer.py` 独占运行配置、源码快照、日志和摘要写入，业务报告经 reports 交付，不写训练张量。
- `packages/ai4e-core/tools/`：项目创建、recipe fork、组件生成和检查等非运行时工具。

## 文档索引

- `packages/ai4e-core/README.md`：包职责、依赖边界、本切片下载/读取/适配/提取/清洗/物化/读回/分片/统计量/几何/pre/train/Stage/run 边界。
- `docs/PRD/ai4e-core/abilities/PRD.md`：原子能力产品说明；数据章含清洗、物化、读回、分片与统计量，几何章写清两种距离的字段名与语义。
- `docs/PRD/ai4e-core/applications/PRD.md`：业务装配产品说明；外流 pre、train 与最小阶段盒子。
- `docs/PRD/ai4e-core/run/PRD.md`：开车、日志与运行目录写入。
- `tests/integration/test_train_dataset_read.py`：选定 AB-UPT、官方分片、按对照表读盘与开车摘要；`@pytest.mark.local_data` 读本机官方 test 第 0 个。
- `tests/integration/test_shapenet_pre_recipe.py`：案例入口、点号覆盖、run 记录与阶段失败停止；`@pytest.mark.local_data` 含单样本 dry-run 与整库 889 对照表核对。
- `tests/integration/test_source_download.py`：下载与多包解压（替身）；`@pytest.mark.network` 真下 HuggingFace 小文件，无网 skip。
- `tests/integration/test_source_read.py`：VTK 家族/NPY 统一 VTK 读取、NPY shape/dtype/数值恢复、Legacy 多数组、内存生命周期、失败边界、多文件/目录入口与 pre 解耦；`@pytest.mark.local_data` 读取本地 ShapeNet 样本，无数据 skip。
- `tests/integration/test_extract_clean.py`：具名 point/cell 字段提取、共享视图、配置预检、同源对象复用、点 mask 与外流 pre 装配；`@pytest.mark.local_data` 读本地 ShapeNet 样本，无数据 skip。
- `tests/integration/test_geometry_domain.py`：点到点、点到面（解析几何、封闭立方体符号、独立三角最近点对照、先拒点云）、表面法向、`exterior_mask`、点数对齐与几何装配；`@pytest.mark.local_data` 读本地 ShapeNet 样本并对点到面做三角化对照，无数据 skip。
- `tests/integration/test_pre_materialize.py`：套对齐 mask、编码、按对照表写 `.pt`、`cell.pt` 启停、单样本/批量编排与统计量；`@pytest.mark.local_data` 写本地 ShapeNet 样本，无数据 skip。
- `tests/support.py`、`tests/conftest.py`：相对路径解析、外网探测与测试设备自动选择。
- `.context/modules/ai4e-core.md`：本模块的目录与文档检索入口。
- `.context/mvp/abupt-mvp1.md`：AB-UPT 首个纵向闭环及 core 参与阶段。
- `.cursor/rules/ai4e-algorithm-architecture.mdc`：本包的能力分层、高内聚低耦合与代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：原子能力、applications、Stage、Artifact 和 run 的设计依据。

## MVP1 约束

为 aero_cfd 的 rawprep/trainprep/model/train/post 提供标准装配，但不得导入 Noether。`applications/base` 不感知具体 modeling/constraint 内部实现，领域 application 也只能经公开 ability 契约组合它们。新增、删除或移动目录时必须同步本索引。

`rawprep/read.py` 同时定义 core 内的 `FieldConfig`、`DomainResult` TypedDict；由 pre 包公开导出，不向 spec 引入 VTK/NumPy。

数据接入的设计原因、NPY 恢复约定见 abilities PRD；具名字段配置、结果交接及迁移见 applications PRD。旧 docs/data_onboarding.md 仅做跳转。

## 具名提取公开接口定位

- extract 包导出 `extract_field(data, *, name, association, kind)`；`extract_scalars`、`extract_vectors` 必须显式提供 name 与 association，均委托统一提取入口。
- geometry 包导出 `nearest_vertex_distance_and_direction`、`mesh_signed_distance`、`require_surface_mesh`、`surface_point_normals`、`surface_point_normals_with_mask`。
- filter 包导出 `exterior_mask`、`apply_aligned_mask`、`filter_records`；validate 包导出首维、记录校验与输出预检。
- save 包导出 `FieldRecord`、`encode_field`、`write_named_tensors`、`load_named_tensor`、`load_named_tensors`。
- source.split 导出 `load_split_lists`、`load_split_expected`、`require_split_counts`。
- train.read 导出 `resolve_preprocessed_root`、`open_preprocessed_sample`。
- stats 包导出 `load_statistics`、`write_statistics`、`accumulate_moments`、`fit_statistics`。
- pre 包保留兼容的单样本几何和提取接口，以及 `discover_samples`、`dataread`、`extract_fields`、`derive_geometry`、`select_fields`、`validate_fields`、`filter_points`、`tensorize`、`write_tensors`、`resolve_statistics`。train 保留已有标准装配。applications.base 导出 `Stage/Pipeline/StageError`；run 导出 `run_from_config/RunWriter/execute_many/for_each/BatchExecutionError`。


## 两份早期计划的现行文档对应

- `.cursor/plans/数据准备与校验_32f73386.plan.md`：历史路径读取、格式保留和配置解耦决策；现行行为见 abilities PRD 功能 1，装配演进见 applications PRD 功能 1.7。NPY 原生数组返回已被统一 VTK 返回替代。
- `.cursor/plans/提取与一致性校验_26b347b3.plan.md`：现行提取见 abilities PRD 功能 3，有效点标记与不采用第二读取库/压力副本对照的原因见功能 4。旧活动字段选择已被具名 point/cell 选择替代。
- `.cursor/plans/几何派生与域校验_47951f86.plan.md`：现行点到点 / 点到面 / 法向见 abilities PRD 几何章；重合点与点数对齐见数据章功能 5、6；装配见 applications PRD 功能 2。两种距离字段名必须分开。
- `.cursor/plans/张量落盘与统计量_24ff82a9.plan.md`：现行套 mask / 编码 / 写出见 abilities PRD 数据章功能 7–9；单样本与统计见 applications PRD 第一章功能 3–5，批量执行见 run PRD 功能 4。编排不进原子能力。最小 Stage 见 applications PRD 第二章与 run PRD。
- 证据定位：source/read.py、source/adapter、extract/vtk_fields.py 核对输入；extract/records.py、validate/fields.py、filter/records.py 核对身份；save/store.py 核对提交恢复；rawprep/read.py、derive.py、select.py、save.py、stats.py 核对业务步骤；run/execute.py 和 recipe/datapre.py 核对执行边界。
- 历史计划保留当时决策，不作为当前实现的替代说明；没有实现的步骤不因计划标为 completed 就写成已交付。

## 几何可选装配使用定位

- 配置入口：先调用 `configured_geometry_enabled(config)`，再把返回清单传给 `derive_configured_geometry(extracted, enabled=...)`；无清单时关闭全部。原子函数仍可直接调用。`volume_normals` 是独立能力，只写最近方向；`nearest_vertex` 只写最近距离。
- 几何输入最低仅含 vtk；公开类型在 rawprep/derive.py，提取允许显式 fields: {}。法向仅需 surface，其余几何需 surface/volume。
- tests/integration/test_geometry_domain.py 覆盖门禁、身份回贴、孤立点、可选执行、冲突、配置迁移与本地 ShapeNet；test_extract_clean.py 覆盖无标签提取。

## Dataset 与脚本入口

- `docs/PRD/ai4e-core/base/PRD.md`：配置与能力事件行为。

- `applications/base/dataset.py`：只持有样本引用与顺序步骤的 Dataset，不持有批量网格。
- `applications/aero_cfd/rawprep/dataset.py`：按需装配、输出预检、安全保存、清单和训练统计；保留旧单样本调用。
- `base/events.py`：阶段上下文、能力开始/结束/失败与真实耗时；循环原子默认 debug，后台心跳只跟常规级别操作，继承阶段和样本，无文件 handler。
- `run/dataset.py`：逐样本消费步骤和通用保存策略，不解释物理字段；样本步骤/提交只记 debug，整批与稀疏进度保持常规日志；`rawprep.workers` 大于 1 时按线程并行，首错仍停止。
- `run/session.py`：脚本 launch、配置路径插值解析、单次运行会话与阶段上下文设置/恢复；`load_user_configuration` 把平台 `rawprep.workers` 从旧任务脚本未知键中取出再写回。
- `run/writer.py`：单份生效配置、带阶段前缀的阶段/批量日志、按事件元信息筛选的控制台摘要、默认不写 debug、延迟创建的错误日志。
- `applications/aero_cfd/trainprep/dataset.py::open_manifest_sample`：按产物清单的实际路径、形状和 physical 状态读回；平台公开清单是 `inputs.trainprep.dataset`，装配层仍可消费 `bind_inputs` 注入的 `train.manifest`。
- `tests/integration/test_dataset_recipe.py`：新入口全链测试；其余 pre/geometry/source/train 测试保留历史原子契约回归。

- `tests/integration/test_recipe_logging.py`：阶段切换、异常恢复、后台心跳身份、循环张量读取保持 debug 及控制台摘要；复制入口一致性见 `test_dataset_recipe.py`。

## 本次实施定位（2026-09-08）

2026-09-18 训练监控追加：`abilities/training/loop.py` 输出 update 粒度 `curves`，`applications/aero_cfd/train/fitting.py` 按选定物理量和指标装配测试评估；相关回归见 `test_train_loop.py` 与 `test_model_evaluation.py`。

- `applications/aero_cfd/trainprep/dataset.py`：按清单读盘、物理/归一化/采样探测。
- `applications/aero_cfd/trainprep/normalization.py`：字段绑定、冻结参数与配置冲突检查。
- `applications/aero_cfd/model/abupt.py、objectives.py`：注入模型与学习目标。
- `applications/aero_cfd/train/fitting.py`：训练业务装配（正式贡献网络的小配置已验收）。
- `applications/aero_cfd/post/evaluation.py`：独立评估装配。
- `applications/aero_cfd/post/stage.py`：解析检查点、只恢复权重、锚点评估保存与完整网格回贴开关。
- `applications/aero_cfd/infer/anchor_export.py`：按样本提交物理预测和可选锚点点云；post/export.py 保留旧导入门面。
- `applications/aero_cfd/post/mesh.py`：测试下标、原始网格路径、固定锚点、查询坐标的模型设备交接、分块查询与反变换。
- `abilities/inference/rebuild.py`：只加载模型权重，恢复契约不含采样点数。
- `abilities/postproc/export/pointcloud.py`：VTK 锚点点云。
- `abilities/postproc/export/mesh.py`：抽真值、回写 VTP/VTU 与门禁验收。
- `tests/integration/test_post_inference.py`：锚点评估、保存、点云、检查模式与语义冲突。
- `tests/integration/test_post_mesh.py`：完整网格回贴、下标/缺文件门禁、坐标放宽与检查模式。
- `abilities/data/source/manifest.py`：一次解析的清单索引。
- `abilities/data/save/normalization.py、vtkhdf.py`：版本资产与网格保存。
- `abilities/transform/standardization.py、coordinate_normalization.py`：可微正反变换。
- `abilities/sampling/points.py`：独立随机流和联动抽点。
- `abilities/modeling/construction.py、requirements.py、weights.py`：构造、要求与权重。
- `abilities/modeling/modules/feed_forward.py、position_encoding.py`：来源组件；位置编码依赖 modeling extra。
- `abilities/constraint/compare.py、supervised.py`：四种比较方法与可配置监督；物理约束现已在参数化 PDE 使用，验收范围见专项记录。
- `abilities/training/batch.py、optimization.py、schedule.py、moving_average.py、loop.py、checkpoint.py、diagnostics.py、split.py、online.py`：收批、可换优化器、公开调度、累积、EMA 十轮落盘、信号收尾、诊断、分流警告与在线损失窗口。
- `applications/aero_cfd/train/resolve.py`：默认展开与联合校验，写出最终生效配置。
- `tests/integration/test_train_resolved_config.py`、`test_train_test_repeat.py`、`test_train_code_snapshot.py`、`test_train_interrupt.py`、`test_train_diagnostics.py`、`test_train_optim_align.py`、`test_train_entry_init.py`、`test_train_shapenet_contract.py`、`test_train_reference_stats.py`：训练闭环剩余对齐机制验收。
- `tests/integration/test_train_formal_two_epoch.py`：官方 789/100 正式两轮全量；`@pytest.mark.local_data`，跳过视为本切片未完成。
- `abilities/eval/metrics.py、evaluation.py`：归一化总分与分项、锚点物理指标与模式恢复。
- `run/training.py`：已有会话的意图、报告和写入桥接。

- `trainprep/dataset.py::read_probe_stage`：旧 Stage 只读兼容入口；原 train/standard.py 已移除。
- `tests/integration/test_normalized_dataset.py`：版本记录、冻结读回与失败保留。
- `tests/integration/test_train_checkpoint.py`：快照独立性、语义冲突、随机状态和严格 best，含真实 MPS RNG 恢复用例。
- `tests/integration/test_constraint_losses.py`：比较方法、监督门禁，以及 recipe 四种方法走到训练步进与评估。
- `tests/integration/test_train_online_loss.py`：逐步记账、更新间隔冲刷、默认只轮次末写出与非有限拒绝。
- `.context/mvp/abupt-acceptance.md`：本期所有功能叶子的验收映射。

## 多域模型变更

`applications/aero_cfd/infer/query.py`：注入贡献上下文，检查点重建与分块点场查询；旧 post/inference.py 为再导出兼容门面。`trainprep/dataset.py`：显式物理派生规则；`normalization.py`：通用字段与条件冻结变换。`abilities/training/batch.py`：嵌套设备搬运。`run/training.py`：按阶段交付报告。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## 三阶段交接与训练行为对齐

- `applications/aero_cfd/trainprep/preparation.py`：公开准备步骤、持久化引用与数据内容校验；可套用准备分片并写入 `preparation.json` 的 `partitions`/`split`。消费只检查现行记录能否导入，按当前平台配置组计算，不拿冻结声明挡现行参数。
- `applications/aero_cfd/train/fitting.py`：open_training/build_model/configure_objectives/configure_optimization/configure_evaluation/execute_training。
- `abilities/training/callbacks.py`：普通可调用组件的 update/epoch 周期包装。
- `run/session.py::stage`：单会话内显式执行阶段并返回交付物；配置 resolver 由 recipe 注入。
- `run/writer.py`：唯一 config.yaml、原子 JSON 阶段交付、独立 EMA 权重文件。
- `abilities/geometry/nearest.py`：锁定 sklearn 1.9.0 近邻实现以保持等距点方向与官方一致。
- `tests/integration/test_train_boundary_alignment.py`：累积尾组、异常轮次重放、EMA 周期和真实诊断。

三阶段数值回归：`tests/integration/test_reference_arithmetic.py` 使用 `tests/fixtures/abupt_inputs/normalization.json` 的独立官方归一化夹具；版本迁移见 `.context/mvp/abupt-reference-acceptance.md`。

历史 post 数值入口默认 `post.random_stream=global`，从独立固定种子开始重建与采样；锚点和网格分支隔离随机状态，旧 independent 按样本采样仍可选择。

## 端到端修复定位（2026-09-09）

- `abilities/transform/normalization.py`：冻结变换组合、恒等变换、记录重建与摘要；application 保留业务绑定和兼容导入。
- `abilities/transform/fields.py`：标量补通道与按声明生成零场。
- `abilities/inference/query.py`：通用分块查询、缓存释放及模式恢复。
- `abilities/inference/randomness.py`：独立推理种子及调用方 Python/NumPy/CPU/CUDA/MPS 随机状态恢复；共享 preserve_randomness 供评估与 post 分支隔离。
- `abilities/data/save/store.py::write_tensor_file`：单文件张量包的原子写入。
- `abilities/postproc/export/pointcloud.py`：保持 dtype 的独立顶点单元；`mesh.py`：表面提取点数、原始点/单元 ID。
- `applications/aero_cfd/post/export.py`：按样本身份保存和按测试顺序交付兼容张量包。
- `tests/integration/test_post_reference.py`：随机状态、原子保存失败和输出开关独立性，含真实 MPS 异常隔离及 RoPE 前后向。
- `.context/mvp/abupt-end-to-end-acceptance.md`：本轮完整 recipe 与 Noether 实跑对照。

`tests/integration/test_abupt_recipe.py` 同时覆盖默认四阶段、不预填未来引用以及旧准备查询接口的反变换推导。

## 框架正确性与部分交付

- `base/events.py::sample_context`：真实样本/批次身份和异常上下文恢复；`run/training.py`：来源入口和报告快照，writer 独占进度文件写入。
- `abilities/data/validate/fingerprint.py`：张量树、文件与源码内容摘要。
- `applications/aero_cfd/model/protocol.py`：实际数据、训练与推理对照事实的装配。
- `applications/aero_cfd/post/progress.py`：操作、样本及逐项提交账本；stage/mesh/export 在明确提交后登记，不推测历史文件。
- `tests/integration/test_framework_correctness.py`：分项输入门禁、设备类型、故障注入、部分交付、补跑、生成协议及真实 GPU 邻域图。
- `tests/integration/test_comparison_protocol.py`：比较目的与数据/采样/来源证据门禁。

## Task 接入

- `run/provenance.py`：可选 managed_run 上下文，启动前写来源与代码快照；writer 原子摘要，独立 recipe 兼容。
- `.context/mvp/task-acceptance.md`：相关验收入口。

## 双模型组件入口

- `abilities/transform/pointfields.py`：冻结 float32 工况与标签正反变换；trainprep 保留旧导入。
- `abilities/training/checkpoint.py`：可恢复选优记录与旧检查点最佳权重验证。
- `abilities/sampling/stride.py`：跨步索引和严格逆映射。
- `abilities/data/save/arrays.py`、`data/stats/population.py`：原子数组提交及总体矩。
- `abilities/eval/pointwise.py`、`field_totals.py`：元素累计和物理场指标。
- `abilities/inference/stream.py`：推理组件生命周期。
- `abilities/postproc/surface_geometry.py`、`export/field_surface.py`：混合面朝向、面积与 HDF5/VTP。
- `applications/aero_cfd/anchor_workflow.py`、`pointfield_workflow.py`：组件注入的两类业务装配。
- `applications/aero_cfd/{rawprep,trainprep,post}/pointfields.py`：点场阶段交接。

历史数值对标及其范围见 `.context/mvp/transolver3-acceptance.md`；当前公开入口和兼容边界见 `.context/mvp/architecture-alignment-acceptance.md`，不迁移历史任务。

## 五段配置与快照职责（2026-09-09）

run/session.py 的 config_loader 为通用加载回调；applications/aero_cfd/configuration.py 保留旧路径解析。run/training.py 只幂等确认快照；run/dataset.py 写来源报告、显式转交保存预检 settings。

## 物理数据跨模型实验

abilities/data/source/physical.py 与 data/stats/physical.py：具名物理视图、按单位冻结统计；applications/aero_cfd/workflow.py 与 trainprep/physical.py：共享组装；infer/stage.py 与 post/comparison.py：全点预测与固定结果的跨运行比较；abilities/eval/physical.py、postproc/comparison.py：指标与切割。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `abilities/data/save/zarr.py`：PT 并列的 Zarr 张量编码，复用目录事务。
- `abilities/transform/minmax.py`：通用冻结 Min-Max，坐标兼容入口共享算术。
- `abilities/modeling/inspection.py`：真实 TorchVista HTML 原子发布；中等体量压缩模块图（一层模块折叠），并把初始缩放改成按宽度适配。
- `abilities/postproc/difference.py`：同身份同单位差值门禁。
- `applications/aero_cfd/inspection.py`：task 调用的检查公开门面；原始处理描述只回已保存的 `dataset.processed_name`；训练设置预检不要求准备记录；模型跟踪先读 `inputs.train.preparation` / `inputs.trainprep.dataset`，再回退内部旧键；现行 version=2 准备走 `trainprep.preparation`，旧物理准备仍走 `trainprep.physical`；`trace_model` 只取样组网，不写 HTML、不设 TorchVista 参数；案例能力含损失与采样声明。
- `applications/aero_cfd/rawprep/extraction.py`：提取容器到成员路由编译。
- `.context/mvp/web-algorithm-acceptance.md`、`web-algorithm-results/`：四组合新提取/准备/正式短训/后处理、四份真实模型跟踪与严格差值证据；不替代 HTTP/浏览器验收。
- `applications/aero_cfd/post/mesh_export.py`：共享物理后处理的真实来源网格回贴，按原身份写 VTP/VTU 并登记 `manifest.meshes`；`test_physical_mesh_export.py` 验证表面/体拓扑和字段身份。
- `abilities/postproc/coordinate_space.py`：显式坐标空间 id/unit 校验，供公开配置、post、真实网格和差值继承；`test_coordinate_space.py` 覆盖声明拒绝与传播。

## Recipe 公开业务步骤（2026-09-11）

- `base/config/steps.py`：通用参数声明校验、target/parameters 解析、能力来源与重建。
- `applications/aero_cfd/rawprep/mapping.py`：FieldMapParameters 与 map_fields；只读数组到继承身份的具名字段。
- `applications/aero_cfd/rawprep/dataset.py`、`rawprep/physical.py`：登记步骤、事务保存、统计与发布分离。
- `applications/aero_cfd/trainprep/preparation.py`、`trainprep/physical.py`：字段绑定、冻结变换、采样和拼批声明、准备分片、准备校验与发布。`declarations` 只写准备真正消费的冻结项；`consume` 只检查现行记录能否导入，按当前平台配置组计算，不拿冻结声明挡现行参数。模型页采样预算不写入。
- `applications/aero_cfd/train/fitting.py`、`train/physical.py`：显式模型、目标、优化、评价、恢复和执行。
- `applications/aero_cfd/infer/anchor_stage.py`、`infer/stage.py`：按登记顺序执行推理，逐样本交接预测与保存；旧 post/stage.py、post/physical.py 为兼容门面，新 post 只读取固定结果。
- `abilities/transform/normalization.py`：可重建自定义正反变换及来源校验。
- 相关 PRD：`docs/PRD/ai4e-core/{base,applications,abilities,run}/PRD.md`。
- 验收：`tests/integration/test_recipe_extensions.py`、`test_recipe_documents.py` 和 `.context/mvp/recipe-explicit-acceptance.md`。


## 参数化 PDE

- `packages/ai4e-core/abilities/geometry/parametric.py`：解析域、物理坐标和法向。
- `packages/ai4e-core/abilities/sampling/physical.py`：监督点、域内点、初值及周期配对。
- `packages/ai4e-core/abilities/transform/trapezoid.py`：完整物理导数变换。
- `packages/ai4e-core/abilities/constraint/physical.py`：标准条件残差与归约。
- `packages/ai4e-core/abilities/data/save/bundle.py`：张量包和内容摘要。
- `packages/ai4e-core/applications/parametric_pde/`：contracts/rawprep/trainprep/model/train/post 公开装配。
- `packages/ai4e-core/run/training.py`：execute_samples 复用逐样本执行和记录。
- `docs/PRD/ai4e-core/abilities/PRD.md`、`docs/PRD/ai4e-core/applications/PRD.md`、`docs/PRD/ai4e-core/run/PRD.md`：长期功能正文。
- `.context/mvp/pibsnet-acceptance.md`：圈定测试及实际验收。

- `run/writer.py::write_operation_sources`：写入已加载能力源码；`run/dataset.py` 交接字段扩展来源。
- `train/physical.py::configure_resume`：旧检查点独立 DataLoader 流按已完成轮次重建，不改完整训练顺序。

## 声明驱动原始处理

applications/aero_cfd/rawprep/descriptor.py 解析默认和校验选择，并把 manifest 来源文件名写入 source_files/输出 filename；catalog.py 负责稳定样本身份与范围，页面只提交全部或指定样本，分片模式仅兼容旧请求；extraction.py 支持 fields 逐场布局；physical.py/dataset.py 发布实际布局，source/physical.py 优先消费清单布局。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

## 原案例迁移

applications/parametric_pde/train.py的epoch_sum先顺序汇总损失图再一次反传；通用训练loop不变，实例用户step契约不变。

## 独立推理切片

- `abilities/inference/{__init__,prediction,execution}.py`：公开单次无梯度预测和模式/RNG保护；既有 rebuild/query/stream 保留。
- `applications/aero_cfd/infer/stage.py`：唯一完整物理步骤实现，旧 post/physical 委托；通过 run.execute_many 执行有序样本。
- `infer/configuration.py`：独立参数与旧模型内部交接。
- `infer/inspection.py`：inspect_checkpoint、inspect_inputs、available_devices，供独立检查进程使用。预检与检查点 `effective_config` 只比权重结构、数据规格、字段角色和采样方法，不整段比 `model+sampling` 点数。
- `infer/configuration.py`：检查进程可从保存的 `inputs.*` 公共配置重建最小业务视图，不要求管理进程依赖 contrib 装配器。
- `abilities/data/source/manifest.py`：重挂分片时按目标分片选择同名来源记录，允许 train/test 来源各自存在同名样本。
- `tests/integration/test_infer_inspect_contract.py`：采样点数不同可通过预检，dim/blocks 或 data_specs 不同必须拒绝。
- `infer/fields.py`：具名派生点场的实体、单位及分量校验。
- `infer/results.py`：固定结果读取、数组读回及严格 compare_results。
- `infer/anchor.py`：旧锚点模板独立 infer 兼容，不改变原计算路径。默认写出锚点 VTK（预测+真值）；完整网格缺拓扑先记原因再失败，不把整批标成功。
- `infer/vtk_export.py`：推理 VTK 交付、跳过原因与样本身份 FieldData。点云走 ability `write_pointcloud`；网格化由 application 按来源 VTK 查询回贴或 `comparison_mesh` 适配。
- `infer/vtk_capability.py`：`describe_vtk_exports` / `mesh_export_available`。可还原 = 清单来源文件名是 VTK/VTKHDF，或配置里已有连接关系路径；空槽位和原始处理 VTKHDF 输出开关不算。
- `infer/configuration.py`：调用契约包 `apply_export_aliases`；契约包尚未导出该符号时回退同一规则，不另写第二套解释。
- `infer/vtk_export.py`：清单 `vtk` 分点云/网格化频道，跳过网格化不得盖掉点云成功。
- `tests/integration/test_infer_vtk_exports.py`：能力判定、旧键别名、NASA 未绑定与清单状态。
- `post/progress.py`：按阶段写 post-progress 或 inference-progress；`post/mesh_export.py`：将派生字段交付网格。
- `tests/integration/test_infer_{abilities,stage,extensions,compatibility}.py`：原子、五例数值、真实网格扩展及配置/比较验收。
- 长期功能正文：`docs/PRD/ai4e-core/{abilities,applications,run}/PRD.md`。

## 后处理三页签与固定结果评价

- `abilities/eval/result_metrics.py`：物理空间九项指标（旧默认五项保留）、分量/模长、有效性及不可定义原因。
- `applications/aero_cfd/post/__init__.py`、`result_evaluation.py`：固定结果公开评价、逐样本运行与CSV/XLSX/JSON显式输出；不加载模型。`post/physical.py` 向旧任务脚本提供 `open_post` 兼容入口。
- 长期行为归 abilities、applications PRD；圈定 `test_post_result_metrics.py`、`test_task_post_metrics.py`、`test_post_installation.py`。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

后处理目录的历史张量分量通过 `describe_result_fields` 在隔离进程中只读头部获取；使用 FakeTensorMode 保留形状而不加载场数组。不能根据缺失的旧指标记录猜成标量。缺真值或形状不符保留文件浏览并禁用该结果重新评价。

## 推理工作台选择与统计

`abilities/eval/{catalog,aggregation,result_metrics}.py`、`abilities/inference/timing.py`、`abilities/report/{__init__,tabular}.py`：指标目录、等权统计、同步计时、CSV/XLSX。`applications/aero_cfd/infer/{catalog,selection,evaluation,exports,stage,results,anchor}.py`：真实字段、分量选择、轻量结果及固定导出。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

- `applications/aero_cfd/post/mesh.py`：历史完整网格查询；原生锚点infer只保存所选域，在各样本目录交付full_surface/full_volume；`infer/anchor.py`登记到固定清单，锚点指标和完整网格实体口径明确区分。


推理结果视图配置更新：`infer/evaluation.py` 的 `result_views` 公开门面交付逐样本值及全部分片统计；`infer/exports.py` 按表格配置展开两种视图。专项数值、性能和CSV/XLSX读回用例：`tests/integration/test_infer_result_views.py`。 验收见 `.context/mvp/inference-result-views-acceptance.md`。

## 项目共享数据切片

applications/aero_cfd/trainprep/normalization.py 按物理清单位置解析相对统计路径；rawprep/dataset.py 发布前冻结参考统计到物理依赖目录。保留旧冻结摘要与算法。

长期说明见对应包 PRD；当前证据见 `.context/mvp/task-shared-datasets-acceptance.md`。

## 耦合物理场增量

`applications/coupled_physics/` 提供 contracts/rawprep/trainprep/model/train/infer/post 局部交接；能力分散在 data/source（原生数组、安全解压）、data/extract（窗口）、data/validate（轨迹）、transform（布局、可逆变换、概率路径）、sampling/flow、constraint/flow_matching、training/iterations 与 iteration_stream、inference/integration 与 coupled_steps、eval/trajectory、postproc/filters 与 visualization/trajectory。checkpoint 新增精确迭代状态，moving_average 可选复制缓冲，inference/execution 保护模型组。run/training 与 writer 新增可选检查点 namespace。长期行为见现有 abilities/applications/run PRD，证据见 [GenCP 验收](../mvp/gencp-acceptance.md)。

## 控制轨迹应用

- `applications/pde_control/{contracts,rawprep,trainprep,model,train,infer,post}.py`：独立物理/准备/权重/固定响应交接、阶段校验与只读结果分析；不导入贡献模型。
- `abilities/training/iterations.py`：可选裁剪、更新后回调和取消边界；默认保持既有数值顺序。
- `docs/PRD/ai4e-core/applications/PRD.md` 第八章、`abilities/PRD.md`训练功能：控制交接与可选扩展。
- `tests/integration/test_safediffcon_integration.py`：恢复、尾批、校准、独立结果、配置和复制入口。

## 时空场预测与共享机制

- `applications/spatiotemporal_pde/{rawprep,trainprep,train,infer,post}.py`：物理轨迹/模型输入分开交接、训练绑定、独立物理预测及固定评价。
- `applications/base/iteration_training.py`：领域无关的完整迭代恢复、调度/EMA顺序与writer交接；`applications/pde_control/train.py`保留旧导入。
- `abilities/data/save/array_manifest.py`：带形状/路径/内容摘要的具名数组保存读回；控制旧`contracts.py`保留门面。
- `abilities/training/cancellation.py`：临时信号标记，完整更新边界保存后退出并恢复处理器。
- 功能正文：applications第九章、abilities数据与训练功能点；测试WDNO migration/recipe、SafeDiffCon integration、GenCP abilities及固定公开接口安装基线。

WDNO已使用公共base/config/conventions和TrainingRun.data_dir/output_dir/record_asset/record_metric；仅消费者适配，不另建任务会话或输出记录器。新旧训练合同按科学参数比较，专项test_wdno_task.py保护两种入口的实际交接。

公共运行交接：`base/config/conventions.py` 解析阶段输入与输入冲突；`run/indexes.py` 计算文件及依赖身份；writer独占assets/metrics索引，session分配数据目录与研究完成状态。`applications/aero_cfd/infer/indexing.py` 将固定结果登记为资产及具有口径的样本等权指标。见Recipe/Task专项，不能以索引存在替代数值验收。

现行锚点 infer/anchor_stage 先通过 trainprep.preparation.consume 校验准备并恢复冻结归一化/分片/组件，再恢复模型；不在推理重新拟合统计。相关 test_task_infer_batches/partitions、test_post_inference/mesh/reference 与 test_train_recipe。

逐样本物理准备新增显式 version=2 / physical_fields：`applications/aero_cfd/trainprep/physical.py` 冻结来源、变换与分片；`infer/inspection.py` 和领域 `inspection.py` 沿同一消费链检查。旧v1仍可Python恢复，平台拒绝。圈定 `test_task_transolver_recipe.py`、`test_recipe_explicit_equivalence.py`、`test_algorithm_platform_contract.py`。公开运行资产可选自包含目录声明由 `run/{training,writer,indexes}.py` 持有。

## 共享训练执行

- `abilities/training/execution.py`：内部工作单元推进、有效更新事实和预算；loop/iterations 保留各自恢复与事件顺序。
- `applications/base/iteration_training.py`：可选局部更新、累积/精度选择，默认不向旧迭代器增加参数。
- `abilities/training/checkpoint.py`：迭代合同/游标副本预检、缩放器恢复；不变更旧容器默认合同。
- `tests/integration/test_training_execution.py`：跳步、预算、有限流、尾批、同轨迹与恢复拒绝。现状见 [专项验收](../mvp/training-execution-acceptance.md)。


训练观察指标：`abilities/eval/metrics.py` 校验并只算所选三项；`evaluation.py` 可选 `metric_names` 保留默认兼容；`applications/aero_cfd/train/fitting.py` 贯通 `train.evaluation_metrics` 与重复评价，观察项不进入恢复合同；`inspection.py` 发布算法指标目录。圈定 `test_model_evaluation.py`、`test_train_loop.py`、`test_train_online_loss.py`、`test_train_recipe.py`、`test_public_api_stability.py`。

## GeoTransolver 引入的中立能力

- `abilities/data/source/matlab.py`、`extract/time_series.py`、`validate/time_series.py`：具名MAT、数值时间/帧组装与实体门禁。
- `abilities/data/save/{indexed_cache,mesh_dataset}.py`、`stats/tensor_moments.py`：身份缓存、逐场PT+VTKHDF可搬移清单、显式dtype及归约顺序的统计。
- `abilities/transform/{mesh_fields,trajectory,field_encoding}.py`、`sampling/structured_grid.py`：保留身份的转点、窗口/轨迹布局、冻结正反变换及一致网格采样。
- `abilities/geometry/radius_query.py`：torch半径查询、CPU回退、独立邻域缓存及身份核验。
- `abilities/modeling/modules/{projected_mlp,physics_attention,geometry_attention,context_projection,multiscale_local}.py`：实际投影、切片、GALE、上下文与局部编码；`modeling/weights.py` 增显式映射严格加载。
- `abilities/constraint/relative_norm.py`、`training/{parameter_partition,combined_optimizer,schedule}.py`：逐样本相对范数、无遗漏分组、组合优化完整状态及真实轮次调度。
- `abilities/inference/prediction.py`、`eval/trajectory.py`、`postproc/visualization/trajectory.py`、`report/tabular.py`：具名取批与末批预测、float64逐帧场指标、显式时间单位与表格。
- `applications/{parametric_pde,spatiotemporal_pde}/{rawprep,trainprep,train,infer,post}.py`：新增具名场/轨迹入口，保留原入口；`applications/base/iteration_training.py`可选检查点间隔；`applications/base/array_assets.py`连接完整资产依赖。
- `Notice/physicsnemo/{LICENSE,source.json}`：迁入core的许可及来源，随core wheel交付。功能正文见 core abilities 第十章及 applications 第十章；验收见 `.context/mvp/geotransolver-acceptance.md`。

## PCNO 提取能力与地热装配

`abilities/modeling/modules/{fourier4d,unet_volume,global_features}.py`、`modeling/models/fourier_unet4d.py`：谱算子、U-Net、全局融合；`constraint/{spatiotemporal_field,geothermal}.py`：监督与物理；`postproc/{wellbore,geothermal_economics}.py`：井筒与经济；`training/rotating_chunks.py`：可恢复轮换；`eval/relative_field.py`：误差。`applications/geothermal/{data,inference,post}.py`：冻结交接、双场推理、固定结果消费。`applications/base/iteration_training.py`：可选评价回调。许可 `abilities/PCNO_LICENSE`，PRD为abilities/applications现行正文。

## 可选 FLARE++ 注意力

- `packages/ai4e-core/README.md` 提供包入口；能力清单的 A163/M13 与 Agent Help 网络指南相互导航，均按可选模型内计算单元描述。

- `packages/ai4e-core/abilities/modeling/modules/flare_attention.py`：可选 `FLAREPlusPlus` 注意力层，普通 `(B,N,C)` 张量，三次 SDPA 动态路由；不绑定模型/几何或默认启用。
- `packages/ai4e-core/Notice/physicsnemo/flare_plus_plus.json`：独立上游 revision、源摘要和修改说明；既有 GeoTransolver 来源记录不变。
- `tests/integration/test_flare_attention.py`、`test_flare_attention_installation.py`：上游/独立公式、梯度与更新、恢复、参数门禁及实际 wheel 仓库外使用。
- [FLARE++ 验收](../mvp/flare-attention-acceptance.md)：组件范围、安装证据和未验证的精度/性能；长期行为在 core abilities PRD 第十章。


## GeoTransolver 外流扩展

`abilities/transform/point_features.py` 校验并拼接具名点特征；`abilities/inference/indexed_prediction.py` 实现索引分块和全覆盖回贴；`data/stats/physical.py` 增加显式坐标组。`applications/aero_cfd/trainprep/point_inputs.py` 与 `infer/point_prediction.py` 提供模型无关点流装配；`train/physical.py` 支持优化与调度构造注入。网格导出优先消费物理 VTKHDF，原身份保留。

行为见对应模块 PRD；实际证据与边界见 [外流验收](../mvp/geotransolver-aero-acceptance.md)。

## 圆柱时空计算

`abilities/data/source/record_download.py`：版本固定的范围记录下载；`data/stats/masked_fields.py`：流式有效域统计；`modeling/models/fourier_unet3d.py`：二维时空网络；`constraint/{continuity,field_supervision}.py`：散度及监督；`eval/field_windows.py`：窗口误差；`training/iteration_stream.py`：计数恢复；`applications/spatiotemporal_pde/window_results.py`：固定结果及派生消费。

功能正文见相应模块PRD；实际范围见[圆柱验收](../mvp/pcno-cylinder-acceptance.md)。
