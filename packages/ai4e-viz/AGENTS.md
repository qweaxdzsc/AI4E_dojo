# AI4E_Vis 开发入口

本文件只负责给出权威信息入口和强制工作流，不重复维护详细架构。用户当前要求优先于仓库文档；文档之间冲突时，以产品 PRD 和当前代码事实为准，并同步修正文档。

## 固定阅读顺序

1. 阅读本文件，确认语言、框架和修改纪律。
2. 阅读 [`.context/index.md`](.context/index.md)，理解前后端总体架构并定位所属一级模块。
3. 阅读 `.context/modules/<module>.md`；`visPhysField` 还要读取其[二级模块索引](.context/modules/visPhysField/index.md)。
4. 阅读对应 [`docs/PRD/`](docs/PRD/) 和上下游模块 PRD；总体架构设计见 [`docs/architecture/architecture.md`](docs/architecture/architecture.md)，迁移执行证据见 [`MODULAR_REFACTOR_PLAN.md`](docs/migration/MODULAR_REFACTOR_PLAN.md)。
5. 后端代码加载[后端 rule](.cursor/rules/ai4e-vis-backend.mdc)，前端代码加载[前端 rule](.cursor/rules/ai4e-vis-frontend.mdc)，规划任务同时读取[计划 rule](.cursor/rules/plan-business-alignment.mdc)。
6. 最后阅读目标源码、调用方、持久化实现和测试，不得用索引代替代码事实。

## 技术栈与语言

- 后端使用 Python 3.12、FastAPI、SQLite、Trame、VTK；依赖唯一入口是包 `pyproject.toml` 与 Dojo 根 `uv.lock`；[`backend/requirements.txt`](backend/requirements.txt) 仅保留为历史基线。
- 前端使用 JavaScript/JSX（不擅自改 TypeScript）、React 18、Vite 5、Ant Design；依赖由 [`frontend/package.json`](frontend/package.json) 和锁文件管理。
- 三维几何继续使用自托管 O3DV；三维物理场继续使用 Trame + VTK。不得未经需求和回归测试替换框架、数据库或公开协议。

## 安装与启动

```bash
uv sync --group visualization
npm ci --prefix packages/ai4e-viz/frontend
npm run --prefix packages/ai4e-viz/frontend build
uv run ai4e-vis --context /absolute/path/context.json
```

`run_project.py` 保留旧三服务启动兼容；新安装入口为 `ai4e-vis`。可信 context JSON 包含任务 scope、固定来源 sources 与运行 bindings。无 context 可浏览旧示例；保存不回退到代码目录。详细迁移见 `docs/migration/dojo-integration.md`。

## 代码编写与修改的强制规范

1. 每次需求和改动开始前，必须从 [`.context/index.md`](.context/index.md) 找到所属一级模块，完整阅读需求问题的上下游链路，包括相关 PRD、前端 Page/Component/Hook/API、后端 Router/Application/Domain/Repository、数据库/文件持久化以及测试；不得只看报错文件或单个函数，以防遗漏联动修改。
2. 实现时保持十三级一级业务模块高内聚。`dataAssets`拥有资产登记、上传、文件和`artifacts`表，`visDatasets`拥有解析、画像、体检和内容查看；跨后端模块只用目标 `__init__.py`，跨前端模块只用目标 `index.js`。
3. 每次修改必须同步对应 `.context` 文件、[`docs/PRD/`](docs/PRD/) 中的模块 PRD 或 [`CHANGELOG.md`](docs/PRD/CHANGELOG.md)，并新增或更新对应测试用例；新增、删除、移动文件时必须同步文件索引和职责。
4. 发现、复现或修复错误时，必须在根 [`error.log`](error.log) 记录日期、完整链路、现象、根因、修复和验证；不得记录密钥、用户数据或大段堆栈。没有发现错误时不得制造错误记录。
5. 每次代码书写都必须有中文注释：Python、JS、JSX 和 CSS 文件必须有中文文件头，公开 Python 项必须有中文 Docstring，导出前端项必须有中文 JSDoc，复杂分支、SQL、Effect 和性能取舍必须解释“为什么”。
6. 每次修改之后必须执行对应部分的测试用例：先跑受影响模块测试，再跑契约/架构测试；跨页面或三服务链路变更还要跑 Playwright。测试失败不得用构建成功替代，也不得删除旧实现掩盖回归。

## 边界与持久化

- Router 不执行 SQL；Application 编排事务；Domain 保存纯规则；Repository 独占模块表与 SQL，公共 SQLite 原语在 `backend/infrastructure/persistence`。
- `visEngine` 只放 VTK/数值内核、缓存和性能原语，不放 Router、URL、Trame Server、SQLite、任务、资产或报告业务。
- 新配置与显式导出只写调用者提供的项目—任务 `visualizations/`；原数据只读引用。运行缓存默认用户缓存目录，可通过启动参数指定；不能写源码或安装树。历史 SQLite 只保留旧读取协议，旧新保存 URL 均必须携带有效上下文。

## 最低验证命令

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules/test_vis_asset_storage.py packages/ai4e-viz/backend/tests/test_architecture.py -q
npm run --prefix packages/ai4e-viz/frontend check:architecture
npm run --prefix packages/ai4e-viz/frontend test
npm run --prefix packages/ai4e-viz/frontend build
```

涉及 API、路由、跨模块、数据库、O3DV、Trame 或报告导出时，在模块测试之外补跑对应契约、集成或 E2E。验证入口见 [`.context/index.md`](.context/index.md)。

## Dojo 融合边界

- 保留十三个业务模块、轻量 DDD、前端 JSX 微领域与物理场二级模块。现有 `inspect/preview/pipeline/serialization/render/compose/runtime` 保留算法库组织方式。
- Vis 仅依赖 spec 与第三方可视化库，不能导入 task/server/core/contrib；独立进程内保留源模块导入命名。
- `visTaskManage` 校验与保存不可变 spec 修订，`visIO` 原子提交资产及导出；`visPhysField` 管理工作区及真实物理计算，`visEngine` 只有计算原语。
- 保存不复制网格、不自动截图、不创建研究版本、不写 run/writer 目录。运行对象、端口、绝对数据路径不能进入 spec。
- 所有 Python 命令使用 `uv run`。测试采用 importlib 导入避免包的 inspect 目录遮蔽 Python 标准库；实际安装与独立 CLI 也要验证。
- 完整迁入、配置资产链路、物理场功能分开验收；Linux 阴影不能以 macOS 构建通过替代。

## 三维对象工作台

物理配置版本 2：导入创建纯色基础显示，计算字段与着色字段分离；计算 Apply，显示增量更新。流线可选线段、球体、平面或命名面起点，应用后显示不可拖的种子；切面与剖切选中时用可视平面三向拖动和轴对齐，拖动只预览、应用才切开。Trame 拥有完整 UI，宿主负责来源授权和资产表单。对象、相机及本地序列化身份保持稳定；不能用裸内存地址作为跨更新的对象身份。验收参见 Dojo `.context/mvp/phys-workbench-acceptance.md`，本地/远程浏览器和 Linux 阴影分别记录。
