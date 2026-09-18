# WDNO 原仓库切片执行与验收

日期：2026-09-17。P0/P1历史原版切片已完成；用户随后明确要求按计划迁移，已在原三小时账本内完成Burgers基础预测缩小迁移的数值对照。原版论文门槛、六例与其他系统仍未完成。仅代码能力，不扩展平台或操作正式服务。

## 执行范围与证据

实验根：`/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/`。

- 源码：冻结 WDNO HEAD `2d5c0ffbe11797e669efe0a34bd22f087eae51d7` 的全部跟踪文件及当前补丁，导入前按完整摘要检查。数据摘要与既有代表轨迹切片一致。
- 切片：训练18000/验证池2000/测试池4000；开训前固定64验证、128测试。原始 u/f 文件只读，未重写重复样本。
- 模型：width128/groups1、140748553参数、MPS float32、batch16、原Adam/余弦10000/EMA；原Trainer真实运行，EMA从计数0开始。
- 原环境：Python3.8.20、Torch2.4.1、Accelerate1.0.1、ema-pytorch0.8.3、pytorch-wavelets1.3.0。Dojo主环境未sync或重装。
- 预算：最多2000更新；累计135分钟训练截止、165分钟评价截止、180分钟之前退出。复用GenCP监督，初始105.672568625秒为历史两次测速，诊断、失败和重试继续计账。

## 已完成诊断

- `diagnostic-2/diagnostic.json`：原Trainer两次真实更新及完整原checkpoint读回通过；EMA计数为2，参数数量与正式网络一致。
- `diagnostic-2-sampling/result.json`：再次两次更新及验证/测试各两条真实条件采样通过，全部有限；这两条不是主切片成绩。
- 64轨迹小波准备的逆变换最大绝对误差约1.91e-6。原模型的独立初态条件通道不会强制重建u初帧等于真值；诊断高初帧误差保留，不私自clamp修正。
- `test_wdno_reference_protocol.py`、`test_wdno_budget.py` 初次6项通过；另补真实忽略中断进程的硬截止测试通过。保护代表身份/泄漏、源码/名单漂移、非有限报告和失败/重试累计成本。

## 主实验最终结果

P0/P1 原仓库工程切片已完成；整体实施计划尚未完成。主报告：[REPORT.md](/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/main/REPORT.md)，结构化验收同目录 `acceptance.json`。

- 2000/2000 次更新完成；累计记账 **1894.4269 秒（31.5738 分钟）**，含历史测速、冻结、两次诊断、主训练/采样、独立重放和报告复算，监督账本全部收尾。
- 固定验证64/64，MSE **0.05284130899**；固定测试128/128，MSE **0.04937983664**。测试初值保持基线MSE **1.333221674**，这是本地简单基线，不是原仓库重训对照。
- 前/后50更新平均损失 **1.079760067 → 0.00546196335**。学习效果可见，不代表收敛或论文精度。
- 18000条准备完成，形状 `[18000,9,64,64]`；逆变换最大绝对误差约 **2.86e-6**，准备文件与原始数据在最终复算时摘要未变。
- 独立原构造器从主检查点加载普通权重，首批16测试预测与主进程**逐值一致，最大差0**；EMA计数2000。主权重SHA-256 `f344ca2c241850ee59aa58c0e297b7d43aac90663b646534e83115e3e6edab3c`。
- 固定预测对原始名单/真值读回一致；独立NumPy归约与原Torch逐样本MSE最大差 **5.96e-8**。测试力项重建最大误差 **2.38e-6**，初帧最大误差约 **0.53238**，保留原条件通道语义，不添加硬钳制。
- `training-curve.png`、`test-fields.png` 已生成并查看；`losses.json`保留全部2000步，`training-evaluation-console.txt`保留训练/评价控制台输出，`entry-code/`与`delivery-source.json`记录实际工具源码及依赖。
- 最终 **16项通过、0失败、0跳过**：三个门禁/预算/指标测试文件、显式真实切片验收、架构文档及recipe入口。额外ruff检查/格式检查通过。未运行全仓，也未把这些结果称为Dojo算法迁移或论文复现。

真实验收命令：

```bash
DOJO_WDNO_SLICE_ROOT=/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917 uv run --no-sync pytest tests/integration/test_wdno_reference_protocol.py tests/integration/test_wdno_budget.py tests/integration/test_wdno_metrics.py tests/integration/test_wdno_slice_acceptance.py tests/integration/test_architecture_alignment_documents.py tests/integration/test_recipe_documents.py::test_authoring_rule_and_development_entry
```

`formal-readiness.json` 明确P2未通过。0.00014为论文参考值，本次协议和测试范围不同，不把其与本次MSE作同协议精度验收。该段为当时P0/P1的授权边界。后续用户明确要求迁移，当前缩小范围按本文末节执行；不扩大原三小时预算，也不将其他模型授权迁入本例。

## 实现与验收边界

- 工具：`tools/verification/wdno/{protocol,budget,reference,replay,report}.py`，详细使用入口见同目录README。
- 数值主体直接来自原冻结源码；只连接本地切片、CPU分块准备、单进程loader、日志/保存和限时。原评价的高分辨率数据来源被显式基础真值连接替换，不称未经修改的论文程序。
- `checkpoint.json`区分原step字段与完成更新次数。本阶段原checkpoint没有完整流游标，精确续训未实现；B5留待正式迁移阶段，不能用原权重读回代替。
- `test_wdno_metrics.py`覆盖初帧排除、名单顺序与非有限结果；主验收已以独立进程/原构造器加载主检查点重放16条测试预测，再对完整固定预测、原文件真值与原MSE完成独立复算。
- 本切片未修改安装包算法，实际执行入口是仓内参考工具加隔离原解释器；wheel/仓库外recipe是后续迁移验收。正式Web冒烟不适用。

## 正式复现仍缺的条件

高分辨率评价真值、论文groups/预算与脚本冲突、官方测试名单/权重选点仍未闭合。仓库六例和论文五系统不能混称；完整原版论文复现仍是最终目标，本次根据后续明确授权先交付基础预测缩小迁移。三小时切片的有限损失下降不等于论文精度。

## 当前基础预测迁移（数值与安装验收完成）

本次同环境原Trainer在`reference-current-2`，Python3.12.14/Torch2.14.0，与Dojo隔离安装依赖相同。旧main和失败诊断保留，原180分钟账本继续累计。完整交付：[REPORT.md](/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/dojo-final/REPORT.md)。

- 双方各完成2000更新；Dojo真实MPS正式网络经过 **2 → 50 → 2000** 恢复，跨越1125批次的首个epoch。全部2000个损失、模型参数、EMA及优化器状态逐值一致，最大差0。
- 原18000条模型准备逐值一致；验证64条、测试128条的状态预测、驱动力及真值逐值一致，最大差0。`dojo-final/comparison.json`保留原始指标值；Dojo验证MSE **0.0632954388711**、测试MSE **0.0602869855757**，原版分别为0.0632954386383、0.0602869853756。预测本身完全一致，指标浮点归约差均小于2.4e-10；不把汇总指标也称逐值一致。
- 训练前/后50步平均损失 **1.085393357 → 0.008043109733**；140748553参数、dim128/groups1、batch16、seed0、Adam1e-4、余弦10000、EMA .995/10、DDIM50 eta1、普通权重。
- 显式原权重source导入：验证/测试各16条重放，与同环境原版预测逐值一致，见`source-import/replay.json`。原权重缺scheduler/RNG/流状态，不能作为精确续训。
- 实际spec/core/contrib wheel、仓库外复制recipe：完整处理/准备/训练/恢复/推理/独立post，以及网络、损失和派生能量替换通过。原数据小网络变体2更新并完成64/128条预测，能量保存读回一致；见`variant/acceptance.json`。该变体只作组合能力证据，不作模型质量结论。
- 代码包括core时空场领域、贡献侧WDNO数值与数据连接、可复制recipe和普通函数变体。数组清单、迭代装配、原EMA适配共用实现，保留旧控制公开入口。数值定义AST、CPU前向/损失/梯度/更新/DDPM与DDIM、完整状态恢复和取消边界均有圈定用例。
- 正式长训练启动后补共享接口兼容：未选取消回调时不向自定义iterate传cancelled关键词。WDNO实际传入回调，选中路径和数学未改变；长训练运行快照保留旧模块，新wheel通过旧精确签名测试。不重写历史快照。
- 首次两个迁移更新错用了划分seed42，已修正为训练seed0，并增加冻结参数门禁；失败证据保留且计账。变体摘要的配置路径曾被循环变量覆盖，已修正元数据并保留修正前摘要，训练/数组未变。

最终圈定回归 **78通过、0失败、0跳过**（17.52秒）；包括此前因账本仍运行而失败的历史切片断言，现按原断言通过。测试清单及命令完整记录在预算账本最后的closed_ledger_audit条目，JUnit为`/Users/zonghui/work/project_simulation/dojo_train/wdno/migration-final-tests.xml`。覆盖WDNO八组、SafeDiffCon集成/参考/包装、GenCP能力/流恢复、固定用户源码基线及文档入口；未跑全仓，未重验其它模型论文精度。

实际入口：`recipes/wdno/README.md`；隔离安装`/Users/zonghui/work/project_simulation/dojo_train/wdno/installed-final`，数据与训练在实验根`dojo-final`。安装文件、wheel摘要和实际配置见`delivery.json`。训练曲线和固定测试场已生成并查看。

仅基础预测切片迁移完成。论文精度、六例全集、超分、控制、Smoke、多卡和独立陌生Agent现场组装尚未验收；已有组件替换证据不等于计划C6。Web无消费链，正式Web冒烟不适用；主环境和8000/5173均未更新。

### 最终累计账本

本次全部计算与审计收尾后为 **6233.4418秒（103.8907分钟）**，15条监督记录均已关闭，低于180分钟。历史失败条目按原样保留；最终78项回归通过，文档更新后的5项导航复查通过。实际安装文件、三份wheel、运行配置身份再次核验一致，结构化最终结果在`dojo-final/delivery.json`。

## 2026-09-17：跟进公共 Task / recipe 架构

当前源码通过 `pipeline.py + config.yaml` 自动发现研究入口，外部输入来自 `inputs.<stage>`，输出使用 `data_root` 与 `TrainingRun.output_dir`；WDNO已按此约定调整，不新增逐案例task-entry，不把数值算法移入Task。本次沿用原180分钟账本，原2000步报告与installed-final完整保留。

### 改动与使用边界

- 同一pipeline用于直接脚本与Task。阶段选择、配置文件、点号覆盖和程序输入共用检查；旧data/train.resume/infer.checkpoint/post.results拒绝。`configuration.py --migrate ... --output ...`只写新配置副本，不改旧文件；旧`[pipeline]`别名只在显式旧配置转换时展开。
- 分片仍是原数组manifest；连续阶段接本次返回值，独立阶段读明确路径。两者不同则拒绝冲突，不猜最近准备或权重。训练中断保留更新边界但不把未完成预算标为成功研究。
- 数组资产登记真实NPY依赖；检查点由writer自动登记。MSE携带样本/真值摘要、字段、单位、初帧排除、样本等权和评价函数身份，Task只读公共索引比较。固定post不构造网络。
- 新目录为贡献应用`handoff.py`（分片/索引绑定）、`migration.py`（显式配置转换）；数值能力和冻结准备/检查点合同未改。原始源文件依赖仍由来源协议摘要和领域读取检查，不把协议JSON本身的Task摘要当作全部原始数组已捕获。
- 全仓并行修改曾使脚本与候选安装副本接口不一致，首次两个测试在导入阶段失败，未开始训练。已保留`task-conventions-v1/first-tests.txt`，按当前源码重建隔离副本；不改主环境或正式服务。

### 实际科学与跨进程补验

- `task-conventions-v2/real-data/acceptance.json`：原数据8训练/2验证/2测试，小网络dim8、2次更新后恢复至3；直接与Task全部损失/权重/优化器/EMA/调度/批次流及已使用CPU随机状态逐值一致，固定预测与派生能量逐值一致。Task运行不增加版本；三次正式任务运行都成功，后处理仅捕获两份结果输入，和推理后原指标可比较。
- 在仓库外复制recipe中替换网络/损失/派生能力，并显式插入audit阶段；两种入口都实际写能量、读回及登记依赖。独立post另将模型入口设为不可用，仍成功重算；这是正常训练预测后的附加隔离测试。
- `task-conventions-v2/historical/acceptance.json`：同一历史2000步检查点与原准备，在旧installed-final和新安装各真实再更新1步至2001；合同、全部训练状态（含MPS随机状态）与两组各16条预测逐值一致。新科学输出独立保存，未重写旧基线；不以仅加载权重替代此项。
- 最终安装位于 `/Users/zonghui/work/project_simulation/dojo_train/wdno/task-conventions-v3/installed`，四份wheel在同级wheels。v3相较v2，WDNO仅清理配置加载器无用导入，数值代码/训练连接/合同不变；最终安装再次通过原数据两种入口全流程。跨进程解释器和包文件路径由实际audit阶段记录，使用同一隔离Python3.12/Torch2.14。

### 可运行入口与回退

模板与使用说明：`recipes/wdno/README.md`。本机解释器 `/Users/zonghui/work/project_simulation/dojo_train/wdno/environment/bin/python`，启动前将上述v3安装目录设为PYTHONPATH；直接脚本和Task管理进程使用同一环境。四包仅装到新目标目录，未sync或更换主环境。回退使用保留的旧installed-final及旧冻结recipe/config；新配置不能送回旧加载器。

本次不接Web，正式8000/5173未操作；其它模型模板仍由其对应架构任务验收。论文精度、超分、控制、Smoke和独立陌生Agent现场组装未在本轮完成。

### 本次最终收尾

**52通过、0失败、0跳过**（25.90秒），ruff检查/格式通过。最终安装v3原数据双入口复验通过，原Trainer权重显式source导入两组各16条重放最大差0。新增计算和验收2.8775分钟，原账本累计**106.7682分钟**，全部收尾且低于180分钟。完整报告：[REPORT.md](/Users/zonghui/work/project_simulation/dojo_train/wdno/task-conventions-v3/REPORT.md)；包摘要、科学证据、测试与预算见同目录delivery.json。

## 2026-09-17：计划近期实施——新建Task分阶段实跑与独立Agent组合

本次交付：[REPORT.md](/Users/zonghui/work/project_simulation/dojo_train/wdno/task-stages-20260917/REPORT.md)，同目录`delivery.json`固定包摘要、实际运行身份、测试和预算。S1a–S1c完成；论文协议及后续完整复现仍未完成。

- 真实四包wheel安装到`task-stages-20260917/installed`，解释器仍为`wdno/environment/bin/python`，主环境未sync/重装。WDNO数值和专属连接安装/源码摘要一致；本轮没有改变WDNO数学定义。
- `staged-v3/acceptance.json`：原数据8/2/2完整轨迹，CPU dim8、batch2、DDIM2，通过公开API新建项目与任务，分别提交rawprep、trainprep、train、infer、post、resume，六份正式运行成功。更新2→3；全部训练状态与直接脚本一致，预测最大差0，续训确实更新权重，版本数量仍为1。模型构造路径不可用时独立post成功、预测数组未改变；缺准备、权重、固定结果分别拒绝。
- 新任务ID `0c110baa05e444338a7a2e4e284525bc`，项目位于报告目录的`staged-v3/project`；Task交付不是只调用内部阶段函数。该小模型测试MSE13.855388，只证明工程链路，不评价模型质量，也不替代历史正式网络2000步成绩。
- 可复制扩展覆盖集新增完整config、pipeline和audit；普通网络/损失/能量能力不要求框架登记，预测后能量检查读取固定结果，缺字段/错误形状/非有限值/错误能量失败。复制完整模板后覆盖这些文件，扩展目录不能单独作为完整模板。
- 未参与实现的Agent只通过公开材料，在`agent-trial`自行完成参数、目标替换和单位长度质量误差步骤，从零2步、续至3步、独立post通过；初稿、查阅记录、运行命令和报告齐全。主Agent另以`agent_trials.py`直接读固定数组、检查点和报告复算，不执行该Agent的能力代码。该现场任务通过，不推广为任意研究变体或论文复现已通过。
- 默认预算续接要求已有账本；首次建账必须显式credit，拼错路径不能重置。所有失败和重试计入原180分钟账本。

### 错误与修正记录

首次两个真实运行的训练/推理已成功，但新增验收工具误用了float64全量归约，随后又误读新结果清单中的mse；原指标为float32逐样本归约，新mse在post报告。复用已有check_arrays独立复算标准并显式交接sample_mse后通过；失败目录保留，未改数值定义或旧基线。

首次回归使用主环境解释器，复制worker缺pytorch_wavelets导致3项失败；切到已有WDNO隔离解释器及同一安装集合后49项通过。最终含独立Agent及真实分阶段交付的完整轮51通过、1项目录断言失败：并行公共架构已移除aero_cfd/task-entry.json。更新盘点断言为现行WDNO config/pipeline后5项文档复验通过，固定公开接口基线未修改。

### 最终范围与预算

**55个唯一圈定用例最终通过、0失败、0跳过**；不是声称单轮55全部通过。JUnit为`final-tests.xml`、`final-docs-tests.xml`、`final-stop-tests.xml`及`final-real-stop-tests.xml`，逐用例最终状态见delivery.json；ruff检查和11文件格式检查通过。测试包括WDNO task/recipe/extensions/agent/budget/audit/metrics/reference协议、公共API基线、公共recipe约定和文档。未跑全仓，其他模型数学本轮未改变。

原账本累计 **6591.8056秒，即109.8634分钟**，新增 **3.0953分钟**，全部收尾，仍在180分钟上限内。独立Agent自身两次监督计算合计8.6144秒，包含在总账本中。当前完整论文阶段仍缺高分真值、准确名单、论文/脚本参数和选点闭合，以及额外资源；超分、控制、Smoke和其他论文系统未实施。正式8000/5173未操作，Web冒烟不适用。

收尾补充：Task worker独立于预算父进程的会话，验证工具wait_task在中断或等待超时时调用公开stop_run并确认终态。两项中断分支、同一分阶段训练回归及真实Task延迟worker超时停止通过；未改变包内执行策略。该有限停止验收不宣称任意忽略终止信号的外部程序均可被公共Task接口强杀。

## 2026-09-17：按用户请求再次新建 Task 复测

本轮没有改算法、Task 或 recipe。复用 `task-stages-20260917/installed` 与隔离解释器，复制当前 recipe/公开扩展，另建项目和任务 `f2f89fdddc0b49b48a1c95ffd68e4045`。原数据 8/2/2 完整轨迹，六次独立 rawprep/trainprep/train/infer/post/resume 均成功；2→3 更新、双入口完整训练状态一致、预测最大差 0、固定 post 无模型成功且数组未变，三个缺输入负向运行按预期失败，版本仍为 1。

新产物专项 `test_current_original_data_staged_delivery` 1 passed、0 failed、0 skipped。新增计算和测试 21.6660 秒，原账本累计 110.2245 分钟，无运行中记录。报告及六份运行身份、安装路径、当前复制源码摘要、JUnit见 [task-recheck REPORT](/Users/zonghui/work/project_simulation/dojo_train/wdno/task-recheck-20260917/REPORT.md) 和同目录 delivery.json。仅 Python Task 基础预测工程复测，未重训论文预算、未验 Web、未改主环境或正式服务。

## 2026-09-17：现行协议收尾——三入口、完整指标依赖与公开恢复

本次代码适配已完成。实际使用入口为 `/Users/zonghui/work/project_simulation/dojo_train/wdno/protocol-update-20260917/installed`，配合既有 `wdno/environment/bin/python`；四包wheel、实际导入路径、源码摘要、任务身份和逐用例状态见[交付报告](/Users/zonghui/work/project_simulation/dojo_train/wdno/protocol-update-20260917/REPORT.md)及同目录 `delivery.json`。历史安装与产物保留，主环境未sync或重装。

- **实际缺陷与修复：** 原WDNO指标只登记manifest；修改预测数组后仍显示available。`before-fix.xml`保留修复前1项失败；现在贡献应用同时登记清单和所有数组依赖，缺失、修改和越界路径会被发现。完整性与可比性分开：只改预测并重新生成结果仍可比较；真值/样本身份、单位、统计或定义不同不可比较。数学计算及公共接口未改变；旧索引不回写，需要此保障时从旧固定结果新建post运行。
- **三个真实来源：** recipe、基础example、扩展分别复制其实际文件，各用原数据8/2/2完整轨迹，新建Task逐次执行rawprep/trainprep/train/infer/post/续训。CPU dim8、batch2、DDIM2、2→3更新，两入口完整训练状态一致、预测最大差0；固定post无需网络且不改变数组，缺输入拒绝，版本始终1。任务ID依次为 `4a360f51b1104ecb9690ba147c922246`、`0746db160fc34da69b8ef8b5dfb5515e`、`15a7d852ee444f0f9b24dfcade31c52a`；详细六次运行收据在各 `staged/acceptance.json`。
- **复制与公开恢复：** example另从指定运行fork，明确绑定复制出的物理数组/准备/权重；临时隐藏仅本次生产运行的原数据和权重位置后仍训练预测成功，状态相同，篡改复制数组拒绝且恢复原件。Python与CLI分别新建任务、提交训练、在2步中断并恢复到冻结目标3步，完整状态与不中断一致。最终回归还核对恢复来源、保存配置不变和版本不增加。实数据证据在 `example/staged/management.json`，停止信号只注入验收副本。
- **历史兼容：** 本轮重新执行旧installed-final与当前安装对历史2000步检查点各续训1步；2001步完整状态/合同一致，验证/测试各16条预测最大差0。见 `historical/acceptance.json`；不改旧报告、不重训整个2000步、不替代论文基准。
- **使用与变体：** README给出可执行的完整配置脚本；文档测试在仓库外实际执行，并经直接/Task两入口修改参数、替换网络/损失、插入能量检查且读回固定数组。已有独立Agent现场证据保留原范围，本轮没有重新派发Agent。

最终相关回归 **90个唯一用例通过、0失败、0跳过**，由 `execution-tests.xml` 的51项和 `contracts-tests.xml` 的40项去重得到；重复恢复用例以后一次为准。执行组明确取消选择1个旧交付目录断言，本轮历史兼容已由上述真实新旧安装实跑独立证明。`focused.xml`是开发中间验证，不重复计数；修复前失败保留但不算最终失败。8个修改Python文件的ruff与格式检查通过。未跑全仓，固定公开基线未修改。

原180分钟账本仍是 `burgers-local-v1-20260917/budget.json`，本轮起点110.932575分钟；最终累计及全部监督记录状态在本节收尾和delivery.json固定。工程MSE不作精度结论：基础模板/案例测试14.530466，扩展13.855388，均为小网络2步采样；历史正式网络原成绩不改写。论文精度、超分、控制、Smoke及完整论文协议闭合不在本次交付。无Web消费链，正式8000/5173未操作，Web验收不适用。

收尾确认：文档更新后5项复查通过，仍为90个唯一最终通过用例。原账本累计 **7031.5161秒（117.1919分钟）**，本轮新增 **6.2594分钟**，距180分钟上限剩余 **62.8081分钟**；无运行中账本记录，未遗留本轮WDNO worker。四包安装Python文件与本次源码逐个一致，16份WDNO数值文件与前次安装一致，完整状态与证据路径已核验。
