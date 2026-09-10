# AI4E_Dojo 架构设计文档

> AI for Engineering / Science 的研究工作台。
> 目标读者：框架开发者，以及要在其上做模型研究的工程师。

> 平台设计更新（2026-09-09）：[第 19 节：Dojo Web / Server 架构草案 v2](#19-dojo-web--server-架构草案-v2) 对应项目管理、任务工作台及项目内六个 Tab。该节为待评审目标架构，不代表实现；平台模块划分以该节为准。产品交互正文见 [Dojo WEB 平台产品设计](PRD/ai4e-web/src/PRD.md)。

---

## 0. 定位

AI4E_Dojo 不是一个训练框架，是一个**研究循环的加速器**。

它服务的人是这样的：他每天产生 5 到 15 个想法，其中活下来 1 个或 0 个。他的瓶颈不是算力，是「从有一个想法，到知道它是死是活」的时间。现在这个时间是 2 到 6 小时，其中真正在算的可能只有 20 分钟，剩下全是接线、等 IO、跑完之后判断好坏。

**唯一北极星指标：把这个时间压到 30 分钟以内。**

每一个架构决策都要能回答「它如何缩短这个循环」。答不上来的设计就是过度设计。

---

## 1. 研究人员在意什么，仓库如何回应

这一节是全文的纲，后面所有内容都是这张表的展开。

| # | 研究人员的真实诉求 | 常见框架的失败方式 | 本仓库的解法 | 落在哪 |
|---|---|---|---|---|
| 1 | 想法要能在几分钟内证伪 | 只有「真跑」一档，排队两小时后在第 3000 步崩 | 四档 profile，共用同一代码路径 | `core/applications/base/profile.py` |
| 2 | 改一行模型代码不要等 40 分钟重跑数据 | 预处理和训练耦合在 `Dataset.__getitem__` 里 | 离线预处理 + 内容寻址缓存 | `core/abilities/data/offline/`、`core/applications/base/cache.py` |
| 3 | 想法不只长在模型层 | 只在 model 处开扩展点 | 变换、几何、采样、约束、指标都是独立可替换 slot | `core/abilities/transform/` `geometry/` `sampling/` `constraint/` |
| 4 | 每次改动只应该改想法那部分 | 组件靠默契通信，改一处波及三处 | 显式数据契约 FieldSpec | `spec/fields.py` |
| 5 | loss 曲线在 AI4S 里是骗子 | 只报标量指标 | 场评估是一等公民 | `core/abilities/eval/` |
| 6 | 跑完不想花 40 分钟判断好坏 | 自己写 pyvista 脚本 | 每次运行自动产出一页纸 | `core/abilities/report/`、`viz/` |
| 7 | 实验的单位是 diff，不是 run | 靠 run name 编码信息 | difftree：派生关系 + 唯一改动 | `task/difftree/` |
| 8 | 默认值会静默出错 | 默认值不可见、不可质疑 | 生效值来源可展开 + 报告主动提示风险 | `core/base/config/explain.py`、`core/abilities/report/warnings.py` |
| 9 | 三个月后要能原样重跑 | 结果目录只有指标，配置和代码已经变了 | 每次运行自动备份 config + 组件源码进 run 目录 | `core/run/backup.py` |
| 10 | 我的组件要活过版本升级 | 强基类 + 字符串 registry，大版本全废 | 独立版本化的 spec，用 Protocol 不用基类 | `packages/ai4e-spec/` |
| 11 | 企业核心组件不能开源 | 私有扩展是二等公民 | 私有插件与官方组件体验完全一致 | `core/base/registry/discover.py` |

---

## 2. 分包与依赖方向

单 monorepo，多个可独立安装的包。**底线场景：研究员在一台没有服务、没有 Docker 的 GPU 机器上，`pip install ai4e-core` 必须能完整跑通训练并产出结果。** 这一条不可妥协，它决定了很多分包边界。

```
ai4e-spec       契约层。几百行，纯 Python，无重依赖，独立版本
   ↑
ai4e-core       运行层。原子能力 + 业务装配 + 执行引擎
   ↑                ↑                ↑
recipes  ai4e-task        ai4e-viz
问题模板       项目/difftree     渲染与报告
                   ↑
              ai4e-server → ai4e-web
```

**CI 强制的依赖方向：**

```
ai4e-spec     → 不 import 任何其他 ai4e 包
ai4e-core     → 只 import spec
recipes  → import spec + core
ai4e-task     → import spec + core，不 import recipes
ai4e-viz      → import spec，不 import core
ai4e-server   → import spec + task
```

几条容易破但必须守住的：

- **core 不 import viz**：训练不能依赖渲染。
- **viz 不 import core**：viz 只读 run 目录，不认识模型和 trainer。这样同一份 run 目录，集群上出静态一页纸、平台上出交互对比，语义完全一致。
- **task 不 import recipes**：task 只认识 run 目录和 config。保证用户完全不用官方模板时 task 照样工作。
- **applications/base 不感知具体 modeling/constraint 实现**：装配机制只认识 Stage、Artifact 和公开协议；调度层一旦知道具体模型或约束，缓存和并行就再也拆不干净。

---

## 3. 仓库总目录

`packages/` 下每个正式包只保留一层目录，不再重复嵌套同名 Python 目录。Python 发布名与导入名由根 `pyproject.toml` 显式映射，例如物理目录 `packages/ai4e-core/` 映射为导入名 `ai4e_core`。

```
AI4E_Dojo/
├── README.md
├── pyproject.toml                   # workspace 根
├── ai4e.toml                        # 项目根标记：store 位置、默认后端
│
├── packages/
│   ├── ai4e-spec/
│   │   ├── pyproject.toml
│   │   ├── data/
│   │   ├── components/
│   │   ├── artifacts/
│   │   └── check/
│   ├── ai4e-core/
│   │   ├── pyproject.toml
│   │   ├── base/
│   │   ├── abilities/
│   │   ├── applications/
│   │   ├── run/
│   │   └── tools/
│   ├── ai4e-task/
│   ├── ai4e-viz/
│   ├── ai4e-server/
│   ├── ai4e-web/
│   └── ai4e-contrib/
│
├── recipes/                       # 普通可复制脚本模板
├── docs/
│   ├── AI4E_Dojo_ARCHITECTURE (1).md # 唯一权威架构文档
│   ├── quickstart.md
│   ├── extending.md                 # 写自己的组件
│   ├── data_onboarding.md           # 数据模块 PRD 的旧入口跳转
│   └── adr/                         # 架构决策记录
│
├── examples/
│   └── flat_minimal.py              # ~200 行单文件，探索期入口
│
├── tests/
│   ├── contract/                    # 不 import core，验证 spec 自足
│   ├── integration/
│   └── regression/                  # 跑 recipe 比对基准指标
│
└── tools/
    └── check_imports.py             # 依赖方向 CI 检查
```

---

## 4. `ai4e-spec` 契约层

### 4.1 它是什么

**唯一一个只写下约定、不写实现的包。**

不是文档，不是纯 schema，也不只是校验库。它是**共享词汇表加上操作这些词汇的最小工具**：定义 AI4E 世界里的名词和语义，让 core、viz、task、server 和无数用户组件能互相理解。

类比：它更像度量衡，不是城门口的检查员。校验只是「有人用错尺子时能发现」，不是它存在的理由。

**约束**：纯 Python + typing + hashlib，不依赖 torch/numpy，安装两秒完成，总量千行以内。

### 4.2 目录

四个子目录对应四类契约：数据长什么样、组件长什么样、产物长什么样、怎么检查。

```
packages/ai4e-spec/             # 构建时映射为 Python 导入包 ai4e_spec
├── __init__.py           # 统一导出，用户只写 from ai4e_spec import FieldSpec, Sample
├── version.py            # SPEC_VERSION，独立于 core 演进
│
├── data/                 # 数据契约
│   ├── fields.py         # FieldSpec / Topology / Rank / State
│   ├── sample.py         # Sample 容器
│   └── batch.py          # Batch 容器
│
├── components/           # 组件契约
│   ├── protocols.py      # Sampler / Transform / Model / Constraint / Metric
│   └── stage.py          # Stage 协议、key_deps 声明
│
├── artifacts/            # 产物契约
│   ├── layout.py         # run 目录布局
│   ├── schemas.py        # metrics / report / lineage 的 json schema
│   ├── keying.py         # compute_key：内容寻址哈希的唯一定义
│   └── config_skeleton.py  # config.yaml 顶层骨架
│
└── check/                # 校验与兼容
    ├── validate.py
    ├── compat.py         # 矢量场 + 逐分量归一化 → 警告
    └── errors.py
```

### 4.3 `data/fields.py`：本仓库区别于通用 DL 框架的实质

```python
class Topology(Enum):
    NODE = "node"; FACE = "face"; CELL = "cell"; GLOBAL = "global"

class Rank(Enum):
    SCALAR = 0; VECTOR = 1; TENSOR = 2

class State(Enum):
    RAW = "raw"; NORMALIZED = "normalized"; RESIDUAL = "residual"

@dataclass(frozen=True)
class FieldSpec:
    name: str
    unit: str                   # "Pa", "m/s", "K", "1"
    topology: Topology
    rank: Rank
    state: State = State.RAW
    dtype: str = "float32"
```

四个属性各自防什么：

- **rank**：矢量场不能做逐分量 z-score，会破坏旋转等变性。这是最典型的静默错误——训练照常收敛、loss 照常下降，模型悄悄丢掉了物理性质，没有任何报错。有了 rank，框架能在启动时警告。
- **topology**：面场和体场的采样、误差分解、导出格式完全不同。
- **unit**：接入新数据集时的语义映射；跨数据集混训时的量纲对齐。
- **state**：「loss 在归一化空间还是物理空间算」这个问题会永远存在，除非它是显式的。

### 4.4 协议：不是准入门槛，不需要穷举

#### 一个必须先回答的疑问

协议能穷举用户的想法吗？我原来用 Transformer 做 model，后来换成 GNN，是不是要加新协议？

**不需要。** 原因分三层。

#### 第一层：调用形状是稳定的，架构变化不影响它

```python
class Model(Protocol):
    def forward(self, batch: Batch) -> Batch: ...
```

Transformer 是 `Batch → Batch`，GNN 也是 `Batch → Batch`。变的是内部实现，不是调用形状。Stage 执行时只做一件事：`x = step(x)`。

#### 第二层：真正在变的东西被推到数据契约层，不在协议层

GNN 需要 `edge_index`，Transformer 需要 `position`。这个差异不该长出两个协议，它是**字段需求的差异**：

```yaml
# my_gnn.yaml
requires:
  - {name: edge_index, topology: node, rank: tensor}
```

**协议管「怎么调用」，FieldSpec 管「需要什么数据」。可变的部分是数据，不是接口。** 如果每换一种架构就要加一个协议，协议确实会爆炸——那说明可变性放错了层。

#### 第三层：Protocol 不参与运行时，框架实际上只要求「可调用」

这是最关键的一点。Python 的 Protocol 是结构化类型，不做运行时检查。Stage 对 step 的唯一要求是它能被调用。所以协议是**分级的可选强化**，不是入场券：

| 级别 | 要求 | 得到什么 |
|---|---|---|
| **0** | 只要是 `callable` | **一定能跑**，没有任何准入检查 |
| **1** | 恰好匹配某个已知 Protocol | IDE 补全、mypy 检查、更精确的报错 |
| **2** | 附带字段声明（yaml 或类属性） | 启动 5 秒内的契约校验 |

级别 0 是保底的。用户写一个谁也没见过的东西，只要能被调用，就能接进链路。

#### 所以协议数量刻意保持很少

5 到 6 个，不追求穷举。撞到边界时有三条出路：

1. 用 `callable`，什么都不声明，照样跑
2. 在自己的包里定义自己的 Protocol，框架不需要知道
3. 某个形状被很多人重复定义时（例如「吃两个 Sample 的对比学习组件」），才提升为官方协议

**加协议是事后追认，不是事前规划。** 协议不该试图预测用户会做什么，它只该把已经反复出现的形状固定下来。

#### 用 Protocol 不用基类

```python
class Sampler(Protocol):
    def __call__(self, sample: Sample) -> Sample: ...

class Transform(Protocol):
    def fit(self, stats: DatasetStats) -> None: ...
    def apply(self, sample: Sample) -> Sample: ...
    def inverse(self, sample: Sample) -> Sample: ...
```

用户写组件时**可以完全不 import 任何东西**。一旦要求继承基类，用户代码就和你的版本绑死了。

反面教材：mmdetection 扩展性极强，但没有独立契约层，扩展点直接依赖主库基类和字符串 registry，大版本升级后用户组件基本全废，用户的应对是 fork 整个仓库然后再也不升级。**那才是真正的固化，而且它恰好发生在一个「开放性很强」的框架上。**

### 4.5 验收标准

找一个组外的人，**在完全不 import `ai4e-core` 的前提下**写一个采样器并跑通。做不到就说明契约还不干净。

---

## 5. `ai4e-core` 运行层

### 5.1 两个轴，两层结构

这是本仓库最重要的结构决策，先讲清楚为什么。

一个直觉是：既然 recipe 的用户入口分为 `rawprep / trainprep / model / train / post` 四段，代码就全部按四阶段分包。**这个做法在原子层会失败**，因为很多能力天然跨阶段：

| 能力 | 出现在哪些阶段 |
|---|---|
| transform | pre（fit 统计量）、train（apply）、post（inverse） |
| eval | train（每个 val epoch）、post（最终评估） |
| sampling | pre（离线降采样）、train（在线 supernode 采样） |
| data/online | train、post 中的推理 |
| geometry | pre、model 的输入编码 |

按四阶段切原子，`transform` 要么被复制三份，要么放进其中一个然后被另外两个反向 import，后者立刻产生循环依赖。

**所以分两层：**

```
原子层（按能力分）      能力是「有什么」，跨阶段复用，无重复
装配层（按业务分）      业务是「怎么用」，recipe 按 rawprep/trainprep/model/train/post 展开
```

用户在 recipe 中看到 `rawprep / trainprep / model / train / post` 四段，维护者在 core 中看到可跨阶段复用的原子能力。`infer` 和最终 `eval` 不再作为独立的 recipe 阶段，而由 `post` 调用；core 内仍保留 `inference`、`eval` 两项独立能力，避免把推理、指标算法和结果处理揉成一个实现模块。

### 5.2 目录

```
packages/ai4e-core/             # 构建时映射为 Python 导入包 ai4e_core
│
├── base/                        # 框架基础设施，不包含数值算法和业务流程
│   ├── registry/                # 组件解析、发现与源码 schema 抽取
│   └── config/                  # 配置合并、解析、校验、diff 与 explain
│
├── abilities/                   # 可跨阶段复用的原子能力
│   ├── data/
│   │   ├── source/              # 来源访问、读取、格式适配、分片名单
│   │   ├── extract/             # 字段提取与身份记录
│   │   ├── validate/            # 数量、归属、身份和输出门禁
│   │   ├── filter/              # 标记与统一选择
│   │   ├── save/                # 张量读写与提交恢复
│   │   └── stats/               # 数组流统计
│   ├── transform/               # fit / apply / inverse，可跨 pre/train/post 复用
│   ├── geometry/                # pointcloud / sdf / graph / voxel
│   ├── sampling/                # uniform / curvature / supernode / importance
│   ├── modeling/
│   │   ├── modules/             # attention, blocks, encoders, decoders
│   │   └── models/              # 框架管理的模型装配；外部模型保持独立
│   ├── constraint/              # Constraint / ConstraintResult 与权重策略
│   ├── training/                # loop / strategy / callbacks / checkpoint
│   ├── inference/               # checkpoint 重建和推理 runner
│   ├── eval/                    # 工程指标、守恒、泛化和 worst-k
│   ├── postproc/                # inverse、误差场、工程量、网格回贴与导出
│   └── report/                  # report artifact、自包含报告与风险提示
│
├── run/                         # 驱动执行、批量循环与运行记录
│   ├── runner.py                # 通用配置与管道入口
│   ├── execute.py               # 顺序逐项执行与失败汇总
│   ├── layout.py
│   ├── writer.py                # run 目录的唯一写入方
│   ├── reader.py
│   ├── provenance.py            # git sha / dirty diff / env / 数据集哈希 / seed
│   ├── backup.py                # 把本次的 config + 用户组件源码快照进 inputs/
│   └── lineage.py               # 写 parent run + 唯一改动，供 difftree 索引
│
├── applications/                # 业务装配层
│   ├── base/                    # 所有业务共享的装配机制
│   │   ├── stage.py             # Stage：inputs/outputs、key_deps 白名单
│   │   ├── graph.py             # DAG 构建与拓扑执行
│   │   ├── cache.py             # 内容寻址缓存
│   │   ├── pipeline.py          # Pipeline 容器
│   │   └── profile.py           # smoke / overfit / dev / full
│   │
│   └── aero_cfd/
│       ├── rawprep/              # 原始数据清洗、提取与公共数据资产
│       ├── trainprep/            # 项目数据准备、归一化、采样及监督目标
│       ├── model/                # 网络选择、参数与学习目标的标准装配
│       ├── train/                # 优化器、训练循环、监控与 checkpoint 的标准装配
│       └── post/                 # infer、eval、inverse/回贴、导出和报告的标准装配
│
├── tools/                       # 生成/改写文件的工具（非运行时）
│   ├── new.py                   # 新建项目
│   ├── fork.py                  # 从 recipe fork
│   ├── show.py                  # 打印组件源码 / 展开装配为等价代码
│   ├── new_component.py         # 生成组件骨架
│   └── check_component.py       # 校验组件能否接进链路
│
└── cli.py                       # 薄壳，见 §6
```

五个一级分组有明确的依赖方向：`base` 提供最小基础设施，`abilities` 在公开契约上形成原子能力，`applications/base` 提供通用装配机制，`applications/aero_cfd` 则按 `rawprep / trainprep / model / train / post` 放置 Aero CFD 的标准业务装配。recipe 选择、配置或轻量覆盖这些标准装配，不复制 core 的算法与执行机制。

AB-UPT 多域架构：贡献模型维护有序域/字段声明、token 布局、条件调制与层内 K/V；core 不引入 Noether 依赖或统一模型容器。trainprep 绑定数据和采样，model 定义学习目标，train 保留更新/评估/恢复机制，post 通过注入的推理上下文组织分块查询。缓存仅属于当前模型的无梯度评估，权重/设备/精度/训练模式改变使其失效，不进入检查点或跨运行内容缓存。新模型与检查点使用版本 2，不保留旧双域实现。

`post` 是用户视角的一段流程，可以依次调用 `abilities/inference`、`abilities/eval`、`abilities/postproc` 和 `abilities/report`。这些能力在实现层仍然彼此独立，不能因为 recipe 合并入口而互相复制代码。

### 5.2.1 `constraint/`：把“优化什么”表达完整

#### 要解决的问题

`loss(pred, target)` 只回答“两个张量怎么比较”，不能完整描述 AI4S 训练中的约束：约束作用于哪个区域、需要哪些字段、计算哪一个物理表达式、目标值是什么、在归一化还是物理空间计算，以及多个约束之间如何加权。

这个缺口在纯监督任务里不明显，但一旦同时训练表面压力和体速度，或者加入 PDE 残差、边界条件、初值和守恒项，相关逻辑就会分散到 Dataset、模型 wrapper、Trainer 和 callback 中。最后虽然都叫 loss，却无法独立配置、校验、记录和比较。

#### 怎么解决

把 `Constraint` 定义为训练中的一等约束单元。每个约束显式绑定：

- `domain/source`：约束作用的数据域，以及数据来自现有 batch 还是专用采样器；
- `requires`：计算所需的字段及其 FieldSpec；
- `expression`：直接读取模型输出，或计算 PDE、边界、守恒等表达式；
- `target`：监督真值、常数、解析函数或零残差；
- `loss`：表达式与目标之间的比较方法；
- `weight/schedule`：固定权重、区域权重或课程学习策略；
- `space`：在 `NORMALIZED`、`RAW` 或 `RESIDUAL` 空间计算。

监督约束与物理约束使用同一个最小调用形状：

```python
class Constraint(Protocol):
    def __call__(
        self,
        batch: Batch,
        prediction: Batch,
        context: ConstraintContext,
    ) -> ConstraintResult: ...
```

`ConstraintResult` 至少包含具名标量、当前权重和可记录的分项值。训练循环只负责执行约束集合、聚合总 loss 和反向传播，不理解 `surface_pressure`、PDE 方程或边界条件。Constraint 可以使用数据管道提供的 batch，也可以声明专用采样源，但不负责创建 Dataset、调度 Stage 或管理优化器。

例如 AB-UPT 的配置可以明确写成两个监督约束：

```yaml
constraints:
  surface_pressure:
    _target_: ai4e_core.abilities.constraint.Supervised
    prediction: surface_pressure
    target: surface_pressure_target
    space: normalized
    loss: mse
    weight: 1.0
  volume_velocity:
    _target_: ai4e_core.abilities.constraint.Supervised
    prediction: volume_velocity
    target: volume_velocity_target
    space: normalized
    loss: mse
    weight: 1.0
```

以后加入物理约束时，只增加新的 Constraint，不需要改训练循环：

```yaml
  mass_conservation:
    _target_: ai4e_core.abilities.constraint.Physics
    expression: divergence_velocity
    target: 0.0
    space: raw
    weight: {schedule: linear_warmup, end: 0.1}
```

#### 价值

1. **语义完整**：一个对象完整回答“在哪里、用什么数据、计算什么、逼近什么、权重多少、在哪个空间算”。
2. **统一监督与物理训练**：AB-UPT 的多字段监督、PINN 的 PDE/边界约束和混合数据—物理训练共享同一装配方式。
3. **错误更早暴露**：启动时即可根据 `requires` 和 `space` 检查字段、拓扑、单位与状态，避免训练中途才发现物理量或归一化空间用错。
4. **实验可解释**：每个约束的配置、权重曲线和分项结果都进入 resolved config、缓存 key、checkpoint 和报告，能够精确比较“这次实验到底改了哪个约束”。

### 5.3 业务应用内部长什么样

application 封装完整但可独立调用的业务步骤，recipe 声明这些步骤的顺序和参数。外流 pre 收敛为 read、derive、select、save、stats 五个模块；不为每个函数创建目录。读取、字段选择、训练样本选择和缺失策略属于 application，数值能力属于 abilities。

```text
recipe 作业阶段：发现样本 → run 逐项执行 → 确定统计量
recipe 单样本阶段：读取 → 提取 → 几何派生 → 选择字段
                  → 对齐校验 → 筛选 → 编码 → 提交
```

用户用 Dataset 登记步骤，内部复用现有 Stage。run 接收样本引用和顺序步骤，不解释业务字段；每次处理一个样本，只汇总轻量结果。application 不反向依赖 run；recipe 负责将双方公开接口连起来。datapre(cfg) 显式展示次一级步骤，循环封装在 run 内。

允许不同领域链路存在少量顺序代码；不建立带大量分支的通用业务工厂。单条装配链超过 30 行时拆分 application 的业务封装，不能将算法留在 recipe。

同组身份校验、字段与文件选择属于训练数据交付边界，不等同于完整 Sample/Artifact 系统。数据目录提交由 save 负责，运行配置、日志与业务报告由 RunWriter 独占；完整生命周期规划不因目录存在而视为已实现。

### 5.4 版本化

稳定的 Aero CFD 标准装配归 `core/applications/aero_cfd`，具体数据、参数和覆盖归 recipe。run 必须记录 core 版本、recipe 版本、resolved config 和组件源码；core 改变标准装配或 ability、recipe 改变参数或覆盖时，都必须明确标出是否影响结果，不能静默污染已有结论。

**经验能迭代的前提，是变更不会静默污染别人已有的结论。**

### 5.5 明确不开放的

- `training/loop.py` 不开放整体替换。只开放 callback 和 constraint。理由：能替换整块就等于复制粘贴，复制粘贴就是分叉的开始。真要改循环的，走 §13.2 第 3 档自拼，那是显式的选择。
- 分布式、混合精度、checkpoint 分片、梯度累积——配置一行，永不出现在用户视野，除非坏了。坏了要给看得懂的报错，不是 NCCL 的十六进制码。

---

## 6. 配置的边界：yaml 管什么，命令行管什么

**一条清晰的分界线：**

| | 归属 | 举例 | 进 run 记录 | 参与缓存 key |
|---|---|---|---|---|
| **算什么** | `config.yaml` | 模型结构、超参、归一化、采样、数据路径、字段语义 | 是 | 是 |
| **在哪算** | 命令行 / 环境 | GPU 数、节点数、后端、num_workers、profile | 是（记录） | **否** |

这条线的意义：**换个 GPU 数量不该让缓存失效，也不该让这次运行看起来和上次是不同的实验。** 而改学习率必须。

```bash
python train.py                                   # 默认，全部读 config.yaml
python train.py --profile smoke                   # 执行档位
python train.py --gpus 4 --backend slurm          # 资源
```

`--set` 仅作为调试例外存在，日常路径不用它。所有实验参数都在 yaml 里，这样一次运行的定义是完整可复现的。

### CLI 只是薄壳

Python 是唯一实现，CLI 是 argparse 到函数调用的映射，不含任何逻辑：

```python
from ai4e_core.applications.base import Pipeline
from ai4e_core.base.config import load_config

Pipeline.from_config(load_config("config.yaml")).run(profile="smoke")
```

保留 CLI 的三类命令（都不是运行参数，yaml 装不下）：

- **文件操作**：`ai4e new` / `fork` / `new-component`
- **只读检视**：`ai4e explain` / `show` / `doctor` / `tree`
- **集群提交**：`ai4e submit --backend slurm`

---

## 7. profile：四档执行

### 要解决的问题

只有「真跑」一档时，一个想法要排队两小时、跑到第 3000 步才在 collator 里崩掉。而 90% 的 bug 是形状对不上、key 拼错、单位没转，这些本该在 10 秒内暴露。

### 怎么做

**不自动识别。** 自动识别是错的方向——「我以为在跑全量，框架自作主张跑了 smoke」这种事一次就足以摧毁信任。执行意图必须显式，但不该让用户手写一堆参数。

做成命名 profile，由具体 recipe 在 `config.yaml` 中声明：

```yaml
profiles:
  smoke:   {samples: 1, max_steps: 2,    subset: dev1, device: cpu, report: true}
  overfit: {samples: 1, max_steps: 5000, subset: dev1}
  dev:     {samples: 8, max_steps: 2000, subset: dev8}
  full:    {}
default_profile: full
```

用户直接 `--profile smoke`，不用写任何东西。要自定义再往这里加。

**profile 只允许覆盖白名单内的执行参数**（样本数、步数、子集、device、日志级别），碰不到模型结构、损失、归一化——否则 smoke 跑的就不是同一件事了。加载器强制这一点，越界直接报错。

**共用同一代码路径。** 任何 `if profile == "smoke"` 出现在 `loop.py` 之外的地方都是设计失败——那种设计必然退化成「smoke 通过但真跑崩」。

### 各档的作用

- **smoke**（10 秒）：回答「全链路有没有断」，不看指标
- **overfit**（20 分钟）：单样本过拟合到接近零，回答「模型有没有表达能力、梯度通不通」。**这是最被低估的一档**——连单样本都过拟合不了的架构，上全量只是浪费一晚上 GPU
- **dev**（小时级）：小规模真实训练，看趋势
- **full**：正式

### 唯一该自动的地方

`full` 之前自动先跑一遍 smoke 作为 preflight，10 秒，失败就不提交。默认开启，可关。

自动不该用来猜用户想跑什么，该用来**在昂贵操作前免费做一次检查**。

---

## 8. 内容寻址：模块如何找到上游产物

### 要解决的问题

`train.py` 单独运行时，它怎么知道前处理的产物在哪？

如果靠用户在 yaml 里手写路径，会发生这三件事：

1. 改了采样参数重跑前处理写到新目录，忘了改 train 的路径 → **训练用了旧数据，没有任何报错**，跑出一个解释不了的结果
2. 写到同一个目录 → 之前那个 run 的产物被覆盖，历史不可复现
3. 做 sweep，8 个配置并行 → 8 个输出路径要手工编排

第一种是静默错误，在 CAE 数据规模下（一次前处理 40 分钟）代价极高。

### 怎么做

两个共享就够了，不需要 task 介入。

**共享一棵 config 树。** 单模块的配置不是「只有自己那段」，是「完整树」。所以 train 单跑时手上就有完整的 preprocess 配置段。

**共享一个 store。**

```
.ai4e/store/preprocess/<key>/
.ai4e/store/train/<key>/
```

`<key> = compute_key(stage_type, 生效配置子集, 上游key, 用户组件源码哈希)`

于是 train 求解上游的过程是：

```
1. 从 config 树取出 preprocess 那一段
2. 按 spec/keying.py 的规则算出它的 key
3. 查 .ai4e/store/preprocess/<key>/
4. 命中 → 直接用；未命中 → 就地跑一遍，写进那个位置
```

**train 从来不需要知道上游产物叫什么，它自己算得出来。** 这是内容寻址和路径寻址的根本区别：路径是被命名的，需要有人告诉你；key 是被计算的，任何人独立算都得到同一个值。

`applications/base/pipeline.py` 在这里只做一件事：按拓扑序执行，让每一步命中缓存。它不传递路径。绕过完整 Pipeline、单跑某个 Stage，结果语义保持一致。

### 三个边界

**只有配置的子集参与 key。** 前处理的 key 不该被 `train.lr` 影响，否则改学习率要重跑 40 分钟。每个 Stage 显式声明白名单：

```python
key_deps     = ["fields", "dataset", "transform", "sampling", "preprocess"]
key_excludes = ["num_workers", "log_level", "device"]
```

必须是显式白名单，不能自动推断。多算了缓存永不命中，少算了用错产物。

**用户组件的源码哈希必须参与 key。** 用户改了自己的采样器实现但没改参数，key 必须变。这是最容易漏、也最坑人的一条。

**未命中时的行为可配：**

```bash
python train.py                    # 默认：自动跑上游
python train.py --require-cache    # CI/大集群：报错并打印缺什么
```

### 显式输入是一等公民，不是例外

每个 stage 都有 `inputs` 段，默认 `auto`，但随时可以指向别处：

```yaml
preprocess:
  inputs:
    raw: /shared/datasets/drivaerml/           # 共享数据集

train:
  inputs:
    preprocessed: auto                         # 默认：内容寻址
    # preprocessed: /shared/prep/drivaerml_v3/ # 复用同事的昂贵产物
    init_from: null                            # 或 runs/2026-08-11_a3f21c/checkpoints/best.pt

post:
  inputs:
    predictions: auto
    # predictions: runs/2026-08-11_a3f21c/predictions/   # 对旧结果重做后处理
```

这三种场景（共享数据集、复用他人产物、基于旧 checkpoint 继续）真实且高频，所以显式指定是正常用法，不是逃生口。**只是默认必须是 auto**——默认值决定 95% 用户的行为，把手写路径设成默认，等于把静默错误设成默认。

指定显式路径时，该 stage 的 key 改为基于该路径的内容哈希，下游依然正常工作。

### pipeline 跑哪些模块，写在 yaml 里

```yaml
pipeline:
  stages: [pre, model, train, post]
  # stages: [model, train, post]     # 用共享数据集，跳过前处理
  # stages: [post]                   # 从 checkpoint 推理、评估并重做结果处理
```

于是 recipe 的运行入口只需三行，不含任何编排逻辑：

```python
from ai4e_core.applications.base import Pipeline
from ai4e_core.base.config import load_config

if __name__ == "__main__":
    Pipeline.from_config(load_config()).run()
```

**改跑哪几段是配置，不是代码。** 这样它和其他所有实验参数一样进 run 记录、可被 diff、可被 sweep。

### 覆盖链必须可见

```bash
$ ai4e explain sampling.max_nodes

sampling.max_nodes = 4096
  ← config.yaml                         (显式设置)
  ← recipe 内置默认值              2048  (recipe 默认)
```

多层覆盖最常见的问题不是不能覆盖，是**覆盖了但没生效，或生效了但用户以为没有**。能打印这个链条，问题就消失了。

---

## 9. recipes 普通模板与共享数据集

recipes 是普通可复制目录，不参与包安装。当前 aero_cfd 提供 README、config、datapre、trainprep、train、post 和 pipeline。pipeline 显式交接阶段引用，datapre(cfg) 展示处理步骤，不要求用户编写 Stage、partial 或样本循环。

数据结构事实与官方分片属于 contrib/application/datasets 的 manifest；adapter 解释来源和样本身份；recipe 声明字段、分量、样本、分片、处理方法和参数。contrib 可安装并通过公开 core/spec 契约复用，也可复制修改。core 不反向依赖 contrib。

Dataset 只持有样本引用和顺序步骤，run 逐样本执行并释放数组。保存策略解释分片输出，训练读盘消费实际产物 manifest。代码、运行记录和 datasets 独立配置；路径使用 ${data_root}/train 等显式插值，相对路径按配置文件解析。

阶段引用可独立重建：datapre 交付数据 manifest，trainprep 交付包含归一化、数据与组件内容摘要的 preparation.json，train 交付 training.json 与检查点。持久化记录不包含 Python 闭包；样本采样在训练迭代发生。领域 application 提供公开装配步骤，recipe 显示输入输出和参数，算法与循环仍在原子能力层。配置 resolver 由入口注入 run，run 不反向识别领域默认值。模型内部归一化、投影与输出头按计算单元组织，参数注册顺序也是数值可复现契约的一部分。

原子能力发事件，writer 独占日志文件；输入只保留最终生效 YAML。训练统计仅使用本次完整训练分片；归一化和训练循环已交付。平台上传和跨运行内容缓存仍为后续；task new/fork 见第 19.5 节。

## 10. `ai4e-task`

> 本节保留研究循环与 difftree 的设计原因。下方早期目录为概念划分；平台落地的 task 模块边界、任务／版本／运行语义更新见第 19 节，不据此并行建立第二套项目、版本或执行服务。

### 目录

```
packages/ai4e-task/             # 构建时映射为 Python 导入包 ai4e_task
├── store.py              # 本地 sqlite + jsonl 索引
├── project.py            # 新建、注册、from-recipe fork
├── difftree/             # 实验的派生关系树
│   ├── scan.py           # 扫描 run 目录的 lineage.json 建索引
│   ├── tree.py           # 树结构与查询
│   └── render.py         # 文本视图
├── hypothesis.py         # expect 断言求值
├── compare.py            # 案例对比的编排（计算在 core）
├── backend/              # local / slurm / k8s / remote
├── sweep.py              # 薄封装 hydra multirun / optuna
└── cli.py
```

### 一条必须守住的分界

**记录在 core（`core/run/lineage.py`），索引与查询在 task。**

派生关系必须由**产生它的那个进程**在结果落盘时原子写入，和 git sha、env、数据集哈希写在一起。如果记录放在 task：

1. 没连 task 的那次运行，溯源永久丢失——而「我在集群上随手跑的那个」最后往往成了论文里的结果
2. run 目录不再自包含，拷给同事就是一堆没有来历的文件

**真相跟着数据走，服务只是索引。**

### difftree：实验的单位是 diff，不是 run

wandb / mlflow 把 run 当扁平原子对象，大家靠 run name 编码信息，三个月后没人看得懂 `abupt_v3_final_fix2_lr3e4` 在验证什么。

```bash
ai4e fork run://a3f21c --set sampling.max_nodes=4096
ai4e tree
```

```
● a3f21c  baseline (supernode 2048)          l2=0.043
├── ● 8b1e02  max_nodes=4096                 l2=0.041  ✓ confirmed
│   └── ● c40f19  + curvature sampling       l2=0.052  ✗ refuted
└── ● 5d7a83  transform: vector_aware        l2=0.038  ✓ confirmed  ← current
```

系统记录的是**派生关系加上那唯一的改动**。研究员的心智模型本来就是树，工具却给一个列表，这个转换每天都在付成本。

### 假设可执行

config 里：

```yaml
hypothesis: 矢量场用模长归一优于逐分量
baseline: run://a3f21c
expect:
  - surface_pressure.l2 < baseline * 0.95
```

跑完自动判定 confirmed / refuted / inconclusive，写进树。实验记录不再是某个 notebook 里的一句话，而是能被重放、被同事审阅的记录。

---

## 11. `ai4e-viz`

**只读 run 目录，不认识模型也不认识 trainer。**

「算」和「显」必须分开：

- **算**（误差分解、守恒残差、worst-K、切片）依赖数据管道、依赖归一化逆变换、依赖物理语义 → 只能在 core
- **显**（3D 交互、联动切片、报告编排）→ viz

```
packages/ai4e-viz/              # 构建时映射为 Python 导入包 ai4e_viz
├── read.py               # 按 spec/artifacts.py 读，校验 schema version
├── render/               # field_3d / slice / curve / scatter / diff_view
├── compose/
├── static.py             # 自包含 HTML，离线可看，能 scp 走
└── service.py            # 给 web 的渲染接口
```

`static.py` 不能省——研究员半夜在集群上看结果，不会为了看一张云图去开平台。这是「代码包独立可用」的最后一环。

---

## 12. 数据流转

从用户敲下第一个命令，到结果落盘，完整走一遍。

### 12.1 用户输入

```bash
$ python train.py --profile dev --gpus 2
```

等价的 Python 调用：

```python
from ai4e_core.applications.base import Pipeline
from ai4e_core.base.config import load_config
Pipeline.from_config(load_config()).run(stages=["train"], profile="dev", gpus=2)
```

### 12.2 第 1 步：配置解析（约 1 秒）

```
load_config()
  ├─ 向上找 ai4e.toml 确定项目根
  ├─ 读 config.yaml
  ├─ 读取 recipe 的 config.yaml 与本地覆盖
  ├─ 合并并记录每个生效值的来源
  ├─ 应用 profile=dev（只覆盖白名单：samples / max_steps / subset）
  └─ 解析 ${} 插值
  ↓
resolved_config     完全展开、无省略、无插值
```

### 12.3 第 2 步：契约校验（约 3 秒，失败在这里发生）

```
config/validate.py
  ├─ 每个 _target_ 能否解析到真实的类？        → 拼错在这里报错
  ├─ 每个组件的参数是否匹配其签名？             → registry/introspect 抽出的 schema
  ├─ fields 段的 FieldSpec 是否合法？           → spec/fields.py
  └─ spec/compat.py 兼容性检查
       velocity 是 VECTOR，transform 是 Moment（逐分量）
       ⚠ 会破坏旋转等变性，建议改用 VectorAware
```

**这一步的意义**：所有配置错误在 5 秒内暴露，不是排队两小时后在第 3000 步崩。

### 12.4 第 3 步：装配（毫秒级）

```
recipes/aero_external/train.py :: build(cfg)
  ↓
Stage(name="train",
      key_deps=["fields","dataset","transform","sampling","model","constraints","train"],
      steps=[...])
```

### 12.5 第 4 步：依赖求解（毫秒 ~ 40 分钟）

```
Stage.resolve_inputs()
  │
  ├─ cfg.train.inputs.preprocessed == "auto"？
  │    │
  │    是 → 从 cfg 取出 preprocess 段
  │        key = compute_key("preprocess", 该段, None, 组件源码哈希) = "a7f3c2e1"
  │        查 .ai4e/store/preprocess/a7f3c2e1/
  │          ├─ 存在   → 直接用            【改模型时走这条，0 秒】
  │          └─ 不存在 → 就地执行 preprocess【改采样时走这条，40 分钟】
  │
  └─ 否（显式路径）→ 用该路径，key 改为路径的内容哈希
```

### 12.6 第 5 步：训练时数据在管道里的完整流转

追踪 Sample 的状态迁移：

```
磁盘 .ai4e/store/preprocess/a7f3c2e1/data.zarr
  ↓ data/online/sample_processor
Sample{
  pressure: ndarray,  FieldSpec(Pa,  FACE, SCALAR, RAW)
  velocity: ndarray,  FieldSpec(m/s, CELL, VECTOR, RAW)
}
  ↓ transform.apply（统计量来自 preprocess 阶段 fit 的 artifact）
Sample{ ..., state: NORMALIZED }
  ↓ sampling（supernode 采样，2048 点）
Sample{ 点数减少，specs 不变 }
  ↓ data/online/collator
Batch{ 多个 Sample 拼接，带 offset }
  ↓ data/online/batch_processor
Batch{ 位置归一化等 batch 级操作 }
  ↓
┌──────── training/loop.py 迭代 ────────┐
│ model.forward(batch) → 预测场 (NORMALIZED)
│ constraints(batch, prediction, context)
│   ├─ surface_pressure  在 NORMALIZED 空间算监督约束
│   ├─ volume_velocity   在 NORMALIZED 空间算监督约束
│   └─ physics_residual  需要 RAW → 通过 context 调 transform.inverse
│ aggregate ConstraintResult.loss
│ backward / optimizer.step
│ callbacks（指标、日志、checkpoint、early stop）
└───────────────────────────────────────┘
  ↓ 每 N epoch
eval（val 集）→ metrics
  ↓ 训练结束
training/checkpoint.py 打包：
  权重 + model schema + transform 统计量 + fields 定义 + resolved_config
  ↑ 这个打包是「推理时统计量对不上」这类事故的唯一防线
```

### 12.7 第 6 步：推理与后处理

```
inference/rebuild.py
  从 checkpoint 反序列化，重建 model 和 transform
  ↑ 与训练走同一条构造路径，不是另写一套
  ↓
预测 (NORMALIZED)
  ↓ transform.inverse
预测 (RAW，物理量纲)          ← 所有指标和导出必须在这之后
  ↓
┌── eval ───────────────────────────────┐
│ decompose       表面/体积、边界层/远场、梯度分桶
│ conservation    质量/动量/能量残差
│ generalization  内插 vs 外插分开报
│ worst_k         最差 K 个样本
└───────────────────────────────────────┘
  ↓
postproc/export   → fields/*.vtp, *.vtu
  ↓
report/build      → report.json（有哪些图、每张图的数据源和语义）
report/local_html → report.html（自包含一页纸）
```

### 12.8 第 7 步：落盘（下图含后续训练产物规划）

```
core/run/writer.py 写入：

runs/2026-09-05T14-22-01_5d7a83/
├── inputs/           ★ 本次输入的完整快照，见 §13.3
│   ├── config.yaml       唯一最终生效配置，含展开变量和默认值
│   └── components/       所有 _target_ 指向项目内的组件源码
│       ├── curvature.py
│       └── my_residual.py
├── provenance.json   git sha / dirty diff / env / 数据集哈希 / seed / 硬件
├── lineage.json      parent: a3f21c, change: {transform.velocity: Moment→VectorAware}
├── metrics.json
├── report.json
├── report.html
├── fields/           vtp / vtu
├── checkpoints/
└── logs/
```

### 12.9 第 8 步：被下游消费

```
runs/2026-09-05T14-22-01_5d7a83/
  ├──→ ai4e-task   扫 lineage.json，把这个 run 挂到 difftree 上
  │                求值 hypothesis 的 expect 断言 → confirmed
  └──→ ai4e-viz    读 report.json 渲染交互视图
                   （或直接打开 report.html，不需要任何服务）
```

### 12.10 三种典型场景下的实际流转

**场景 A：只改了模型代码**

```
model 段变 → train 的 key 变 → preprocess 的 key 不变
  → preprocess 缓存命中，0 秒 → 直接进训练
```

**场景 B：改了采样密度**

```
sampling 在 preprocess 的 key_deps 里 → preprocess key 变
  → 缓存未命中，重跑前处理（40 分钟），写到新 key 下
  → 旧 key 的产物仍在，之前的 run 依然可复现
```

**场景 C：用共享数据集，跳过前处理**

```yaml
train:
  inputs:
    preprocessed: /shared/prep/drivaerml_v3/
```
```python
Pipeline([model, train, post], cfg)     # 不含 pre；post 内执行 infer/eval
```
```
train 的上游 key = hash(/shared/prep/drivaerml_v3/ 的内容)
  → 不触发任何前处理，下游依然正常，因为 key 链条完整
```

### 12.11 关键的错误信息

契约在 stage 交接处校验，报错要能直接指出问题：

```
StageContractError: train 需要字段 'surface_normal' (FACE, VECTOR, RAW)
  但 preprocess 的输出中不存在。

  preprocess 实际输出：
    pressure  (FACE, SCALAR)
    velocity  (CELL, VECTOR)
    wss       (FACE, VECTOR)

  提示：检查 sampling.Supernode 是否丢弃了法向信息
        （它的 preserve_fields 默认不含 surface_normal）
```

**这一句报错省下的时间，比整个装配层加起来还多。**

---

## 13. 用户如何使用

### 13.1 三个入口

| 入口 | 什么时候用 | 得到什么 |
|---|---|---|
| `ai4e new --flat` | 探索期，一个全新的想法 | ~200 行单文件，从数据到评估全在里面 |
| `ai4e fork aero_external` | 日常，做一个具体案例 | 一份 config + 四个薄装配脚本 |
| 直接 import | 已有项目里嵌入 | 从 recipe 导入 `rawprep/trainprep/model/train/post` 的构造函数 |

**为什么要有单文件入口**：研究的真实起点永远是脚本。我有个想法，第一件事是复制一个能跑的短脚本改它，而不是配置一个框架。一个不能容纳脚本的框架，最后会变成一个所有人都绕开的框架。

### 13.2 四档改动

#### 要解决的问题

用户的改动大小是**长尾分布**的：

| 改动类型 | 占比 | 例子 |
|---|---|---|
| 只改数值 | ~50% | supernode 从 2048 改 4096 |
| 换一个已有组件 | ~30% | 采样从均匀换成曲率自适应 |
| 插入一个自己写的组件 | ~15% | 在变换后加一个残差编码 |
| 重排整条链路 | ~5% | 前处理顺序完全不同 |

如果框架只提供两档——「用默认」和「全自己写」——那么占 80% 的小改动用户，被迫付出 5% 大改动的成本：他要复制整条链路的代码，只为了改中间一行。

**这就是「框架很脆」的体感来源。而脆和固化在用户眼里是一回事：都是不敢碰它，然后 fork 出去。**

#### 设计原则

**改动的成本必须正比于改动的大小。** 四档就是这个原则的展开。

四档全部在**同一个文件、同一个函数**里，往下走时不换文件、不换概念、不换心智模型。这个连续性比任何一档本身都重要。

#### 第 0 档：用默认（~50%，连代码都不碰）

```python
# train.py
from ai4e_core.applications.base import Pipeline
from ai4e_core.base.config import load_config
build = lambda: Pipeline.from_config(load_config())
```

改动全在 `config.yaml`：

```yaml
sampling:
  max_nodes: 4096
```

*存在的意义*：绝大多数改动是调参。调参不该需要读懂任何代码。

#### 第 1 档：换一个槽（~30%）

```python
from my_project.components import CurvatureAdaptive

def build(cfg):
    stage = build_train_stage(cfg)
    stage.override(sampling=CurvatureAdaptive)
    return stage
```

或者根本不写代码，直接在 config 里换 `_target_`：

```yaml
sampling:
  _target_: my_project.components.CurvatureAdaptive
  max_nodes: 2048
  curvature_weight: 1.0
```

*存在的意义*：**这是研究想法最常落地的形式**——我有一个新方法，它替换掉链路里的某一个环节，其余保持不变。这一档必须极其顺滑，因为它是主战场。

*它解决的问题*：不需要重写完整 Stage，就能替换其中一步；链路的其余部分继续复用 core 的 ability 与装配机制。

#### 第 2 档：插入一段（~15%）

```python
def build(cfg):
    stage = train.standard(cfg)
    stage.insert_after("transform", MyResidualEncoder(cfg.residual))
    return stage
```

*存在的意义*：我的想法不是替换，是**增加**。比如在归一化之后加一个残差编码，或在采样前先做几何特征提取。

*为什么第 1 档凑合不了*：只有 override 的话，用户为了插一步必须把相邻那一步整个替换掉，然后在自己的实现里重新包含原逻辑加新逻辑。那是复制粘贴，而复制粘贴就是分叉的开始。

*为什么第 3 档凑合不了*：为了加一步而重写整条十几步的链路，成本完全不成比例，而且从此失去所有升级收益。

#### 第 3 档：完全自拼（~5%）

```python
from ai4e_core.applications.base import Stage
from ai4e_core.abilities import data, transform

def build(cfg):
    return Stage(
        name="train",
        key_deps=["fields", "dataset", "transform", "my_geom", "model"],
        steps=[
            data.source.auto(cfg.dataset),
            MyGeometryEncoder(cfg.my_geom),      # 顺序与标准链路完全不同
            transform.build(cfg.transform),
            data.online.collate(cfg.train),
            ...
        ],
    )
```

*存在的意义*：**天花板必须存在，而且必须是完整的自由。** 任何框架，只要用户撞到「这件事在你的抽象里表达不了」，他就会离开。第 3 档保证这件事不会发生。

*为什么它还在框架内*：即使完全自拼，用户依然享有内容寻址缓存、四档 profile、run 记录、difftree、自动报告。**逃出去的人也必须留在系统里**——这是 COMSOL 用户跳到 MATLAB 后失去一切的反面。

*起点不是空白*：

```bash
$ ai4e show train --recipe aero_external
```

把 `standard()` 展开成第 3 档的等价代码打印出来。用户自拼时的起点是这份打印，而不是从零。这一条让第 2 档到第 3 档的跨越从「重写」变成「编辑」。

#### 这样设计的好处

1. **成本正比于改动**：50% 的用户永远不碰代码，30% 只写三行，只有 5% 需要理解全貌
2. **天花板是局部的**：黑箱封装死掉的真正原因不是它封装了，是它的逃生是全有或全无——要改一点点就得整个替换。四档让「改一点点」有对应的档位
3. **升级收益不丢失**：第 0 到 2 档的用户，core 修了 bug、改进了默认链路，`pip install -U` 就拿到了。只有第 3 档放弃这个收益，而那是他明确的选择
4. **可测量**：统计各档的使用分布。第 2、3 档超过 30%，说明标准链路划分错了，是框架的问题不是用户的问题

#### 一个反向信号

统计各 slot 被 override 的频次。**一个 slot 被 80% 的用户 override，说明它的默认实现是错的，或者边界划错了。**

正确的反应不是把某个用户的实现搬进核心，而是重新设计这个默认值甚至这个抽象。这比被动等 PR 有效得多：PR 只告诉你「有人做了这个」，覆盖率数据告诉你「你哪里做错了」。

### 13.3 输入备份：让一次运行三个月后还能原样重跑

#### 要解决的问题

一次运行的结果，取决于两样东西：**那份 config，和那些代码**。

而这两样都会变。用户第二天改了 `curvature.py` 的实现，第三周改了 config 的十几个值，第二个月 `pip install -U` 升级了 core。半年后他翻出一个漂亮的结果想复现，会发现：

- `metrics.json` 里的数字还在
- 但产生它的 config 已经被改过 20 次
- 那个自定义采样器的实现也不是当初那份了

结果目录记录了**结论**，没记录**前提**。这是「三个月后要能原样重跑」失败的根本原因。

#### 后续完整溯源设计：自动快照输入（当前已实现生效配置与源码压缩快照）

`core/run/backup.py` 在结果落盘时，把这次运行的完整输入拷进 run 目录：

```
runs/2026-09-05T14-22-01_5d7a83/
├── inputs/
│   ├── config.yaml           唯一最终生效配置，含展开变量和默认值
│   └── components/           所有 _target_ 指向项目内的组件源码
│       ├── curvature.py          （逐字节拷贝，不是引用）
│       └── my_residual.py
├── provenance.json           core/recipe 版本、git sha、env、数据集哈希
├── metrics.json
...
```

**范围**：拷贝的是「用户侧」的东西——项目内的 config 和组件源码。core 和第三方库不拷贝（那是 GB 级），改为在 `provenance.json` 记录精确版本号，配合 `requirements.lock` 可重建。

**自动，不需要用户操作。** 一个需要记得执行的备份等于没有备份。

#### 价值

1. **run 目录真正自包含**：拿到它就能重跑，不依赖用户项目还在不在、有没有被改过
2. **拷给同事就是完整的**：他不需要问「你当时用的哪版采样器」
3. **difftree 的对比有了基础**：两个 run 的差异能精确到 config 的哪一行、组件源码的哪一处，而不是只有指标差
4. **审稿可追溯**：论文里的某个数字，能定位到产生它的完整输入

#### 配套：看 core 内部实现的只读命令

备份解决「我这次跑的是什么」。另一个相关但不同的需求是「core 默认帮我做了什么」：

```bash
$ ai4e show transform.VectorAware             # 打印这个组件的源码
$ ai4e show train --recipe aero_external      # 打印 recipe 训练段的等价代码
```

这是只读的，不改任何文件。它解决两件事：

- **可审阅性**：审稿人问「你的速度场怎么归一化的」，我不能说「框架默认这么做的」，我得能看到并解释它
- **给第 3 档搭桥**：想完全自拼时，`show` 的输出就是起点，不是从空白开始

如果用户看完想改，就是普通的复制粘贴——把 `show` 的输出存成自己项目里的文件，config 的 `_target_` 改成指向它。这不需要一个专门的命令。

#### 与 explain / warnings 的配合

备份记录「跑了什么」，`show` 回答「代码是什么」，另外两个回答「哪些默认值在起作用」：

```bash
$ ai4e explain                     # 所有生效值 + 来源层
$ ai4e explain sampling.max_nodes  # 单个值的覆盖链
```

报告里自动提示（`core/abilities/report/warnings.py`）：

```
⚠ 本次运行的关键默认值风险
  · velocity 是 VECTOR 场，但 transform 使用了逐分量 Moment 归一化。
    这会破坏旋转等变性。建议改用 VectorAware。
  · test 集与 train 集的几何参数范围重叠度 18%，属于外插场景。
    请参考 metrics 中的 extrapolation 分组，而非总体 L2。
```

**这个东西的价值可能比整个装配层还大**，因为它是唯一能防止「用默认值跑出一堆自己都不知道错在哪的结果」的机制，而这恰恰是低门槛框架最大的风险。

---

## 14. 用户如何扩展自己的组件

### 14.1 要解决的问题

框架「固化」的根本原因，不是不让你加东西，是**你加进去的东西活不过两个版本**。

mmdetection 的 registry 开放性极强，但强基类加字符串注册加版本间大改，用户的自定义组件跨版本基本活不下来，最后大家 fork 整个仓库然后再也不升级。**开放性和可吸收性是两件事。**

同时有一个 to-B 的结构性问题：**企业用户不会把核心组件 PR 出来**。那是他们的 knowhow，是他们付钱的理由的反面。所以纯开源 PR 路径对工业客户是失效的。

### 14.2 一个组件从写下到被调用的完整链路

先把「零注册」这句话落到实处，走一遍全过程。

#### 第 1 步：用户写组件，不 import 任何东西

```python
# my_project/components/curvature.py
class CurvatureAdaptive:
    def __init__(self, max_nodes: int = 2048, curvature_weight: float = 1.0):
        self.max_nodes = max_nodes
        self.curvature_weight = curvature_weight

    def __call__(self, sample):
        curv = sample["curvature"]                       # 按名字取字段
        idx = weighted_sample(curv, self.max_nodes, self.curvature_weight)
        return sample.select(idx)                        # Sample 提供的方法
```

**没有装饰器、没有 registry、没有基类、没有 entry_points。** 一个普通的 Python 类。

测试它也不需要框架在场：

```python
s = CurvatureAdaptive(max_nodes=100)(my_sample)
```

#### 第 2 步：接进链路，两条路，都不写注册代码

**路径 A：yaml 里写全路径**

```yaml
sampling:
  _target_: my_project.components.CurvatureAdaptive
  max_nodes: 4096
  curvature_weight: 2.0
```

**路径 B：脚本里直接传对象**

```python
from my_project.components import CurvatureAdaptive

def build(cfg):
    return train.standard(cfg).override(sampling=CurvatureAdaptive(max_nodes=4096))
```

#### 第 3 步：框架实例化并调用

```python
# core/base/registry/resolve.py 实际做的事
def resolve(node):
    module_path, cls_name = node["_target_"].rsplit(".", 1)
    cls = getattr(importlib.import_module(module_path), cls_name)
    params = {k: v for k, v in node.items() if k != "_target_"}
    return cls(**params)          # CurvatureAdaptive(max_nodes=4096, curvature_weight=2.0)
```

```python
# recipes/aero_external/pre.py
def standard(cfg):
    return Stage(steps=[
        data.source.auto(cfg.dataset),
        data.ingest.attach_specs(cfg.fields),
        resolve(cfg.sampling),               # ← 用户的组件出现在这里
        data.offline.store(cfg.preprocess),
    ])
```

Stage 执行时就是顺序调用：`sample = step(sample)`。用户的对象只要能被这样调用，就能工作。

#### 协议在这条链路上的四个作用

**（a）规定「能被这样调用」的形状**

```python
class Sampler(Protocol):
    def __call__(self, sample: Sample) -> Sample: ...
```

用户不继承它——Python 的 Protocol 是结构化类型，形状对就行。它的作用是**告诉用户该长什么样**，以及让 mypy/IDE 能检查。见 §4.4：它不是准入门槛，级别 0 只要 `callable` 就能跑。

**（b）Sample 由协议定义，所以用户不用适配上下游**

上下游传的都是同一个 `Sample` 对象，结构由 spec 定义：

```python
sample["curvature"]                            # 取数据
sample.spec("velocity").rank                   # 取语义：这是矢量场
sample.select(idx)                             # 保持 specs 不变地筛选
sample.with_field("foo", arr, FieldSpec(...))  # 加字段必须带 spec
```

**这是数据契约最直接的价值**：用户不需要知道上游是哪个类、下游要什么格式，他只跟 `Sample` 打交道。上下游换实现，他都不受影响。

**（c）启动 5 秒内校验，而不是运行 20 分钟后 KeyError**

组件可选地声明它需要什么（一个 yaml，或类属性）：

```yaml
# my_project/components/curvature.yaml
requires:
  - {name: curvature, topology: node, rank: scalar}
  - {name: position,  topology: node, rank: vector}
preserves: all
```

`config/validate.py` 沿 Stage 顺序推演字段：

```
StageContractError: my_project.components.CurvatureAdaptive 需要 'curvature'
  (NODE, SCALAR)，但上游 data.ingest 的输出中没有。

  上游输出：position(NODE,VECTOR), pressure(FACE,SCALAR), velocity(CELL,VECTOR)
  提示：curvature 需要在 geometry 步骤计算，检查 cfg.geometry 是否启用
```

**这是协议最值钱的地方。** 声明是可选的——不写，组件照样跑，只是失去这层校验。

**（d）参数校验与缓存失效**

`registry/introspect.py` 从 `__init__` 签名抽出参数表，于是：

- config 里写了 `curvature_wieght`（拼错）→ 启动就报错，而不是静默用默认值
- `ai4e explain` 能列出这个组件的所有参数和当前值
- 组件源码哈希进入内容寻址 key → 用户改了实现，缓存自动失效

### 14.3 三级门槛

#### 第 0 级：就地指向（零门槛，覆盖 90% 场景）

就是 §14.2 走的那条路：写个类，config 里指路径，完事。

不需要注册、不需要继承、不需要 `pip install`，改完就能跑。

*为什么这一级不能省*：研究员在探索期不会为了试一个想法去建一个包。门槛必须是零，否则他会直接改 core 的源码，然后你永远不知道他改了什么。

#### 可选的辅助（不是要求）

```bash
$ ai4e new-component my_sampler --protocol sampler   # 生成骨架
$ ai4e check-component my_project/components/curvature.py
  ✓ 可调用，签名匹配 Sampler
  ✓ 参数可抽取：max_nodes(int), curvature_weight(float)
  ⚠ 未声明字段需求，将跳过启动时契约校验
```

两个命令都是可选的。不用它们，组件照样工作。

#### 第 1 级：插件包（跨项目复用、给同事、私有分发）

```toml
[project.entry-points."ai4e.components"]
curvature_adaptive = "mylib.sampling:CurvatureAdaptive"
```

`pip install` 后 `registry/discover.py` 自动发现。可以是公司内部的私有包。

#### 第 2 级：contrib（可发现性）

进 `packages/ai4e-contrib/`，明确标注不承诺 API 稳定、不进全量 CI、作者自负维护。

*为什么需要*：解决「用户能搜到、能看到别人怎么用」。没有它，好组件会散落在各人的私有仓库里。

#### 第 3 级：核心

有测试、有文档、有向后兼容承诺。

#### 晋级标准必须客观

不能靠 maintainer 心情：被 N 个 recipe 引用、有可复现的 benchmark、连续 M 个版本无 breaking change。

否则 contrib 会变成垃圾场，社区会失去往上走的动力。

#### 默认入口是 extension，不是 PR

PR 的门槛是「我要说服你这值得进核心」；extension 的门槛是「我自己能用」。**后者的转化率高一个数量级。** PR 应该是 extension 成功之后的自然结果。

### 14.4 让组件活过版本升级

**机制**：用户组件只依赖 `ai4e-spec`（甚至完全不 import），不依赖 core 的实现。core 可以疯狂重构，用户不受影响。spec 独立版本、变更需显式 review、承诺长期兼容。

**价值**：这是「我在这上面投入敢不敢」的技术答案，也是企业客户会直接问你的问题。没有它，你无法对任何人承诺兼容性。

**可验收**：`tests/contract/` 里必须有一个不 import `ai4e-core` 的用例。

### 14.5 私有插件是一等公民

**问题**：如果私有组件在框架里是二等公民——不能被 schema 校验、不出现在 `--help`、不能被 sweep、不进报告——企业用户会立刻 fork。

**怎么做**：`registry/discover.py` 对官方、contrib、私有三类来源一视同仁。

| 能力 | 官方 | contrib | 私有 |
|---|---|---|---|
| schema 校验 | ✓ | ✓ | ✓ |
| `ai4e explain` 中显示 | ✓ | ✓ | ✓ |
| 参与内容寻址 key | ✓ | ✓ | ✓ |
| 被 sweep | ✓ | ✓ | ✓ |
| 进报告 | ✓ | ✓ | ✓ |
| 随 checkpoint 分发 | ✓ | ✓ | ✓ |

**价值**：这是商业化的抓手——不是卖框架，是卖「让你的私有资产在这个框架里活得跟官方组件一样好」的能力：私有组件仓库、企业内的 recipe 分享、跨版本兼容性保障。

开源社区那条路负责生态和口碑，私有扩展这条路负责收入。**两条路共用同一套扩展机制，这必须一开始就想清楚，事后加不上去。**

### 14.6 组件的 schema：抽取加标注

**问题**：要求用户为每个组件手写 schema 是真实的摩擦，也是研究员讨厌配置系统的主要原因。但完全没有 schema，配置错误就只能在运行时暴露。

**怎么做：混合**

- **自动抽取**（`registry/introspect.py`）：从签名、类型标注、默认值、docstring 抽出结构。代码是权威，自动同步。
- **人工标注**（可选的 `component.yaml`）：单位、拓扑位置、张量阶、字段依赖。**这层信息代码里根本不存在，抽不出来。**

```bash
$ ai4e component describe my_project.components.CurvatureAdaptive

自动抽取（来自签名）：
  max_nodes: int = 2048
  curvature_weight: float = 1.0

需要确认（无法从代码推断）：
  输入需要哪些字段？    [推测] position(NODE,VECTOR), normal(FACE,VECTOR)
  输出改变了哪些字段？  [推测] 保持不变，仅减少点数
  是否保留 surface_normal？ [未知]
```

用户确认一次写进 `component.yaml`，之后契约校验就能用它。

**价值**：用户不用手写 schema，摩擦接近零；但契约校验依然能在启动 5 秒内发现问题。而「需要确认」的那几项恰恰最容易出错、最难 debug——比如上面的 `surface_normal`，丢了会在下游几百步之后才崩。

### 14.7 从脚本到组件：人工，不自动

**问题**：研究的真实起点永远是脚本。一个只能往外逃、不能往回收的框架，会持续失去用户最有价值的产出。

**为什么不做自动提取**：曾考虑过一个 `promote` 命令，用 AST 分析自动识别脚本里可提取的组件并切出来。放弃了，两个理由：

- **边界判断不可靠**：代码上的边界和研究员心里的边界经常不一致。工具切出来的东西，用户还得回头改，净成本可能是负的。
- **可靠性存疑**：「自动提取 + 自动验证数值一致」的实现成本很高，而它服务的是一个低频动作。

**改成人工，工具只做两件小事**：

```bash
$ ai4e new-component my_sampler --protocol sampler   # 生成骨架（含签名和声明模板）
$ ai4e check-component my_project/components/my_sampler.py
  ✓ 可调用，签名匹配 Sampler
  ✓ 参数可抽取
  ⚠ 未声明字段需求
```

**用户自己决定切哪里、怎么切；工具只负责「你切完之后，帮你确认它能接进去」。**

同样地，把用户的组件吸收进 contrib 或核心，也是人工审核、人工转移。不做自动化管线——那是一个需要判断力的动作，判断力不该外包给脚本。

### 14.8 最值得吸收的不是代码，是 recipe

一个用户贡献「我们厂换热器的数据 + 跑通的 config + benchmark 数字」，价值远大于贡献一个新 attention 层。因为它同时是**需求信号、验证集、别人的起点**，而且贡献门槛低得多——用户不需要写出通用代码，只需要把自己跑通的东西提交上来。

所以 recipe 的贡献通道单独开放，门槛比代码低一档：能跑通、benchmark 段填了、字段语义完整，就可以进。

### 14.9 fork 之后的漂移：doctor 怎么实现

**问题**：无论 recipe 多薄，只要是复制，漂移就会发生。用户 fork 了 `aero_external`，半年后 core 修了三个 bug、改了两个默认值，他一无所知。

**怎么做**：

fork 时，`core/tools/fork.py` 在项目里写一份来源记录：

```json
// .ai4e/origin.json
{
  "recipe": "aero_external",
  "recipes_version": "0.4.1",
  "files": {
    "config.yaml":   "sha256:a3f2...",
    "train.py":      "sha256:8b1e...",
    "pre.py":        "sha256:c40f..."
  }
}
```

doctor 时做一次简化的三方比较：`上游当前版本 ←→ fork 时的版本 ←→ 用户当前文件`

```bash
$ ai4e doctor

recipe: aero_external，fork 自 recipes 0.4.1（当前 0.6.0）

上游变更（3 项）：
  ⚠ recipe 的 post 评估分组发生结果相关变更
      边界层判据从 y+ 改为速度梯度（指标不可直接对比）
  ✓ config.yaml 默认 lr 3e-4 → 2e-4
      你已自行设为 1e-4，不受影响
  ✓ pre.py 修复面法向朝向判断
      你未修改该文件，可安全更新

你的本地改动（2 项）：
  · config.yaml    已修改（12 处）
  · components/    3 个自定义组件，不受上游影响

建议：
  ai4e doctor --apply pre.py            # 安全项，自动更新
  升级该 recipe 会改变评估分组，请手动确认
```

判断逻辑：

| 上游改了 | 用户改了 | 结论 |
|---|---|---|
| 是 | 否 | 可安全更新，`--apply` 自动合入 |
| 是 | 是 | 冲突，列出双方 diff，人工决定 |
| 否 | 是 | 用户的定制，不动 |
| 否 | 否 | 无事 |

**前置条件（必须承认的成本）**：这套机制要能用，`recipes` 发布时必须带 **per-recipe 的 changelog**，标注每次变更是否影响结果。这是一份持续的人工维护成本，不是自动生成的。

做不到这一点，doctor 只能退化成「告诉你版本差了多少，自己去看 git log」——依然比没有强，但价值大打折扣。**这是一个需要投入才能兑现的功能，不是免费的。**

**价值**：有这个命令，漂移是**可见的**；没有，它就是暗债。

它反过来还是最好的产品信号：如果 doctor 经常报出「上游改了、用户也改了」的冲突，说明那个文件本来就不该被复制走，应该推回 core。

---

## 15. 三条 CI 强制约束

**依赖方向**：`tools/check_imports.py` 强制 §2 的依赖图，任何反向 import 直接 fail。

**契约测试**：`tests/contract/` 对任意组件验证 Protocol 满足性。**必须有一个不 import `ai4e-core` 的用例**，证明 spec 自足。

**recipe 回归**：`tests/regression/` 定期跑所有 recipe，比对 `config.yaml` 的 `benchmark` 段。防止 core 的一次「改进」静默改变所有下游结果。

---

## 16. 已知风险与对策

| 风险 | 表现 | 对策 |
|---|---|---|
| 业务包变成巨型工厂 | 十几个开关参数，谁也看不懂 | 按问题类分裂，允许重复；单条链路超 30 行就分裂 |
| 用户 fork 后漂移 | 200 份副本各带旧 bug | recipe 保持极薄 + `doctor`（需 changelog 维护成本） |
| 多包版本不匹配 | viz 渲染空白页 | 跨包 schema 由 spec 定义并带 version，不兼容明确报错 |
| 默认值静默出错 | 矢量场逐分量归一化，loss 正常但丢了物理性质 | `report/warnings.py` 主动提示 + `explain` 可展开 |
| key 白名单写错 | 缓存永不命中，或用错产物 | 显式声明；`ai4e explain --cache <stage>` 打印参与哈希的字段 |
| 组件划分带气动偏见 | 第一个做瞬态/多物理场的用户撞墙 | 上线前用一个尽量不像的问题压测 slot 划分 |
| 高速迭代侵蚀严谨性 | benchmark 漂亮、客户数据崩 | 见下 |

### 关于「反复评估同一个测试集」

现象是真实的：一天试 15 个想法并用同一个 test set 选模型，等于对它做了 15 次梯度下降。半年后会得到一个在自己 benchmark 上漂亮、在客户数据上崩掉的模型（Kaggle 公榜私榜落差就是这个）。

但**强制限制评估次数会激怒用户，而且工业场景数据本来就少**，锁住一部分不让用代价太大。

所以降级为记录与提示，不拦人：

- `run/provenance.py` 记录本次用的是哪个 split
- difftree 统计每个 split 被评估过多少次
- 报告里显示：`本 split 已被评估 47 次，结论可能存在选择偏差`

**让风险可见，把决定权留给用户。** 这比强制闸门更符合研究员的实际处境。

---

## 17. 落地顺序

严格按依赖顺序，每步有明确验收。

**第 1 步：`ai4e-spec`**
交付 `fields.py` / `sample.py` / `protocols.py` / `keying.py` / `artifacts.py`
验收：组外的人不 import core，写一个采样器并通过契约测试
**这是唯一定错了要全盘返工的部分**

**第 2 步：`applications/base` + 内容寻址缓存**
验收：改模型代码，前处理缓存 100% 命中；改采样参数自动失效重跑，旧产物仍可复现

**第 3 步：一个真实业务包跑通**
交付 `applications/aero_cfd/{pre,model,train,post}/` + 完整 `aero_external` recipe
验收：**「换个采样策略」的 diff ≤ 3 行**。超了回头改前两步，不要往前走

**第 4 步：eval + report**
验收：跑完到判断好坏 ≤ 5 分钟（原来 40 分钟）

**第 5 步：`ai4e-task` difftree**
验收：能回答「上周那条分支验证的是什么假设，结论是什么」

**第 6 步：viz / server / web**

**第 7 步：`data/ingest` 接入向导**
验收：组外的人拿一份没见过的数据集，从零到第一张误差云图 ≤ 4 小时

### 最终验收（每季度重跑）

> 找一个组外的人，给他一份团队没见过的数据和一个具体的研究想法（如「把采样换成曲率自适应」），让他从零跑到出对比结果。全程录屏，计时。

这个数字会暴露所有在设计文档里看不见的摩擦点。它比任何架构评审都有用。

---

## 18. 一句话总结每个包

| 包 | 一句话 |
|---|---|
| `ai4e-spec` | 大家怎么描述同一件事——共享词汇表，不含实现 |
| `ai4e-core` | 原子能力 + 业务装配 + 执行引擎，算完并序列化，不渲染 |
| `recipes` | 问题模板，极薄，可验证，可被社区贡献 |
| `ai4e-task` | run 之间的关系——项目、difftree、假设、任务 |
| `ai4e-viz` | 只读 run 目录的渲染器 |
| `ai4e-server` | 多用户索引与协作，不是真相的所在 |
| `ai4e-contrib` | 社区组件的孵化区 |

---

## 附录 A：设计争议裁决表

| 问题 | 判据 |
|---|---|
| 进代码包还是平台？ | 产出或读取 run 目录的进代码包；跨 run、跨用户、需常驻服务的进平台 |
| 进 core 还是 recipes？ | 半年动一次进 core；每周都在加的独立成包 |
| 按能力分还是按阶段分？ | 原子按能力（跨阶段复用），装配按阶段（符合心智模型） |
| 进 yaml 还是命令行？ | 「算什么」进 yaml 并参与 key；「在哪算」进命令行不参与 key |
| 用户该复制什么？ | 薄的、属于这个问题的复制；厚的、通用的导入 |
| 扩展点开在哪？ | 开在数据流的「缝」上，不是「块」上。能替换整块 = 复制粘贴 = 分叉 |
| 抽象是否成功？ | 量 10 个真实想法的 diff 大小。超过 3 个文件说明有隐式耦合没抽干净 |
| 默认值是否安全？ | 能否被完全展开查看 + 报告是否主动标注风险 |
| 要不要加一个新协议？ | 只有当同一个形状被反复重复定义时才追认。协议是事后总结，不是事前规划 |
| 这件事要不要自动化？ | 需要判断力的动作留给人（组件切分、上游吸收）；机械且高频的才自动（备份、缓存、校验） |
| 记录放哪？ | 真相跟着数据走，服务只是索引 |

## 附录 B：长期目标的六条约束

以下为完整产品目标；本期未交付源码快照、四档 profile 和完整网格报告，当前验收范围见 `.context/mvp/abupt-acceptance.md`。

1. `pip install ai4e-core` 在无网络、无服务的 GPU 机器上能完整跑通并出结果
2. run 目录自包含：`inputs/` 里有当时的 config 和组件源码，拷给同事就能原样重跑
3. 用户组件零注册：写个普通类，config 里指路径就能用，不继承不注册不打包
4. 协议不是准入门槛：只要 `callable` 就能接进链路，协议是可选的强化
5. 四档 profile 共用同一代码路径，不存在 mode 分支
6. 私有插件与官方组件体验完全一致

## 附录 C：外部依赖的取舍

**Hydra：拆开用，不整体引入。**

| 组件 | 用不用 | 理由 |
|---|---|---|
| `omegaconf` | 用 | 合并、插值、类型转换很扎实 |
| `hydra.utils.instantiate` | 自己写 ~100 行 | 需要在解析 `_target_` 时记录源码哈希供内容寻址用，Hydra 不给这个钩子 |
| sweeper / launcher 插件 | 用，但只在 `ai4e-task` | 扫参和集群提交交给成熟工具，不自造 |
| `@hydra.main` | 不用 | 劫持入口、自动 chdir，与 python-first 冲突 |
| `defaults` 列表 | 不用 | 自成体系的 DSL，报错信息差；本仓库用单一 config 树，不需要组合 |
| 全局单例状态 | 不用 | 一个进程跑两个配置很麻烦，直接影响「单模块独立运行 + pipeline 串跑」两条路径共用 |

结论：`ai4e-core` 依赖 `omegaconf`，不依赖 `hydra-core`；`ai4e-task` 可选依赖 `hydra-core` 做 sweep 后端。核心执行路径没有 Hydra 的全局状态和目录魔法。


### 数据处理边界与长期文档

source 在入口统一为 VTK 内存表示，extract 提取具名字段，filter 生成原点序 mask，rawprep 组织原 VTK 对象与字段结果的交接；VTK/NumPy 依赖留在 core，不进入 spec。

模块功能、选择原因、恢复约定和迁移以 [原子能力 PRD](PRD/ai4e-core/abilities/PRD.md) 与 [业务装配 PRD](PRD/ai4e-core/applications/PRD.md) 为准。本节仅保留跨模块边界，不复制功能正文。

## 19. Dojo Web / Server 架构草案 v2

> 日期：2026-09-09。状态：DRAFT，供产品与架构评审。
> 本节替代会话中的 v1 平台草案；与本文旧平台设想冲突时，本节为当前设计提案。core 已交付行为不因提案改变。
> 交互和功能正文统一见 [Dojo WEB 平台产品设计](PRD/ai4e-web/src/PRD.md)，此处只定义结构、接口、所有权和实施边界。

### 19.1 v2 的主要变化与技术建议

产品入口确定为项目管理与任务工作台。左侧可收起菜单只包含项目管理、任务工作台。项目详情主视区通过六个 Tab 组合任务管理、版本树、版本比较、项目报告、文件管理和批量运行；任务工作台在内容区上方用八步横向步骤条组织页面，训练设置与训练运行独立。页面入口、前端微领域、后端限界上下文不要求一一对应。

相比 v1，补充任务／版本／运行分离、单父血缘、比较定义与文件视图、批量派生计划、CAE/DOE 接入、报告范围及步骤失效规则。保留 task 的独立研究管理与执行能力。v1 中分散在 server 的配置管理收敛为 task 的工作目录、正式版本创建记录和运行快照；server 不再维护一份脱离任务版本的可执行配置真相。

建议 Python 3.12 + FastAPI/Pydantic/Uvicorn；初期 SQLite 存元数据，通过显式仓储端口隔离。Web 建议 TypeScript + React + Vite + Ant Design + React Router，TanStack Query 管理远端缓存，React 局部状态管理交互。REST/OpenAPI 负责命令与查询，SSE 提供执行进度与日志通知。React Flow 建议用于版本树，ECharts 用于指标和训练曲线；版本布局保持血缘拓扑，不依时间顺序捏造祖先关系。

三维浏览建议以独立 ViewerAdapter 隔离：浏览器端优先 vtk.js，原始 VTKHDF/PT 经受控转换生成预览资产；大型或不支持的数据格式再接服务端渲染适配。不得宣称 vtk.js 可直接读取全部输入格式。首期选定真实数据样本验证读取、字段、色标和内存开销，之后锁定查看器版本。报告编辑保存结构化块，HTML/PDF 由独立生成作业处理。

这些是选型建议，尚未安装或锁定。工程初始化前以 ADR 确认版本、唯一依赖清单与运行方式。继续使用 uv workspace，不复制 Vis 的 requirements.txt、Python 版本或现有业务代码。

### 19.2 业务对象与唯一所有权

| 对象 | 所有者 | 身份、关系和约束 |
| --- | --- | --- |
| Project | task.projects | 研究项目，包含多个任务；归档／回收站不销毁血缘 |
| ResearchTask | task.tasks | 可编辑代码任务，属于一个项目；new/fork 创建唯一正式版本；区别于执行 Job |
| TaskVersion | task.versions | 任务创建时的完整记录，与任务一一对应；记录正式版本、直接父版本与基线版本 |
| RunRecord | task.tasks 的索引；执行结果在产物中 | 属于一个版本的一次逻辑执行，可覆盖顺序步骤；重试新建记录 |
| Job | task.tasks | 实际排队／进程尝试，属于运行或平台生成请求；不等同研究任务 |
| DatasetVersion / ArtifactRef | task.projects / task.tasks | 已登记数据和产物的稳定身份、存储引用与来源；内容由生产者生成 |
| Comparison | task.versions | 固定的版本／运行集合、量、基线与视图定义；供 CLI/API 复用 |
| BatchPlan | task.batch | 冻结 base、参数差异与执行策略，每行关联派生任务及执行尝试 |
| Report | server.reports | 范围为任务或项目；草稿、发布版本、证据块与来源引用 |

server 是 API 和服务侧协作边界，不能重复拥有 Project、TaskVersion 或 Job 聚合。task 管理记录由 task 的公开操作修改；server 不以 SQL 或 ORM 跨包访问。报告内容与服务访问策略属于 server 自有事实，需要备份；运行索引可重建，但任务工作目录、未执行版本和批量计划不能假设可以从运行目录恢复。

任务创建记录保存完整快照和可解释差异，读取不要求逐祖先应用 patch。记录 `parent_version_id`，首版不接受多父合并。工作目录编辑不增加版本；只有 new/fork 新任务才创建正式版本。运行捕获当次代码和配置；树的根可不止一个。

运行记录固定引用版本。一次运行内可顺序完成若干步骤；CAE 样本、训练进程和渲染生成可对应多个 Job。恢复检查点新建运行并记录 `resumed_from`；编辑参数或试跑不改变正式版本，研究分支由显式 fork 创建。用户指定代表运行；无指定时查询默认最近完整成功运行，保存比较／报告时将选择解析为确定 run ID。

### 19.3 包依赖与进程边界

```text
web ── REST / SSE ──> server ── 公开用例 ──> task ── 公开契约 ──> core
                         │                    │                  │
                         └────────────── spec ──────────────────┘
                                              │
                                     ExecutionBackend
                                              │
                         独立 worker / 用户执行入口 / 仿真求解器
                                              │
                          运行记录、数据集、检查点、评估和预览资产
```

箭头表示调用或导入方向，Web 的 HTTP 调用不是 Python 包依赖。spec 保持无 torch/numpy 依赖；server 只导入 spec/task；task 只导入 spec/core；core 不反向依赖平台。contrib 提供模型、数据集和未来仿真适配实现，运行入口注入组件，不由 core 硬编码导入。task 不 import recipes，但允许 ExecutionBackend 执行已登记的用户项目入口。

API 进程不执行训练、DOE 求解、网格转换或 PDF 生成。task 通过后台执行端口提交已登记入口；具体进程句柄、调度器凭证、停止操作由执行适配器处理。viz worker 通过 spec 和稳定资产读取结果，独立部署或由执行后端启动，task/server 不直接导入 viz 内部实现。

网页八步不要求构建通用 DAG 引擎。顺序工作流加明确的输入产物引用满足本期流程；现有 Stage/Pipeline 保持顺序调用。CAE/DOE 和报告是平台工作流新增步骤，通过对应执行入口衔接。

### 19.4 Server 目标代码结构

```text
packages/ai4e-server/                 # 包根兼 Python 源码根 → ai4e_server
├── README.md / pyproject.toml / __init__.py
├── bootstrap/                       # app、依赖注入、模块路由与生命周期
├── modules/
│   ├── projects/                    # 项目管理 API
│   ├── tasks/                       # 任务、工作目录与工作台配置 API
│   ├── lineage/                     # 版本发布、fork、血缘查询 API
│   ├── executions/                  # 运行／Job 提交、停止、恢复、SSE
│   ├── assets/                      # 文件、数据集、产物与内容访问 API
│   ├── comparisons/                 # 保存比较、跨版本查询与视图请求
│   ├── batches/                     # 批量计划预览、执行与结果 API
│   ├── reports/                     # 服务自有报告领域
│   └── capabilities/                # 可用阶段、模型、求解器、资源与预览能力
└── infrastructure/
    ├── persistence/                 # 服务自有数据的连接／事务原语
    ├── storage/                     # 受控内容传输与服务报告存储
    ├── transport/                   # HTTP 错误、身份上下文、SSE
    └── observability/               # 请求、诊断和关联标识
```

边界沿用 Vis 的模块优先思想，先按业务上下文，再按实际规模分层：

```text
modules/reports/
├── __init__.py                      # 业务用例与必要类型门面
├── api.py                           # HTTP / 错误映射
├── schemas.py                       # 入出站 DTO
├── application.py                   # 用例、事务与证据协作
├── domain.py                        # 报告范围、发布规则和纯不变量
├── ports.py                         # 仓储、证据查询和生成端口
└── adapters/
    ├── repository.py                # 本模块表与映射
    └── task.py                      # task 公开能力适配
```

仅代理 task 的简单模块只需 api/schemas/application 和公开入口，不创建重复 Domain 或 Repository。Application 依赖 Domain/ports，适配器实现端口，由 bootstrap 注入；Domain 不依赖 Web、数据库和文件系统。跨模块只通过 `__init__.py` 暴露的用例与契约，不导出低层 SQL 操作来绕开聚合。

### 19.5 Task 的代码与本地项目边界

2026-09-09 决策：task 是可安装的功能模块化 Python 包，不采用 DDD 分层；Server 的轻量 DDD 不向 task 套用。Python API 和 ai4e CLI 调用同一实现。

```text
packages/ai4e-task/
├── cli/          # 命令解析、公开用例调用及输出
├── projects/     # 项目身份与 shared 资产
├── tasks/        # new/fork、任务查询、本地执行和运行导入
├── versions/     # 正式版本记录、单父血缘树与比较
├── templates/    # 用户模板登记与文件展开
└── storage/      # SQLite、文件事务、快照与产物读取
```

只有 new/fork 创建正式版本，一个任务对应一个版本。任务工作目录可以持续编辑，没有草稿、冻结、发布步骤。创建快照不可变；run 是该任务的一次测试记录，捕获实际执行代码和配置，不增加正式版本。正式版本比较默认比较创建记录，当前工作目录比较和固定 run 比较使用独立入口。父来源与比较基线分开保存，fork 默认来自父工作目录，也可选择创建快照或固定运行快照，不要求 Git 仓库。

```text
project/
├── project.json
├── .dojo/task.sqlite
├── shared/<资产名称>/asset.json + content/
└── tasks/<task_id>/
    ├── task.json
    ├── recipe/
    ├── .dojo/snapshots/ + executions/
    ├── assets/<资产名称>/asset.json + content/
    ├── data/<run_id>/
    └── runs/<run_id>/
```

shared/datasets 下可以按数据集名称继续分组；其他资产直接按名称登记。未复制资产保留引用，显式复制资产附带来源和摘要。数据集、准备产物、检查点复制选项独立且默认关闭；复制权重不等于续训。fork 不复制历史 runs，新输出不覆盖父任务或 shared。

管理记录使用 SQLite 与具体文件操作，不预建 Repository、UnitOfWork 或端口层。写事务串行化 new/fork，文件先暂存、校验并提升，再发布数据库引用；幂等键拒绝不同请求复用。recover_project 清理由中断创建留下的未登记任务和临时目录，不假设运行目录能恢复所有管理事实。

模板是普通目录，通过 task-entry.json 显式声明脚本、配置、输入资产类型、输出路径绑定及可选指标语义。task 不猜测案例字段，不导入 recipes；子进程执行捕获的用户代码，通过 core 公共 managed_run 交接。RunContext 在 spec 定义，core writer 独占运行配置、来源、代码快照和摘要写入。启动失败也保留来源；task 控制收据留在 executions，不回写 run。

本地停止需核对进程身份，控制端重启后先核对进程和完成收据；无法核对时标 unknown，不自动重复启动。运行导入核对 ID 和内容摘要，旧记录无版本时标来源未知。core 旧独立入口保持兼容。

安装使用单层 Hatchling 映射，分发名 ai4e-task、导入名 ai4e_task；提供 ai4e 和 python -m ai4e_task，管理命令延迟加载训练依赖。远程执行、批量计划及 Web/Server 实现不在此切片。

### 19.6 Web 目标代码结构

```text
packages/ai4e-web/
├── README.md / package.json / package-lock.json / index.html
├── src/
│   ├── main.tsx
│   ├── app/
│   │   ├── App.tsx / router.tsx / moduleRegistry.ts
│   │   ├── pages/                  # 跨领域页面装配，不拥有业务逻辑
│   │   │   ├── ProjectDetailPage.tsx
│   │   │   └── TaskWorkbenchPage.tsx
│   │   └── workflows/              # 选版本→比较、证据→报告等跨域组合
│   ├── modules/
│   │   ├── projects/               # 项目导航、详情头与项目信息
│   │   ├── tasks/                  # 任务列表、任务选择与工作台上下文
│   │   ├── lineage/                # 版本树、差异和节点选择
│   │   ├── comparisons/            # 比较清单、表格、趋势与多窗口
│   │   ├── files/                  # 项目文件浏览、搜索和详情
│   │   ├── batches/                # 多 base 计划表与批量进度
│   │   ├── sampling/               # CAE 模型、DOE 与样本执行
│   │   ├── rawprep/                # 原数据浏览、清洗、校验和提取
│   │   ├── trainprep/              # 输入绑定、归一化、转换与训练采样
│   │   ├── modeling/               # 模型、学习目标与优化器编辑
│   │   ├── training/               # 训练设置与独立运行步骤、监控、恢复
│   │   ├── post/                   # 推理、评估与任务内三维结果
│   │   └── reports/                # 任务／项目报告共用，按 scope 区分
│   └── infrastructure/
│       ├── http/                   # HTTP / SSE 通用客户端
│       ├── contracts/              # OpenAPI 生成类型，只读依赖
│       ├── components/             # 无业务基础组件
│       ├── rendering/              # 图表、版本图、Viewer 技术适配
│       └── theme/                  # 主题和基础样式
├── scripts/                        # 架构检查
└── e2e/                            # 跨页面流程验收
```

项目详情由 app 组合六个 Tab 的公开业务组件；任务工作台组合 tasks 上下文和八步公开组件。它们是应用壳组合页面，区别于禁止的全局业务 pages：不持有草稿规则、不请求 Endpoint、不实现训练配置逻辑。

微领域按需具有 `index.ts`、`module.ts`、`model.ts`、`api.ts`、`hooks/`、`components/`、`pages/`、`tests/`。`index.ts` 是唯一跨模块门面；`module.ts` 只声明路由、导航或工作台步骤元数据。组件读取本领域 Hook，Hook 调用本领域 API；API 集中 Endpoint 与 DTO 转换。infrastructure 不导入任何业务模块。

tasks 维护可执行工作目录的规范状态和修改命令，各步骤通过工作台注入的受限接口编辑自己的配置片段；领域内可以维护未提交表单。优化器虽展示在 modeling 中，仍映射到同一份训练配置，training 不保存第二份副本。前端字段映射和后端最终配置解析由契约测试验证。

lineage 右侧以所选任务为上下文切换阶段及输入／输出／参数，不另设版本切换；用户勾选量后加入比较参数，再显式跳转。lineage/files/post 只发出包含固定引用的“加入比较”或“加入报告”意图，app/workflows 调用 comparisons/reports 门面，避免相互导入内部文件。比较清单由 comparisons 拥有，URL 记录 project/task/version/comparison 等导航标识；刷新页面恢复选择时重新校验访问与对象状态。

比较工作区采用左侧大尺寸表格／趋势／三维可视化入口，各页内置比较清单与属性。三维和后处理共用 ParaView 风格 ViewerAdapter：管线、属性、过滤器、相机、可动态增减视图；后处理另有指标与图表。八步均通过同一预览弹窗访问文本、表格和三维资产。项目与文件页的搜索、筛选、排序归各自微领域状态，文件版本选择置于左上方筛选区。

### 19.7 八步与既有算法能力的衔接

| 用户步骤 | 当前衔接点或新增能力 | 执行及配置边界 |
| --- | --- | --- |
| 数据采样 | 新增 DOE 策略和 CAE 求解器适配 | DOE 产生方案；ExecutionBackend 调度求解器；不能用训练点采样冒充仿真 DOE |
| 原数据处理 | applications/aero_cfd/rawprep | 用户步骤对应当前 datapre 入口；不重命名现有运行配置键 |
| 数据准备 | applications/aero_cfd/trainprep | 冻结身份、归一化和采样／拼批声明；在线采样继续在训练迭代执行 |
| 模型设置 | applications/aero_cfd/model | 模型与监督目标装配；物理约束待扩展，优化器 UI 不改变算法归属 |
| 训练设置 | applications/aero_cfd/train | 预算、调度、监控、回调和检查点策略配置 |
| 训练运行 | task.tasks + applications/aero_cfd/train | 最终解析、优化器创建、资源调度、训练与运行监控；新增用户步骤不复制训练循环 |
| 后处理 | applications/aero_cfd/post；未来 viz worker | 当前已有权重恢复、评估、张量和网格输出；浏览器查看与预览转换待新增 |
| 报告 | server.reports + 独立生成作业 | core report 仅占位，报告编辑、组织与发布需新实现 |

能力接口按工作流和可执行操作声明支持情况，不自动枚举每个 Python 函数。模型和 callback 使用已登记组件选择，不允许浏览器提交任意 Python 代码作为接口执行。

训练前仍执行现有冻结契约检查。步骤依赖签名包含配置片段、输入内容摘要、组件版本、随机种子及输出契约；无法证明一致时视为需要重新执行。产物失效仅作用于当前工作目录，历史运行记录不可变。

### 19.8 比较、预览与报告契约

spec 只承载跨包稳定、可序列化的 VersionRef、RunRef、ArtifactRef、QuantityRef 和 ViewSpec 等契约；具体名称在实现时与现有契约整理，不能因本节类型名创建重复表示。HTTP DTO 留在 server，Web 从 OpenAPI 生成传输类型并在 api.ts 转成领域模型。

QuantityRef 至少表达量的语义名称、物理域、归属、分量、单位、分片／样本与统计定义。ArtifactRef 表达资产 ID、内容摘要、类型、来源版本和运行；存储定位留在受控端。Comparison 固定对象引用、所选运行、基线、显示模式与 ViewSpec，不能只存文件名或“最新版本”。

比较查询返回每个版本的值或资产引用，并返回 available/missing/incompatible/pending 及原因。可视化层只做显示转换，单位换算规则明确；误差计算、统计聚合和跨网格插值归计算执行层。对齐操作产生独立结果资产，保留输入与算法记录。

ViewSpec 保存字段、分量、时间步、相机、色标、切片和联动组；浏览器预览缓存按内容摘要与视图请求区分。ReportBlock 引用固定 Comparison 或 Artifact 与 ViewSpec，同时存发布快照。Report 的 scope 为 project 或 task，避免实现两套编辑器和发布机制。

### 19.9 API 与持久化

建议统一 `/api/v1` 前缀，按业务组织命令与查询：

- projects：项目列表／详情／管理状态；tasks：任务创建、查询与工作目录读取／保存。
- versions：创建记录、详情、fork、血缘与差异；runs：状态、阶段、指标与日志。
- executions：提交、停止和恢复；capabilities/resources：可用入口、模型、求解器和资源摘要。
- assets：项目文件查询、来源、预览和受控内容访问；comparisons：创建、修改、解析量及视图请求。
- batches：计划展开、冻结、执行、逐行结果与失败重试；reports：草稿、证据块、发布和导出。

任务文件编辑不创建版本；未来服务侧编辑使用 revision 乐观并发控制。提交、fork、批量执行采用幂等键。输入缺失、版本不兼容、状态冲突和资源不可用返回稳定业务错误码与可定位字段。API 不泄露求解器凭证或本地绝对路径。

提交先持久化 Job 意图及幂等映射，再由后台调度。崩溃恢复用相同提交身份查询执行端后再决定是否重提；执行端不能幂等时标为状态待核对，不盲目再启动一个训练进程。SSE 使用事件序号和快照恢复；事件暂缺时保留未知／待核对状态，不误报失败。

task 元数据与 server 元数据分开所有权，可使用各自 SQLite 文件；连接和表迁移由各包基础设施装配，模块提供自身迁移。跨包不使用跨库事务；报告发布通过固定引用及保留策略保证证据存在，失败时不发布半成品。

运行根、数据根、平台元数据根、报告／预览根独立配置。core 的运行记录由 writer 写，数据由 save 写；task/server 只索引和读取，不回写训练日志和检查点。服务生成报告或预览写自己的产物区域并登记，不能写入已有训练 run 目录。

### 19.10 批量派生与资源执行

BatchPlan 的每行固定 base_version_id、参数 patch、展开后的完整配置摘要、种子、资源和执行范围。默认笛卡尔积、默认单任务并发；显式配对需校验行数。预览阶段完成所有 base 的参数检查，禁止运行时再猜缺失字段。

plan_id + row_id 标识派生操作；创建子任务、版本与计划行关联在 task 事务内完成。提交执行采用独立幂等作业意图，失败重试不重新创建子任务。计划整体报告逐行计数与部分失败；停止计划取消未启动项并向运行项请求停止，等待实际确认。

完整运行默认从所选流程入口开始。复用上游是显式策略，必须命中输入／配置／组件／产物一致性检查并记录来源；不得将“复制 base 文件夹”作为继承语义。报告中保留本次计算与引用复用的区别。

### 19.11 规范与文档治理

实际源码继续落在 packages/ai4e-server 和 packages/ai4e-web。不在本次设计文档交付中初始化工程、安装依赖或创建空模块。

- `.cursor/rules/ai4e-backend-ddd.mdc` 保留 task/server 共性规则；实施时新增 `ai4e-server-architecture.mdc` 明确上述服务端模板。扩充现有 `ai4e-web-architecture.mdc`，不并存两套前端规范。
- 规则需要检查公开门面、Domain 纯净性、所有权、按需分层、中文模块说明和公开 API 文档，以及配置来源、状态语义、错误处理与相关测试。
- AGENTS 维护入口和强制边界；.context 维护当前路径、职责、设计状态和测试入口，不复制本节架构正文。
- 本次产品设计按未来源码一级 src 归入 `docs/PRD/ai4e-web/src/PRD.md`，是用户明确要求的设计稿，标为 DRAFT。这是对“未交付不建空 PRD”规则的有内容设计交付，不代表 Web src 已存在。
- server 的功能 PRD 按 `modules/PRD.md` 归档；task 按六类一级目录各自维护 PRD；Web 产品交互仍以现有产品设计为唯一正文。技术路径和契约细节不复制进 PRD。
- 技术栈与 task 配套重组在实施前形成 ADR；原有 CLI/recipe 入口、包导入边界和正式训练验收不因平台引入改变。

### 19.12 分期与验收场景

1. 先完成项目／任务／不可变版本、已有数据入口、训练准备到 post 的真实短训、文件和执行状态闭环；首个数据集采用当前已验收案例。
2. 增加版本树、标量／曲线比较、三维预览与多窗口、任务／项目报告，固定证据引用并验证渲染数据契约。
3. 增加多 base 批量计划和 CAE/DOE 接入；批量执行可先基于已有数据训练，DOE 按求解器逐个验证。多用户认证与远程资源在部署扩大前单独交付，初期本机可信工作台默认只监听回环地址。

以上顺序不删减目标功能，界面按真实能力显示支持范围。版本身份、引用和执行契约从第一期确立，避免后续重建数据模型。

实施时按影响圈定测试：

- task 领域：创建记录不可变、fork 完整继承、多根／多层血缘、并发创建幂等、编辑和重试不生新版本、停止确认与删除引用保留。
- 批量契约：多 base 展开、非法参数、幂等重试、创建成功但提交中断、部分失败、失败项重试、复用签名失效。
- 比较契约：跨分支不连假曲线、同名不同单位／分片不可误比、缺失不归零、零基线差值、网格身份不一致禁止直接差值、固定 run 的比较不随最新结果漂移。
- 资产与报告：路径访问边界、引用中资产不能清除、报告冻结证据、未知格式降级、单窗口失败隔离、PT 受控读取和大文件取消。
- API／Web：工作目录保存到训练生效值一致、断线与训练状态分离、SSE 重新同步、从树／文件进入比较和报告、八步回看及工作目录修改后的下游失效。
- 真实集成：已有数据 → rawprep → trainprep → train → post → 文件／指标查看；CAE/DOE 与三维／报告分别使用真实适配器验收，替身只验证端口。
- 架构门禁：Python import 边界、跨模块门面、Domain 禁止依赖框架；Web 内部导入与基础设施反向依赖检查。仅文档更新验证链接、章节、需求覆盖和状态描述，不以训练测试冒充新平台验收。

### 19.13 本次核对依据与当前缺口

本稿参考 Vis 的 AGENTS、后端／前端 rules、实际 dataAssets 的 API/Application/公开门面，以及前端 api/index/moduleRegistry。采用模块优先和公开门面思想，不复制其 Application 引用 HTTPException 或门面导出 Repository 操作的具体做法。

Dojo 当前核对了 rawprep/save.py 的 PT 与可选 VTKHDF/实体关联交付，trainprep/preparation.py 的冻结数据摘要与准备，model/objectives.py 的监督目标，以及 train/fitting.py 中优化器和 callback 装配。abilities/report 仅含占位文件；server/web 尚未建立可运行平台；task 的本地切片验收见 .context/mvp/task-acceptance.md。源码静态核对不证明本稿新功能可执行，正式模型等价性仍只引用现行专项验收证据。

## 20. 外流双模型组件边界

同一 aero_cfd recipe 通过全限定路径选择数据组件、模型组件和领域标准装配。contrib 负责来源格式、字段含义、模型布局和专用全表面推理；spec 定义轻量读取、描述与预测约定。core 能力提供原子提交、统计、更新、评估和网格导出，领域 application 串接准备、训练及后处理；公共训练循环不按模型名称分支。未声明组件时保持汽车组件选择及原构造器身份；公开旧配置树的兼容政策与组件缺省分别处理。

样本身份是来源、分片与样本编号的组合，计算项追加块和点索引。阶段交付冻结输入声明与内容摘要；数据产物由 save 写入，运行来源和部分交付由 writer 写入。独立推理复用需验证数据、权重、变换和块完整性，模型状态缓存仅在样本范围生存。两类示例的实际验证状态由验收索引登记；完整规模对标是接入完成门槛；当前正式数值结果通过，旧公开配置兼容政策仍待确认。


## 案例配置与运行快照边界（2026-09-09）

案例以 rawprep/trainprep/model/train/post 五段表达用户输入，configuration.py 负责默认展开、路径解析与向既有 application 参数的映射。rawprep 案例函数可以调用库 datapre 方法；文件名不构成库接口约束。

run.launch 接收通用 config_loader，writer 保存启动时最终配置快照；内部调用参数不回写用户配置。实际数据来源与分片进入运行报告，准备和检查点引用进入业务产物。检查点附带同一份用户快照；原子能力、模型、训练和既有产物版本不随配置分组变更。
