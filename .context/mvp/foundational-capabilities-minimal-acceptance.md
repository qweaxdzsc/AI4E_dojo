# 精简基础能力独立交付验收

日期：2026-09-22。下文先保留首轮独立组件验收，最新状态见文末“框架与正式扩展联合验收”。历史证据不改写。

## 已实现

- EpochBatchStream：用户函数生成有限有序记录，默认保留尾批/显式丢尾，独立 PCG64，保存轮次、记录、游标和 RNG；验证后恢复，失败保持原状态。公开 epoch/offset/epoch_end，现有迭代训练可读取边界。无数据读取、额外打乱、预取或模型逻辑。
- BestMetric：min/max 与 first/last 平局政策；improves 无副作用，writer 成功后 commit；独立政策/值/位置/来源状态，非法恢复保持当前选择。模型、科学指标、文件写入由调用方负责。
- PRD 第三章6/7项、data/training帮助与自动生成索引/API页面、core模块索引同步。Skill/Guide没有新的策略规则。

## 实际验证

- 新组件54项：70/16完整身份与尾批、丢尾、轮内/轮界/初始恢复、独立 NumPy 抽样参考、坏状态与可执行对象拒绝、无额外取样、累积不跨轮、两类任务短训梯度/参数逐值一致。
- 两类数值任务为静态数组索引与随机时间窗记录；各10次线性模型更新，对照手写独立参考；7次更新后经既有 capture_iteration/restore_iteration 继续到10，梯度及每步参数 rtol=0/atol=0一致。
- 真实 launch/TrainingRun writer：raw→EMA→raw→EMA选优，EMA由既有MovingAverage实际更新；获胜为第3位置EMA权重0.5，后续raw权重4不替代。保存失败不commit，最新恢复载荷保留此前选优权重独立快照；恢复预测逐值一致。
- 新组件、帮助及配套安装共73项通过。独立构建并安装spec/core/task三个wheel，在仓库外复跑54项行为测试；导出帮助能检索两个新符号，两个组件wheel内容摘要与当前源码一致。
- 现有test_training_execution、test_training_strategy_extensions、test_recipe_extensions共26项通过。WDNO可选依赖仅在证据目录隔离venv补齐，不同步主环境。
- 5个新增/修改源码测试文件ruff通过；帮助生成器write/check通过（494生成文件）。

## 独立阶段的首轮失败与界限（联合续接见下文）

- 初次隔离venv错误地依赖system-site-packages继承项目环境，pytest缺失；已改为显式只读第三方依赖路径，Dojo三包仍从独立安装目录导入并检查来源。三包相互配套，不以旧主环境Dojo替代。
- 既有帮助安装测试仅安装task，回退主环境旧spec，因缺task_operations失败；未修改其共享测试。该项从最终73项中明确排除，原失败在final-tests.xml保留；本次新增安装测试安装配套三wheel并真实执行相同导出/搜索路径，不能把被排除项计为通过。
- 不要求独立解析/重新安装所有第三方依赖；隔离的是Dojo安装和输出。未改变主环境、8000或5173。
- 独立交付当时未实施自动状态bindings和正式extension；该历史缺项已由下方联合验收补齐。第一计划的正式Web与Agent行为范围仍分别记录。
- 无生产精度、MPS训练或新的五轮实验声明。

## 证据

本目录的verification.json记录源码/wheel摘要与边界；delivery-tests.xml记录73项，regression-tests.xml记录26项。
delivery-runs/test_installed_foundational_ca0/installation-evidence.json保留每个构建/安装/导入/导出/行为命令及退出码；其research/和installed-test-runs/保留仓库外脚本与检查点。
tests.xml、final-tests.xml保留早期失败，不替换历史；reference-hashes.json证明原WindowStream、旧循环/检查点/固定流未修改。

证据目录：`/Users/zonghui/work/project_simulation/dojo_train/foundational-capabilities-minimal/1a594661-867c-414d-b90e-10c72efe4475`。

## 框架与正式扩展联合验收（2026-09-22续接）

本轮已接通之前未实施的可选用户状态连接和两个正式extension。它们基于 `geotransolver.darcy`，保留完整五阶段及既有公开模型、具名数组、目标、优化器、共享训练、固定infer/post；变体仅局部替换有序流/轮次调度和验证状态装配。无自写训练循环，无正式JOREK集成。

- `recipe_extensions.tail_batch`：不足整批数据正常更新，检查点恢复有序记录/游标/RNG，报告实际尾批。
- `recipe_extensions.research_state`：原训练名单留出验证后才拟合训练统计，验证raw/EMA、独立验证保存周期、BestMetric与最佳权重通过state_bindings一并恢复。latest用于恢复、best用于推理，旧best移走仍可继续。
- `test_research_extensions.py` 最终6项通过：分片不交叉，3种损坏状态预检拒绝不修改，两种正式物化链路。实际构建并隔离安装spec/core/contrib/task四个wheel，两个extension全部脚本/配置/README与wheel内资源字节一致。
- 两例均在仓库外物化，实际修改批量、替换loss组件、新增有单位/轴声明的误差数组并由post消费；direct-core与Task分别4更新、恢复到6，以及连续6更新的模型/优化器/调度/流/历史/可选EMA和用户状态逐值一致，固定预测数组逐值一致。
- research_state本次最佳为update4的raw，最终更新6，选择值0.07898537069559097仅是数值夹具结果；嵌入快照与实际best文件科学载荷逐值一致。旧best被移走后恢复仍成立。
- 两例均独立infer读回固定权重；固定结果复制后，禁止导入train/infer脚本并去掉准备/权重输入，独立post仍成功消费误差数组。
- 输入为11×11合成数值夹具，仅用于状态/流程连接：8训练来源、3测试；research再留出3验证，仅5条拟合统计；模型网格3×3、1层16宽、CPU短更新。并非真实Darcy数值复现、生产精度或新的五轮实验。

本计划之前列出的“自动状态/正式extension/Task联合验收”现已在上述受控小规模范围完成。正式服务及Agent是否因此提高工具采用率由第一计划另行验收，不由本记录代替。

联合证据：`/Users/zonghui/work/project_simulation/dojo_train/framework-skill-evolution/3cbdc67f-bb6c-4786-bcb6-2b2d3b07654f/extensions-wheel.xml`（6项），`extension-verification.json`（资源摘要与两例精确证据位置），`extensions-wheel/test_external_copy_direct_task{0,1}/acceptance.json`（direct与Task完整摘要）。源码失败轮保留为extensions-source.xml、extensions-source-v2.xml；已修复示例使用未知writer标签，以及比较时未区分writer附加effective_config与科学载荷的问题。

安装快照边界：上述extension正常链路依据 `extension-verification.json` 中四个wheel摘要与core源码摘要。主会话随后加强用户状态版本类型和失败回滚时的逐项恢复；该后续变更的最终wheel专项补验另由主会话记录，不把本快照自动视为后续代码已验。

## 主会话最终复核

主会话已在最终检查点强化后复跑：`final-joint.xml`的31项包括现有训练策略/检查点/扩展与两个新extension真实四包wheel链路；`final-state.xml`的基础安装用例重新构建配套三包并在隔离环境复跑54项；`final-docs.xml`再次核对最终框架wheel、Guide/Skill摘要及12项用户状态行为。证据均在上述框架证据根。两计划圈定用例按名称去重162项通过，原有失败XML保留。第二计划的独立及联合小规模验收已完成；第一计划亦已在用户授权后补齐正式Web现有训练消费链兼容性验收（页面启动、Task完整状态恢复、页面读回），详见[框架验收](framework-skill-evolution-acceptance.md)。
