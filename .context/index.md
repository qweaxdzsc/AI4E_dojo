# AI4E_Dojo 当前仓库索引

先读根 AGENTS，再从本页定位模块、PRD、源码、上下游和测试。架构决策进入唯一 [全局架构](../docs/AI4E_Dojo_ARCHITECTURE%20%281%29.md)，不在本索引复制架构正文。

## 当前范围

七个正式包。外流 CFD 使用 rawprep → trainprep → train → infer → post，PDE 有独立生成/训练/预测流程。六类模型代码可安装（GenCP 含 CNO/SiT-FNO，SafeDiffCon 与 WDNO 按缩小预算），Web 只开放 AB-UPT/Transolver-3 与两数据集五例。物理约束已在 PDE 使用；CAE 采样、平台批量研究和完整报告生成仍未开放。生产精度与硬件等价按各专项实际证据限定。

组件自由签名，连接负责适配；公开 run 入口和按需任务操作隔离平台内部变化。全仓现状核对、接口变更、修改测试并集与最终运行结果见 [本轮架构验收](mvp/architecture-alignment-acceptance.md)。历史数值报告保留当时范围，不作为最新源码通过记录。本机正式入口 8000/5173 由用户控制，未授权不得擅自重装/重启；有 Web 消费链时 Agent 必须自己在该入口冒烟，隔离 7999/5172 不能替代。未重装 `.venv` 安装副本则正式 Web 验收不了，「待发布」不是完成。后处理 Vis 依赖与何时才允许 `uv sync` 见根 `AGENTS.md`「注意事项」与「发布与正式 Web 冒烟验收」。

## 包与模块入口

- [研究任务导航](tasks/research.md)：训练、组 recipe、接模型、做变体的最小阅读、修改与验证路径。
- [面向 Agent 的分层架构入口](tasks/architecture.md)：按 Core、Application、Recipe、Task、Server、Web、Vis 定位职责、交接和修改边界；完整设计仍以唯一架构正文为准。
- [开发进度历史](history/development-updates-20260917.md)：根入口移出的原文，按历史范围保留。
- [共享训练执行验收](mvp/training-execution-acceptance.md)：当前源码、安装与正式入口分别记录，未验范围不推断完成。2026-09-18 正式 8000 已重装 `ai4e-core`；对照任务开训写出预测 run `b3d788ac` 成功。

- [ai4e-spec](modules/ai4e-spec.md)：标准库交接类型；components 为局部消费者约定，data 为检查描述，artifacts 为持久化与跨进程格式。
- [ai4e-core](modules/ai4e-core.md)：base 通用配置与事件；abilities 原子计算；applications 领域步骤；run 执行与唯一记录写入。
- [ai4e-contrib](modules/ai4e-contrib.md)：ability 中的模型/方程与 application 中的数据适配、模型专属配置和局部连接。
- [ai4e-task](modules/ai4e-task.md)：cli/projects/tasks/versions/templates/storage 六类功能；任务运行、版本与资产管理。
- [ai4e-server](modules/ai4e-server.md)：bootstrap 装配，infrastructure 受控存储与传输，modules 平台业务用例。
- [ai4e-web](modules/ai4e-web.md)：src 中按用户任务组织微领域；e2e 浏览器流程，scripts 架构与传输类型检查。
- [ai4e-viz](modules/ai4e-viz.md)：算法库与迁入可视化应用并存；包内 .context、PRD 和 architecture 为内部真源。
- [recipes](modules/recipes.md)：普通研究脚本、五个外流案例、五个 PDE 案例、GenCP 六组、SafeDiffCon 两个完整可复制案例、WDNO 基础预测及自由连接扩展。
- [全仓辅助目录](modules/repository.md)：examples、tools、tests、docs、构建和规则导航。
- [模型集成目标与验收原则](../docs/model-integration-goals.md)：目标与交付、必须检查节点、可选参考三部分；八项目标及效率积累方向，保留三项准入和原仓库先复现门槛，不规定统一流程或记录模板。
- [模型集成 skill](../.agents/skills/dojo-integrate-model/SKILL.md)：目标与交付、必须检查节点、可选参考；明确后续更新原则和阶段改进日志要求，方法自主选择。
- [模型集成改进日志](model-integration-learning.md)：实际错误、有效流程与待核实观察的证据及适用边界，供 skill 后续修订参考。
- [PRD 总入口](../docs/PRD/README.md)：所有正式模块功能正文；不存在平行的 `.context/prd` 功能真源。
- [全仓文件清单](mvp/architecture-alignment-results/inventory.json)：逐文件用途、声明、导入和内容摘要；结构关联不是验收结果。

训练运行实时曲线与评估（2026-09-17）：每轮覆盖训练报告；运行页分列在线分项与测试评估。圈定 `tests/integration/test_train_loop.py`、`packages/ai4e-web/e2e/execution-monitor.spec.ts`。

平台改走现行准备与模型架构（2026-09-17，2026-09-18 续）：开训、检查、跟踪、推理与训练结束写出只认 version=2 与现行训练脚本；旧官方物理包装可迁，`version=1` 准备记录须重做。现行 `version=2`（含 `physical_fields`）只判断能否导入，选中后按当前平台与 core 参数计算，不再用冻结声明比字段、规格、采样方法或模型字典。模型页采样预算不属于准备冻结：新记录不写这些点数。推理预检另比权重结构，dim/blocks 对不上仍拒绝恢复该检查点。圈定 `tests/integration/test_web_stage_consistency.py`、`tests/integration/test_algorithm_platform_contract.py`、`tests/integration/test_task_configuration.py`、`tests/integration/test_train_export.py`、`tests/integration/test_trainprep_consume.py`、`tests/integration/test_infer_inspect_contract.py`。隔离 `http://127.0.0.1:7999` / `5172` 已核对 v1 拒绝与 v2 可提交。2026-09-18 15:28–15:32 用户当次授权后重装 `ai4e-core`/`ai4e-contrib`/`ai4e-server`/`ai4e-task` 并只重启 8000（PID **48179**，5173 **23629**）；对照任务 `测试09182` 结构图、归一化目录与无官方 test 三项再过。证据 [准备导入验收](mvp/preparation-import-acceptance.md)。

训练设置开训与运行监控（2026-09-16，2026-09-18 续）：训练设置页选择已准备数据及其 train/test/eval 切片后提交开训，默认训练集；继续训练只覆盖这一轮起始权重。开训按当次平台选择合成运行配置，不夹带其他页留下的清单。训练运行属于执行监控，不再作为伪阶段去读配置。圈定 `tests/integration/test_web_stage_consistency.py`、`tests/integration/test_trainprep_split.py`、`packages/ai4e-web/e2e/stage-consistency.spec.ts`、`packages/ai4e-web/e2e/execution-monitor.spec.ts`。

训练设置预检与步骤完成态（2026-09-16，2026-09-18 续）：`aero_cfd/inspection.py` 的 train 预检不再索要准备产物；server `stages` 只在保存后记录模型/训练完成，未改参数的保存也会记下完成并盖住旧失败预检；检查或结构跟踪不能冒充或清掉。执行步以正式成功运行为准，后来的 unknown 读盘不把已成功改成未运行。刷新与跳步按后端摘要恢复绿色勾。圈定 `tests/integration/test_web_stage_consistency.py`、`packages/ai4e-web/e2e/stage-consistency.spec.ts`。

工作台切步加载（2026-09-17）：配置先出，产物列表并行补齐；登记用文件戳。列举成功运行产物时不再调用内容核验。准备处理结果认现行 `data_dir/trainprep/normalize`，历史运行回退 `data_dir/normalize`。正式 8000/5173 已于 20:46–20:54 重装 `ai4e-task`/`ai4e-viz` 并重启后冒烟：`stage-inputs` 21 条 0.18s，训练设置约 1.56s。该训练设置耗时不能当成模型页已经够快。模型设置进页先反显已保存参数；`model-options` 只出 YAML 目录，点选再 `describe_case`，同任务短时复用。圈定 `test_web_stage_consistency.py` 与 `e2e/model-picker.spec.ts`。证据见 `.context/mvp/post-workspace-acceptance.md`、`.context/mvp/model-picker-acceptance.md`。原始处理 RawprepWorkbench 已对齐同一语义：三栏与已保存配置先出，文件树/处理结果/运行名单栏内补齐，不整页等待 `listRuns`、目录检查或 `stage-inputs`；同任务复用阶段工作台的 `stage-inputs` 合并。圈定 `packages/ai4e-web/e2e/rawprep-consistency.spec.ts`。已接入数据集缺 VTKHDF 键时页面默认勾选；对照任务已把保存成关的开关改回默认开。只改 web 源码时正式 5173 读源码即可冒烟。原始处理输入是绑定数据集官方/自身分片，页面只存可见处理配置；当次执行或发布的样本名单不得写回下次输入。`samples=all` 不吃任务里看不见的 `dataset.partitions` 子集。平台提交非 NASA 案例写 `unsplit`，产物不按官方 train/test 落盘，切分只在数据准备。`unsplit` 与 `official` 一样是分片模式名，配置加载不得展开成文件路径。圈定 `test_web_rawprep.py`、`test_web_dataset_binding.py`、`test_web_rawprep_handoff.py`、`test_train_shapenet_contract.py`。正式入口冒烟见 [准备导入验收](mvp/preparation-import-acceptance.md)。

## 当前专项导航

- [共享训练执行与研究任务导航计划](../.cursor/plans/training-execution-and-research-navigation.plan.md)：实施中；现有模板最小修改、受影响入口逐个核验与语义代表实跑，当前进度及正式发布未验范围见共享训练执行验收。

- [Recipe/Task公共约定实施](mvp/recipe-task-conventions-acceptance.md)：新输入树、无额外任务描述、资产指标交接、官方同案例迁移/离线候选、自包含数组复制及安装/双入口验收；实施中。2026-09-17正式8000已按新约定重装重启；正式工作区只留首页项目与该任务，旧准备已删，平台共享 shapenet_car/2/3/4 已迁到 `inputs.trainprep.dataset`；原数据根未删。其余计划项未收口。

- [SafeDiffCon Task一致执行优化计划](../.cursor/plans/safediffcon-task-transparent-execution.plan.md)：2026-09-17现行公共约定适配实施；自包含案例、显式旧配置转换、真实双入口对照、资产与隔离安装发布，完成证据见专项验收。
- [SafeDiffCon Task补验](mvp/safediffcon-acceptance.md)：2026-09-17补模板入口；两案例真实新建与分阶段训练/推理/post、37项测试及CLI后处理通过。复用原准备数据，不重做精度验收；历史入口已被普通 pipeline 取代，当前进度见 Recipe/Task 公共约定专项。

- [SafeDiffCon 集成执行](mvp/safediffcon-acceptance.md)：模型、控制应用与可复制模板已有4000步/50样本缩小基线；本轮按[更新实施计划](../.cursor/plans/safediffcon-integration.plan.md)补独立原定义后训练/适配参考、恢复与阶段限时，已完成5000/8000步双侧续训和各50样本完整对照，模型及响应逐值一致，66项测试通过；累计104.79/57.25分钟，论文精度未达成。工程一致、学习效果与论文口径分别记录。入口 `tools/verification/safediffcon/`。

- [WDNO 现有集成补全实施方案](../.cursor/plans/wdno-reproduction-and-agent-composition.plan.md)：2026-09-17 综合当前迁移和公共Task/recipe证据重写；基础预测及Task适配已完成，本轮已完成指标数组依赖修复、三个真实入口、复制品消费及公开中断恢复；既有独立Agent证据保留，论文协议及逐例正式复现仍未完成。累计预算与最终测试见WDNO专项记录，仅代码能力。
- [WDNO 原仓库切片执行](mvp/wdno-acceptance.md)：P0/P1已完成，原Trainer正式网络2000更新、64/128固定评价，累计31.57分钟；测试MSE0.04938，独立检查点重放逐值一致，16项测试通过。P0/P1历史证据保留；当前Dojo基础迁移已完成同环境2000步权重/损失及64/128预测逐值对照，真实恢复、原权重导入和组合入口通过；最终测试/预算见该记录。
- [推理表格/图表独立草稿及固定结果](mvp/inference-result-views-acceptance.md)
- [推理工作台、字段与分片](mvp/inference-ui-acceptance.md)：现行另含进页先填一份目录再核对、检查点不一致回退、全选与过期批次不误报数据根；检查点按训练运行收成树。指标表/图表已加高，图表配置含刻度、网格线与点数值。推理配置分行排布、标题不带序号，不再锁 90px 单行。输出为「导出点云数据」「导出VTK网格化数据」，默认勾选且含真值；无 VTK 来源文件、也未绑定连接关系时网格化置灰。样本目录须带 `vtk_exports`，服务不得丢掉。2026-09-18 13:16 正式 `5173→8000` 已重装 `ai4e-spec`/`ai4e-core`/`ai4e-server` 并只重启 8000（PID **3619**）；对照任务「测试0918」两项默认可勾，样本接口带 `vtk_exports`，检查不再 422。
- [后处理结果文件与三维会话](mvp/post-workspace-acceptance.md)：后处理只留结果文件与三维两个页签，默认结果文件；旧 `tab=metrics` 落到结果文件。三维页相对原 820px 至少加高 40% 并铺满剩余视口，宿主不展示「打开已保存配置」。结果文件列平台数据集、训练 run 与推理批次；无写出时仍显示该 run 并说明没有预测/网格。空态不要求必须先推理。批次下拉用 `infer` 加创建时间。指标表/图表在推理页，不在后处理重复入口。推理默认写出 VTK（预测+真值）；用户关闭导出须写明原因，缺拓扑则该样本失败。2026-09-17 23:50 正式 5173→8000 对照五页已冒烟。
- [模型选择与结构跟踪](mvp/model-picker-acceptance.md)：2026-09-18 起含两档官方结构图；正式入口冒烟见该记录。
- [准备导入、脚本迁移与无切分原始处理](mvp/preparation-import-acceptance.md)：冻结准备只负责导入；计算与切分走当前平台。2026-09-18 正式 `5173→8000` 对照任务 `测试09182` 三项冒烟通过。
- [声明驱动原始处理](mvp/manifest-rawprep-acceptance.md)：`samples=all` 读绑定宇宙；正式 catalog 仍待重装兑现。
- [三维工作台与实际宿主](mvp/phys-workbench-acceptance.md)
- [三维工作台十一项增强](mvp/phys-workbench-acceptance.md#三维工作台十一项增强2026-09-17)
- [线段提取 Line Chart View](mvp/phys-workbench-acceptance.md#线段提取-line-chart-view2026-09-17)
- [工作台色标、Probe 与视图联动](mvp/phys-workbench-acceptance.md#工作台色标probe-与视图联动2026-09-17)
- [辅助平面轨道相机](mvp/phys-workbench-acceptance.md#辅助平面轨道相机2026-09-17)
- [PDE 数值迁移和未验范围](mvp/pibsnet-acceptance.md)
- [显式步骤与可复制扩展](mvp/recipe-explicit-acceptance.md)
- [双模型数值参考](mvp/transolver3-acceptance.md)
- [独立 Vis 包内真源](mvp/vis-migration-acceptance.md)

## 历史验收与专题材料

以下保存原实验与当时交付范围，现行源码可能已演进。

- [abupt-acceptance](mvp/abupt-acceptance.md)
- [abupt-end-to-end-acceptance](mvp/abupt-end-to-end-acceptance.md)
- [abupt-multidomain-acceptance](mvp/abupt-multidomain-acceptance.md)
- [abupt-mvp1](mvp/abupt-mvp1.md)
- [abupt-reference-acceptance](mvp/abupt-reference-acceptance.md)
- [config-regroup-acceptance](mvp/config-regroup-acceptance.md)
- [cross-model-50-acceptance](mvp/cross-model-50-acceptance.md)
- [cross-model-acceptance](mvp/cross-model-acceptance.md)
- [framework-correctness-acceptance](mvp/framework-correctness-acceptance.md)
- [inference-acceptance](mvp/inference-acceptance.md)
- [task-acceptance](mvp/task-acceptance.md)
- [web-algorithm-acceptance](mvp/web-algorithm-acceptance.md)
- [web-integrated-acceptance](mvp/web-integrated-acceptance.md)
- [web-rawprep-acceptance](mvp/web-rawprep-acceptance.md)
- [web-visualization-acceptance](mvp/web-visualization-acceptance.md)

- [Neumann与Advection输入核查](../docs/pibsnet/Neumann与Advection输入核查.md)：历史只读输入差异与未重训范围。

- [原子能力源码清单](../docs/abilities-inventory.md)、[能力归并讨论](../docs/abilities-merged.md)、[能力简表](../docs/abilities-summary.md)：保留设计讨论分类，实际推理与后处理职责以当前架构为准。

- [AI4S 框架能力比较](../docs/ai4s-framework-comparison.md)：案例驱动演进参考。

- [Task 项目共享数据](mvp/task-shared-datasets-acceptance.md)：Task 独立共享、显式覆盖、平台联动与指定项目迁移（含旧登记名与来源运行精确配对）；实际验收状态以记录为准。

- [平台配置合成与完整保存](mvp/platform-configuration-acceptance.md)：平台优先、删除、兼容及执行交接。

- [GenCP 缩小实验接入](mvp/gencp-acceptance.md)：三套时空数据、CNO/SiT-FNO、独立场训练与耦合生成；扩展示例包含条件替换、派生输出及单场重训重新组合，六组算法验收以记录为准；2026-09-17 Task 补验缺入口声明，未能提交计算，未开放平台。


三维交互与对象隔离（2026-09-16）：新对象计算和显示草稿一起提交；辅助平面独立显隐，三轴平移与三轴旋转仅命中手柄启动；删除局部清理不重建背景和相机。种子和Probe有候选预览，等高线支持自动分层，同标量等值面保留生成标量。圈定 `test_phys_interaction.py`、`test_phys_objects.py`、`test_phys_display_updates.py`、`test_phys_filters.py`、配置/存储用例与 `viz_interaction_browser.cjs`；最终范围见根 `.context/mvp/phys-workbench-acceptance.md`，正式8000/5173不自动更新。

三维着色与显示设置专项：新增 `backend/tests/modules/test_phys_display_settings.py`（Vis包内），前端 `transparentExport.test.jsx`；实现和证据见根 `.context/mvp/phys-workbench-acceptance.md`，正式入口未自动发布。

发布验收必读：根 `AGENTS.md` 与 `.cursor/rules/plan-business-alignment.mdc` 的正式发布/Web 冒烟门槛；每份实施计划必列，未通过不得称完成。

- WDNO 当前目录：`contrib/ability/{model,transform,constraint,inference,eval}/wdno`、`contrib/application/spatiotemporal_pde/wdno`、`core/applications/spatiotemporal_pde`、`recipes/wdno`、`examples/wdno/burgers_base` 与 `examples/recipe_extensions/wdno`。原六例扩展与论文完整复现未完成。

- [WDNO Task公共约定适配](mvp/wdno-acceptance.md)：新输入/输出、同一recipe直接与Task运行、资产指标登记、旧配置显式转换和历史检查点消费；当前补验状态见记录。


训练评估指标与三维度曲线（2026-09-18）：[验收记录](mvp/training-metrics-ui-acceptance.md) 汇总指标实际计算、保存、曲线页签与正式发布状态。

训练运行/推理/后处理一致性修复（2026-09-18）：训练报告新增 update 粒度 `curves`，训练评估支持物理量、指标和聚合选择；推理结果保留无统计 checkpoint 占位行并禁止运行中重复提交；后处理只消费训练绑定平台数据集；VTK prediction/truth 继续按资产身份逐层核验；三维工作区高度调整见对应 PRD 与圈定测试。
