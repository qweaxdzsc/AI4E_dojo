# AI4E_Vis 模块化重构执行计划

## 目标与完成定义

前后端以十三级一级业务模块为限界上下文。第十三级`dataAssets`是数据恢复后确认的独立资产域；完成不是“建立空目录”，而是同时满足：

1. 真实实现、Router、Application、Domain、Repository、SQL、Page、API和业务Component进入所属模块。
2. Server与App只通过模块公开门面注册，不直接引用模块内部实现。
3. 每迁完一个模块，立即运行该模块的导入、Repository、API契约或前端构建测试。
4. 全部模块接管后运行完整后端、前端和E2E回归。
5. 只有新入口和全量回归都通过，才删除旧文件；删除后再次运行全量回归。
6. SQLite表、现有记录、公开URL、HashRouter路径和渲染行为保持兼容。

## Git与删除策略

- 在删除任何旧文件前建立本地Git仓库和基线提交。
- `var/`、旧运行库、上传文件、虚拟环境、`node_modules`和构建产物不进入Git。
- 每组模块迁移完成并通过测试后形成阶段提交。
- 删除前用 `rg` 证明旧文件已无生产引用；测试和脚本也必须切换到新入口。
- 删除采用精确文件清单，不递归删除仓库根或业务数据目录。

## 后端迁移批次与模块测试

### 批次一：持久化模块

1. `dataAssets`
   - 拥有`artifacts`、`artifact_classification_history`、上传、SHA-256去重、列表/详情、分类版本和原始文件定位。
   - 测试：临时SQLite、上传去重、详情、分类历史、文件落盘和API契约。
2. `visDatasets`
   - 拥有格式解析、画像、检测、统计和内容查看；分析结果只通过`dataAssets`公开门面写回。
   - 测试：格式注册、画像、体检、显式分析和跨模块接入。
3. `visIO`
   - 将 `artifact_visualizations` 的SQL、表现清单、保存和查询迁入模块Repository。
   - 测试：创建、查询、冲突、表现更新、VisualizationSpec引用和API契约。
4. `visTaskManage`
   - 完成VisualizationSpec Repository接管；推荐、参数Schema、默认值和乐观锁进入模块。
   - 测试：23方法、动态参数、创建版本、过期基线冲突和工作台路由。
5. `reportManage`
   - 迁移报告实体、冻结版本、复制和导出任务SQL。
   - 测试：CRUD、冻结、复制、导出状态、版本读取和报告API。
6. `reportDesigner`
   - 迁移草稿、文档校验、布局与历史操作相关持久化。
   - 测试：草稿修订冲突、文档校验、冻结前编排和编辑路由。

### 批次二：可视化与转换模块

7. `visGeometry`：几何解析、O3DV表现、结构树与视角适配；测试PLY/OBJ/GLB/VTU表现和降级。
8. `visFigure`：PNG/JPG解析与预览；测试格式、尺寸、静态表现和错误输入。
9. `visConvertor`：迁移 `geo_conversion.py`；测试现有VTK兼容几何到GLB及失败诊断。
10. `visPhysField`：迁移Trame场景与Miller时序到三个二级业务模块，共享一级Trame会话。
   - 测试九类场景注册、Miller时序、拓扑复用、二级模块禁止项和旧深链接。
11. `visEngine`：仅接收从物理场中提取的纯VTK/数值内核、缓存和性能代码。
    - 测试纯函数、缓存淘汰、抽样边界以及禁止FastAPI/Trame Server/SQLite依赖。

### 批次三：集成模块

12. `automation`：脚本模型、保存和公开用例；未实现能力保持明确状态，不伪造完成。
13. `MCP`：只封装其他一级模块公开接口；测试工具Schema与禁止访问内部Repository。

## 前端迁移与模块测试

- 页面源码进入所属模块 `pages/`，旧全局页面只在迁移期作为兼容入口。
- 业务请求进入模块 `api.js`；共享HTTP、无业务Component和运行时进入Infrastructure。
- 跨模块只从目标模块 `index.js` 导入。
- `visPhysField/modules` 二级业务共享一级API、Provider、Store语义和Trame连接。
- 每个前端模块迁移后运行架构检查和生产构建；补齐可独立执行的模块契约测试。
- 修复当前Node/jsdom/undici测试运行时兼容后，Vitest必须真实执行全部用例。

## 旧文件删除候选

以下文件只有在实现迁入、生产引用归零和对应模块测试通过后才能删除：

- 后端：`api_app.py`、`artifact_store.py`、`spec_store.py`、`report_store.py`、`geo_conversion.py`、
  `catalog_data.py`、`example_data.py`、`parameter_registry.py`、`report_data.py`、`quarto_service.py`、
  `trame_app.py`、`miller_animation.py`、`miller_report.py`、`gs_report.py`。
- 前端：`src/config/backend.js`、`src/pages/` 下兼容门面、`src/App 2.jsx`，以及迁移后不再引用的
  全局业务Component、Hook、Data和Lib文件。

`backend/state`、`backend/uploads` 属于旧运行数据，不按源码删除。完成新运行路径校核和备份后，
单独制定数据归档清单，避免把用户数据当作散乱源码删除。

## 最终验收

- 十三级后端模块全部由Server模块注册；前端只保留有UI或公开前端能力的模块。
- 旧生产源码引用为零，旧兼容文件删除。
- 后端模块测试、完整契约测试、前端架构测试、Vitest、生产构建和关键Playwright E2E通过。
- 5个数据家族、19种语义类型、23种方法、O3DV、Trame九类场景、VisualizationSpec、报告编排与导出可用。
- 数据库完整性为 `ok`，记录数和索引与迁移前基线一致；新写入只保存 `storage_key`。

## 执行记录

> 本节记录已经由代码和测试证实的状态；未完成项不能仅因目录存在而标记完成。

- `dataAssets`已从`visDatasets`拆出资产表、上传和资产页面；`visDatasets`保留解析与体检。跨模块组合58项、后端最终全量89项、前端13项契约与生产构建通过，SQLite表与公开URL未改名。
- 已建立重构前 Git 恢复点和逐批模块迁移提交；旧源码删除均可从 Git 恢复。
- `visDatasets`、`visIO`、`visTaskManage`、`visConvertor`、`visPhysField` 已迁移并通过各自模块测试。
- `reportManage` 与 `reportDesigner` 已分离：文档骨架、校验、草稿读取及乐观锁更新归
  `reportDesigner`，报告实体、不可变版本和导出任务归 `reportManage`；报告与 Quarto 组合测试
  结果为 `10 passed, 1 skipped`。
- 前端业务页面已进入一级模块，旧 `src/pages` 页面、`pages/v2` 兼容门面和 `App 2.jsx` 已在
  引用归零后删除。
- 前端测试环境固定为兼容 Node 20 的 `jsdom 26.1.0`；删除旧页面后架构检查通过、Vitest
  `11 passed`、生产构建通过。
- 前端全局业务文件已进一步收口：共享组件与 Hook 进入 `infrastructure`，几何查看器进入
  `visGeometry`，案例预览/术语/目录回退进入 `visTaskManage`，报告文档纯逻辑进入
  `reportDesigner`；无引用的旧全局 API、Mock 与演示组件已删除。
- `visGeometry`、`visFigure`、`visEngine`、`automation` 和 `MCP` 已增加独立模块测试，当前
  8 个用例全部通过；未实现的脚本持久化仍明确返回未就绪，不伪造功能。
- `visTaskManage` 的方法 Schema 与 VisualizationSpec Router、`reportDesigner` 的草稿 Router
  已从旧入口迁入一级模块，迁移后模块、契约和架构组合测试为 `50 passed`。
- 数据集解析/画像管线与各业务 Router 已迁入所属一级模块；旧 FastAPI 上帝入口已删除，
  `backend/server/api.py` 只负责注册模块 Router 和技术健康检查。新入口组合测试为
  `53 passed`，覆盖 `visIO`、`visTaskManage`、`visDatasets`、API 契约与架构门禁。
- `resources/examples` 与 `fixtures/gs` 已接管内置案例；旧 `backend/data`、
  `backend/fixtures` 和 O3DV 源码树缓存已删除。受影响模块组合回归为 `62 passed`。
- 旧上传文件已按 SHA-256 迁入 `var/objects/datasets`，11 个文件逐条哈希一致；SQLite
  已迁入 `var/db/ai4e_vis.sqlite3`，三类资产路径全部为相对 storage key。旧库在删除前
  备份到 `var/backups`，新旧关键记录数一致且 `integrity_check=ok`。
- 删除旧入口、旧运行目录、旧全局前端目录与生成缓存后，2026-08-29 数据恢复修订后的后端全量回归为
  `85 passed, 1 skipped`；前端架构检查通过、Vitest `11 passed`、生产构建通过；
  Playwright 桌面/移动三服务 E2E 为 `19 passed, 1 skipped`。移动端大体积 G-S HTML
  下载用例按测试设计跳过，桌面端同链路已通过。
- 便携清单已按新目录重建，共 352 个源文件与业务数据条目，机器依赖检查为零。
- 运行时排查发现重构前 `api_app.py` 仍可占用 8091 并连接废弃 `backend/state`；现已在线
  备份旧库、通过 `reportManage` Repository 合并两条新增报告、切换到 `server.api`。启动器
  现在拒绝缺少 `server.api/var-v1` 健康标识的旧进程，防止资产和报告引用再次“假消失”。
