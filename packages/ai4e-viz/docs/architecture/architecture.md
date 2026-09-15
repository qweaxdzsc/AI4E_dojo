# AI4E_Vis 模块化架构计划

> 本文由原始 `PLAN.md` 校对后纳入仓库，是总体架构和迁移验收的权威设计文档。原稿中的十二模块已按当前代码事实修正为十三级，并把资产登记、上传、去重和资产页面从 `visDatasets` 调整到独立 `dataAssets`。具体产品行为以 `docs/PRD/` 为准，当前文件位置以 `.context/` 为准，已经执行的迁移证据以 `MODULAR_REFACTOR_PLAN.md` 为准。

## 1. 目标与核心原则

前后端以十三级一级业务模块作为限界上下文：

```text
backend/modules/<moduleName>/
frontend/src/modules/<moduleName>/
```

- 一级模块高内聚、低耦合，可连同前端、后端和持久化边界整体拆分。
- 目录第一层按业务模块切分，模块内部再按实际复杂度做技术分层；小模块不建立空壳文件。
- 一级模块拥有自己的 Router、Application、Domain、Repository/SQL，以及有 UI 时的 API、Model、Hook、Component 和 Page。
- 大型一级模块可建立 `modules/<secondLevelModule>`，但二级模块不是独立服务，不复制一级技术基座。
- `server`/`app` 只负责装配，`infrastructure` 只提供无业务含义的技术基座。
- SQLite、FastAPI、Trame + VTK、自托管 O3DV、JS/JSX 和现有公开接口保持兼容。
- 前后端源码必须具备充分的原因型中文注释。

功能范围以 `可视化功能模块.xlsx` 的“功能模块”Sheet及对应 PRD 为准。设计文档不得把目录占位、潜在内核能力或演示数据伪装成已完成功能。

## 2. 十三级一级模块

| 模块 | 业务边界 | 前端形态 |
| --- | --- | --- |
| `dataAssets` | 资产登记、上传、SHA-256去重、列表/详情、分类历史、原始文件与资产表 | 资产列表和详情页 |
| `visTaskManage` | 目录、推荐、参数 Schema、示例、VisualizationSpec版本与乐观锁 | 推荐、示例、配置器和Spec页面 |
| `visGeometry` | 几何表现、视角、结构/选择能力与O3DV适配 | 几何业务组件，按需被页面组合 |
| `visDatasets` | 格式解析、画像、质量体检、统计和内容查看 | 数据分析公开能力，无资产页面所有权 |
| `visPhysField` | 三维物理场显示、数据提取、数据概览和统一Trame会话 | 独立工作区与二级业务组件 |
| `visFigure` | PNG/JPG等同源静态预览 | 当前由任务预览组合，无独立模块 |
| `visIO` | 可视化资产保存、冻结、查询、报告引用和导出边界 | 保存/查询公开能力 |
| `visConvertor` | 几何和数据格式转换及失败诊断 | 当前无前端模块 |
| `automation` | 脚本模型、校验、保存和执行边界 | 当前无前端模块 |
| `MCP` | 将一级模块公开用例封装为MCP工具 | 无前端模块 |
| `reportManage` | 报告中心、版本、复制、冻结、母版和导出 | 报告中心与阅读页 |
| `reportDesigner` | ReportDocument、草稿、布局、拖拽、历史操作和乐观锁 | 报告编辑页 |
| `visEngine` | 无业务语义的VTK/数值内核、缓存和性能原语 | 不建立前端模块 |

## 3. 仓库结构

```text
AI4E_Vis/
├── AGENTS.md
├── .context/
├── .cursor/rules/
├── backend/
│   ├── server/
│   ├── modules/
│   ├── infrastructure/
│   └── tests/
├── frontend/
│   ├── src/app/
│   ├── src/infrastructure/
│   ├── src/modules/
│   └── tests/
├── docs/
│   ├── PRD/
│   ├── architecture/
│   ├── api/
│   ├── migration/
│   └── testing/
├── resources/
├── fixtures/
├── var/
└── run_project.py
```

根`AGENTS.md`是仓库唯一开发入口，只维护阅读入口、技术约束和修改纪律；代码子目录不建立局部`AGENTS.md`。`.context/index.md`维护总体架构和文件导航；`.context/modules/*.md`维护模块设计、局部约束与逐文件索引；`.cursor/rules/`维护可执行的前后端设计原则；`docs/PRD/`维护产品行为。

## 4. 后端 DDD 设计

后端采用 DDD 和端口适配思想。一级模块是限界上下文，典型结构如下：

```text
<moduleName>/
├── __init__.py       # 跨模块公开门面
├── api.py            # Router、请求响应和HTTP错误转换
├── application.py    # 用例、事务、补偿和跨对象编排
├── domain.py         # 实体、值对象、不变量和纯计算（按需）
├── repository.py     # 模块表、SQL、映射和持久化适配（按需）
└── <adapter>.py      # o3dv、trame、quarto、converter等模块专属适配器
```

调用方向：

```text
server → module.api → application → domain/repository/adapters → infrastructure
```

强制边界：

- Router 不执行 SQL，只做协议适配。
- Application 定义用例、聚合协作和事务边界。
- Domain 不依赖 FastAPI、SQLite、Server，也不提交事务。
- 所有写操作经过所属模块 Repository；Repository 独占模块表和 SQL，并复用公共 SQLite 原语。
- 跨模块只导入目标模块 `__init__.py`，不访问内部 Repository、SQL 或 Domain。
- Server 不执行产品业务和业务表迁移。
- Infrastructure 不包含资产、任务、报告等业务语义。

## 5. `visPhysField` 二级业务设计

`visPhysField` 是一个大型一级限界上下文，其二级业务统一放入 `modules/`：

```text
visPhysField/
├── api.py
├── application.py
├── domain.py
├── repository.py
├── trame.py
└── modules/
    ├── fieldVisualization/
    ├── dataExtraction/
    └── dataOverview/
```

- `fieldVisualization`：视角、云图、矢量、切面/流线/等值分析、Probe、色带、显示样式、时序、动画和多结果。
- `dataExtraction`：点/线/面/体空间提取、时序提取和聚合提取。
- `dataOverview`：二维表格、散点/折线/柱状图和多维云图。

二级模块只保存自身业务模型、规则、Hook、Component和局部样式，共享一级 Router、Application、Repository、SQLite、Trame Server、前端 API、Provider、Store 和路由。禁止建立二级 Router、Repository、数据库连接、端口、`api.js`、`module.js` 或跨一级模块公开门面。

调用方向：

```text
visPhysField.api
  → visPhysField.application
  → visPhysField.modules.<businessModule>
  → visEngine公开内核（仅在需要纯计算时）
  → visPhysField.repository
```

## 6. `visEngine` 边界

`visEngine` 只允许：

- VTK/数值纯计算原语。
- 无业务语义的缓存、内存和性能优化。
- 可由多个业务模块复用、且不依赖业务配置的内核代码。

严禁放入 Router、Server、URL、Trame状态/Server、Repository、SQLite、业务配置、云图用例、任务、资产或报告语义。云图、时序和多结果等产品功能即使调用 VTK，也仍属于 `visPhysField`。

## 7. 前端微领域驱动设计

前端以模块为第一层，并采用轻量的微领域驱动思想：围绕业务对象和用例组织代码，但不机械复制后端 DDD 层级。

```text
modules/<moduleName>/
├── index.js          # 跨模块唯一公开门面
├── module.js         # 路由、导航和权限元数据
├── model.js          # 前端实体、值对象和状态字典
├── api.js            # Endpoint、请求和DTO防腐转换
├── hooks/            # Query、Command、状态与副作用编排
├── components/       # 本领域可复用组件
└── pages/            # 路由页面与业务区域组合
```

- Page 保持干净，只组织布局和页面业务区，可通过目标模块 `index.js` 组合多个聚合业务对象。
- Component 不直接发起网络请求，通过 Props/事件和 Hook 协作。
- `api.js` 已合并 URL、请求和 DTO 转换，不另建 `url.js`。
- 小模块按实际功能精简文件；没有 UI 的 `MCP`、`visConvertor`、`visEngine` 不建立前端空目录。
- `frontend/src/infrastructure/components` 是共享组件基座，只放无业务语义的布局、导航、反馈、表单和数据展示组件；模块内 `components` 保存领域组件。
- Infrastructure 不得反向导入业务模块。

## 8. 持久化、文件和可观测性

```text
var/
├── db/ai4e_vis.sqlite3
├── objects/datasets/
├── derived/{profiles,conversions,previews,snapshots,animations}/
├── exports/{visualizations,reports}/
├── quarantine/
├── tmp/
├── logs/
├── telemetry/
├── runtime/
└── backups/
```

- SQLite 公共连接、WAL、外键和事务原语归 Infrastructure；表、SQL和映射归所属模块 Repository。
- 数据库只保存相对 `storage_key`；用户上传按 SHA-256 寻址。
- `dataAssets` 拥有资产和分类历史，`visDatasets` 只提供分析并经 `dataAssets` 公开门面回写。
- 日志采用结构化 JSONL 和轮转；埋点失败不得影响业务；数据质量检测归 `visDatasets`，技术健康归 Infrastructure。
- 内置案例放 `resources/`，测试数据放 `fixtures/`。测试只能使用临时 SQLite 或一致性副本。

## 9. 注释和自动架构门禁

- Python 文件具备中文模块 Docstring，公开类/函数/方法具备中文 Docstring。
- JS/JSX 文件具备中文文件头，导出 Component/Hook/函数具备中文 JSDoc。
- 复杂 SQL、事务补偿、坐标/单位、Effect/Memo/Callback、复杂 JSX 和性能取舍解释原因。
- 自动门禁检查 Router/SQL、模块依赖、二级禁止项、`visEngine` 依赖、中文注释、Context文件索引和前端模块公开门面。

## 10. 修改流程与测试验收

每次改动必须遵循：

1. 从 `.context` 定位模块，阅读 PRD、前端到后端、持久化和测试的完整上下游链路。
2. 同步模块 `.context`、模块 PRD或 `docs/PRD/CHANGELOG.md` 和对应测试用例。
3. 发现、复现或修复错误时更新根 `error.log`。
4. 先运行受影响模块测试，再运行契约和架构测试；跨页面或三服务链路补 Playwright。
5. 新入口和全量回归通过、生产引用归零且已有 Git 恢复点后，才能删除旧文件；运行数据库与上传资产不得当成散乱源码删除。

功能回归必须保持解析、资产去重与画像、方法目录和参数Schema、ECharts/Perspective/Trame/O3DV、VisualizationSpec版本、可视化保存、报告冻结/编排/导出以及现有SQLite数据。Excel功能继续区分 `implemented`、`partial`、`demo_only`、`unverified` 和 `not_implemented`，不得扩大已实现口径。

## 11. 文档职责与防漂移

- 本文回答“为什么这样设计”和“总体边界是什么”。
- `.context/index.md` 回答“总体架构如何导航”。
- `.context/modules/*.md` 回答“模块边界、调用方向、持久化所有权和每个文件在哪”。
- `.cursor/rules/*.mdc` 把设计原则变成编码时可执行约束。
- `docs/PRD/*.md` 回答用户可见功能和验收。
- `MODULAR_REFACTOR_PLAN.md` 记录迁移批次、测试和删除证据。

任何一处架构变化都必须同步这些受影响文档和架构测试，避免计划、索引、规则与真实代码再次分叉。


## Dojo 内独立部署与资产交付

后端仍按十三个一级模块进行轻量 DDD 分层，物理场二级功能共用一级会话；前端仍为 JSX 微领域，原库目录并列保留。`visTaskManage/fileSpecRepository` 管不可变配置，`visIO/assetRepository` 管资产索引，`visIO/exports` 管输出状态与独立生产进程，`visPhysField/scene` 管工作区 VTK 对象，`visEngine` 提供纯过滤与采样。

每个交互工作区独占一个 Trame 进程，多个视口共用该工作区。IPC 请求带身份并串行进入工作进程主事件循环；超时或进程退出使会话失效，不复用迟到响应。独立输出进程可取消，避免长动画阻塞交互。默认四会话、十五分钟无心跳回收，可通过实例配置调整。

存储区域由可信宿主或独立 CLI 注入；配置/导出位于任务 visualizations，缓存位于明确运行根。保存不将原始网格、数组、临时 URL 或端口写入 spec，也不生成缩略图。来源通过固定引用解析，文件、复合文件成员及时间成员均核验；变化后需用户显式重新绑定为新配置。

新保存路径保留旧 URL，但缺上下文返回明确错误。旧 SQLite 读取协议保留，历史数据不迁库。原图表继续使用旧渲染实现，新保存转为配置资产。全局 Dojo 架构只维护包间交接，包内规则和 PRD 继续主动维护。

## 三维对象工作台的增量交互（2026-09-14）

Trame 工作台由布局装配、控制器、工具栏、对象树、属性、视图与时间组件构成；React 仅组合保存/导入/导出弹窗。工作会话使用具名管线对象，显示实例通过输入对象与视图身份绑定；计算和着色字段分离。计算事务构建候选下游输出后提交，显示更新只更换 mapper/property，不运行上游过滤器。工作进程有界复用 renderer，避免 Trame 同步期间析构回调失效。

物理配置版本 2 保存来源、pipeline、layers、probes、views、单一 layout、time 和 link_groups。旧版本只在内存适配，配置仓库与导出仓库所有权保持不变。工作区选择/草稿不持久化，配置保存不改变任务版本。基础对象的内存输入保留完整体数据；显式等高线可从基础对象表面提取。

宿主追加来源先经 Server 校验，再调用 Vis 可信控制接口；公开 session commands 禁止注入路径绑定。独立模式仅接受已登记资产 ID。追加加载失败不提交来源上下文。所有二级业务共享一级命令和会话；不新增二级 Router、Repository 或 Trame Server。

本地渲染为每个 native 对象分配生命周期内稳定、不复用的序列化身份；主视图及装饰层相机在场景加载后显式同步，不能依赖 vtk.js 的一次性相机初始化。Probe、方向轴与时间采用可导出的几何注记，标签按当前视口投影限制尺寸和位置，固定空间锚点不变。

相机位置恢复后按可见网格重算派生裁剪范围，联动相机使用关联视图合并边界；范围只进入实时渲染状态，不写物理配置身份。本地相机同步包含该范围，PNG/视频使用同一场景规则。Probe CSV 的单分量采样解包为数值，矢量保留分量列表。
