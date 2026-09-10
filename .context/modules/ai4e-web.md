# ai4e-web 模块索引

- `docs/prototypes/dojo-rawprep-detail.html`：原始数据处理独立细节原型；已落盘文件统一浏览、字段选择与输出计划、文本／张量／三维弹窗。`tests/integration/rawprep_detail_browser.cjs` 检查对应交互。

## 模块边界

- 状态：**PLANNED**，本阶段只保留包位置。
- 职责：未来展示 run、对比、报告和任务状态。
- 允许依赖：稳定的 ai4e-server API 或版本化 artifact schema。
- 禁止依赖：core、模型、Trainer、Dataset 与本地文件布局细节。
- 前端框架、语言、构建工具和状态管理尚未决定；确定前必须新增 ADR。
- 结构原则：按用户任务形成自治微领域，不镜像后端 package 或接口目录。

## 目录索引

- `packages/ai4e-web/`：Web 包占位。本阶段不创建 `src/`、`package.json` 或构建配置。

## 文档与规则索引

- UI 参考图（用户提供）：`docs/prototypes/项目管理-项目导航-首页.png`、`docs/prototypes/项目管理-任务管理.png`、`docs/prototypes/项目管理-版本树.png`、`docs/prototypes/任务工作台-原始数据处理.png`。首页四张封面裁片内嵌在 HTML 中，不依赖外部图片。
- 原型 v3：浅蓝视觉、双列卡片、纵向血缘图、原始处理三栏和底部日志。能力来源为 `recipes/aero_cfd/{config.yaml,datapre.py,trainprep.py,train.py,post.py,pipeline.py}`、`packages/ai4e-core/applications/aero_cfd/rawprep/dataset.py`、`packages/ai4e-contrib/application/datasets/shapenet_car/manifest.yaml`。
- 浏览器测试新增项目范围／领域、原始处理示例匹配、PT/VTKHDF、预检和模拟执行日志、recipe 配置／顺序／交接弹窗。仍只验证 UI，不产生实跑证据。

- `docs/prototypes/dojo-web-wireframe.html`（左侧仅两个一级入口，项目六 Tab 位于主视区）：可点击线框稿，项目六 Tab 与工作台八步；左侧推拉菜单、项目／文件搜索筛选排序、任务进度和阶段参数比较；文件与 ParaView 风格三维视图均为占位，无真实文件解析，新增项目共用示例内容，刷新恢复样例。
- `tests/integration/web_wireframe_browser.cjs`：浏览器链路检查；运行时由 `PLAYWRIGHT_MODULE` 指定或使用已安装的 `@playwright/test`。

- `docs/PRD/ai4e-web/src/PRD.md`：Dojo WEB 平台产品设计草案，两个产品入口、项目内六个 Tab、八步工作台及版本比较交互。src 是拟定源码一级目录，此设计稿不表示源码存在。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 19 节：架构 v2，app 组合页面、十三个候选微领域及公开门面；技术栈仍为待 ADR 确认的建议。
- `tests/integration/test_web_design_documents.py`：本次设计稿文档检查；平台行为未验收。

- `packages/ai4e-web/README.md`：包职责、依赖边界和 PLANNED 状态。
- `.context/modules/ai4e-web.md`：本模块的目录与文档检索入口。
- `.cursor/rules/ai4e-web-architecture.mdc`：Web 文件改动时必须读取的微领域、稳定接口边界与书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解 Web、server、task 和 artifact 的全局关系时按需读取。

新增目录、文档或技术栈 ADR 后必须同步本索引。
