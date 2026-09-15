# AI4E_Vis

AI4E_Vis 是面向工程数据的可视化与报告平台，覆盖数据资产管理、格式解析与画像、可视化推荐、几何/物理场显示、VisualizationSpec 保存，以及报告编排和导出。

当前仓库采用前后端模块优先架构：后端以 DDD 限界上下文组织 Python/FastAPI/SQLite/Trame + VTK 代码；前端以微领域驱动思想组织 JavaScript/React 页面、业务对象和组件。详细设计见 [`docs/architecture/architecture.md`](docs/architecture/architecture.md)。

## 业务主链路

```text
数据上传或内置案例
  → 数据资产登记与SHA-256去重
  → 格式解析、画像和质量检测
  → 可视化方法推荐与参数配置
  → O3DV / Trame+VTK / 图表Renderer预览
  → VisualizationSpec与可视化资产保存
  → 报告编排、冻结版本与HTML/PDF导出
```

## 十三级业务模块

| 模块 | 职责 |
| --- | --- |
| `dataAssets` | 资产登记、上传、去重、列表/详情、分类历史和原始文件 |
| `visTaskManage` | 目录、推荐、参数 Schema、示例和 VisualizationSpec 版本 |
| `visGeometry` | 几何表现、视角及自托管 O3DV 适配 |
| `visDatasets` | 格式解析、数据画像、质量体检、统计和内容查看 |
| `visPhysField` | 三维物理场显示、数据提取、数据概览和统一 Trame 会话 |
| `visFigure` | PNG/JPG 等同源静态预览 |
| `visIO` | 可视化资产保存、冻结、查询、报告引用和导出边界 |
| `visConvertor` | 几何/数据格式转换及失败诊断 |
| `automation` | 脚本模型、校验、保存和执行边界 |
| `MCP` | 将一级模块公开用例封装为 MCP 工具 |
| `reportManage` | 报告中心、版本、冻结、复制和导出 |
| `reportDesigner` | ReportDocument、草稿、布局和历史操作 |
| `visEngine` | 无业务语义的 VTK/数值内核、缓存和性能原语 |

`dataAssets` 拥有资产和文件生命周期，`visDatasets` 只负责理解数据内容；二者不共享 Repository。`visPhysField` 的 `fieldVisualization`、`dataExtraction`、`dataOverview` 是二级业务模块，共享一级 Router、Application、Repository、SQLite 和 Trame 基座。`visEngine` 不允许放置 Router、URL、Trame Server、SQLite 或产品业务。

## 目录结构

```text
AI4E_Vis/
├── AGENTS.md                 # 唯一开发规范入口
├── .context/                 # 总体与逐模块文件索引
├── .cursor/rules/            # 前后端可执行设计规则
├── backend/
│   ├── server/               # 进程和Router装配
│   ├── modules/              # 十三级后端业务模块
│   ├── infrastructure/       # 无业务含义的公共技术基座
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/              # React应用装配
│       ├── modules/          # 有UI能力的前端业务模块
│       └── infrastructure/   # HTTP、Renderer和共享组件基座
├── docs/
│   ├── PRD/
│   ├── architecture/
│   ├── migration/
│   └── testing/
├── resources/               # 内置业务案例
├── fixtures/                # 测试数据
├── var/                     # SQLite、对象、导出、日志和运行状态
└── run_project.py           # 三服务统一启动器
```

可视化应用的规则入口为包根 [`AGENTS.md`](AGENTS.md)，与 Dojo 根规则按作用域衔接。各模块的边界、文件位置和局部开发约束统一维护在 [`.context/index.md`](.context/index.md) 及 `.context/modules/`，不在代码子目录散放 `AGENTS.md`。

## 技术栈

- 后端：Python 3.12、FastAPI、SQLite、Trame、VTK。
- 前端：JavaScript/JSX、React 18、Vite 5、Ant Design。
- 三维几何：仓库自托管 Online3DViewer（O3DV）。
- 三维物理场：Trame + VTK/vtk.js。
- 报告：React 同版式冻结导出及锁定版本 Quarto 1.10.18。

## 安装和当前入口

在 Dojo 根目录运行：

```bash
uv sync --group visualization
npm ci --prefix packages/ai4e-viz/frontend
npm run --prefix packages/ai4e-viz/frontend build
uv sync --group visualization --reinstall-package ai4e-viz
uv run --no-sync ai4e-vis --runtime-root /absolute/runtime --context /absolute/trusted-context.json
```

打开命令输出的工作台地址。Dojo Server 自动启动独立 Vis 子进程，通过同源 HTTP/WebSocket 代理嵌入这个应用。保存只写项目—任务下的配置；PNG/CSV/WebM/MP4 需显式导出。输出位置、可信 context 示例、脚本操作和真实验收见 [迁移接入说明](docs/migration/dojo-integration.md)。

原三服务示例启动器仍保留：在 Dojo 根运行 `uv run --no-sync packages/ai4e-viz/run_project.py start`，对应的 `status` 和 `stop` 管理它启动的服务。九示例模式属于兼容展示；新物理工作区由每会话独立 Trame 进程提供。运行根在源码与安装目录外，不能用旧 `var/` 路径保存任务可视化。

## 历史数据与持久化布局（兼容读取）

```text
var/
├── db/ai4e_vis.sqlite3       # 当前SQLite业务库
├── objects/datasets/         # SHA-256寻址的上传对象
├── derived/                  # 可重建画像、转换、预览和动画
├── exports/                  # 可视化与报告导出
├── logs/                     # 结构化业务日志
├── telemetry/                # 本地埋点
├── runtime/                  # 服务PID与进程输出
└── backups/                  # 一致性备份
```

当前 SQLite 业务库位于 `var/db/ai4e_vis.sqlite3`，数据库只保存相对 `storage_key`。所有写操作经过所属模块 Repository；公共 SQLite 连接、WAL、外键和事务原语位于 `backend/infrastructure/persistence/`。测试必须使用临时 SQLite 或副本，不得写真实运行库。

## 测试

后端模块与架构测试：

```bash
cd backend
.venv/bin/python -m pytest tests/modules/test_<module>.py tests/test_architecture.py -q
```

前端架构、单元测试和构建：

```bash
cd frontend
npm run check:architecture
npm test
npm run build
```

跨页面和三服务业务链路使用 `npm run test:e2e`。Excel“功能模块”Sheet 的逐项状态和验证证据见 [`docs/testing/EXCEL_FEATURE_TEST_MATRIX.md`](docs/testing/EXCEL_FEATURE_TEST_MATRIX.md)；`partial`、`demo_only` 和 `not_implemented` 不得表述为完整实现。

## 报告下载

- 内置审计报告在下载时冻结当前 API 数据，并生成当前 React 阅读页的自包含 HTML 或同版式 PDF。
- 用户编排的 ReportDocument 通过锁定的 Quarto 1.10.18 导出。
- 原始数据由数据资产模块管理，不把 Python、NPZ 或归档 HTML 冒充为报告下载。

## 安全清理与移植

查看可清理内容，默认不会删除：

```bash
backend/.venv/bin/python backend/scripts/maintenance.py
```

应用清理前建议先停服。`--apply` 只允许删除可重建缓存、测试/构建产物、失败或无引用导出；不得删除数据资产、上传对象、fixture、SQLite 业务记录、最新报告或 Renderer 依赖。

```bash
backend/.venv/bin/python run_project.py stop
backend/.venv/bin/python backend/scripts/maintenance.py --apply
backend/.venv/bin/python run_project.py start
```

检查便携包范围或在仓库外生成 ZIP：

```bash
backend/.venv/bin/python backend/scripts/create_portable_bundle.py --check-only
backend/.venv/bin/python backend/scripts/create_portable_bundle.py --output /tmp/AI4E_Vis-portable.zip
```

## 开发文档入口

1. [`AGENTS.md`](AGENTS.md)：唯一开发入口、语言/框架约束和强制修改流程。
2. [`.context/index.md`](.context/index.md)：总体架构、模块位置与逐文件索引。
3. [`docs/architecture/architecture.md`](docs/architecture/architecture.md)：模块化架构设计。
4. [`docs/PRD/README.md`](docs/PRD/README.md)：十三级模块产品需求入口。
5. [`docs/api/README.md`](docs/api/README.md)：API 文档入口。
6. [`docs/migration/MODULAR_REFACTOR_PLAN.md`](docs/migration/MODULAR_REFACTOR_PLAN.md)：迁移批次、删除与测试证据。
7. [`docs/testing/BASELINE.md`](docs/testing/BASELINE.md)：回归基线。

开始修改前必须沿 Page/API/Router/Application/Domain/Repository/持久化和测试阅读完整链路；每次修改同步 `.context`、PRD 和测试，错误记录到根 `error.log`，代码必须具有中文注释。


## Dojo 已有可视化库入口

# ai4e-viz

通过稳定文件独立检查和生成显示资产；只依赖 spec 和第三方读取/渲染库，不构建模型或执行训练。

`uv run python -m ai4e_viz` 从标准输入读取请求。旧 `{path,operation,options}` 请求继续返回单 JSON；协议版本 1 请求返回 NDJSON progress/result/error。服务解析源路径并管理操作、取消及缓存生命周期。

新增 pipeline 执行表面、平面切片/裁切、标量阈值、点标量等值。体网格先过滤再抽取显示表面；点云不自动重建体，单元标量不自动插值到点。serialization 将坐标、拓扑、字段、掩码写入分离二进制文件并最后发布 manifest。默认单显示结果限制 128 MiB。

VTK 家族、HDF5/H5、PT/NPY/Zarr 支持成员和维度切片；PT 使用 weights_only。HDF5 多样本同构组只列一份字段。大整数以字符串传给表格保持精度。字段统计只用于观察，不作为归一化配置。

验证：`uv run pytest tests/integration/test_viz_pipeline.py tests/integration/test_viz_file_preview.py`。当前新增工作区仍需完整浏览器资源、联动及原型视觉验收；不能以构建通过声明全部可视化交付。
