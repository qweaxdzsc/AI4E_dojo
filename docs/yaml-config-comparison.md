# 五个 AI4S 框架的运行 YAML 与 Dojo 配置讨论

日期：2026-09-10  
状态：源码梳理与讨论材料，未形成实施决策。

本文整理 Noether、PaddleScience、MindScience、PhysicsNeMo、Anemoi 的具体运行案例，并对照 Dojo 当前 aero_cfd 配置。依据为本地源码静态检查；本轮没有执行这些框架的训练，没有修改配置或计算代码。案例写法不代表整个框架的统一规范，当前文件也未锁定为各框架的版本基准。

## 1. 主要判断

Dojo 的五段业务结构可以保留。更值得借鉴的是“案例默认声明、实验覆盖、最终生效配置记录”之间的配合，而不是其他仓库的字段名称。

不同框架的 YAML 分组并不一致。使用 Hydra 也不意味着训练流程全部由 YAML 组织：有的配置选择组件，有的只是给 Python 装配脚本提供参数。

评价配置设计应同时看四件事：研究者需要填写什么、默认值从哪里来、参数如何进入计算、运行后能否还原实际实验条件。文件短或分组少，不能单独说明设计更好。

## 2. Noether：组件配置与实验配置组合

### 实际组织

ShapeNet-Car 训练配置分成三个层次：

- 入口配置声明数据根目录，并通过 Hydra `defaults` 组合数据规格、归一化器、模型、训练器、数据集、回调、数据处理管线和优化器。
- 组件配置定义具体参数，通过 `kind` 指定完整类路径。
- 实验配置选择 AB-UPT 等组件，并覆盖采样预算、模型参数和精度。

`${data_specs}` 等插值让多个组件引用同一份声明。实际 YAML 入口经过 Hydra 合并与解析，再由 `HydraRunner` 构造 `ConfigSchema` 校验；运行保存 `hp_resolved.yaml`。

这里的 `pipeline` 是模型数据处理管线，不能直接等同于 Dojo 的 rawprep → trainprep → train → post。仓库还有 Python preset 入口，不能把它与 Hydra YAML 入口的默认参数混用。

### 对 Dojo 的启发

适合借鉴的是：标准案例提供稳定默认值，研究者主要表达实验差异，同时记录完整生效参数。不一定要立即把 Dojo 拆成很多文件；多文件组合也增加了追踪参数来源的成本。

源码依据：

- [训练入口配置](../../noether/recipes/aero_cfd/configs/train_shapenet.yaml)
- [AB-UPT 实验覆盖](../../noether/recipes/aero_cfd/configs/experiment/shapenet/ab_upt.yaml)
- [AB-UPT 模型配置](../../noether/recipes/aero_cfd/configs/model/ab_upt.yaml)
- [数据处理管线配置](../../noether/recipes/aero_cfd/configs/pipeline/shapenet_pipeline.yaml)
- [YAML 启动入口](../../noether/src/noether/training/cli/main_train.py)
- [配置校验与运行记录](../../noether/src/noether/training/runners/hydra_runner.py)

## 3. PaddleScience：公共默认配置与案例脚本装配

### 实际组织

Transolver ShapeNet-Car 案例主要分为 `DATA / MODEL / TRAIN / EVAL / INFER`，另有 `mode、seed、output_dir` 等公共设置。

Hydra `defaults` 引入训练、评估、推理的公共默认配置。案例 Python 入口根据 `mode` 选择 train、eval、export 或 infer；脚本用 `cfg.MODEL` 构建模型，另外装配数据、损失和优化器。

该配置明确设置 `hydra.job.chdir: false`，并用时间插值组织运行目录。不同分支可以有不同必填输入，例如独立评估需要已有权重。

### 对 Dojo 的启发

用户配置可以按实验用途分组，计算库只接收其需要的参数。案例组织流程不要求库反向认识案例配置树。

但把训练和部署推理全部放进同一个 YAML，会暴露很多当前任务用不到的选项；这个案例也不是一次自动串起全部阶段的流水线。

源码依据：

- [ShapeNet-Car 配置](../../PaddleScience/examples/transolver/conf/shapenet_car.yaml)
- [案例装配与模式选择](../../PaddleScience/examples/transolver/main.py)

## 4. MindScience：直接读取 YAML 的研究案例

### 实际组织

MindFlow 的 Navier–Stokes FNO2D 案例使用 `model / data / optimizer / summary` 四组。训练脚本读取字典，分别构建数据集、模型和优化器。

设备通过命令行传入。精度选择、损失函数等部分实验行为写在 Python 中。该案例调用的加载器使用 `yaml.safe_load`，路径处理以当前工作目录为基准。

### 对 Dojo 的启发

单个案例的 YAML＋Python 可以非常直接，但 YAML 简短不等于实验条件完整。复制到其他目录运行时，需要核对工作目录、脚本默认值和命令行参数。

Dojo 现有按配置文件位置解析路径的约定应保持清晰，不应因为参考案例使用工作目录就改变。上述结论只适用于本次检查的 MindFlow 案例。

源码依据：

- [FNO2D 配置](../../mindscience/MindFlow/applications/data_driven/navier_stokes/fno2d/configs/fno2d.yaml)
- [训练入口](../../mindscience/MindFlow/applications/data_driven/navier_stokes/fno2d/train.py)
- [YAML 加载器](../../mindscience/mindscience/utils/load_config.py)

## 5. PhysicsNeMo：案例决定布局，Hydra 负责加载

### 实际组织

Darcy Transolver 案例分为 `model / data / normaliser / scheduler / training / validation`。

Python 入口使用 Hydra 加载配置，再显式把字段传给模型、数据管线、优化器和调度器。检查点目录等部分设置仍写在脚本中，不能只凭 YAML 判断全部实验条件。

该案例在 YAML 中直接给出归一化均值和标准差。源码能确认它们是预先提供的常量，但本轮没有核验其统计来源；不能据此推导 Dojo 应要求用户填写本次尚未计算的统计量。

### 对 Dojo 的启发

配置布局可以服务具体研究案例，计算库消费明确参数。已有参考统计量可以作为输入，本轮统计结果则应进入运行产物，并记录来源。

源码依据：

- [Darcy 配置](../../physicsnemo/examples/cfd/darcy_transolver/config.yaml)
- [训练与检查点入口](../../physicsnemo/examples/cfd/darcy_transolver/train_transolver_darcy.py)

## 6. Anemoi：任务、图结构与运行环境分别表达

### 实际组织与证据范围

本地 Anemoi 仓库提供集成测试与生成配置，没有本次案例对应的训练核心源码。检查到的全局训练 YAML 标注为从 `anemoi-core` 自动生成，不能把它当成研究者通常手写的最小配置。

它包含 `data / dataloader / diagnostics / system / graph / model / task / training`：

- `data` 表达变量角色和预处理；`dataloader` 表达批量、工作进程和训练/验证/测试数据选择。
- `system` 放输入输出和硬件；`diagnostics` 放日志、检查点与诊断选择。
- `graph` 描述节点与边；`model` 描述网络组件；`task` 描述预报步长和 rollout。
- 多个组件用 `_target_` 指定，配置之间通过插值复用声明。

集成测试实际调用 `anemoi-training train`，通过命令行覆盖输入根目录、输出目录和轮数。本轮未进一步确认训练核心的默认合并、校验和快照实现。

### 对 Dojo 的启发

研究任务、模型结构和执行环境可以分别表达，完整配置也可以详细到组件层。但无需为了对齐气象模型训练而给 aero_cfd 增加 graph、rollout 等无关分组。

源码依据：

- [生成的全局训练配置](../../anemoi/tests/system-level/anemoi_test/configs/training/global/training_config.yaml)
- [测试任务的训练调用](../../anemoi/tests/system-level/anemoi_test/nodes.py)

## 7. 对照 Dojo 当前配置

### 7.1 五段归属清楚，标准案例的填写负担仍可降低

当前配置是五个业务分组 `rawprep / trainprep / model / train / post`，加上 dataset、pipeline、路径和源码快照等公共设置，并非只有五个顶层键。

五段能够展示完整业务过程，但标准 ShapeNet-Car 实验同时暴露了路径、字段绑定、空映射、采样边界、归一化、模型布局和训练选项。

讨论建议：稳定的案例声明可以提供默认值，研究者主要修改路径、模型选择、种子、采样预算和训练参数；高级字段仍可显式覆盖。最终快照应完整展开，便于核查默认值是否改变。默认声明放 Python 还是辅助 YAML、是否拆文件，尚未决定。

### 7.2 多处字段声明有不同职责，需要统一来源或一致性校验

以压力字段为例：

- `rawprep.fields` 声明从原始数据提取什么。
- `trainprep.domains.targets` 声明磁盘字段如何绑定监督目标。
- `model.data_specs` 声明模型输出维度等契约。
- `model.supervision` 声明预测、标签、归一化和损失的对应关系。

这些声明不能因为名称相似就直接删除。标准案例可以减少重复填写，同时保留自定义映射，并在计算前检查字段、维度与目标是否一致。

`feature_dim` 是特征布局声明；本案例是否使用物理特征由 `trainprep.use_physics_features` 控制。配置说明应明确两者差异，避免用户把“有字段声明”理解为“已经输入模型”。

### 7.3 实验声明、调用参数和运行事实分别保存

实验声明包括：已有数据来源、阶段选择、采样与归一化方法、模型参数、损失、训练预算、输出位置与导出要求。

调用参数由 recipe 从最终配置提取，匹配 application 与能力接口，不需要维持用户 YAML 的分组形状。

运行事实包括：实际样本名单、生成统计量、准备产物、实际选定设备、检查点与预测清单。它们应进入报告和产物记录。

因此，声明输出目录、导出字段、模型输出维度是合理输入；要求用户预填本次尚未产生的检查点或统计结果则不合理。补跑时引用已有检查点属于正常输入。

### 7.4 YAML 表达调整应停留在已有边界内

Dojo 当前 `configuration.py` 负责加载、默认展开、路径解析和业务参数提取，`pipeline.py` 组织阶段，run 通过 `config_loader` 接收最终配置。

若仅改变用户表达方式，应优先在 recipe 边界内处理。只有稳定调用契约确实不足时，才讨论 application 或 run 的功能改动；不能仅因 YAML 改分组而让业务库理解新配置树。

这也不意味着把业务计算迁入 recipe：原子能力仍归 abilities，领域计算与交接归 application，recipe 保持薄调用。

源码依据：

- [当前用户配置](../recipes/aero_cfd/config.yaml)
- [配置加载与参数提取](../recipes/aero_cfd/configuration.py)
- [阶段组织](../recipes/aero_cfd/pipeline.py)
- [通用运行入口](../packages/ai4e-core/run/session.py)

## 8. 后续讨论应先确认的选择

1. 用户默认看到完整案例配置，还是主要看到实验差异？两者都需要能查看完整生效参数。
2. 标准案例哪些声明可以默认提供，哪些研究选择必须显式展示？采样、归一化、字段语义不能因简化而失去可核查性。
3. 默认值如何维护唯一来源，并记录其展开结果？应避免 YAML、Python 默认值和组件默认值各自演化。

目前建议保留五段业务视图，优先讨论标准案例的填写负担和声明一致性。本文件不批准新的配置格式，不替代模块 PRD 或唯一架构文档，也不构成跨框架数值等价性结论。
