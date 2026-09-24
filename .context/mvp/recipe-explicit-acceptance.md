# Recipe 显式流程与扩展验收

日期：2026-09-11。状态：本记录圈定范围完成。默认模板、五例、两个扩展目录、旧脚本兼容、实际 wheel 安装和相关回归均取得证据；规模与未承诺边界见末节。

## 范围与业务约定

默认模板显示四阶段的实际业务步骤和参数交接；五例明确使用物理准备、训练和完整预测的步骤，NASA 读取为独立来源差异。Python 决定顺序，YAML 提供参数。旧 workflow 保留为兼容包装，新模板不使用 components.workflow。历史 NPY 参考流程继续由原复制脚本和兼容入口执行，和当前物理 PT 五例分开核验。

速度模长示例 require_features=true，默认 query=false：新增输入特征必须在预测实体上可用，任意网格查询须另行提供相应特征，不能静默当成零。本例验证数据交接，不作为未知速度预测的精度基线。

两个可复制示例为 `examples/recipe_extensions/field_mapping/` 与 `sampling/`。字段例通过普通 NumPy 函数生成速度模长，继承 point 实体顺序、声明单位来源和物理状态，经过选择、同步筛选、PT/Zarr 保存、读回、统计、归一化进入模型特征。采样例改变实际训练迭代中的几何选择；准备只冻结方式，不缓存训练样本。变换、目标、指标、预测分别使用具名接口。

普通函数与 target/parameters 共用解析；可持久化采样必须可以从模块重建，闭包拒绝。有状态 callable 对象使用 dataclass 声明构造参数，或以 target/parameters 工厂返回运行对象。能力源码进入 run/sources，来源声明分别参与准备、训练和推理契约；不使用全部脚本快照摘要阻断所有阶段。

## 证据位置

所有实跑与缓存位于 `/Users/zonghui/work/project_simulation/dojo_train/recipe-explicit-20260911/`。

- `baseline/`：修改前应用和默认模板源码；基线首组 19 项通过。
- `tests/fixtures/recipe_before_explicit/`：版本固定的历史脚本、物理训练及后处理源码；README 记录提交。仅供验收，不是发布模板。对照共用未修改的模型算子，不宣称独立算法复现。
- `final-regression.xml`：配置、惰性原始处理、日志、准备、物化、训练恢复、锚点后处理、网格、来源快照与比较共 122 项通过，151.51 秒。
- `platform-1.xml`：task 配置/资产/契约/recipe、Web 原始处理/交接/绑定与整合流程共 31 项通过，28.66 秒。
- `installation-final.xml`：最终源码 wheel 新环境安装、task 创建/fork/run，以及仓库外字段扩展完整训练通过，14.61 秒。第三方依赖复用已有环境，四个产品包强制从新 wheel 加载并检查导入位置。
- `equivalence-verified.xml`：五例与旧物理训练/后处理源码、两个扩展示例（路径与直接函数采样）、四类能力替换、task fork 与比较等 14 项通过，72.74 秒。
- 五例均在 CPU 上比较两轮所有模型权重、实际批次输入摘要、完整物理预测张量与指标，容差 rtol=0、atol=0；从旧源码的第 1 轮检查点恢复后与连续第 2 轮所有权重逐值一致。三个汽车例 train=1/test=1、原始小网格；两个 NASA 例 train=4/validation=1/test=2、每样本32点。AB-UPT dim=24/一层几何/每域一层解码，Transolver hidden=16/layers=2/heads=4/slices=4；各例字段、原模型算子、学习目标和调度方式保留。
- `remaining-contracts.xml`：步骤删除、跨实体映射、错误状态以及 Web 模板门禁/标准编辑保留共 5 项通过，5.89 秒。
- `documents-final.xml`：计划完整源码、规则范围、AGENTS、索引、历史覆盖导航和 task 文档共 7 项通过，0.28 秒。
- `closure.xml`：最终 Web 配置兼容、计划与 Recipe 文档复核共 8 项通过，1.30 秒。
- 原 Transolver 两轮/恢复数值对照在 `final-docs-reference.xml` 通过；其中旧“所有脚本字节一致”文档断言已按批准方案改为共享配置/交接与可见局部步骤，并在 `documents-final.xml` 通过。历史 NPY 复制、跨目录、独立阶段和覆盖门禁在 `equivalence-2.xml` 的 test_aero_cfd_examples 六项全部通过。
- 本次修改的 82 个 Python 文件通过 ruff check 和 format --check；git diff --check 通过。失败和返工记录保留于早期 XML 与 error.log，不覆盖历史证据。

## 圈定用例与完成门槛

- A1/A2：test_dataset_recipe、test_recipe_three_stage、test_recipe_logging；步骤登记无网格读盘，流水线/独立执行、检查延后、事务失败和日志。
- B1/B2/C2：test_recipe_extensions；PT/Zarr 逐值速度模长，训练统计、冻结变换、新模型特征及同权重前向影响；两轮训练、独立 post、快照保留及来源变化拒绝。
- B3：同文件中实际轮次采样、直接函数重建、变换正反、零损失目标、定制指标、恒定归一化预测变为物理值；错误参数和返回形状拒绝。
- C1：test_recipe_configuration、test_run_config_snapshot、test_train_code_snapshot、test_comparison_protocol；旧键及双键、跨目录、覆盖、来源与按用途比较。
- D1：test_recipe_explicit_equivalence 五例改动前后输入、权重、预测、旧中途检查点恢复；test_transolver_reference 对原仓库两轮/恢复；历史脚本 test_aero_cfd_examples；准备/物化/训练和 post 相关回归。
- D2：test_task_installation、task/Web 圈定回归；无新增页面、无前端功能范围扩张。
- E1/E2：test_recipe_documents；专项规则、AGENTS 阅读入口、唯一架构与 PRD、索引和计划中的完整源码一致。

## 核实并修复的恢复问题

NASA Transolver 的历史独立 DataLoader 随机生成器未包含在全局 RNG 检查点内，直接恢复会重置第二轮洗牌。新物理训练依据原种子和已完成轮次重放同一 DataLoader 索引消耗，不读取数据、不重做训练；模型、优化器、调度器和全局随机状态仍在原 fit 生命周期恢复。正常连续训练与旧源码逐值一致，此恢复修复经过五例旧检查点测试，不迁写旧文件。

## 迁移与边界

默认模板为汽车锚点研究流程，五例为物理数据跨模型流程，分别提供显式步骤。研究者切换到另一种数据/模型输入契约时复制对应 example；历史带 components.workflow 的脚本仍调用兼容入口，当前模板不再以该键隐藏步骤切换。原公开旧键拒绝政策不变，历史产物保持原样。

本轮数值验收使用合成但完整 schema 的 CPU 小网格/HDF5 和缩小网络，正式模型组件及原训练算法不变；不以小规模结果代替五例正式网络的科研精度，不重跑 50 轮。历史 MPS/CUDA 数值边界沿用其原验收记录，本轮不新增硬件等价声明。Web 验收为已有 API 的配置与交接回归，未新增通用能力编辑页面。

并行工作区中的 PI/PiBSNet、优化器新增通用功能、依赖与其文档是另一项任务的改动，本记录不将其计作 Recipe 交付。

## 2026-09-23 失败矩阵恢复

本轮不改冻结基线与数值容差：通用训练在全局随机流下补回历史 DataLoader 建立迭代器时的 base-seed 消耗，AB-UPT 两例重新达到权重逐值一致；Transolver 增加平面字段准备适配，不再误要求 AB-UPT `data_specs`。训练协议继续记录逐批输入摘要，旧第一轮检查点按原总轮次合同恢复。历史 post 只读桥接现行 version=2 准备；SafeDiffCon 安装案例按所选阶段延迟导入训练依赖。最终证据以本轮重新生成的圈定测试与正式入口冒烟为准，不改写上方 2026-09-11 历史 XML。
