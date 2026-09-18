# 三维对象工作台验收（2026-09-14）

## 范围与入口

本次在迁入后的 ai4e-viz 上实施对象工作台，没有再次复制 AI4E_Vis。原图表、几何、报告与 Dojo 预览库保留。用户布局参考为 `docs/后处理-三维可视化.png`，现行交互说明为 `docs/三维物理场可视化_UI界面说明.md`。

实现入口：包内 `backend/modules/visPhysField/{commands,scene,rendering,producer}.py`、`trameUI/`；配置在 `visTaskManage/physicalSpec.py`；Vis React 的物理工作台组件及 Dojo visualization 门面。文件说明分别在根与包内 `.context/modules/`。

## UI 与交互

已实现两行工具栏、来源/对象树、单对象属性、草稿应用与切换保留、树行删除图标与依赖确认、复制、重命名、搜索和显隐。嵌入预览贴合父框，文件预览弹窗按视口封顶并可滚动，外框尽量加高；后处理三维页相对原 820px 至少加高 40% 并尽量铺满剩余视口，iframe 保底 840px；左下属性加高并可滚动。纯色基础显示由导入创建，着色属于显示属性，没有云图创建按钮或预建物理量资产。

真实浏览器覆盖本地与远程渲染：着色、切面应用、非法法向保留旧结果、切换草稿、三个视图、鼠标旋转/平移/缩放、相机隔离/联动、Probe、时间切换、保存后刷新重开、900/1440/1920 宽度、MP4 下载及 WebM 录制。本地浏览器额外核对序列化相机与实际客户端相机一致；真实表面点击按活动视图建立采样射线。轨道结束只回写相机，不整屏刷新或重读网格，避免工作进程占满 CPU 后点击像没反应。连点切面只保留一份未应用草稿。对象树显隐只改已有 actor。Probe 当前值显示表格，不再使用常驻 JSON 区。JSON 仅在外部配置对话框中编辑。

窄容器将分析创建操作收纳到“更多分析”菜单，标准视角收纳到独立菜单，显示工具自适应收紧，其他菜单承载对象/导出与透明度/比例。Probe 标签按视口投影缩放并限制边界，固定采样位置由引线保留。视觉验证证明主要区域不横向溢出，不声明逐像素复刻原图。

## 物理计算

真实 VTK 解析夹具验证切面→等高线依赖、平面裁剪、矢量箭头、流线计算字段与着色字段独立、等值分析门禁、空结果与非法参数、显示更新不运行过滤器、固定空间 Probe 插值和域外有效性、同名 point/cell 字段、时间缺帧与拓扑变化。

浏览器输入是实际可读的 9×9×9 VTI/PVD 四帧体数据，温度为 x+y+z+3×帧序号，速度为 (1, 0.2y, 0.1z)。这是解析验收数据，不是生产 CFD 结果或训练精度证明。原始数据/预测的既有 VTK、数组和身份读取回归另外执行。

Linux 阴影未在本机 macOS 验收；本地、远程普通光照通过不能代替 Linux 阴影能力结论。

## 多视图与宿主融合

一个 Layout，1–4 窗口按全幅 / 横排 / 上二下一 / 田字格展开，标签叠在对应窗体左上角；每窗口着色/显隐独立。处理结果共享，相机联动默认关闭，开启后全体窗口共用相机，不要求共同坐标空间；现行正文见包内 `docs/PRD/visPhysField.md`。

宿主浏览器 `viz_host_browser.cjs` 覆盖 preview/post/comparison 三种公开微领域调用模式，真实双层 iframe、HTTP/WebSocket、来源追加、保存 r2 后由宿主重绑定并重开；另从真实项目文件页面点击进入。三种组件模式不等于重新执行全部科研阶段页面或完整训练。

会话追加与跨项目拒绝、绑定失败保留场景、两独立进程和相机隔离均有相关测试。满员时回收已无心跳的短空闲会话；宿主重开先关闭再创建，避免占满后不传 embed_url。独立 Vis 的上传/登记选择沿用数据资产模块；保存不触发上传。

## 配置与输出

物理配置 v2 保存固定来源、处理依赖、显示实例、Probe、视图、单 Layout 与实际时间。v1 在内存转换，历史修订及摘要不改写；图表原版本保持。空工作区允许重新导入。

任务目录资产修订、冲突、失败原子提交、缺失来源/修订变化、缓存删除后读回、导出不改变配置摘要与报告固定修订均有测试。PNG、CSV、PNG 序列、MP4、WebM 只在明确请求后产生。输出取消/失败不发布成功清单。

本地及远程 MP4 解码验证：4 帧、1280×720、24 fps；WebM 已实际解码并确认非空、操作前后画面不同。WebM 采用浏览器实际帧时间，媒体元信息可能不提供恒定 fps。单视图跨时间导出另验证每帧选择与分辨率、背景区域，不把布局导出冒充单视图输出。

实际 wheel 安装测试启动独立 CLI、创建会话、保存、关闭后读回重开、PNG 导出下载，并比较安装目录前后所有文件摘要。保存不生成原网格副本、不增加任务版本、不写训练 runs。

## 验证命令与证据

证据目录：`/Users/zonghui/work/project_simulation/dojo_train/phys_workbench_ui/`。

- `backend-tests.log`：41 项圈定后端及包内架构测试通过。
- `integration-tests.log`：27 项宿主绑定、真实 wheel、迁入布局和原预览/管线回归通过。
- `frontend-tests.log`：Vis 前端 13 项契约测试通过。
- `browser.log`、`objects-browser-results.json`、`remote/`：本地/远程对象浏览器。
- `host-browser.log`、`host/host-browser-results.json`：宿主三模式、追加重开和项目文件入口。
- `workbench-1440.png`、`workbench-1920.png`：尺寸与布局；`animation.mp4`、`recording.webm`、`video-validation.json`：真实视频。
- `frontend-build.log`、`web-build.log`、`lint.log`：两前端构建、包间门面检查、改动 Python 格式与静态检查。

复现入口：

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules/test_phys_objects.py packages/ai4e-viz/backend/tests/modules/test_phys_sources.py packages/ai4e-viz/backend/tests/modules/test_phys_filters.py packages/ai4e-viz/backend/tests/modules/test_phys_views.py packages/ai4e-viz/backend/tests/modules/test_phys_timeline.py packages/ai4e-viz/backend/tests/modules/test_phys_session.py packages/ai4e-viz/backend/tests/modules/test_vis_asset_storage.py packages/ai4e-viz/backend/tests/modules/test_vis_exports.py packages/ai4e-viz/backend/tests/modules/test_vis_phys_field.py packages/ai4e-viz/backend/tests/test_architecture.py -q
uv run --no-sync pytest tests/integration/test_viz_host_bindings.py tests/integration/test_viz_installation.py tests/integration/test_viz_migration_layout.py tests/integration/test_viz_file_preview.py tests/integration/test_viz_pipeline.py tests/integration/test_viz_extended.py -q
VIS_EVIDENCE_ROOT=<已登记上下文和四帧数据目录> node tests/integration/viz_objects_browser.cjs
VIS_RENDERER=remote VIS_EVIDENCE_ROOT=<远程证据目录> node tests/integration/viz_objects_browser.cjs
VIS_EVIDENCE_ROOT=<宿主证据目录> node tests/integration/viz_host_browser.cjs
```

旧 `viz_workbench_browser.cjs`、`viz_timeline_browser.cjs` 属于迁移时期界面记录，不作为本次对象 UI 验收入口。当前文件入口由上述新脚本取代，旧记录保留不重写。

## 流线起点与可拖动切面（2026-09-14）

流线可改选线段、球体、平面或命名面；命名面来自对象树表面或授权文件中带名称的二维块/文字分区。应用后同视图显示种子，隐藏流线时种子一起消失。选中切面或剖切时出现可视平面、三向轴手柄和旋转环；拖动或点 X/Y/Z 只回填草稿，点应用才切开。旧流线缺起点类型仍按线段计算。配置版本仍是 2。

圈定后端：

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules/test_phys_filters.py packages/ai4e-viz/backend/tests/modules/test_phys_objects.py packages/ai4e-viz/backend/tests/modules/test_phys_sources.py packages/ai4e-viz/backend/tests/modules/test_phys_session.py packages/ai4e-viz/backend/tests/test_architecture.py -q
```

浏览器在 `tests/integration/viz_objects_browser.cjs` 增加球体/平面/切面种子、隐藏种子、切面拖 X / 点 Y / 旋转后须应用。没有命名块的夹具不得 skip 后声称网格命名面已验收。本地浏览器通过不能代替远程手柄；两边都走同一 `plane_drag` 命令。

本期不做：视口拖动流线种子、独立线/球/面对象、跨网格自动对齐、把无名整数分区当成命名面、拖动过程中持续切开、服务端隐式平面控件作为本地交互。


## 真实 CFD 结果补充验收（2026-09-14）

当前额外验证两份已有后处理比较结果，原文件均只读引用：

- ShapeNet-Car 表面：3,586 点、3,584 单元，选择 pressure.truth 和 pressure.abupt。
- NASA CRM 表面：454,404 点、455,304 单元，选择 cp.truth 和 cp.transolver3。

输入来自外部 dojo-cross-model-50/comparison 的 sample-0/surface.vtp。它们是实际后处理结果文件，规模与字段以本次读取为准；不将它们称为新训练结果或全部原始网格。各案例独立工作区内对同一来源建立两个视图，未做跨网格插值或坐标对齐。色标保持各字段自动范围，截图不作为统一色标下的误差大小比较。

真实浏览器覆盖：纯色基础对象、原点/单元数量、真值与预测分别着色、静态时间门禁、固定原顶点位置 Probe、保存、刷新重开、Probe 字段选择恢复、活动视图 PNG、CSV 下载和数值读回。Probe/CSV 与来源顶点字段误差小于 1e-5；原文件 SHA-256 未变，保存时只产生轻量配置，导出不改变配置摘要。

本次修复的真实问题：Probe 元信息回溯输入；明确 CSV 按钮预选 CSV；单分量 CSV 写数值单元格；恢复相机后重算近远裁剪面并同步浏览器，避免 NASA 机翼与标签被截断。远距离相机单元测试及实际浏览器包围盒裁剪断言覆盖该问题。两个案例的 PNG 和浏览器截图已人工检查完整机体、标签与坐标轴。

证据：`/Users/zonghui/work/project_simulation/dojo_train/phys_workbench_real/`。`inputs.json` 固定来源路径、哈希、规模、两个字段及选定顶点参考值；`results.json` 保存实际 Probe、资产 ID 与配置字节数；`*-workspace.png`、`*-export.png`、`*-probe.csv` 为实际输出。`loaded_ms` 只计到会话与首次元信息查询，不是完整画面传输耗时或 FPS 基准。

新增入口：`tests/integration/viz_real_results_browser.cjs`，使用显式 `VIS_EVIDENCE_ROOT` 和测试服务 `VIS_CONTROL_TOKEN`；输入清单使用上述来源、规模、字段与参考值，真实文件缺失时失败，不合成替代来源。

本轮回归：42 项圈定后端（上一轮 41 项加远距相机用例）、27 项宿主/安装/预览集成、13 项前端契约及包内架构检查通过。真实 wheel 的启动、保存重开和输出复验通过。`remote-regression/` 另记录解析四帧数据的远程完整工作台浏览器、MP4 与 WebM 下载，`output-validation.json` 记录 PNG 尺寸与视频实际解码验证。

范围仍限本机这两份静态表面结果的本地渲染和解析四帧数据的远程回归；本轮未新验收生产体场时序、交互帧率/并发上限或 Linux 阴影，也未重新执行宿主全部科研阶段。


## 参考图视觉校正（2026-09-14）

用户指出旧界面与参考图不符，本轮重新核对图片本身；前面的功能通过记录不代表视觉已符合。新界面保留实际 Trame 工作台，重排蓝白图标工具带、约24%左栏、上下对象/属性分区、紧凑 XYZ 输入、视图标签与深蓝灰画布。嵌入页去掉外围留白，导出状态改为可关闭提示。没有复制参考图的泵模型或预建物理量节点。

色标使用本地与输出原生渲染；同视图多个色标分别排列，避免自动范围不同却叠加刻度。Probe 和时间标签采用屏幕字号，数值仍取原数据。按钮显式保留无障碍名称；窄窗口保留更多分析、标准视角和显示入口。三坐标表单的模型拾取回填同步核验。

证据根：`/Users/zonghui/work/project_simulation/dojo_train/phys_workbench_visual/`。`reference-layout-{1672,1440,1920,900}.png` 为实际浏览器截图；`visual-results.json` 记录区域尺寸、图标解码和横向溢出，脚本额外检查右侧光照按钮可见。1672宽度下标题32px、首行80px、视图工具68px、视口起点约(411,226)，与参考图约(415,231)接近；不宣称逐像素一致。

本轮相关验收：`backend-tests.log` 46项通过（含三个模型尺度/两种分辨率的标签字号与色标不重叠）；`frontend-tests.log` 13项通过；`wheel-tests.log` 真实安装、保存重开、PNG输出与安装目录摘要检查通过。真实 ShapeNet/NASA 的着色、分屏、Probe、保存重开、PNG/CSV 下载见 `real/`；对象交互、草稿、时序、实际录制见 `objects/`。最终 `visual-results.json`、`real/results.json`、`objects/objects-browser-results.json` 与 `objects/remote/objects-browser-results.json` 全部通过；本地/远程 MP4 实际解码均为4帧、1280×720、24fps，WebM均可解码。Linux阴影仍未在本机验收。

## 真实平台默认入口修正（2026-09-14）

用户反馈原始处理 VTK 预览与后处理看不到 Trame。核查确认：平台门面仍默认旧查看器，Trame 需二次启动，后处理保留旧占位布局。此前独立工作台/直接挂载门面的通过记录没有覆盖这个默认路径，不能代替本轮页面验收。

修正后网格预览直接启动 Trame；后处理默认打开空工作台，支持在同一会话中选择受控来源。原始处理页同时修正状态声明分号引发的 `entryEdit is not defined`，保留并行的运行进度改动。原始处理的文件与执行读取经各自公开入口调用。历史旧场景显式兼容；普通张量、文本预览仍保留原行为。

本轮使用正在服务的原平台 `http://127.0.0.1:5173`、项目 abc、任务 as。任务没有后处理运行，因此后处理页通过“文件 → 导入结果”加载同一个原始 `quadpress_smpl.vtk`，不宣称生成或验收了该任务新的预测结果。实际数据为 3,682 点、3,584 单元、`point_scalars`；1440×1000 截图人工核查了真实汽车模型、字段着色、色标、方向轴及 Trame 工具区。没有重新训练或保存新任务版本。

圈定验收：

- `packages/ai4e-web/e2e/trame-entry.spec.ts` 两项：真实原始处理/后处理路由、默认工作台、着色、会话内追加不重建、关闭预览/路由退出释放，以及创建响应迟到时回收。
- 同跑 `http-errors.spec.ts` 七项，合计九项浏览器用例通过，真实用例未跳过。
- `uv run --no-sync pytest tests/integration/test_viz_host_bindings.py -q`：一项通过，覆盖宿主可信来源及追加边界。
- Web 构建、微领域边界检查以及 Vis 前端构建通过。Vis 安装副本已更新供当前服务使用；本轮没有重做历史 wheel 全功能验收，也未改动 VTK 算法。

复现真实入口：设置 `DOJO_TRAME_PROJECT=34f74688805f4d4e815885da04a081d2`、`DOJO_TRAME_TASK=f9fca9f6c4414c17abae50f8713fd86b`，执行上述两个 Playwright 文件。该样本缺失应明确失败，不以合成场景代替。测试只释放自身创建的会话，平台服务保持运行。

证据根：`/Users/zonghui/work/project_simulation/dojo_train/trame-entry/`。`browser.log`、`host-bindings.log`、`build.log`、`architecture.log`、`vis-build.log` 记录结果；`browser/trame-entry-原始VTK预览与后处理默认打开真实Trame/` 下 `raw-vtk-trame.png` 与 `post-import-trame.png` 为最终实际页面截图。这里只证明上述宿主入口修复，其他物理计算、输出与 Linux 阴影范围沿用前文各自记录。

## 2026-09-15 响应诊断（未实施修复）

- 当前用户任务原始处理入口、真实 hexvelo_smpl.vtk，29,498 点/26,112 单元；自动化 Chromium 1920×1080、本地渲染。
- 隐藏：服务端 actor 约 0.2ms 已修改，随后 `_sync_tree_visible` 使用 `State.get()` 抛 TypeError，视口推送未执行。隔离浏览器等待 45 秒不隐藏；实际 5173 入口点击其他对象选择后 90ms 才隐藏。显示同理，后续刷新 67ms 才出现。
- 实际入口首次着色 282ms；连续 12 次纯色/矢量模长切换 149–196ms；简单切片应用 210ms。计时终点是浏览器场景状态，另用截图核对像素；不作为生产性能验收。字段切换历史 30 秒现象本次未复现。
- 切片草稿的树与参数存在，等待后客户端仍无平面手柄；应用后截面与手柄同时出现。
- 旧 `test_phys_objects.py::test_hide_base_display_does_not_rebuild_mesh` 本次 1 passed，但使用字典替身，无法捕获真实 Trame State 不支持 get 的错误；该通过不构成显隐验收。
- 开始时正式 Vis 缺 pandas 启动失败；随后共享环境中依赖已存在，重试实际入口成功。本轮未同步共享依赖或重启正式 Server，环境变化来源未核实。临时诊断服务与本轮会话已回收。
- 证据：`/Users/zonghui/work/project_simulation/dojo_train/trame-response-diagnosis-20260915/`；summary.json、host/、repeated/、server-timing.jsonl。未保存可视化、未导出业务结果、未修改源文件或任务版本。
- 更新计划：[响应与独立显隐](../../.cursor/plans/trame-response-and-independent-visibility.plan.md)。本节是缺陷诊断，不是修复完成或整体 UI 验收。

## 2026-09-15 响应修复与实际 Web iframe 复测

本节接续上面的诊断，记录本次实施。显隐改用真实 Trame State 支持的访问方式，目标 actor、树状态与视口同步失败时恢复并提示；来源分组取消总显隐，父子、祖孙与各视图显示独立。首次切面草稿同步平面手柄，重复点击不增加草稿或整屏推送。样式更新复用 mapper/输入，字段选择缓存按数组修改时间失效；普通鼠标经过不调用后端平面计算或整屏刷新。拖动结束回填完成前坐标输入暂时禁用，非法法向不清除旧结果和旧手柄，修正后可继续应用。

**实际入口与数据**：使用当前 `http://localhost:5173`，项目 `34f74688805f4d4e815885da04a081d2`、任务 `f9fca9f6c4414c17abae50f8713fd86b`，从原始处理文件树点击 `hexvelo_smpl.vtk`，通过 Web → Vis → Trame 双层 iframe 操作。真实体场 29,498 点、26,112 单元，自动化 Chrome、本地渲染；1920×1080 完整操作并核查 1440×1000 截图。没有模拟 API、替换 iframe 或注入合成网格。

**浏览器结果**：`packages/ai4e-web/e2e/trame-responsiveness.spec.ts` 两项通过，共 53.8 秒。字段、显隐、切面草稿和切面应用各连续 30 次，P95 依次为 176、96、137、112 毫秒，最大值为 209、96、145、192 毫秒。计时从点击到浏览器目标 vtk.js 场景状态；字段/显隐/草稿另跨两个绘制帧，应用等待场景加载及已应用状态，不等同 GPU 完成时间。实际拖动后立即编辑 XYZ、零法向错误与恢复、父隐藏子仍显示、子隐藏父仍显示，以及普通鼠标经过没有重复场景推送均通过，页面未捕获脚本异常。

后处理通过真实菜单导入同一份已授权 CFD 原文件，创建双视图、分别着色和设置显隐；切换三个 Tab 十次，iframe 文档、会话、相机和对象保持。显式保存配置、重新打开后独立显隐及相机恢复，离开路由回收测试会话。当前任务没有本次新推理产物，本节不作为推理结果或指标计算验收。截图人工核查左视图仅切面、右视图着色体场，源分组无显隐开关。

**回归与安装**：使用真实 Trame State 与 VTK 数据的 `test_phys_display_updates.py` 共 13 项，覆盖回滚、缓存失效、首次草稿、样式不重算、Probe 和多视图。对象、过滤、来源、视图、时间、会话、资产保存与架构最终圈定 73 项通过，记录于 `backend-verified-final.log`；命令使用 `PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib`，此前未提供包内导入路径的收集失败另留在 `backend-verified.log`，不计作通过。安装及宿主三项通过，记录于 `installation-host.log`，包括实际 wheel 安装后的创建切面、独立显隐保存重开、PNG 导出和安装目录摘要不变。Web 构建及 Web/Vis 前端边界检查单独通过，不替代浏览器结果。并行重构生成的控制器辅助文件补入模块索引，随后清理未使用导入；此整理不改变已验收的业务行为。

最终证据根：`/Users/zonghui/work/project_simulation/dojo_train/trame-response-fix-20260915/`。`verified-web-round2.log`、`verified-web-round2/` 是最终成功浏览器记录，包含完整操作计时、两入口截图、保存重开前后状态；`summary.json` 汇总范围，`installed-fingerprints.json` 核对源码与实际安装文件。原数据及 task.json 哈希仍与 `source-task-before.json` 一致；名称前缀 `响应复测-独立显隐-` 的验收资产仅含 asset.json 与 spec.json，没有自动截图或网格副本。平台服务保持可用；旧会话需关闭预览后重新打开以加载修复代码。

**明确边界**：原始“着色等待 30 秒”未复现，不声称解释了全部历史延迟；已确定并修复的是显隐异常中断、草稿漏推送和不必要更新。未新增生产级分阶段追踪或单独测定 100ms 点击接收指标；本次不验收 Linux 阴影、远程渲染性能或生产大网格并发。过程中共享安装环境及 8000 服务曾变更，导致早期重试出现依赖缺失和宿主 400/500；失败日志保留，不算通过，最终成功记录是在核对修复安装副本并恢复实际主服务后取得。

## 2026-09-16 三维交互、对象隔离与视觉优化

本轮按用户批准的八项计划实施。对象草稿与显示设置由 visPhysField 一起提交；几何/命中/旋转与等值算术仍在 visEngine；配置校验在 visTaskManage；React 宿主不复制业务状态。保存仍走既有可视化修订，不改变训练配置、历史修订或原始网格。

### 已实现行为与根因

- **A/B 平面及交互**：旧边长的 2.5 倍、灰白半透明面、四边框、XYZ 箭头及三轴旋转环。只命中手柄才开始拖动，几何命中前后端一致；拖动基于初始姿态，独立身份拒绝迟到事件，捕获指针并抑制相机和释放后的资产点击。辅助开关按对象/视图保存；隐藏对象或切换选择不残留。窗口 resize 重建注记层曾移除手柄，已补恢复。多 tracker 共用全局拖动状态的问题通过实例归属修复。
- **C 对象属性**：新对象原来只提交计算参数，显示草稿被丢弃。现在创建/更新一起提交计算与显示，失败保留旧结果与草稿，事件携带对象身份；父级着色与 mapper 保持。
- **D 删除**：删除不再整场重建，清理下游、草稿、附件及缓存引用。另在真实宿主复现 Trame 只剩相机时不传 renderer，导致背景消失；序列化适配保留空 renderer、背景、相机与旧资产移除调用。未将用户描述的所有父级异常归因为原数组被污染，原数组污染未独立复现。
- **E 等值颜色**：生成等值面后重新计算插值向量模长不等于生成标量，是颜色变化的一项确定原因。保留生成标量，同字段用上游色域，近常量范围不放大浮点噪声；其他字段仍可独立着色。开启光照时仍有正常明暗变化。
- **F 种子**：线段、球体、平面均可预览轮廓及采样点，不积分；参数、取消、应用及删除交接临时附件；截图发现体网格内部的种子被遮挡，候选预览改用注记层并覆盖 resize 恢复。球体使用独立固定随机序列，避免预览/计算采样点不一致。
- **G 等高线**：默认自动 10 个内部等值级别，可改 1–256 及范围；旧 values 恢复自定义模式；values 与 levels 冲突拒绝，常量场明确报错。
- **H Probe**：新建和拾取即显示金色候选球及坐标，应用后才产生正式采样；取消清除候选附件。正式球与草稿有不同颜色及文字状态。
- **I/J UI 与兼容**：蓝白面板、深色视口、计算/显示/辅助分组、固定应用区与未应用标记；保存只含正式配置及辅助开关，临时预览和选择不进入正式导出。对应模块 PRD、索引、AGENTS、规则与 error.log 已同步；新增测试入口已登记。

### 验收证据

证据根：`/Users/zonghui/work/project_simulation/dojo_train/viz-interaction-20260916/`。`status.txt` / `preexisting.patch` 保存本轮开始时已有修改，本轮未回滚其他工作。`before-user/` 是用户提供的问题截图，明确不是同相机、同场景的自动化像素基线。

- `backend.log`：圈定对象、显示、交互、过滤、配置、存储、导出、契约及架构 **129 passed**（包含新增边界用例）。入口使用 `PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib`。不跑全仓替代专项验收。
- `frontend-test.log`：**14 passed**，包括两个 Trame tracker 的移动/释放归属；`frontend-architecture.log` 与 `frontend-build.log` 通过，构建的大包提示不是功能失败。
- `installation.log`：**2 passed**，真实 wheel 独立目录安装与安装链路测试。最终另构建隔离 wheel（`wheel.log`），真实宿主加载 `/tmp/dojo-viz-eight-evidence/installed-overlay`，不替换共享 `.venv`。
- `host.log` / `host/`：**1 项真实 Dojo → Vis → Trame 双层 iframe 用例通过**。真实体网格 29,498 点 / 26,112 单元，数据来源为现有 CFD `param1/1dc58be25e1b6e5675cad724c63e222e/hexvelo_smpl.vtk`。检查子对象着色、辅助显隐、1440×900 / 1672×941 / 1920×1080 截图、宿主放大、等高线模式切换、真实模型拾取候选球及删除唯一可见对象后相机/renderer 保持。截图 `host-deleted-background.png` 人工确认深色背景，无白屏；`host-probe-candidate.png` 可见候选球及未应用状态。
- `result-local.json` / `result-remote.json` 与对应 log：独立 Vis 正式页面沿平台 `/vis` 代理进入，两种渲染方式真实鼠标平移及旋转，正式对象参数/相机不变，取消可恢复；父子显示隔离、辅助开关、三种种子预览、Probe 初始预览和删除通过。`plane-*`、`seed-*`、`probe-*` 为实际截图。
- `test_phys_interaction.py` 补充等值层数非法边界、常量场与旧表单恢复，独立复测 **18 passed**，结果另见 `additional-boundaries.log`，其中层数与兼容边界已纳入 129 项，随后追加的连续切换形状用例单独通过，合计 130 个不同后端用例。同标量等值面与异字段着色以真实 VTK 数组检验，不凭截图宣称数值一致。

### 范围与运行纪律

本轮服务仅使用 Agent 的 7999；5172 已有其他进程，未占用。正式 8000/5173 未重启、未重装、未发布，因此正式页面不会自动加载本轮代码。安装验证使用隔离目标；本轮会话和 Agent 服务完成后回收。未删除数据库、用户上传或旧源码。

本轮不宣称生产大网格并发、Linux 阴影或远程网络延迟验收。真实浏览器覆盖了平移/旋转代表手柄及当前 CFD 网格，不是所有六手柄×所有相机姿态的穷举；等值颜色正确性用数值回归验证。历史 `viz_objects_browser.cjs` / `viz_visual_browser.cjs` 的六手柄和尺寸检查已更新并检查语法，本轮完整交互和截图执行入口是新增 `viz_interaction_browser.cjs` 与宿主专项；未把旧大脚本未重跑的条目算成本轮通过。修改前截图来自用户，未交付同场景逐像素前后误差指标。


## 第二轮：着色、显示设置及删除同步（2026-09-16）

完整结果、截图、日志和 wheel：`/Users/zonghui/work/project_simulation/dojo_train/viz-display-20260916/README.md`。

- 根因已确认：mapper.ShallowCopy 不替换输入，实际网格缺少着色数组；显式 SetInputData 并保留 mapper 身份。A1 由实际数组、中央模型像素与宿主输入检查验证。
- A2/A3：属性应用/取消、顶部只提交自身字段、自动及自定义范围、视图草稿隔离；显示更新失败恢复旧画面。B1：色标方向/尺寸/字体/位置及配置恢复，本地与远程消费同一声明。
- C1/C2：箭头/圆锥/线段及三类大小模式，零向量、方向/长度、确定性空间分箱与原数组不变检查通过。
- D1/D2：对象级删除、空场景、相机保持及背景设置通过；浏览器最终中央像素为原背景 RGB(36,54,74)。未独立复现另一个“缓存残影”根因，沿用并回归已有删除及空渲染器修复。
- E1：透明PNG经真实页面保存配置后导出下载，alpha读回0–255；PNG序列由真实生产器文件读回验证。MP4拒绝透明请求。
- F1/F2：上一轮专项回归、三尺寸/放大、真实双层iframe通过。源码117项、契约/会话48项、隔离安装107项、前端16项通过，前端架构/构建及本轮源码ruff检查通过。最终wheel有100个源码/构建文件摘要匹配证据。

同步现行PRD、索引、AGENTS与错误记录。纯色/着色截图是本次运行的交互前后对比，未声称同相机的修复前故障像素基线。正式8000/5173未更新；本轮服务由Agent在7999隔离启动，最终回收。正式发布须另获当次授权。Linux阴影、生产并发及穷举相机姿态仍不在本轮验收声明内。


## 正式接入（2026-09-17，用户本轮授权）

用户明确要求将此前全部修复接入正式服务。此前源码和隔离安装通过，但正式 `.venv` 安装副本仍旧，六项针对性回归在旧安装全部失败；这是页面未生效的已确认原因。

本轮更新正式 `ai4e-viz`，保留 dev/visualization 依赖组；预检发现普通 sync 会同时更新其他工作中的 contrib，因此使用 `--no-install-package ai4e-contrib --inexact` 保留该包，实际仅替换 viz。安装后的 100 个后端和前端构建文件与先前验收摘要全部相同。只回收正式 8000 所属旧 Vis 39556；8000 主进程 39267、5173 及其他服务保持运行。通过正式任务接口自动拉起新版 Vis 76660。

正式安装专项 `test_phys_display_updates.py`、`test_phys_interaction.py`、`test_phys_display_settings.py` 共 63 项通过。通过 8000 正式任务会话加载用户 CFD 体网格（29498 点、26112 单元），执行着色、范围、色标、背景与删除命令，确认对象/图层清空且相机和背景声明保持；验证会话已关闭。5173 的工作台页面及 JS/CSS 返回 200，实际返回字节与新版安装构建一致。证据位于 `/Users/zonghui/work/project_simulation/dojo_train/viz-display-20260916/formal-audit/` 的 `published-tests.log`、`published-api.json`、`published-web-assets.json`。

发布状态：两轮修复已进入正式安装及正式 Web 资源，新开的三维会话使用新版。旧三维窗口需要关闭后重新打开。验收边界：本轮浏览器连接报 apikey 认证不支持，原生 Chrome 操作因用户切换窗口被中止，尚未完成新版正式页面逐项点击及像素复验；不得将接口与安装回归称为正式浏览器全部通过。先前隔离浏览器证据保留原范围。


## 自定义范围预填与色标默认（2026-09-17）

切到自定义范围时预填该对象、视图、物理量上次应用的上下限；还没有记忆则填当前自动最小、最大。未写过色标样式时标题字号、厚度、刻度字号默认都是 25。圈定 `packages/ai4e-viz/backend/tests/modules/test_phys_display_settings.py`。源码改动不自动进入正式 8000；未获当次同意不 `uv sync`、不重启正式入口。

## 三维工作台十二项优化（2026-09-17）

属性行与透明度对齐；色标改到右上角弹窗即时提交；纯色可选颜色。矢量图只留形状和固定/物理量，圆锥线段不再因箭头尺寸报错。等高线界面去掉自定义等值并增加线宽，旧列表仍能打开。切面手柄服务端确认后才锁旋转，滚轮始终缩放，六面体交面保留多边形。本地窗口坐标轴跟随主相机；关闭种子预览撤下预览附件，已应用后不再显示该按钮。

圈定：

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules/test_phys_display_settings.py packages/ai4e-viz/backend/tests/modules/test_phys_filters.py packages/ai4e-viz/backend/tests/modules/test_phys_interaction.py packages/ai4e-viz/backend/tests/modules/test_phys_views.py
```

以及 `packages/ai4e-viz/frontend/src/test/interaction.test.js`。圈定后端 74 项与前端 `interaction.test.js` 3 项已通过。

发布（2026-09-17，用户当次同意重装）：`uv sync --group dev --group visualization --reinstall-package ai4e-viz --no-install-package ai4e-contrib --inexact`。安装副本与源码五项关键文件一致。只回收正式 8000 所属旧 Vis 16753；8000 主进程 16491、5173 的 15396 保持运行。新 Vis 20654 监听 51573。contrib 仍为可编辑安装，trame 仍在环境中。

正式 `5173` 打开「真实 CFD 推理验收 / Transolver 推理」后处理三维页，200。经正式任务接口加载用户 CFD 体网格（29498 点、26112 单元），着色、纯色、色标样式、圆锥矢量、自动等高线与线宽 4、切面均写入并保存为 `viz-7c5a8ca5ed2c4ea2804f839a01bf787a`；重开后纯色 `[1,0,0]`、色标字号 18、圆锥形状和线宽 4 仍在。浏览器逐项点验：属性透明度有名称、纯色选色、右上角色标弹窗（显示/方向/长度/厚度/字号/位置）、矢量只留形状和固定/物理量且无箭头尺寸、等高线无自定义等值且线宽为 4、切面六轴手柄可见、未应用流线有「预览种子」。证据：`/Users/zonghui/work/project_simulation/dojo_train/viz-workbench-12-20260917/`。

发布状态：已进入正式安装与正式 Web。旧三维窗口须关闭后重开。8000/5173 主进程未重启。

## 三维工作台十一项增强（2026-09-17）

本轮曾把「应用后不能拖种子」改成草稿期可拖。2026-09-17 再次改回：线段/球体/平面移动手柄暂时去掉，草稿期也不拖种子。十二项其余条目仍按原日期保留。

### 范围

Surface LIC 显示模式与按需远程窗口；LIC 方向用点向量，着色物理量即时/应用后跟随新标量或向量幅值/分量，不再保持纯色。辅助平面滚轮不再回弹；切面皱折/三角化、剖切皱折；已应用流线「显示种子」；草稿种子手柄已撤下；导入在任务产物、共享数据集、已挂数据根内选可视化网格；等值面滑条按所选物理量实际标量范围（不是归一化 0–1）与越界手填；自定义色标允许最小等于最大；Probe 即刻出球、应用后标签改表；分析图标缩小并新增线段提取。

### 圈定命令

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib \
  packages/ai4e-viz/backend/tests/modules/test_phys_display_settings.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_filters.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_interaction.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_views.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_objects.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_plot_over_line.py
uv run --no-sync pytest tests/integration/test_viz_host_bindings.py
npm test --prefix packages/ai4e-viz/frontend -- src/test/interaction.test.js
```

### 源码验收

圈定后端与宿主 **121 passed**（含 LIC 拒绝/远程切换与保存重开、皱折切面、种子显隐与草稿手柄、等值越界、色标相等、Probe 表、线段提取、来源列表）。前端 `interaction.test.js` **4 passed**，含滚轮保护。包内 PRD 六节结构与根导航链接核对通过。功能正文只在包内 PRD，本记录不另写第二套说明。`test_architecture_alignment_documents.py::test_inventory_includes_runtime_declarations_and_ui_sources` 因历史路径 `recipes/aero_cfd/task-entry.json` 不在现行盘点中失败，与本切片无关，未计入通过。

### 发布与正式冒烟

- 目标：正式 `http://127.0.0.1:5173` 后处理三维页，接口 `http://127.0.0.1:8000`
- 发布方式：须当次同意后 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`；服务或 Web 有改动再重装对应包并构建前端；同意后重启 8000 或只回收其 Vis
- 本会话：未获正式 8000/5173 安装或重启授权
- 状态：**待发布 / 待正式验收**
- 回退：恢复上一份已安装可视化包，再按同样方式重启 Vis

未验证：正式页面逐项点击 LIC、滚轮、皱折、藏种子、导入两边目录、等值滑条、色标相等、Probe 表、图标大小、线段提取；保存后重开与导出读回。接口 200 与单测通过不能代替上述冒烟。

## 辅助平面轨道相机（2026-09-17）

添加辅助平面后，旋转、平移、缩放都不得回到添加时的固定视角。产品规则是按下分类，不是事后复原：点住手柄只改平面；滚轮和拖空白只改本地视角。几何刷新包默认不含相机，平面出现或变色不得夹带视角。圈定 `test_phys_interaction.py` 与 `packages/ai4e-viz/frontend/src/test/interaction.test.js`。正式 8000/5173 须当次重装并重启 Vis 后才能冒烟，未重启不得验收。

## 默认光照对齐 ParaView Light Kit（2026-09-17）

三维默认光照改为 VTK/ParaView `vtkLightKit` 五灯套件（主光 0.75，K:F=3、K:B=3.5、K:H=3），关掉自动单头灯；阴影默认仍关。旧修订缺键按新默认读，不回写历史 spec。不改十一项历史 plan。圈定 `test_vis_engine.py`、`test_phys_display_settings.py`。安装副本重装后须用户重启 8000 或回收旧 Vis，关掉三维窗口再开，才能做正式 5173→8000 冒烟。

## Probe 点选拾取可见开关（2026-09-17）

Probe「在模型上拾取位置」改为属性区可见的「点选拾取」开/关，不是新的分析工具。开着点模型立刻出球，应用后按所选物理量出表；关着点击模型走轨道，不误出球。切到切面/流线/旋转等其他操作会关掉点选，开关与后台是否接受拾取一致。旧修订缺 `pick_enabled` 视为关，不回写历史 spec。圈定 `test_phys_interaction.py`。已执行安装重装，正式 8000/5173 **未重启、未做正式冒烟，未验收**。

## Surface LIC 着色联动（2026-09-17）

换着色物理量后，LIC 颜色跟随新标量或向量幅值/分量，方向仍用点向量，不再保持纯色。圈定 `test_phys_display_settings.py`、`test_phys_views.py` **49 passed**。已执行 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`，安装副本与源码四份关键文件一致。正式 8000 PID 23591、Vis 58724 仍是重装前进程，**未重启、未做正式 5173→8000 冒烟，未验收**。

## 线段提取 Line Chart View（2026-09-17）

对齐 ParaView Plot Over Line + Line Chart View：线段提取是对象树独立对象；起点/终点/分辨率须应用，**不提供视口拖线**。应用后打开或激活折线图视口；新增窗口可选「三维渲染」或「折线图」。属性 X 轴为弧长 / 序号 / Points_X|Y|Z / 已取样场，Y 轴多选物理量，当前折线图视口改轴立即更新。CSV 导出当前图 X+Y，可下载读回。旧修订缺视口类型或轴字段按三维渲染、X=弧长、Y=第一条标量读取，不回写历史 spec。不改十一项历史 plan。

圈定 `test_phys_plot_over_line.py`、`test_phys_views.py`、`test_phys_display_settings.py` 及 `test_architecture.py` **67 passed**；回归 `test_phys_filters.py`、`test_phys_objects.py` **42 passed**。功能正文只在包内 PRD。

- 目标：正式 `http://127.0.0.1:5173` 后处理三维页，接口 `http://127.0.0.1:8000`
- 发布方式：`uv sync --group dev --group visualization --reinstall-package ai4e-viz` 后须用户重启 8000 或回收旧 Vis
- 状态：**安装已更新；未重启 8000 则未验收**
- 回退：恢复上一份已安装可视化包，再按同样方式重启 Vis

## 工作台小修复收口（2026-09-17）

从光照到折线图的源码与圈定用例已齐。本轮补强：按下先分类（点住手柄只改平面，滚轮/拖空白只改本地视角）；几何刷新默认不夹带相机；删除平面移动里线/种子死分支。折线图视口、X/Y、CSV 仍按上节。不改十一项历史 plan。

### 圈定命令

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib \
  packages/ai4e-viz/backend/tests/modules/test_phys_display_settings.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_filters.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_interaction.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_views.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_objects.py \
  packages/ai4e-viz/backend/tests/modules/test_phys_plot_over_line.py \
  packages/ai4e-viz/backend/tests/modules/test_vis_engine.py
uv run --no-sync pytest tests/integration/test_viz_host_bindings.py
npm test --prefix packages/ai4e-viz/frontend -- src/test/interaction.test.js
```

### 源码验收

圈定后端 **135 passed**（光照、相机不夹带、LIC 换场、等值范围、Probe 点选、流线线/圆管、无种子/线拖动、折线图视口/改轴/CSV）。宿主 `test_viz_host_bindings.py` **3 passed**。前端 `interaction.test.js` **6 passed**（含几何重载不得用旧 `render_cameras` 盖轨道）。功能正文只在包内 PRD。

### 发布与正式冒烟

- 目标：正式 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`
- 页面：`/projects/cfaa5a5281524be2a0200e41f657dd63/tasks/9211b435b2244a85a60ce177b7a39991/post`，可视化「十二项优化冒烟」
- 发布：16:04 装过一版；正式冒烟复现「扫平面弹回」后补前端 epoch 守卫，**16:24** 再执行 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`。安装副本 `interaction.js` 摘要 `c712c3e9527bb8f6`（含 `applyPushedCameras`），`controller.py` 仍为 `c601c377283a4d78`
- 进程：用户授权后重启正式 `8000`，Python PID **78186** 于 16:24:55 起来，`GET /api/v1/health` 为 `ok`。`5173` 仍是原 node PID **23629**，未动。当前 Vis 子进程 PID **93780**（8000 的子进程）
- 证据目录：`/Users/zonghui/work/project_simulation/dojo_train/viz-workbench-close-20260917/`（`official-smoke.mjs`、`followup-smoke.mjs`、`results.json`、`followup.json`、截图 01–08）
- 状态：**正式 5173→8000 已由 Agent 点验**（隔离 7999/5172 未当作证据）

| 项 | 结果 | 证据 |
| --- | --- | --- |
| 辅助平面不锁视角 | **通过** | 加切面后轨道 `moved=true`；扫平面 hover 位姿与轨道相同，不再弹回添加时相机。`02-plane-orbit.png` 为转过后的顶视+手柄 |
| 保存后再转 | **通过** | 保存后再次转视角并扫平面，hover 未弹回 |
| 光照 | **通过** | 有「光照设置」入口；`02` 六面体有明暗，不是整面死黑 |
| Surface LIC | **通过（入口）** | 显示模式菜单含 Surface LIC。本页未改着色场，换场着色以圈定测试为准 |
| 等值滑条 | **本任务不适用** | ShapeNet 表面六面体，等值面按钮不可用。滑条物理量范围见圈定测试 |
| Probe 点选拾取 | **通过** | `06-probe.png`：属性「点选拾取」开/关可见，当时为关 |
| 流线 | **部分通过** | 第一次冒烟已建「流线-1」，种子类型线段/球体/平面可见，视口无拖动手柄（`05-line-chart.png`）。补点时 Probe 选中使分析按钮不可用，显示区「线/圆管」未再展开 |
| 折线图 | **通过** | `08-plot-over-line.png`：LineChartView2 画出曲线，X 为弧长、Y 为 `point_vectors`，有「导出 CSV」。本次未下载读回文件 |

首轮换进程后的冒烟曾失败：hover 精确弹回添加切面时的 `render_cameras`。根因是 LocalView `after_scene_loaded` → `phys-scene-ready` → `syncCameras` 无条件盖位姿。已改为只在 `render_cameras` 真正推过新位姿时同步。

- 回退：恢复上一份已安装可视化包，再按同样方式重启 8000 / Vis

## 流线去拖动、形状与坐标轴实时（2026-09-17）

流线线段/球体/平面的移动手柄暂时去掉，草稿期也不拖种子、不拖线、不拖平面手柄。保留添加流线、选种子类型、预览种子按钮和应用生成；已应用「显示种子」显隐仍可用。本地左下角坐标轴在轨道过程中跟随当前本地相机，不只等 pointerup / EndAnimation，不以 `render_cameras` 为实时源。流线显示可选线或圆管，可调粗细；圆管可调圆周面数 3–64。`style.streamline` 缺键按线、细、8 面读取，不回写历史。圈定 `test_phys_filters.py`、`test_phys_display_settings.py`、`test_phys_interaction.py` 与前端 `interaction.test.js`。安装副本更新后须用户重启 8000 或回收旧 Vis，**未重启则未验收**。

## 工作台色标、Probe 与视图联动（2026-09-17）

色标入口在左栏「显示设置」图标，弹层标题带当前对象名，改完点「应用」才写入该对象；右上角不再放色标设置。位置是字段旁的普通下拉。Probe「点选拾取」只留一个开关。新建窗口加号与分割菜单贴在按钮旁边。点窗即活跃，左侧眼睛跟随该窗，不重读网格。折线图活跃时树只列出线段提取。线段提取去掉取样物理量，新应用取全部场，旧 `fields` 只读。

圈定 `test_phys_display_settings.py`、`test_phys_interaction.py`、`test_phys_display_updates.py`、`test_phys_plot_over_line.py`、`test_phys_views.py` 与前端 `interaction.test.js`。2026-09-17 源码圈定 **109 passed**，前端 `interaction.test.js` **7 passed**。源码测过不等于正式生效。

- 目标：正式 `http://127.0.0.1:5173` → `http://127.0.0.1:8000` 后处理三维页
- 页面：`/projects/7142b2dc062e4808a1686795076b8028/tasks/9c1dac251856411d9091d8d1cc60bc3e/post?tab=visualization`
- 资产：`40efd349…` / 修订 `fd24345d…`（首页任务已有 ShapeNet 表面，3682 点 / 3584 单元）
- 发布：用户授权后执行 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`；正式 8000 于约 17:17 重启为 PID **10303**，随后因色标 `menu_props` 把 Python `True` 泄漏进 Vue 再重装一次并回收 Vis。`5173` 仍是 node PID **23629**，未动
- 安装副本与源码一致：`toolbar.py` `f1b6ab43949979a4`，`controller.py` `cd480def86174308`，`propertiesPanel.py` `6086f40d36e5612e`，`viewportGrid.py` `b9bbb5f5c7c616ac`
- 进程：`GET /api/v1/health` 为 `ok`。当前 Vis 子进程 PID **27954**，端口 62633
- 会话：宿主页 `7679693d06924baaa109a1ffba9cc22a`（context `238f2f01…`）；Playwright 另开 `a0eca14ce8a34b3a8e8752ea1352345d`
- 证据：`/Users/zonghui/work/project_simulation/dojo_train/viz-ui-link-20260917/`（`formal-smoke.mjs` / `formal-smoke.json`、`shots/01–07`、`official-host/`）
- 时间：2026-09-17 17:38–17:44（CST）
- 状态：**正式 5173→8000 已由 Agent 点验**（隔离 7999/5172 未当作证据）

用户指出色标窗体偏空、位置列表飘到左侧后，源码改为属性卡描边/标题条/紧行距，位置改为字段旁普通下拉。2026-09-17 **17:59** 授权后再次 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`，安装副本 `toolbar.py` `5b128939af950650`、`workbench.css` `10406ef150412509` 与源码一致。正式 8000 保持 PID **46982**，回收旧 Vis 47003；新 Vis PID **50229** 端口 63401。5173 仍是 **23629**。18:00 在同一后处理三维页点验：弹层 7 行、宽 268、标题条 29px；位置「左侧」选项与字段同列 x=1248、在其下方 y=673，不再落到左栏。会话 `d0dd4743cabc4f768011189cb01d49ed`。证据 `legend-style-smoke.mjs`、`legend-style.json`、`legend-style/01-legend-card.png`、`legend-style/02-position-dropdown.png`。该样式修正 **已在正式入口生效**。色标下移到属性区并改为「应用」后写入当前对象，为随后源码修正，**须再重装并换 Vis 后才算正式生效**。
- 回退：重装实施前的 `ai4e-viz` 并同样回收 Vis

| 项 | 结果 | 证据 |
| --- | --- | --- |
| A 色标属性行与位置下拉 | **通过** | 弹层 7 行：显示色标 / 方向 / 长度比例 / 厚度 / 标题字号 / 刻度字号 / 位置。`shots/02-colorbar-position.png` 可选右侧/左侧/顶部/底部/自定义，并改到左侧。下拉挂到 iframe `body`，不被卡片裁切；1672 截图里列表画在窗口左侧，不挡卡片内控件 |
| B Probe 点选只留一个开关 | **通过** | `official-host/B-probe-switch.png`、`shots/03-probe-switch.png`：属性「点选拾取」仅一行一个开关，无重复按钮/提示条；可拨到开 |
| C 加号菜单贴按钮 | **通过** | Playwright 加号 `(696,533)`，菜单「三维渲染」`(696,570)`。随后出现 RenderView2（`shots/05-click-window.png`） |
| D 点窗切活跃并刷新树 | **通过** | `shots/05-click-window.png` 双三维窗；宿主页点 LineChartView2 后 `active_view=1`，树从「基础显示 / Probe」换成只剩线段提取，未重开页面、未重读网格 |
| E 折线图树只列线段提取 | **通过** | 应用「线段提取 1」后切到 LineChartView2：树节点为来源行 + `线段提取 1`，无基础显示/Probe/切面。`official-host/E-line-chart-tree.png`。首轮 Playwright 误把占位文案「将在此显示折线图」当成已切窗，`shots/07` 仍停在三维树，不作为本项失败 |
| F 无取样物理量 | **通过** | Probe / 线段提取属性均无「取样物理量」；线段提取为起点/终点/分辨率与折线 X 轴 |

首轮工作台空白的根因是 `toolbar.py` 把 `menu_props=(_LEGEND_SELECT_MENU,)` 写成内联字面量，Vue 收到 Python `True` 后 `ReferenceError: True is not defined`。随后改为命名状态；用户指出位置列表飘到左侧后，已去掉 `attach=body`，改为字段旁普通下拉，窗体改成左栏属性卡样式。17:59 已重装并换 Vis，18:00 正式页点验通过。

本页 LineChartView2 仍是空图占位（`has_chart=false`，`y_arrays` 为空）。树过滤与属性已按本轮范围验收，不把空折线画成曲线导出验收。

首轮 `formal-smoke.mjs` 在 True 泄漏修复前 90s 等不到「基础显示」，`shots/99-fatal.png` 作废。

## Surface LIC 远程交接防崩（2026-09-17）

选 Surface LIC 不得弄死可视化会话。能生成时先出远程静帧再拖转；无点向量、建图失败或第一帧失败只提示「无法生成 Surface LIC」或「请选择三维点向量场…」，画面停在原来的表面/网格。交接未完成时拖转/滚轮不进远程交互。切回表面后回到本地窗口。

圈定 `test_phys_display_settings.py`、`test_phys_display_updates.py`、`test_phys_views.py` 与前端 `interaction.test.js`。原生段错误无法用 pytest 代替正式页点验。源码圈定 **70 passed**，前端 `interaction.test.js` **8 passed**。

- 目标：正式 `http://127.0.0.1:5173` → `http://127.0.0.1:8000` 后处理三维页
- 页面：`/projects/7142b2dc062e4808a1686795076b8028/tasks/9c1dac251856411d9091d8d1cc60bc3e/post?tab=visualization`
- 资产：`40efd349…` / 修订 `fd24345d…`（首页任务已有 ShapeNet 表面；该网格无三维点向量）
- 发布：2026-09-17 用户授权后执行 `uv sync --group dev --group visualization --reinstall-package ai4e-viz`。安装副本与源码一致：`controller.py` `cde753fd42f3b1a0`、`viewportGrid.py` `5c93a28645ed936e`、`interaction.js` `de17b5d3b4f11c28`、`workbench.css` `1d45fbb6a251cc6d`
- 进程：`GET /api/v1/health` 为 `ok`。正式 8000 PID **95113**（18:41:22 起，官方 platform 参数未改）。5173 仍是 node PID **23629**，未重启。旧 Vis 50229 已不在；新 Vis PID **96966** 端口 64260
- 会话：`fa2a4c27a9e14cd685525007254c05b8`
- 冒烟时间：2026-09-17 约 18:42（CST）
- 证据：`/Users/zonghui/work/project_simulation/dojo_train/viz-lic-handoff-20260917/`（`lic-handoff-smoke.mjs`、`lic-handoff.json`、`shots/01-before.png`、`shots/02-after-lic.png`）
- 状态：**正式 5173→8000 已由 Agent 点验**（隔离 7999/5172 未当作证据）
- 回退：重装上一份 `ai4e-viz` 并同样换 Vis

| 项 | 结果 | 证据 |
| --- | --- | --- |
| B 点 Surface LIC 后会话仍在 | **通过** | 点显示模式 → Surface LIC 后宿主 iframe 仍在；Vis 96966 仍在；8000=95113、5173=23629 |
| A1 无点向量只提示、不切远程 | **通过** | 页底提示「请选择三维点向量场才能使用 Surface LIC」；属性无 Surface LIC 段，模式仍是表面；`shots/02-after-lic.png` |
| A 有向量先静帧再拖转 | **未验证** | 首页任务这份 ShapeNet 表面没有三维点向量，官方页走失败提示路径，不能冒充出图成功 |
| 色标入口（顺带） | **可见** | 属性「显示设置」旁仍有色标图标，本轮未再改色标 |

## 相机联动不再要求共同坐标空间（2026-09-17）

开启「相机联动」后，当前工作台全部窗口共用相机；缺坐标空间声明或跨来源不再弹出 `camera_link_requires_common_coordinate_space`。已声明单位不一致只提示。非法来源、跨项目、符号链接门禁不变。包内正文见 `packages/ai4e-viz/docs/PRD/visPhysField.md`。圈定 `test_phys_views.py`、`test_phys_session.py`、前端 `interaction.test.js`；宿主旧查看器语义见 `packages/ai4e-web/e2e/visualization-camera.spec.ts`。

正式 5173→8000 冒烟（2026-09-17 20:51–20:52，用户当次授权重装 `ai4e-viz` 并重启 8000）：入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，任务 `7142b2dc…` / `9c1dac25…` 后处理三维页。安装 `scene.py` `bf008c274581c4df`。正式 8000 PID **6975**、Vis **7457** 端口 50759，会话 `fc293cff64154c499ec1eb94905aa7a9`。空工作台新建窗口得到 RenderView2，打开「相机联动」无共同坐标空间报错；空场景无单位提示。证据：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/official-20260917-2052-camera-link.png`、`official-20260917-2054-smoke.json`。未把网格导入双窗后再拖轨道，不冒充跨单位提示路径。
