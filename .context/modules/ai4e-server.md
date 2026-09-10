# ai4e-server 模块索引

## 模块边界

- 状态：**PLANNED**，MVP1 本地闭环不依赖服务。
- 职责：未来提供多用户索引、协作和稳定 API，不保存唯一真相。
- 允许依赖：`ai4e-spec`、`ai4e-task`。
- 禁止依赖：core 内部模型、Trainer、recipes 和本地训练进程对象。
- 数据边界：消费 run/artifact 引用；训练必须在没有 server 的机器上完整运行。
- 结构原则：围绕协作、任务和资源生命周期采用轻量 DDD；领域规则不依赖 Web、存储和执行基础设施。

## 目录索引

- `packages/ai4e-server/`：服务包占位。内部技术栈、接口形式和源码目录尚未决定，ADR 确认前不扩展虚构结构。

## 文档索引

- `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 19 节：Web / Server 架构 v2（DRAFT），业务 API 按上下文组织；task 拥有项目、任务、版本和执行，server 拥有报告编辑发布。目标目录未创建。
- `docs/PRD/ai4e-web/src/PRD.md`：平台用户流程与交互设计，server 接口的产品需求来源。
- `tests/integration/test_web_design_documents.py`：设计稿链接、章节与来源检查，不替代服务验收。

- `packages/ai4e-server/README.md`：包职责、依赖边界和 PLANNED 状态。
- `.context/modules/ai4e-server.md`：本模块的目录与文档检索入口。
- `.cursor/rules/ai4e-backend-ddd.mdc`：本包的限界上下文、依赖倒置和代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解平台层与本地训练解耦原因时按需读取。

新增目录、接口文档或 ADR 后必须同步本索引。
