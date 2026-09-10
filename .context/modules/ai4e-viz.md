# ai4e-viz 模块索引

## 模块边界

- 状态：**PLANNED**，MVP1 报告阶段前不实施交互渲染。
- 职责：读取稳定 run/report artifact，生成静态或交互视图。
- 允许依赖：`ai4e-spec` 和独立渲染库。
- 禁止依赖：`ai4e-core`、模型、Trainer、Dataset 实现。
- 计算边界：误差、守恒量、切片等物理计算归 core；viz 只负责表达。
- 结构原则：按稳定 artifact 的读取、渲染和组合能力聚合，不使用 DDD 或 Web 微领域目录。

## 目录索引

- `packages/ai4e-viz/`：包工程根兼 viz 源码根；未来由构建配置映射为 `ai4e_viz` 导入名。
- `packages/ai4e-viz/render/`：稳定 artifact 到单一图形/视图的渲染。
- `packages/ai4e-viz/compose/`：多个已渲染视图的布局与组合。

## 文档索引

- `packages/ai4e-viz/README.md`：包职责、依赖边界和 PLANNED 状态。
- `.context/modules/ai4e-viz.md`：本模块的目录与文档检索入口。
- `.context/mvp/abupt-mvp1.md`：MVP1 报告和可视产物所处阶段。
- `.cursor/rules/ai4e-algorithm-architecture.mdc`：本包的能力分层、高内聚低耦合与代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解 artifact 与可视化解耦原因时按需读取。

新增目录或文档时必须同步本索引。
