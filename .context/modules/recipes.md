`tests/integration/test_pibsnet_trapezoid_acceptance.py`：完整预算报告门槛及真实双方权重/历史/十个场验收；实跑目录通过DOJO_TRAPEZOID_ACCEPTANCE_ROOT指定。

`tools/verification/pibsnet/trapezoid_environment.py`：同一Dojo环境执行原数值函数的完整预算验证，分离运行环境与框架迁移差异。

梯形迁移：`tools/verification/pibsnet/trapezoid_dojo.py` 独立生成/源数组与初权重预检、实际recipe完整训练/独立post及报告；`examples/parametric_pde/diffusion_trapezoid/` 为10实例。`docs/pibsnet/Neumann与Advection输入核查.md` 为两例只读核查；`test_pibsnet_trapezoid_alignment.py` 为逐层/恢复验收。

# recipes 模板索引

- [经典网络主计划](../../.cursor/plans/classic-networks-main.plan.md)：`recipes/classic_networks/` 三个数据案例、`examples/classic_networks/` 完整复制案例和 `examples/recipe_extensions/network_composition/` 三项重组扩展已形成源码与资源登记。先合并组件再顺序训练；十三组100更新及六项独立wheel/Python/Task流程已完成统一验收，设备和覆盖范围以专项记录为准，未登记平台模型。

## MeshGraphNets / CylinderFlow

- `recipes/meshgraphnet/`：固定二维网格的 MeshGraphNet 时空预测流程，显式交接 rawprep、trainprep、train、infer、post；Python 决定顺序，YAML 只提供参数。
- `docs/PRD/recipes/meshgraphnet/PRD.md`：Recipe 长期功能与使用约定。
- `tests/integration/test_meshgraphnet_core.py`、`test_tfrecord_source.py`、`test_meshgraphnet_recipe.py`：core-first 图能力、TFRecord/轨迹适配、累计指标、直接 Recipe、固定 post、恢复和 Task 托管。
- `.context/mvp/meshgraphnet-acceptance.md`：参考版本、真实单条官方轨迹、wheel、工程测试和论文级未验范围。
- `.context/mvp/meshgraphnet-aero-cfd-acceptance.md`：ShapeNet-Car/NASA CRM 静态图准备、短训、完整拼回、全表面分区缓存、Task、wheel 与正式 Web rawprep；Web 模型训练/推理边界单列。

- `.cursor/plans/wdno-reproduction-and-agent-composition.plan.md`：2026-09-17 按计划rules重排；基础迁移和Task适配已完成，近期补公开API新建任务及分阶段实跑、独立Agent使用；完整配置和研究脚本示例、文件职责、逐叶验收已列明，正式论文复现保留前置条件。
## 参数化 PDE 模板

- `docs/pibsnet/设置与算法一致性核查.md`：五例PDF/源码/Dojo设置与算法差距、未决来源冲突和不依赖最终误差的验收链；2026-09-14只核查。

- `recipes/parametric_pde/`：configuration 加载和校验；generate 独立生产；rawprep/trainprep/train/post 独立阶段；pipeline 顺序交接；README 用户命令。
- `examples/parametric_pde/`：五个案例各自 config.yaml 与 generate.yaml；equations.py 演示 Burgers/NS 直接调用。
- `docs/PRD/recipes/parametric_pde/PRD.md`：长期功能与使用约定。
- `.context/mvp/pibsnet-acceptance.md`：数据、训练、安装和原仓库对照状态。

- `docs/yaml-config-comparison.md`：五框架运行 YAML 的源码梳理与 Dojo 配置讨论；非实施决策，不替代 PRD 或架构正文。

平台原型映射：`docs/prototypes/dojo-web-wireframe.html` 通过配置快照展示 aero_cfd 四阶段及其产物交接，不执行或修改 recipe。参考图与字段来源见 web 模块索引。

普通文件集合，不是 workspace 成员或安装包。允许引用 core/spec/contrib；task 将来复制文件，不导入 recipe。

- `recipes/aero_cfd/README.md`：复制、安装依赖、执行和参数说明。
- `recipes/aero_cfd/config.yaml`：实验选择、路径插值与统计策略；新默认 VTKHDF 开、归一化副本开，场上 `scale` 默认 1，AB-UPT 官方案例坐标预填 1000，`rawprep.formats` 可同时写 PT/Zarr；与清单默认合并时以平台 `formats` 覆盖旧单键，`rawprep.workers` 控制并行样本线程。
- `recipes/aero_cfd/pipeline.py`：显式顺序串接 rawprep/trainprep/train/infer/post。
- `docs/PRD/recipes/aero_cfd/PRD.md`：模板行为与迁移。
- `tests/integration/test_dataset_recipe.py`：复制脚本、路径、统计、失败与日志验收。
- `tests/integration/test_aero_cfd_documents.py`：外流脚本交接、NASA HDF 物理 rawprep，以及有拓扑来源的 ShapeNet/NASA 默认打开 VTKHDF。
- `tests/recipe_assets.py`、`tests/legacy_pre.py`、`tests/fixtures/legacy_pre.yaml`：旧行为回归夹具，不是产品入口。

不包含 init/main、缓存、训练占位和用户组件目录；共享 manifest/adapter 在 contrib。

## 本次实施定位（2026-09-08）

- `aero_cfd/train.py`：probe/prepare/fit 单一会话入口。
- `aero_cfd/post.py`：显式登记恢复、预测、物理输出、评价、保存和网格步骤。
- `aero_cfd/config.yaml`：公开采样预算、模型参数、损失权重、设备自动选择、Lion/调度/累积/`test_repeat`/快照与 VTKHDF 开关；post 含评估/保存/点云/完整网格回贴开关与 `sample_indices`。

## 多域模型变更

`recipes/aero_cfd/post.py`：通过 run.launch 加载配置，只读取固定推理结果；pipeline 显式连接 rawprep/trainprep/train/infer/post。`config.yaml` 的 infer 控制预测、评价与网格交付，post 历史参数仅供旧数值入口兼容。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## 三阶段 recipe 与参考验收

- `recipes/aero_cfd/rawprep.py`：数据前处理显式业务流水线。
- `recipes/aero_cfd/trainprep.py`：独立准备、全分片校验与 preparation.json 引用；可选 `trainprep.split` 重划 train/test/eval，官方名单不改。
- `recipes/aero_cfd/train.py`：消费准备引用、构建模型、目标、优化、评估与执行；成功后按 `train.export_predictions` / `export_vtk` / `export_split` 显式写出，默认关闭。
- `tests/integration/test_recipe_three_stage.py`：独立入口、完整流水线、干跑和数据冲突。
- `.context/mvp/abupt-reference-acceptance.md`：逐阶段官方对照及未完成门槛。

端到端样板默认包含 post；config 不预填未来准备引用或检查点。独立运行时可通过公开覆盖指向已有产物，连续运行自动交接。见 `.context/mvp/abupt-end-to-end-acceptance.md` 与 `tests/integration/test_post_reference.py`。

README 新增按 post-progress.json 检查部分交付、已有检查点仅补网格及自动比较协议说明；配置不增加未来输出输入项。

## Task 接入

- `.cursor/plans/safediffcon-task-transparent-execution.plan.md`：SafeDiffCon公共约定适配实施计划；已补齐案例、配置迁移和实际安装下双入口真实计算，证据见专项验收。

历史说明（已被公共 pipeline/config 与 inputs 约定取代）：`aero_cfd/task-entry.json`：显式输入输出绑定、恢复键与标量比较定义；模板不导入 task。
- `.context/mvp/task-acceptance.md`：相关验收入口。

## 双模型组件入口

- `recipes/aero_cfd/`：共享阶段脚本。
- `examples/aero_cfd/shapenet_car_abupt/`、`nasa_crm_transolver3/`：复制案例、配置和使用说明。

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。

## 五段配置与快照职责（2026-09-09）

历史五段收组切片：configuration.py 负责配置加载与映射，当时 rawprep.py 调用整段 datapre；该入口写法由下述 2026-09-11 显式步骤设计取代。test_recipe_configuration.py、test_run_config_snapshot.py、test_verification_config.py 覆盖本轮。

## 物理数据跨模型实验

- `docs/ai4s-framework-comparison.md`：Dojo 与五框架的能力比较；后续通过新模型、数据集和科研案例发现共同需求，相关建议按案例触发，不预设接入清单或前置重构。
- `tests/integration/test_framework_comparison_document.py`：比较文档的索引与仓内证据链接检查；本次只新增参考文档和演进约定，不改变案例执行行为。

examples/aero_cfd/ 下有九个独立配置，阶段脚本基于 recipes/aero_cfd，物理流程以对应公开步骤显式编写；除原五例外，另有 ShapeNet-Car 与 NASA CRM 两个静态 MeshGraphNet 和两个普通 GALE GeoTransolver 案例。公开配置把原始输入、已处理数据、数据产物和运行记录分别放在复制目录的 `../inputs`、`../datasets`、`../data`、`../runs`，不写进案例代码目录；`infer.seed` 作为公开可选参数保留。公共模板与 AB-UPT 固定锚点链；Transolver、MeshGraphNet、GeoTransolver 固定物理链。`trainprep.topology` 仅控制从平台 VTKHDF 派生图，MeshGraphNet 缺必需拓扑时拒绝。所有 ShapeNet 与 NASA 案例均打开 VTKHDF；NASA HDF 来源使用其物理 rawprep 步骤，数据集清单默认支持网格交付。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `docs/aero-cfd-server-runbook.md`：复制五例、CUDA预检、50轮配置、分阶段执行与报告交付操作手册。

- `.context/mvp/cross-model-50-acceptance.md`：沿用五例网络与共享入口的50轮实验；验收测试支持显式epoch/设备预算，历史默认不变。

## Web 复用

平台只复制现有 aero_cfd，经 task 的原 submit_run 覆盖原始处理阶段和固定样本。不修改模板或生成替代脚本。真实接入与输出交接见 `.context/mvp/web-rawprep-acceptance.md`。

- `aero_cfd/configuration.py`：规范模型采样写入 model.sampling；旧 trainprep.sampling 由 application 显式转换副本，双键冲突拒绝；Task 保存不自动迁移。字段容器和 PT/Zarr 格式保留于 rawprep。

## 本机实验存储位置

按 AGENTS.md 的本机约定，新训练输出使用 `/Users/zonghui/work/project_simulation/dojo_train/<实验名>/`，显式配置运行与预测路径。50轮运行已迁至 `dojo_train/dojo-cross-model-50`；七个用户指定的历史工具缓存/暂存目录已同名迁入 dojo_train，迁移记录为该目录下 `cache-relocation-20260910.json`。旧tmp位置仅保留兼容链接，未变更可复制模板的跨机器默认路径。
历史说明（已被公共 pipeline/config 与 inputs 约定取代）：`aero_cfd/task-entry.json`：当前比较量采样选择器使用 `model/sampling`，旧运行仍读取其代码快照中的历史 entry，不迁写冻结资产。

## 显式流程与真实扩展

- `.cursor/rules/ai4e-recipe-authoring.mdc`：模板正文、参数、扩展与复制验收规范。
- `.cursor/plans/显式_recipe_步骤_9ea01c80.plan.md`：批准的实现范围及各文件完整目标写法。
- `recipes/aero_cfd/configuration.py`：组件选择与案例本地 STEP_PARAMETERS 声明；Python 定顺序，YAML 只供参数。
- `examples/recipe_extensions/README.md`：两例导航。
- `examples/recipe_extensions/field_mapping/`：速度模长函数、字段声明、统计、归一化和模型特征的完整可复制目录。
- `examples/recipe_extensions/sampling/`：实际训练迭代中的几何采样替换。
- `tests/integration/test_recipe_extensions.py`：仓库外字段、采样、错误输出与独立后处理。
- `tests/integration/test_recipe_documents.py`：规范、计划目标代码与索引一致性。
- `.context/mvp/recipe-explicit-acceptance.md`：逐项测试证据、迁移与未交付边界。

- `docs/pibsnet/原始训练流程功能列表.md`、对应 `.xlsx`：保留原始122项对照。
- `docs/pibsnet/实施映射.md`、对应 `.xlsx`：逐项实现位置与当前验收状态，不能当作全部通过报告。
- `examples/parametric_pde/generalization.yaml`：复用 Advection 数据的独立泛化协议。
- `tools/verification/pibsnet/`：reference_cd/reference_neumann 外部锁定源码分支；compare 同数据预算校验；derivatives 消融；generalization 经验拟合；plots 已完成产物绘图。
- `tools/verification/pibsnet/paper_parameters.py`：冻结原基线执行器、严格限定论文参数补丁、顺序执行三组完整预算；不更改 Dojo 算法。`tests/integration/test_pibsnet_paper_parameters.py` 验证源码范围、损失计算与预算。
- `tools/verification/pibsnet/paper_trial_report.py`：完整预算及逐轮日志门禁、逐实例预测重算、Burgers数据与初权重核对、三组Markdown/HTML报告；支持等待已启动批次完成，失败不发布完成报告。

- `tests/fixtures/recipe_before_explicit/`：冻结旧模板、物理训练与后处理源码，保护旧复制目录及数值对照；不是新产品入口。
- `tests/integration/test_recipe_explicit_equivalence.py`：五例同输入、两轮权重、完整预测和旧检查点恢复逐值比较。

- `tests/integration/test_web_recipe_compatibility.py`：标准工作台局部编辑保留未编辑用户参数和字段列表，旧专用映射仍校验脚本。

- `tools/verification/pibsnet/reference_advection.py`：摘要锁定原 Advection 训练循环，同数据独立参考；`test_pibsnet_reference_protocol.py` 验证执行与配点协议。

- `tools/verification/pibsnet/reference_notebooks.py`：Burgers/梯形原数值定义与文献预算；`report.py`：重算完整对照、明确部分结果，`generalization.py` 排除非有限拟合点。

- `report.py --wait-for-pids`：本批已启动外部进程结束后汇总，最多等待24小时；只读进程状态，失败保留部分报告，不是调度器。

## 声明驱动原始处理

aero_cfd/configuration.py 和五例使用统一 resolve_rawprep 补缺，默认参数来自 contrib manifest，显式步骤和仓库外字段扩展保留。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

- `tools/verification/pibsnet/neumann_advection_trials.py`：迁移前六组独立全预算实验，冻结原生成器/初始化和严格数值补丁；`test_pibsnet_neumann_advection_trials.py` 检查标准物理导数、源码漂移及更新范围。
- `tools/verification/pibsnet/neumann_advection_report.py`：完整预算/逐轮日志门禁、数据与初权重逐值核验、全预测重算及独立六组Markdown/HTML/科学误差图报告。

## 原案例迁移

tools/verification/pibsnet/source_dojo.py执行独立生成、来源预检、实际recipe完整训练/独立post与同环境原函数逐值报告；test_pibsnet_source_alignment.py圈定迁移门禁。

- `tools/verification/pibsnet/source_migration_report.py`：重核两例完整迁移证据，生成实际Dojo精度报告、固定参数补充评价及场图。

- `docs/pibsnet/五案例精度对照报告.md`：2026-09-14五例Dojo实跑与论文精度汇总，标明当前迁移版、历史结果、统计口径和证据；不代表五例全部重新迁移。

- `docs/pibsnet/figures/accuracy-2026-09-14/`：五案例报告配图与重算metrics.json；固定首个测试实例，预测/参考共用色标，保留源数组摘要。

## 独立推理与结果消费

- `recipes/aero_cfd/infer.py` 与七个 `examples/aero_cfd/*/infer.py`：显式步骤，独立运行或 pipeline 中选择 infer；图案例走完整物理拼回，原五例保留锚点兼容路径。
历史说明（已被公共 pipeline/config 与 inputs 约定取代）：`recipes/aero_cfd/legacy-profile.json`：六套模板在独立推理迁移前的 36 份完整 Python 脚本及 AST 摘要，保留历史来源记录；当前宿主以 task-entry 的操作声明判断支持范围。
- 六份 configuration.py：支持 infer 参数及阶段顺序；config.yaml 仍写旧 `export_vtk`（未拆键时同时开关点云与网格化），源码已接受 `export_pointcloud` / `export_mesh`。`infer.py` 只调用 application 装配，不直接写 VTK。
- 六份 post.py：固定推理结果读取；旧归档 post-only 仍走原计算；新模板不再提供预测开关，数值对照通过独立验证工具进行。
- `recipes/aero_cfd/legacy-profile.json`：本切片前精确 AST 摘要和原任务 entry，保留当时来源；当前操作适配不以 AST 摘要做可用性判断。
- `examples/recipe_extensions/inference_fields/{fields.py,README.md}`：普通误差函数、保存读回及真实网格交付。
- `tests/integration/test_infer_{abilities,stage,extensions,compatibility}.py`：圈定验收；长期正文 `docs/PRD/recipes/aero_cfd/PRD.md`。

## 推理工作台选择与统计

`recipes/aero_cfd/inference-profile.json`：实施前六套原生infer脚本固定指纹；`infer.py`与五例同名脚本明确登记字段选择。原`legacy-profile.json`保持历史基线。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

- `examples/recipe_extensions/inference_metrics/{metrics.py,README.md}`：普通逐场评价函数与复制方法；`test_infer_extensions.py` 验证版本记录、结果读回及派生字段真实VTK。原生post缺少固定结果拒绝，历史算术对照由独立验证工具调用旧公开门面，新模板不再提供 post.legacy_predict 开关。

## 架构优化后的当前连接

- `examples/recipe_extensions/free_wiring/`：普通函数、自定义返回对象和局部连接，固定运行门面基线。
- `configuration.py`：案例只保留局部 STEP_PARAMETERS，通用转换委托 contrib/application/aero_cfd/configuration。
历史说明（已被公共 pipeline/config 与 inputs 约定取代）：`task-entry.json`：按需声明 inspect/evaluate/export 操作以及显式旧配置加载适配；平台不比较脚本目录指纹来判断可用性。历史 profile 文件只保留来源与旧验收说明。
- `tests/fixtures/public_api_baseline/` 与 `test_public_api_stability.py`：冻结用户源码和真实安装测试；基线不可随内部改动重算摘要。

## 项目共享数据切片

历史说明（已被公共 pipeline/config 与 inputs 约定取代）：aero_cfd/task-entry.json 与字段/采样扩展入口声明共享物理输出及阶段输入；五案例共享名称由用户明确填写，独立脚本不受托管路径影响。五例 trainprep.py 已与通用模板同一条 `trainprep.preparation` 链对齐；历史 physical 包装仅作已核验摘要迁移来源。

长期说明见对应包 PRD；当前证据见 `.context/mvp/task-shared-datasets-acceptance.md`。

平台配置交接补齐：`examples/aero_cfd/*/rawprep.py` 五例与主模板一样优先透传 formats，避免平台双格式选择仅输出 PT；不改冻结脚本。验收见 `mvp/platform-configuration-acceptance.md`。

## GenCP 可复制模板

`recipes/gencp/` 含 README/config/configuration/rawprep/trainprep/train/single/infer/post/pipeline；Python 显示独立场和条件连接。`examples/gencp/` 为六组配置与 source-config；`examples/recipe_extensions/gencp/` 的 custom/extension 展示条件替换和固定速度模长保存/读回，retrain 展示单独重训流体、保留其他场权重并重新生成。长期说明 [GenCP PRD](../../docs/PRD/recipes/gencp/PRD.md)，真实范围 [验收记录](../mvp/gencp-acceptance.md)。

## SafeDiffCon

- `recipes/safediffcon/{pipeline.py,config.yaml}`：Task自动发现并执行同一研究正文，不恢复task-entry或专用执行器；pipeline 与两个安装案例只导入选中阶段，单跑 trainprep 不提前加载 EMA 等训练专属依赖；公共inputs声明分片/权重/固定结果/求解资源。`tests/integration/test_safediffcon_{task,conventions}.py`覆盖阶段门禁、资源捕获及迁移。

- `recipes/safediffcon/{configuration,rawprep,trainprep,train,posttrain,infer,post,pipeline}.py`：显式六阶段研究流程，posttrain正文显示两轮；README导航至模块PRD。
- `examples/safediffcon/{burgers,tokamak}/`：各含configuration、pipeline及六阶段Python正文、README和config/quick.yaml；可在仓库外独立编辑执行或创建Task。quick保留原科学默认值，耗时须由原累计账本监督。
- `examples/recipe_extensions/safediffcon/variants.py`：小模型、严格安全引导、带单位/有效性的安全余量；仓库外复制实跑。
- `docs/PRD/recipes/safediffcon/PRD.md`：使用与扩展约定。
- `recipes/safediffcon/README.md`：继续预训练的总更新语义、阶段限时与最终评价预留；后训练采用完整轮次交接。

GenCP 当前只验收直接脚本运行；Task 入口补验缺少声明，尚不能提交训练/推理/post，见 [补验记录](../mvp/gencp-acceptance.md)。

## WDNO 可复制研究入口

- [现有集成补全方案](../../.cursor/plans/wdno-reproduction-and-agent-composition.plan.md)：基础迁移与公共Task适配已完成；本轮补分阶段实跑和独立Agent使用，论文完整复现仍待数据/协议及资源闭合。现有接口示例、后续职责和验收映射以新方案为准，不沿用早期未实现描述。

- `recipes/wdno/`：configuration、rawprep、trainprep、train、infer、post、pipeline及config.yaml；步骤由Python决定。
- `examples/wdno/burgers_base/`：原dim128/groups1基础配置；与模板同一完整脚本集合。
- `examples/recipe_extensions/wdno/variants.py`：网络层级、损失替换与带单位/轴的能量输出；无需框架登记。
- `examples/recipe_extensions/wdno/{config.yaml,pipeline.py,audit.py}`：完整变体参数、显式五阶段及预测后能量读回；覆盖到完整WDNO模板副本使用，扩展目录自身不是完整模板。
- `tests/integration/test_wdno_extensions.py`：完整配置及新增结果消费，拒绝缺字段/错误形状/非有限值/错误能量；真实复制与Task运行由test_wdno_task.py圈定。
- `docs/PRD/recipes/wdno/PRD.md`：长期使用边界；各README为复制/配置/恢复/扩展入口。
- 验收 `test_wdno_recipe.py`：实际wheel、仓库外完整流程、续训、独立post与三个组件替换。

WDNO当前直接/Task使用同一pipeline.py，配置采用inputs.<stage>和data_root，不新增task-entry.json；configuration.py提供显式旧配置转换。阶段通过TrainingRun发布目录、资产和指标；相关功能见WDNO PRD，真实双入口测试test_wdno_task.py，历史隔离安装保持。

## 公共配置迁移

当前官方模板共用 `inputs.<stage>.<name>`、`run_root`、`data_root`；Python决定阶段顺序，普通pipeline由直接入口和Task共用。取消task-entry，保留各领域与案例的实际步骤差异。`examples/recipe_extensions/gencp`消费固定准备/权重，在公开输出目录保存条件变体与单场替换结果。源码及安装验收见 `../mvp/recipe-task-conventions-acceptance.md`。

公共路径续接：外流 configuration 的 application_parameters 是纯配置入口，阶段正文显式传入 session 分配输出。field_mapping/sampling 扩展采用同一连接；原数值夹具通过显式准备阶段及固定旧预测入口测试，固定公开基线不改。相关用例及当前限制见 Recipe/Task 专项验收。

## WDNO最新公共约定补验（2026-09-17）

WDNO protocol-update补验：recipe、burgers_base example、extension分别复制与运行；README分别解释正常增加步数、中断恢复、复制品显式绑定和旧指标保护范围。test_wdno_documents实际执行文档配置例子。 当前结果以 `.context/mvp/wdno-acceptance.md` 为准。

## 研究变体任务入口

[研究导航](../tasks/research.md) 按任务链接当前模板、示例和测试。`examples/recipe_extensions/wdno/variant_training.py` 是局部训练函数覆盖文件；先复制完整recipes/wdno。`examples/recipe_extensions/model_block/variants.py` 是AB-UPT内部激活变体，README给出复制和components.model选择。普通原模板不因共享执行重构批量修改。

## GeoTransolver 双案例

`recipes/geotransolver/{darcy,bumper_beam}/` 每例九个完整文件：README/config/configuration/rawprep/trainprep/train/infer/post/pipeline。显式连接core能力与贡献语义；同样正文复制至 `examples/geotransolver/`。`examples/recipe_extensions/geotransolver/variants.py`替换损失、保存误差数组并独立消费。PRD见 `docs/PRD/recipes/geotransolver/PRD.md`；状态与真实证据见 `.context/mvp/geotransolver-acceptance.md`。

## PCNO 双场流程

`recipes/pcno/` 与 `examples/geothermal/pcno/`：完整五阶段脚本与配置。`examples/recipe_extensions/pcno/`：替换构造器、插入温降保存与下游消费。PRD见 `docs/PRD/recipes/pcno/PRD.md`。实际证据与范围见 `../mvp/pcno-acceptance.md`。


## GeoTransolver 外流扩展

`recipes/geotransolver/{shapenet_car,nasa_crm}/` 为两个完整九文件案例；安装资源位于 `examples/aero_cfd/{shapenet_car,nasa_crm}_geotransolver/`；`examples/recipe_extensions/geotransolver_aero/` 替换 L1 并保存、消费绝对误差。

行为见对应模块 PRD；实际证据与边界见 [外流验收](../mvp/geotransolver-aero-acceptance.md)。

## PCNO圆柱案例

`recipes/pcno_cylinder/`、`examples/pcno/double_cylinder/`：显式阶段正文；`examples/recipe_extensions/pcno_cylinder/`：普通构造器替换和速度模长消费。`examples/pcno/cylinder_flow/README.md`只记录准入阻断，不登记可训练案例。

功能正文见相应模块PRD；实际范围见[圆柱验收](../mvp/pcno-cylinder-acceptance.md)。

## Task 标签扩展示例（实施中）

`examples/recipe_extensions/task_labels/`：以 SafeDiffCon Burgers 为基案例，覆盖本地 application 及配置，在原控制描述上显式增加校准名称条件；由 case-manifest 声明并随 wheel 物化。`test_safediffcon_task_replay.py` 对基案例和外复制扩展实跑准备、训练、恢复、后训练、推理及固定 post，检查候选用途与输入捕获标签。结果见 Task 通用化验收记录，不声明科学精度。

## 通用研究extension

`examples/recipe_extensions/tail_batch`和`research_state`均物化`geotransolver.darcy`；前者替换有限轮次流，后者从训练来源留出验证并配对保存普通/EMA最佳权重。复用公共训练与固定infer/post，不扩大科学精度结论。清单摘要负责初选，README说明覆盖文件和交接。测试`test_research_extensions.py`。


## 经典网络三案例与重组扩展

- `recipes/classic_networks/{darcy,shapenet_volume,double_cylinder}/` 与 `examples/classic_networks/`：每例README/config/configuration/rawprep/trainprep/train/infer/post/pipeline九文件，Python显式五阶段、独立inputs、共享训练和固定结果；对应文件按case-manifest声明保持一致。
- `examples/recipe_extensions/network_composition/{resunet,unet_transformer,cnn_rnn}/`：分别登记可物化的覆盖集，各含配置、README、普通构造器和派生消费者。前两项基于Darcy；CNN-RNN基于double_cylinder，family=custom、sample_points=null。根目录四个Python文件是组件验证入口，覆盖副本同步检查防止漂移。
- `examples/case-manifest.json`：`classic_networks.*`三项standalone及`recipe_extensions.network_composition.*`三项extension；登记不表示完整训练验收完成。
- 功能正文：`docs/PRD/recipes/classic_networks/PRD.md`；来源与字段：contrib/application PRD第八章；计算与布局：core/abilities PRD第十一章。
- 非训练资源核查：`tests/integration/test_classic_network_examples.py`、`test_example_contract.py`、`test_example_discovery.py`；组合前后向：`test_network_recomposition.py`。`test_classic_network_pipeline.py`涉及实际训练，交主控最终串行执行。`tools/verification/classic_networks/installed_replay.py`在真实独立wheel中物化以上六项并由主控串行验证；`run_matrix.py`执行统一科学矩阵，全状态检查见`test_classic_matrix_validation.py`。真实训练、搬移、Task及实际wheel证据由主控在经典网络统一验收记录中逐项汇总。

本批阶段证据与未验范围见[经典网络统一验收](../mvp/classic-networks-acceptance.md)，该记录已按本批缩小验证范围完成。


## 算子与普通代理五案例

本批公开流程已实现；非训练组件与合成数据复制检查不能代替真实统一矩阵、安装和 Task 验收。行为正文为 `docs/PRD/recipes/operator_learning/PRD.md` 与 `docs/PRD/recipes/surrogate_modeling/PRD.md`。

- `recipes/operator_learning/{darcy,shapenet_volume,double_cylinder}/`：各含 README、config.yaml、configuration/rawprep/trainprep/train/infer/post/pipeline.py，显式五阶段。前两例支持 FNO/DeepONet，双圆柱为三帧历史通道 FNO；准备复用 classic 公开能力，不从原始样本空间随机分块冒充完整谱域。
- `recipes/surrogate_modeling/{nasa_crm,double_cylinder}/`：各含 README、config.yaml、configuration/trainprep/train/infer/post/pipeline.py，显式四阶段，无空 rawprep。NASA默认二次RSM，直接读 HDF5 属性；双圆柱默认 POD-RBF，消费 classic 准备。
- 代理 `train.py` 显式拟合、`save_state`、`record_bundle`；`configuration.py` 中 `fit_context` 交接准备及子清单摘要/字段/统计/组件；`infer.py` 先核上下文再普通重建，`post.py` 只读固定结果。
- `examples/recipe_extensions/operator_branch_replacement/{branch_replacement.py,config.yaml,user_outputs.py,README.md}`：DeepONet 分支构造替换及派生输出；`operator_physical_loss/{config.yaml,user_outputs.py,README.md}`：Darcy 非负解物理目标与固定派生结果；`pod_surrogate_replacement/{pod_mlp.py,config.yaml,README.md}`：普通拟合/重建替换为 POD-MLP，不把新状态类型加入框架注册表。
- `tests/integration/test_operator_surrogate_data.py`：两例代理仓库外复制完整流程、相容性失败和独立固定post；`test_operator_physical_loss.py`：约束与实际梯度；公共资源发现仍沿 `test_example_contract.py`、`test_example_discovery.py`。
- `tools/verification/operator_surrogates/serial_operators.py`：算子真实参考与Dojo对照；`serial_classical.py`：NASA及POD代理参考对照；`serial_matrix.py`：统一串行入口与组合累计预算；`installed_replay.py`：独立 wheel 中复制及Task复核。工具存在不是执行通过证据。
- `tools/verification/operator_surrogates/sources.json`：独立来源/版本/许可身份；实际证据由主控本批验收记录汇总，不复用经典网络上一批结论。每组合准备、参考、重试及恢复累计最多三小时。

外流三阶段明确连接：公共模板、NASA/ShapeNet AB-UPT 为锚点链；三个 Transolver 与两个 MeshGraphNet 为物理链（后者必需 topology）；GeoTransolver 保留物理链。三阶段脚本可不同，公共输入一致；`test_cross_model_recipe.py`、`test_infer_stage.py`、`test_recipe_explicit_equivalence.py` 覆盖连接与独立数值。
