# ai4e-web 模块索引
## 当前职责与本轮变更

src 中按用户任务组织微领域；e2e 浏览器流程，scripts 架构与传输类型检查。

- `packages/ai4e-web/src/modules/stages/useModelSelection.ts`：模型候选、选择草稿和请求失效控制；目录先出，点选后再取目标默认值与能力。
- `packages/ai4e-web/src/modules/stages/inputChoices.ts`：输入候选去重、排序、稳定选择键，以及只有当前绑定失效才报警。
- `packages/ai4e-web/src/modules/stages/api.ts`：保存阶段配置时提交 `edited_paths`/`removed_paths`，数据准备执行前先走同一保存契约；同任务 `model-options` 合并在途请求并短时复用，换模或导出后失效；结构图资产地址可按档选取成员。
- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


正式前端已接入整合平台真实流程。唯一 UI 基准 `docs/prototypes/dojo-web-integrated.html`；该 HTML 的示例状态不代表实际计算。旧首期验收与新四组合验收分别保留，范围以总验收记录为准。有 Web 消费链的改动须由 Agent 自己在正式 5173→8000 冒烟；隔离 7999/5172 与「待发布」不能当完成，细则见根 `AGENTS.md`。

## 工程与公共基础设施

- `packages/ai4e-web/package.json`、`package-lock.json`：唯一 npm 清单与锁；React、TypeScript、Vite、Ant Design、vtk.js。
- `index.html`、`src/main.tsx`：页面加载与挂载。
- `tsconfig.json`、`vite.config.ts`：类型、构建与可配置本机 API 代理。
- `playwright.config.ts`：自动化浏览器入口。
- `scripts/check-boundaries.mjs`：微领域公开门面导入检查。
- `scripts/generate-contracts.py`：从服务 OpenAPI 生成 `src/infrastructure/contracts/api.generated.ts`。
- `scripts/generate-platform-contracts.py`：从 spec 生成 `src/infrastructure/contracts/platform.generated.ts`。
- `src/infrastructure/http/client.ts`：统一请求与错误，区分网络断开、HTTP失败、非JSON/空正文及204成功；优先 `error.message`，否则用业务 detail。
- `src/infrastructure/components/`：异常边界、未开放提示、无业务语义配置输入组件；ActionButton 提供稳定可访问名称和真实忙碌禁用状态。
- `src/infrastructure/theme/global.css`：平台布局；`visualization.css`：查看器内部布局。
- `src/infrastructure/assets/binary.ts`：带修订二进制读取、引用计数与 CPU 缓存。
- `src/infrastructure/rendering/vtk/Viewport.tsx`：vtk.js 相机、表示、点选及 GPU 生命周期；`MeshViewer.tsx` 保留旧预览兼容。

## 应用壳与微领域

`src/app/App.tsx` 装配路由；`layouts/PlatformLayout.tsx` 提供整合外壳；`pages/ProjectDetailPage.tsx` 组合六页签，`TaskWorkbenchPage.tsx` 组合任务与九步导航。下列领域通过各自 `index.ts` 导出：

`pages/WorkbenchLandingPage.tsx` 是真实工作台选择入口，读取项目/任务和有效最近任务，`?choose=1` 强制切换；已归档或不存在的最近对象不自动恢复。全局侧栏由路由决定高亮与面包屑，整行链接和装饰图标的可访问名称分开。`pages/TaskWorkbenchPage.tsx` 与 `task-workbench.css` 用整合 HTML 最终主题的单行标题（任务名、状态、任务/项目/版本）和 `topsteps` 九步，不再使用 Ant Design Steps，标题右侧不放案例徽章或切换/返回按钮。已完成且非当前步为成功绿，当前步保持蓝；任务表进度行同一套颜色。训练设置走阶段工作台并提交开训，训练运行直接挂执行监控，不再使用伪阶段 `execution`。模型/训练设置保存后的完成态刷新后仍恢复，检查或结构跟踪不能冒充；过期检查不把已保存清成未完成。保存配置在已读且未忙碌时可用。

- `src/modules/projects/`：ProjectNavigation 项目创建、列表与管理，api 代理真实服务。
- `public/project-covers/`：从整合原型提取的四张原字节装饰封面及来源 README；不作为科研结果。
- `src/modules/tasks/`：TaskManagement 简洁创建时必选四组案例并按接口字段展示数据集与模型，成功进入原始处理；编辑仅元信息，派生继承配置与绑定。案例加载失败可在弹窗内重试。`stages.ts` 提供任务表与工作台共用的九步名称及真实阶段状态映射。api 读取登记案例，`task-management.css` 管任务表、更多菜单和创建弹窗密度，不写进全局样式。行内进入工作台与血缘使用同一按钮样式。
- `src/modules/files/`：FileBrowser 文件树、选择、查询和刷新；ProjectFiles 对照整合 HTML 的任务版本 / 搜索 / 类型 / 排序工具条和表列，浏览内容仍是真实目录，api 管访问。
- `src/modules/rawprep/`：RawprepWorkbench 三栏；切步时配置与执行区先渲染，不整页等待运行名单、文件树或样本目录；第 04 段 PT/Zarr 复选可同时写出，VTKHDF 独立附加且仅已接入时显示；ShapeNet 新任务与缺键按官方案例/清单默认勾选，NASA 不显示，已保存关闭保持原值；执行区填写平台数据集名称；执行范围只提供全部或指定样本，不按 train/test 分片，执行区区分处理样本数与来源文件数，并标明来自绑定数据集或本次指定样本；执行配置可改并行线程并写入 `rawprep.workers`；名称框展示 `processed_name_status`，名称已存在时点执行先保存再询问是否覆盖；执行门禁还要求名称与至少一种格式，未保存修订在提交前写入，不因 dirty 禁用主按钮；FieldExtractionEditor 读文件后只勾选一个场或坐标；ExtractionDialog 旧兼容编辑组件；api 管配置与完整样本操作，目录请求同任务短时复用。
- `src/modules/rawprep/DatasetBindingPanel.tsx`：修改绑定只选 contrib 公开数据集及其本机完整副本，一次保存处理方式与受控地址；左栏页签右侧刷新与修改绑定并排，其下直接是搜索框，不展示处理方式与本机地址说明。`BoundDatasetFiles.tsx` 用原始数据处理/处理结果页签限制输入选择；处理结果经 `stageInputs` 读取已登记平台数据集再按路径建树，不自动勾最新，预览复用文件预览弹窗，下载走资产地址；树未到时栏内转圈，失败只提示树。`RawprepWorkbench.tsx` 按每个 `.pt` 一张提取卡片，对话框只勾选一个场或坐标；平台数据集名称可预填来源标识，检查/试跑/执行前写入 `dataset.processed_name`；执行配置四个按钮立刻带动进度条、日志状态与说明，再执行立刻清完成态，日志同页叠加；无运行不把空日志快照显示成「处理中」。`dataset-binding.css` 与 `rawprep-workbench.css` 对照细节原型三栏。NASA 文件选择使用根与路径组合的稳定键，FieldExtractionEditor 分别解析根和相对路径。
- `src/modules/stages/`：StageWorkbench 只协调阶段配置修订、固定输入和操作；切步骤时配置先渲染，产物列表与运行名单并行补齐，失败仍展示已读配置；同任务 `stage-inputs` 与 `model-options` 合并在途请求并短时复用；模型设置不整页等待候选列表；模型/训练设置点保存即使未改参数也会落盘记下完成；训练设置页提交开训，只带当次所选准备与可选续训覆盖，由服务合成这次运行配置并只认现行 version=2 准备，不带 `prepare_first`，也不再使用伪阶段 `execution`；旧准备的拒绝文案由服务返回；e2e 核对即使配置里另有已选清单也不写入开训绑定；失效绑定用人话说明，不写内部键名；目录里空的共享名或未选用坏项不报「已绑定来源不可用」；平台数据集同一清单只列一条且名称优先，选项值不复用 asset_id，下拉按登记时间倒序且不自动勾最新；api 为共享阶段传输。
- `src/modules/trainprep/PreparationPanel.tsx` 与 `trainprep.css`：对照细节原型三栏（9px 间距、等高 640），左栏按平台数据集选择并用产物树浏览，处理结果只绑正式准备运行，展示 `preparation.json` 与归一化 PT 树；字段按模型角色与物理场下拉匹配并对照张量形状，中栏可按官方数据集-模型组合加载处理声明，数据转换含归一化、统一空间和 scale，可改 train/test/eval 数量与抽取方法，右栏执行区展示已选平台数据集名称与全部/指定样本范围，不再放无效执行数量。保存副本默认勾选，统计与采样不手填。已有平台数据集但未选择时提示先选且主执行不可用，不自动勾最新。执行进度与叠加日志与原始处理同一套。
- `src/modules/models/ModelPanel.tsx`：模型参数、采样、输入和真实结构宿主；已保存参数不接下拉；模型类型下可选官方数据集-模型组合并只覆盖本页参数；「已导出的模型配置」选项目内导出预设，「当前参数来源」只读说明来自案例默认还是导出配置；「导出模型配置」写出参数不含权重；候选下拉独立转圈，失败只坏下拉；两档结构图用按钮切换，生成与载入时视窗只显示加载样式并卸掉旧 iframe；无物理清单或准备记录时不能生成结构。`graphViews.ts` 只在结果真正登记两档时提供切换。`graphViewport.ts` 与 viz 同一按宽度替换。
- `src/modules/training/TrainingPanel.tsx`：按案例参数组织优化与训练控制；可独立加载官方组合覆盖本页训练参数；预检不要求准备记录；本页选择已准备完成的数据集、其中的切片、训练模式和检查点并开始训练；已准备数据集下拉只显示登记名称，切片来自该准备记录的 train/test/eval，默认训练集。测试评估说明写明：关闭时运行页仍有曲线和在线分项，打开后才有测试评估表。另有「训练结束写出」：预测、网格、分片默认关闭，不解开评价锁。
- `src/modules/executions/`：ExecutionLog 日志恢复，原始处理可叠加多次运行正文；操作说明只在发生时写入一行，随正文滚动，不钉在底部。默认只渲染最近 500 行，其余留在内存，向上滚动展开；自动滚动取消后不抢滚动位置。运行失败且日志为空时仍展示运行记录中的错误原因。`logWindow.ts` 计算窗口起点。可选回传运行快照给进度条；TrainingMonitor 对照运行细节页的摘要、左右栏和真实指标，只监控已提交训练，不选数据、不开训，api 管运行事实；评估表分列在线分项与测试评估，无记录不从日志拼数。
- `src/modules/post/`：PostWorkspace 对照整合 HTML 后处理步（结果文件 / 三维页签，默认结果文件），PostMetricCharts 只绘制真实指标且不进入导航，`post.css` 管本页皮肤，api 管固定场景。不复刻示意徽章或假结果。
- `src/modules/lineage/`：对照整合 HTML 的左图右检版本树；`layout.ts` 按真实父版本排布节点，不使用原型固定示意树。`LineageView` 区分创建快照、当前目录与固定运行，Fork 走任务公开派生门面。
- `src/modules/comparisons/`：配置及固定来源比较；DifferencePanel 协调严格差值与查看器。`comparison.css` 只画表格/趋势/三维导轨外壳。
- `src/modules/reports/`：新整合入口未开放；`ProjectReport` 只读历史正文，`report-shell.css` 同时给批量两栏外壳。
- `src/app/pages/BatchShell.tsx`：批量页未开放外壳，不生成计划。
- `src/modules/previews/`：FilePreviewDialog 宿主；`preview-dialog.css` 管网格预览弹窗按视口封顶加高、可滚动、视口全屏和嵌入高度链。后处理三维页由 `task-workbench.css` / `post.css` 相对原 820px 至少加高 40% 并尽量铺满剩余视口，iframe 保底 840px；宿主不展示「打开已保存配置」。FilePreviewContent、FieldTree、FieldSummary 由可视化领域提供真实内容，api 保留兼容。
- `src/modules/visualization/`：VisualizationWorkspace 为唯一工作区公开组件；model 定义源、管线、窗口与场景，api 调用平台辅助操作。

宿主不访问 vtk.js 对象；查看器不访问 task、训练配置或 Python 文件路径。显示对象与科学计算分开。

## 文档与验收

- `docs/PRD/ai4e-web/src/PRD.md`：长期业务正文。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 19 节：唯一平台架构。
- `docs/adr/0004-web-server-runtime.md`、`0005-preview-worker.md`：栈与两条进程链。
- `.context/mvp/web-rawprep-acceptance.md`：旧首期证据。
- `.context/mvp/web-integrated-acceptance.md`、`web-integrated-results/`：本轮实际完成状态及证据。
- `e2e/project-task.spec.ts`：项目、任务管理；`navigation.spec.ts`：入口与未开放状态；`rawprep.spec.ts`：真实原始处理。
- `e2e/visualization-views.spec.ts`：真实 ShapeNet/NASA 文件、过滤、相机联动、场景恢复、取消与资源释放。
- `tests/integration/test_web_integrated_pipeline.py`：主 Agent 独立跨包与显式 HTTP 四阶段验收。

- `e2e/platform-integrated.spec.ts`：复用真实运行检查阶段配置、固定交接、提取草稿与六页原型矩形对照。
- `e2e/model-inspection.spec.ts`：生成加载样式、两档切换与历史单图不假切换。
- `e2e/task-dataset-binding.spec.ts`：从项目页点击完成五案例简洁创建（模型在前，含体场），绑定改为选择公开数据集与本机副本；弹窗校验/重试/约定尺寸，以及 1440/1920 任务表对照整合 HTML。证据见 `.context/mvp/web-integrated-results/task-binding-correction/`。
- `e2e/visualization-difference.spec.ts`、`visualization-export.spec.ts`：真实 NASA 差值及完整导出网格。
- `e2e/visualization-safety.spec.ts`、`visualization-subscriptions.spec.ts`：资源/上下文恢复及明确标注的订阅协议夹具。
- `e2e/visualization-camera.spec.ts`：固定来源身份仍可核对；相机联动覆盖全部窗口，缺坐标空间声明不再断开，单位不一致只提示。
- `e2e/research-records.spec.ts`：版本固定阶段参数加入比较、保存恢复及真实迟到请求隔离。
- `e2e/home-entry.spec.ts`：从首页逐项点击、空项目新建任务、最近任务恢复与归档失效，以及 1440/1920 首页原型几何和封面摘要对照；测试生成记录按确切身份归档。

一致性切片新增：`src/modules/files/StageFiles.tsx` 固定清单/运行文件与资产预览；`model.css`、`training.css`、`executions.css` 分属模型、训练、监控领域。`e2e/stage-consistency.spec.ts` 验证状态与保存协调、平台数据集同清单去重及登记时间倒序，以及训练设置开训与运行页只监控，`prototype-consistency.spec.ts` 验证整合原型控件几何，`execution-monitor.spec.ts` 验证真实坐标语义、日志交互与运行页无开训控件（契约夹具明确标记）。当前证据入口为 `mvp/web-integrated-results/ui-consistency/`，不沿用历史通过数。

补充测试：`e2e/stage-files.spec.ts` 固定来源空态、按层展开与范围切换；`e2e/rawprep-consistency.spec.ts` 公开数据集绑定取消、结果树按层预览下载与正式执行进度，以及进页先出三栏、慢文件树不挡住；`e2e/rawprep-real-consistency.spec.ts` 两数据集真实页面执行与结果预览；`e2e/execution-log.spec.ts` 长日志 500 行窗口、自动滚动开关、向上展开，以及失败且空日志时展示 `run.error`。整体证据与未覆盖状态见上述ui-consistency/README。

## 独立可视化任务交接

- `packages/ai4e-web/src/modules/visualization/PhysFieldEmbed.tsx`：任务目标、独立应用嵌入；`source-list` 走任务来源列表，追加前先登记定位再 `append_session_sources`。显式重开先关闭再创建，满员可重试。内层 Trame 菜单挂到页面根节点；嵌入页关闭后的对话框蒙层不得挡住点击。已可见时重复可见性消息由 Trame 忽略，避免工作进程连读网格。
- `packages/ai4e-web/src/modules/visualization/api.ts`：可视化任务资产、会话请求与任务范围内可视化网格来源列表。

## 声明驱动原始处理

rawprep 页面展示声明默认值、真实字段、能力依赖及样本范围；字段提取添加按钮在列表上方，配置固定高度单行滚动，编辑/删除为图标；法向/SDF 等几何产物不进提取列表，与左侧能力同一行命名且不带 `.pt`；最近顶点距离只对应 `volume_sdf`，体积法向独立对应 `volume_normals`，点到网格表面距离三个名称纵向列出；阈值按默认写入不展示；对话框列出声明源文件和样本目录场文件，编辑回填默认 VTK 与字段，来源表与处理结果树固定列宽、样式图标与「预览 文件名」标签，保存提示与进度在执行栏内。新增 e2e/manifest-rawprep-real.spec.ts 从首页操作真实任务到 PT 预览。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

三维对象工作台：visualization 原公开门面增加会话内追加结果；宿主来源选择经项目身份校验后进入独立 Vis，保留既有会话和任务版本。浏览器验收 `tests/integration/viz_objects_browser.cjs`，交接测试 `tests/integration/test_viz_host_bindings.py`。

## 同数据集模型选择

- `src/modules/models/ModelPanel.tsx` 与 `model.css`：两个官方模型、可选表面/体场、已导出的模型配置与导出模型配置；结构区不再展示清单或准备下拉。采样、固定损失行与切片数量跟随当前模型字段，不沿用上一模型。模型设置不展示权重加载。
- `src/modules/stages/StageWorkbench.tsx` 与 `api.ts`：读取官方模型与预设、按 `target_model`/`target_preset` 整段替换；跟踪不传用户勾选的清单或准备。
- `src/modules/tasks/TaskManagement.tsx`：新建案例名为「模型 · 数据集」，含体场起步项。
- `e2e/model-picker.spec.ts`：双数据集、变体、导出模型配置、未改参数也可保存、切换/编辑/保存/刷新/冲突与选项失败；换到 Transolver-3 后展示其步长/分块/切片与固定损失，不残留 AB-UPT 超节点，也不出现权重加载。`model-inspection.spec.ts` 直接生成真实结构。
- `src/infrastructure/contracts/api.generated.ts`：阶段保存含官方模型、变体与预设字段。
- 验收状态见 `mvp/model-picker-acceptance.md`；长期说明归 Web PRD 模型设置章节。

`e2e/http-errors.spec.ts`：项目页的空/HTML代理错误、业务错误、截断成功正文、断连后恢复，以及204与有效JSON契约。

默认 Trame 入口修正：`visualization/VisualizationWorkspace.tsx` 默认装配 `PhysFieldEmbed.tsx`，旧场景保留显式兼容；`physical-workspace.css` 提供宿主尺寸。`previews/FilePreviewDialog.tsx`、`FilePreviewContent.tsx`、`files/StageFiles.tsx` 交付来源与任务，网格不走旧分页预览；阶段文件与原始处理共用同一预览弹窗。网格弹窗默认加高可视区，标题提供放大到视口全屏；全屏后工作台贴满，预览不显示「保存到任务」条。`post/PostWorkspace.tsx` 在未选择来源时也显示工作台。`visualization/api.ts` 的物理会话请求复用 HTTP 错误门面。`files/index.ts` 与 `executions/index.ts` 公开原始处理需要的文件及运行读取操作，调用方不穿透微领域。

`e2e/preview-dialog.spec.ts`：网格预览弹窗默认高度与放大/退出全屏。

`e2e/trame-entry.spec.ts`：真实原始处理及后处理路由、网格着色、会话内导入、页面退出回收，以及迟到建会话响应回收。真实用例需 `DOJO_TRAME_PROJECT`、`DOJO_TRAME_TASK` 指向已有 ShapeNet 任务；缺少环境跳过不能算验收。证据及范围见 `mvp/phys-workbench-acceptance.md`。

2026-09-14 HTTP恢复验收：7项浏览器回归、构建与微领域检查通过；原平台项目abc实际浏览器读取正常。证据目录 `/Users/zonghui/work/project_simulation/dojo_train/http-recovery/`，包含测试日志、恢复截图和本机服务启动记录。


## 独立推理 Web 切片

- `src/modules/inference/index.ts`：公开 InferenceWorkspace、InferenceResults、listInferenceBatches、inferenceResults、inferenceSource、inferenceBatchLabel 及轻量显示类型。其他领域只通过该入口调用。
- `src/modules/inference/batchName.ts`：新批次默认 `infer-YYYYMMDD-HHMMSS`；旧「批量推理」有 `created_at` 时格式化成同一身份。
- `api.ts`：检查点、样本、检查、提交、批次查询/取消/重试/恢复及结果接口适配；过渡响应解析集中在此，兼容缺失不放行。
- `model.ts`：已确认批次状态和服务显示契约；`catalog.ts`：比较各检查点样本/物理量/指标是否同一套，并先取第一份再核对其余；`useInference.ts`：进页先填一份目录再后台核对、不一致回退、过期批次记忆清理、选择草稿、持久请求身份、轮询及迟到响应隔离；终态通过既有 `dojo:task-updated` 通道通知壳重读任务摘要。
- `CheckpointPicker.tsx`、`checkpointTree.ts`、`SamplePicker.tsx`、`FieldPicker.tsx`、`MetricPicker.tsx`、`BatchProgress.tsx`、`InferenceResults.tsx`：候选按训练运行收成树、样本、物理量、指标、真实进度、文件和服务指标，检查点/物理量/指标提供全选；选父级等于该 run 下兼容叶子；样本页签固定训练/测试/评价并优先测试集，名单来自准备切片不是源清单；`InferenceWorkspace.tsx` 与 `inference.css` 组合工作区，不实现物理计算。
- `src/modules/tasks/stages.ts`：九步和稳定 slug；`resolveStage` 保留旧数字 6→post、7→report。任务表、血缘页、最近任务与工作台共用映射，访问不改变完成事实。
- `src/modules/post/PostResultsWorkspace.tsx`：后处理两页签（结果文件 / 三维）；结果文件树同时列平台数据集、推理固定结果与训练 run 输出文件夹，无写出时仍显示该 run。跳转为 `post?batch=<批次>&run=<运行>&sample=<样本>&split=<分片>`，不提交模型计算。旧 `tab=metrics` 落到结果文件。`PostWorkspace.tsx` 保留历史调用签名并适配统一两个Tab；旧图表与指标组件不进入后处理导航。
- `e2e/inference.spec.ts`：契约夹具覆盖真实页面请求、批量选择、幂等重试、状态恢复、导航兼容和结果交接；不代表物理计算验收。
- `e2e/inference-real.spec.ts`：使用 `DOJO_INFER_PROJECT`、`DOJO_INFER_TASK`、逗号分隔的 `DOJO_INFER_CHECKPOINTS` 与 `DOJO_INFER_SAMPLES`，在隔离真实任务验证至少2×2结果、下载和Trame；核验终态刷新，分别滚入批次/结果/指标区域截图。无环境跳过不算通过。

## 后处理两页签与固定结果

- `modules/post/PostResultsWorkspace.tsx`：结果文件与三维两个Tab，默认结果文件；页签为 12px 紧凑条。任务级常驻Trame；不再使用全局批次选择器。旧指标深链接落到结果文件。
- `PostMetricsPanel.tsx`、`usePostMetrics.ts`：评价组件与接口保留，后处理页不再挂指标页签；指标表/图表在推理页查看。
- `PostResultFilesPanel.tsx`、`PostFilePreviewPanel.tsx`、`usePostResults.ts`：结果树、内联预览、分隔条和批量加入。树并列「平台数据集 ·」「训练运行 ·」与推理批次；样本按钮显示完整 `param1/<设计号>`。
- `InferenceSettings.tsx` / `useInference.ts` / `InferenceResults.tsx`：推理配置分行排布（设备/块大小/输出、预算、说明），卡片随内容增高。输出项为评估指标、导出点云数据、导出VTK网格化数据，后两项默认勾选且含真值。目录缺 `vtk_exports`、检查失败或 `mesh.available` 不为真时网格化按不可用置灰。结果 tab 为「结果文件」与「聚合」，按清单区分「未写出点云」和「未写出网格化」。各区块标题不带序号。
- `post/model.ts`、`api.ts`、`post.css`：协议、领域状态和参考图皮肤。
- `files/ArtifactFileTree.tsx`、`artifactTree.ts`、`artifact-file-tree.css`：原始数据、数据准备与后处理共用树，默认收起，点开再取一层且不标选中；`rawprep/BoundDatasetFiles.tsx`输入和处理结果都走这棵树。
- `visualization/PhysicalFilePreview.tsx`：Vis转换后的单文件紧凑视口；`PhysFieldEmbed.tsx`公开追加句柄和可见性通知，创建与追加分离。
- `previews/FilePreviewContent.tsx`支持内联模式及来源切换重置；`TaskWorkbenchPage.tsx`按稳定任务身份挂载，兼容深链接。
- `e2e/post-{workspace,files,session,real}.spec.ts`、`post-fixture.ts`：布局、文件、会话、三维页剩余视口与真实CFD分开验收。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

后处理参考图精修：`post.css` 按内容容器调整横向配置、紧凑指标网格和文件预览比例；共享 `ArtifactFileTree` 提供独立勾选列、展开箭头和文件类型图标。`FilePreviewContent` 的compact网格包装保持伸展，`PhysicalFilePreview` 统一Ant Design控件。`e2e/post-ui.spec.ts` 圈定1440/1920行高、树表溢出、勾选列对齐、浮层关闭及预览放大。证据继续归 `mvp/post-workspace-acceptance.md`。

## 推理工作台选择与统计

2026-09-18 训练监控与推理结果追加：Loss 横轴配置消费 update 曲线，更新步不再是独立 Tab；训练评估复用推理字段/指标选择；checkpoint 结果保留无统计占位，运行状态和后处理数据集过滤沿现有 API 适配器交接。

`src/modules/inference/{FieldPicker,MetricPicker,InferenceSettings,InferenceMetricTable,InferenceCharts,ResultViewSettings}.tsx` 与 `src/modules/inference/useInferenceResults.ts`：四栏、分行推理配置与固定结果视图，标题不带序号；`e2e/inference-{layout,selection,results,usability}.spec.ts`：原图尺寸、配置不溢出、2000样本和真实CFD流程。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。


推理结果视图配置更新：`ResultViewSettings.tsx` 管理表格模式、聚合多选及物理量—指标列；`ChartViewSettings.tsx` 管理 X/Y 轴、刻度、网格线与点数值；`useInferenceResults.ts` 组织固定值与系列联动，并把图表显示选项按任务写入浏览器。指标表 460px、图表区 420px（原 218/194 的 2 倍以上），绘图区随卡片加高。`e2e/inference-results.spec.ts` 覆盖两弹窗、高度与显示选项保存；`e2e/inference-result-views-real.spec.ts` 用真实已完成批次核验两模式、下载及零预测提交。 验收见 `.context/mvp/inference-result-views-acceptance.md`。

`e2e/trame-responsiveness.spec.ts`：实际原始处理/后处理双层 iframe 点击，持续字段/显隐/切片操作、多视图、Tab 保持与配置重开；需要 `DOJO_TRAME_PROJECT/TASK`，不模拟接口。

## 项目共享数据切片

rawprep 复用覆盖弹窗并按来源身份浏览；stages/inputChoices 按项目与共享身份区分，tasks/stages 分开共享可用与本任务处理成功。

长期说明见对应包 PRD；当前证据见 `.context/mvp/task-shared-datasets-acceptance.md`。

## 平台配置生成

`packages/ai4e-web/src/infrastructure/configuration/edits.ts`：两类工作台共用的无业务语义编辑差异，保留空值、删除与字符串数组路径；四页保存回读重置基线。`e2e/configuration-composition.spec.ts`：编辑传输与修订交接。

专项证据：`../mvp/platform-configuration-acceptance.md`。


训练指标与曲线：`TrainingPanel.tsx` 按算法目录保存实际评估选择；`TrainingMonitor.tsx` 提供 Loss／累计更新步／学习率页签及各自空配置面板，独立处理缺失值。圈定 `e2e/execution-monitor.spec.ts`、`e2e/stage-consistency.spec.ts`；发布状态见 `.context/mvp/training-metrics-ui-acceptance.md`。
