# 面向 Agent 的 Dojo 分层入口

这是一份定位和路由说明，不是第二份架构正文。全局设计、依赖方向和数据流以[唯一架构正文](../../docs/AI4E_Dojo_ARCHITECTURE%20%281%29.md)为准；本页只告诉 Agent 修改前先找哪一层、哪些边界不能跨越。

## 1. 先判断问题属于哪一层

| 你要解决的问题 | 首先进入 | 该层的交付 |
| --- | --- | --- |
| 算法、数据处理、训练、推理、评价、后处理 | `ai4e-core` 的 `abilities` / `applications` | 原子能力或领域装配；算法不认识项目数据库和页面 |
| 模型、数据集、方程、物理约束和专属参数 | `ai4e-contrib` 的 `ability` / `application` | 科学实现、输入输出连接、描述和 provider；不改 Task 生命周期 |
| 流程顺序、研究实验、可复制案例 | `recipes/` 或 `examples/` | Python 流程正文、YAML 参数；不把流程复制成平台内部状态机 |
| 项目、任务、版本、运行、资产、输入绑定、恢复 | `ai4e-task` | 管理事实、固定引用、收据和状态；不识别模型或科学语义 |
| 平台检查、保存、提交、受控路径、能力描述 | `ai4e-server` | 业务用例和适配；调用 Task/provider，不实现数值计算 |
| 页面、工作台、草稿和用户导航 | `ai4e-web` | 稳定 API 消费和用户任务交互；不导入 Python 包或训练 |
| 预览、结构图、三维会话和导出 | `ai4e-viz` | 独立进程消费固定资产；不读 Trainer 私有状态 |
| 跨进程、持久化、资产和指标的最小记录 | `ai4e-spec` | 共享名词和边界形状；不把所有领域压成一个科学协议 |

## 2. 包之间如何沟通

```text
web → server API → task 公共门面
                       ↓
               recipe / application provider
                       ↓
                  core + contrib
                       ↓
              run / writer / fixed result
                       ↓
               task receipt → server → web/viz
```

- `recipe` 负责把领域步骤接起来；普通返回值可以直接交接，只有跨进程、持久化或展示才使用稳定记录。
- `Task` 只接收任务声明和 provider 结果。它保存配置修订、运行状态、资产引用、检查点引用和失败原因，不读取模型对象或模型私有配置。
- `Server` 通过 Task 的公开门面提交和查询，通过 provider 获得检查、评价、导出和页面描述；`capabilities` 中的官方模型目录只是平台选项来源。
- `Web` 只依赖 Server API 和稳定 Artifact schema。页面上显示的模型参数是 provider 返回的描述，不是 Web 自己解释的模型逻辑。
- `Vis` 只消费固定资产、来源修订和会话引用。它不能回到训练流程重新计算模型。

## 3. 跨领域可以统一的管理语言

不同领域可以共同记录：

`输入身份 → 配置/版本修订 → 运行 → 资产/检查点 → 固定结果 → 指标 → 失败/取消 → 恢复引用`

这套语言用于 Task 的记录、Server 的状态和 Web 的比较。它不要求 CFD、PDE、控制或时空预测共享同一字段名、张量布局、损失函数或网络协议。科学对象由领域 application 定义，Task 只保存不透明引用和通用状态。

## 4. 修改时的边界检查

1. 要是算法逻辑变了，先在 core/contrib/application 找拥有科学语义的地方，再由 recipe 连接；不要把算法分支加进 Task。
2. 要是任务状态、资产、版本或恢复变了，只改 Task 的公共管理门面；输入内容如何解释由 provider 负责。
3. 要是页面要新增选项，先确认 Server 是否已有稳定描述和操作，再改 Web；不要让 Web 读取模型内部配置。
4. 要是跨层需要新数据，先问它是否真的跨进程/持久化/展示；普通中间值留在 recipe/application 内，不要为了统一而 Artifact 化。
5. 要是需要新的共享接口，先证明至少两个领域拥有相同语义，再把最小交接放入 spec；单一模型的需求留在 application。

## 5. 当前已具备与待补

已具备：包依赖方向、core 的稳定 run 门面、recipe 的 Python 主流程、Task 的项目/任务/运行/资产管理、`components.application` 操作入口、Server 的受控 API、Web 的稳定传输类型，以及 Vis 的独立进程交接。

仍需补齐的架构工作：

- 为 provider 明确定义“描述、检查、评价、导出、兼容性”的最小返回边界，让 Server/Web 不必猜模型字段。
- 将 Task 推理批次中目前读取 `contract.component/model` 的同批次兼容判断下沉到 provider，Task 改为只消费不透明的执行身份和结果。这是现有实现的边界接缝，不应继续扩展为模型分支。
- 为跨领域比较固定管理维度（输入、版本、运行、资产、结果、指标、失败、恢复）的最小索引，缺少科学比较条件时返回不可比，不填空值伪装相同。
- 为 Agent 在 `.context/modules/` 中补齐“调用方—被调用方—交接—测试—PRD”索引；本页只做入口，不复制模块正文。

## 6. 阅读顺序

先读根 [`AGENTS.md`](../../AGENTS.md)，再读本页定位；需要架构决策时进入[唯一架构正文](../../docs/AI4E_Dojo_ARCHITECTURE%20%281%29.md)，需要当前文件和测试位置时进入[仓库索引](../index.md)与对应[模块索引](../modules/)。产品行为读 `docs/PRD/`，具体验收只读相关 `.context/mvp/` 记录，不把验收数字当成架构定义。

