# ai4e-core 模块索引


当前实施状态（2026-09-08）：已交付五类业务、归一化与采样、正式 AB-UPT、训练评估与轮次恢复、可选归一化物化及 VTKHDF/PT 关联、监督比较方法、训练闭环剩余对齐，以及完整网格回贴。物理约束未进。验收范围、逐项用例与执行结果以 `.context/mvp/abupt-acceptance.md` 为准；云图、报告及生产规模训练不在本期验收范围。

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
- `packages/ai4e-core/base/registry/`：按公开契约发现、解析组件并抽取源码 schema。
- `packages/ai4e-core/base/config/`：OmegaConf 读取 YAML，支持点号覆盖并展开为可还原字典。diff 和 explain 仍为规划。

## 原子能力目录

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
- `packages/ai4e-core/abilities/data/source/split.py`：按传入名单列分片并校验人数，不扫盘冒充官方顺序。
- `packages/ai4e-core/abilities/data/stats/`：`load.py` 读写 YAML/JSON；`moments.py` 保留尾维流式累计；`fit.py` 对具名数组流累计，不解释目录或训练分片。不做训练期 apply/inverse。
- `packages/ai4e-core/abilities/transform/`：字段变换和可追踪逆变换。
- `packages/ai4e-core/abilities/geometry/`：本切片已交付。`surface.py` 为全二维面门禁、私有表面转换及原 point ID；`nearest.py` 为点到最近表面顶点（只吃坐标）；`mesh_sdf.py` 先校验全部单元为支持的二维面再算有符号距离、面上最近点与方向；`surface_normals.py` 按原点身份回贴法向及有效性 mask，参与面法向非有限/零长度拒绝。不加 sklearn / trimesh / meshio。
- `packages/ai4e-core/abilities/sampling/`：采样策略与采样结果，不绑定具体 recipe。
- `packages/ai4e-core/abilities/modeling/{modules,models}/`：模型模块与框架管理的模型装配；独立 AB-UPT 源码不复制到这里。
- `packages/ai4e-core/abilities/constraint/`：监督比较方法与严格形状监督；物理约束未交付。
- `packages/ai4e-core/abilities/training/`：循环、可换优化器、公开调度（`schedule.py`）、累积更新、检查点、诊断（`diagnostics.py`）、分流警告（`split.py`）与信号收尾。
- `packages/ai4e-core/abilities/inference/`：`rebuild.py` 只加载模型权重并核对版本与语义契约。
- `packages/ai4e-core/abilities/eval/`：指标和物理量评估。
- `packages/ai4e-core/abilities/postproc/export/`：`pointcloud.py` 写出带独立顶点单元的锚点 `.vtp`；`mesh.py` 把预测写回原始网格并验收表面 VTP / 体积 VTU。
- `packages/ai4e-core/abilities/report/`：稳定评估结果到报告 artifact 的生成。

## 业务装配与运行目录

- `packages/ai4e-core/applications/`：标准业务装配；只能协调公开能力，不能实现原子算法。
- `packages/ai4e-core/applications/base/`：已交付最小 `Stage` / `Pipeline`（顺序 `ctx = step(ctx)`，按 `pipeline.stages` 选阶段）。DAG、内容缓存和 profile 仍为规划。
- `packages/ai4e-core/applications/aero_cfd/rawprep/`：五模块公开业务步骤：`read.py` 样本发现/读取/提取及域类型；`derive.py` 可选几何装配；`select.py` 选场/组契约校验/筛选；`save.py` 实际路径/编码/提交和轻量结果；`stats.py` 训练样本/字段/缺失策略与统计量。无批量循环，不导入 run。
- `packages/ai4e-core/applications/aero_cfd/model/`：贡献模型引用、初始权重、冻结和学习目标装配。
- `packages/ai4e-core/applications/aero_cfd/train/`：`fitting.py` 装配训练、评估、监控与恢复；`resolve.py` 展开默认（设备默认自动选择）并联合校验；`__init__.py` 保留旧只读调用的兼容导出，读盘实现位于 trainprep/dataset.py。
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

- 配置入口：先调用 `configured_geometry_enabled(config)`，再把返回清单传给 `derive_configured_geometry(extracted, enabled=...)`；无清单时关闭全部。原子函数仍可直接调用。
- 几何输入最低仅含 vtk；公开类型在 rawprep/derive.py，提取允许显式 fields: {}。法向仅需 surface，其余几何需 surface/volume。
- tests/integration/test_geometry_domain.py 覆盖门禁、身份回贴、孤立点、可选执行、冲突、配置迁移与本地 ShapeNet；test_extract_clean.py 覆盖无标签提取。

## Dataset 与脚本入口

- `docs/PRD/ai4e-core/base/PRD.md`：配置与能力事件行为。

- `applications/base/dataset.py`：只持有样本引用与顺序步骤的 Dataset，不持有批量网格。
- `applications/aero_cfd/rawprep/dataset.py`：按需装配、输出预检、安全保存、清单和训练统计；保留旧单样本调用。
- `base/events.py`：阶段上下文、能力开始/结束/失败与真实耗时；后台心跳继承阶段和样本，无文件 handler。
- `run/dataset.py`：逐样本消费步骤和通用保存策略，不解释物理字段。
- `run/session.py`：脚本 launch、配置路径插值解析、单次运行会话与阶段上下文设置/恢复。
- `run/writer.py`：单份生效配置、带阶段前缀的能力日志、按事件元信息筛选的控制台摘要、延迟创建的错误日志。
- `applications/aero_cfd/trainprep/dataset.py::open_manifest_sample`：按产物清单的实际路径、形状和 physical 状态读回；标准训练准备可传 train.manifest。
- `tests/integration/test_dataset_recipe.py`：新入口全链测试；其余 pre/geometry/source/train 测试保留历史原子契约回归。

- `tests/integration/test_recipe_logging.py`：阶段切换、异常恢复、后台心跳身份及控制台摘要；复制入口一致性见 `test_dataset_recipe.py`。

## 本次实施定位（2026-09-08）

- `applications/aero_cfd/trainprep/dataset.py`：按清单读盘、物理/归一化/采样探测。
- `applications/aero_cfd/trainprep/normalization.py`：字段绑定、冻结参数与配置冲突检查。
- `applications/aero_cfd/model/abupt.py、objectives.py`：注入模型与学习目标。
- `applications/aero_cfd/train/fitting.py`：训练业务装配（正式贡献网络的小配置已验收）。
- `applications/aero_cfd/post/evaluation.py`：独立评估装配。
- `applications/aero_cfd/post/stage.py`：解析检查点、只恢复权重、锚点评估保存与完整网格回贴开关。
- `applications/aero_cfd/post/export.py`：按样本提交物理预测和可选锚点点云。
- `applications/aero_cfd/post/mesh.py`：测试下标、原始网格路径、固定锚点、查询坐标的模型设备交接、分块查询与反变换。
- `abilities/inference/rebuild.py`：只加载模型权重。
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
- `abilities/constraint/compare.py、supervised.py`：四种比较方法与可配置监督；物理约束未进。
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

`applications/aero_cfd/post/inference.py`：注入贡献上下文，检查点重建与分块点场查询。`trainprep/dataset.py`：显式物理派生规则；`normalization.py`：通用字段与条件冻结变换。`abilities/training/batch.py`：嵌套设备搬运。`run/training.py`：按阶段交付报告。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## 三阶段交接与训练行为对齐

- `applications/aero_cfd/trainprep/preparation.py`：公开准备步骤、持久化引用与数据内容校验。
- `applications/aero_cfd/train/fitting.py`：open_training/build_model/configure_objectives/configure_optimization/configure_evaluation/execute_training。
- `abilities/training/callbacks.py`：普通可调用组件的 update/epoch 周期包装。
- `run/session.py::stage`：单会话内显式执行阶段并返回交付物；配置 resolver 由 recipe 注入。
- `run/writer.py`：唯一 config.yaml、原子 JSON 阶段交付、独立 EMA 权重文件。
- `abilities/geometry/nearest.py`：锁定 sklearn 1.9.0 近邻实现以保持等距点方向与官方一致。
- `tests/integration/test_train_boundary_alignment.py`：累积尾组、异常轮次重放、EMA 周期和真实诊断。

三阶段数值回归：`tests/integration/test_reference_arithmetic.py` 使用 `tests/fixtures/abupt_inputs/normalization.json` 的独立官方归一化夹具；版本迁移见 `.context/mvp/abupt-reference-acceptance.md`。

post 默认 `post.random_stream=global`，从独立固定种子开始重建与采样；锚点和网格分支隔离随机状态，旧 independent 按样本采样仍可选择。

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

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。

## 五段配置与快照职责（2026-09-09）

run/session.py 的 config_loader 为通用加载回调；applications/aero_cfd/configuration.py 保留旧路径解析。run/training.py 只幂等确认快照；run/dataset.py 写来源报告、显式转交保存预检 settings。
