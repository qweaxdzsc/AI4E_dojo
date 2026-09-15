# 三维对象工作台验收（2026-09-14）

## 范围与入口

本次在迁入后的 ai4e-viz 上实施对象工作台，没有再次复制 AI4E_Vis。原图表、几何、报告与 Dojo 预览库保留。用户布局参考为 `docs/后处理-三维可视化.png`，现行交互说明为 `docs/三维物理场可视化_UI界面说明.md`。

实现入口：包内 `backend/modules/visPhysField/{commands,scene,rendering,producer}.py`、`trameUI/`；配置在 `visTaskManage/physicalSpec.py`；Vis React 的物理工作台组件及 Dojo visualization 门面。文件说明分别在根与包内 `.context/modules/`。

## UI 与交互

已实现两行工具栏、来源/对象树、单对象属性、草稿应用与切换保留、树行删除图标与依赖确认、复制、重命名、搜索和显隐。嵌入预览贴合父框，文件预览弹窗按视口封顶并可滚动，外框尽量加高；后处理三维页保持 820px 独立滚动窗口，iframe 保底 600px；左下属性加高并可滚动。纯色基础显示由导入创建，着色属于显示属性，没有云图创建按钮或预建物理量资产。

真实浏览器覆盖本地与远程渲染：着色、切面应用、非法法向保留旧结果、切换草稿、三个视图、鼠标旋转/平移/缩放、相机隔离/联动、Probe、时间切换、保存后刷新重开、900/1440/1920 宽度、MP4 下载及 WebM 录制。本地浏览器额外核对序列化相机与实际客户端相机一致；真实表面点击按活动视图建立采样射线。轨道结束只回写相机，不整屏刷新或重读网格，避免工作进程占满 CPU 后点击像没反应。连点切面只保留一份未应用草稿。对象树显隐只改已有 actor。Probe 当前值显示表格，不再使用常驻 JSON 区。JSON 仅在外部配置对话框中编辑。

窄容器将分析创建操作收纳到“更多分析”菜单，标准视角收纳到独立菜单，显示工具自适应收紧，其他菜单承载对象/导出与透明度/比例。Probe 标签按视口投影缩放并限制边界，固定采样位置由引线保留。视觉验证证明主要区域不横向溢出，不声明逐像素复刻原图。

## 物理计算

真实 VTK 解析夹具验证切面→等高线依赖、平面裁剪、矢量箭头、流线计算字段与着色字段独立、等值分析门禁、空结果与非法参数、显示更新不运行过滤器、固定空间 Probe 插值和域外有效性、同名 point/cell 字段、时间缺帧与拓扑变化。

浏览器输入是实际可读的 9×9×9 VTI/PVD 四帧体数据，温度为 x+y+z+3×帧序号，速度为 (1, 0.2y, 0.1z)。这是解析验收数据，不是生产 CFD 结果或训练精度证明。原始数据/预测的既有 VTK、数组和身份读取回归另外执行。

Linux 阴影未在本机 macOS 验收；本地、远程普通光照通过不能代替 Linux 阴影能力结论。

## 多视图与宿主融合

一个 Layout，1–4 窗口按全幅 / 横排 / 上二下一 / 田字格展开，标签叠在对应窗体左上角；每窗口着色/显隐独立。处理结果共享，相机联动默认关闭，开启后全体窗口共用相机，跨来源需要共同坐标声明。

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
