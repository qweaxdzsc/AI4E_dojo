PI-BSNet 原案例迁移（2026-09-14，Neumann/Advection完整验收通过）：保留原参数导数、初始化与损失算术；实际Dojo分别5000轮/5000更新、2000轮/200000更新，平均相对L2为1.881%和10.427%。与同环境原函数全部权重、每轮损失和40个测试场逐值一致。75项圈定测试通过，含完整产物、恢复和真实wheel安装；梯形保留十实例，另外两例原算法切换范围待用户确认。入口tools/verification/pibsnet/source_dojo.py，报告工具source_migration_report.py，证据见.context/mvp/pibsnet-acceptance.md。

## 独立推理实施入口（2026-09-14，进行中）

- `.context/mvp/inference-acceptance.md`：各层验收状态、Web 13 项结果、真实 CPU 2×2 流程证据及待补安装范围，不代替架构正文。
- `packages/ai4e-core/abilities/inference/`：原子恢复、预测、查询和状态保护；`packages/ai4e-core/applications/aero_cfd/infer/`：外流推理步骤、配置、检查及固定结果读取；各文件导航见 [core 索引](modules/ai4e-core.md)。
- `recipes/aero_cfd/infer.py` 与五个外流 example：独立脚本和显式流水线；新 post 消费结果，旧调用入口兼容。导航见 [recipe 索引](modules/recipes.md)。
- [spec 索引](modules/ai4e-spec.md)：固定检查点、推理请求和结果身份；[task 索引](modules/ai4e-task.md)：检查、权重固定、批次协调和结果读取。
- [server 索引](modules/ai4e-server.md)：任务下 inference API、来源登记及受控文件；[Web 索引](modules/ai4e-web.md)：九步 slug 导航、批次页面及 Trame 交接，旧数字 6/7 保留后处理/报告语义。
- `tools/verification/inference_acceptance.py`：隔离真实 CFD 准备、2 份权重与 2 个样本，输出身份供浏览器及原生 Task 验收使用。
- `tests/integration/test_task_infer_checkpoints.py`、`test_task_infer_batches.py`、`test_web_inference.py`、`test_infer_results.py`、`test_infer_devices.py`、`test_infer_installation.py`：固定输入、串行批次、HTTP 结果、设备和安装圈定测试；实际结果统一登记验收记录。
- 唯一架构正文：`docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 5、9、19.11 节。原子/业务/脚本、管理记录和输出所有权在该文档维护；已知旧 profile 按固定 36 份脚本核验，回归已通过；正式 8000/5173 入口已核验，当前阶段回归剩余失败与最终文档测试见验收记录。


PI-BSNet Neumann/Advection 独立六组测试（2026-09-14，完整预算完成）：用户批准同时测试源码与物理导数解释，Neumann交叉整轮/逐实例更新；完整预算后再决定迁移，本轮不改Dojo算法。入口 `tools/verification/pibsnet/neumann_advection_trials.py`；圈定 `test_pibsnet_neumann_advection_trials.py`，进度与未决项见 `.context/mvp/pibsnet-acceptance.md`。

梯形十实例 Dojo 迁移（2026-09-14）：唯一梯形生成与模型已按用户选中实验接入；3000轮/30000更新与同环境原函数的权重、全部损失、十个场逐值一致。当前相对L2=0.00540455，未复刻旧环境0.00305350。Neumann/Advection 本轮只核查，见 `docs/pibsnet/Neumann与Advection输入核查.md`；实际运行以 `mvp/pibsnet-acceptance.md` 为准。

平台数据集与数据准备页对齐（2026-09-15）：工作区 `datasets/` 按名称登记正式原始处理产物；数据准备按名称选用并复用产物树与执行面板；候选项按登记时间倒序，不自动勾最新；同一清单只列平台名。执行区展示已选名称与全部/指定样本范围。准备可重划 train/test/eval，官方名单不改，划分写入准备记录。实现见 task `storage/processed_datasets.py`、server `modules/datasets/`、web rawprep/trainprep/stages，core `abilities/data/source/split.py`，圈定 `tests/integration/test_web_processed_datasets.py`、`test_trainprep_split.py` 与 `e2e/stage-consistency.spec.ts`。

# AI4E_Dojo 仓库结构索引

PI-BSNet 论文参数验证（2026-09-14，三组完整预算完成）：用户确认 Burgers 正对流/MSE、梯形10与50实例两组及论文控制网格/权重；入口 `tools/verification/pibsnet/paper_parameters.py`，只改变获批参数，保留样条/数据/初边界未决差异。误差分别为0.10458919、0.00305350、0.00237572；报告与边界见 `mvp/pibsnet-acceptance.md`。

PI-BSNet 原仓库基线（2026-09-14）：五例原数据/原设置/完整预算独立运行及报告已完成，未修改Dojo算法；报告入口、数值与论文比较边界见 `mvp/pibsnet-acceptance.md` 首节。

平台一致性切片（2026-09-14，圈定验收通过）：真实阶段摘要、保存后操作、固定阶段文件、领域表单及日志曲线；路径见 Web/Server/Task 模块索引，当前证据在 `mvp/web-integrated-results/ui-consistency/`。不沿用历史验收数。

PI-BSNet 设置与算法核查（2026-09-14）：`docs/pibsnet/设置与算法一致性核查.md` 对照用户PDF与锁定仓库，列出结构/数据算法差距、论文与代码冲突及逐步等价门禁；只核查，未修改训练实现。

参数化 PDE / PI-BSNet：`mvp/pibsnet-acceptance.md` 记录五案例数据、完整训练、五例最终对比报告及未通过的精度门槛；`modules/ai4e-core.md`、`modules/ai4e-contrib.md`、`modules/recipes.md` 索引物理能力、模型、方程与独立生成/阶段脚本。

整合平台已通过圈定验收：稳定传输 `packages/ai4e-spec/artifacts/platform.py`，自动 TypeScript 生成入口 `packages/ai4e-web/scripts/generate-platform-contracts.py`；四组合真实短训、最终18项浏览器与范围限制见 `mvp/web-integrated-acceptance.md`。旧首期记录保留，不能当作新功能验收。

首页入口纠正：`ai4e-web` 增加真实 `WorkbenchLandingPage` 和原型装饰封面 `public/project-covers/`，恢复项目卡与进入操作；首页真实点击及双视口对照在 `e2e/home-entry.spec.ts`，修复后21项前端回归及截图见 `mvp/web-integrated-results/homepage-correction/`。原18项阶段验收不能替代首页验收。

任务创建与绑定修正：任务弹窗只填写名称、案例和描述，选项展示数据集与模型；ShapeNet目录/NASA跨根文件在原始处理页绑定。实现索引见Web/Server模块，测试为`test_web_dataset_binding.py`、`test_web_binding_real.py`和`e2e/task-dataset-binding.spec.ts`，证据位于`mvp/web-integrated-results/task-binding-correction/`。

整合交互原型：`docs/prototypes/dojo-web-integrated.html`。沿用旧平台框架，内嵌第 2–7 步独立页面；项目页与第 1、8 步保留。单文件离线可打开，阶段配置按任务保留于当前会话，刷新重置；无真实计算或后端交接。验收：`tests/integration/web_integrated_browser.cjs`。

- `docs/ai4s-framework-comparison.md`：六框架能力、优势、证据边界及案例驱动演进参考；以新增科研案例推动框架改进，不是架构实施计划。`tests/integration/test_framework_comparison_document.py` 检查文档导航与仓内来源链接。

- `docs/prototypes/dojo-post-detail.html`：后处理独立原型，本轮仅结果可视化 Tab；文件树、场景资产、属性与多窗口。汽车云图为用户参考图内嵌裁片，未接入真实渲染；指标／图表等待 UI。测试为 `tests/integration/post_detail_browser.cjs`。

- `docs/prototypes/dojo-run-detail.html`：训练运行独立原型，摘要、合成曲线、指标表、日志与快捷操作。不提供暂停，停止后从检查点继续；全部数据为示例。`tests/integration/run_detail_browser.cjs` 验证对应 UI 交互。

- `docs/prototypes/dojo-training-detail.html`：训练设置独立原型，优化器／训练控制／EMA／诊断／测试评估配置；测试执行阶段待用户确认。`tests/integration/training_detail_browser.cjs` 检查增删、开关、预检和会话保存。

- `docs/prototypes/dojo-model-detail.html`：模型设置独立原型，左侧模型参数、输入输出、学习目标与权重加载，右侧 TorchVista 展示示意；优化器已归训练设置。`tests/integration/model_detail_browser.cjs` 覆盖相关 UI 与图形导出。

- `docs/prototypes/dojo-trainprep-detail.html`：按数据准备 UI 参考图制作的独立布局初稿，保留现有工作台外壳；统计来源与采样生效阶段待用户确认。`tests/integration/trainprep_detail_browser.cjs` 检查字段编辑、资源选择、预览和示意执行。

- `docs/yaml-config-comparison.md`：Noether、PaddleScience、MindScience、PhysicsNeMo、Anemoi 的案例配置比较及 Dojo 讨论建议；静态源码范围与来源链接见文内。

- `docs/prototypes/dojo-rawprep-detail.html`：原始数据处理独立细节原型；已落盘文件统一浏览、字段选择与输出计划、文本／张量／三维弹窗。`tests/integration/rawprep_detail_browser.cjs` 检查对应交互。

## Web 平台设计入口（DRAFT，2026-09-09）

- 原型 v3 按用户四张 `docs/prototypes/*.png` UI 参考图调整，并映射实际 aero_cfd application/recipe。参考素材与能力来源见 web 模块索引；仅 UI 示意。

- `docs/prototypes/dojo-web-wireframe.html`（左侧仅两个一级入口，项目六 Tab 位于主视区）：独立离线 HTML 历史线框，示意布局；本轮唯一 UI 基准为整合原型。
- `tests/integration/web_wireframe_browser.cjs`：本地 Playwright 浏览器交互检查，覆盖版本比较、报告、文件预览、批量派生和工作台；复用外部测试运行时，不新增平台依赖。

- [Dojo WEB 平台产品设计](../docs/PRD/ai4e-web/src/PRD.md)：项目管理六个 Tab、八步工作台、跨版本比较与批量派生的待评审产品正文；不代表源码已实现。
- [Web / Server 架构 v2](<../docs/AI4E_Dojo_ARCHITECTURE (1).md#19-dojo-web--server-架构草案-v2>)：唯一架构正文第 19 节，定义 task/server/web 职责、版本与运行契约及目标目录。
- `tests/integration/test_web_design_documents.py`：产品与架构设计稿本地链接、章节和来源引用的相关文档检查。

server/web 已有首期代码，本轮整合平台扩展正在实施；当前包内入口见模块索引，规划与已验证能力以专项验收区分。

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
├── README.md                 # 使用者运行说明 + 开发者仓库入口；细则仍在 AGENTS/.context
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
│   ├── ai4e-viz/             # 独立可视化应用 + 原静态/预览库
│   ├── ai4e-server/          # 本机项目/任务/文件/处理/报告 API
│   ├── ai4e-web/             # 正式 React 微领域 Web 工程
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

- **算法原则** — `ai4e-spec`、`ai4e-core`、`ai4e-contrib` 与 viz 现有库目录：按权威架构文档中的 base、abilities、applications、Stage 和 Artifact 分层，保持高内聚、低耦合，不套 DDD 目录。
- **后端原则** — `ai4e-server`：围绕业务生命周期采用轻量 DDD，先按限界上下文组织，再在上下文内部按需分层。
- **前端原则** — `ai4e-web`：按用户任务组织微领域，每个领域自治，只消费稳定 API 或 Artifact schema。

修改 package 前先进入其模块索引，再读取下方对应代码规则；三类结构原则不得混用。

## 正式包导航

- [Ability 五类简表](../docs/abilities-summary.md)：按 rawprep/trainprep/train/model/post 汇总 20 项业务能力，作为优先阅读入口；详细合并与源码表保留对照。检查复用 `tests/integration/test_ability_merged_document.py`。

- [当前 Ability 源码清单](../docs/abilities-inventory.md)：core / contrib 能力表、公开入口与实现边界，供工作流粒度讨论；文档检查为 `tests/integration/test_ability_inventory_document.py`。
- [合并后的 Ability 清单](../docs/abilities-merged.md)：v2 按 rawprep/trainprep/model/train/post 展开操作、策略与嵌套计算单元，保留原始 89 项及 O/P 大组对照；仅讨论稿，不改变公开 API。文档检查为 `tests/integration/test_ability_merged_document.py`。

- [`ai4e-spec`](modules/ai4e-spec.md)：`packages/ai4e-spec/` 的目录、文档、契约职责与依赖。
- [`ai4e-core`](modules/ai4e-core.md)：`packages/ai4e-core/` 的 base、abilities、applications、run 和 tools 目录索引。
- [`recipes`](modules/recipes.md)：`recipes/` 的普通脚本模板与运行入口。
- [`ai4e-task`](modules/ai4e-task.md)：`packages/ai4e-task/` 的六类代码目录与本地验收入口。
- [`ai4e-viz`](modules/ai4e-viz.md)：`packages/ai4e-viz/` 的 render 和 compose 位置。
- [`ai4e-server`](modules/ai4e-server.md)：本机服务模块、配置映射和文档入口。
- [`ai4e-web`](modules/ai4e-web.md)：正式 Web 工程、边界和文档入口。
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
- `tools/ssh-git-remote.conf`：远程 Git SSH 连接与 `git push server` 用法；不含私钥。

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

- `examples/aero_cfd/`：汽车与 NASA 五个独立配置案例，共享 `recipes/aero_cfd` 阶段入口；三个 ShapeNet 案例默认打开 VTKHDF，NASA 不写该键。
- `tools/verification/transolver3/`：只读参考运行、实际批次追踪、训练/缓存/全量输出逐元素比较、正式硬件探测。
- [Transolver 验收记录](mvp/transolver3-acceptance.md)：功能叶子、100 项映射、正式规模对标及配置兼容未决项。
- `mvp/transolver3-results/`：baseline/coverage 为来源锁定及 100 项映射；provenance 与冻结 YAML/JSON 保存实际配置定位；formal-* 和 full-* 为数值结果；XML 与 delivery-checks/delivered-source 为圈定验收及当前代码摘要。完整数据和权重在独立运行目录。

## 五段配置与快照职责（2026-09-09）

mvp/config-regroup-acceptance.md 与 mvp/config-regroup-results/ 为五段配置、快照与真实复制案例验收；tools/verification/recipe_config.py 仅供对照入口读取案例参数。

## 物理数据跨模型实验

- `.context/mvp/cross-model-acceptance.md`：五组独立实验、完整点场与图表验收状态。
- `tools/verification/cross_model/`：顺序训练、固定名单评价及两份比较报告入口。
- `packages/ai4e-viz/`：静态渲染包，源码及 PRD 见 viz 模块索引。
- 新增物理视图和共享工作流位置见 core/contrib/spec 模块索引。

- `docs/aero-cfd-server-runbook.md`：五案例服务器50轮操作、数据迁移、报告结构与交付门禁。

- `mvp/cross-model-50-acceptance.md`：五案例50轮本地实验运行状态与显式预算验收入口。

## Web / Server 首期接入

- `.context/mvp/web-rawprep-acceptance.md`：页面到现有案例的真实样本验收、保护范围、已知限制。
- `docs/adr/0004-web-server-runtime.md`、`docs/adr/0005-preview-worker.md`：本机栈与预览工作进程。
- `tests/integration/test_web_*.py`、`test_viz_file_preview.py`、`test_task_configuration.py`：平台、配置、文件及任务回归。
- `packages/ai4e-web/e2e/rawprep.spec.ts`：真实页面到文件结果、报告和预览。

- `mvp/web-rawprep-results/`：browser-handoff.json 为实际浏览器运行和原数据准备数值证据，backend.xml 为 48 项圈定验收，mesh.png/workbench.png 为实际界面截图。

本机训练持久目录约定见 AGENTS.md 与 recipes 模块索引：后续 Dojo 实验及相关缓存写入 `/Users/zonghui/work/project_simulation/dojo_train/`，不再新建到 tmp。

## 整合平台并行验收

- `mvp/web-integrated-acceptance.md`、`mvp/web-integrated-results/`：主 Agent 独立 HTTP 四组合、数值交接和总验收。
- `mvp/web-algorithm-acceptance.md`、`mvp/web-algorithm-results/`：数据、模型、归一化、采样与真实计算子计划。
- `mvp/web-visualization-acceptance.md`、`mvp/web-visualization-results/`：VTK、真实浏览器、多窗口、联动与资源子计划。
- `tests/integration/test_web_integrated_pipeline.py`：HTTP 阶段提交、固定产物、真实预览对照及契约生成。

## Recipe 显式流程与用户扩展

- 规则：`.cursor/rules/ai4e-recipe-authoring.mdc`；计划规则：`.cursor/rules/plan-business-alignment.mdc`。
- 目录：`recipes/aero_cfd/`、`examples/aero_cfd/` 与 `examples/recipe_extensions/{field_mapping,sampling}/`，逐文件用途见 `.context/modules/recipes.md`。
- 公开步骤与组件索引：`.context/modules/ai4e-core.md`、`.context/modules/ai4e-contrib.md`。
- 圈定验收完成（五例 CPU 小规模逐值对照、真实扩展、wheel 外部复制与相关回归）；规模与迁移：`.context/mvp/recipe-explicit-acceptance.md`；批准计划：`.cursor/plans/显式_recipe_步骤_9ea01c80.plan.md`。

PI-BSNet 功能核对资产：`docs/pibsnet/` 保留原122项 MD/XLSX 及独立实施映射；`tools/verification/pibsnet/` 执行来源锁定、比较和实验。状态以 `mvp/pibsnet-acceptance.md` 为准。

## 独立 Vis 迁移入口

`packages/ai4e-viz/{backend,frontend,.context,.cursor,docs,resources,fixtures}` 保留源应用结构；详见 [viz 索引](modules/ai4e-viz.md)。包内架构维护内部实现，根架构仅维护 task/spec/server/web 的交接。

迁移验收分三类记录在 [vis-migration-acceptance.md](mvp/vis-migration-acceptance.md)；完整文件目录与变更处置在包内 docs/migration/。

## 数据集声明驱动原始处理

历史任务映射修正：server capabilities/recipe_profile.py 区分格式差异、已审定旧加载入口和真实逻辑变更；`tests/fixtures/rawprep_legacy/configuration.py` 固定已核验历史入口。回归与真实旧任务执行见 `tests/integration/test_web_recipe_compatibility.py`。

ShapeNet-Car/NASA 默认配置、真实字段目录和样本范围接入；模块入口见 contrib/core/task/server/web/spec/recipes 索引。验收范围及证据见 [专项验收](mvp/manifest-rawprep-acceptance.md)。

三维对象工作台实施：见 `.context/modules/ai4e-viz.md` 与 `.context/mvp/phys-workbench-acceptance.md`，真实图形交互与时序导出单独验收。

三维真实 CFD 验收入口：`tests/integration/viz_real_results_browser.cjs`；源数据不迁入仓库，执行证据与范围见 `mvp/phys-workbench-acceptance.md`。

参考图样式校正入口：`tests/integration/viz_visual_browser.cjs`；四种宽度实际截图与功能回归见 `.context/mvp/phys-workbench-acceptance.md`，视觉验收与计算验收分别记录。

## 同数据集模型选择

模型设置选项、官方起步预设、项目导出预设与结构跟踪来源见 Web/Server/Task 模块索引；`packages/ai4e-server/modules/capabilities/model_cases.py` 按两个官方模型和五个 example 解析默认值，`model_presets.py` 写入项目共享资产，`trace_source.py` 在当次检查解析最近可用物理来源；现行 version=2 准备由检查门面按训练同一条消费链跟踪。现行模型页不展示权重加载；采样跟随当前模型字段，Transolver-3 展示步长/分块/切片与固定损失行。独立 HTML 原型仍保留历史权重加载示意，不代表现行页面。真实交接与圈定验收见 [模型选择验收](mvp/model-picker-acceptance.md)。

- `docs/pibsnet/五案例精度对照报告.md`：2026-09-14五例Dojo实跑与论文精度汇总，标明当前迁移版、历史结果、统计口径和证据；不代表五例全部重新迁移。

- `docs/pibsnet/figures/accuracy-2026-09-14/`：五案例报告配图与重算metrics.json；固定首个测试实例，预测/参考共用色标，保留源数组摘要。

Web请求失败定位：`modules/ai4e-web.md` 中的HTTP门面及 `e2e/http-errors.spec.ts`，覆盖后端未启动导致的空代理响应与刷新恢复。

平台默认 Trame 入口：`modules/ai4e-web.md` 索引网格预览、后处理空场景与宿主尺寸；`packages/ai4e-web/e2e/trame-entry.spec.ts` 从实际研究页面验证打开、导入和关闭回收；`e2e/preview-dialog.spec.ts` 验证网格预览弹窗加高与视口全屏。证据见 `mvp/phys-workbench-acceptance.md`。

## 后处理工作台（2026-09-15）

- core `abilities/eval` 与 `applications/aero_cfd/post`：固定结果指标计算。
- task `tasks/post_results.py`、`post_metrics.py`、`post_metrics_worker.py`：目录和后台评价。
- server `modules/post`：任务范围API；web `modules/post`：指标/文件/三维三个Tab。
- web `modules/files`：共用产物树；`modules/visualization`：紧凑预览与常驻Trame。
- Vis `visPhysField`：可见性消息、草稿保留与来源追加。
- 各包文件和文档见对应模块索引；验收与未覆盖项见 [后处理验收](mvp/post-workspace-acceptance.md)。

后处理参考图UI精修与浏览器验收：见 [Web模块索引](modules/ai4e-web.md) 和 [后处理验收](mvp/post-workspace-acceptance.md)。

## 推理工作台四栏与跨分片统计

- `docs/prototypes/dojo-inference-reference.png`：用户原图1672×941。
- `.context/mvp/inference-ui-acceptance.md`：完整文件交接、UI与真实功能两道验收及未完成项。
- 新能力、Task批次、Server协议、Web组件与六套模板分别见对应模块索引。
