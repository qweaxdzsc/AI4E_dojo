# AI4E_Dojo 仓库结构索引

- `docs/prototypes/dojo-rawprep-detail.html`：原始数据处理独立细节原型；已落盘文件统一浏览、字段选择与输出计划、文本／张量／三维弹窗。`tests/integration/rawprep_detail_browser.cjs` 检查对应交互。

## Web 平台设计入口（DRAFT，2026-09-09）

- 原型 v3 按用户四张 `docs/prototypes/*.png` UI 参考图调整，并映射实际 aero_cfd application/recipe。参考素材与能力来源见 web 模块索引；仅 UI 示意。

- `docs/prototypes/dojo-web-wireframe.html`（左侧仅两个一级入口，项目六 Tab 位于主视区）：独立离线 HTML 交互线框，示意页面布局和跳转；未初始化正式 Web 工程。
- `tests/integration/web_wireframe_browser.cjs`：本地 Playwright 浏览器交互检查，覆盖版本比较、报告、文件预览、批量派生和工作台；复用外部测试运行时，不新增平台依赖。

- [Dojo WEB 平台产品设计](../docs/PRD/ai4e-web/src/PRD.md)：项目管理六个 Tab、八步工作台、跨版本比较与批量派生的待评审产品正文；不代表源码已实现。
- [Web / Server 架构 v2](<../docs/AI4E_Dojo_ARCHITECTURE (1).md#19-dojo-web--server-架构草案-v2>)：唯一架构正文第 19 节，定义 task/server/web 职责、版本与运行契约及目标目录。
- `tests/integration/test_web_design_documents.py`：产品与架构设计稿本地链接、章节和来源引用的相关文档检查。

server/web 模块索引登记设计入口；server/web 仍为 PLANNED，task 本地实施见 task 模块索引，未来模块目录以架构稿为提案，不作为已存在目录树。

当前端到端验收（2026-09-09）：默认 recipe 为 rawprep → trainprep → train → post。冻结变换组合、点场整理与分块查询归 abilities；aero_cfd application 负责业务绑定。独立 post 默认从配置种子沿 global 流采样，隔离锚点/网格两路；兼容张量包、点云与表面原始身份已对齐。实跑规模、数值证据及范围见 `.context/mvp/abupt-end-to-end-acceptance.md`。



当前训练对齐切片：用户入口为 rawprep → trainprep → train。准备交付冻结数据摘要、归一化记录和采样/拼批声明；训练消费前校验。模型结构版本 3 修正 RMSNorm、绝对位置编码器、联合投影与初始化顺序，版本 2 权重不支持直接续训。完整官方等价性必须以 `.context/mvp/abupt-reference-acceptance.md` 的实际证据为准，不能用旧小模型验收替代。

多域 AB-UPT 使用结构版本 3：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。


当前实施状态（2026-09-08）：已交付五类业务、归一化与采样、正式 AB-UPT、训练评估与轮次恢复、可选归一化物化及 VTKHDF/PT 关联、监督比较方法、训练闭环剩余对齐，以及 post 锚点推理（只恢复权重、test 集评估、逐样本保存、可选锚点点云）与完整网格回贴。训练设备默认按 CUDA/MPS/CPU 选择，找不到加速器时警告后回退 CPU；MPS 默认两轮复制案例已实测，范围与结果见 `.context/mvp/framework-correctness-acceptance.md`。物理约束未进。验收范围、逐项用例与执行结果以 `.context/mvp/abupt-acceptance.md` 为准；云图、报告及生产规模训练不在本期验收范围。

本文件是 LLM 每次进入仓库时使用的首要结构入口。先在这里确定功能所属模块，再进入对应模块索引；不要先通读整个仓库或架构长文。

## 当前状态

仓库已建立 uv workspace（`ai4e-spec` / `ai4e-core` / `ai4e-contrib`）。**本切片已交付**：通用下载与多包解压、读取前校验、VTK 家族/NPY 统一 VTK 内存适配、从 VTK 内存对象抽出场量、按单元类型生成有效点 mask、点到最近表面顶点 / 点到网格表面 / 表面法向、体积重合点标记与点数校验、具名场编码与按对照表落盘/读回、规范化预处理根与官方分片、打开样本并派生表面距离、外流 pre 单样本业务步骤、run 批量执行与统计量、外流 train 选定 AB-UPT 与作业级读盘探测，并支持显式准备和正式训练、最小 Stage/Pipeline、run 开车、批量执行与唯一写入，以及 aero_cfd 案例前处理与训练准备入口、监督比较方法（均方误差、平均绝对误差、Huber、相对 L2）。物理约束未进。默认 `pipeline.stages` 为 `rawprep/trainprep/train/post`。不做 VTK 压力对 `press.npy` 的对照，也不自动下载官方包。Dataset 按需执行、产物 manifest、训练清单读盘和三级日志已交付；归一化准备已实现，内容缓存仍为规划。其余目录存在只表示规划位置，不表示规划能力已经交付。

## 查询顺序

1. 从下方仓库目录树判断目标属于治理、正式包、测试、文档、工具还是历史材料。
2. 正式包进入对应的 `.context/modules/*.md`，查询模块内目录和文档含义。
3. 按 package 分类读取算法、后端或前端规则；AB-UPT 纵向流程同时进入 `.context/mvp/abupt-mvp1.md`。
4. 只读取任务相关的源码、文档与测试；需要设计理由或架构决策时再读 `docs/AI4E_Dojo_ARCHITECTURE (1).md`。

## 仓库目录结构

```text
AI4E_Dojo/
├── AGENTS.md                 # LLM 工作入口、依赖边界、索引维护与修改验收纪律
├── README.md                 # 面向使用者的项目概览与当前状态
├── pyproject.toml            # uv workspace 与开发依赖
├── .context/                 # 面向 LLM 的仓库与模块级检索索引
│   ├── index.md              # 本文件：全仓目录结构入口
│   ├── modules/              # 正式包及普通模板的模块级目录/文档索引
│   └── mvp/                  # 纵向 MVP 的范围与链路索引
├── .cursor/rules/            # 按作用域加载的开发和治理规范
├── packages/                 # 正式产品代码
│   ├── ai4e-spec/            # 稳定数据、组件与 artifact 契约；本切片不交付字段契约
│   ├── ai4e-core/            # 原子能力、业务装配和运行产物
│   │   ├── abilities/data/source/download/  # HuggingFace、网址、多包解压
│   │   ├── abilities/data/source/read.py    # 校验 + 选适配器 + 单文件/多文件/递归
│   │   ├── abilities/data/source/adapter/   # VTK 家族、NPY 统一 VTK 内存读取
│   │   ├── abilities/data/extract/          # 从 VTK 内存对象抽点坐标与具名点/单元字段
│   │   ├── abilities/data/filter/           # 有效点 mask、重合点标记、套对齐 mask
│   │   ├── abilities/data/validate/         # 点数对齐与写出计划
│   │   ├── abilities/data/save/             # 具名场记录、编码为张量、按逻辑名写/读 .pt
│   │   ├── abilities/data/source/split.py   # 按传入名单列分片，不扫盘
│   │   ├── abilities/data/stats/            # 统计量读入、累计矩、按训练分片重算
│   │   ├── abilities/geometry/              # surface.py 公共门禁/身份映射；距离、法向及有效性 mask
│   │   ├── base/events.py                   # 阶段上下文、能力事件与继承上下文的心跳
│   │   ├── base/config/                     # OmegaConf 加载案例 YAML 与点号覆盖
│   │   ├── applications/base/               # 最小 Stage / Pipeline
│   │   ├── applications/aero_cfd/rawprep/       # 外流 pre：read/derive/select/save/stats 五个业务模块
│   │   ├── applications/aero_cfd/trainprep/ # 项目读盘、准备与冻结变换
│   │   ├── applications/aero_cfd/model/     # 贡献模型、权重冻结和学习目标
│   │   ├── applications/aero_cfd/post/      # 锚点评估保存、可选点云与完整网格回贴
│   │   ├── applications/aero_cfd/train/     # 训练装配、默认展开、监控、检查点和轮次恢复
│   │   └── run/                             # 开车、最终生效配置、源码快照、运行日志与唯一写入
│   ├── ai4e-task/            # 六类功能模块：项目、任务版本、资产、CLI 与本地执行
│   ├── ai4e-viz/             # 稳定 artifact 的可视表达（PLANNED）
│   ├── ai4e-server/          # 协作与稳定服务 API 占位
│   ├── ai4e-web/             # Web 交互层占位
│   └── ai4e-contrib/         # 可安装的共享数据集适配
├── recipes/                  # 可复制的 config/datapre/trainprep/train/post/pipeline/README，无包安装
├── docs/                     # 使用文档、权威架构、ADR 和 PRD
│   ├── AI4E_Dojo_ARCHITECTURE (1).md # 唯一权威架构文档
│   ├── architecture/         # 架构文档导航，不复制架构正文
│   ├── adr/                  # 已决定架构事项及其理由
│   └── PRD/                  # 先按 package、再按包内一级模块分文件的产品说明
│       ├── README.md         # PRD 书写规范与模块对照
│       ├── ai4e-core/base/PRD.md           # 配置与能力事件
│       ├── ai4e-contrib/application/PRD.md  # 共享数据集适配
│       ├── ai4e-core/abilities/PRD.md      # 原子能力；数据章含物化与统计量，几何章两种距离分开
│       ├── ai4e-core/applications/PRD.md   # 业务装配；外流 pre、train 与最小阶段盒子
│       ├── ai4e-core/run/PRD.md            # 开车、日志与运行目录写入
│       └── recipes/aero_cfd/PRD.md     # 案例字段映射、几何启用、前处理与训练准备入口
├── examples/                 # 后续可运行示例
├── tests/                    # contract、integration、regression
│   └── integration/          # 下载/读取/提取清洗/几何/落盘/案例入口/训练读盘/剩余对齐；有网或有本地数据才跑真实冒烟
├── tools/                    # 仓库维护工具，不承载框架运行逻辑
├── user_project/             # 历史 ShapeNet-Car/AB-UPT 验证资产
└── dos/                      # 历史设计稿和调研附件
```

`.venv/`、`.DS_Store`、运行缓存与输出不是代码结构，也不是查询入口；不得加入模块 API 索引。

`packages/` 下采用单层包目录：业务子目录直接位于 `packages/ai4e-*/`，不得再创建 `ai4e_*` 同名内层。根 `pyproject.toml` 与各包 hatch 配置把连字符物理目录映射为下划线导入名。

## Package 结构原则

- **算法原则** — `ai4e-spec`、`ai4e-core`、`ai4e-contrib`、`ai4e-viz`、`ai4e-contrib`：按权威架构文档中的 base、abilities、applications、Stage 和 Artifact 分层，保持高内聚、低耦合，不套 DDD 目录。
- **后端原则** — `ai4e-server`：围绕业务生命周期采用轻量 DDD，先按限界上下文组织，再在上下文内部按需分层。
- **前端原则** — `ai4e-web`：按用户任务组织微领域，每个领域自治，只消费稳定 API 或 Artifact schema。

修改 package 前先进入其模块索引，再读取下方对应代码规则；三类结构原则不得混用。

## 正式包导航

- [`ai4e-spec`](modules/ai4e-spec.md)：`packages/ai4e-spec/` 的目录、文档、契约职责与依赖。
- [`ai4e-core`](modules/ai4e-core.md)：`packages/ai4e-core/` 的 base、abilities、applications、run 和 tools 目录索引。
- [`recipes`](modules/recipes.md)：`recipes/` 的普通脚本模板与运行入口。
- [`ai4e-task`](modules/ai4e-task.md)：`packages/ai4e-task/` 的六类代码目录与本地验收入口。
- [`ai4e-viz`](modules/ai4e-viz.md)：`packages/ai4e-viz/` 的 render 和 compose 位置。
- [`ai4e-server`](modules/ai4e-server.md)：服务层占位、允许依赖和文档入口。
- [`ai4e-web`](modules/ai4e-web.md)：Web 层占位、边界和文档入口。
- [`ai4e-contrib`](modules/ai4e-contrib.md)：贡献数据集与完整模型、许可和文档入口。

## 跨模块入口

- [`AB-UPT MVP1`](mvp/abupt-mvp1.md)：ShapeNet-Car preprocess → train → checkpoint → inference → postprocess → eval/report 的首个闭环。
- [`算法代码规范`](../.cursor/rules/ai4e-algorithm-architecture.mdc)：修改 spec/core/recipes/viz/contrib 时读取。
- [`后端 DDD 规范`](../.cursor/rules/ai4e-backend-ddd.mdc)：修改 task/server 时读取。
- [`前端微领域规范`](../.cursor/rules/ai4e-web-architecture.mdc)：修改 web 时读取。
- [`权威架构设计`](<../docs/AI4E_Dojo_ARCHITECTURE (1).md>)：需要理解设计原因、全局链路或作出架构变更时按需读取。

## 文档与验证入口

- `docs/PRD/recipes/aero_cfd/PRD.md`：ShapeNet 显式启用四项几何，已有数据根与薄前处理入口。
- `docs/PRD/README.md`：PRD 书写规范与模块对照。
- `docs/PRD/ai4e-core/abilities/PRD.md`：core 原子能力产品说明；数据章含下载/读取/适配/提取/清洗/套 mask/物化/读回/分片/统计量，几何章写清两种距离。
- `docs/PRD/ai4e-core/applications/PRD.md`：core 业务装配产品说明；外流 pre、train 与最小阶段盒子。
- `docs/PRD/ai4e-core/run/PRD.md`：开车、运行日志与运行目录唯一写入；摘要可抄训练探测字段。
- `docs/quickstart.md`：前处理与训练模板上手导航。
- `docs/data_onboarding.md`：旧接入说明的跳转入口；功能、设计原因和迁移统一见上方两份模块 PRD。
- `docs/extending.md`：未来组件扩展边界。
- `docs/architecture/README.md`：架构文档导航。
- `docs/adr/0002-aero-cfd-workflow.md`：五类业务、贡献模型与分段交付决策。
- `docs/adr/0001-repository-boundaries.md`：当前仓库依赖边界决策。
- `examples/README.md`：示例目录状态与收录标准。
- `tests/README.md`：测试层次和本切片相关用例。
- `tools/README.md`：仓库维护工具边界。

## 依赖方向

```text
ai4e-spec
   ↑
ai4e-core
   ↑           ↑          ↑
recipes      task        viz
               ↑
            server → web
```

`contrib` 通过与私有插件相同的组件契约接入，不取得跨层特权。

## 现有材料边界

- `../user_project/`：历史脚本、输出和工作台，只作迁移证据，不是正式包或框架 API。
- `../dos/`：来源材料，不作为当前架构真源。
- `/Users/zonghui/work/new_code_project/AB-UPT/`：锁定模型来源参考；正式运行使用已安装 contrib 模型。
- `/Users/zonghui/work/new_code_project/noether/`：行为参考，不允许成为新 packages 的依赖。

## 索引同步规则

- 新增、删除、移动顶层目录或跨模块入口：更新本文件。
- 改变包内目录或文档：更新对应 `.context/modules/*.md`；若影响模块职责或入口，同时更新本文件。
- 架构设计发生变化：更新 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 或新增 ADR，再同步这里的路径和一句话摘要。
- 索引描述当前可验证状态；不得把规划目录写成已实现功能。

- [本期逐项验收](mvp/abupt-acceptance.md)：A1–I4 对应测试节点、命令、结果与硬件范围。

- [多域模型逐项验收](mvp/abupt-multidomain-acceptance.md)：A1–F3、参考夹具、CPU 多样本与缓存查询。

## 官方参考对照工具

`tools/verification/` 包含 `compare_datapre.py`、`compare_trainprep.py`、`compare_abupt.py`、`compare_full_updates.py`、`compare_training.py`、`state_mapping.py`、`reference_env.py`、`run_noether_reference.py`。仅验收工具可导入本地 Noether；正式包不依赖它。结果与命令见 `.context/mvp/abupt-reference-acceptance.md`。

`mvp/abupt-reference-results/`：本次三阶段全量对照、官方重复运行、完整训练与复制/恢复的 JSON 证据；统一解释见 `mvp/abupt-reference-acceptance.md`。

## 端到端验收与修复

- [全流程对照验收](mvp/abupt-end-to-end-acceptance.md)：2026-09-09 独立复跑、默认 post、真实恢复与配置输入边界。
- `mvp/abupt-end-to-end-results/`：本轮原始数值对照、测试和源码摘要 JSON。
- `tools/verification/run_noether_post.py` 与 `compare_post.py`：真实 user_project 后处理入口和逐样本、逐点、拓扑、指标对照。

- `mvp/abupt-mps-results/`：复制个人配置的 MPS 全流程、参考重复、同权重与独立训练输出差异和相关测试证据。严格数值一致状态见上述全流程验收文档；`run_noether_reference.py` 和 `run_noether_post.py` 支持从复制的 YAML 配对设备、种子和采样预算。

## 框架正确性验收

- `mvp/framework-correctness-acceptance.md`：输入诊断、部分交付、比较协议和正式复制 recipe 验收。
- `mvp/framework-correctness-results/`：对应配置、测试、运行摘要、源码指纹与比较结果。
- `tools/verification/comparison_protocol.py`：比较目的和证据门禁；compare_post.py 支持 contract/inference/training，compare_training.py 在数值比较前检查训练协议，缺证据非零返回。

## Task 本地实施

- `.context/mvp/task-acceptance.md`：切片范围、相关用例与执行证据。
- `.cursor/rules/ai4e-task-architecture.mdc`：功能模块化 task 规则；不套 DDD。
- `docs/adr/0003-task-local-package.md`：正式版本、目录及安装决策。
- `tests/integration/test_task_*.py`：项目、版本、资产、本地执行、正式案例及安装验收。
- `examples/task_lifecycle.py`：Python new/fork 与运行示例。

## aero_cfd 双模型接入

- `examples/aero_cfd/`：汽车与 NASA 两个配置案例，共享 `recipes/aero_cfd` 阶段入口。
- `tools/verification/transolver3/`：只读参考运行、实际批次追踪、训练/缓存/全量输出逐元素比较、正式硬件探测。
- [Transolver 验收记录](mvp/transolver3-acceptance.md)：功能叶子、100 项映射、正式规模对标及配置兼容未决项。
- `mvp/transolver3-results/`：baseline/coverage 为来源锁定及 100 项映射；provenance 与冻结 YAML/JSON 保存实际配置定位；formal-* 和 full-* 为数值结果；XML 与 delivery-checks/delivered-source 为圈定验收及当前代码摘要。完整数据和权重在独立运行目录。

## 五段配置与快照职责（2026-09-09）

mvp/config-regroup-acceptance.md 与 mvp/config-regroup-results/ 为五段配置、快照与真实复制案例验收；tools/verification/recipe_config.py 仅供对照入口读取案例参数。
