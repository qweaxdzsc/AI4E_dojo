# SafeDiffCon 执行与验收记录

## 2026-09-17：现行公共约定适配完成

本轮按[已批准实施计划](../../.cursor/plans/safediffcon-task-transparent-execution.plan.md)完成代码集成，不扩展Web、不重启长训练；以下旧入口及待实施说明保留当时范围，不再代表现行协议。

- 模板与Burgers/Tokamak两个example均含完整可编辑的八份Python正文、配置及README，Task从pipeline.py/config.yaml发现，执行同一正文。未恢复task-entry或独立Task算法执行器，未改Task/core通用协议。
- 公共输入、运行/数据根和内部领域参数分离；旧配置转换按原文件目录生成新副本，新旧键混用拒绝。求解资源为inputs.infer.solver_assets；真实KSTAR验收发现并修复解释器符号链接穿透venv的问题。
- 物理/准备/推理结果均登记自包含数组目录，领域补足预训练/后训练/适配的检查点身份，指标交付真值、样本与归约口径。复制共享结果后移走本次原结果目录，fork任务独立post成功；fork引用共享副本，不宣称为other资产再创建独立物理副本。
- **正常训练通过**：三个目录均经实际安装公开Task入口运行；两例官方读取器原分片8/4/2前缀，CPU dim8/DDIM4，从零更新2次、恢复至3次、后训练两轮各1次、适配1次、2测试样本实际Burgers/KSTAR响应。直接/Task模型、EMA、优化器、调度器、批次流、随机状态、损失、控制、预测及响应逐值一致，最大差0；只排除已单独核验的父权重位置等运行路径，科学合同不删除。
- 连续执行和分阶段执行均通过；复制正文真实替换模型构造器、生成能量字段并插入audit读取消费。历史Burgers5000→5001、Tokamak8000→8001真实续训及后续阶段成功；旧50样本固定结果通过交付启动器CLI新建任务后独立post，旧数组摘要未变。新协议工具修复不等于重跑历史完整对照。
- 负向测试单列：缺权重/固定结果失败，篡改资产失效，旧键/冲突输入拒绝；模型与求解器不可用时post成功只是附加隔离测试，不代表正常训练被禁用。
- 研究环境独立安装同批spec/core/contrib/task；CLI worker核对解释器、模块路径及文件摘要。主环境缺少SafeDiffCon依赖/旧安装副本不作为可用入口；交付启动器固定研究解释器和安装目标。Task配置测试含server夹具，使用主测试解释器加载隔离四包，不重装主环境或修改正式服务。

证据根：`/Users/zonghui/work/project_simulation/dojo_train/safediffcon/public-conventions/`。最终`REPORT.md`、`report.json`、`source.json`记录发布文件摘要、测试与原账本读数；`burgers-example-v2`、`burgers-template`、`tokamak-example-v3`含双入口报告，`{burgers,tokamak}-legacy`含历史续训报告，`{burgers,tokamak}-cli`含CLI及worker环境记录。旧失败/重试目录保留，均已计账。

实际启动器：上述证据根的`run.sh`。可执行 `run.sh /你的案例/pipeline.py --config /你的案例/config.yaml` 或 `run.sh -m ai4e_task ...`；发布完整目录为`release/{recipe,burgers,tokamak}`。默认科学参数仍是此前缩小科研配置，并不自行限时；所有新增计算继续包在原累计账本监督器内，不能复制目录重置预算。`initial-wheels`及既有安装/模板证据保留供回退。

最终圈定 **131项唯一测试通过、0跳过**：主要103项、Task配置/管理17项、文档7项、追加科学口径4项；重复用例不重复计数。报告日志分别为related-tests-v2.log、task-regression.log、doc-final-tests.log、metric-final-tests.log；ruff通过。修复的compare/replay工具两例缩小完整执行及逐值重放也通过。

原累计账本最终Burgers **112.10分钟**、Tokamak **65.99分钟**；本轮分别新增5.24/7.32分钟，均在20+10分钟本轮分配与180分钟原总额内。含失败重试、共用回归在两例的保守分摊、各60秒安装/构建/探针预留；非实施人员墙钟工时。source.json核对472份安装源码一致；同时发生的无关WDNO handoff源码变化单独登记，不覆盖另一项工作。

验收范围为当前公开代码入口和缩小预算工程一致性；论文精度仍未达成，Tokamak两类目标和论文离散归约未决。无正式Web消费链改动，8000/5173与主安装环境不在本次发布范围。

## 历史：2026-09-17 Task失败原因复核与当时待实施优化

本轮只读核查源码、既有报告和训练检查点，未新增训练。方案见[任务一致执行优化计划](../../.cursor/plans/safediffcon-task-transparent-execution.plan.md)。

- 原先缺 `task-entry.json` 导致提交拒绝，发生在计算开始前；另一独立记录 `task-validation-20260917/before.json` 为 worker 缺 `ai4e_contrib.application.pde_control`，同样未开始训练。后者未保存完整解释器/包来源，具体安装版本或导入路径原因不能追认。
- `task-validation-20260917/{burgers,tokamak}-complete/report.json` 均有真实准备、从零训练2次、恢复至3次、后训练、推理/post及连续训练至post成功；本轮读回两例检查点，确认从零训练的resume为空、恢复历史前缀相同、权重最大变化约1.00434e-5。实际为原物理数组8/4/2子集、dim8、DDIM4的工程验证，不代表论文精度，也没有重跑原始数据处理。
- 不可用模型和求解器仅用于推理完成后的独立post隔离测试；不能解释为正常训练被禁用。缺结果导致的预期失败须与正常流程失败分列。
- 当前pipeline和task是两份流程，加载器有阶段重设/补回逻辑。拟合并正文并补同输入直接/Task训练数值对照；这些优化尚未实施，已有成功记录不代替该项新验收。
- 本轮原账本读取值：Burgers6411.487秒、Tokamak3520.074秒；下一轮重新读取余额。主环境与正式服务未修改。

## 2026-09-17 Task公开API补验

此前66项及精度对照没有经过Task新建/提交链；缺少task-entry.json的原模板被实际提交拒绝：entry_required。本轮补task.py与声明，配置显式阶段范围，保持旧普通脚本行为，未修改Task包算法或平台。

- 证据根：`/Users/zonghui/work/project_simulation/dojo_train/safediffcon/task-verification/`；REPORT.md、report.json、source.json、两例acceptance.json及runs.json。
- 独立安装Task wheel，复用已验spec/core/contrib；使用register_template→new_task→submit_run→wait_run公开接口，经真实worker执行。
- Burgers正式任务 `5017ffc71c514eeb9ce8b0bc88f905cc`；Tokamak正式任务 `f1704002a4f140f5a5e64e2b1e3f2d97`。各四次成功运行train/posttrain/infer/post；另有一次预期缺权重失败，不增加版本。
- 各从5000/8000步预训练状态新增2次真实更新并核验权重改变；两轮各2次后训练、一次适配、2个原样本实际Burgers/KSTAR响应。复用原数据准备，本组没有重做原始处理或完整50样本精度。
- post覆盖模型入口与求解器为不可用值后仍成功，指标一致、清单摘要不变、不生成检查点。Burgers CLI独立post通过；首次CLI被正在运行的同案例预算锁拒绝，待收尾后重试成功，未重置账本。
- tests.log：37项通过、1条上游转义警告，无skip；圈定SafeDiffCon Task/数值/打包与Task管理/契约。ruff及格式通过。
- 交付时原账本累计Burgers106.86分钟、Tokamak58.67分钟，含其他已计账同案例验证和本组各15秒构建/文档保守预留；预留不作实测训练。旧报告保留当时数字。
- 结论：通用Task Python API/CLI可以新建并执行控制案例。平台模型选择、专用推理批次/评价操作未声明；阶段范围只裁剪Python固定顺序，独立步骤显式传入准备、阶段权重或固定结果。

以下为2026-09-16历史集成与精度记录。


更新日期：2026-09-16。用户纠正后按**每案例累计最多三小时**执行集成。原版完整论文训练不在本次范围；最新授权覆盖 skill 的完整论文复现前置门槛。计划见 [实施计划](../../.cursor/plans/safediffcon-integration.plan.md)。

## 历史4000步集成范围

- 已实现并完成本次缩小预算验收：contrib 模型、扩散、校准、重加权、适配与响应；core 控制领域交接；六阶段可复制 recipe。
- 已停止错误启动的 200000 步长训练，不使用其中权重作为短预算从头基线。
- 每案例账本包含此前计算、失败、重试、参考、Dojo、校准、后训练、适配及求解；175 分钟软停止，180 分钟终止进程组。
- 短配置：dim64、batch16、两侧各4000预训练更新、DDIM50、校准200；Burgers 后训练2×320，Tokamak2×1；适配1次；各50个测试样本。
- 正式服务、主环境及外部原仓库不修改；wheel 仅装入独立环境。全部计算产物在 `/Users/zonghui/work/project_simulation/dojo_train/safediffcon/`。
- 原训练器独立执行预训练；校准/安全引导/采样另与冻结原函数数值对照。两侧后训练与响应的领域连接共享 Dojo 装配，不能称为两套独立的完整论文复现。

## 来源与数据

固定来源提交 `f931ca5243286a83952333fac73cf7014f86ee45`，保存 HEAD 相对修改补丁；
patch SHA256：`45cecc1effda2e500c5cc9f79acd4426daa8a8a046f9295773decb689c0456e0`。
快照包含两个案例的 183 个跟踪文件和资源；2d 不在本次范围。未跟踪文件不执行。

证据根：`/Users/zonghui/work/project_simulation/dojo_train/safediffcon/admission/20260916/`。
`admission.json` 保存完整来源、逐文件摘要、形状与全量数值检查。

- Burgers：train/cal/test 为 39000/1000/50；不安全样本 34985/900/50，与论文 Table 11 一致。
- Tokamak：四个 Arrow 分片均完整，50000 样本全部字段有限；划分 48950/1000/50。
  第 1、2 分片从 ZIP 流读取；第 0、3 分片的展开副本与 ZIP 内容哈希一致。
- Tokamak 不安全样本 train/cal/test 为 34843/722/36；训练占比与论文 71.18% 的舍入值一致。
- Tokamak 的原 `targets` 与 `outputs[:,[1,6]]` 不同：以源码同类 MSE 和归约计算两者距离，
  train/cal/test 分别为 0.0093924960 / 0.0094079901 / 0.0094952390。
  该数值是两类标签之间的差值，不是 SafeDiffCon 模型成绩。

## 实跑证据

- `burgers-probe.json`：原求解器 CPU 回放 50 条原控制，1.370 秒；最大绝对误差
  1.01328e-6；原后训练和推理类用 dim=8 实际构造通过，只证明可启动。
- `kstar-probe.json`：原 KSTAR 回放前两条测试控制，通过 rtol=1e-4 / atol=1e-6，
  q95 安全判定一致；每样本含重新加载模型约 5.18 / 4.89 秒。
  不同单位字段的绝对误差不可混用，wmhd 为约 0.394 的绝对差但相对误差满足约定。
- `kstar-probe-50.json`：全部 50 条测试原控制回放通过；总响应计算 211.681 秒，
  全字段通过 rtol=1e-4 / atol=1e-6，q95 安全判定逐值一致。最大绝对误差：
  βp=7.018e-6、q95=1.476e-6、li=1.320e-6；wmhd=1.092（自身单位，仍满足相对容差）。
  这里只证明原控制的响应环境一致，不是新生成控制的性能。
- 参考预训练诊断：`reference/burgers/diagnostic-20/progress.json`，正式 140710147 参数、
  dim=128、batch=16、MPS FP32，20 次原 Trainer 更新成功，训练循环约 11.6 秒；
  含最终检查点写入总计 14.47 秒，末次 loss=0.4722563922。这不是精度验收。
- `reference/burgers/diagnostic-50/`：50 次更新通过，含保存共 31.652 秒，
  loss=0.2170595825；验证新增只读进度观察和 checkpoint 保留连接。

## 已停止的错误长训练

原目录 `reference/burgers/full-pretrain-20260916/` 保留历史失败证据。用户要求停止后，向该任务发送 SIGINT；PID 16551/16552 已退出。最后观测 step1450、loss0.005566615、elapsed971.3626秒；`reference/burgers/stopped-by-user.json` 保存停止记录。此前约32小时估计来自误用 dim128/200000步，不符合用户要求，已取消。

新账本初始计入 Burgers1018.851秒、Tokamak221.755秒，此后每次计算累计，不能通过改目录重置预算。旧 `reference.py` 取消步数默认值并拒绝超过4000步；实际短预算采用 `compare.py` 的 dim64 配置。

## 论文与源码处理清单

论文采用 arXiv 2502.02205v4 与本地 PDF 附录 F/H、Algorithm 2/3。科学差异不能通过测试集选优来掩盖。当前缩小变体采用以下明确约定。

1. Burgers 正式预训练 dim=128、200000 更新，Table 12 与原 turbo 配置一致；
   Adam、lr=1e-5、batch=16、Cosine T_max=10000、EMA beta=.995/update_every=10 按原 Trainer。
2. Burgers 原采样默认 200，论文 Table 12 为 100；正式论文配置应使用 100，并保留原版差异记录。
3. Burgers 原后训练保存调用被注释，推理仍加载 model-171；必须建立后训练权重明确交接，
   不能以直接加载预训练权重的入口当成完整三阶段复现。
4. Burgers 原后训练初始 Q=0、每轮末更新 Q（末轮不更新），Algorithm 2 要求每轮开始校准；
   原推理同样在更新后校准，与 Algorithm 3 的顺序不同。论文修正参考版本必须单独记录补丁及证据。
5. Burgers `InfFT_iters=3` 在原循环实际执行 2 次更新；对照分别记录声明数与实际数，不默默改成 3 次。
6. Tokamak 预训练 turbo 默认 dim=128，与发布后训练配置/权重 dim=256 不符；正式网络采用发布的 256，
   在构造和加载验收中保留这一来源差异。原 finetune.sh 实际采样 250，不应误记为后训练的 200。
7. Tokamak 原 `get_target`、校准和条件从 outputs 取 βp/li，论文描述随机目标，数据同时提供 targets。
   两种口径数值不等，尚不能认定源码指标就是论文 Table 3 指标；本次同时报告 J_source_outputs 与 J_dataset_targets，不宣称论文口径已解决。

## 历史4000步验证及未完成项

- 准入与历史参考门禁10项、GenCP能力回归9项通过；独立 wheel 环境的控制交接7项通过。
- Burgers dim64/MPS 相同输入初值下10更新，原Trainer与Dojo损失列表、全部模型权重逐值一致；小规模后训练、适配、实际响应和结果读回通过。
- Tokamak 原函数对照：dim8/CPU、DDIM50采样逐值一致，校准Q逐值一致，输入梯度最大绝对差2.384e-7。DDIM3 的诊断出现非有限采样，未作为通过证据；正式配置保留已验证50步。
- 两案例4000更新、全部50测试响应、仓库外三个扩展、最终安装包重放与文档回归均已完成。

论文参考值（本次不承诺达到）：Burgers J=0.0011、三类违规率零；Tokamak J+=0.0094、样本/时间违规率零。数值迁移容差 rtol1e-4/atol1e-6，身份、数量与实际更新次数须相同；不通过事后放宽容差取得通过。

缩小变体的显式差异：固定官方训练/校准/测试划分，独立可恢复排列流保留尾批；两轮开始校准，修正Burgers原轮末顺序；明确交接后训练权重；实际适配次数取1，不复用原 off-by-one 计数；Burgers普通采样采用EMA、适配采用在线权重；Tokamak目标输出和数据targets分别评价。每阶段重置种子用于可重复对照。训练数据仍全部进入预训练抽样池；更新预算只覆盖其中有限次抽样，不称完整收敛。

## 历史4000步验收（三小时累计范围内）

总报告：`/Users/zonghui/work/project_simulation/dojo_train/safediffcon/delivery/REPORT.md`；结构化结果同目录`report.json`，`source.json`固定最终代码和实际wheel摘要。

- Burgers实测实验累计54.58分钟，加共享测试/安装保守预留5分钟，核算59.58/180分钟；Tokamak实测25.57分钟，核算30.57/180分钟。此前停止的错误长训练已计入Burgers，不重置账本。全部监督运行均已收尾。
- `short/{burgers,tokamak}-acceptance.json`：两侧各4000更新的损失列表、模型/EMA逐值一致，优化器/调度器/数据流通过对照；两轮后训练和1次实际适配一致；全部50样本的控制、预测、响应最大差值0，身份及安全判定一致。
- `short/{burgers,tokamak}-final-replay/replay.json`：最终安装包对原权重重放校准、适配和采样，控制、预测、校准值与适配权重逐值一致，因此已保存的真实响应仍有效，无须重复KSTAR求解。
- Burgers：J=0.2227771660，R_sample=0.04，R_time=0.0072727273，R_point=0.0009659091。Tokamak：J_source_outputs=0.4017584727，J_dataset_targets=0.3916010415，R_sample=1.0，R_time=0.2540983607。**均未达到论文精度；本次完成缩小预算集成，不是完整论文复现。**
- `extensions-final/acceptance.json`：实际wheel与仓库外复制运行通过；dim32小网络、安全梯度+控制能量变体、物理安全余量三个扩展通过。安全变体控制变化最大0.6019637585；派生字段的B,T轴、u单位、有效性与ids身份保存并由独立post读回。
- 55项圈定测试通过：独立wheel环境控制/打包/预算/GenCP共34；准入与历史CLI保护12；固定公开源码与实际wheel5；架构文档4。ruff检查和格式检查通过。最终包同时保留原maximum在安全边界的半梯度。
- 隔离参考环境的无关VTK导入曾等待并中断，不计为通过；同一公开接口测试使用已有工作台依赖和新wheel后5项通过。DDIM3诊断非有限未记为通过，正式50步配置通过。

### 检查点与独立性边界

预训练提供正式resume配置；后训练保存完整状态并跨轮交接，官方模板未提供轮内续训专用CLI开关。本次普通步/尾批/EMA状态恢复测试不扩大为所有实际控制模型中断位置的验收。原Trainer独立执行预训练；校准/引导/采样另与原定义核对；两侧后续领域连接共用Dojo，不能将其称为两套独立完整论文程序。

平台未增加SafeDiffCon入口，正式8000/5173未操作，主环境未同步或重装。最终源码、安装包和原始论文/代码之间的差异保留在本记录、source.json与原准入快照中。

## 本轮续接实施

本节与以上4000步历史记录分别保留。新增证据根为原实验目录下的 `continuation/`；原累计账本不重置。

- `reference_stages.py` 直接执行冻结原类/方法，独立编排校准、后训练、适配和采样。双方仍共享准备数组、批次流、状态容器、响应求解、指标与存储。协议见 `continuation/scientific-protocol.md`，不冒称原脚本未经修改的论文复现。
- 预训练配置默认4000不变，总目标允许1–20000的整数；恢复时总数包含已完成历史。实际墙钟上限由原账本与分阶段监督器执行，不能靠换目录获得新预算。原Trainer连接恢复优化器、调度器和步数，每500步保存最近状态。
- `*-resume-acceptance.json`：两案例各侧4000→4100实际恢复，全部权重、EMA及4100条历史逐值一致，优化器/调度器/批次流通过。
- `*-diagnostic-acceptance.json`：独立编排小样本诊断通过；四样本不作为完整指标。两案例参数、控制、预测、响应最大差值0；Burgers适配损失存在容差内归约差，不能称所有损失逐位相同。
- `input-revalidation.json`：原HDF5、Arrow与ZIP副本重新核对，全部摘要仍与准入记录一致；冻结源码每次参考启动前校验。
- 原拟Burgers7000步因持续参考吞吐慢于100步短测而停止，失败尝试计账并保留。Burgers改为5000；Tokamak在启动前保守从16000改为8000，均从双方已验4100状态接续。两例固定后训练2×320、DDIM50、校准200、适配1次、最终50样本。收紧仅依据耗时，不用测试成绩选优。
- `burgers-final-acceptance.json`：5000步预训练、两轮后训练及适配的模型/EMA最大差值0；50样本控制、预测、响应最大差值0，安全判定一致。适配损失仅容差内一致。`burgers-installed-replay/replay.json`：最新安装包重放的权重、控制、预测及Q逐值一致。
- Burgers最新J=0.4102355633，R_sample=0.36，R_time=0.1272727273，R_point=0.0231392045。较4000步基线退步；工程一致不代表学习改善或论文达标。`burgers-reweight-diagnostic.json`只读原训练子集与保存Q：两轮Q为10.322463/4.071980，原指数权重均为0/10240非零，按原定义回退全部权重1。已证实本次安全重加权未生效，但不能单凭此项解释全部精度差距；未擅自改变原算术。
- `tests-complete.log`：最终隔离安装包57项通过；`public-api-tests.log`：固定公开接口和架构9项通过，共66项圈定测试。独立源码有一条上游转义警告。新增配置冻结与报告失败门禁在预算用例中覆盖。
- `extension-evidence-reuse.json`：旧/新wheel逐文件核对，仅案例配置校验变化；已验小模型、安全引导与派生字段扩展的算法/连接未变，复用 `extensions-final/acceptance.json`，不声称本轮重训了三个变体。

- `tokamak-final-acceptance.json`：8000步预训练、两轮各320步后训练及适配的模型/EMA最大差值0，所有损失历史逐值一致；50样本控制、预测、真实KSTAR响应最大差值0，安全判定一致。
- Tokamak最新J_source_outputs=0.2939375415，J_dataset_targets=0.2946154641，R_sample=1.0，R_time=0.0950819672。源码目标误差较基线降低约26.84%，数据目标误差降低约24.77%，时间违规率降低约15.90个百分点，但样本违规率仍100%。

论文表3名称复核为J，历史J+不代表额外惩罚项；目标来源及离散时间归约仍未解决，两种目标分别报告。完整论文精度目标未达成，不因缩小集成通过或尚有预算余额宣称达标。


### 本轮最终交付

- 总报告：`/Users/zonghui/work/project_simulation/dojo_train/safediffcon/continuation/delivery/REPORT.md`；同目录 `report.json` 与 `source.json` 保存结果、实际代码/配置/安装包摘要。旧 `delivery/REPORT.md` 保持不变。
- 原累计账本全部收尾：Burgers **104.7867分钟**，Tokamak **57.2493分钟**，均少于180分钟。各保留历史5分钟共享预留，本轮另各计1分钟构建、格式、只读报告与摘要检查保守预留；预留不是实测训练。停止的7000步尝试及全部失败/重试均已计账。
- `tokamak-installed-replay/replay.json`：最新安装包的校准Q、适配权重、50样本控制与预测逐值重放通过；两例最终安装验证均完成。只有控制字节一致才复用已计算响应。
- `tokamak-reweight-diagnostic.json`：两轮48950个原指数权重均非零，未触发Burgers式均匀回退；仍存在控制误差与违规，不用此现象宣称论文安全目标已达成。
- 本次 **A—E代码集成、独立原定义对照、约定的双侧训练与50样本评价、受影响兼容和安装验收已完成**。A2论文口径保留明确未决，完整论文复现及精度目标未达成；不追加训练、不以余额未用满掩盖结果，也不根据测试成绩选优。
- 继续使用入口为 `recipes/safediffcon/` 及两例 `quick.yaml`；本次实际续训配置位于 `continuation/{burgers-dojo-5000,tokamak-dojo-8000}.yaml`。默认4000步示例不改成带本机权重路径的新默认。模型、配置和执行方案保持可复制研究用途。
