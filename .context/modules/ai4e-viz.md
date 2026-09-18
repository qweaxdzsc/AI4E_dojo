# ai4e-viz 模块索引
## 当前职责与本轮变更

算法库与迁入可视化应用并存；包内 .context、PRD 和 architecture 为内部真源。

- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


## 模块边界

- 状态：独立静态比较与本机交互预览共存；整合工作区验收范围见本文末尾。
- 职责：读取稳定 run/report artifact，生成静态或交互视图。
- 允许依赖：`ai4e-spec` 和独立渲染库。
- 禁止依赖：`ai4e-core`、模型、Trainer、Dataset 实现。
- 计算边界：误差与守恒量等研究计算归 core；viz 可执行显示切片/裁切等通用 VTK 过滤，不计算研究差值。
- 原库按能力聚合；迁入应用的 backend 采用轻量 DDD、frontend 采用 JSX 微领域。

## 目录索引

- `packages/ai4e-viz/`：包工程根兼 viz 源码根；由构建配置映射为 `ai4e_viz` 导入名。
- `packages/ai4e-viz/render/`：稳定 artifact 到单一图形/视图的渲染。
- `packages/ai4e-viz/compose/`：多个已渲染视图的布局与组合。

## 文档索引

- `packages/ai4e-viz/README.md`：包职责与依赖边界。
- `.context/modules/ai4e-viz.md`：本模块的目录与文档检索入口。
- `.context/mvp/abupt-mvp1.md`：MVP1 报告和可视产物所处阶段。
- `.cursor/rules/ai4e-algorithm-architecture.mdc`：本包的能力分层、高内聚低耦合与代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解 artifact 与可视化解耦原因时按需读取。

新增目录或文档时必须同步本索引。

## 物理数据跨模型实验

render/comparison.py：共色标表面、切面和曲线；compose/comparison.py：离线 HTML；pyproject.toml：仅 spec 和渲染依赖。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `docs/PRD/ai4e-viz/render/PRD.md`、`compose/PRD.md`：渲染和报告功能正文。

报告预算说明由源运行记录提供，HTML 不假定单轮；服务器报告操作见 `docs/aero-cfd-server-runbook.md`，回归见 `tests/integration/test_comparison_visualization.py`。

## 本机平台接入（2026-09-10）

- `packages/ai4e-viz/inspect/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/dispatch.py`：按扩展名分派 VTK/HDF5/PT/NPY/Zarr/文本检查。
- `packages/ai4e-viz/inspect/hdf5.py`：HDF5 字段目录与单数据集读取；VTKHDF 交给网格检查。
- `packages/ai4e-viz/inspect/mesh.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/tensor.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/text.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/model_graph.py`：平台两档官方结构图；只接收可前向网络和输入，一次写出阶段主干与阶段压缩块，失败不留半份页。
- `packages/ai4e-viz/inspect/stage_display.py`：网络公开编码器/几何块/物理块/解码/读出时，按这些子模块收成阶段盒再交给两档参数；不实现模型前向。
- `packages/ai4e-viz/preview/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/mesh.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/tensor.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/text.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/runtime/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/runtime/worker.py`：真实文件检查、预览及独立执行。
- `.context/mvp/web-rawprep-acceptance.md`：平台接入验收记录。

- `docs/PRD/ai4e-viz/inspect/PRD.md`：真实字段检查与两档结构图展示。

- `docs/PRD/ai4e-viz/preview/PRD.md`：分页与基础三维预览业务。

- `docs/PRD/ai4e-viz/runtime/PRD.md`：独立进程请求和失败边界。

## 整合工作区实现切片

- `pipeline/execute.py`：表面、平面切片/裁切、阈值、等值的有序 VTK 显示管线；保留源实体身份，生成点明确标记。
- `serialization/geometry.py`：独立几何、拓扑、字段与映射二进制输出；128 MiB 门禁和 manifest 最后提交。
- `preview/fields.py`：完整字段有效值统计和直方图。
- `preview/tensor.py`：指定行列轴及剩余轴索引的分页，不隐式压平高维数组。
- `runtime/worker.py`：旧单 JSON 与新 NDJSON 协议兼容。
- `tests/integration/test_viz_pipeline.py`：真实体切片和二进制交接；其他完整工作区验收由总体验收记录跟踪。
- `docs/PRD/ai4e-viz/pipeline/PRD.md`、`serialization/PRD.md`：过滤和显示交付。
- `tests/integration/test_viz_extended.py`：解析场等值与裁切、向量范围/无效值、真实 Zarr、块选择和拒绝路径。
- Web `modules/visualization`：统一查看器；`infrastructure/rendering/vtk/Viewport.tsx`：资源生命周期与纯显示属性。完整前端索引由主 Agent 统一维护。
- 已通过 20 项圈定 Python 用例，以及真实 ShapeNet/NASA 文件的服务登记→转换→二进制→浏览器、多窗口、阈值、服务场景持久化和恢复自动化。上述不代表所有原型视觉状态已验收。

- `pipeline/tensor_points.py`：受信任显式几何声明到点云，保留独立整数身份；不猜拓扑。
- `.context/mvp/web-visualization-acceptance.md`：可视化切片已测范围与未交付项。
- `.context/mvp/web-visualization-results/`：两真实数据源自动化报告与实际渲染图片。

- 浏览器 `visualization-safety.spec.ts`：窗口预算隔离和单元字段大整数身份拾取；`visualization-views.spec.ts` 包含真实 WebGL context-loss 恢复。

- 浏览器 `visualization-difference.spec.ts`：正式 NASA 双模型差值受控引用到真实点云显示及截图，固定内容修订。

- 浏览器 `visualization-export.spec.ts`：正式 HTTP post 导出 NASA 网格固定资产，原拓扑、预测/真值和原身份交接；具体执行结果见切片验收记录。
- 浏览器 `visualization-subscriptions.spec.ts`：传输协议夹具验证取消仅释放本调用的订阅，并覆盖旧无订阅字段服务；后端共享进程真实隔离由平台验收。

- 浏览器 `visualization-camera.spec.ts`：完整固定源身份、显式同坐标声明、恢复联动重校验；真实服务解析VTK夹具和实际NASA未知单位拒绝分别验收。

## 独立 Vis 应用迁移

- `packages/ai4e-viz/backend/modules/`：完整十三模块；逐文件职责在包内 `.context/modules/`。
- `packages/ai4e-viz/backend/server/`：独立装配与上下文注册；`backend/infrastructure/`：进程、文件事务和通信。
- `packages/ai4e-viz/frontend/`：保留 JSX 应用，`visPhysField` 嵌入独立 Trame 会话。
- `packages/ai4e-viz/{AGENTS.md,.context,.cursor,docs,resources,fixtures}`：原治理、架构、产品、测试资源。
- `packages/ai4e-viz/cli.py`：安装后的独立应用入口；`pyproject.toml`：单层 wheel 与 workbench 可选依赖。
- `packages/ai4e-viz/docs/migration/source-manifest.json`：385 个跟踪文件与 8 个额外规则/技能文件的来源清单。
- `packages/ai4e-viz/docs/migration/dojo-integration.md`：迁移说明、可运行命令和验收边界。
- `packages/ai4e-viz/.context/modules/visIO.md`、`visTaskManage.md`、`visPhysField.md`：资产、修订与物理工作区文件入口。

- `.context/mvp/vis-migration-acceptance.md`：393份来源迁入、配置链路、三维实际验收与环境边界。
- `packages/ai4e-viz/docs/migration/file-inventory.md`：迁入后完整有效文件目录。

迁移时期浏览器入口（旧 UI）：tests/integration/viz_workbench_browser.cjs（本地/远程、真实像素视频、拾取、Probe、切面）；viz_timeline_browser.cjs（PVD时间、四视口、相机联动）；viz_host_browser.cjs（宿主三模式和真实项目文件页面）。

三维对象工作台的当前 UI/配置与文件目录由包内 `.context/modules/visPhysField.md` 维护。新增浏览器入口 `tests/integration/viz_objects_browser.cjs`；验收记录 `.context/mvp/phys-workbench-acceptance.md`。

真实 CFD 文件验收：`tests/integration/viz_real_results_browser.cjs`，ShapeNet/NASA 既有后处理结果只读引用与双字段视图、Probe、保存重开及输出。结果继续归 `mvp/phys-workbench-acceptance.md`。

参考图样式校正入口：`tests/integration/viz_visual_browser.cjs`；四种宽度实际截图与功能回归见 `.context/mvp/phys-workbench-acceptance.md`，视觉验收与计算验收分别记录。

## 后处理三页签与固定结果评价

2026-09-18 三维结果核验追加：prediction/truth 按资产 revision、字段名和 Vis scalar 逐层核验；后处理宿主三维物理场最小高度调整为约 714px，正式入口换 Vis 后再做浏览器验收。

- `backend/modules/visPhysField/worker.py`：IPC操作前保留草稿；visibility仅暂停/重绘。
- `trameUI/controller.py`、`client/bridge.js`：隐藏暂停及返回尺寸通知。
- `frontend/src/modules/visPhysField/hooks/usePhysField.js`、`pages/PhysFieldWorkspacePage.jsx`：直接同源宿主消息校验，常驻心跳。
- 宿主后处理通过既有来源绑定链追加，独立Vis不依赖task或core。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

物理场嵌入样式 `frontend/src/modules/visPhysField/pages/PhysFieldWorkspacePage.css` 绑定iframe视口高度，避免自动高度包装层造成150px裁切；后处理真实浏览器同时断言内外iframe尺寸。

## 响应诊断与独立显隐计划（2026-09-15）

- `.cursor/plans/trame-response-and-independent-visibility.plan.md`：已实施并完成真实 Web 回归的计划；真实 Trame 状态读取异常、草稿手柄漏同步、父子显隐独立及圈定测试。
- `trameUI/controller.py` 已修复 `_sync_tree_visible` 错用 State.get 的异常；显隐包含回滚和推送，首次切面同步手柄；`test_phys_objects.py` 的相关用例改用真实 State。
- 证据与测试边界见根 `.context/mvp/phys-workbench-acceptance.md`，不覆盖历史验收。

响应实现与真实状态测试：包内 `backend/tests/modules/test_phys_display_updates.py`；真实宿主双层 iframe 点击回归 `packages/ai4e-web/e2e/trame-responsiveness.spec.ts`。结果见 `.context/mvp/phys-workbench-acceptance.md` 的本轮记录，历史诊断不等于修复验收。


三维交互与对象隔离（2026-09-16）：新对象计算和显示草稿一起提交；辅助平面独立显隐，三轴平移与三轴旋转仅命中手柄启动；删除局部清理不重建背景和相机。种子和Probe有候选预览，等高线支持自动分层，同标量等值面保留生成标量。圈定 `test_phys_interaction.py`、`test_phys_objects.py`、`test_phys_display_updates.py`、`test_phys_filters.py`、配置/存储用例与 `viz_interaction_browser.cjs`；最终范围见根 `.context/mvp/phys-workbench-acceptance.md`，正式8000/5173不自动更新。

三维着色与显示设置专项：新增 `backend/tests/modules/test_phys_display_settings.py`（Vis包内），前端 `transparentExport.test.jsx`；实现和证据见根 `.context/mvp/phys-workbench-acceptance.md`，正式入口未自动发布。

三维工作台十一项增强（2026-09-17）：验收入口 `.context/mvp/phys-workbench-acceptance.md`。新增索引文件 `seedWidget.py`、`lineWidget.py`、`test_phys_plot_over_line.py`；导入对话框改为目录网格选择。功能正文只在包内 PRD。2026-09-17 后续：流线草稿不再拖种子；显示可选线/圆管；本地坐标轴实时跟转。

线段提取 Line Chart View（2026-09-17）：`lineChart.py`、视口类型 `render`/`line_chart`、属性 X/Y 与 CSV。不拖线。验收入口 `.context/mvp/phys-workbench-acceptance.md`。

三维默认光照对齐 ParaView（2026-09-17）：`visEngine/renderPasses.py` 使用 VTK Light Kit 五灯默认值；`visPhysField/scene.py` 持久渲染器装配该套件，阴影仍默认关。圈定 `test_vis_engine.py`、`test_phys_display_settings.py`。正式 8000/5173 须用户重启 Vis 后才能冒烟。

辅助平面轨道相机（2026-09-17）：添加平面后旋转/平移/缩放不得被旧位姿拉回。按下先分类，几何刷新不夹带相机。圈定 `test_phys_interaction.py`、`interaction.test.js`。

工作台小修复收口（2026-09-17）：删线/种子拖动残留；四条交接（按下分类、刷新不带相机、窗口类型、当前物理量）写入包内 PRD。验收入口 `.context/mvp/phys-workbench-acceptance.md`。正式 8000/5173 须换 Vis 后点验。

正式发布/Web 冒烟硬规则：根 AGENTS 同名段。Agent 必须自己在正式宿主 5173→8000 验收双层嵌入；未重装 `ai4e-viz`、未换 Vis 子进程、只跑 7999/5172 或标「待发布」都是未验收。
