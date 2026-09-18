# visPhysField 一级模块文件索引

职责：三维物理场显示、数据提取、数据概览及统一 Trame 会话。PRD：[`visPhysField.md`](../../docs/PRD/visPhysField.md)。二级模块完整索引见 [`visPhysField/index.md`](visPhysField/index.md)。

## 模块设计

`visPhysField`是一个大型一级限界上下文，以物理场会话/显示配置为聚合边界。一级API、Application、Repository和Trame适配统一承载事务、连接和公开协议，三个二级业务只实现领域能力；纯VTK/数值计算可调用`visEngine`公开内核，但云图、时序、Probe和多结果等业务语义必须留在本模块。调用方向为`api → application → modules/<business> → visEngine(可选)/repository`。

## 后端一级基座

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visPhysField/__init__.py) | 物理场公开应用门面 |
| [`api.py`](../../backend/modules/visPhysField/api.py) | 一级物理场 Router |
| [`application.py`](../../backend/modules/visPhysField/application.py) | 二级业务、Engine 与持久化用例编排 |
| [`domain.py`](../../backend/modules/visPhysField/domain.py) | 公共物理场模型、命令和规则 |
| [`repository.py`](../../backend/modules/visPhysField/repository.py) | 模块持久化、SQL 和事务边界 |
| [`trame.py`](../../backend/modules/visPhysField/trame.py) | 一级 Trame 状态与连接适配 |
| [`trameServer.py`](../../backend/modules/visPhysField/trameServer.py) | 九类场景统一 Trame 进程入口 |
| [`modules/__init__.py`](../../backend/modules/visPhysField/modules/__init__.py) | 二级业务包声明，不作为独立门面 |

## 前端一级基座

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/visPhysField/index.js) | 物理场跨模块公开门面 |
| [`module.js`](../../frontend/src/modules/visPhysField/module.js) | 一级工作区路由元数据 |
| [`model.js`](../../frontend/src/modules/visPhysField/model.js) | 一级物理场状态与命令模型 |
| [`api.js`](../../frontend/src/modules/visPhysField/api.js) | 一级 Endpoint、请求和 DTO 转换 |
| [`hooks/usePhysField.js`](../../frontend/src/modules/visPhysField/hooks/usePhysField.js) | 一级 Query/Command/连接状态编排 |
| [`components/PhysFieldProvider.jsx`](../../frontend/src/modules/visPhysField/components/PhysFieldProvider.jsx) | 二级模块共享状态与动作 Provider |
| [`components/PhysFieldViewport.jsx`](../../frontend/src/modules/visPhysField/components/PhysFieldViewport.jsx) | 统一物理场视口 |
| [`components/PhysFieldViewport.module.css`](../../frontend/src/modules/visPhysField/components/PhysFieldViewport.module.css) | 视口局部样式 |
| [`pages/PhysFieldWorkspacePage.jsx`](../../frontend/src/modules/visPhysField/pages/PhysFieldWorkspacePage.jsx) | 组合三个二级业务的工作区页面 |

测试：[`test_vis_phys_field.py`](../../backend/tests/modules/test_vis_phys_field.py)、[`test_miller_animation.py`](../../backend/tests/test_miller_animation.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)及桌面/移动Trame E2E。

## Dojo 当前实现文件

- `backend/modules/visPhysField/__init__.py`：三维物理场可视化一级模块公开门面。
- `backend/modules/visPhysField/api.py`：三维物理场统一HTTP适配层。
- `backend/modules/visPhysField/application.py`：三维物理场一级应用门面。
- `backend/modules/visPhysField/domain.py`：三维物理场一级共享领域对象和不变量。
- `backend/modules/visPhysField/exampleScenes.py`：AI4E VizReport — trame 3D 可视化服务（FLD / ENT）
- `backend/modules/visPhysField/modules/__init__.py`：三维物理场二级业务集合；所有目录共享一级技术基座。
- `backend/modules/visPhysField/modules/dataExtraction/__init__.py`：数据提取二级业务：空间、时序和聚合提取。
- `backend/modules/visPhysField/modules/dataExtraction/aggregate.py`：聚合提取方法和空值策略业务规则。
- `backend/modules/visPhysField/modules/dataExtraction/spatial.py`：点、线、面和体空间提取业务规则。
- `backend/modules/visPhysField/modules/dataExtraction/temporal.py`：时序提取范围和步长业务规则。
- `backend/modules/visPhysField/modules/dataOverview/__init__.py`：数据概览二级业务：二维表格、基础图表和多维云图。
- `backend/modules/visPhysField/modules/dataOverview/basicCharts.py`：散点图、折线图和柱状图字段映射业务规则。
- `backend/modules/visPhysField/modules/dataOverview/lineChart.py`：Plot Over Line 的 Line Chart View 轴映射、视口折线与 CSV。
- `backend/modules/visPhysField/modules/dataOverview/multiDimensionalCloud.py`：多维云图维度和颜色字段业务规则。
- `backend/modules/visPhysField/modules/dataOverview/table.py`：二维表格分页、字段选择和抽样业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/__init__.py`：物理场展示二级业务：视图、云图、矢量、分析、时序和多结果。
- `backend/modules/visPhysField/modules/fieldVisualization/animation.py`：动画录制请求和输出格式业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/colorMapping.py`：颜色带、离散层级和范围映射业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/cutAnalysis.py`：切面、流线、等值面和等高线分析业务对象。
- `backend/modules/visPhysField/modules/fieldVisualization/displayStyle.py`：透明度、面/网格模式、光照和阴影业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/multiResult.py`：多结果导入、多窗口、统一视角和显隐业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/probe.py`：Probe点选和采样业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/scalarCloud.py`：标量云图、层数、范围和调用配置业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/timeline.py`：时序播放、前进、倒退、暂停和循环业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/timelineAnimation.py`：Miller时序物理场的VTK场景与标量缓冲区原位更新。
- `backend/modules/visPhysField/modules/fieldVisualization/vectorField.py`：矢量箭头、流线密度和缩放业务规则。
- `backend/modules/visPhysField/modules/fieldVisualization/view.py`：旋转、平移、缩放、坐标轴、标准视图和适合窗口业务规则。
- `backend/modules/visPhysField/producer.py`：物理场输出生产器，只在显式请求时写入分配的暂存目录。
- `backend/modules/visPhysField/repository.py`：三维物理场配置与结果索引的Repository边界。
- `backend/modules/visPhysField/scene.py`：声明式场景装配；一次 Apply 成功后才替换现有视图。解析流线种子网格，选中切面时挂可视平面附件；LIC 层切换远程出图，种子附件受 `seeds_visible` 约束。持久渲染器默认挂 ParaView Light Kit，阴影缺省关闭。相机联动覆盖当前全部窗口，不因缺少共同坐标空间拒绝；单位不一致只进 `camera_link_notice`。
- `backend/modules/visPhysField/session.py`：独立物理场工作区监督；VTK 对象绝不在工作区之间共享。
- `backend/modules/visPhysField/trame.py`：三维物理场统一Trame会话适配器。
- `backend/modules/visPhysField/trameServer.py`：旧示例服务兼容入口；仅显式启动时创建九类场景。
- `backend/modules/visPhysField/trameUI/__init__.py`：一级物理场 UI 适配；共享同一会话与命令入口。
- `backend/modules/visPhysField/trameUI/layout.py`：ParaView 风格工作台，数据树、Apply 属性、视口、提取和时间轴。
- `backend/modules/visPhysField/worker.py`：工作进程主线程拥有全部 VTK 对象，Trame 和 IPC 共用事件循环。
- `frontend/src/modules/visPhysField/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/components/PhysFieldProvider.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/components/PhysFieldViewport.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/components/PhysFieldViewport.module.css`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/hooks/usePhysField.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/module.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataExtraction/components/DataExtractionPanel.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataExtraction/hooks/useDataExtraction.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataExtraction/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataOverview/components/DataOverviewTable.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataOverview/hooks/useDataOverview.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/dataOverview/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/fieldVisualization/components/ViewControls.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/fieldVisualization/hooks/useFieldView.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/modules/fieldVisualization/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visPhysField/pages/PhysFieldWorkspacePage.jsx`：独立应用交互与调用适配。

迁移时期浏览器入口（旧 UI）：tests/integration/viz_workbench_browser.cjs（本地/远程、真实像素视频、拾取、Probe、切面）；viz_timeline_browser.cjs（PVD时间、四视口、相机联动）；viz_host_browser.cjs（宿主三模式和真实项目文件页面）。

## 对象工作台新增文件

- `backend/modules/visPhysField/commands.py`：物理对象与视图命令；所有提交都经过同一场景事务。
- `backend/modules/visPhysField/rendering.py`：同一场景的显示对象和导出注记，保持计算字段与着色字段独立；流线种子与切面手柄是显示附件。Surface LIC 走 OpenGL 映射器，方向用点向量、着色跟随当前物理量；Probe 应用后标签为所选物理量表。几何刷新默认不写相机位姿，只有明确改视角才带上。
- `backend/modules/visPhysField/trameUI/client/bridge.js`：Trame 只发业务事件，保存位置与输出表单由 Vis React 持有；已可见时重复可见性消息不派发 resize。
- `backend/modules/visPhysField/trameUI/client/interaction.js`：按下先分类轨道 / 切面手柄 / 点选；按下即按指针所在窗切活跃。本地三维窗轨道由浏览器持有。同步相机期间不上报，尺寸未变不发。左下角坐标轴在轨道过程中跟随本地当前相机。`phys-scene-ready` 只在 `render_cameras` 推过新位姿时同步，几何/悬停重载不盖轨道。
- `backend/modules/visPhysField/trameUI/client/workbench.css`：两行工具栏、可调侧栏、加高可滚属性、按父框高度铺满并覆盖 Vuetify 100vh、窄容器折叠菜单的样式。分析创建行约 60px，图标约缩小四分之一。
- `frontend/src/styles.css`：`#root` / Ant Design App 包装层跟 iframe 视口走，避免嵌入后只剩工具条。
- `backend/modules/visPhysField/trameUI/controller.py`：工作台选中对象与未应用草稿；按下命中切面手柄才拖平面，不切开，也不走线/种子拖动。轨道回写相机与尺寸变化不走整屏 refresh。连点同一分析不嵌套未应用对象。对象树显隐只改已有 actor；切窗只重填树眼睛，不重读网格。折线图活跃时树只列线段提取，来源行仅在其下仍有线段提取时保留。几何刷新不夹带相机；Probe 点选拾取是可见子模式开关，与后台拾取一致；线段提取应用后出现折线图视口，新对象全场取样、X/Y 即时更新，CSV 导出当前图。Surface LIC 先建显示再切远程静帧，未就绪不接远程手势；失败只提示并回退。
- `backend/modules/visPhysField/trameUI/extractionPanel.py`：Probe 数值表、时间曲线与线段提取取样表；折线主图在视口。
- `backend/modules/visPhysField/trameUI/pipelinePanel.py`：结果来源与用户创建对象树，行内删除图标打开级联确认；不创建物理量占位节点。
- `backend/modules/visPhysField/trameUI/propertiesPanel.py`：当前选中对象的计算和显示草稿、应用提交及顶部即时字段；流线起点类型与切面 X/Y/Z 对齐；拖动提交期间锁定坐标输入，防止晚到回填覆盖。含 LIC、皱折、显示种子、流线线/圆管/粗细/面数、等值滑条（按所选物理量实际标量范围，不是 0–1）、线段两端/分辨率/折线图 X/Y 轴，以及 Probe「点选拾取」开/关。流线草稿本期不提供拖种子手柄；线段提取不提供拖线。
- `backend/modules/visPhysField/trameUI/timelinePanel.py`：真实时间步的播放与定位控件。
- `backend/modules/visPhysField/trameUI/toolbar.py`：对象创建工具与活动视图显示工具，两行分工明确；第八项为线段提取，显示模式含 Surface LIC。色标设置在属性「显示设置」图标，不在右上角。
- `backend/modules/visPhysField/trameUI/viewportGrid.py`：每个窗体左上角叠放标签，点标签或折线图画布切活跃窗；新增/分割菜单贴在按钮旁，可选三维渲染或折线图。工具条提供全体相机联动；单位不一致只在旁提示，不挡住开关。本地与远程视口叠放，按是否 LIC 切换；远程未就绪时视口提示「正在切换出图」且不挂交互。折线图窗体覆盖独立 SVG 视口。
- `backend/modules/visPhysField/trameUI/icons.py`：分析工具 SVG，含线段提取图标。
- `frontend/src/modules/visPhysField/components/AnimationExportDialog.jsx`：固定实际时间步的导出表单，帧率不改变物理时间。
- `frontend/src/modules/visPhysField/components/ConfigurationDialog.jsx`：外部声明式配置在应用前经过服务端完整校验。
- `frontend/src/modules/visPhysField/components/ResultImportDialog.jsx`：受控目录内的可视化网格树选择，目录必须选到成员，不接受机器路径。
- `frontend/src/modules/visPhysField/recording.js`：实际视口录制；本地媒体流和远程图像合成共用输出协议。

当前浏览器验收：`tests/integration/viz_objects_browser.cjs`（含流线种子与切面可视平面）；对象、显示、Probe、配置兼容、流线种子与切面拖动用例：`backend/tests/modules/test_phys_objects.py`。旧 UI 浏览器脚本是迁移时期入口，不作为新 UI 验收依据。

真实 CFD 浏览器入口：`tests/integration/viz_real_results_browser.cjs`，显式接收外部证据目录内的输入清单，验证原文件哈希、点单元数量、双字段视图、固定位置 Probe、重开后的字段选择、PNG/CSV 显式导出；不将数据复制进仓库。`export_csv` 嵌入事件由 React 共享导出弹窗预选 CSV。

参考图视觉布局：`backend/modules/visPhysField/trameUI/icons.py` 提供统一 SVG 图标，`frontend/src/modules/visPhysField/pages/PhysFieldWorkspacePage.css` 控制嵌入边距与导出提示。`tests/integration/viz_visual_browser.cjs` 检查真实工作台的工具带、面板比例、三分量表单与多尺寸截图。

参考图校正同时调整 `rendering.py` 的屏幕字号与同视图多色标排布；浏览器 XYZ 拾取回填在 `controller.py` 与 `viz_objects_browser.cjs` 联验。

`frontend/src/modules/visPhysField/components/ResultImportDialog.jsx`：受控目录内的可视化网格树选择，目录必须选到成员。平台真实默认入口、来源追加与关闭回收由根 `packages/ai4e-web/e2e/trame-entry.spec.ts` 覆盖，不能用单独挂载组件替代实际页面验收。

后处理Tab保持：`worker.py`在IPC前stash草稿；`trameUI/controller.py`接受visibility暂停/重绘，轨道回写相机不走整屏 refresh；`client/bridge.js`接收直接同源宿主尺寸通知且已可见时不重复 resize；React `PhysFieldWorkspacePage.jsx`与`usePhysField.js`校验并转交。宿主验收见根 `e2e/post-session.spec.ts`、`post-real.spec.ts` 与 `.context/mvp/post-workspace-acceptance.md`。

响应与独立显隐：`test_phys_display_updates.py` 使用真实 Trame State 覆盖错误回滚、推送失败、Probe/多视图独立显示、画像与着色缓存失效；`test_phys_objects.py` 首次草稿同步手柄，连点不重复。根 `packages/ai4e-web/e2e/trame-responsiveness.spec.ts` 从真实原始处理/后处理页面点击双层 iframe，并核对场景、截图、持续响应及保存重开。

- `backend/modules/visPhysField/trameUI/camera_controls.py`：工作台委托的相机与视图控制，仍共享原 Workbench 和会话；联动不经坐标空间门禁。

- `backend/modules/visPhysField/trameUI/object_controls.py`：工作台委托的对象菜单与依赖删除，仍共享原 Workbench 和会话。

- `backend/modules/visPhysField/trameUI/session_controls.py`：工作台委托的宿主可见性及会话操作，仍共享原 Workbench 和会话。

- `backend/modules/visPhysField/trameUI/export_controls.py`：工作台委托的导出和草稿处理交接，仍共享原 Workbench 和会话。


三维交互与对象隔离（2026-09-16）：新对象计算和显示草稿一起提交；辅助平面独立显隐，三轴平移与三轴旋转仅命中手柄启动；删除局部清理不重建背景和相机。种子和Probe有候选预览，等高线支持自动分层，同标量等值面保留生成标量。圈定 `test_phys_interaction.py`、`test_phys_objects.py`、`test_phys_display_updates.py`、`test_phys_filters.py`、配置/存储用例与 `viz_interaction_browser.cjs`；最终范围见根 `.context/mvp/phys-workbench-acceptance.md`，正式8000/5173不自动更新。

- `backend/tests/modules/test_phys_interaction.py`：六手柄、候选预览、配置及向量模长等值回归。
- 根 `tests/integration/viz_interaction_browser.cjs`：真实网格本地/远程鼠标拖动、独立着色、辅助显隐、三尺寸截图、种子/Probe预览与删除验收。

- `frontend/src/test/interaction.test.js`：两个 Trame tracker 的拖动归属回归，非发起视口不得截获移动或释放。

2026-09-16 显示设置：对应模块 PRD 已更新色标/范围/背景、矢量采样或透明输出职责。专项测试 `backend/tests/modules/test_phys_display_settings.py`；前端透明表单 `frontend/src/test/transparentExport.test.jsx`，真实入口 `tests/integration/viz_interaction_browser.cjs`（Dojo 根）。

2026-09-17 自定义范围预填与色标默认：切到自定义先填上次应用的记忆值，没有记忆则填当前自动最小、最大；色标标题/厚度/刻度缺省 25。圈定 `backend/tests/modules/test_phys_display_settings.py`。

2026-09-17 十二项优化：属性行/透明度对齐，色标弹窗即时提交，纯色选色；矢量两档大小；等高线只留自动分层和线宽；切面确认后锁定且保留多边形交面；本地坐标轴跟随主相机，关闭预览清附件。圈定 `test_phys_display_settings.py`、`test_phys_filters.py`、`test_phys_interaction.py`、`test_phys_views.py` 与前端 `interaction.test.js`。

2026-09-17 十一项增强：LIC/皱折/种子显隐/导入网格树/等值滑条/色标相等/Probe 表/线段提取。圈定 `backend/tests/modules/test_phys_display_settings.py`、`test_phys_filters.py`、`test_phys_interaction.py`、`test_phys_views.py`、`test_phys_objects.py`、`test_phys_plot_over_line.py`，前端 `frontend/src/test/interaction.test.js`，根 `tests/integration/test_viz_host_bindings.py`。证据见根 `.context/mvp/phys-workbench-acceptance.md`。

2026-09-17 等值滑条物理量范围：滑条 min/max/当前值取当前计算物理量在输入网格上的实际标量，不是归一化 0–1；换场后重算，手填仍可越界。圈定 `test_phys_interaction.py`。

2026-09-17 色标/Probe/视图联动：色标入口在属性「显示设置」图标，弹层带对象名和「应用」，只写当前选中对象；Probe 只留一个开关；加号菜单贴按钮；点窗切活跃并刷新树眼睛；折线图树只列线段提取；去掉取样物理量。圈定 `test_phys_display_settings.py`、`test_phys_interaction.py`、`test_phys_display_updates.py`、`test_phys_plot_over_line.py`、`test_phys_views.py` 与前端 `interaction.test.js`。证据见根 `.context/mvp/phys-workbench-acceptance.md`。
