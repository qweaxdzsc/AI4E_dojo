# PRD 书写规范

本目录是仓库长期功能文档的唯一维护位置，记录已开发能力、行为变化、设计原因、使用约定和迁移影响。写或改 PRD 时先读本文，再读 [`.cursor/rules/prd-writing.mdc`](../../.cursor/rules/prd-writing.mdc)。改功能时必须按根目录 `AGENTS.md` 的修改与验收纪律同步受影响的模块 PRD。

代码路径、测试路径、框架命令不写进 PRD，写在 `.context`。目录与模块名对齐 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 的 package 一级分组，不得另起一套产品切分。

## 目录约定

先按一级 package 分文件夹，再按该包内的一级模块各写一份 `PRD.md`：

```text
docs/PRD/
  README.md
  {包名}/
    {模块名}/PRD.md
```

普通模板集合使用 `recipes/{案例}/PRD.md`；其余包名与 `packages/` 下正式包一致，例如 `ai4e-core`、`ai4e-spec`、`recipes`。模块名与该包源码一级目录一致，例如 core 为 `base`、`abilities`、`applications`、`run`、`tools`。

- 禁止在 `docs/PRD/` 根下再放扁平切片或按能力层编号的目录（如 `shapenet_car_raw_read.md`、`01_数据源下载与读取/`）。
- 禁止把一次切片、一个函数或一对操作升成模块目录。读取、下载属于 `abilities` 里「数据」章节的功能点，不是独立 PRD，也不是独立功能域。
- 一篇模块 PRD 可按该模块的下一级稳定分组分章节（一、二、三…）。`abilities` 按 `data`、`transform`、`geometry` 等分章；未交付的分组不写空章。
- 未交付的包或模块只在下方对照表标「待编写」，不建空目录。

## 必选章节

每份模块 `PRD.md` 必须有 `## 目录`，用嵌套锚点指向各章节。每个章节必须含下列六节，不得删节。无状态机时，1.3 / 1.4 写「本章无业务状态」并说明原因，不得省略标题。

```markdown
## 目录

- [一、{章节 A}](#一章节-a)
  - [1.1 背景与定位](#11-背景与定位)
  - [1.2 核心业务操作流程图](#12-核心业务操作流程图)
  - [1.3 业务状态机](#13-业务状态机)
  - [1.4 状态值说明](#14-状态值说明)
  - [1.5 功能点清单](#15-功能点清单)
  - [1.6 功能点详解](#16-功能点详解)
- [二、{章节 B}](#二章节-b)
  - [2.1 背景与定位](#21-背景与定位)
  …
```

| 章节 | 写什么 |
| --- | --- |
| 1.1 背景与定位 | 给谁、解决什么、做成后看见什么；边界（不做什么）写在这里 |
| 1.2 核心业务操作流程图 | mermaid `flowchart`，覆盖本章全部功能点，节点用人话 |
| 1.3 业务状态机 | mermaid `stateDiagram`；无状态则写明原因 |
| 1.4 状态值说明 | 表：中文含义 / 标识 / 业务说明 |
| 1.5 功能点清单 | 本章功能点与子功能，用人话；用独立数字编号，不要把功能点再拆成「一、二」 |
| 1.6 功能点详解 | 每个功能点带与清单相同的编号，再分点写作用，见下一节 |

保持六节结构，不另增数据模型、接口清单、验收标准等顶层节。必要的用户可见配置及结果约定写在 1.6 对应功能点内；原因与取舍写在 1.1 或该功能点内。验收由 `AGENTS.md` 圈相关测试；路径由 `.context` 索引。

禁止再用旧顶层：用户结果、做什么、不做什么、功能点、上下游、验收。

## 功能点编号

1.5 与 1.6 共用一套**功能点编号**，两边必须对得上。这套编号只在清单、详解里另起，不延续章节标题的 1.1–1.6。

- 主功能点：`1.` `2.` `3.`……
- 子功能：挂在所属主功能下，写成 `1.1` `1.2`、`2.1`……
- 1.5 用编号列表，不用无序号的点。
- 1.6 每个功能点、子功能的标题前必须带同一编号，禁止只写 `#### 名称` 或用点当功能点序号。
- 作用说明仍可用短句分点，那些句子不是功能点，不必再占一个功能号。
- 第二章的清单、详解从 `1.` 重新起号，不要接着第一章的 4、5 往下编。

## 功能点详解

1.5 列出功能点；1.6 必须按同一编号切开，每条围绕**作用与使用约定**（给谁、挡住什么、做成后看见什么）说明，并写清必要的设计原因、输入输出含义、限制、失败行为和迁移影响。配置示例、共享关系及格式恢复约定归入对应功能点，不在文末散落补丁式说明。不写内部算法步骤或界面实现。

```markdown
### 1.5 功能点清单

1. 原始文件读取与格式适配
    1.1 按格式把一个文件读进内存
    1.2 文件不存在时拒绝读取
2. 数据源下载与解压
    2.1 从 HuggingFace 拉整库或单文件

### 1.6 功能点详解

#### 1. 原始文件读取与格式适配

- 磁盘上已有受支持的 VTK 家族文件或 NPY 时，读进内存并得到统一 VTK 对象。
- 文件不在或格式不认识时，在打开适配器之前失败，避免半成品。

##### 1.1 按格式把一个文件读进内存

- 读取知道格式后，得到可继续用的内存对象。

##### 1.2 文件不存在时拒绝读取

- 目标不是已有文件时直接拒绝，不进入适配。

#### 2. 数据源下载与解压

- 给定来源和本地目标目录后，目标目录出现解开后的文件，供读取使用。

##### 2.1 从 HuggingFace 拉整库或单文件

- 按仓库标识取回整库或其中一个文件，落到指定本地目录。
```

反例：清单用无序号的点；详解标题没有编号，两边对不上；把读取、下载写成「一、二」两个功能域并各写一套 1.1–1.6；或把 1.6 写成一段散文 / 「实现逻辑 / UI 展示」。

## 模块对照

整合平台实施中（2026-09-10）：[Dojo WEB 平台产品设计](ai4e-web/src/PRD.md)，状态实施中。完整产品正文按 Web 一级目录 src 归档，包含项目管理和任务工作台两章；不表示本轮全部功能已经通过验收。后续功能实现直接更新此正文，避免另建平行产品说明。技术架构见唯一架构文档第 19 节。

| 包 | 模块 PRD | 状态 |
| --- | --- | --- |
| ai4e-core | [abilities](ai4e-core/abilities/PRD.md) | 已交付：数据章、几何章、准备与训练能力，以及推理重建、锚点点云与完整网格回贴 |
| ai4e-core | [applications](ai4e-core/applications/PRD.md) | 已交付：外流 pre、train 与 post（锚点评估保存、可选点云、完整网格回贴） |
| ai4e-core | [run](ai4e-core/run/PRD.md) | 已交付：开车、点号覆盖、逐项执行、失败汇总与唯一写入；摘要可抄训练探测字段 |
| ai4e-core | [base](ai4e-core/base/PRD.md)、tools | base 已交付配置与事件；tools 待编写 |
| ai4e-spec | [components](ai4e-spec/components/PRD.md)、[artifacts](ai4e-spec/artifacts/PRD.md)、data、check | components 与 artifacts 已有契约；data 检查描述见下方导航，check 待编写 |
| recipes | [aero_cfd](recipes/aero_cfd/PRD.md) | 已交付：字段映射、几何启用、已有数据根、官方分片、前处理与训练准备入口 |
| ai4e-task / viz / server / web | 见下方模块导航 | 平台扩展实施中，按专项验收限定交付 |

范本：[`ai4e-core/abilities/PRD.md`](ai4e-core/abilities/PRD.md)。


## 长期维护约定

- 每次功能改动直接更新所属模块 PRD 的现行说明，说明行为变化及原因；不要把 PRD 仅当简短功能清单，也不要用逐次追加的聊天记录代替完整正文。
- 迁移影响写在对应功能点下，区分现已交付、明确不做和未来计划。旧行为仅在解释迁移时保留，不与现行行为混写。
- 不新增 data_onboarding 一类并行功能正文；旧入口可保留跳转。README 与 .context 负责导航，函数签名、代码和测试路径由 .context 与源码说明承载。
- 架构文档保留全局分层与依赖边界；模块功能细节及其设计原因以 PRD 为准，避免复制同一份功能正文。

- ai4e-contrib 的 application：[共享数据集 PRD](ai4e-contrib/application/PRD.md)。

新增模块导航： [贡献模型](ai4e-contrib/ability/PRD.md)、[最小模型协议](ai4e-spec/components/PRD.md)。正式模型按专项验收记录限定已验证范围。

## Task 本地模块

- [ai4e-task/cli](ai4e-task/cli/PRD.md)：本地切片现行行为。
- [ai4e-task/projects](ai4e-task/projects/PRD.md)：本地切片现行行为。
- [ai4e-task/tasks](ai4e-task/tasks/PRD.md)：本地切片现行行为。
- [ai4e-task/versions](ai4e-task/versions/PRD.md)：本地切片现行行为。
- [ai4e-task/templates](ai4e-task/templates/PRD.md)：本地切片现行行为。
- [ai4e-task/storage](ai4e-task/storage/PRD.md)：本地切片现行行为。
- [运行来源契约](ai4e-spec/artifacts/PRD.md)：轻量跨包身份与来源。

双模型功能更新归入上述 components、core、contrib 与 aero_cfd 模块正文；NASA 正式规模数值对标通过；旧公开 YAML 兼容政策仍待确认。

- [ai4e-viz/render](ai4e-viz/render/PRD.md)：表面、切面及曲线静态表达。
- [ai4e-viz/compose](ai4e-viz/compose/PRD.md)：独立域比较的离线报告。

## 本机平台文档入口

- `ai4e-server/modules/PRD.md`：研究管理代理、处理配置、文件与报告。
- `ai4e-spec/data/PRD.md`：跨包文件检查描述。
- `ai4e-viz/inspect/PRD.md`、`ai4e-viz/preview/PRD.md`、`ai4e-viz/runtime/PRD.md`：真实检查、预览与独立请求执行。
