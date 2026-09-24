# ai4e-contrib 模块索引
## 当前职责与本轮变更

- [经典网络主计划](../../.cursor/plans/classic-networks-main.plan.md)：`application/classic_networks/` 已按配置、Darcy、ShapeNet体场、Double Cylinder及准备/预测形成源码连接；中立网络本体归core，业务布局与监督语义留在此层。十三组100更新及六项独立wheel/Python/Task流程已完成统一验收，设备和覆盖范围以专项记录为准，具体文件见下方经典网络小节。

ability 中不可中立化的模型/方程与 application 中的数据适配、模型专属配置、步骤和局部连接。来自单个模型源码的通用计算优先进入 ai4e-core/abilities；contrib 不承载通用图构造、批处理、rollout 或评价。

## MeshGraphNets / CylinderFlow 与静态外流扩展

- `ability/model/meshgraphnet/`：MeshGraphNet 的 Encoder/Processor/Decoder 模型本体及静态单域/多域外壳；通用图消息传递、网格边和分区复用 core。
- `application/datasets/cylinder_flow/`：官方 meta/TFRecord 字段、固定轨迹、九类节点和 train/valid/test 分片适配；通用 TFRecord framing、图构造和评价复用 core。
- `application/spatiotemporal_pde/meshgraphnet/`：完整 11 维节点归一化、Normal 噪声、Normal/Outflow loss、速度增量、边界保持 rollout、恢复合同和来源身份。
- `application/aero_cfd/meshgraphnet.py`：静态外流字段、工况广播、核心节点监督、分区拼回和检查点身份连接；ShapeNet-Car 使用表面/体积两个独立子网络，NASA CRM 使用表面子网络。
- `recipes/meshgraphnet/`：可复制研究流程；长期行为见 `docs/PRD/recipes/meshgraphnet/PRD.md`，当前工程验收由相关 integration tests 记录。

- `packages/ai4e-contrib/application/aero_cfd/configuration.py`：官方配置分组转换和本地扩展参数连接。
- `packages/ai4e-contrib/application/aero_cfd/abupt.py`：AB-UPT 默认布局和专属参数校验。
- `packages/ai4e-contrib/application/aero_cfd/transolver3.py`：Transolver-3 专属配置连接，接受现行 eval 与旧 validation 评价切片名；组件平台约束发布 eval。回归见 `test_transolver_training.py`。
- `packages/ai4e-contrib/application/aero_cfd/loader_adapter.py`：显式旧外流加载适配，不反向转导出通用 run。
- `packages/ai4e-contrib/application/parametric_pde/pibsnet.py`：PDE 准备参数连接，不约束其他组件。
- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


- [Ability 五类简表](../../docs/abilities-summary.md)：简表中的模型构建及专用数据准备/推理包含已有贡献模型路线，不表示任意模型配置均受支持。

- [Ability 源码盘点表](../../docs/abilities-inventory.md)：贡献模型与 core 通用能力分列，包含完整网络、专用准备、推理及内部组件。
- [合并后的 Ability 清单](../../docs/abilities-merged.md)：v2 明确列出位置编码、池化、条件调制、域/物理切片注意力及输出映射等模型内计算单元，区别于薄包装；保留专用准备/推理与源码对照。

已实现可安装、可 import 的共享数据集适配；不实现平台上传。仅使用 core/spec 的公开接口。

- `packages/ai4e-contrib/pyproject.toml`：workspace 包和资源打包。
- `packages/ai4e-contrib/application/datasets/shapenet_car/adapter.py`：按 manifest 选择样本与分片，不加载网格。`unsplit` 把官方名单收成单一训练宇宙，供平台原始处理不按 train/test 落盘。
- `packages/ai4e-contrib/application/datasets/shapenet_car/manifest.yaml`：数据结构、字段分量/归属、未知单位、输出契约；能力与默认均打开 VTKHDF；默认写出 `formats: [pt]`。
- 同目录 `partition.yaml`：官方 train/test 稳定样本名单；`statistics.yaml`：显式选择的参考统计。
- `packages/ai4e-contrib/application/datasets/nasa_crm/manifest.yaml`：NASA 默认写出 `formats: [pt]` 并开启 VTKHDF；`physical.py` 使用官方 connectivity 与每样本坐标构造 `surface.vtkhdf`。
- `docs/PRD/ai4e-contrib/application/PRD.md`：适配器复用、复制修改和失败规则；SafeDiffCon 的参考数据准入与正式适配交付边界。现已新增控制算法与案例，验收范围见专项记录。
- `tests/integration/test_dataset_recipe.py`：安装、复制与自定义 manifest 交接。

## 本次实施定位（2026-09-08）

- `ability/model/abupt/`：network.py 与 modules 保留完整网络，model.py 为构造/输出入口；sampling.py 与 batch.py 声明模型布局。超节点半径检索在 MPS 上先回 CPU 再搬回边索引；复数旋转保持 MPS，已验前后向。scatter_reduce 的 MPS 非确定性仍限制严格复现。
- `ability/model/abupt/README.md、LICENSE、source.json`：来源、许可和源码摘要。Notice 在包根统一打包。
- `pyproject.toml`：abupt 可选依赖；使用已验证镜像，uv.lock 已锁定可选依赖；PyG 固定 2.6.1，图扩展复用当前 Torch 构建。
- `docs/PRD/ai4e-contrib/ability/PRD.md`：贡献模型说明。

## 多域模型变更

`ability/model/abupt/domains.py`：有序域、字段、特征和条件布局。`network.py` 与 `modules/blocks/domain.py`：唯一多域网络、条件调制与逐层 K/V；无条件路径经模块 `forward` 进入 `forward_domains`，供结构跟踪收成模块盒。`inference.py`：缓存验证、上下文释放与查询分块。`sampling.py`/`batch.py`：按声明绑定和嵌套收批。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

network 输入错误保留 ValueError 并拆分实际/期望约束；sampling 元信息提供分片下标。相关测试见 test_framework_correctness.py。

## 双模型组件入口

- `application/aero_cfd/`：全限定组件加载及缺省汽车组件选择；不代表兼容旧公开配置树。`loader_adapter.py` 是显式旧外流加载适配；通用运行器不解释业务键。`operations.py` 的 inspect 对现行公共键做输入绑定，并把临时数据输出隔离到检查目录；历史旧键仍走原检查门面，不改写任务 YAML。
- `application/datasets/nasa_crm/`：HDF5/NPY 视图、字段声明、拓扑适配。
- `ability/model/{abupt,transolver3}/component.py`：组件出口；AB-UPT 声明可配置点/锚点/查询采样，Transolver-3 声明抽稀步长只读的采样与固定 MSE。
- `ability/model/transolver3/`：独立训练网络、缓存解码、适配与来源摘要。

历史数值对标及其范围见 `.context/mvp/transolver3-acceptance.md`；当前公开入口和兼容边界见 `.context/mvp/architecture-alignment-acceptance.md`，不迁移历史任务。

NASA 的 `SOURCE_PATH_FIELDS` 声明来源路径，复制 recipe 按配置目录解析；contrib transolver3 extra 依赖 core 的 hdf5 extra，HDF5 导出依赖由 core 唯一清单管理。

## 物理数据跨模型实验

datasets/{nasa_crm,shapenet_car}/physical.py：物理字段与原拓扑适配；ability/model/{abupt,transolver3}/preparation.py：模型专用输入及完整推理。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `application/datasets/{shapenet_car,nasa_crm}/inspection.py`：样本依赖和真实字段目录，供平台检查门面调用。
- `ability/model/{abupt,transolver3}/component.py`：公开损失与训练限制描述；平台依据真实组件约束显示优化器、采样与学习目标。

## 显式 Recipe 组件适配

`application/aero_cfd/__init__.py` 的配置默认解析只选择数据/模型，旧 load/workflow 调用兼容保留；新模板和五例直接使用公开业务步骤。用户字段与采样例在 `examples/recipe_extensions/`，入口及验收见 recipes 模块索引和 `.context/mvp/recipe-explicit-acceptance.md`。


## PI-BSNet 与物理数据

- `packages/ai4e-contrib/ability/model/pibsnet/`：model 网络、spline 物理样条、component 准备/求值/训练步、README 来源与修正。
- `packages/ai4e-contrib/ability/constraint/equations/`：普通张量方程函数，包括二维 NS。
- `packages/ai4e-contrib/application/datasets/parametric.py`：独立生成清单、身份校验及读取器。
- `packages/ai4e-contrib/application/datasets/{convection_diffusion,neumann_diffusion,advection,burgers,diffusion_trapezoid}/generate.py`：五例各自生产算法和入口。
- `docs/PRD/ai4e-contrib/ability/PRD.md`、`docs/PRD/ai4e-contrib/application/PRD.md`：长期功能正文。
- `.context/mvp/pibsnet-acceptance.md`：实际证据和未验收边界。

- `tools/verification/pibsnet/reference_advection.py`：摘要锁定原 Advection 训练循环，同数据独立参考；`test_pibsnet_reference_protocol.py` 验证执行与配点协议。

## 声明驱动原始处理

数据集 shapenet_car/nasa_crm 的 descriptor.py 提供 describe_rawprep；manifest.yaml 提供默认值、绑定槽位、本机识别规则（目录标记或三文件名）、输出及能力依赖，inspection.py 返回样本范围、检查覆盖与缺项。平台 `sample_scope` 检查用官方/自身分片作输入宇宙，回传 `sample_universe`。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

## 原案例迁移

source_cases.py装配原Neumann/Advection；neumann_numerics.py/advection_numerics.py保留各案例不同数值定义；对应generate.py生产原FP32/连续流数据。

## 独立推理参数

- `ability/model/abupt/preparation.py`：原生 infer 的查询参数交接；旧 post 路线独立保留。Transolver 专用状态汇总不改。
- 长期正文 `docs/PRD/ai4e-contrib/ability/PRD.md`；数值验收 `tests/integration/test_infer_stage.py`。

## 推理工作台选择与统计

`ability/model/transolver3/{inference,preparation,component}.py`：缓存后解码查询块；同时提供物理视图 `prepare_sample` 与通用准备链的平面字段 `prepare_inputs`，后者不要求 AB-UPT `data_specs`，组件拼批兼容两种入口。`application/datasets/{shapenet_car,nasa_crm}/{physical,__init__}.py`：字段、分量、单位描述。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

共享数据兼容：`application/aero_cfd/loader_adapter.py` 隔离旧加载器不认识的并行与多格式键，仅本次托管运行生效，冻结脚本不改写；验收见 Task 共享专项。

## GenCP

`ability/model/gencp/`：cno、sit_fno、adapters、原模型 modules、source.json 与许可证。`ability/transform/gencp/`：normalization/preprocessing/state/conditions/boundaries；`constraint/gencp/objective.py`、`inference/gencp/velocity.py`、`postproc/gencp/reference.py` 各司数值职责。`application/datasets/gencp/` 为 fsi/ntcouple 读取描述及 manifests；`application/coupled_physics/gencp/` 为 configuration、cases、validation。模块长期说明归现有 ability/application PRD，实际验收见 [GenCP](../mvp/gencp-acceptance.md)。

## SafeDiffCon 限时集成

- `ability/model/safediffcon/`：两种原UNet与构造器，LICENSE/source.json覆盖迁入数值定义。
- `ability/{constraint,inference,training,transform,eval,postproc}/safediffcon/`：原扩散/残差、校准与重权、EMA、原生缩放、物理指标和Burgers/KSTAR响应；KSTAR在隔离解释器运行。
- `application/datasets/safediffcon/arrays.py`：HDF5/Arrow和ZIP原数据读取。
- `application/pde_control/safediffcon/{configuration,migration,handoff,stream,training,inference,solver}.py`：公共/内部配置边界、只生成新配置的迁移、数组/指标与阶段权重登记、尾批游标、训练与推理局部连接。求解器解释器保留虚拟环境路径。
- `configuration.py` 的预训练总更新目标默认4000、短实验上限20000；恢复历史包含在总数内。墙钟预算由工具层持久账本负责，旧准备和配置继续兼容。
- `docs/PRD/ai4e-contrib/{ability,application}/PRD.md`第三章：算法与案例功能；当前范围见`.context/mvp/safediffcon-acceptance.md`。

WDNO 的原版历史切片与当前缩小范围迁移分开记录；可安装基础能力和连接见下方，执行与数值验收见 `.context/mvp/wdno-acceptance.md`。

## WDNO 基础预测与共享EMA

- `ability/model/wdno/{unet,schedules}.py`：作者二维网络、辅助算子与噪声日程；`source.json` 为抽取位置及完整摘要。
- `ability/constraint/wdno/objective.py`：原条件噪声目标；`ability/inference/wdno/{diffusion,predict}.py`：原扩散采样与物理预测函数。
- `ability/transform/wdno/{layout,multiscale,preparation,burgers}.py`：原系数布局、保留的辅助定义、模型准备及基础物理正逆变换；多尺度分支保留源码不等于超分闭环已支持。
- `ability/eval/wdno/{metrics,physical}.py`：原MSE及固定场评价绑定。
- `ability/training/moving_average.py`：WDNO/SafeDiffCon共享原EMA适配，旧SafeDiffCon路径保留门面。
- `application/spatiotemporal_pde/wdno/{data,configuration,model,training,inference,stream,provenance}.py`：原始Torch来源、严格配置与路径、网络/条件连接、优化/恢复、独立采样、可恢复原随机批次顺序、实际组件身份及研究目录源码归档。
- 功能正文：贡献ability第四章、application第四章；依赖`wdno` extra；不注册平台。
- 验收：`test_wdno_migration.py`、`test_wdno_recipe.py`、真实对照工具 `tools/verification/wdno/migration.py`。

- `tests/integration/test_wdno_migration_acceptance.py`：显式真实两侧2000步、64/128预测和独立安装产物门槛；无真实产物不能记通过。

WDNO公共约定调整：`application/spatiotemporal_pde/wdno/handoff.py`连接分片输入冲突、资产依赖及MSE语义；`migration.py`仅显式转换旧用户配置副本。configuration读取公共inputs/data_root，训练和推理不读旧用户路径键。数值与冻结合同不变；验收test_wdno_task.py及专项记录。

公共研究配置：`application/aero_cfd/inputs.py` 只在领域边界展开输入路径；`operations.py` 的检查与推理检查共用该连接，管理层不解释模型配置。GenCP训练片段参数校验、条件扩展及直接/Task证据见Recipe/Task专项。

## WDNO最新公共约定补验（2026-09-17）

WDNO handoff.py共用数组依赖解析；指标绑定清单与全部数组，资产保留bundle_root；test_wdno_public_metrics覆盖篡改、缺失、越界和科学口径。无需修改公共索引格式。 当前结果以 `.context/mvp/wdno-acceptance.md` 为准。

## WDNO 局部训练策略

`application/spatiotemporal_pde/wdno/{training,configuration}.py` 接收可选优化器/调度器/更新函数并记录来源；未选择保持原合同。`inference.py` 对固定权重忽略新增训练策略身份，原模型/数据/目标身份仍严格检查，完整续训不忽略策略。示例与验收从 [研究任务导航](../tasks/research.md) 进入。

## GeoTransolver

- `ability/model/geotransolver/{network,__init__}.py`：网络组合公开入口；`README.md/source.json/LICENSE`说明支持范围和来源。
- `application/geotransolver.py`：模型构造、Muon/AdamW分组选择、参考调度及公共配置绑定。实际数学和状态属于core。
- `application/datasets/{darcy_flow,bumper_beam}/{adapter.py,__init__.py,manifest.yaml}`：来源文件、字段、样本身份、单位与工况顺序。
- `application/{parametric_pde,spatiotemporal_pde}/geotransolver/{binding,configuration,__init__}.py`：分别绑定Darcy与保险杠；无贡献侧训练/预测循环、统计或报告算法。
- PRD：贡献ability与application第六章；真实状态见 `.context/mvp/geotransolver-acceptance.md`。不登记Web案例。

## PCNO 发布连接

`ability/model/pcno/`：组合、严格原权重导入、GPL许可证与source.json；`application/datasets/geothermal_cmg/adapter.py`：24/18例身份及字段校验；`application/geothermal/pcno/`：configuration、protocol、objective、training、inference、economy、post。计算主要在core。PRD见ability/application正文。

根 `dev` 组选择 `ai4e-contrib[pcno]`，默认开发环境由现有 extra 继续取得 `ai4e-core[geothermal]`、`iapws==1.5.4` 与 pandas；依赖仍只在各包 `pyproject.toml` 和根锁文件维护，不在测试中临时安装。


## GeoTransolver 外流扩展

`application/aero_cfd/geotransolver/{configuration,binding}.py` 绑定 ShapeNet-Car 双域和 NASA CRM 全局工况；`ability/model/geotransolver/network.py::forward_stream` 复用网络权重，仅支持无局部非结构分支。计算与循环仍由 core 提供。

行为见对应模块 PRD；实际证据与边界见 [外流验收](../mvp/geotransolver-aero-acceptance.md)。

## PCNO圆柱连接

`ability/model/pcno/cylinder.py`：变体组合；`application/datasets/cylinder_flow/download.py`：官方子集；`datasets/gencp/cylinder.py`：5/1轨迹及未清零速度；`application/spatiotemporal_pde/pcno/`：configuration/objective/training/inference/post。CylinderFlow物理准入未通过。

功能正文见相应模块PRD；实际范围见[圆柱验收](../mvp/pcno-cylinder-acceptance.md)。

## Task 通用化交接（实施中）

- `application/aero_cfd/task_description.py`、`task_inference.py`：输入标签和输出声明、检查点科学身份及子运行计划。
- `application/aero_cfd/task_results.py`、`task_post.py`、`task_datasets.py`：固定结果、指标/字段、处理身份、科学清单及副本转换。
- `application/aero_cfd/model_inspection.py`、`abupt_stage_display.py`：两档图与特定网络阶段包装；调用 core ability。
- `application/pde_control/safediffcon/{operations,task_description}.py`：同一管理入口的控制用途/权重标签，未实现操作明确不可用。
- `application/parametric_pde/resources.py`：清单显式 smoke 数据生产。

公开接口变化、圈定测试与未验范围见 [本轮验收](../mvp/task-generalization-acceptance.md)，功能正文更新既有对应 PRD。


## 经典网络数据与研究连接

- `application/classic_networks/configuration.py`：按配置位置加载/覆盖、数据与模型局部校验、全限定普通构造器；不增加全仓网络注册。
- `darcy.py`：共同原ID采样坐标/系数/解；`shapenet_volume.py`：官方分片、体网格/表面距离、真实单元插值与有效域回贴（距离为来源顶点场插值近似）；`double_cylinder.py`：来源时间/坐标身份、三帧历史与一帧目标及独立轨迹分片。
- `preparation.py`：物理来源、训练分片有效域统计、模型独立准备和可搬移数组清单读回、ShapeNet物理快照；`binding.py`：网络构造、末轴场/卷积/token/图/真实序列布局、取批及监督。
- `prediction.py`：固定推理、反变换、派生声明保存、original_*拼接/offsets以及独立分场/原点覆盖评价。普通派生范数默认unknown，不将混合物理分量解释为速度模长。
- 消费者：`recipes/classic_networks/`与`examples/classic_networks/`三案例；扩展登记：`examples/recipe_extensions/network_composition/`，见recipes索引。
- 功能正文：`docs/PRD/ai4e-contrib/application/PRD.md`第八章。圈定来源检查为`test_classic_network_data.py`；运行/资源检查为`test_classic_network_pipeline.py`与`test_classic_network_examples.py`。源码和非训练证据不能代替主控真实训练、安装与Task验收。

本批阶段证据与未验范围见[经典网络统一验收](../mvp/classic-networks-acceptance.md)，该记录已按本批缩小验证范围完成。


## 算子学习与普通代理应用

新增应用只绑定领域输入、训练目标及配置，计算正文由 core 持有。功能正文见 `docs/PRD/ai4e-contrib/application/PRD.md` 第九、十章；真实数据矩阵和安装仍待本批统一验收。

- `packages/ai4e-contrib/application/operator_learning/configuration.py`：本地模型/网格/完整场/物理权重检查；`preparation.py`：复用 classic 场准备公开入口；`binding.py`：固定传感器、逐样本坐标、FNO通道和真实历史顺序，完整网络普通构造器替换。
- `application/operator_learning/objectives.py`：复用 core `residual_loss`；Darcy 反变换物理解后计算非负违约及监督。来源支持正系数、非负源和零 Dirichlet 的最大值原理，不把采样外圈当精确零边界，不宣称完整 PDE 或新增 PINN。
- `application/surrogate_modeling/preparation.py`：NASA 六工况/三响应属性表、来源身份和训练统计；从 classic 双圆柱准备去重训练快照、冻结 POD、三帧系数输入与下一帧目标；`preparation_identity` 绑定顶层、分片与基状态内容并允许搬移。
- `application/surrogate_modeling/fitting.py`：RSM/RBF/独立目标 Kriging/LightGBM 的显式拟合装配；`configuration.py`：案例、预算和普通全限定组件解析，不增加框架注册表。
- `application/surrogate_modeling/prediction.py`：普通状态重建与 `predict_prepared(..., predictor=...)` 注入；NASA物理响应、POD固定解码，Kriging NASA物理 latent 方差及POD系数 latent 方差；固定结果继续交由 classic `prediction.evaluate` 消费。
- 调用方：`recipes/operator_learning/{darcy,shapenet_volume,double_cylinder}/` 与 `recipes/surrogate_modeling/{nasa_crm,double_cylinder}/`。NASA表不是平台网格准备，不能借此省略真正场数据的VTKHDF/实体交付。
- 圈定测试：`test_operator_blocks.py`、`test_operator_physical_loss.py`、`test_operator_surrogate_data.py`、`test_surrogate_source_identity.py`（NASA跨分片完整属性重复拒绝，同工况异响应诊断）。数据流程用例含训练独立统计/轨迹身份、POD基、目录搬移、方差与自定义预测器、两例仓库外复制和无模型独立post；使用合成夹具，不算真实数据训练验收。
