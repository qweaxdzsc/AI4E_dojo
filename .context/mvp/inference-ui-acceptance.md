# 推理工作台 UI 与功能验收（2026-09-15）

本记录对应用户批准的完整推理工作台计划。旧 `inference-acceptance.md` 和历史科研数值证据保留原验收边界。

2026-09-18 13:16 正式 `5173→8000` 契约贯通冒烟（当次授权重装 `ai4e-spec`/`ai4e-core`/`ai4e-server` 并只重启 8000）：入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，对照任务「测试0918」（`f8f89f8037b34026ae778116f441a3f6` / 项目 `179ed1fe…`）。旧 8000 PID **61841**，新 8000 PID **3619**，5173 **23629** 未动。安装摘要：`inference.py` `45aae1917eab53cf`，`vtk_capability.py` `38b24b8b83d4e3c4`，`application.py` `7a507fc8e2611938`，`api.py` `2b87fecec8a3a2ae`。样本接口带回 `vtk_exports`（点云/网格化均 available，来源 `source_vtk`+`comparison_mesh`）。页面两项默认勾选且含真值，ShapeNet 网格化可勾。选 `last.pt`+1 样本点「检查推理配置」得「检查通过；尚未提交推理」，无 422。旧键只关 `export_vtk` 且不保存预测的检查 HTTP 200，点云和网格化均为关。历史批次 `infer-20260918-095609` 100 个测试样本均有 `surface.vtp`/`volume.vtu`。切到训练运行再回推理，工作台 2–8 步仍绿勾。平台无未绑定 NASA 任务，置灰未在正式页另开任务验证（源码 e2e 已覆盖）。证据 `official-20260918-export-contract-defaults.png`、`official-20260918-export-contract-after-return.png`、`official-20260918-export-contract-smoke.json`。未新跑推理批次。

2026-09-18 推理点云/网格化导出契约贯通：页面两项默认勾选且含真值。置灰只认来源文件名或已绑定连接关系路径，不认空槽位或原始处理 VTKHDF 输出开关。样本接口必须带 `vtk_exports`，服务不得丢掉；页面缺字段按不可用。旧键/新键只在契约包解释，HTTP 未写的新键不得先填成开。清单跳过网格化不得盖掉点云成功。源码圈定 `test_infer_vtk_exports.py`、`test_web_inference.py` 与 `e2e/inference-layout.spec.ts`。2026-09-18 13:16 已按当次授权重装并只重启 8000，正式入口见上文冒烟。

2026-09-18 推理配置布局：配置卡改为控件行、预算与说明分行，高度随内容，不再锁 90px 单行；关闭导出网格的警告留在卡内。各区块标题去掉序号。仅改 web 源码。正式 5173→8000 冒烟（10:55，Vite HMR，未重装/未重启 8000）：入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，任务 `测试0918`（`f8f89f80…`）。标题为 Checkpoint / 样本 / 物理量 / 指标 / 推理配置 / 指标表格 / 折线图；默认态与取消网格警告均无溢出、不覆盖表格。证据 `official-20260918-infer-settings-layout.png`、`official-20260918-infer-settings-vtk-off.png`、`official-20260918-infer-settings-smoke.json`。圈定 `e2e/inference-layout.spec.ts`。

2026-09-17 补充：进入推理页先填第一份兼容检查点的样本、物理量和指标目录，再后台核对其余；一致则继续共用，失败或不一致则提示并回退先选检查点。Checkpoint、物理量、指标提供全选。缺准备或已清理批次改为明确中文原因，浏览器记住的已清理批次不再把缺文件说成数据根未配置。圈定 `test_web_inference.py` 与 `e2e/inference-selection.spec.ts`。

2026-09-17 批次身份：页面提交默认名称改为 `infer-YYYYMMDD-HHMMSS`，同一选择重试复用该身份；后处理与推理批次下拉把旧「批量推理」按 `created_at` 格式化。未改 spec/server 缺省字符串，未重装 8000。圈定 `e2e/inference.spec.ts`、`e2e/post-workspace.spec.ts`。

2026-09-17 默认 VTK：推理配置默认勾选导出网格；取消时页面提示本次不会写出 VTK。结果文件对缺网格样本展示清单原因。缺拓扑或点数对不上则该样本失败，整批不冒充全部成功。2026-09-17 23:50 正式 8000 已重装 `ai4e-core`/`ai4e-task` 等并重启；对照任务历史批次展示「未写出VTK：该次推理未导出网格」。当前大结构对小检查点仍拒绝，未新跑默认网格批次。

2026-09-17 检查点树：推理 Checkpoint 栏按服务 `run_id` 把同一次训练运行收成父级，子级为 latest/last/best 等检查点；父级文案「训练运行 ·」加短号，缺 `run_id` 归「未归属运行」。全选与选父级都只勾叶子。夹具改为两个 run 各 6 个检查点，`e2e/inference-selection.spec.ts` 核树与选父级。契约未改，不重装 task/server。

2026-09-17 图表/表格加高与显示选项：指标表 460px、图表 420px（原 218/194 至少两倍）；图表配置增加刻度、网格线、点数值，按任务保存。圈定 `e2e/inference-results.spec.ts`。正式 5173 读源码即可核高度与弹层，未改 8000。同日正式页实测表格/图表计算样式 460/420、`max-height:none`，配置弹层可见三项开关与疏密档；截图 `official-20260917-2035-chart-config.png`。该任务当时无推理批次，无绘点。

正式 5173→8000 冒烟（2026-09-17 20:35，仅 web 源码 / Vite HMR，未重启 8000）：入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，任务 `7142b2dc…` / `9c1dac25…`。Checkpoint 栏见三棵父级「训练运行 · 3a5933a4」「训练运行 · e066c799」「训练运行 · 3dfc0915」，各下挂 `last.pt` / `latest.pt`。进页仍预加载样本。证据：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/official-20260917-2035-infer-run-tree.png`。

正式 8000/5173 冒烟（2026-09-17 20:46–20:54，用户当次授权重装 `ai4e-task`/`ai4e-viz` 并重启 8000）：入口仍 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，任务同上。8000 PID **6975**、Vis **7457**，5173 **23629**。推理页检查点 6、样本 889、物理量 4/5、指标 5/11，无数据根红条，重开后无 HTTP 500。后处理「批量推理 · 0bdc98ce」结果树搜索 `.vtp` 共 100 个 `full_surface.vtp`。切步 `stage-inputs` 0.18s。证据：`official-20260917-2054-smoke.json`、`official-20260917-2054-post-vtp.png`。未新跑 887 样本推理，张量日志降级未验证。

正式 8000/5173 冒烟（2026-09-17 19:41–20:05，用户当次授权重装重启）：`uv sync --group dev --group visualization --reinstall-package ai4e-core --reinstall-package ai4e-task --reinstall-package ai4e-server` 后重启官方 8000（Python PID **99745**，约 20:01 起来；5173 未动）。入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，任务 `7142b2dc…` / `9c1dac25…`。安装摘要：`checkpoints.py` `dcb74e5702d553bf`，`inference/application.py` `43fa563ca5a2b716`，`export.py` `ec124f6f6e502a07`。不存在批次改为 400「推理批次不存在或已被清理」。推理页未选手动检查点即列出 4 个检查点与 889 样本，全选 4/4、5/5、11/11，无数据根红条。训练设置见写出卡片默认关闭。后处理结果文件 0 条，空态含训练写出说明。证据：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/official-20260917-2001-infer.png`、`official-20260917-2002-training-export.png`、`official-20260917-2003-post-files.png`、`official-20260917-2005-smoke.json`。未重训打开写出，故无训练场文件。评价开关值保持关闭；页面控件未带 disabled（描述接口 `readOnly=false`），不当作已锁死控件验收。

## 实施范围

- 沿用独立infer，未新增core生命周期/DAG。ability提供评价、等权统计、设备同步计时与表格输出；application装配字段选择、预测和固定结果；Task管理检查点×分片串行批次；Server/Web消费稳定协议。
- 九项场指标、样本等权Mean/Median/P90/Max、真实计时、CSV/XLSX已接通。物理空间float64计算；有效实体mask和所选分量参与评价，保存完整原始矢量。未定义值保留原因，逐点相对误差阈值和排除数量记录在结果。
- 新v2轻量结果不依赖张量manifest存在，旧v1可读。新post默认拒绝缺少固定结果的预测回退；`post.legacy_predict=true`仅作显式历史算术对照。旧归档API/profile保持原行为，未知修改拒绝。
- 一份检查点只固定一次完整字节；跨分片同名样本保留身份；取消、中断恢复、只重试失败部分及继承已成功结果均保留来源。最后一个子运行成功不能掩盖批次部分失败。推理和固定结果重算不创建任务版本、不修改训练配置。
- 六套外流模板、用户派生场/普通评价函数扩展、真实wheel外部复制完成交接。六份configuration.py的现有加载/覆盖/路径行为适用，推理专项直接复用。最终并行rawprep改动新增workers透传键；已逐行核对该差异并加入固定兼容摘要，未将任意新模板自动放行。旧legacy-profile.json不改写；新增原生infer指纹来自实施前真实脚本。
- AB-UPT与Transolver查询参数实际生效。Transolver按原顺序累计物理状态，仅缓存后的解码按查询块拆分。通用锚点模板的采样指标与完整网格实体口径分别记录，full_surface/full_volume只保存所选域并登记到固定结果。
- 后处理样本选择也使用“分片＋样本”，CSV/XLSX保存分片与算法来源；下载、文件树、完整日志与Trame复用既有组件。

## UI还原度验收

原图保留在 `docs/prototypes/dojo-inference-reference.png`（1672×941）。以固定夹具控制填充密度，主基准与1440×900、1920×1080均截图。另检查默认、空、运行、配置弹层、长中文名称与1000px窄视口。

原尺寸实际边界（x,y,width,height）：

- Checkpoint：210,117,341,271。
- 样本：567,117,338,271。
- 物理量：921,117,352,271。
- 指标：1289,117,353,271。
- 配置条：原图 210,397,1432,90；现行卡片按控件、预算与说明分行，高度随内容，不再锁 90px。各区块标题不带序号。
- 指标表：原图 210,496,1432,218；现行卡片高度 460px。
- 图表：原图 210,723,1432,194；现行卡片高度 420px、绘图区 368px。

关键区域最大边界误差2px，未扩大4px门槛，未加像素遮罩。原图、并排、叠加、差异图及区域JSON全部保留。已实际查看原尺寸、两个响应式尺寸、长名称、空态/默认态、配置弹层及真实结果截图；配置截图等待进入动画稳定，不能用只有遮罩的瞬间截图验收。2000样本已加载后的勾选在1秒内完成断言通过；整个浏览器测试时长不冒充操作延迟。

差异边界：平台品牌、任务元数据和现行步骤名称沿用当前产品；热/结构在未有能力时不可用；分页50、实际字段/指标数和真实指标值不复制图中示意数字；图表按确认后的Checkpoint横轴与Mean/Median/P90系列展示。字体抗锯齿保留真实浏览器差异。未用未经测量的“还原百分比”。

## 真实功能验收

证据根：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/`。

真实数据为ShapeNet-Car三辆CFD车，训练/验证(eval)/测试各1样本。两份不同Transolver检查点来自1个训练样本、2轮及1轮CPU小模型预算，验证工程交接，不代表生产精度或完整科研训练。

- `real-browser/results.json`：两权重×三分片共6个成功子运行，明确提交名单、字段、指标、设备和查询块。从首页进入并完成预检、提交、刷新、日志、表格和三种图表。
- `real-browser/resilience.json`：只评价不生成预测张量；实际终止本次协调进程后显式恢复，不重复提交已启动子运行；实际取消、关闭重开、任务隔离和409过期修订。原训练配置逐项不变。
- `real-browser/partial-retry.json`：实际终止首个推理子进程，最后子运行成功但批次保持partial；重试仅新增1个失败子运行并继承5个成功来源，6份最终结果可比。
- `formal-browser/results.json`、`browser-evidence.json`：正式8000/5173从首页重新完成6个子运行、CSV/XLSX下载和固定post跳转。真实Trame选择surface.pressure.prediction并适窗，截图实际可见正确汽车网格；不是空canvas验收。
- `formal-browser/post-recalculated.json`：固定数组重新评价6份结果，保留三个分片并逐值对照原推理指标；全过程没有提交推理批次。
- `formal-browser/download-readback.json`：真实后处理XLSX六行和三个分片读回，预测张量实际下载读回为float32、3586×1；CSV与推理XLSX数值和来源另由报告工具核对。
- `real-browser/independent-check.json`及`formal-browser/independent-check.json`：直接加载原预测/真值，用独立NumPy计算复核默认五项指标，未调用产品评价函数；九项公式、有效mask、矢量分量、零分母、线性P90有独立算术夹具覆盖。
- `formal-browser/selection-check.json`：实际目录搜索、排序、筛选、分片往返、全选/取消后，预检提交名单核对。

## 相关回归与安装

- `test-results-latest.json`逐用例记录最新结果；早期失败XML保持原样，后续修复结果按同一用例定位，不用文件总数重复计数。
- `core-compatibility.xml`、`anchor-final.xml`、`anchor-extension-final.xml`、`final-evaluation-installation.xml`：五个外流案例、新旧数值、通用锚点、用户能力、真实wheel和固定post交接。
- `final-contracts.xml`、`partitions.xml`、`native-profile.xml`、`profile-regression.xml`：请求边界、批次完整状态、任务/服务、当前与固定旧模板识别。
- `recipe-boundaries.xml`及`final-reuse-boundaries.xml`等：配置加载与冻结快照、准备消费、归一化物化、训练恢复、模型评价、任务new/fork/执行、资产与比较选择器。`final-logging.xml`验证复用日志。
- `final-documents.xml`：相关PRD、模块与案例文档验收。Web构建、公开门面检查与生成契约重复生成均通过；生成摘要见`generated-contracts.json`。
- 浏览器：推理布局/选择/结果及兼容17项；后处理布局/浮层/同名分片选择；首页、阶段状态、文件与会话相关回归；真实CFD流程分开记录，不把HTTP夹具当成实跑。
- 两个既有真实换模专项因未启用DOJO_MODEL_PICKER_REAL而skip，不算真实换模验收。真实MPS训练到完整网格的已有相关用例通过；CUDA硬件本机不可用，不宣称CUDA实跑。其余本切片明确CPU预算。
- `installed-formal-entry.json`：安装模块路径、源码与安装字节摘要一致、正式API及前端代理200。正式入口保留原平台根和已授权数据根；验收项目仅登记既有项目目录，不迁移或改写训练来源。

## 文件交接与可追溯性

`file-test-map.md` / `file-test-map.json`逐文件记录责任、最终字节和相关测试。范围包含计划中的契约、ability、application、contrib、六套模板、task、server、web、PRD、索引、规则和工具；实际新增关联包括通用锚点网格交接的post/mesh.py、后处理样本分片选择和导出来源。测试文件另有逐例XML与浏览器记录。

工作区实施前已有大量修改。`baseline/git-status.txt`与`baseline/templates.json`保留当时状态；不把其他并行工作归为本次，不重写其文件或历史验收。

两道验收结论及最终测试汇总以证据根`acceptance-summary.json`为准。未采集的生产精度、GPU规模和真实换模不纳入已通过声明。

## 正式双 checkpoint 冒烟（2026-09-18，用户授权）

- 正式入口：`http://127.0.0.1:5173` → API `8000`（PID **34563**）。任务 `179ed1fe447b415b8870c45b6a89a296 / 01400e5e5b8a4bd88d43f658ddc2fb9f`。
- 推理批次 `c9a60689c6254c4296ee205b7cd0d7ec` 返回 `checkpoint_count=2`、`subrun_count=2`、`items=200`、`statistics=80`；页面结果区保留 `last.pt · d5d42ab7` 与 `latest.pt · 4d055b5a` 两行。
- 运行状态位于推理配置下方；无选择时开始计算按钮禁用。结果文件树显示推理批次和两个 checkpoint 目录，不再显示“固定结果文件与后处理交接”容器。
- VTK 精确核验详见 `/Users/zonghui/work/project_simulation/dojo_train/formal-20260918-consistency/vtk-identity.json`：源 PT prediction/truth 不相等（max abs diff 104.5523529、mean abs diff 4.89271736）；经 `original_point_id` 对齐后，VTK 的 `surface.pressure.prediction` 与 `surface.pressure.truth` 分别逐值匹配源 prediction/truth，字段没有写反或被覆盖。
- 后续健康检查返回 `{"status":"ok"}`；正式服务当前 PID 为 **48179**。
