# ai4e-spec 模块索引
## 当前职责与本轮变更

标准库交接类型；components 为局部消费者约定，data 为检查描述，artifacts 为持久化与跨进程格式。

- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


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

历史数值对标及其范围见 `.context/mvp/transolver3-acceptance.md`；当前公开入口和兼容边界见 `.context/mvp/architecture-alignment-acceptance.md`，不迁移历史任务。

## 物理数据跨模型实验

components/dataset.py 与 model.py：物理数据视图及模型准备/预测协议，无数值库依赖。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `artifacts/physical.py`：物理预测与图形引用 TypedDict，无数值库依赖。

## 本机平台接入（2026-09-10）

- `packages/ai4e-spec/data/inspection.py`：稳定检查或管理配置公开操作。
- `packages/ai4e-spec/artifacts/preview.py`：稳定检查或管理配置公开操作。
- `.context/mvp/web-rawprep-acceptance.md`：平台接入验收记录。

## 平台显示与辅助操作契约

- `packages/ai4e-spec/artifacts/platform.py`：AssetRef、字段、数据集、提取成员、阶段配置、操作状态、二进制显示资产和可序列化场景。只依赖标准库。
- `packages/ai4e-web/scripts/generate-platform-contracts.py`：从该契约生成浏览器类型。
- `tests/integration/test_web_integrated_pipeline.py`：跨语言生成一致性及真实服务到显示数组交接。
- 产品语义：`docs/PRD/ai4e-spec/artifacts/PRD.md`。

## 独立可视化任务交接

- `packages/ai4e-spec/artifacts/visualization.py`：存储上下文、资产与会话公开交接类型。

## 声明驱动原始处理

artifacts/platform.py 增加 RawprepDescriptor 与检查范围、缺项及原生选择；同步生成 TypeScript 描述。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

## 独立推理交接

- `artifacts/inference.py`：`InferenceCheckpointRef` 固定权重身份与修订；`InferenceRequest` 声明配置修订、多检查点、有序样本、分片、设备、输出选择和幂等身份。`apply_export_aliases` 是旧键/新键的唯一解释：未拆新键时旧 `export_vtk` 同时开关点云和网格化，拆开后只表示网格化；值为空的新键视为未写。样本目录形状含 `vtk_exports`。`InferenceResultRef` 固定任务/批次/运行/权重修订/样本。
- `artifacts/__init__.py`：公开上述标准库类型。配置字节、模型、数组和任意机器路径不进入这些契约；结果成员仍经固定资产引用读取。
- `docs/PRD/ai4e-spec/artifacts/PRD.md` 第三章：来源与选择的长期使用约定；`.context/mvp/inference-acceptance.md`：圈定测试和当前未验收边界。

## 推理工作台选择与统计

`artifacts/inference.py`：跨分片请求、字段/指标选择与固定结果身份，拒绝新旧名单同时提交。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

## Task 通用化交接（实施中）

- `artifacts/task_operations.py`：JSON 管理描述、执行计划验证、类型敏感的身份/标签等值。只依赖标准库。

公开接口变化、圈定测试与未验范围见 [本轮验收](../mvp/task-generalization-acceptance.md)，功能正文更新既有对应 PRD。
