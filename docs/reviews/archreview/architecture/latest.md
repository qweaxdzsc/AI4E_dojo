# Dojo 框架分层架构复审 · 2026-09-21

复审性质：当前工作树静态架构审查；仅报告与提案，无实现授权。北京时间内容采样：2026-09-21 04:03:23 +08:00。

- Git HEAD：`477c47bc4cba83fd1e903800034d7d58286ee6d8`。
- 工作区内容 SHA-256：`7d4c5ea0e8470c0bd72589ada98e5e4883ca6119f90ded25c1a05aee98720b0c`。
- 纳入 3,488 个 Git 跟踪或未忽略的未跟踪路径；437 个 porcelain 状态条目。工作树已有改动不归因于本次复审。
- 方法：排序后的路径、文件类型、字节摘要与大小；符号链接记录链接目标；缺失路径保留标记。排除复审目录避免报告自引用；未忽略之外的运行环境、安装副本不在身份内。
- [内容清单与静态调用统计](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-21-identity.json)。该身份是内容采样，不是工作区备份。

## 全局判断

分层方向仍值得保留：科学计算由 core/contrib 与领域 application 解释，recipe 表达研究顺序，Task 管管理事实，Server 管平台用例，Web 展示稳定接口，Vis 管显示。研究入口和平台开放范围应各自声明，不能要求所有研究依次经过 Recipe→Task→Web 才算有效。

当前问题集中在**领域可选操作已经具备声明入口，但部分管理便捷接口仍把外流科学格式和显示装配内置为默认值**。这是未来扩展平台和 Task 比较能力的结构性成本，不能用“已经隔离到子进程”当成职责已分离。本轮没有证据证明当前五个 Web 案例因此失效，也不把未开放领域的 Web 支持当作既有产品承诺。

### 八层事实所有权与实际交接

1. **spec** 拥有资产、指标、请求及来源的持久化形状，不拥有科学算法或通用张量协议。[指标索引](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-spec/artifacts/indexes.py:26)要求 field/unit/split/statistic/data_identity 与资产引用；字段可承载领域自定语义。
2. **core** 拥有中立计算、领域步骤、顺序执行和运行记录。[writer](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-core/run/writer.py:129)写资产和指标索引；Task 不应另造一份科学运行摘要。core 不拥有项目数据库、官方模型目录或页面状态。
3. **contrib/application** 拥有模型、数据集与领域配置连接，以及不可中立化的科学解释。[外流操作](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-contrib/application/aero_cfd/operations.py:9)在边界转换配置，再调用 core 领域能力；不应让 Task 重做这次解释。中立能力仍优先归 core。
4. **recipe** 拥有步骤顺序和局部连接；普通函数返回值无需 Artifact 化。[控制流程交接](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-contrib/application/pde_control/safediffcon/handoff.py:23)已用公开 writer 登记自己的 split/phase，说明保留领域差异与共享管理语言可以同时成立。
5. **Task** 应拥有项目、版本、配置修订、运行、输入、资产、权重引用、结果、失败/恢复事实。[operations](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/operations.py:11)已从 components.application 解析操作，[inspections](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inspections.py:46)在独立进程执行。实际仍有下述三类职责泄漏；因此不能写成“已完全模型无关”。
6. **Server** 拥有平台开放目录、受控路径、业务校验及显示适配。[推理用例](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/inference/application.py:11)调用 ai4e_task 公共门面；[官方目录](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/capabilities/model_cases.py)属于 Server，不能误归 Task。当前平台的 CFD 门禁本身不是架构错误。
7. **Web** 拥有草稿和交互，不拥有运行终态或科学指标定义。[结果 API](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-web/src/modules/inference/api.ts:97)透传 comparison/statistics/records，文件使用受控引用；本次抽查链路没有在浏览器重新计算指标。未全量核验所有页面。
8. **Vis** 拥有场景、渲染、显示配置和导出；物理结果消费固定资产。[Vis 启动](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/infrastructure/vis_client.py:26)为独立服务进程。但“整个 Vis 只接固定资产”并非源码全貌：结构跟踪目前接收活网络和输入，桥接代码位于 Task worker，详见 R3；不能隐去这个例外。

包清单中 spec 无依赖；core→spec；contrib→core/spec；task→core/spec；server→task/spec；viz→spec（此处只计 ai4e 包）。包清单方向正确不等于所有运行时调用都符合所有权。

### 进程、固定资产与失败归属

当前主链为 Web HTTP→Server→Task 门面；Task 捕获配置、代码和引用后启动 recipe worker/检查进程/推理协调进程；科学执行写固定结果和运行摘要；Task 记录收据与终态；Server 登记受控来源后交给 Web/独立 Vis。文件来源修订、显示会话状态、科学运行状态是三类不同事实，不应合并。

[运行 worker](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/worker.py:60)从 summary 的 failed/research_status 判断失败，[批次结果](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inference_results.py:174)禁止将未完整成功批次开放为完整比较。这两处应保留，不因提炼 provider 接口而减弱。

### 跨领域管理语言与比较

共享输入身份、版本、修订、运行、资产、检查点、固定结果、指标及失败恢复是可行的，已有实现并非空白。[compare_runs](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/versions/compare.py:87)核验固定指标资产内容、运行终态及完整 semantics 相等；缺失或不同口径分别给 missing/incompatible，不把空值当相同。SafeDiffCon 的 J/R 指标可保留自己的定义、约束和数据身份，不必变成 CFD 场指标。

要保留“可共同登记和比较管理事实”与“科学指标可以直接比较”的区别。不同领域并不天然可进行数值优劣排序。当前通用 compare_runs 的谨慎边界值得保留；专用推理结果比较仍被外流默认路由约束，见 R1。

### Agent 路由与设计真源

[architecture 短入口](/Users/zonghui/work/new_code_project/AI4E_Dojo/.context/tasks/architecture.md)负责选层和跳转，[唯一架构正文](</Users/zonghui/work/new_code_project/AI4E_Dojo/docs/AI4E_Dojo_ARCHITECTURE (1).md>)负责设计原因；PRD 负责长期功能，模块索引负责源码/调用方/测试定位。短入口含职责摘要和调用图，但未形成独立长篇设计正文；应保留这一级概览。

新增帮助中心、案例清单以及 [resources.py](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/templates/resources.py:109)的检索/符号门面已能从任务进入说明和源码，纯静态资源读取不加载模型。上轮“建立任务导航”不能原样重复；当前应评估真实定位效率。新增数据集和平台接入的短路由仍可改进，但本轮不占核心建议名额。不把帮助中心的 API 用途说明认作第二份架构正文。

## 与上次报告的变化

上次正式报告为 [2026-09-18-global.md](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-18-global.md)，HEAD 为 e48bde91ad11fd60d8fb95897a53397827947e8c。本次 HEAD 已前进，且存在大量未提交内容。上轮只存工作区状态摘要，没有逐文件内容清单，故无法用摘要精确证明某处代码“新增于上次之后”；下面区分新观察与新代码。

- **A：强制逐级晋级的表述失效。** 依据上轮会后澄清与当前架构正文，采用研究/Task/Web 可选入口支持与科学复现质量分别说明。保留产品开放边界，不再提出强制晋级流程。
- **B：最小管理交接继续开放，落到 R1/R2。** 上轮已识别 component/model 同批判断与固定资产槽位；本轮重新确认。新增洞见是：provider 选择并未贯穿元信息→结果比较→视图→导出，不能只修一个 model 字段就宣布边界完成。
- **C：导航已有部分实现，效果待验。** 帮助中心、可复制案例清单及静态检索门面在当前源码存在；没有重跑安装或盲定位，不记为完整解决。
- **新增 R3：检查 worker 的 Task→Vis 活对象桥接。** 是本轮新识别的跨层所有权问题，不声称本周刚引入。
- 当前入口已扩展地热、GeoTransolver/PCNO 等研究案例；这支持继续检验跨领域管理交接，不能据此宣布其 Web 能力或论文精度已交付。

## R1 · 高：让领域 provider 覆盖完整科学操作链

**源码与调用链证据。** [checkpoints.py:17](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/checkpoints.py:17)默认 provider 是 ai4e_core.applications.aero_cfd.infer.inspect_artifacts。AST 静态统计共 8 个 inspect_inference 调用点，仅 inputs 显式传入任务 provider；其余 metadata、compare、result_views、export、metric_catalog、result_fields 和 devices 共 7 处使用默认值。devices 可视为通用资源查询，另外 6 处承载科学格式/展示口径。

实际链：Web results→Server results→Task inference_results→默认外流适配器→外流 compare_results/result_views；导出复走同样路线。[外流分派](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-core/applications/aero_cfd/infer/artifact_operations.py:12)确实解释这些操作。同时 [inference.py:75](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inference.py:75)直接比较 preparation.digest 与 contract.component/model。

**系统性痛点。** 新领域即便提供 components.application.infer，仍不能只靠声明替换整条科学消费链；后半段回到 CFD。管理层知道模型合同键，后续会继续诱发按领域补分支。

**根因。** 事实：显式 provider 只用于一个调用点，同批兼容判断仍在 Task。推断：早期外流便捷接口比后加的可选操作声明更早固化，迁移只覆盖了输入检查；本轮没有查作者意图，不能将此推断当提交历史。

**最小架构动作与职责。** 复用现有 operation_target 和独立进程，不另建协议总线。由领域 provider 返回候选描述、科学可兼容结论及带作用域的不透明执行身份；Task 只核验引用完整性、修订、权限与身份等值。metadata/compare/result_views/export/result_fields/metric_catalog 从任务或固定批次所捕获的声明解析；无声明明确 operation_unavailable，不默选 CFD。devices 单独作为资源能力，不要求科学 provider 实现。批次需保留所用 provider 的来源/版本引用，避免历史结果随当前任务编辑改换解释器。

涉及 Task checkpoints/inference/inference_results/inference_exports/post_results/post_metrics、contrib 的领域 operations、core 的现有科学适配器；Server/Web 保持稳定 API 与显示字段，不引入科学分支。spec 只在真实跨进程返回确需版本化时增加最小记录。相关长期边界位于 Task tasks PRD 第一、三章及 Server modules PRD。

**科学语义保持与迁移。** 外流兼容检查原样委托给外流 provider；不减少结构、准备或内容校验。不要求其他领域复用外流准备 schema。既有外流任务的兼容适配应显式、可识别且单独验证；历史请求/结果字节不批量改写，旧公开函数参数变化须登记迁移。

**验收设计。** 在现有推理候选/批次/结果/导出用例外，增加一个不含 component/model 的 provider，覆盖完整链及缺操作失败；领域决定相容与不相容两条路径。编辑当前 provider 后读取旧批次仍使用原来源；取消、部分交付与幂等保持。真实 wheel 外复制后验证管理进程不加载模型。若实施影响 Web，最后仍须获当次授权后做正式 8000/5173 冒烟。

**可量化收益与未验证效果。** 基线为 6 个科学操作调用点绕过声明、1 个 Task 同批判断读取模型键；目标均归零，并用第二领域证明无需增加 Task 科学分支。暂不承诺接入耗时或性能百分比；尚未实施或执行上述验收。

## R2 · 中：分离资产事实目录与领域输入候选映射

**源码与调用链证据。** [writer.record_asset](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-core/run/writer.py:129)已经登记 name/stage/kind/semantics/dependencies。Task [list_stage_artifacts](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/artifacts.py:41)却固定将 checkpoint 投影到 inputs.train.resume / inputs.infer.checkpoint，将 preparation 投影到 inputs.train.preparation / inputs.infer.preparation，将 dataset 投影到 inputs.trainprep.dataset。[Server stage-inputs](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/application.py:777)随后直接消费 binding。

[SafeDiffCon inputs](/Users/zonghui/work/new_code_project/AI4E_Dojo/recipes/safediffcon/config.yaml:53)实际有 preparation_train/cal/test 与 posttrain.checkpoint；[handoff](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-contrib/application/pde_control/safediffcon/handoff.py:23)已保留 split/phase。相反 [read_entry](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/templates/materialize.py:27)的输入捕获能按 inputs.* 遍历，所以不能据候选投影问题断言 Task 直接执行失败。

**系统性痛点。** 通用资产索引已有领域语义，管理候选投影却丢失消费角色。未来平台加入多准备输入/多阶段权重时，容易在 Task 扩展固定表，造成框架随每个领域修改。

**根因。** 事实：资产类别直接决定科学消费槽位，实际消费不检查原 asset 的 split/phase。推断：当前候选 API 同时承担“管理层有哪些资产”和“领域步骤能消费哪些资产”，两种事实所有权混在一起。

**最小架构动作与职责。** Task 先提供原样资产事实目录（运行、类别、阶段、名称、摘要、依赖、不透明语义及受控引用）；由 application/provider 描述本步骤可接受的输入角色和候选关系。Server 将其适配为现有 binding/ref 列表，现有外流 UI 不变。复用已投影的 inputs.*，不增加每份 recipe 必填的第二张配置表。Task 仍控制来源、修订、是否完整提交与权限，provider 不接管管理校验。

涉及 Task artifacts/inspections、已有 spec 资产记录、领域 handoff/operations、Server stages；只在字段缺口确有跨领域证据时扩展 spec。长期行为归 Task tasks/templates 与 Server modules PRD，不另写统一科学生命周期规范。

**科学语义保持与迁移。** train/cal/test、posttrain 各自角色保留，不把它们改名为 CFD preparation。保留旧 list_stage_artifacts 返回形状作为兼容投影；历史资产字节不改。无 provider 的自由脚本仍可用通用 Task 执行/资产引用，只是不自动获得阶段候选适配。该建议以新领域候选/平台消费需求为实施触发条件，不阻塞当前研究运行。

**验收设计。** 用 CFD 单准备记录和控制流程三准备记录/后训练权重作对照：候选只进入声明角色，不误绑定；缺声明不给猜测候选；失败运行仅暴露已提交恢复资产，试跑仍排除。验证复制资产、bundle 依赖、恢复引用与比较索引均不改变。继续保留读取候选时只查文件存在/受控路径、真正消费时核字节的性能边界。

**可量化收益与未验证效果。** 当前投影覆盖 4 类固定分支、6 个去重 binding 路径；三份 preparation 都被映向同两个通用槽位。目标是跨两领域新增候选角色不新增 Task 阶段/字段条件分支，全部声明角色均有准确映射。未测接入工时、UI 完整性或运行成功率；不据此声称新领域平台已支持。

## R3 · 中：将检查出图装配移出 Task worker

**源码与调用链证据。** [inspection_worker.py:11](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inspection_worker.py:11)先调用领域 execute，判断 trace_model，读取返回的 network/inputs/predict，再直接 import ai4e_viz.inspect.model_graph.export_platform_views。后者 [model_graph.py](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-viz/inspect/model_graph.py:1)接收活对象出图。故管理主进程不加载模型成立，但 Task 包内部仍拥有领域对象→显示产物的装配，且发生 Task→Vis 的运行时依赖。

**系统性痛点。** 每种新诊断视图都可能让 Task worker 增加对象字段/渲染分支；仅按包清单查依赖会漏掉延迟 import。该问题涉及检查操作职责，不以某个模型为架构中心。

**根因。** 事实：worker 同时是通用进程执行器和特定诊断的渲染适配器。推断：将桥接放进子进程解决了加载隔离，却没有解决装配所有权。

**最小架构动作与职责。** Task worker 只执行声明入口并返回可序列化结果。将现有构造→出图连接移到显式选用的 recipe/检查适配入口，由它在生产诊断资产的进程中组合领域检查和 Vis 公开出图 API，最终只向 Task 交付固定 HTML/图资产与修订；不把 Vis 强制加入 core/contrib 依赖，也不要求普通研究组件提供网络。保留现有 Vis 绘图实现和 Server 固定资产登记。若将来需要跨进程图中间格式，另以真实需求论证，本轮不先建统一计算图 schema。

涉及 Task inspection_worker、声明检查适配入口、Vis 公开出图边界、Server visualization 消费；架构正文应明确“诊断资产生产”和“固定结果展示”的不同边界，Task/Vis PRD 随实现同步。

**科学语义保持与迁移。** 现有网络、输入、predict 及随机状态保护不变，只移动连接的所有者。已有两档图、资产名、来源修订和错误传播保持；旧声明可通过显式兼容适配继续运行，历史图不重生成。

**验收设计。** 普通 inspect 在未安装 Vis 时仍能运行；只有显式 trace 适配要求出图能力。验证 worker 不再读取 network/inputs/predict、不导入 Vis；两档图和来源修订可由 Server 继续消费，出图失败无半份成功资产，模型前向及随机流不变。安装与正式 Web 链路需单独授权验证。

**可量化收益与未验证效果。** 当前有 1 个 Task 特定渲染桥接和 1 处该链路的 Vis 导入；目标为零，新增诊断输出不修改 Task worker。未测绘图耗时、数值等价或跨模型覆盖；只提出所有权调整，不宣称已有迁移。

## 应保留的设计与维护观察

保留公开 run 门面、Python recipe 正文、领域内自由函数、通用资产/指标索引、完整修订检查、固定结果 post、独立执行/Vis 进程，以及 Server 的明确官方目录。不要新增全仓科学协议、DAG 调度器或强制模型登记中心来解决这些接缝。

维护观察不占核心名额：架构正文的“五领域/模型清单”已落后于当前 AGENTS 与新目录；Task 模板 PRD 仍夹有旧 task-entry operations 描述，而现行 read_entry/operation_target 走 config.yaml 的 components.application；部分长模块索引仍带历史状态叙述。优先更新各自真源与跳转，不能用文案修正替代 R1/R2/R3 的源码迁移。本轮不修改这些文档。

## 未验证范围与本轮执行边界

- 仅阅读当前源码、PRD、模块导航并做 AST 调用点统计及内容哈希；未运行 pytest、训练、科学复现、wheel 构建、安装验证或浏览器冒烟。测试名称只用于未来验收设计，历史通过数不算本轮结果。
- 未验证安装副本、8000/5173/Vis 运行时是否与源码一致；未 sync、重装、重启、迁移、提交或改框架文件。
- 未全面审计每个动态 import、全部 Web 微领域、所有科学领域 provider 或外部用户 recipe。静态调用数量仅限明确命名的 inspect_inference 调用，不是全仓调用图。
- 未验证建议实施收益或 Agent 盲定位效果；现有帮助资源源码存在不等于 wheel 与使用效果已通过。
- 写入范围仅本复审目录（日期报告、最新入口、状态与身份）及自动化 memory。历史 2026-09-18 报告原样保留。
- Experience 查询回执 receipt_81fbde6dc65040b6a05b400e2c39336d 只返回消息聚合习惯，未作为架构证据或采用配置修改；未归档会话。


写入后核对：2026-09-21T04:08:21.245136+08:00；上述 3,488 路径逐项重新核验，复审目录外内容及路径集合未变化。
