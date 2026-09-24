# Dojo 框架分层架构复审 · 2026-09-24

## 全局判断

主干分层已趋于一致：研究计算与专属连接由 core/application/contrib 持有，recipe 明示流程，Task 管固定身份和生命周期，Server 管平台用例，Web/Vis 消费公开交接。原 R1–R3 的 Task 科学解释、标签候选和活网络出图问题在本轮抽查源码中未回退；R4/R5 的修复仍在。本轮只新增 **R6 一项中优先级建议：把准备页的科学描述、默认值和兼容判断收回 application，避免 Server/Web 继续拥有另一套科学解释规则**。

这不是宣称所有平台入口已经领域无关。当前 Web 仍为已登记外流案例服务；真正剩余的分层缺口在具体页面的科学解释所有权，而不是缺一个统一模型协议。无需因本报告新增模型平台入口、DAG、统一张量格式或全环境冻结。

北京时间起始身份采样：**2026-09-24 07:15:34 +08:00**。Git HEAD：`9b53fc4cc4e38c128b18489f0b95f85055ceafaf`。工作区内容身份：`006772c54ed623d939203143a3a105a614d33aa9d58b35cb7802820a6ae88ca6`，4,195 个 Git 可见路径；包含未提交内容和已删除跟踪路径的 missing 标记，排除复审目录，不涵盖忽略文件、安装环境和外部运行数据。算法及逐文件摘要见 [内容身份](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-24-identity.json)。

相较 9 月 23 日上午报告的逐文件身份：178 项改变、11 项新增、0 项新删除，HEAD 未变。新增来源依赖模块及三阶段连接修复来自已有工作区，本轮没有实施。建议状态文件在 9 月 23 日晚已将 R4/R5 标为完成，但日期报告仍是上午的问题态，且状态文件的 `active_core_recommendations`、`implementation`、`repair_verification.formal` 残留发布前文字。本轮保留旧报告和原状态快照，在当前状态中区分历史验收与本轮复核。

## 五个全局问题

### 1. 事实归属、调用方向与进程边界

- **spec** 拥有持久化和进程交接的最小记录，不拥有算法和所有领域的统一科学对象。现有 [task_operations.py](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-spec/artifacts/task_operations.py:16) 只约束 JSON 描述、输入位置、标签与执行单元；这些是可选管理功能的约定，不是普通组件准入协议。
- **core** 拥有中立计算、领域步骤、执行机制和运行记录；不拥有任务数据库或官方模型目录。能力组合与 `run` 门面应保留。**contrib/application** 拥有模型/数据/方程专属参数和科学连接；[operations.inspect](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-contrib/application/aero_cfd/operations.py:20) 解释描述、检查及固定结果操作。普通函数继续自行定义输入输出。
- **recipe** 拥有研究步骤顺序及连接选择。当前 [Transolver trainprep](/Users/zonghui/work/new_code_project/AI4E_Dojo/examples/aero_cfd/nasa_crm_transolver3/trainprep.py:15)、[train](/Users/zonghui/work/new_code_project/AI4E_Dojo/examples/aero_cfd/nasa_crm_transolver3/train.py:18) 与 [infer](/Users/zonghui/work/new_code_project/AI4E_Dojo/examples/aero_cfd/nasa_crm_transolver3/infer.py:15) 显式选择科学链；不能再由图缓存开关间接选择另一条算法路径。
- **Task** 拥有项目、版本、配置修订、运行收据、固定输入/来源、资产引用及失败恢复。它不应决定坐标、损失、采样、结构或科学兼容性。**Server** 拥有平台授权、路径范围、配置编辑事务、公开目录与 API 投影；官方模型登记是 Server 的合法职责，不是 Task 的模型中心。
- **Web** 拥有编辑草稿、请求状态和展示；不应再次推导科学兼容性。**Vis** 拥有显示会话、场景及显示变换，读取固定文件，不接管训练对象或重新预测。[runtime.worker](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-viz/runtime/worker.py:14) 实际消费路径、选项和显示来源。

实际主链是 Web HTTP → Server 平台用例 → Task 公共门面 → 捕获来源的独立 application/recipe 进程 → core 计算与 writer → 固定资产/管理收据 → Server/Web/Vis。结构图链为 Server `submit_model_inspection` → Task `inspect_task`/JSON worker → contrib 装配 → core `trace_views` → 固定 HTML/来源；[Task worker](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inspection_worker.py:8) 不再读取 network/inputs/predict。训练、检查、显示进程分别承担各自故障，不把进程隔离误当作职责自动正确。

当前 968 个存在的 Git 可见包内 Python 文件绝对静态导入扫描未发现逆向 ai4e 包依赖；Task→contrib/Vis 直接导入为 0。三个已不存在的跟踪路径单独记录，不算解析通过或新增删除。扫描不能覆盖动态入口和同包内部越界，详见 [依赖证据](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-24-dependencies.json)。

### 2. Task 是否模型无关

主链已做到模型无关：[check_inference](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/inference.py:57) 核查内容修订、应用给出的兼容结果和带 scope 的不透明 execution_identity；[asset_matching](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/asset_matching.py:6) 只按 kind/stage/name/semantics 的类型和值匹配，不按文件名、模型名猜用途。[smoke-data](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/templates/resources.py:531) 已按案例资源声明启动隔离入口，预算不再写在 Task。

仍有已知配置边界残留：[rawprep.py](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/rawprep.py:12) 直接读取 `dataset.processed_name`，并在创建默认展开中用 `components.dataset` 和 `rawprep` 判断适用性。这不是模型名分支，但仍要求管理层认识某一配置树。最小下沉是 application 描述输出共享名称和默认展开能力，Task 仅处理通用共享身份与固定修订；本轮沿用观察项，不据此重开已解决的 R1，也不声称已造成当前任务失败。

### 3. 跨领域管理语言与比较

已有输入身份、版本、运行、资产、检查点、固定结果、指标、失败及恢复语言，应保留。[described_entry](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/descriptions.py:61) 接收可选应用声明；没有描述的普通脚本仍可托管。[compare_runs](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/versions/compare.py:113) 比较完整终态、来源资产完整性和已发布 semantics 等值，不重算科学指标。

“管理层可比”表示发布者声明的统计口径和身份一致，不表示 CFD 压力、PDE 解场和控制安全代价可以互换。缺指标仍可比较代码/配置；缺科学语义不能填默认后声称相同。恢复引用、代数拟合状态与神经优化器状态可以同属资产管理，但恢复计算仍各归应用。`InferenceRequest` 的检查点×分片功能是局部产品约定，不应升级成每个领域必用的运行格式。

### 4. Server、Web 与固定资产

推理链已主要经 [Server inference](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/inference/application.py:12) 调用 Task 门面，透传应用提供的样本、指标和兼容结论；结构图注册的是固定文件。Task 管运行状态，Server 管辅助操作和设置保存事实，Web 管草稿与读取状态，Vis 管显示会话；这些状态用途不同，本轮未发现上述抽查链需要合并为一套数据库。

但准备页还存在真实的事实所有权冲突：Server 从 model/data_specs 与物理清单重新推导角色和兼容性，Web 再实现一份点场形状规则；Server 还识别 AB-UPT 来注入科学默认值。它们并非仅仅展示 provider 结果，见下文 R6。另有 Server 描述缓存只以配置修订为键的观察，不能据 Task 已修来源门禁推断整个显示链缓存都已同步。

### 5. Agent 路由与唯一设计真源

当前 [architecture 短路由](/Users/zonghui/work/new_code_project/AI4E_Dojo/.context/tasks/architecture.md) 负责定位职责、模块与修改边界，已撤下过时的“Task component/model 尚待迁出”说明；[唯一架构正文](</Users/zonghui/work/new_code_project/AI4E_Dojo/docs/AI4E_Dojo_ARCHITECTURE (1).md>) 持有设计理由和全局边界。模块索引连接 PRD、源码和测试，案例检索的 [list_examples](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/templates/resources.py:313) 支持文本和标签过滤，无需先导入模型。

本轮读到的路由没有建立第二套独立架构设计；Vis 内部架构属于子系统正文，不与全局包边界争夺所有权。不过部分模块索引仍累积历史切片，唯一正文第 0 节清单也落后于后文新增能力。这是导航维护观察，不能包装成核心架构建议。未做 Agent 盲定位计时，不宣称检索工时已减少。

## 核心建议 R6 · 中：准备页科学解释归 application，平台消费声明和结果

**重要性与系统性痛点。** 下一次新增领域页面或准备规则时，不能要求研究者同时修改 Python 科学连接、Server 形状/默认值逻辑和 TypeScript 兼容算法。问题影响平台演进与跨领域接入，不是某个模型的精度或局部性能。建议在下一次准备页科学语义扩展前处理；当前没有证据要求立即重写全部工作台，也不因建议自动开放其他领域。

**源码与调用链事实。**

1. Web [readStage/saveStage](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-web/src/modules/stages/api.ts:5) → Server [configuration](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/application.py:63) 先取 application `describe_case`，随后自行覆盖/补充 `field_matching`、split，并调用 `normalize_field_scales`。保存时 [application.py:287](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/application.py:287) 在持久化之前再次运行本地科学判断。
2. [domain.model_roles](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/domain.py:113) 读取 `model.data_specs`，缺 position_dim 时采用 3；`dataset_fields` 解释 physical_layout/rawprep 字段；[validate_field_bindings](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/domain.py:387) 判断物理域及特征轴相容。[abupt_model/default_field_scale](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/domain.py:341) 按组件路径含 `abupt` 判断，把缺省 coordinate scale 写成 1000，其余为 1。此为 Server 科学参数分支，不能误报成 Task 分支，也不能与合法官方目录登记混为一谈。
3. Web [PreparationPanel.shapesCompatible](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-web/src/modules/trainprep/PreparationPanel.tsx:21) 再次实现忽略 N 轴、比较剩余轴的规则，缺角色描述时从配置 domains 重建角色，并据此禁用候选（同文件第 356 行）。因此形状显示和科学适用性判定实际混在一起。
4. 科学计算已有归属：[contrib operations](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-contrib/application/aero_cfd/operations.py:20) → [core inspection](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-core/applications/aero_cfd/inspection.py:318)，实际变换由 [trainprep normalization](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-core/applications/aero_cfd/trainprep/normalization.py:12) 消费。官方案例 YAML 已显式声明 scale=1000。当前 [Web PRD](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/PRD/ai4e-web/src/PRD.md:204) 也承诺形状禁选及保存拒绝，迁移不能删掉门禁来“简化分层”。

**根因：事实与推断分开。** 事实是准备角色、尺度默认值和形状兼容存在于平台 Python/TypeScript，而 application 承担实际科学计算和其他检查。推断是平台初期以外流数据配置直接驱动页面，之后 provider 迁移覆盖了 Task 操作，却未覆盖页面准备契约。本轮未证明这些规则何时引入，也没有证明现有五例发生了新的数值错误；这是新观察，不是本轮新增回归。

**最小架构动作与文件职责。** 复用现有可选 inspect 连接，让领域 application 返回准备角色、数据字段、已解析科学默认值及候选适用性/原因；保存前由同一应用按当前配置、输入修订检查候选草稿。contrib/application 绑定专属科学语义，core 保留中立形状或变换计算；Task 只固定请求/响应和来源。Server `stages/application` 保留授权、路径解析、编辑合成、修订事务及错误映射，`stages/domain` 保留平台状态与输入选择规则，移出上述科学解释。Web 保留表单、形状字符串展示和草稿，按服务返回的适用性禁选，不独立发明领域规则。新增交接只约束这项可选页面能力，复用现有 API 形状优先；确需新增稳定记录时才更新 spec/传输类型，不建立通用科学算法协议。

**科学语义保持。** 保持 AB-UPT 既有 coordinate scale=1000、其他现行默认、显式用户 scale 优先、错域/特征轴拒绝、未知形状不伪称已验证。点场的 N 轴规则归外流连接；控制时序、规则网格和异形多场可用各自描述，不能为了页面复用改成 `(N,C)`。Python 与平台使用同一科学解释，平台编辑范围仍由 Server 决定。

**迁移影响。** 影响 contrib/application、现有 core 领域检查、Server stages、Web PreparationPanel 及各自 PRD/模块索引；若扩展管理请求则 Task 只透传。保留旧 API 字段或逐项声明迁移，缓存必须计入应用来源和实际输入修订。旧配置/准备/检查点不批量改写，已有固定运行不切换当前解释器。Server 官方目录和 Task 比较门禁不移走。实施后的正式 Web 验收必须另获当次发布授权，本轮不实施或请求发布。

**验收设计。** 先用现行外流准备契约做前后等价：显式/缺省 scale、错域、标量/多轴特征、不明形状和候选草稿均经同一 provider；比较 Python 描述/检查与 Server 响应、Web禁选结果。再用一个不含 `model.data_specs`、具有时间轴或多场角色的最小测试 provider 证明可经相同管理通道表达，不登记新平台模型、不训练。变更 provider 或输入资产而配置不变时描述失效，旧运行来源保持固定；保留现有相关测试，最后做受影响包安装及已开放正式准备页面验证。

**可量化收益与未验证效果。** 目标：平台中 AB-UPT 科学默认判断从 1 处降为 0；Server/Web 两份领域形状兼容实现降为 0 份平台自有算法，应用成为唯一科学判定方；外流与一个非点场 provider 共用管理通道，Task 新增模型条件为 0。当前仅确认这些代码位置，未实施，未测接入时间、请求次数、延迟或准确率收益。允许页面缓存已返回的候选结论，但不能为减少请求重新复制算法。

## 既有建议状态与应保留设计

- **R1/R2/R3**：继续保持源码已解决的判断，未在本轮重新完整运行其全部科学/页面验收。应保留完整 semantics 比较、标签缺失不可选、多候选显式选择、JSON worker 和固定结构图。
- **R4**：不再列为待修。当前三例 Transolver 的三阶段显式连接已核对；同批 wheel 中 736 个非资源 Python 成员与当前五包源码比较无差异，见 [只读核对](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-24-wheel-source-audit.json)。这是 wheel 成员到源码的字节核对，不是本轮安装测试或完整资源审计。9 月 23 日正式范围见 [当次验收记录](/Users/zonghui/work/new_code_project/AI4E_Dojo/.context/mvp/task-generalization-acceptance.md:119) 及 [原始发布收据](/Users/zonghui/work/project_simulation/dojo_train/architecture-repair-20260923/release/final-verification.json)；本轮未重新训练或打开正式页面。
- **R5**：继续保留 9 月 23 日晚的范围内验收状态，本轮独立确认 [source_dependencies](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/source_dependencies.py:99) 捕获静态依赖和声明资源，[operation_sources](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-task/tasks/operation_sources.py:180) 校验内容和解析身份。安装中的 operation_sources/source_dependencies/snapshots 与当前源码逐字节一致；本轮针对外部内容变化、同名遮蔽、声明动态模块/资源、复制加无关文件、旧来源不可用的 6 项检查通过，见 [日志](/Users/zonghui/work/new_code_project/AI4E_Dojo/docs/reviews/archreview/2026-09-24-source-check.log)。来源闭环不等于冻结解释器/驱动或任意动态 Python 行为。

保留自由函数和局部协议、run/writer 单一记录方、application 解释科学事实、Task 公共管理门面与终态/完整性门禁、固定结果 post、Server 官方目录、独立 Vis，以及研究/Task/Web 各自明确的支持范围。不要为消除平台重复规则而要求全部组件实现页面协议。

## 观察项

1. Task rawprep 对配置树的残留读取见前文，延续旧观察；不占新增核心建议名额。
2. [Server `_describe_case`](/Users/zonghui/work/new_code_project/AI4E_Dojo/packages/ai4e-server/modules/stages/application.py:51) 的进程内 LRU 键只有项目、任务、配置修订和输出根；Task 描述缓存已带来源修订，外层仍可能在 provider 改动且 YAML 不变时返回旧描述。这是源码支持的失效条件推断，未做页面反例。R6 的描述交接应连同该缓存核验，不能据此说实际执行来源门禁已被绕过。
3. Agent 入口已修旧整改说明；部分索引仍堆积历史进度。建议状态文件的发布前后混合字段本轮已以审计元数据纠正，旧状态另存；普通维护问题不升级为架构建议。

## 未验证范围与执行边界

本轮完成架构/模块/相关 PRD 与当前源码调用链核对、Git 可见内容比较、静态包依赖扫描、历史最终 wheel 的只读字节核对和 6 项来源针对性检查。没有运行全仓测试、训练、数值恢复矩阵、构建/安装、浏览器或正式 8000/5173/Vis 冒烟；未验证所有动态导入、全部 Web 微领域、Agent 盲定位速度及新建议的运行效果。历史验收只说明当时记录的范围，不计入本轮通过数。

写入仅复审目录的报告、状态、身份、扫描与检查产物，以及 automation memory。未改框架、源码、配置、规则、PRD、索引、基线、历史证据、提交或服务；未 sync、重装、重启或迁移。Experience 检索回执 `receipt_ffcfcf3910f94c7a9db1f5ed5853d688` 无结果，未应用经验、未归档。

通知理由：R6 是新发现的跨层科学解释所有权问题；R4/R5 的旧问题态报告本轮与后续修复证据对齐。结束内容身份复核结果见当前建议状态文件。

结束复核：2026-09-24T09:07:50.055018+08:00；复审目录外 Git 可见内容与起始身份存在变化，见状态记录；不归为本轮修改。
