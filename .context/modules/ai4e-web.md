# ai4e-web 模块索引

正式前端已接入整合平台真实流程。唯一 UI 基准 `docs/prototypes/dojo-web-integrated.html`；该 HTML 的示例状态不代表实际计算。旧首期验收与新四组合验收分别保留，范围以总验收记录为准。

## 工程与公共基础设施

- `packages/ai4e-web/package.json`、`package-lock.json`：唯一 npm 清单与锁；React、TypeScript、Vite、Ant Design、vtk.js。
- `index.html`、`src/main.tsx`：页面加载与挂载。
- `tsconfig.json`、`vite.config.ts`：类型、构建与可配置本机 API 代理。
- `playwright.config.ts`：自动化浏览器入口。
- `scripts/check-boundaries.mjs`：微领域公开门面导入检查。
- `scripts/generate-contracts.py`：从服务 OpenAPI 生成 `src/infrastructure/contracts/api.generated.ts`。
- `scripts/generate-platform-contracts.py`：从 spec 生成 `src/infrastructure/contracts/platform.generated.ts`。
- `src/infrastructure/http/client.ts`：统一请求和错误。
- `src/infrastructure/components/`：异常边界、未开放提示、无业务语义配置输入组件；ActionButton 提供稳定可访问名称和真实忙碌禁用状态。
- `src/infrastructure/theme/global.css`：平台布局；`visualization.css`：查看器内部布局。
- `src/infrastructure/assets/binary.ts`：带修订二进制读取、引用计数与 CPU 缓存。
- `src/infrastructure/rendering/vtk/Viewport.tsx`：vtk.js 相机、表示、点选及 GPU 生命周期；`MeshViewer.tsx` 保留旧预览兼容。

## 应用壳与微领域

`src/app/App.tsx` 装配路由；`layouts/PlatformLayout.tsx` 提供整合外壳；`pages/ProjectDetailPage.tsx` 组合六页签，`TaskWorkbenchPage.tsx` 组合任务与八步导航。下列领域通过各自 `index.ts` 导出：

`pages/WorkbenchLandingPage.tsx` 是真实工作台选择入口，读取项目/任务和有效最近任务，`?choose=1` 强制切换；已归档或不存在的最近对象不自动恢复。全局侧栏由路由决定高亮与面包屑，整行链接和装饰图标的可访问名称分开。`pages/TaskWorkbenchPage.tsx` 与 `task-workbench.css` 用整合 HTML 最终主题的标题、`topsteps` 八步和 Recipe 条（真实案例名与输入输出交接），不再使用 Ant Design Steps。

- `src/modules/projects/`：ProjectNavigation 项目创建、列表与管理，api 代理真实服务。
- `public/project-covers/`：从整合原型提取的四张原字节装饰封面及来源 README；不作为科研结果。
- `src/modules/tasks/`：TaskManagement 简洁创建时必选四组案例并按接口字段展示数据集与模型，成功进入原始处理；编辑仅元信息，派生继承配置与绑定。案例加载失败可在弹窗内重试。`stages.ts` 提供任务表与工作台共用的八步名称。api 读取登记案例，`task-management.css` 管任务表、更多菜单和创建弹窗密度，不写进全局样式。行内进入工作台与血缘使用同一按钮样式。
- `src/modules/files/`：FileBrowser 文件树、选择、查询和刷新；ProjectFiles 对照整合 HTML 的任务版本 / 搜索 / 类型 / 排序工具条和表列，浏览内容仍是真实目录，api 管访问。
- `src/modules/rawprep/`：RawprepWorkbench 三栏；第 04 段对照细节原型勾选 PT/VTKHDF/Zarr，第 05 段为分片统计策略；执行门禁只看绑定有效与已选文件，未保存修订在提交前写入，不因 dirty 禁用主按钮；FieldExtractionEditor 自由字段容器；ExtractionDialog 旧兼容编辑组件；api 管配置与完整样本操作。
- `src/modules/rawprep/DatasetBindingPanel.tsx`：带修订读取/保存目录或 NASA 三文件绑定，内置受控来源选择弹窗。`BoundDatasetFiles.tsx` 用原始数据处理/处理结果页签限制输入选择并浏览运行产物，表头对照细节原型第一行页签、第二行左刷新右绑定；`dataset-binding.css` 与 `rawprep-workbench.css` 对照细节原型三栏。NASA 文件选择使用根与路径组合的稳定键，FieldExtractionEditor 分别解析根和相对路径。
- `src/modules/stages/`：StageWorkbench 只协调阶段配置修订、固定输入和操作；api 为共享阶段传输。
- `src/modules/trainprep/PreparationPanel.tsx` 与 `trainprep.css`：对照细节原型三栏（9px 间距、等高 640），左栏真实文件表，字段与归一化可编辑，统计与采样不手填。
- `src/modules/models/ModelPanel.tsx`：模型参数、采样、输入和真实结构宿主；无物理清单或准备记录时不能生成结构。
- `src/modules/training/TrainingPanel.tsx`：按案例参数组织优化与训练控制。
- `src/modules/executions/`：ExecutionLog 日志恢复；TrainingMonitor 对照运行细节页的摘要、左右栏和真实指标，api 管运行事实。
- `src/modules/post/`：PostWorkspace 对照整合 HTML 后处理步（横向配置、指标/图表/三维页签、默认三栏可视化），PostMetricCharts 只绘制真实指标，`post.css` 管本页皮肤，api 管固定场景。不复刻示意徽章或假结果。
- `src/modules/lineage/`：对照整合 HTML 的左图右检版本树；`layout.ts` 按真实父版本排布节点，不使用原型固定示意树。`LineageView` 区分创建快照、当前目录与固定运行，Fork 走任务公开派生门面。
- `src/modules/comparisons/`：配置及固定来源比较；DifferencePanel 协调严格差值与查看器。`comparison.css` 只画表格/趋势/三维导轨外壳。
- `src/modules/reports/`：新整合入口未开放；`ProjectReport` 只读历史正文，`report-shell.css` 同时给批量两栏外壳。
- `src/app/pages/BatchShell.tsx`：批量页未开放外壳，不生成计划。
- `src/modules/previews/`：FilePreviewDialog 宿主；FilePreviewContent、FieldTree、FieldSummary 由可视化领域提供真实内容，api 保留兼容。
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
- `e2e/model-inspection.spec.ts`：真实 TorchVista 图形加载。
- `e2e/task-dataset-binding.spec.ts`：从项目页点击完成四案例简洁创建与受控绑定、弹窗校验/重试/约定尺寸，以及 1440/1920 任务表对照整合 HTML。证据见 `.context/mvp/web-integrated-results/task-binding-correction/`。
- `e2e/visualization-difference.spec.ts`、`visualization-export.spec.ts`：真实 NASA 差值及完整导出网格。
- `e2e/visualization-safety.spec.ts`、`visualization-subscriptions.spec.ts`：资源/上下文恢复及明确标注的订阅协议夹具。
- `e2e/visualization-camera.spec.ts`：完整固定引用、显式坐标空间及恢复场景重新校验；实际 NASA 缺声明时拒绝跨源联动。
- `e2e/research-records.spec.ts`：版本固定阶段参数加入比较、保存恢复及真实迟到请求隔离。
- `e2e/home-entry.spec.ts`：从首页逐项点击、空项目新建任务、最近任务恢复与归档失效，以及 1440/1920 首页原型几何和封面摘要对照；测试生成记录按确切身份归档。
