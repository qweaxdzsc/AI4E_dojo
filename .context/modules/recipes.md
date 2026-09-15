`tests/integration/test_pibsnet_trapezoid_acceptance.py`：完整预算报告门槛及真实双方权重/历史/十个场验收；实跑目录通过DOJO_TRAPEZOID_ACCEPTANCE_ROOT指定。

`tools/verification/pibsnet/trapezoid_environment.py`：同一Dojo环境执行原数值函数的完整预算验证，分离运行环境与框架迁移差异。

梯形迁移：`tools/verification/pibsnet/trapezoid_dojo.py` 独立生成/源数组与初权重预检、实际recipe完整训练/独立post及报告；`examples/parametric_pde/diffusion_trapezoid/` 为10实例。`docs/pibsnet/Neumann与Advection输入核查.md` 为两例只读核查；`test_pibsnet_trapezoid_alignment.py` 为逐层/恢复验收。

# recipes 模板索引

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
- `recipes/aero_cfd/config.yaml`：实验选择、路径插值与统计策略；新默认 VTKHDF 开、归一化副本开，`rawprep.formats` 可同时写 PT/Zarr，`rawprep.workers` 控制并行样本线程。
- `recipes/aero_cfd/pipeline.py`：显式顺序串接 rawprep/trainprep/train/post。
- `docs/PRD/recipes/aero_cfd/PRD.md`：模板行为与迁移。
- `tests/integration/test_dataset_recipe.py`：复制脚本、路径、统计、失败与日志验收。
- `tests/integration/test_aero_cfd_documents.py`：五例脚本交接，以及 ShapeNet 默认打开 / NASA 关闭 VTKHDF。
- `tests/recipe_assets.py`、`tests/legacy_pre.py`、`tests/fixtures/legacy_pre.yaml`：旧行为回归夹具，不是产品入口。

不包含 init/main、缓存、训练占位和用户组件目录；共享 manifest/adapter 在 contrib。

## 本次实施定位（2026-09-08）

- `aero_cfd/train.py`：probe/prepare/fit 单一会话入口。
- `aero_cfd/post.py`：显式登记恢复、预测、物理输出、评价、保存和网格步骤。
- `aero_cfd/config.yaml`：公开采样预算、模型参数、损失权重、设备自动选择、Lion/调度/累积/`test_repeat`/快照与 VTKHDF 开关；post 含评估/保存/点云/完整网格回贴开关与 `sample_indices`。

## 多域模型变更

`recipes/aero_cfd/post.py`：贡献组件注入与唯一 session.launch；pipeline 登记 rawprep/trainprep/train/post。`config.yaml`：data_specs、trainprep、域采样、supervision，以及 post 评估/保存/点云/完整网格回贴开关。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## 三阶段 recipe 与参考验收

- `recipes/aero_cfd/rawprep.py`：数据前处理显式业务流水线。
- `recipes/aero_cfd/trainprep.py`：独立准备、全分片校验与 preparation.json 引用；可选 `trainprep.split` 重划 train/test/eval，官方名单不改。
- `recipes/aero_cfd/train.py`：消费准备引用、构建模型、目标、优化、评估与执行。
- `tests/integration/test_recipe_three_stage.py`：独立入口、完整流水线、干跑和数据冲突。
- `.context/mvp/abupt-reference-acceptance.md`：逐阶段官方对照及未完成门槛。

端到端样板默认包含 post；config 不预填未来准备引用或检查点。独立运行时可通过公开覆盖指向已有产物，连续运行自动交接。见 `.context/mvp/abupt-end-to-end-acceptance.md` 与 `tests/integration/test_post_reference.py`。

README 新增按 post-progress.json 检查部分交付、已有检查点仅补网格及自动比较协议说明；配置不增加未来输出输入项。

## Task 接入

- `aero_cfd/task-entry.json`：显式输入输出绑定、恢复键与标量比较定义；模板不导入 task。
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

examples/aero_cfd/ 下固定五个独立配置，阶段脚本基于 recipes/aero_cfd，物理流程以对应公开步骤显式编写；新增 nasa_crm_abupt、shapenet_car_transolver3_surface、shapenet_car_transolver3_volume。三个 ShapeNet 案例 `rawprep.vtkhdf` 默认打开；NASA 案例不写该键，沿用清单未接入。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `docs/aero-cfd-server-runbook.md`：复制五例、CUDA预检、50轮配置、分阶段执行与报告交付操作手册。

- `.context/mvp/cross-model-50-acceptance.md`：沿用五例网络与共享入口的50轮实验；验收测试支持显式epoch/设备预算，历史默认不变。

## Web 复用

平台只复制现有 aero_cfd，经 task 的原 submit_run 覆盖原始处理阶段和固定样本。不修改模板或生成替代脚本。真实接入与输出交接见 `.context/mvp/web-rawprep-acceptance.md`。

- `aero_cfd/configuration.py`：规范模型采样写入 model.sampling；旧 trainprep.sampling 单键兼容，双键拒绝。字段容器和 PT/Zarr 格式保留于 rawprep。

## 本机实验存储位置

按 AGENTS.md 的本机约定，新训练输出使用 `/Users/zonghui/work/project_simulation/dojo_train/<实验名>/`，显式配置运行与预测路径。50轮运行已迁至 `dojo_train/dojo-cross-model-50`；七个用户指定的历史工具缓存/暂存目录已同名迁入 dojo_train，迁移记录为该目录下 `cache-relocation-20260910.json`。旧tmp位置仅保留兼容链接，未变更可复制模板的跨机器默认路径。
- `aero_cfd/task-entry.json`：当前比较量采样选择器使用 `model/sampling`，旧运行仍读取其代码快照中的历史 entry，不迁写冻结资产。

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

- `recipes/aero_cfd/infer.py` 与五个 `examples/aero_cfd/*/infer.py`：显式步骤，独立运行或 pipeline 中选择 infer。
- `recipes/aero_cfd/legacy-profile.json`：六套模板在独立推理迁移前的 36 份完整 Python 脚本及 AST 摘要，供宿主精确识别已知历史模板；不代表任意历史修改均可自动执行。
- 六份 configuration.py：支持 infer 参数及阶段顺序；config.yaml 提供独立推理设置并保留旧 post 参数兼容。
- 六份 post.py：固定推理结果读取；旧归档 post-only 仍走原计算；新模板必须显式 post.legacy_predict=true 才允许历史数值对照。
- `recipes/aero_cfd/legacy-profile.json`：本切片前精确 AST 摘要和原任务 entry，供宿主定向兼容，不放行任意旧逻辑。
- `examples/recipe_extensions/inference_fields/{fields.py,README.md}`：普通误差函数、保存读回及真实网格交付。
- `tests/integration/test_infer_{abilities,stage,extensions,compatibility}.py`：圈定验收；长期正文 `docs/PRD/recipes/aero_cfd/PRD.md`。

## 推理工作台选择与统计

`recipes/aero_cfd/inference-profile.json`：实施前六套原生infer脚本固定指纹；`infer.py`与五例同名脚本明确登记字段选择。原`legacy-profile.json`保持历史基线。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

- `examples/recipe_extensions/inference_metrics/{metrics.py,README.md}`：普通逐场评价函数与复制方法；`test_infer_extensions.py` 验证版本记录、结果读回及派生字段真实VTK。原生post缺少固定结果拒绝，`post.legacy_predict=true`仅显式历史算术对照。
