推理工作台升级（2026-09-15，两道专项验收通过）：跨分片选择按检查点×分片串行，权重单次固定；步骤状态以完整批次为准。物理量分量评价且保留完整向量；有效实体mask、轻量指标、九项评价、样本等权统计与CSV/XLSX贯通。新post只读固定结果，旧post兼容与模板指纹保留。1672×941关键区域最大误差2px（门槛4px），1440/1920、2000样本及状态截图通过；真实CFD两权重三分片、只评价/取消/中断/部分失败重试、固定数组重算、下载读回和Trame经正式8000/5173入口验收。CPU小模型2/1轮仅验证工程交接，不代表生产精度。文件—测试映射、实跑证据、两个未启用的真实换模用例及GPU范围见 `.context/mvp/inference-ui-acceptance.md`。

平台数据集与数据准备页对齐（2026-09-15）：原始处理执行前填写 `dataset.processed_name`，页面预填来源标识不算已写入，检查/试跑/正式执行前才写入配置；正式成功后在工作区 `datasets/<name>/dataset.json` 登记名称、清单路径与摘要，张量仍留在产生它的任务数据目录；同名同摘要复用，同名不同内容拒绝，路径丢失或摘要变化标不可用；声明指纹不含 `rawprep.workers`，改并行线程可复用同名，真冲突返回中文说明。数据准备按平台名称选择并写入既有 `train.manifest`，同一清单只列一条且平台名称优先，不与任务历史重复可选；下拉按登记时间倒序，不自动勾最新；左栏复用产物树，右栏进度与叠加日志与原始处理同一套。原始处理不按 train/test 分片，只处理全部或指定样本；划分由数据准备完成。执行配置可改并行线程，写入 `rawprep.workers`，缺省 1、范围 1–64，每个线程处理不同样本。执行配置四个按钮点下后立刻带动同一条进度、日志状态和说明；操作说明只在开始时打一行普通日志，不钉在底部。执行日志默认只显示最近 500 行，更早行留在内存并向上滚动展开，自动滚动开关必须能停住或钉住最新行。PT/Zarr 可同时写出，旧 `rawprep.format` 单格式仍有效；VTKHDF 仅能力允许时显示，三个 ShapeNet 官方案例写 `rawprep.vtkhdf: true` 故新任务默认勾选，NASA 未接入不强开，已保存关闭不自动改写。归一化方法与统一空间分列，旧 `method: coordinate` 读成最小最大+统一空间且写出仍用原方法名。准备页可重划 train/test/eval：样本池为当前清单已处理的全部样本，默认显示原分片数量（缺的为 0），三者之和须等于总数，训练至少 1 个，test/eval 可为 0；抽取为保持原划分或随机，种子写入准备记录。官方 `partition.yaml` 原样保留，不重算张量；新划分是这次准备产物。无 `trainprep.split` 时保持物理清单原划分，只要求 train 非空，评估分片可空。圈定 `test_web_processed_datasets.py`（含倒序、缺时间回退、同清单去重）、`test_web_dataset_binding.py`、`test_web_rawprep.py`、`test_web_rawprep_handoff.py`、`test_web_stage_consistency.py`、`test_web_project_task.py`、`test_aero_cfd_documents.py`、`test_dataset_rawprep_descriptor.py`、`test_rawprep_manifest_configuration.py`、`test_rawprep_workers.py`、`test_recipe_configuration.py`、`test_train_recipe.py`、`test_trainprep_split.py`、`test_task_contracts.py` 与 `e2e/rawprep-consistency.spec.ts`、`e2e/execution-log.spec.ts`、`e2e/execution-monitor.spec.ts`、`e2e/stage-consistency.spec.ts`、`e2e/rawprep.spec.ts`。真实大数据交接仍按现有 `DOJO_*` 环境显式跑，缺数据 skip 不算平台资源验收通过。

文件树按需加载（2026-09-15）：原始数据、数据准备和后处理结果文件共用同一棵树表。首次只列当前一层，点开再取子项；列举不哈希、不登记，预览/下载/加入三维时才按受控路径登记。后处理指标目录与文件树分开，默认指标页不拉结果树。圈定 `test_web_stage_consistency.py`、`test_web_post_results.py`、`test_task_post_results.py`、`test_task_post_metrics.py`、`test_web_dataset_binding.py` 与 `e2e/stage-files.spec.ts`、`post-files.spec.ts`、`post-ui.spec.ts`、`post-workspace.spec.ts`、`rawprep-consistency.spec.ts`。

后处理三页签切片（2026-09-15）：默认指标、结果文件、三维物理场可视化。指标从固定预测/真值重算，core eval负责数值、post负责绑定，task管理独立评价运行，writer独占运行报告；评价数据和显式导出在任务data/post。文件树复用files公开组件，按层打开。三维会话按任务持有，Tab切换只隐藏，追加按固定来源去重，离开页面才回收；刷新仍需保存配置重开。轨道回写相机不重读网格、不整屏刷新；命名块按路径与修改时间缓存。连点切面只留一份未应用草稿，不嵌套、不重推整屏。对象树显隐只改已有 actor，不重建映射。不重跑推理、不新增任务版本。当前验收范围见 `.context/mvp/post-workspace-acceptance.md`。

工作台步骤色与清单交接（2026-09-15）：已完成且非当前步骤用任务成功绿，当前步骤保持蓝；案例模板清单占位不当成已绑定失效来源，正式产物可落在项目、任务目录或已登记数据根；有正式清单未选择时提示先选且主执行不可用，不自动勾最新；摘要未返回前不闪「未运行」；数据准备执行日志与原始处理同一套完整面板。圈定 `test_web_stage_consistency.py`、`test_web_project_task.py`、`test_task_contracts.py` 与 `e2e/stage-consistency.spec.ts`、`task-dataset-binding.spec.ts`。

独立推理实施完成（2026-09-14）：原子能力保留 `abilities/inference`，业务步骤位于 `applications/aero_cfd/infer`，外流新 recipe 显式串联 train → infer → post；新 post 只消费固定推理结果，旧 post 和36份已核验旧模板保持兼容，未知改动不自动放行。Task 固定checkpoint完整字节，同任务推理串行，输出各归子运行/数据目录，不创建任务版本。Web九步使用稳定slug，旧数字6→post、7→report保持。CORE38项、任务/服务/契约18项、旧profile11项、实际wheel和真实CPU 2份权重×2辆CFD车的下载/Trame交接通过；正式8000已更新，5173实际入口已核验。CPU小模型训练预算1样本、2/1轮，不代表生产精度；完整分项证据和跳过边界见 `.context/mvp/inference-acceptance.md`。以下历史验收保留当时范围。

模型目录与导出（2026-09-15）：模型页只列 AB-UPT 与 Transolver-3；换官方模型按当前数据集套对应 example 默认值，ShapeNet 的 Transolver-3 另选表面/体场。导出只存项目内同数据集配置预设，不含权重。生成结构由后台取最近相容准备或正式清单，现行 version=2 准备按训练同一条消费链跟踪，模型页不再勾这两项，不回写训练绑定。新建任务案例名为「模型 · 数据集」，含体场起步项。模型采样跟随当前模型自己的字段：AB-UPT 为点/锚点/查询，Transolver-3 为种子/步长/分块/随机流，步长只读；切片数量在主干参数。损失不可配时仍展示固定 MSE 与目标行。换模整段替换，无采样键才隐藏。模型设置不展示权重加载。圈定 `test_web_stage_consistency.py`、`test_algorithm_platform_contract.py::test_model_sampling_capability_follows_component`、`test_task_configuration.py`、`test_web_dataset_binding.py`、`test_web_project_task.py`、`test_web_recipe_compatibility.py` 与 `model-picker`/`stage-consistency`/`task-dataset-binding`/`model-inspection` 浏览器用例。真实换模仍用 `DOJO_MODEL_PICKER_REAL=1`，证据见 `.context/mvp/model-picker-acceptance.md`。

PI-BSNet 原案例迁移（2026-09-14，Neumann/Advection完整验收通过）：保留原参数导数、初始化与损失算术；实际Dojo分别5000轮/5000更新、2000轮/200000更新，平均相对L2为1.881%和10.427%。与同环境原函数全部权重、每轮损失和40个测试场逐值一致。75项圈定测试通过，含完整产物、恢复和真实wheel安装；梯形保留十实例，另外两例原算法切换范围待用户确认。入口tools/verification/pibsnet/source_dojo.py，报告工具source_migration_report.py，证据见.context/mvp/pibsnet-acceptance.md。

PI-BSNet Neumann/Advection 独立六组测试（2026-09-14，完整预算完成）：用户批准同时测试源码与物理导数解释，Neumann交叉整轮/逐实例更新；完整预算后再决定迁移，本轮不改Dojo算法。入口 `tools/verification/pibsnet/neumann_advection_trials.py`；圈定 `test_pibsnet_neumann_advection_trials.py`，进度与未决项见 `.context/mvp/pibsnet-acceptance.md`。

PI-BSNet梯形迁移（2026-09-14）：用户选定10实例、100×20×20、3000轮/PDE权重0.001，保留原Euler与参数样条数值行为。唯一梯形案例替换旧完整映射变体；旧数据/准备/检查点拒绝续用。Neumann/Advection本轮只审查，冲突须先确认。圈定 `test_pibsnet_trapezoid_alignment.py`、`test_pibsnet_trapezoid_acceptance.py`、生成/数值/训练/准备/安装/文档和post相关用例；正式结果见 `.context/mvp/pibsnet-acceptance.md`，不以单步对齐代替完整精度。

历史 Web / Server 首期切片（被后续并行扩展范围取代）：React/TypeScript/Vite/Ant Design 与 FastAPI 已按 ADR 0004 初始化。仅原始处理开放真实执行，服务通过 task 原 submit_run 使用既有 recipe；该历史切片未改 recipe/core/contrib；当前批准范围以以下并行实施段为准。task 增加配置与管理公开操作；创建模板允许未绑定输入，执行仍严格检查。viz 增加独立文件预览进程，与原有静态比较共存。实际验收与未交付边界见 `.context/mvp/web-rawprep-acceptance.md`，不能用工程构建替代端到端验收。

整合交互原型：`docs/prototypes/dojo-web-integrated.html`。沿用旧平台框架，内嵌第 2–7 步独立页面；项目页与第 1、8 步保留。单文件离线可打开，阶段配置按任务保留于当前会话，刷新重置；无真实计算或后端交接。验收：`tests/integration/web_integrated_browser.cjs`。

交叉模型实施（2026-09-10）：唯一 aero_cfd recipe 的五个独立 example 使用共享物理工作流；物理 PT、模型准备和完整预测分开交接。NASA 无体场，单表面 AB-UPT 配置不能含跨域块。本期五组正式单轮实跑、固定五样本全点评价及报告已交付；范围与工具限制见 `.context/mvp/cross-model-acceptance.md`。圈定新增用例：test_physical_dataset_contract.py、test_model_preparation_contract.py、test_cross_model_recipe.py、test_cross_model_training.py、test_cross_model_comparison.py、test_comparison_visualization.py、test_cross_model_acceptance.py；同时覆盖原数据、模型、训练与 post 相关回归。viz 只依赖 spec，比较数据独立于运行目录。

# AI4E_Dojo 开发入口

PI-BSNet 论文参数差异验证（2026-09-14）：独立工具只按用户确认修改 Burgers 正对流/MSE、梯形10/50实例及100×20×20控制点、0.001物理权重，不改Dojo算法。样条、初边界和数据算子未决差异必须披露，不将参数验证称为完整论文复现。圈定 `test_pibsnet_paper_parameters.py`、`test_pibsnet_documents.py`；完整训练进度与证据见 `.context/mvp/pibsnet-acceptance.md`。

PI-BSNet 接入（2026-09-11，实施中）：参数化 PDE 共享模板和五个独立数据生成入口已加入。方程为 contrib 普通 PyTorch 函数，模型自带样条导数，core 不反向导入 contrib。物理约束已进入本专项，历史“物理约束未进”仅描述旧验收范围。正式训练、原仓库对照和未完成项见 `.context/mvp/pibsnet-acceptance.md`；不得以短训替代五案例精度验收。本期不改 Web/Server。

当前整合平台验收（2026-09-10）：整合 HTML 为唯一布局基准。已接入项目管理与第 2–7 步、双表面数据集/双模型、PT/Zarr、统一 Min-Max、模型采样迁移、真实 TorchVista、有限 VTK 管线。四组合完整目标网络短训及真实产物交接通过；最终浏览器18项通过，主面板尺寸对照通过，不承诺全部状态逐像素一致或生产精度。报告和批量未开放。三组分别负责算法、可视化、平台，主 Agent 维护公共契约及集成验收；实际规模、失败修复与证据见 `.context/mvp/web-integrated-acceptance.md`。

可视化入口：浏览器 visualization 微领域统一复用于文件、后处理与比较；server 通过独立 viz 进程读文件/转换，viz 不导入模型或 core。检查与预览支持 VTK 家族、HDF5/H5、PT、NPY 与 Zarr。模型跟踪走 task 独立检查与 core 公开门面。相机联动默认关闭，不做跨网格自动插值。统计参数不可手填，色标显示范围与归一化统计分开。

首页入口验收纠正：阶段深链接和主面板尺寸测试不能证明首页可用。项目管理按整合原型提供卡片与进入项目，任务表明确进入工作台，侧栏整行可点且按路由高亮。新增 `packages/ai4e-web/e2e/home-entry.spec.ts` 从首页真实点击、创建任务、刷新/继续及归档失效验证；首页单独对照 1440/1920 两个视口。

案例驱动演进（2026-09-10）：优先接入新模型、数据集和科研案例，在真实研究中发现需求并打磨框架；不将框架比较中的优化建议自动视为实施任务或案例接入前置条件。能力比较与按案例触发的升级参考见 `docs/ai4s-framework-comparison.md`，文档验收入口为 `tests/integration/test_framework_comparison_document.py`。

历史五段配置切片（入口写法已由显式步骤设计取代）：recipe 的 configuration.py 负责分组、默认展开和参数提取；rawprep.py 调用库原 datapre 方法。run 接收 config_loader 并冻结用户配置，业务参数不得覆盖快照，数据来源写 reports.dataset。相关新增测试为 test_recipe_configuration.py、test_run_config_snapshot.py、test_verification_config.py；范围与结果见 `.context/mvp/config-regroup-acceptance.md`。

Transolver-3 双模型数值验收（2026-09-10）：共享 recipe 按组件选择锚点或逐点外流装配，NASA 身份为来源/分片/样本。真实 MPS 正式网络完整两轮、恢复、44 测试样本全部输出与参考逐元素对标通过，最大误差 0；参考恢复 RNG 设备交接修正已披露。旧公开配置兼容政策仍待确认，不宣称整体计划全部完成。范围、源码快照与证据见 `.context/mvp/transolver3-acceptance.md`。本切片相关用例：`uv run pytest tests/integration/test_aero_cfd_examples.py tests/integration/test_nasa_crm_data.py tests/integration/test_transolver_training.py tests/integration/test_transolver_post.py tests/integration/test_transolver_reference.py tests/integration/test_aero_cfd_documents.py`；新增选优恢复与通用归一化须联验既有 checkpoint、优化、post 与比较协议用例。

原始数据处理细节原型：`docs/prototypes/dojo-rawprep-detail.html`，文件浏览与字段输出计划分离，仅 UI 示意。相关检查：`uv run pytest tests/integration/test_web_design_documents.py` 与 `tests/integration/rawprep_detail_browser.cjs`（本地 Playwright）。

原型 v3 按用户 UI 图调整，并映射 aero_cfd application/recipe：原始处理三栏、模板配置、执行范围和产物交接。仅 HTML 演示，仍保留已确认八步；不接后端、不执行真实计算。

Task 本地切片（2026-09-09）：六类功能目录、项目、new/fork 正式版本、模板、shared/私有资产、本地执行及比较；运行归 tasks/<task_id>。实现与验收入口见 `.context/mvp/task-acceptance.md`。new/fork 才新增版本；编辑和 run 不新增版本，无草稿/发布/冻结流程。task 不使用 DDD。源码树与安装副本可能不同，验收须核对加载位置。


框架正确性修正（2026-09-09）：设备为参数，沿用同一套训练与后处理；输入错误分项定位，样本/批次身份随异常保留。post-progress.json 记录评估、预测、网格各自状态及部分交付，失败不冒充完整成功。训练/后处理自动记录比较协议；缺证据的历史产物只可做契约核验。相关新增用例为 tests/integration/test_framework_correctness.py 与 test_comparison_protocol.py；与既有后处理、训练恢复及日志用例一起验收。实跑与边界见 .context/mvp/framework-correctness-acceptance.md。


MPS 个人实验验收（2026-09-09）：复制 recipe 修改种子、学习率、权重衰减和锚点预算，889 样本、正式网络两轮、100 测试预测与两辆完整网格已全流程跑通。修复网格查询设备交接、MPS 随机状态保存/隔离及过时的旋转 CPU 回退。Noether MPS 重复训练自身不精确复现；严格数值一致尚未通过，不能沿用 CPU 对齐结论。详见 `.context/mvp/abupt-end-to-end-acceptance.md`。本切片相关测试：`uv run pytest tests/integration/test_train_checkpoint.py tests/integration/test_post_reference.py tests/integration/test_post_mesh.py tests/integration/test_post_inference.py tests/integration/test_model_evaluation.py tests/integration/test_abupt_recipe.py tests/integration/test_reference_arithmetic.py`；MPS 用例须在能访问真实 Apple GPU 的环境执行，skip 不算硬件验收。


可点击线框原型：`docs/prototypes/dojo-web-wireframe.html`（左侧仅两个一级入口，项目六 Tab 位于主视区），仅示意项目六 Tab、八步工作台及比较／报告跳转；使用内存样例数据，无后端、无真实计算，刷新重置，不代表前端技术栈已选定。

Web 平台设计草案（2026-09-09）：产品入口为项目管理与八步任务工作台；项目内含任务管理、版本树、版本比较、项目报告、文件管理和批量运行。产品稿见 `docs/PRD/ai4e-web/src/PRD.md`，Web / Server 架构 v2 见唯一架构文档第 19 节。一个任务对应一个版本，分别展示版本、来源、基线版本；运行尝试可多次，只有 new/fork 创建正式版本；工作目录可编辑，运行保留快照但不增加版本。task 保留研究管理与执行职责。上述为历史设计定位；当前栈与实现状态见 ADR 0004、0005 及整合平台验收。DOE、报告与批量仍不可据设计声明交付。

当前端到端验收（2026-09-09）：默认 recipe 为 rawprep → trainprep → train → post。冻结变换组合、点场整理与分块查询归 abilities；aero_cfd application 负责业务绑定。独立 post 默认从配置种子沿 global 流采样，隔离锚点/网格两路；兼容张量包、点云与表面原始身份已对齐。实跑规模、数值证据及范围见 `.context/mvp/abupt-end-to-end-acceptance.md`。



当前训练对齐切片：用户入口为 rawprep → trainprep → train。准备交付冻结数据摘要、归一化记录和采样/拼批声明；训练消费前校验。模型结构版本 3 修正 RMSNorm、绝对位置编码器、联合投影与初始化顺序，版本 2 权重不支持直接续训。完整官方等价性必须以 `.context/mvp/abupt-reference-acceptance.md` 的实际证据为准，不能用旧小模型验收替代。

多域 AB-UPT 使用结构版本 3：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。


当前实施状态（2026-09-08）：已交付五类业务、归一化与采样、正式 AB-UPT、训练评估与轮次恢复、可选归一化物化及 VTKHDF/PT 关联、监督比较方法、训练闭环剩余对齐，以及 post 锚点推理（只恢复权重、test 集评估、逐样本保存、可选锚点点云）与完整网格回贴。训练设备默认按 CUDA/MPS/CPU 选择，找不到加速器时警告后回退 CPU；MPS 默认两轮复制案例已实测，范围与结果见 `.context/mvp/framework-correctness-acceptance.md`。物理约束未进。验收范围、逐项用例与执行结果以 `.context/mvp/abupt-acceptance.md` 为准；云图、报告及生产规模训练不在本期验收范围。

AI4E_Dojo 是 AI4S/Engineering AI 研究框架。仓库已建立 uv workspace；另已交付普通 recipes、contrib 数据集适配、Dataset 按需执行、产物 manifest 和能力日志。除数据源下载、路径读取、VTK 家族/NPY 统一 VTK 内存适配、字段提取、有效点 mask、几何派生（点到最近顶点 / 点到网格表面 / 表面法向）、重合点标记与点数校验、具名场张量落盘与按对照表读回、外流 pre 单样本/批量编排与统计量、外流 train 选定 AB-UPT / 打开官方分片 / 按对照表读盘，并支持显式准备和正式训练、最小 Stage/Pipeline、run 开车与写入，以及 aero_cfd 案例前处理与训练准备入口、监督比较方法（均方误差、平均绝对误差、Huber、相对 L2）外，其余目录存在不代表功能已经实现。物理约束未进。

## 工作入口与阅读顺序

每次工作按以下顺序阅读，当前用户指令优先级最高：

1. `AGENTS.md`
2. `.context/index.md`：每次工作的仓库结构与功能检索入口
3. 与任务对应的 `.context/modules/*.md` 或 `.context/mvp/*.md`
4. 修改 recipe、案例配置或扩展入口时读取 `.cursor/rules/ai4e-recipe-authoring.mdc`。按目标 package 读取对应规则：算法包读 `ai4e-algorithm-architecture.mdc`，task 包读 `ai4e-task-architecture.mdc`，server 包读 `ai4e-backend-ddd.mdc`，Web 包读 `ai4e-web-architecture.mdc`
5. 写或改 PRD 时先读 `docs/PRD/README.md` 与 `.cursor/rules/prd-writing.mdc`；PRD 按 `docs/PRD/{包}/{模块}/PRD.md` 落文件，包与模块对齐 `packages/` 一级目录
6. 目标源码、调用方、产物契约、文档与测试

PRD 是模块功能的长期文档，须记录现行行为、设计原因、使用约定和迁移影响；按六节结构归入对应功能点，不另建平行功能说明。README/.context 负责导航，既有独立入口可保留跳转。

`docs/AI4E_Dojo_ARCHITECTURE (1).md` 是业务与代码架构设计文档，不是每次工作的必读文件。需要理解设计原因、整体数据流、Stage/Artifact/RunManifest/ExecutionBackend 或进行架构决策时，由 `.context/index.md` 按需进入。架构设计只在该文档维护；`.context` 负责索引当前仓库结构与文件用途，不复制第二份架构正文。

## 索引维护纪律

- `.context/index.md` 必须反映整个仓库的代码目录结构，并指向各模块上下文。
- `.context/modules/*.md` 必须列出对应模块的目录、文档路径及其含义，帮助 LLM 先定位再读取。
- 新增、删除、移动目录或文档，或改变文件职责时，必须同步对应模块索引和 `.context/index.md`。

## 修改与验收纪律

每次改动只针对本仓库，并遵守下面三条。未同时做到，不得视为完成。

1. **上下游整条链一起看。** 改一处必须想清谁提供输入、谁消费输出、中间交接什么、失败时谁感知。至少核对：调用方、被调用方、契约/配置、缓存或产物、文档读者。不得只改局部、默认上下游自己适应。
2. **同一改动必须带齐这些更新。** `AGENTS.md`（入口、边界或验收纪律受影响时）、`.context`、相关 PRD（按 `docs/PRD/README.md` 的模块目录补；没有则补上受影响模块的 PRD，不得只改代码）、以及测试用例。目录或职责变了还要按上面的索引维护纪律改模块索引。
3. **用相关测试验收，不跑全仓冒充验收。** 先圈定本次改动影响到的用例并跑通，才算验收。不要用全量测试代替「先圈相关用例」。尚无对应测试则先补再跑。用 `uv run pytest <相关路径>`。未跑通相关用例不得验收。

**重点：改配置树必须走完整交接链，不得只改案例 YAML 和眼前几个装配文件。** 漏核下游会引入静默误判，不是“改完眼前再补”。至少核到这三组：

1. **加载与默认注入。** 配置加载、相对路径、从其他目录启动、`--set`、独立脚本和程序调用入口都要读新树；所有模型的默认采样/归一化必须写进新位置，禁止再注入旧顶层键。旧键拒绝须覆盖配置文件、`--set`、脚本和程序入口，并测新旧键同时存在。内部装配键（如 rawprep 的 `pre:`）与已废弃的案例阶段名不是一回事，禁止误拒绝。
2. **对照与选择器。** 对照工具与 task 比较选择器必须指向新路径。已声明的比较条件取不到值就是不可比，禁止填 `None` 或空对象后仍判相同。缺键禁止 `get(..., {})` 静默回到默认种子或预算。对照脚本若加载案例模块、调用阶段函数，必须一起改，不能只改阶段字符串。
3. **用户配置 ≠ 冻结产物。** 用户配置可以拒绝旧格式；历史准备产物能否消费、要不要重新准备、旧检查点能否续训，必须分开定义。冻结声明按业务语义提取，不得把收组后的整段配置直接当作准备一致性、续训或数值比较条件。已有历史证据文件保留原样。验收必须覆盖准备消费、轮次恢复、独立 post、归一化物化、task 资产与指标比较、其他模型工作流，以及实际 wheel 安装后的复制 recipe；不能只用几个 recipe 脚本测试代替。

本切片相关验收入口：

```bash
uv run pytest tests/integration/test_train_resolved_config.py tests/integration/test_train_test_repeat.py tests/integration/test_train_code_snapshot.py tests/integration/test_train_interrupt.py tests/integration/test_train_diagnostics.py tests/integration/test_train_optim_align.py tests/integration/test_train_entry_init.py tests/integration/test_train_shapenet_contract.py tests/integration/test_train_reference_stats.py
uv run pytest tests/integration/test_train_loop.py tests/integration/test_train_checkpoint.py tests/integration/test_train_recipe.py tests/integration/test_constraint_losses.py tests/integration/test_train_online_loss.py tests/integration/test_model_evaluation.py
uv run pytest tests/integration/test_post_inference.py tests/integration/test_abupt_recipe.py tests/integration/test_post_mesh.py
uv run pytest tests/integration/test_train_formal_two_epoch.py
```

## 技术基线

- Python 基线为 3.12；根 `pyproject.toml` 管理 uv workspace，成员为 `ai4e-spec`、`ai4e-core`、`ai4e-contrib`、`ai4e-task`。
- `packages/` 下每个包只保留一层物理目录；根 `pyproject.toml` 必须把连字符目录显式映射为下划线 Python 导入名（如 `packages/ai4e-core/` → `ai4e_core`），不得重新创建内部同名目录。
- 所有 Python、pytest、ruff、mypy 和 Sphinx 命令必须使用 `uv run`。
- `ai4e-web` 使用 ADR 0004 已确定的 React/TypeScript/Vite/Ant Design；依赖只进入 package.json 与 package-lock.json。
- 依赖只允许进入各生态的唯一清单；本阶段不得创建临时依赖文件。

## 包依赖边界

```text
ai4e-spec
   ↑
ai4e-core
   ↑           ↑          ↑
recipes      task        viz
               ↑
            server → web
```

- `ai4e-spec` 不导入其他 ai4e 包，也不依赖 torch/numpy。
- `ai4e-core` 只依赖 spec；core 不导入 viz。
- `ai4e-contrib` 依赖 spec + core。
- `ai4e-task` 依赖 spec + core，不导入 recipes。
- `ai4e-viz` 只依赖 spec，通过稳定 run artifact 读取结果，不认识模型和 Trainer。
- `ai4e-server` 依赖 spec + task；`ai4e-web` 只消费 server API 或稳定 artifact schema。
- `applications/base` 只提供通用编排机制；领域 application 按 rawprep/trainprep/model/train/infer/post 组织标准业务装配，但不得感知具体 modeling/constraint 内部实现。

## 三类代码结构原则

- **算法包**：`ai4e-spec`、`ai4e-core`、`ai4e-contrib`，以及 `ai4e-viz` 现有算法库目录。严格遵循 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 给出的 base、abilities、applications、Stage 和 Artifact 划分，以高内聚、低耦合约束实现；跳出 DDD 的 `api/domain/application/infrastructure` 目录表象。
- **任务包**：`ai4e-task` 按 cli/projects/tasks/versions/templates/storage 六类功能组织，不套用 DDD；Python API 与 CLI 共用实现。
- **后端包**：`ai4e-server`。围绕 Project、Experiment、Run、Artifact、Job、Execution 等业务生命周期采用轻量 DDD；先划分限界上下文，再按真实需要在上下文内部区分 domain/application/ports/adapters，不建立全局空壳层。
- **前端包**：`ai4e-web`。按数据接入、recipe 配置、run、对比、报告等用户任务形成微领域；每个微领域自治，并通过稳定 server API 或 Artifact schema 交互，不镜像后端目录。
- 三类原则不能互相套用：算法不包装成贫血领域对象，后端不实现数值算法，前端不承担训练与物理计算。

## 分层与修改纪律

- 原子能力按 data、transform、geometry、sampling、modeling、constraint、training、inference、eval、postproc、report 分层。
- `data` 按六个阶段组织：`source` 来源读取与分片名单、`extract` 字段与记录、`validate` 对齐和输出门禁、`filter` 标记与筛选、`save` 张量读写与恢复、`stats` 数组流统计。不得恢复 clean/offline/online 的状态式划分。
- 同组字段声明来源、point/cell、实体数和原 ID 序列，无 mask 也必须校验行身份与数量；筛选统一更新组内字段与身份，点 mask 不适用于 CellData。编码器不猜组名后缀，`cell.pt` 是 recipe 的可选业务打包约定。
- `geometry` 保留完整 VTK，点到面与法向共用全二维面门禁，不抽取体外壳；按原 point ID 回贴法向，孤立点为零且有效性标记为 False。几何不依赖物理场，`pre.geometry.enabled` 显式选择，未启用不计算。`nearest_vertex` 只出最近距离，`volume_normals` 独立出体积法向。fields 可显式为空。
- 外流 rawprep 保留 read/derive/select/save/stats 单样本能力，由 dataset 模块提供按需装配。recipe 使用 datapre(cfg) 显式登记步骤，run 内封装样本循环，application 不反向导入 run。
- 样本发现与统计样本/字段/缺失策略属于 application；通用样本循环、首错/继续和汇总属于 `run/execute`。Stage/Pipeline 沿用现有顺序调用，不另建 DAG。任何样本失败都不能汇总为完整成功，首错停止保留之前提交结果且跳过统计。
- dry-run 与提交共用输出预检，针对实际样本目标检查覆盖；张量使用同级临时目录、旧目录备份、提升与失败恢复，遗留路径显式处理。重算统计只用本次成功结果的实际路径，逐数组流累计；dry-run 不扫描旧张量或写统计量。
- `run/writer` 独占运行配置、日志与摘要写入；runner 不解释 pre 路径或业务字段，业务通过 reports 交付摘要。预处理张量写数据目录。外流 train 已有的分片读取与表面零距离处理保留，正式模型构建、监督更新、评估和轮次恢复由 model/train 装配。
- 外流 recipe 按 rawprep/trainprep/model/train/infer/post 展开；infer 业务组合原子推理、评价与数据输出，post 消费固定结果。旧 post API 仅保留兼容调用语义，不能使新 post 静默重跑模型。recipe 不写算法或训练循环，PI-BSNet 等其他案例不因本次外流拆分自动迁移。
- `run/writer` 是 run 目录唯一写入方；运行记录与数据目录独立配置；运行配置/日志由 writer 写入，数据产物由 save 写入，禁止写入包源码目录。
- 用户组件默认通过全限定 import 路径接入，不要求继承 core 基类。
- 修改功能时按「修改与验收纪律」同步 `AGENTS.md`、`.context`、PRD 与测试；新增、删除或移动文件时同步模块索引。
- Python 源码必须更新中文模块说明与公开 API Docstring；复杂数据语义、单位、拓扑和性能取舍解释原因。

## AB-UPT MVP1 边界

- `user_project/` 是历史验证资产，只作迁移参考，不得成为新包的公共依赖。
- AB-UPT 完整模型托管于 contrib；recipe 注入构造器，core 不导入 contrib。通用组件按验证后的等价实现提炼。模型迁入与小规模训练已验收。
- `packages/` 下的新代码不得导入 `noether`；如需参考行为，应重建最小契约并用测试证明等价。
- MVP1 目标与验收以 `.context/mvp/abupt-mvp1.md` 为准。

## 验证纪律

单次改动的验收以「修改与验收纪律」第 3 条为准：只跑相关用例。下面是仓库门禁，不是每次改动都要跑完全部：

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/
uv run sphinx-build -b html docs/source docs/_build/html
```

不得用目录存在、import 成功或构建成功替代对应功能测试。发现并核实错误时按 `.cursor/rules/error-log.mdc` 记录；没有错误时不得制造日志。

## 可复制 Recipe 与 Dataset

Recipe 是研究者可阅读、可编辑、可扩展的流程正文。打开阶段脚本应能看清处理顺序、参数和交接；Python 决定顺序，YAML 提供参数。Application 提供业务步骤，ability 实现计算，run 承担通用执行与运行记录。

不以脚本行数少作为目标，不允许新模板退化成整段 workflow 转发。自定义能力通过公开接口接入，新增输出必须完成保存、读回和下游消费。

修改 recipe 时读取专项规则，并以“仓库外复制、接入用户能力、实跑交付下游”为验收项。五例允许明确的局部步骤差异；旧整段入口作为共用公开步骤的兼容包装。历史配置、准备、检查点和证据分别判断，不批量改写。

2026-09-11 显式流程切片已完成圈定验收：五例 CPU 小规模两轮、完整预测与旧检查点恢复逐值对齐；两个用户能力目录、真实 wheel 外部复制及相关平台回归通过。实际规模与验收状态见 `.context/mvp/recipe-explicit-acceptance.md`；下方历史切片记录只代表各自当时范围，不能作为新扩展已交付证据。

- `recipes/` 是普通模板集合，不是 Python 安装包；外流模板交付 README/config/configuration/rawprep/trainprep/train/infer/post/pipeline，不建 init/main、缓存或组件占位。
- `ai4e-contrib/application/datasets` 提供可安装的 manifest/adapter，recipe 可 import 或复制修改；core 不依赖 contrib。
- `${...}` 插值展开后按配置文件解析路径；数据根、各分片、normalize 路径和运行根独立可配。
- 原始 manifest 描述来源；产物 manifest 描述本次成功交付。统计默认仅用本次完整训练分片。覆盖开始撤下旧完整清单；部分失败不得继续发布完整清单。
- recipe 阶段日志使用 `[阶段/能力/事件]`（如 `[datapre/数据集/选择结果]`）；运行入口设置并恢复阶段上下文，原子能力不感知 recipe，后台心跳显式继承阶段与样本身份。阶段边界使用 `[datapre/阶段/开始]`；整体运行及无阶段的独立调用不强加阶段前缀。writer 统一写入并按事件元信息筛选控制台摘要。
- inputs 只保存一份最终生效 config.yaml；日志包含能力/工作流开始结束与长任务进度，不倾倒配置、数组和整批结果。
- 归一化正反变换、冻结记录与可选物化已实现；prepare/fit 对物理输入必须显式 execute=true。正式网络小规模拟合与恢复已验收，复制案例短训与恢复已验收，生产规模训练不在本期范围。训练设备默认 `auto`，无加速器时警告后继续用 CPU，MPS 的邻域检索和复数旋转显式经 CPU。
- PRD 增加 `docs/PRD/recipes/{案例}/PRD.md` 作为非安装模板集合的对应位置。

## Task 本地切片验收

相关用例：`uv run pytest tests/integration/test_task_management.py tests/integration/test_task_assets.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py tests/integration/test_task_recipe.py tests/integration/test_task_documents.py tests/integration/test_task_installation.py`。安装用例构建实际 wheel；运行和既有 core 的相关回归范围见 `.context/mvp/task-acceptance.md`。不可用全仓测试代替这些接口、资产和真实案例验收。

服务器操作手册：`docs/aero-cfd-server-runbook.md` 记录五案例 CUDA/50 epoch 配置、物理清单迁移、独立阶段与报告格式；这是待执行操作说明，不代表服务器验收。报告不再写死单轮，预算以源运行产物为准；相关验证为 `test_comparison_visualization.py`。

五例50轮实跑进度见 `.context/mvp/cross-model-50-acceptance.md`；测试 `test_cross_model_acceptance.py` 支持 `DOJO_CROSS_MODEL_EPOCHS` 与 `DOJO_CROSS_MODEL_DEVICE` 显式预算，默认仍为历史1轮MPS。执行中不得宣称报告完成。

## Web / Server 圈定验收

```bash
uv run pytest tests/integration/test_web_project_task.py tests/integration/test_web_rawprep.py tests/integration/test_web_rawprep_handoff.py tests/integration/test_web_research_records.py tests/integration/test_web_runtime.py tests/integration/test_web_architecture.py tests/integration/test_viz_file_preview.py tests/integration/test_task_configuration.py tests/integration/test_task_management.py tests/integration/test_task_execution.py tests/integration/test_web_design_documents.py
npm run --prefix packages/ai4e-web build
npm run --prefix packages/ai4e-web check:architecture
npm run --prefix packages/ai4e-web test:e2e
```

真实样本缺失导致 skip 时不得声称真实链路完成。当前安装采用单层 wheel 映射，源码变更后核对安装副本或重装受影响包。

本机平台已完成一份真实 ShapeNet-Car 样本的页面执行、PT/VTKHDF 文件预览和原数据准备读取；48 项圈定后端用例与三条浏览器流程通过。仅声明上述范围，尚未开放批量及其他工作台执行。详见 web-rawprep-acceptance.md。

## 本机训练与缓存存放约定（2026-09-10）

用户指定后续训练相关文件统一放在 `/Users/zonghui/work/project_simulation/`；Dojo 使用其下 `dojo_train/`。新建实验时显式将运行、检查点、预测、比较报告及本次产生的数据/准备产物写入 `dojo_train/<实验名>/`，相关工具缓存也放在 dojo_train 下，不再新建到 `/private/tmp`。使用明确的 run_root、数据输出与缓存路径实现，不将本机绝对路径硬编码进可移植框架默认值。已有输入数据与历史冻结记录不批量改写；旧 tmp 位置的兼容符号链接仅用于历史引用，新配置直接使用真实目录。


整合平台圈定验证：主 Agent 使用 `uv run pytest tests/integration/test_web_integrated_pipeline.py tests/integration/test_web_platform_operations.py tests/integration/test_web_project_task.py tests/integration/test_web_research_records.py tests/integration/test_web_runtime.py tests/integration/test_web_architecture.py tests/integration/test_web_design_documents.py tests/integration/test_task_configuration.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py`。文件交接另圈 `test_web_rawprep.py`、`test_web_recipe_compatibility.py`、`test_web_rawprep_handoff.py`、`test_viz_file_preview.py`、`test_viz_pipeline.py`、`test_viz_extended.py`。真实四组合、模型大小、样本预算与浏览器证据统一见整合验收记录；不以少样本正式网络短训声明生产规模精度。

任务创建与数据绑定修正：新建明确选择案例，原始处理「修改绑定」选择 contrib 公开数据集及本机完整副本，一次接上处理方式与受控地址；配置编辑不新增版本，未绑定或失效来源不可执行。历史缺 `components.dataset` 的外流任务按 NASA 文件键或模板默认目录识别，绑定接口不再因缺声明返回 400。相关验收使用 `uv run --no-sync pytest tests/integration/test_web_dataset_binding.py tests/integration/test_web_binding_real.py tests/integration/test_web_stage_consistency.py tests/integration/test_web_project_task.py tests/integration/test_task_configuration.py tests/integration/test_web_rawprep.py tests/integration/test_web_rawprep_handoff.py`（真实绑定显式指定 `DOJO_BINDING_REAL_ROOT`），以及 `packages/ai4e-web/e2e/task-dataset-binding.spec.ts`、`rawprep-consistency.spec.ts`、`home-entry.spec.ts`、`project-task.spec.ts`、`navigation.spec.ts`。单层force-include包修改后刷新可编辑安装，再核验安装源码；不要让普通同步复用旧构建替代当前源码。

PI-BSNet 文献参数验证：参考配置不得额外加入原目标没有的初值/周期罚项；完整 PDE 网格包含初边界。论文优先、源码补缺，不调参掩盖精度失败。新增圈定 `test_pibsnet_physical_reference.py`、`test_pibsnet_reference_protocol.py`，当前 Neumann 精度失败及正式运行见 `.context/mvp/pibsnet-acceptance.md`。

平台一致性切片（2026-09-14，圈定验收通过）：任务表与工作台共用真实阶段摘要；检查、试跑、执行和结构生成先保存修订，固定绑定保存在原配置。阶段文件限定清单/运行，PT/Zarr互斥、VTKHDF独立附加；导航不推断完成。数据准备字段按模型 `data_specs` 与物理清单下拉匹配并校验张量形状。圈定 `test_web_stage_consistency.py`、`test_web_platform_operations.py`、`test_web_binding_real.py`、`test_web_rawprep_handoff.py` 与受影响项目、配置、运行、资产、架构及文档测试；浏览器圈定 `stage-consistency`、`stage-files`、`rawprep-consistency`、`prototype-consistency`、`execution-monitor` 及首页/任务绑定回归。当前证据见 `.context/mvp/web-integrated-results/ui-consistency/`，夹具不算真实数值交接。


## 独立可视化应用迁移（2026-09-14）

`ai4e-viz` 包含原 AI4E_Vis 十三模块、JSX 前端、完整规则/索引/文档/资源及原 Dojo 库。包内应用读 `packages/ai4e-viz/AGENTS.md` 和根 `ai4e-vis-*` 规则入口：后端轻量 DDD、前端微领域；原 inspect/preview 等库仍按算法能力组织。Vis 只依赖 spec，不导入 task/core/server。

任务公开 `visualization_storage` 提供受控任务目录，server 经独立 Vis 进程交付上下文。配置保存在 `tasks/<task>/visualizations/<id>/asset.json + revisions/<revision>/spec.json`，图片/视频/CSV 仅显式导出到 exports。保存不复制原数据、不自动截图、不改任务版本、研究配置或 runs。项目上下文逐请求传递，不能用进程环境变量切换目标任务。宿主iframe只在拿到会话地址后渲染；重开先关闭再创建，满员先回收无心跳空闲会话。

圈定验收入口：`tests/integration/test_viz_host_bindings.py` 与 `packages/ai4e-viz/backend/tests/modules/test_vis_asset_storage.py`、`test_phys_filters.py`、`test_phys_session.py`、`test_vis_exports.py`。完整迁入、统一配置资产链路、三维功能分别报告；当前事实见包内 `docs/migration/dojo-integration.md`，不可用目录或构建替代真实浏览器/视频/数值验收。

Vis迁移验收（2026-09-14）：原393份治理/源码/资源按清单迁入，具体范围见 `.context/mvp/vis-migration-acceptance.md`。新可视化保存仅写任务visualizations配置修订，显式导出独立提交。独立应用按包内轻量DDD/前端微领域规则治理；旧viz库仍按算法边界。Linux阴影和完整科研页面新链路不得用本机构建或组件验收替代。

## 数据集声明驱动原始处理（2026-09-14）

历史任务兼容：页面映射比较代码语法与已核验版本；格式/注释不阻断，已知旧配置加载入口消费完整有效默认值。逻辑/入口变化继续拒绝并列出文件。圈定 `test_web_recipe_compatibility.py`、`test_web_rawprep.py`、`test_web_architecture.py`，旧任务脚本与创建快照不自动替换。

ShapeNet-Car/NASA 的 manifest 提供默认处理参数、字段与绑定槽位；Web 展示生效配置并按样本执行，文件浏览不再决定新入口的执行范围。描述和校验经 task 独立检查，server 不导入数据集；旧文件请求、容器和历史产物分别兼容。新输出为逐场张量且清单记录实际布局，缺失字段不能冒充可训练。验收见 `.context/mvp/manifest-rawprep-acceptance.md`；圈定新 descriptor/configuration/catalog/selection 用例及真实 `test_manifest_rawprep_real.py`、`manifest-rawprep-real.spec.ts`，同时回归 recipe、扩展、安装、配置、绑定、物理读盘与恢复。真实数据用例不接受 skip 作为通过。

三维对象工作台（2026-09-14）：Trame 基于用户确认布局重构；导入自动创建纯色基础显示，着色是对象属性，不预建压力/温度节点。计算参数应用后生效，显示设置即时更新；物理配置版本 2 的旧版适配不重写历史修订。流线可选线段/球体/平面/命名面起点，应用后显示不可拖的种子；切面与剖切选中时用可视平面三向拖动和轴对齐，拖动只预览、应用才切开。验收入口为 `.context/mvp/phys-workbench-acceptance.md`、`test_phys_objects.py`、`viz_objects_browser.cjs`，不以旧界面浏览器记录替代新工作台验收。 真实 ShapeNet/NASA 表面结果补充验收与裁剪面/Probe/CSV 修复见同一记录；新增入口 `viz_real_results_browser.cjs`，不以静态表面结果声明生产体场时序或并发性能。

三维参考图样式校正：圈定 `tests/integration/viz_visual_browser.cjs` 的真实四尺寸截图，并联验 `viz_objects_browser.cjs`、`viz_real_results_browser.cjs`；视觉与物理计算分别验收，记录见 `.context/mvp/phys-workbench-acceptance.md`。

Web服务响应错误回归：`packages/ai4e-web/e2e/http-errors.spec.ts` 圈定空代理响应、网络断开、业务detail、无效成功正文与204；不得用空数组掩盖服务失败。恢复原平台后另以真实项目列表验证。

平台默认三维入口修正（2026-09-14）：网格文件预览和后处理直接打开 Trame，已有旧场景显式兼容。任务上下文自动带入，未选结果允许空工作台内导入；关闭预览和平台路由退出释放所属会话，迟到响应也须回收。网格预览弹窗默认加高，可放大到视口全屏；放大后对象树、属性和三维窗口须露出，属性框可滚动。后处理三维页保持 820px 独立滚动窗口，嵌套 iframe 贴合该窗口，不能只剩工具条和白底，页面可向下滚动。原始处理字段提取按每个 `.pt` 一张卡片，对话框只勾选一个物理量或坐标；再点执行立刻清掉完成态和进度条，日志同页叠加。圈定 `packages/ai4e-web/e2e/trame-entry.spec.ts`、`preview-dialog.spec.ts`、`rawprep.spec.ts`、`rawprep-consistency.spec.ts`、`manifest-rawprep-real.spec.ts`、`http-errors.spec.ts` 与 `tests/integration/test_viz_host_bindings.py`；真实项目/任务环境变量缺失导致 skip 不算实际入口验收。证据见 `.context/mvp/phys-workbench-acceptance.md`。
