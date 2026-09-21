# 按研究任务定位 Dojo

先读根 [AGENTS](../../AGENTS.md) 的当前边界，再选下面一项。根目录历史进度和全仓源码不是每次必读；跨模块时进入[模块总索引](../index.md)。本页只做导航，行为正文在 PRD。

如果问题涉及包职责、Task/Server/Web 分工、跨领域交接或 Agent 路由，先读[面向 Agent 的分层架构入口](architecture.md)，再进入唯一架构正文；不要从某个模型或局部测试反推全局架构。

## 训练已有模型

- 必读：[模板总入口](../../recipes/README.md)，所选模板 README、config.yaml 和 train.py。
- 最少修改：配置中的阶段输入、运行/数据目录、设备和训练预算；默认入口不要求自行组装原子能力。
- 按需：[运行记录](../../docs/PRD/ai4e-core/run/PRD.md)、[训练能力](../../docs/PRD/ai4e-core/abilities/PRD.md)、[core 索引](../modules/ai4e-core.md)。恢复问题再读 training/checkpoint.py 和对应领域合同。
- 验证：[轮次行为](../../tests/integration/test_train_loop.py)、[边界恢复](../../tests/integration/test_train_boundary_alignment.py)、[WDNO 安装复制](../../tests/integration/test_wdno_recipe.py)。选择当前训练路线，不为单次调参跑全部模型。
- 交接：已准备数据进入训练，检查点与报告由 writer 写入；输入冲突或恢复合同变化明确失败。

## 组装 recipe

- 必读：[编写规则](../../.cursor/rules/ai4e-recipe-authoring.mdc)、所选模板 pipeline.py 与 configuration.py。
- 最少修改：复制完整模板，在 Python 中连接步骤；YAML 只选参数和能力，`pipeline.stages` 只选择执行范围。
- 示例：[自由连接](../../examples/recipe_extensions/free_wiring/README.md)、[WDNO 插入审计](../../examples/recipe_extensions/wdno/README.md)。扩展覆盖集须覆盖到完整模板，不单独运行残缺目录。
- 按需：[模板索引](../modules/recipes.md)、[公共约定验收](../mvp/recipe-task-conventions-acceptance.md)。普通返回值直接交接，跨阶段外部路径用 `inputs.<stage>.<name>`，运行记录与数据目录分开。
- 验证：[公共约定](../../tests/integration/test_recipe_conventions.py)、[可复制扩展](../../tests/integration/test_recipe_extensions.py)。若选用 Task，再做直接/Task 同一正文对照。

## 接入新模型

- 必读：[模型集成技能](../../.agents/skills/dojo-integrate-model/SKILL.md)、[接入目标与原则](../../docs/model-integration-goals.md)，以及原仓库、论文与数据证据。
- 修改位置：贡献能力持有模型/专属算法，领域应用绑定数据与合同，recipe 表达步骤；按[贡献索引](../modules/ai4e-contrib.md)定位最接近案例。
- 按需：[唯一架构](../../docs/AI4E_Dojo_ARCHITECTURE%20%281%29.md)，仅在做架构决策时读取。
- 验证：按集成技能沿已有证据续接原版对照与安装验收，不把某模型的单步测试当成新模型的验收。

## 研究原模型变体

- 必读：[扩展示例入口](../../examples/recipe_extensions/README.md)、当前模型的构造/目标函数及本次选中的扩展说明。
- 换整网或损失：[WDNO 变体](../../examples/recipe_extensions/wdno/variants.py)；保持模型自己的输入约定，不要求任意网络都能无适配接入。
- 换内部部件：[AB-UPT 前馈激活](../../examples/recipe_extensions/model_block/README.md)；只改本地组件，验证参数、缓存与恢复。
- 换优化器/调度/更新：[局部训练函数](../../examples/recipe_extensions/wdno/variant_training.py)；只选择变化部分，默认保存、数据流和恢复继续复用。
- 加研究步骤/输出：[WDNO 审计](../../examples/recipe_extensions/wdno/audit.py)和同目录 pipeline.py，结果通过固定数组读回，注明身份、单位和轴。
- 验证：[策略与部件实跑](../../tests/integration/test_training_strategy_extensions.py)、[共享执行](../../tests/integration/test_training_execution.py)。至少前向、短训、连续/恢复对照、推理与固定输出读回；不复制框架循环。

## 需要更深定位时

源码索引生成器 [architecture_inventory](../../tools/verification/architecture_inventory.py) 输出文件、声明签名和行号，供先定位再读；它不能证明组件兼容或运行成功。当前共享执行的证据与未验范围见[专项验收](../mvp/training-execution-acceptance.md)。

## 可组合 Dojo 案例与 Agent 路由

Dojo 研究入口首先按能力和接入深度分流：单工具、已有研究代码、完整领域流程。九类能力教程位于 `docs/agent-help/capabilities/`，元数据是 skill、GUIDE、帮助首页菜单的唯一来源；生成器 `tools/docs/build_agent_help.py --write/--check` 同步导航及索引。不要要求局部工具用户先复制完整案例。

支持 Agent Skills 时使用 `.agents/skills/dojo-research/SKILL.md`，否则从 `DOJO_AGENT_GUIDE.md` 进入相同帮助中心。直接读能力教程，再用 `describe_help_symbol` 核对现行签名、源码和稳定性；搜索用于补充定位。已有 PyTorch 模型优先阅读 training 的真实短训/恢复例子，已有 NumPy 预测优先阅读 evaluation 的 FP64 复算例子。具体不兼容时允许局部适配或自定义，不把搜索无结果视为能力缺失。

完整流程仍选 standalone、物化 extension、阅读阶段正文并 direct-core 验证；按需交给同目录 Task。单个工具只需真实输入输出证据，训练与恢复验证状态，post 固定预测读回。工程接线、学习效果和论文精度分别陈述。

案例资源清单为 `examples/case-manifest.json`，只允许 `standalone` 与 `extension` 两种类型。recipe 是仓库内维护源，example 是仓库外复制交付物；清单声明的公共阶段脚本逐文件核对，配置和研究预算可以不同。Neumann smoke 固定 train 2、test 1、nx=7、nt=7、CPU、两轮以内，只验证公开入口、参数生效、恢复和结果交接。

Agent Help Center 的源文件位于 `docs/agent-help/`，机器索引由 `tools/docs/build_agent_help.py` 从 AST、Markdown 元数据和案例清单生成。`uv run --no-sync python tools/docs/build_agent_help.py --check` 只检查签名、源码位置、案例和索引漂移；逐 API 用途、研究工作流与证据边界仍由人工正文负责。当前覆盖与安装证据见 `../mvp/agent-help-acceptance.md`。

PCNO 地热：完整案例 `examples/geothermal/pcno/`，扩展 `examples/recipe_extensions/pcno/`；能力优先在core，当前核验见 `../mvp/pcno-acceptance.md`，长期功能见 `docs/PRD/recipes/pcno/PRD.md`。用户已改为先集成后短训，不等待已停止的250轮任务。
