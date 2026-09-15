## Neumann / Advection Dojo原代码迁移（2026-09-14，完整预算验收通过）

用户确认以复现原代码训练路径、精度接近论文为目标；不再以标准物理导数修正作为前置条件。Neumann固定原整轮求和后一次反传，Advection固定原首行插值、参数导数及MSELoss。五案例中梯形仍为已选10实例方案；另外两例切回原代码涉及Burgers正负对流/MSE冲突，已向用户明确询问范围，未擅自覆盖。

本轮根 `/Users/zonghui/work/project_simulation/dojo_train/pibsnet/source_dojo_2026-09-14/`。独立新生成Neumann50/10、Advection100/30，所有训练/测试标签、参数及初权重均与原完整基线逐值一致。原函数在当前Dojo环境完整预算执行结束：Neumann0.01881386627、Advection0.10427001952；与旧Python3.9环境Neumann0.01875176621略不同，不调参追末位。实际Dojo完整预算及独立post已完成：Neumann5000轮/5000更新，相对L2=0.01881386627241883；Advection2000轮/200000更新，相对L2=0.10427001951814978。与同环境独立原函数的全部最终权重、5000/2000条轮次损失和10/30个完整测试场逐值一致，最大差异0。论文对应均值为0.01932和0.1444（后者报告±0.1352）；这些是相对误差而非场量。

新增模型文件source_cases/neumann_numerics/advection_numerics；数据生成不依赖模型。通用物理方程库及SciPy物理样条工具保留，但不是这两个原案例的训练目标。导数键使用parameter_前缀；默认原条件执行，非支持条件/离网采样拒绝。旧数据协议、准备及检查点不能续用。共用component源码摘要改变时其他历史准备需使用旧源快照，不能冒用新来源。

工具 `tools/verification/pibsnet/source_dojo.py` 按数据/初始化/矩阵/损失/梯度/完整训练/独立post逐层验证；真实wheel安装复制模板覆盖Neumann用户step、Advection默认step和梯形。最终圈定75项测试全部通过，无跳过（source-dojo-final-tests.log）；覆盖源行为、完整产物、训练、准备/恢复、生成、物理样条独立能力、真实wheel外部复制、模型/数值/协议、检查点、损失和文档。完整产物验收显式设置DOJO_SOURCE_ALIGNMENT_ROOT。报告：source_dojo_2026-09-14/reports/迁移验收报告.md、HTML、verification.json及fields.png。122项功能表已同步其中65–86项；原版保存在evidence_before_migration。公共epoch_sum算术顺序修正也影响对流扩散，不能沿用旧精度声称新默认已验收。

## Neumann / Advection 迁移前六组实验（2026-09-14，完整预算完成）

用户批准全部测试后再决定迁移。实验根 `/Users/zonghui/work/project_simulation/dojo_train/pibsnet/neumann_advection_trials_2026-09-14/`；`protocol.json` 冻结六组、来源摘要和解释。Neumann四组为原/标准物理导数 × 整轮/逐实例更新，5000轮，对应5000/250000更新；Advection两组保留首行插值，原/物理导数各2000轮/200000更新。全部原数据生成、初始化顺序、Adam .001、权重、名单和测试逻辑保持；Python3.9/NumPy1.26/Torch2.8，CPU单线程，与旧原基线环境一致。标准物理组同时使用标准值基与单侧端点，不能称为仅缩放；论文式12阶数记号仍披露未决。本轮不改Dojo数值组件。

六组完整预算和100份测试预测已重新读回核验。Neumann 原导数整轮0.0187517662、物理导数整轮0.9423786994、原导数逐实例0.0193013447、物理导数逐实例0.8397489648；Advection原导数0.1042700195、物理导数0.3364399931。论文对应0.01932及0.1444±0.1352。每组数据与初权重均与锁定原基线逐值一致；两组原代码的最终权重与全部预测也逐值一致（最大差0）。六组无失败、预算未缩小、没有选中途检查点。独立源训练环境Python3.9/NumPy1.26/Torch2.8；报告在Dojo工具环境FP64重算，不改变训练。

Neumann换标准物理导数后沿用原权重会显著改变目标尺度；两种更新方式均未恢复精度。物理整轮/逐实例预测场范数仅为真值0.0991/0.1761。Advection同样保留原初值插值时物理组仍偏差，不能将其归因于旧Dojo lifting。原导数组接近论文并不证明源码导数数学正确，Neumann逐实例误差最接近也不证明作者实际使用逐实例更新。

交付 `reports/六组独立验证报告.md`、同名HTML、relative-l2.png、verified_evidence.json。数学一二阶/更新范围/来源漂移/未完成报告拒绝5项与相关文档3项共8项通过，无skip，圈定ruff通过。正式报告门禁真实核对逐轮日志、更新、检查点、数据、初权重、每个预测/真值及重算指标；科学图已目视检查。HTML仅静态产物，不声明浏览器验收。本轮没有修改Dojo数值组件或案例配置。

# PI-BSNet 接入验收（实施中）

## 梯形十实例迁入Dojo（2026-09-14，完整训练等价性通过）

本轮按用户选定主文10实例实验替换Dojo唯一梯形实现，不提供双版本开关。数据由contrib独立生成，完整输出头/初始控制平面/边界覆盖/参数空间样条/近似残差由contrib模型执行；core继续装配原rawprep→trainprep→train→独立post。Neumann/Advection只核查，没有改算法、配置或重训，逐项说明在 `docs/pibsnet/Neumann与Advection输入核查.md`。

正式资产根：`/Users/zonghui/work/project_simulation/dojo_train/pibsnet/trapezoid_dojo_10/`。

- 10个训练实例、10个测试实例；21×21空间网格、1001时间点；100×20×20控制网格、degree3、隐藏64、CPU/FP32/单计算线程；3000轮、30000次更新；Adam .001，PDE/数据权重0.001/1。保留原连续MT19937流，训练后消耗原单例演示抽样，再生成正式测试名单。所有训练标签/时间坐标与原实验逐值一致；初始权重逐值一致。
- 真实Dojo训练及独立post完成：逐时间空间相对L2再平均为 **0.005404546049**；跨时间/实例标准差 **0.003786410995**。整体时空相对L2 **0.005423066436**，分开命名。此前独立旧环境为 **0.003053496246**，论文为 **0.003172±0.001580**；不能声明当前环境复现了旧数值。
- 为定位上述差异，同一Dojo环境独立运行锁定原函数，同初权重/数据/预算，原函数同样得到 **0.005404546049**。全部最终权重、3000轮损失记录、十个完整预测场逐值一致，最大差异均 **0**。这证明本次迁移的完整训练等价性；不同环境数值轨迹仍未拆分到具体库/算子原因，未调参或擅自变更依赖版本。
- 当前环境Python3.12.14/NumPy2.5.3/Torch2.14.0；旧独立环境Python3.9.25/NumPy1.26.4/Torch2.8.0。同旧检查点的完整前向最大误差3.576e-7，跨环境重新训练最大场差0.01801945。Dojo训练阶段1224.634秒，同环境原函数对照约228.717秒（包含部分评价，未含Dojo逐轮保存/读盘）；不能用此计时直接判断算法加速。

主证据：`verification.json`、`preflight.json`、`接入验证报告.md`、`same_environment_reference/result.json`及双方真实检查点/历史/完整数组。验证工具 `tools/verification/pibsnet/trapezoid_dojo.py` 和 `trapezoid_environment.py`；后者只在验证目录执行原函数，不是第二套Dojo模型。测试实际重读双方数组和权重，没有仅相信报告中的零差异字段。

圈定测试：原生成、数值、模型、训练、准备、物理参考、参考协议、文档、实际wheel复制安装合计44节点；新增完整预算拒绝与真实完整产物2节点，总计46节点通过，无skip。命令为 `uv run --no-sync pytest tests/integration/test_pibsnet_trapezoid_alignment.py tests/integration/test_pibsnet_generation.py tests/integration/test_pibsnet_training.py tests/integration/test_pibsnet_numerics.py tests/integration/test_pi_preparation.py tests/integration/test_pibsnet_model.py tests/integration/test_pibsnet_physical_reference.py tests/integration/test_pibsnet_reference_protocol.py tests/integration/test_pibsnet_documents.py tests/integration/test_pibsnet_installation.py`；完整产物圈定 `test_pibsnet_trapezoid_acceptance.py`，显式设置 `DOJO_TRAPEZOID_ACCEPTANCE_ROOT` 为上述根目录。未提供此目录的skip不代表完整验收。修改文件ruff检查通过。

迁移边界：保留原Euler近似空间算子和参数导数，尚未解决论文完整映射/导数公式冲突。旧完整映射梯形数据、准备和检查点不能直接续用；共享组件源身份变化时其他案例历史准备也须用旧源码快照消费，不能静默冒用新来源。新点集目前限网格子集；特殊条件、离网采样明确拒绝。原10次均有效的测试名单固定重放，不实现按预测误差凑足10次的筛选。

122项MD/XLSX只更新97–110条；原四个对照页及其他108条内容、窗格保留，全部122项MD/XLSX一致，变更区域已渲染检查。修改前实施映射副本保存在上述根目录 `evidence_before_migration/`。源数据/旧报告不覆盖。预检曾因工具漏写预测文件test-前缀在训练前失败，修复后复用已完整新数据继续逐值检查；归约展平引起的loss差异经修复后单步全梯度一致，原事实已记error.log。

## 论文参数三组验证（2026-09-14，完整预算完成）

用户后续选择保留梯形主文10实例组作为后续研究参考（2026-09-14）；原10/50实例及Burgers资产均保留，未改写历史证据，未自动修改Dojo默认算法或将数值接近升级为完整论文复现。

三维热方程新增核查（论文F.2，第41—43页）：2026-09-14只读查询官方GitHub，main仍为40ffb6239d865b6b7a16538559939a990e6d9cd5，唯一公开分支main，无标签，完整目录树没有三维案例；本地七个脚本及Notebook代码单元同样未发现对应入口。论文明确D=0.1、三空间轴及时间均[0,1]、四个随机线性初值参数、x3两端固定值1及x1/x2两端零梯度；每轴15控制点、21采样点，先监督学习初始控制面，再通过带残差连接的约5万参数网络顺序学习后续时间。论文所报0.0032为测试平均PDE残差，不是相对L2。训练/测试实例数、每阶段预算、确切网络结构、案例样条次数、损失权重及平均残差具体归约均未充分给出。当前无法锁定唯一可执行复现协议，未自行补值训练；需要对应源码/完整配置补足。官方来源：https://github.com/jacobwang925/PI-BSNet ，目录树和分支通过GitHub API即时核验。

用户明确批准先做参数差异验证并保留未决项：Burgers 正对流与 MSE（5000轮/500000次更新），梯形10实例与50实例（均3000轮，对应30000/150000次更新），控制网格100×20×20、PDE权重0.001。原数据求解器、样条、初边界和测试流程沿用。Burgers相同种子下数据名单应与原基线一致；梯形改变训练实例数后原随机流的测试名单会变化，不能把两组误差差异全部归因于训练数量。

实际运行根：`/Users/zonghui/work/project_simulation/dojo_train/pibsnet/paper_parameter_trials_2026-09-14_run2/`。`protocol.json`冻结来源与未决项，`source/`保存原始代码、执行器及修改记录，各组保存数据、权重、完整预测和日志。首次目录`paper_parameter_trials_2026-09-14/`保留训练前环境启动失败：解释器resolve绕过虚拟环境，报缺NumPy；修复入口后新目录重启，不改任何数值设置。

源码与损失门禁、原指标两种聚合、现有文档用例共7项通过，圈定ruff通过。三组完整预算、逐轮日志、源函数定义、全部42份预测与重算指标通过；Burgers的数据和初始权重与原基线逐值一致。梯形启动前补齐原执行器遗漏的每轮avg_loss记录，差异与前后摘要保存在`source/epoch_logging_amendment.json`，没有修改数值计算。

重算平均相对L2：Burgers=0.1045891868（论文0.07294，+43.39%；原基线0.1034558495），梯形10=0.003053496246（论文0.003172，-3.74%），梯形50=0.002375722044（-25.10%）。两组梯形均10次评价全部有效，另各保存单例预测。梯形误差低于原基线0.004961557849，但测试名单随训练数量改变，不能单独归因于实例数。Burgers两项损失修改没有改善精度，不继续擅自调参。

交付：[Markdown报告](/Users/zonghui/work/project_simulation/dojo_train/pibsnet/paper_parameter_trials_2026-09-14_run2/reports/论文参数三组验证报告.md)、[HTML报告](/Users/zonghui/work/project_simulation/dojo_train/pibsnet/paper_parameter_trials_2026-09-14_run2/reports/论文参数三组验证报告.html)；`reports/verified_evidence.json`保存数据、检查点摘要和预测重算。已检查报告文件和科学图片；浏览器安全策略阻止本地HTML导航，未完成浏览器显示验收。实验执行完成不等于完整论文算法复现，未决项继续保留。

## 原仓库独立基线（2026-09-14，全预算已完成）

用户要求先独立运行原仓库，再决定Dojo修正。五例使用锁定提交`40ffb6239d865b6b7a16538559939a990e6d9cd5`的原数据生成、模型和训练代码；未使用共享修正数据、未覆盖论文参数、未修改Dojo算法。仅调整输出路径、跳过其他基线训练和非必要绘图/拟合单元、明确重新训练，并增加产物记录；执行差异和源码副本逐文件保存。

环境为原仓库Python3.9.25、NumPy1.26.4、SciPy1.13.1、PyTorch2.8.0；Shapely2.0.7隔离安装。CPU/FP32/单计算线程；原种子沿用，未声明时设42。不是论文RTX4090环境或多次独立运行统计。

五例完整更新次数为CD5000、Neumann5000、Advection200000、Burgers500000、梯形60000。原评价平均相对L2依次为0.0108717526、0.0187517664、0.1042700186、0.1034558495、0.00496155785。梯形使用20训练实例、1001×21×21控制网格和1e-5物理权重；随机评价10次全部有效，另保存单例测试。其指标按时间片先求空间相对L2再汇总，与其他案例的整场口径分开说明。

交付根：`/Users/zonghui/work/project_simulation/dojo_train/pibsnet/original_baseline/`。

- [原仓库五案例HTML报告](/Users/zonghui/work/project_simulation/dojo_train/pibsnet/original_baseline/reports/原仓库五案例基线报告.html)与同名Markdown：原设置、论文对应、结果和五张预测图。
- `reports/verified_evidence.json`：72份预测数组的形状/有限性、原指标重算、数据和检查点摘要，以及包含嵌套函数的源码AST一致性检查；五例预算均通过。
- `source/run_original.py`、各例`logs/*.patch`：运行入口和允许调整；`batch.json`记录五例退出码均为0。

该基线是原仓库实验完成的证据，不代表Dojo已完成原算法等价修正，也不代表全部论文实验已复现。原仓库与论文的冲突仍需用户逐项确认。下文paper_v3为此前Dojo修订实现实验，不能与本次原基线混称。

更新于2026-09-13。用户要求严格按原文献参数验证，不以调参消除精度失败。五例完整预算训练、独立参考及报告已完成，但精度复现未通过，不能声明完整计划验收通过。

## 已实现与已执行

- contrib 五个独立生成器已产生五个逻辑数据集，共411实例：CD 40/1、Neumann 50/10、Advection 100/30、Burgers 100/20、梯形50/10（训练/测试）。梯形当前使用 datasets_paper；旧20/10数据保留。
- 普通张量方程函数覆盖 Burgers、Advection、扩散、对流扩散和二维 NS。core 提供物理域、法向、采样、标准条件、准备交接；唯一 PI-BSNet 组件负责样条重建与导数。
- 独立 generate → rawprep → trainprep → train → post、恢复、用户训练函数与完整测试预测已实现。实际 wheel 安装后，从仓外复制模板运行用户组件的短训链路通过。
- 圈定71项通过，证据 validation/paper-current.xml；后续纠正额外条件权重的18项通过，证据 validation/objective-v3.xml；当前安装/文档/原生协议10项通过，证据 validation/final-protocol.xml。测试通过不代表论文精度通过。
- 导数实验已保存完整数组、五种导数指标和图像；采用源码121²网格、20²控制点、四次样条，属于源码拟合实验，不等同于论文 Appendix E 的随机控制点15²/100²实验。

## 文献优先与协议修正

锁定来源提交40ffb6239d865b6b7a16538559939a990e6d9cd5；论文为 arXiv 2503.16777v3，HTML和文本保存在 source/，摘要见模型 source.json。

- 梯形按 Appendix D.3：50个训练实例、控制网格[t,eta,xi]=[100,20,20]、degree3、hidden64、Adam .001、3000轮、PDE权重.001、数据权重1。原 notebook 的20实例、[1001,21,21]、1e-5不作为文献参数。真值用完整物理变换；训练用文献明确选择的近似Eq.84，不把省略交叉项误称为缺陷。
- 原参考 PDE 使用完整网格，包括初始面与空间边界。此前严格内点版本为诊断；当前 include_boundary=true，改变采样后重新准备。
- 原 PI 目标仅 Neumann 包含独立初边界罚项；其他案例的初值和周期残差仍计算监测值，默认权重0，不额外加入训练。此前正权重版本保留为诊断，不作为文献参数验收。
- Neumann 40²控制点来源为锁定代码：论文HTML对应数值空缺，不能声称论文明确给出40²。
- 泛化按全部30测试实例和全部点的最大绝对误差拟合，2000轮/41次评价；不是平均相对L2。有限正值且损失不大于1才参与拟合，不足时明确失败。
- 数学改动仍需披露：物理样条导数、单侧端点、Burgers符号与不重复周期端点、梯形完整真值映射、Advection解析初值lifting、CD/梯形初值不再以首行控制系数冒称严格满足。CD自由系数600，原576。关闭额外初值罚项后，初值由数据监督和监测覆盖，不宣称与原硬条件等价。

## Neumann 已确认精度失败

原分支5000更新平均相对L2=0.0157551；第一版严格内点Dojo=0.8777908；纠正完整网格后Dojo=0.9647427。独立原生PyTorch原循环仅换成SciPy物理导数矩阵，结果=0.9646117。

正式网格128²、控制点40²、degree5、hidden128下，各PDE/数据/初值/边界损失及全部参数梯度与独立SciPy+原生PyTorch目标核对通过。证据入口 test_pibsnet_physical_reference.py。该结果支持定位导数修正后的目标差异，不证明已经复现论文精度，也不授权更改论文超参数。

## 当前正式目标重跑

以下运行使用 prepared_paper_v3 / predictions_paper_v3，新结果不得覆盖旧记录。CPU fp32、seed42、单计算线程；状态应以运行产物为准，启动不代表完成。

- CD：convection_diffusion/runs/2026-09-11T16-43-09_7a5ad4，5000更新。
- Neumann：neumann_diffusion/runs/2026-09-11T16-43-20_086407，5000更新。
- Advection：advection/runs/2026-09-11T16-43-30_aa28a9，2000轮/200000更新。
- Burgers：burgers/runs/2026-09-11T16-43-40_7de45d，5000轮/500000更新。
- 梯形：diffusion_trapezoid/runs/2026-09-11T16-43-58_780761，3000轮/150000更新。
- 泛化：generalization/runs/2026-09-11T16-44-42_bc9919，2000轮/41次全测试评价。

16:26—16:30启动的paper_v2病例包含额外条件罚项：CD已结束（相对L2=.01376756），其余四个长期作业已停止并保留诊断检查点。早先paper_v2结果不能称全部目标对齐。

## 历史已完成对照（2026-09-11）

CD与Neumann的paper_v3完整训练、独立参考和对照已完成。CD平均相对L2=0.01939550，原分支=0.009521686；Neumann=0.96474268，原分支约0.0157551。结果与未完成案例汇总于 reports/paper_v3/report.md。对照完成不等于精度验收通过。

## 未完成验收

五案例当前目标完整预算、全部原分支独立对照和精度报告已于2026-09-13核验完成。五例平均误差均高于原分支，精度复现未通过；论文参数导数消融仍未完成，泛化拟合因合格评价点为0而失败。122项表格需要随真实最终证据更新。旧比较报告只证明其中声明的数据和预算，不证明配点、目标或数学实现全部一致。

## 路径与圈定验收

全部数据、训练、预测和验证缓存根为 /Users/zonghui/work/project_simulation/dojo_train/pibsnet/。
用户入口 recipes/parametric_pde/；五案例配置 examples/parametric_pde/；原始122项表保留于 docs/pibsnet/。

相关测试：test_pde_equations.py、test_pibsnet_generation.py、test_pibsnet_model.py、test_pibsnet_training.py、test_pi_preparation.py、test_pibsnet_physical_reference.py、test_pibsnet_experiments.py、test_pibsnet_installation.py、test_pibsnet_documents.py、test_pibsnet_numerics.py。公共训练联验 test_train_checkpoint.py、test_train_optim_align.py、test_constraint_losses.py、test_train_online_loss.py。所有 Python 检查使用 uv run。

## Neumann 初始目标尺度诊断

同一原网络随机系数、首个训练实例（nu=1.3834418205768717）下，原导数 PDE MSE=0.46928346，独立 SciPy 物理导数 PDE MSE=1101159.375；数据 MSE 两者均约0.02562222。边界平方项和从0.4696458变为1777.5471。证据 diagnostics/neumann_initial_objective.json。这是单实例初始目标诊断，不单独证明完整优化失败的唯一原因；结合全预算原生物理导数复核与梯度测试，说明修改导数后沿用原权重的尺度发生重大变化。用户未授权调参，当前保持原权重。

## 历史运行进度（2026-09-11 17:16）

Advection 已完成2000轮/200000更新及全部30测试实例，平均相对L2：Dojo=0.30085132，原分支=0.12946399。泛化完成2000轮/41次评价，评价对应训练损失最小4.118505，loss<=1的合格点为0；fit_failure_paper_v3.json记录拟合不可用，不调整阈值。CD/Neumann新进程独立post完整输出与pipeline预测最大绝对差均为0。

Burgers、梯形的Dojo与原分支仍在运行。report.py已为本批四个已启动进程串接结束后的汇总；不重启训练、不改参数，缺完整产物时仍输出partial并非零退出。当前报告 reports/paper_v3/report.md；报告完成不等于精度通过。

## 五案例最终对比报告（2026-09-13）

五例均完成上述完整预算与全部71个测试实例预测。重新以FP64从保存数组计算实例相对L2并取算术平均：对流–扩散原分支0.00952169、Dojo 0.01939550；Neumann原分支0.01575514、Dojo 0.96474202；Advection原分支0.12946399、Dojo 0.30085132；Burgers原分支0.09123585、Dojo 0.10060746；梯形原分支0.00474876、Dojo 0.00929374。末位与FP32训练记录略有不同。

原分支使用锁定原数值定义和训练分支，在共享修正物理数据上独立运行；不是论文表格值或原仓库全流程的无修改复刻。报告披露数学、初边界条件与自由参数差异，不能把同数据同预算对照称为逐元素等价证明。未调参，也未事后设置通过阈值。

交付根为 `/Users/zonghui/work/project_simulation/dojo_train/pibsnet/reports/comparison_2026-09-13/`：

- [五案例HTML报告](/Users/zonghui/work/project_simulation/dojo_train/pibsnet/reports/comparison_2026-09-13/PI-BSNet_五案例对比报告.html)：离线内嵌六图、参数与来源差异、71实例明细。
- [Markdown报告](/Users/zonghui/work/project_simulation/dojo_train/pibsnet/reports/comparison_2026-09-13/PI-BSNet_五案例对比报告.md)：同内容可编辑正文。
- `verified_metrics.json`、`protocol/`：重算指标、逐例协议、数据与检查点摘要。核验411个数据文件、5个最终检查点、双方目标一致性及全部预测形状/有限值。

HTML浏览器检查六图加载、五案例章节、无页面横向溢出与无脚本错误通过。训练耗时仅作为运行记录，非受控性能比较。泛化41次评价已完成但不产生有效拟合斜率，其失败边界已纳入报告。

五例汇总报告（2026-09-14）：`docs/pibsnet/五案例精度对照报告.md`。仅汇总既有证据；本次没有新增训练或变更算法，历史结果与当前迁移版分开标注。
