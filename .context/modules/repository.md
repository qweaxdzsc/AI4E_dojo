# 全仓辅助目录

- [GeoTransolver 集成前评估](../mvp/geotransolver-assessment.md)：记录论文/源码身份、公开数据访问、实验配置差异与能力归属；第 6 节补充 20 GB 以下保险杠/Darcy 候选及文献对标限制，不表示模型已实现。
- [GeoTransolver 小数据实施计划](../../.cursor/plans/geotransolver-small-data-integration.plan.md)：原始数据归档及全量核验完成；计划涵盖参考修正、两个案例的科学协议、源码迁移与可复制研究验收，模型实现未启动。

- [共享训练执行与研究任务导航计划](../../.cursor/plans/training-execution-and-research-navigation.plan.md)：两点优化正在实施；共享执行、局部策略与研究路由已落盘，分层数值/复制/安装证据见专项验收，core/contrib已授权发布，实际页面补验发现Task恢复候选缺口，修正待追加发布授权。

- [.agents/skills/dojo-integrate-model/SKILL.md](../../.agents/skills/dojo-integrate-model/SKILL.md)：模型接入参考；能力优先抽取进 core 后逐步通用化；每次训练先估时，优先本机整体小于三小时的集成检查，保留用户明确范围与阶段证据。
- [.context/model-integration-learning.md](../model-integration-learning.md)：真实错误和流程候选的反馈日志，注明证据与边界，不自动成为规则。
- [docs/model-integration-goals.md](../../docs/model-integration-goals.md)：新模型接入的长期目标与关键检查；目标与交付、必须检查节点、可选参考三部分，无统一记录模板或个案进度。不替代架构正文或模块 PRD。

- `.cursor/plans/wdno-reproduction-and-agent-composition.plan.md`：2026-09-17 综合现有基础迁移和Task适配后的补全方案；当前成果、独立Agent使用、论文协议、正式训练与其余任务分别列明，沿用原180分钟累计账本。本次仅修订方案，不新增训练；六例和论文五系统缺项未闭合。
- `examples/aero_cfd/`：两模型、两数据源的五个配置案例；`examples/parametric_pde/`：五个独立生成案例；`examples/recipe_extensions/`：字段映射、采样、free_wiring。现行入口见 recipes 索引。
- `examples/task_lifecycle.py`：本地项目、new/fork、运行与版本交接。
- `tools/verification/`：AB-UPT/Transolver/跨模型/PDE 参考对照与平台实跑，研究计算预算由具体参数决定，不用于自动变更算法。
- `tools/verification/abupt_model_viewers.py`：用当前任务正式 AB-UPT 导出 TorchScript/ONNX/pt2，供本机 Netron 与 Model Explorer 对照，不接入工作台。
- `tools/verification/architecture_inventory.py`：按 Git 正式与未忽略源码生成目录、声明、PRD、测试及摘要索引；不替代人工功能核对。
- `tests/contract/`：依赖、轻量契约、模型组件和产物边界。
- `tests/integration/`：真实数据/算法/运行、Task、Web、Vis、文档和实际 wheel 交接。`test_public_api_stability.py` 与 `test_task_operation_provider.py` 覆盖固定用户代码和自由平台连接。`test_trainprep_consume.py` 核准备导入：新记录不含模型页采样预算，冻结声明不同也不挡 consume。
- `tests/fixtures/`：输入与数值参考；`public_api_baseline/sha256.json` 锁定公开用户源码，不随格式化或内部实现调整。
- `packages/ai4e-web/e2e/`：实际页面流程及固定响应交互测试；有真实数据开关的测试须分别记录缺环境和结果。
- `packages/ai4e-viz/backend/tests/` 与 `frontend/` 的测试/架构脚本：按包内索引定位，不能只跑根测试代替。
- `docs/PRD/`：模块产品真源；`docs/adr/`：技术决策；`docs/prototypes/`：UI 设计与历史原型；`docs/pibsnet/`：研究来源与精度材料；其它专题报告保留来源与范围。
- `AGENTS.md`、`.cursor/rules/`：开发阅读顺序、包边界、recipe、PRD 与圈定验收纪律。有 Web 消费链时，正式 8000/5173 冒烟与 force-include 重装是硬规则，隔离口与「待发布」不能当完成；正文只在根 `AGENTS.md`。
- `pyproject.toml`、各包 `pyproject.toml`、`uv.lock`：Python 构建与依赖；根 `dev` 含 `ai4e-viz[workbench]`，默认组含 `visualization`。Web 和 Vis frontend 各自 package 清单管理前端依赖。同步纪律见根 `AGENTS.md`「注意事项」。

全仓文件枚举与内容摘要见 `.context/mvp/architecture-alignment-results/inventory.json`；逐项功能状态与修改测试并集见本轮验收记录。

## 脚本物理场验证

- `tests/integration/test_post_visualization_*.py`：字段、切面、矢量、探针、真实渲染、文件和安装验收。
- `tests/integration/test_post_analysis_recipe.py`：只读固定结果与参数连接。
- `tests/integration/test_post_region_statistics.py`：区域统计和九项误差。
- `tests/integration/test_train_post_observation.py`：训练观察的两轮数值对照。

## 项目共享数据切片

tests/integration/test_task_shared_*.py、packages/ai4e-web/e2e/shared-datasets.spec.ts 与 tools/verification/task_shared_datasets.py 对应无服务共享、安装、平台与真实迁移验收。

长期说明见对应包 PRD；当前证据见 `.context/mvp/task-shared-datasets-acceptance.md`。

## GenCP 辅助入口

`tools/verification/gencp/` 独立参考、累计预算、实际产物对比；`tests/integration/test_gencp*.py` 覆盖能力/真实模型/交接。六例与扩展见 recipes 模块索引；当前结果与未决项见 [GenCP 验收](../mvp/gencp-acceptance.md)。

## SafeDiffCon 参考准入与复现

- `tools/verification/safediffcon/admission.py`：全量数值扫描、ZIP/展开分片冲突校验、原源码及当前补丁快照。
- `tools/verification/safediffcon/probe.py`：原 Burgers 数值回放/构造诊断、隔离 KSTAR 原控制回放及逐场误差。
- `tools/verification/safediffcon/reference.py`：先验摘要门禁、原 Burgers Trainer 历史诊断、进度与有限 checkpoint 保留；显式步数最多4000。
- `tools/verification/safediffcon/{reference_env,kstar}/pyproject.toml`：两个独立参考环境的依赖真源，不属于根 workspace 成员。
- `tools/verification/safediffcon/README.md`：参数、执行命令及限制导航。
- `tests/integration/test_safediffcon_{admission,reference}.py`：数据完整性、快照和参考启动门禁。
- `.cursor/plans/safediffcon-integration.plan.md`：沿原 A—E 结构执行的实施计划，复用已有集成，补科学口径和独立参考，训练使用每案例180分钟原累计账本余额。`.context/mvp/safediffcon-acceptance.md`：分别记录历史4000步基线、本轮续接与论文差异。

- `tests/integration/viz_interaction_browser.cjs`：三维交互八项修复的真实页面与视觉验收。

## SafeDiffCon 缩小对照与使用验收

- `tools/verification/safediffcon/public_conventions.py`：官方原数据8/4/2、六阶段Task与直接入口、2→3恢复、共享/fork及模型/派生字段/插入步骤的真实对照。
- `tools/verification/safediffcon/release_replay.py`：交付启动器经CLI新建三目录，历史固定结果post及worker解释器/安装摘要核对。
- `tests/integration/test_safediffcon_conventions.py`：可复制案例、旧键拒绝、路径迁移、公共/内部树隔离及求解器虚拟环境回归。

- `.cursor/plans/safediffcon-task-transparent-execution.plan.md`：2026-09-17公共约定适配实施与验收；完整案例、旧配置转换、隔离发布及真实双入口逐值一致。

- `tools/verification/safediffcon/task_acceptance.py`：实际安装Task包，经新建、提交、等待公开API完成真实控制训练、后训练、推理与固定结果后处理；捕获缺权重失败；历史入口缺项断言已移除。`tests/integration/test_safediffcon_task.py`：阶段选择和输入/输出捕获回归。

- `tools/verification/safediffcon/reference_stages.py`：冻结原校准类、加权训练步、适配步与引导的独立连接；共享只读数组/批次流及状态/响应/结果适配，不调用Dojo训练或推理编排。
- `tools/verification/safediffcon/budget.py`：已有账本的阶段限时与评价时间预留，拒绝以新账本继续。
- `tools/verification/safediffcon/continue_case.py`：核验冻结配置摘要，串行执行双侧预训练、独立参考阶段、Dojo流程及50样本验收。
- `tools/verification/safediffcon/report.py`：只读新旧验收及累计账本生成续接报告，拒绝诊断样本或未完成结果进入正式报告。

- `tools/verification/safediffcon/{compare,numerics,short_probe,acceptance,extensions,replay}.py`：原Trainer独立训练、原定义数值对照及设备计时；`reference.py`保留显式步数的历史诊断，拒绝200000步。
- `tools/verification/gencp/budget.py`：共用持久累计监督，每个控制案例一个账本。
- `tests/integration/test_safediffcon_{integration,packaging,budget}.py`：交接、恢复、上游定义、依赖、复制入口及限时。
- `.context/mvp/safediffcon-acceptance.md`：停止记录、缩小配置、数值与实际安装范围。

## WDNO 原仓库本地切片

- `tools/verification/wdno/protocol.py`：完整源码/补丁与数据身份冻结，代表轨迹门禁、预先固定验证/测试名单。
- `tools/verification/wdno/budget.py`：复用现有累计监督，原版与Dojo合计三小时上限和终止宽限。
- `tools/verification/wdno/reference.py`：隔离原环境，CPU分块小波、原Trainer、源检查点读回、限时、普通权重与原采样/指标；精确数据流恢复未实现。
- `tools/verification/wdno/replay.py`：独立进程使用原构造函数加载主检查点，重放固定首批16条测试预测。
- `tools/verification/wdno/report.py`：只读固定数组，独立核对原始真值/名单/MSE及累计账本生成报告，复算也计账。
- `tools/verification/wdno/README.md`：真实命令、依赖入口和运行目录导航。
- `tests/integration/test_wdno_{reference_protocol,budget,metrics}.py`：来源/名单漂移、泄漏、累计失败/重试及固定结果归约门禁。
- `.context/mvp/wdno-acceptance.md`：P0/P1历史与当前缩小迁移证据，论文目标未完成；长期数据准入说明在 `docs/PRD/ai4e-contrib/application/PRD.md` 共享数据集选择。

- `tests/integration/test_wdno_slice_acceptance.py`：通过 `DOJO_WDNO_SLICE_ROOT` 显式核验真实主切片、源码/权重身份、完整64/128样本及报告；缺产物不计通过。

## WDNO 当前迁移工具

- `tools/verification/wdno/vendor.py`：从既有冻结源码抽取数值定义，不修改作者仓库；按原方法AST验收。
- `tools/verification/wdno/migration.py`：调用复制recipe执行准备、训练、独立预测和固定对照，不复制数值循环。
- `tests/integration/test_wdno_migration.py`：原代码逐方法、数组、小波条件、损失/梯度/更新/采样、完整恢复和取消测试。
- `tests/integration/test_wdno_recipe.py`：wheel安装后的真实复制/变体/续训/固定结果。
- 实验、同环境参考和比较保存在 `/Users/zonghui/work/project_simulation/dojo_train/wdno/`；唯一当前验收入口仍是 `.context/mvp/wdno-acceptance.md`。

- `tests/integration/test_wdno_migration_acceptance.py`：显式真实两侧2000步、64/128预测和独立安装产物门槛；无真实产物不能记通过。

- `tools/verification/wdno/finish.py`：衔接本次已在执行的原版，之后在同一账本串行执行Dojo训练/采样/比较；不创建定时任务。

- `tools/verification/wdno/import_replay.py`：经实际recipe的source权重导入入口，独立重放验证/测试各首批16轨迹。
- `tools/verification/wdno/delivery.py`：只读固定比较结果、生成报告与科学图，并核对隔离安装来源/wheel摘要。

- `tools/verification/wdno/audit.py`：在同一账本独占锁下检查计算已关闭状态，硬限时执行最终测试并追加审计耗时；`test_wdno_audit.py`验证观察状态、超时和失败计账。

- `tools/verification/wdno/variant.py`：实际安装包、仓库外复制及原数据准备复用，运行网络/损失/派生场变体；原始结果和修正过的配置路径摘要保存在实验根variant。

- `tools/verification/wdno/task_replay.py`：相同原数据直接/Task从零2步、续到3步、固定预测/指标与插入能量步骤的实际对照。
- `tools/verification/wdno/legacy_replay.py`：历史2000步检查点在旧/新隔离入口各续1步及首批16条预测对照；不改历史文件。
- `tests/integration/test_wdno_task.py`：公共配置、旧键拒绝、显式迁移、输入冲突、双入口恢复与资产指标比较。
- `tools/verification/wdno/task_replay.py --staged`：新建原数据WDNO任务，分别提交处理、准备、训练、推理、后处理和续训，逐阶段直接/Task对照，并核对缺输入失败及固定结果不变。
- `tools/verification/wdno/agent_trials.py`：只读独立Agent实际过程和产物，核对完整更新、固定新增场、身份/单位/轴及独立post；不执行Agent代码，不以自报成功代替证据。
- `tests/integration/test_wdno_agent_acceptance.py`：拒绝仅声明成功，显式真实目录核验独立Agent输出；缺真实目录跳过不能算现场通过。
- `tools/verification/wdno/budget.py::continue_budget`：续接已有累计账本，错误路径拒绝；首次创建仅通过显式credit入口，已有实验不重置。

## Recipe / Task 离线迁移工具

- `tools/migration/recipe_conventions/configuration.py`：显式公共路径转换；不被运行时导入。
- `tools/migration/recipe_conventions/transaction.py`：原件、候选、摘要、日志与离线应用/回滚；候选复制中断同样可恢复。
- `tools/migration/recipe_conventions/cli.py`：用 `uv run --no-sync python -m tools.migration.recipe_conventions.cli` 调用 prepare/inspect/apply/rollback；apply/rollback 的 `--offline` 表示调用者已经停用对应目录，不会停止服务。先审阅候选目录并准备 bundle，正式目录仅按批准后的发布执行。
- `tests/integration/test_recipe_migration.py`：目录切换/部分复制故障与逐字节回滚；`test_task_transolver_recipe.py`：保留原领域正文的普通 Task/直接脚本数值与独立 post 对照。后者不代表旧准备通过平台新版门禁。

`tools/verification/recipe_task/migrations.py`：历史任务副本小样本准备/训练/恢复/推理/post实跑；保留领域流程、隔离钩子与完整训练状态对照，不应用正式任务。正式候选与安装回滚包位置见公共约定验收记录。

## WDNO最新公共约定补验（2026-09-17）

tools/verification/wdno/task_replay.py --staged --case recipe|example|extension分别核验真实来源；task_management.py --staged-root复用该次产物补复制和公开恢复。test_wdno_public_metrics.py为公共指标依赖，test_wdno_task_assets.py为资产/恢复，test_wdno_documents.py执行文档中的完整配置脚本。 当前结果以 `.context/mvp/wdno-acceptance.md` 为准。

## 研究导航和执行对照

- `.context/tasks/research.md`：任务阅读/修改/验收路由；`.agents/skills/dojo-research/SKILL.md` 仅作薄入口。
- `.context/history/development-updates-20260917.md`：保留根入口历史进度原文。
- `tools/verification/training_execution.py`：冻结原/新训练轨迹对照及所有配置入口盘点。
- `tools/verification/architecture_inventory.py`：新增声明签名、起止行与类方法定位。
- `tests/integration/test_training_{execution,strategy_extensions}.py`、`test_research_navigation.py`：执行语义、安装复制变体与导航。

## 案例资源与 Agent 文档

- `examples/case-manifest.json`：standalone 与 extension 的机器可读契约。
- `examples/`：仓库外可复制完整案例；每个 standalone 包含 README、配置、configuration、pipeline 及清单声明阶段。
- `DOJO_AGENT_GUIDE.md`：安装后研究者和 Agent 的公开使用指南，不依赖仓库内部导航。
- `.agents/skills/dojo-research/SKILL.md`：Agent 决策树唯一源文件，安装副本由 ai4e-task 构建生成。

## PCNO 参考工具与历史边界

- `tools/verification/pcno/{data_audit,reference,verify_first_step,economy}.py`：发布数据门禁、完整原训练透明适配、无观察首步对照与固定预测经济回放；README记录实际入口与科学边界。
- `tools/verification/pcno/{predict,finish_reference}.py`：双分支完整检查点推理、井级结果与指标；保留历史250轮最终态门禁，用户已停止长训练，当前不运行等待器。
- `tests/integration/test_pcno_{data,reference,reference_prediction,reference_artifacts}.py`：数据异常、AST适配、参考轮次恢复、最终态门禁、指标、真实准入产物；仅覆盖参考前置；Dojo短训与复制/安装另有当前证据。
- `.cursor/plans/pcno-small-data-integration.plan.md`：用户最新授权的先集成后短训计划，250轮已停止。
- `.context/mvp/pcno-acceptance.md`：当前代码集成、短训、科学修正、实际使用入口与剩余回归问题。

## GeoTransolver 对照与可复制验收

`tools/verification/geotransolver/`：`vendor_sources.py`按锁定源码提取；`reference.py`独立上游定义；`audit_preparation.py`独立原数据与统计；`compare.py`前向/梯度/更新；`benchmark.py`正式网络整网测速；`budget.py`累计计费与截止；`reference_train.py`独立参考短训；`write_recipes.py`仅作初次脚手架，最终双案例正文独立维护。参考差异见 `reference_patches.md`。相关用例为 `tests/integration/test_geotransolver_*.py`；不运行全仓代替圈定验收。

## PCNO 代码集成与短训验证

`tools/verification/pcno/{short_reference,compare_short,numerical_repair,diagnose_temperature}.py`：缩小预算参考、固定容差对照与原版数值问题定位；`test_pcno_*.py` 为数据、源码、训练、后处理与真实产物门禁。250轮旧任务已停止，当前状态见 `../mvp/pcno-acceptance.md`。

## Neumann 双组有效性实验

- `tools/verification/dojo_validity/rmhd/`：独立的 JOREK 协议，不改旧 Neumann 数学和历史结果。`protocol/model/preflight` 定义冻结起点和主控预实验；`materials/verification` 交付原始分片与网络、核查独立准备；`isolation/network/sessions` 限制全进程路径、公网代理和新CLI会话；`controller` 保证双最终锁定后才允许隐藏评价；`worker/evaluate/metrics` 分离无真值预测与可信FP64评分；`accounting/report` 保留未知项、独立排序和科学曲线；`worker_check` 仅主控验证已训baseline复放及恶意访问拒绝。
- `tests/integration/test_dojo_validity_rmhd.py`：六场等权、非法输出、完整预实验门禁、fake双组round00加五轮、冻结防篡改、公开代理与真实Seatbelt边界。
- [RMHD验收](../mvp/jorek-rmhd-validity-acceptance.md)：真实MPS预实验、隔离及正式执行证据。长期行为同下方参数化PDE PRD第二章维护。

- `tools/verification/dojo_validity/`：prepare/environment/baseline/metrics/ledger/isolation/runner 与 CLI；单组工作根和 experiment ID 分离，比较由主会话读取。
- `tests/integration/test_dojo_validity.py`：目录边界、FP64 指标、时间/token、失败续接、fake 五轮和正式阻塞门禁。
- [参数化 PDE PRD 第二章](../../docs/PRD/recipes/parametric_pde/PRD.md#二独立双组研究实验)：现行行为及未实现边界。
- [验收记录](../mvp/dojo-validity-acceptance.md)：科学起点、独立环境、命令级隔离及真实会话未验范围。

GeoTransolver后续验证入口：`train_pairs.py/continue_pairs.py/reference_train.py/evaluate_pairs.py`负责固定目标训练、已完成目标恢复及全量评价；`install.py/installed_replay.py/task_replay.py/asset_replay.py`负责真实安装和复制案例/worker一致性。`docs/agent-help/workflows/geotransolver.md`为用户研究导航；API与案例关联支持嵌套recipe来源。

- `tools/verification/dojo_validity/{cli,formal,activity}.py`：整进程隔离的新 CLI 会话、同会话五轮及只读候选重放、分阶段进程计时；`policies/` 保存上游 Seatbelt 平台策略及许可。`test_dojo_validity_cli.py` 覆盖实际权限、配置续接和请求用量读取。

- `tools/verification/dojo_validity/telemetry.py`：从正式 session 的原始工具调用与供应商 usage 重建编码、训练观察及混合请求分类；模型生成、工具、活动进程和执行器等待各按实际事件计时，失败尝试保留，未结束不封账。

- `tools/verification/dojo_validity/finish.py`：核对两组五轮与冻结内容后封账，按原始记录汇总失败成本，分别输出最终/第五轮/最佳精度、开发与训练成本、入口读取事件及源码组件引用；未结束 CLI 拒绝封账。

## 可选注意力组件验证

- `tests/fixtures/flare_plus_plus/upstream.py.txt`：PhysicsNeMo 锁定 commit 的原始源码，只提取独立类用于数值对照；对应许可随 core Notice 交付。
- `tests/integration/test_flare_attention.py`、`test_flare_attention_installation.py`：组件与实际 wheel 验收。
- `docs/agent-help/api/core/abilities/modeling/modules/flare_attention.md`：自动生成的公开 API；用户组合示例位于 `docs/agent-help/user-components/network.md`。
- `docs/reviews/trend/news/`：每周框架调研的日期报告、最新入口、候选/建议去重账本与来源证据；网络组件候选和全局架构建议分开。

- `docs/agent-help/capabilities/`：九类能力的输入输出、真实调用例子和边界；教程元数据生成 skill/GUIDE/帮助首页菜单。`tests/integration/test_agent_capabilities.py` 覆盖链接、符号、九例实跑、查询及离线导出；验收见 `.context/mvp/agent-capabilities-acceptance.md`。

- [JOREK RMHD 下一轮双组实验计划](../../.cursor/plans/jorek-rmhd-dojo-validity.plan.md)：原始数据核查、独立前处理、整轨迹隐藏测试、MPS U-Net 和延迟准入；正式运行进度见对应验收记录。


## GeoTransolver 外流扩展

`tools/verification/geotransolver/aero_reference.py` 锁定独立数值参考，`aero_acceptance.py` 完成测速、成对训练、完整预测对照，`aero_replay.py` 检查实际安装 Task、恢复和独立 post。新增 `tests/integration/test_geotransolver_aero_{inputs,reference,training,inference,recipe_task}.py`；预算、安装和文档用例沿用同模型专项文件。

行为见对应模块 PRD；实际证据与边界见 [外流验收](../mvp/geotransolver-aero-acceptance.md)。

## PCNO圆柱验证

`tools/verification/pcno/cylinder/`：官方来源恢复、标签准入、准备、测速、安装和清理验证；`tests/integration/test_pcno_cylinder_*.py`：相关用例。现行结果见`.context/mvp/pcno-cylinder-acceptance.md`。

功能正文见相应模块PRD；实际范围见[圆柱验收](../mvp/pcno-cylinder-acceptance.md)。
