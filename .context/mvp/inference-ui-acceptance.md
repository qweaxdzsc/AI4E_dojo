# 推理工作台 UI 与功能验收（2026-09-15）

本记录对应用户批准的完整推理工作台计划。旧 `inference-acceptance.md` 和历史科研数值证据保留原验收边界。

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
- 配置条：210,397,1432,90。
- 指标表：210,496,1432,218。
- 图表：210,723,1432,194。

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
