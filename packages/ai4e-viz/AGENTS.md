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

Dojo 根上不要用只含 `dev`、不含 visualization / `ai4e-viz[workbench]` 的 `uv sync` 覆盖环境，否则官方 8000 拉后处理会 `vis_service_start_failed`。改 viz 源码后才需要 `--reinstall-package ai4e-viz`：安装副本是 force-include，8000 不读 `packages/`。纪律见根 `AGENTS.md`「注意事项」。

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

物理配置版本 2：导入创建纯色基础显示，计算字段与着色字段分离；属性计算与显示 Apply，顶部快捷操作增量更新。流线可选线段、球体、平面或命名面起点，本期暂时不做拖种子，可用「显示种子」隐藏；显示可选线或圆管并调节粗细与圆管面数；本地坐标轴在轨道过程中实时跟随；切面与剖切选中时用可视平面三向拖动和轴对齐，拖动只预览、应用才切开。Trame 拥有完整 UI，宿主负责来源授权和资产表单。对象、相机及本地序列化身份保持稳定；不能用裸内存地址作为跨更新的对象身份。验收参见 Dojo `.context/mvp/phys-workbench-acceptance.md`，本地/远程浏览器和 Linux 阴影分别记录。

三维响应与独立显隐（2026-09-15）：眼睛只控制单对象当前视图；来源分组无总开关，父子计算与删除依赖保持。首次草稿必须同步平面手柄，连点不重复同步。普通移动不发计算 RPC；透明度不重建着色数组。新增真实 Trame State 回归 `test_phys_display_updates.py`，禁止用字典替身证明状态 API 正确；宿主验收必须从 Dojo Web 点击 iframe 并检查实际画面，入口为根 `e2e/trame-responsiveness.spec.ts`。


三维交互与对象隔离（2026-09-16）：新对象计算和显示草稿一起提交；辅助平面独立显隐，三轴平移与三轴旋转仅命中手柄启动；删除局部清理不重建背景和相机。种子和Probe有候选预览，等高线支持自动分层，同标量等值面保留生成标量。添加辅助平面后旋转/平移/缩放不得被旧相机拉回。圈定 `test_phys_interaction.py`、`test_phys_objects.py`、`test_phys_display_updates.py`、`test_phys_filters.py`、配置/存储用例与 `viz_interaction_browser.cjs`；最终范围见根 `.context/mvp/phys-workbench-acceptance.md`，正式8000/5173不自动更新。

着色与显示设置（2026-09-16）：属性计算/显示均应用后生效，顶部快捷操作只提交自身字段；映射器更新必须显式替换输入，不能以标量可见或色标变化代替模型像素验收。色标、范围和背景可保存，透明PNG/序列读回校验alpha。圈定 `test_phys_display_settings.py`、显示/对象/过滤器/配置/存储用例及真实本地、远程与宿主浏览器；源码、隔离安装、正式发布分别记录，正式8000/5173不自动更新。

三维工作台十一项增强（2026-09-17）：LIC 按需远程窗口、皱折/三角化、种子显隐与草稿手柄、目录内网格导入、等值滑条、色标相等、Probe 表、线段提取。圈定 `test_phys_display_settings.py`、`test_phys_filters.py`、`test_phys_interaction.py`、`test_phys_views.py`、`test_phys_objects.py`、`test_phys_plot_over_line.py` 与前端 `interaction.test.js`。正式 8000/5173 须当次同意。

Probe 点选拾取（2026-09-17）：属性区可见开/关，开着点模型出球、应用出表，关着不拾取；切到其他工具开关回到关。圈定 `test_phys_interaction.py`。正式 8000/5173 须当次重装并重启后才能冒烟。

工作台色标、Probe 与视图联动（2026-09-17）：色标入口在属性「显示设置」图标，弹层带对象名和「应用」，只写当前选中对象；Probe 点选只留一个开关；加号菜单贴按钮；点窗切活跃并刷新左侧眼睛；折线图树只列线段提取；去掉取样物理量。相机联动开启后覆盖当前全部窗口，不要求共同坐标空间。圈定 `test_phys_display_settings.py`、`test_phys_interaction.py`、`test_phys_display_updates.py`、`test_phys_plot_over_line.py`、`test_phys_views.py` 与前端 `interaction.test.js`。色标下移后须再重装并换 Vis 才能在正式入口看到。证据见根 `.context/mvp/phys-workbench-acceptance.md`。

Surface LIC 远程交接防崩（2026-09-17）：选 LIC 先出远程静帧再开拖转；无向量、建图或第一帧失败只提示并回退，不切半套远程。圈定 `test_phys_display_settings.py`、`test_phys_display_updates.py`、`test_phys_views.py` 与前端 `interaction.test.js`。18:42 已重装并换 Vis，正式后处理三维页点 LIC 后会话仍在，缺向量只提示。证据见根 `.context/mvp/phys-workbench-acceptance.md`。


## 正式发布与宿主 Web 冒烟（硬规则）

宿主消费链的 Vis 改动：未重装 `ai4e-viz`、未回收正式 8000 的旧 Vis 子进程时，正式 Web 验收不了；Agent 必须自己在用户 5173→8000 冒烟，隔离口与「待发布」不算完成。未授权不得擅自重装/重启正式入口，必须当场申请。完整条文只在根 `AGENTS.md`「发布与正式 Web 冒烟验收」。
