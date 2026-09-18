# 共享训练执行与研究导航验收

状态：core/contrib 正式发布完成；实际页面开训、实时监控、停止、评估、推理及固定结果读回通过。停止权重恢复候选已修复并测试，追加 task 发布待授权；页面固定目标恢复仍未完成。计划见 [实施计划](../../.cursor/plans/training-execution-and-research-navigation.plan.md)。本轮保持两个核心方向，不重开论文级训练。

## 本轮实现

- loop 与 iterations 共用内部 execution 推进；轮次外层恢复/观察与各模型原优化器、EMA、调度顺序保留。默认调用不需要重新组装 abilities。
- 迭代可选局部更新、累积 mean/sum、缩放器和真实轮次边界；预算只计有效更新，不足尾组不计算目标，跳步不推进调度/EMA。累积、精度、有限轮次边界进入恢复合同；具体回调身份由领域调用方声明。
- WDNO 可选优化器、调度器和更新函数，默认科学合同不变。显式策略源码变化拒绝完整恢复；固定权重推理与 post 不导入训练策略。
- 新增本地 AB-UPT SiLU 部件覆盖集、WDNO 策略函数与可执行配置脚本。局部 SOURCE/describe 区分部件身份；余弦调度恢复保持原总目标。
- 新增四任务导航和薄研究 skill；索引输出声明签名/位置。架构、相关功能 PRD、规则、模块索引同步；根 AGENTS 原历史进度原文移到 history 并保留链接。

生产代码只改共享训练、迭代装配、WDNO局部注入及其模板连接。未批量修改已有 Recipe/Example；WDNO扩展是覆盖文件集，没有重复新建 train.py；其它原调用方继续按原接口运行。optimization.update 直接复用，未改原算术。固定公开基线文件未改。

## 实验与安装来源

所有证据位于 `/Users/zonghui/work/project_simulation/dojo_train/training_execution/20260917-implementation/`。

- baseline/ 保存改前 core/contrib；baseline-entries.json 是当时17个完整目录。后续盘点扩展至28个含配置目录，区分完整模板与覆盖集。
- source/ 只供源码测试。主环境缺EMA依赖的收集失败和错误pytest解释器尝试保留在原JUnit中；后续用已有WDNO隔离解释器的 `uv run --no-sync python -m pytest`，没有为了测试sync主环境。
- release/final-installed/ 是真实四包wheel安装副本；release/final-manifest.json 证明 core/contrib 安装与当前源码逐文件一致。
- WDNO所有本轮数值与原数据验收继续计入原180分钟账本；最后记录累计124.2919分钟，剩余以原budget.json实时值为准，不新建/重置账本。

## 圈定汇总

按 test-summary.json 对最终用例去重并以定向复跑覆盖先前失败：256项通过、0项未解决失败、3项跳过。跳过项是旧专用目录的历史WDNO交付检查（本轮另有真实历史恢复/预测对照）及两个未启用的真实换模页面用例。另有2项浏览器契约测试通过；28入口配置核验、冻结数值对照和原数据工具单独记录，不混算为pytest用例。

## 数值、恢复与代表性调用证据

- baseline-core.xml：42项改前训练基线通过。
- comparison-final.json：改前/本轮的轮次与更新路线各6次有效更新，逐步权重、优化器、EMA、调度、损失及保存事件逐值一致；轮次含累积与尾批。
- callers-final.xml：78项全部通过。覆盖共享执行11项、原轮次/恢复/中断/优化/在线窗口、训练观察、五个外流数据集/模型分支的冻结源码与恢复对照、Transolver直接/Task、字段/采样扩展、GenCP原数据真实安装与逐场替换、SafeDiffCon打包/Task阶段连接。
- numeric-models.xml：49项全部通过，覆盖WDNO数值/流恢复、SafeDiffCon预训练和后训练集成、GenCP原参考。未重新验收论文精度。
- callers-v2.xml：13项通过，覆盖PI-BSNet逐实例/整轮路线及现行推理交接、跨模型与导航。
- block-final.xml：2项通过。真实AB-UPT激活变化、参数更新、旧缓存失效、仓库外安装副本完整推理/post与同计划中间检查点恢复。
- strategy-final.xml：1项通过。实际执行configure_variant.py并消费其网络/损失/训练策略组合；2→3恢复和连续3步完整状态相等，推理和post在优化器函数不可导入时仍读固定权重/结果。
- installation-v2.xml：24项通过、2项环境入口未设置跳过。当前原数据跳过项随后由以下新实跑及3份 real-*-checked.xml 各1项通过补验；历史任务专用旧目录测试未冒用新目录，改由historical本轮直接对照提供证据。

缩放器溢出使用可控协议测试，不声称完成CUDA混合精度硬件验收。新接口仅覆盖已验证的单优化器/无额外持久策略状态；不宣称自动支持分布式、多优化器或任意闭包。

## 原数据、历史检查点与固定结果

- real-recipe/、real-example/、real-extension/：各从原始来源选择8/2/2条完整轨迹，经隔离安装后独立新建Task，分次完成处理、准备、训练、推理、post、2→3续训；直接/Task完整状态与预测逐值一致，版本数保持1，缺输入明确失败，禁用模型后的post不改变预测。每项有acceptance.json与summaries.json，后者与实际Task运行记录再次核对。
- historical/acceptance.json：历史2000步权重经旧/新隔离包各继续一步，模型、优化器、EMA、调度、数据流、随机状态、历史和合同逐值一致；validation/test各16条预测最大差0。
- 新实跑没有改写历史输入、检查点或报告。失败重试均保留，均计入原账本。

## 入口覆盖与研究使用

entries-checked.json 实际加载全部28个配置并导入选中组件；entry-coverage.json 将每个目录映射到代表性数值证据。轻量检查只证明配置/导入，不冒充每个覆盖集都独立完整训练；共用调用链按训练语义分组验证。

research-use.json 记录实际修改面：部件只新增variants.py并选择components.model；训练策略只新增variant_training.py并选择需要的键；整网/损失/审计复用已有覆盖集。两类新变体复制框架训练循环的代码均为0行。没有整理前相同任务的独立耗时基线，也没有独立Agent计时，因此不报告提速百分比或声称已量化Agent速度。

documents-final.xml中11项导航/文档检查通过。薄技能通过官方quick_validate；导航、源码签名/链接与固定公开API由圈定测试验证。source-index.json为本次索引产物，不另建功能正文。

## 失败与修正

- 新策略初次安装推理失败：训练来源合同混入固定预测比较；现已只从预测身份排除新增strategies，模型/数据/目标/原数值身份仍严格校验。安装复跑通过。
- 新部件初次恢复失败：测试把余弦总目标从1轮改2轮；按同一2轮计划捕获第1轮完整状态后恢复，逐值对照通过。同时为本地部件补科学身份，未放宽框架恢复合同。
- 7项原测试加1项观察测试使用迁移前路径或跳过现行独立推理。legacy-test-baseline.xml、observation-baseline.xml均在冻结改前源码复现。只改测试的公开输入/阶段交接，保留训练与结果断言，后续通过。
- 平台另3项旧测试：名单仍少体场案例、读取退役task-entry、迁移仍强求通用模板。按现行用户约定，选对应模型案例保留领域流程；只修正测试，未改server/task生产代码。
- 初次收集、失败JUnit和重试目录保留，汇总按最终用例去重，不把失败尝试重复计为通过。

## 平台与正式发布

运行监控execution-monitor浏览器2项契约用例通过，覆盖曲线、在线分项/测试评估和日志交互；它们使用模拟接口，不能替代正式训练。navigation-web-final.xml：80项通过、3项旧测试失败、2项真实换模环境用例跳过。3项失败已在改前源码复现于platform-baseline.xml、platform-migration-baseline.xml；更新测试的五案例名单、公共阶段输入与对应模型案例迁移断言，前两项复跑见platform-corrections.xml，迁移及用户脚本保护2项通过，见platform-migration-final.xml。未通过修改生产迁移逻辑来迎合测试。跳过的真实换模页面交接尚未重验；五分支Python短训/恢复不冒充该页面证据。

首次申请发布前未重装或重启正式服务。release/before.json记录安装路径和当时8000/5173进程：主环境由其它工作更新过，捕获时core仍有iteration_training差异、contrib仍有3处WDNO差异，不能只凭版本号断言正式运行的是本轮最终代码。发布前须重新核对活动任务和摘要，避免覆盖并行修改。

release/已准备安装副本、逐文件摘要、依赖快照、原安装备份及可校验回退wheel，发布/回退操作见release/README.md。取得当次明确授权后按根AGENTS规定更新core/contrib并重启8000，再由Agent经实际5173→8000验证开训、停止、固定目标恢复、进行中曲线/在线分项/评估、日志、检查点和固定结果读回，保存截图及数值证据。该段记录首次申请发布时的状态；后续授权、发布和页面实测如下。


## 正式页面补验进行中（2026-09-17）

用户已明确授权更新 core/contrib 并重启 8000。formal-release/ 保留当次安装备份、摘要与进程记录，5173 未重启；验收独立项目 32cdee6900924df096838663a4a70a05、任务 beab7b5ab1414787b8cc6a288e6db0cc，不改原用户任务。两条真实 CFD 样本，训练/测试各1条，CPU小模型，只验工程交接。

实际页面发现并修正更新日志冲刷导致轮次在线分项丢失：轮次报告独立累计完整统计；更新算术不变。online-before.xml 中3个失败保留，online-final.xml 44项通过。修正后的正式运行已经展示进行中曲线、在线分项、日志和资源；实际停止保存第315轮检查点。完整1000轮连续基线 e9fbb4bed19e44eeb6b5dd349355b1d8；停止运行7f80018e2eb64953a463eb663628b3ad。

发现Task候选仅列成功运行，停止权重未进入恢复下拉框。已修正为终止正式运行只开放公开索引完整提交的恢复权重，其他产物、试跑、未登记残留不可选；resume-catalog.xml 7项通过。追加 task 正式安装授权已申请，尚未发布该修正；固定315→1000页面恢复仍待验收。


正式页面补验新增：e14ce7954df441dfb323cb931fe6428b 从训练设置开启测试评估并训练2轮，运行页展示两项在线分量与六项测试指标。页面选 best.pt 后提交推理批次 f0213b8b9670445697b456d5a2a4ca98，单测试样本成功；这是每域16锚点预测，不是全点或论文精度验收。页面CSV下载读回与固定数组独立NumPy重算相符（1e-12容差），后处理评价3507f56e63ff48cba1289d8652842788读取同一固定结果，两物理量四指标一致；推理运行数与任务版本数仍各1。证据：formal-release/{training-live,training-stopped,training-evaluation,inference-results,post-fixed-results}.png、对应AX、evaluation-metrics.json、inference-export.csv、post-metrics.json及fixed-result-check.json。

本轮新增4项在线报告测试、5项恢复候选测试；分别包含在44项训练回归和7项候选/HTTP回归内，不与前轮256项简单相加。尚未完成的是停止315轮→固定目标1000轮的实际页面恢复及与连续1000轮数值对照；不以隔离回归或推理页能看见停止权重替代训练页恢复。未改既有用户项目/任务配置。

## 训练结束写出正式发布（2026-09-18）

正式开训 run `e13ba20504e34296a5fd395d1ac4a973` 在第 1 轮后失败：现行 version=2 准备已被绑定，但 `export.py` 误走旧物理准备接口。源码已改为只消费 `trainprep.preparation` 并复用独立推理锚点保存。2026-09-18 08:41 按当次授权执行 `uv sync --group dev --group visualization --reinstall-package ai4e-core`，只重启 8000（PID 33633 → **34128**），5173 仍为 23629。安装副本 `export.py` 摘要 `2159f6d4bd0093b5` 与源码一致。

正式 `5173→8000` 对照任务 `beab7b5ab1414787b8cc6a288e6db0cc` 训练设置页确认「写出预测」勾选、准备 `shapenet_car2`，点「开始训练」。新 run `b3d788acfa8a4392bb355229ff3647c9` 成功：第 1 轮更新完成，日志无旧物理准备报错，网格按用户关闭跳过并写明 `param1/1dc757e77f3cfad0253c03b7df20edd5`，`artifacts/physical-predictions.json` 状态 succeeded。证据 `/Users/zonghui/work/project_simulation/dojo_train/training_execution/20260918-export-official/`。停止权重恢复候选的 task 发布与 315→1000 页面恢复仍未验收。
