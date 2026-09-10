# ai4e-spec 模块索引

## 模块边界

- 状态：可安装，已交付最小 ModelFactory/ModelRequirements；完整 FieldSpec、Sample 和 artifact schema 仍为规划。
- 职责：定义 FieldSpec、Sample/Batch、组件协议、artifact schema、内容 key 和兼容检查。
- 允许依赖：Python 标准库中的 typing、dataclasses、enum、hashlib 等轻量能力。
- 禁止依赖：其他 ai4e 包、torch、numpy、训练器、渲染器和服务。
- 下游：core、recipes、task、viz、server 和外部组件。
- 结构原则：算法契约包按稳定语义高内聚组织，不使用 DDD 目录；实现遵循 `ai4e-algorithm-architecture.mdc`。

## 目录索引

- `packages/ai4e-spec/`：包工程根兼稳定契约源码根；由构建配置映射为 `ai4e_spec` 导入名，不放运行时编排。
- `packages/ai4e-spec/data/`：FieldSpec、Topology、Rank、State、Sample、Batch 等数据语义契约。
- `packages/ai4e-spec/components/`：已交付 model.py 的构造/描述/预测协议与 dataset.py 的读取/内容身份/描述协议；持久视图描述包含可恢复引用。
- `packages/ai4e-spec/artifacts/`：Artifact schema、引用、内容寻址 key 和兼容元数据。
- `packages/ai4e-spec/check/`：契约与兼容性检查；不执行训练业务。

## 文档索引

- `packages/ai4e-spec/README.md`：包职责、允许/禁止依赖和 已交付最小协议及规划边界。
- `.context/modules/ai4e-spec.md`：本模块的目录与文档检索入口。
- `.cursor/rules/ai4e-algorithm-architecture.mdc`：本包的能力分层、高内聚低耦合与代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解稳定契约层的设计理由时按需读取。

## 首个验收

组外组件不导入 core，即可通过 spec 契约测试。新增目录或文档时必须同步本索引。

## 本次实施定位（2026-09-08）

- `components/model.py`：最小 ModelFactory 与 ModelRequirements，无数组依赖。
- `docs/PRD/ai4e-spec/components/PRD.md`：组件协议说明。

## 多域模型变更

`components/model.py`：必需与可选输入名称、可选最大批次要求；域布局保留在贡献组件。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## Task 接入

- `artifacts/run.py`：RunContext 标准库契约，传递项目、任务、正式版本、运行身份和资产来源。
- `.context/mvp/task-acceptance.md`：相关验收入口。

## 双模型组件入口

- `components/dataset.py`：数据视图和内容摘要协议。
- `components/model.py`：模型组件及构造器描述回调。

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。
