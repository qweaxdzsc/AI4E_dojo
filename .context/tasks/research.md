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
