# AI4E_Dojo 开发入口

五段配置切片：recipe 的 configuration.py 负责分组、默认展开和参数提取；rawprep.py 调用库原 datapre 方法。run 接收 config_loader 并冻结用户配置，业务参数不得覆盖快照，数据来源写 reports.dataset。相关新增测试为 test_recipe_configuration.py、test_run_config_snapshot.py、test_verification_config.py；范围与结果见 `.context/mvp/config-regroup-acceptance.md`。

Transolver-3 双模型数值验收（2026-09-10）：共享 recipe 按组件选择锚点或逐点外流装配，NASA 身份为来源/分片/样本。真实 MPS 正式网络完整两轮、恢复、44 测试样本全部输出与参考逐元素对标通过，最大误差 0；参考恢复 RNG 设备交接修正已披露。旧公开配置兼容政策仍待确认，不宣称整体计划全部完成。范围、源码快照与证据见 `.context/mvp/transolver3-acceptance.md`。本切片相关用例：`uv run pytest tests/integration/test_aero_cfd_examples.py tests/integration/test_nasa_crm_data.py tests/integration/test_transolver_training.py tests/integration/test_transolver_post.py tests/integration/test_transolver_reference.py tests/integration/test_aero_cfd_documents.py`；新增选优恢复与通用归一化须联验既有 checkpoint、优化、post 与比较协议用例。

原始数据处理细节原型：`docs/prototypes/dojo-rawprep-detail.html`，文件浏览与字段输出计划分离，仅 UI 示意。相关检查：`uv run pytest tests/integration/test_web_design_documents.py` 与 `tests/integration/rawprep_detail_browser.cjs`（本地 Playwright）。

原型 v3 按用户 UI 图调整，并映射 aero_cfd application/recipe：原始处理三栏、模板配置、执行范围和产物交接。仅 HTML 演示，仍保留已确认八步；不接后端、不执行真实计算。

Task 本地切片（2026-09-09）：六类功能目录、项目、new/fork 正式版本、模板、shared/私有资产、本地执行及比较；运行归 tasks/<task_id>。实现与验收入口见 `.context/mvp/task-acceptance.md`。new/fork 才新增版本；编辑和 run 不新增版本，无草稿/发布/冻结流程。task 不使用 DDD。源码树与安装副本可能不同，验收须核对加载位置。


框架正确性修正（2026-09-09）：设备为参数，沿用同一套训练与后处理；输入错误分项定位，样本/批次身份随异常保留。post-progress.json 记录评估、预测、网格各自状态及部分交付，失败不冒充完整成功。训练/后处理自动记录比较协议；缺证据的历史产物只可做契约核验。相关新增用例为 tests/integration/test_framework_correctness.py 与 test_comparison_protocol.py；与既有后处理、训练恢复及日志用例一起验收。实跑与边界见 .context/mvp/framework-correctness-acceptance.md。


MPS 个人实验验收（2026-09-09）：复制 recipe 修改种子、学习率、权重衰减和锚点预算，889 样本、正式网络两轮、100 测试预测与两辆完整网格已全流程跑通。修复网格查询设备交接、MPS 随机状态保存/隔离及过时的旋转 CPU 回退。Noether MPS 重复训练自身不精确复现；严格数值一致尚未通过，不能沿用 CPU 对齐结论。详见 `.context/mvp/abupt-end-to-end-acceptance.md`。本切片相关测试：`uv run pytest tests/integration/test_train_checkpoint.py tests/integration/test_post_reference.py tests/integration/test_post_mesh.py tests/integration/test_post_inference.py tests/integration/test_model_evaluation.py tests/integration/test_abupt_recipe.py tests/integration/test_reference_arithmetic.py`；MPS 用例须在能访问真实 Apple GPU 的环境执行，skip 不算硬件验收。


可点击线框原型：`docs/prototypes/dojo-web-wireframe.html`（左侧仅两个一级入口，项目六 Tab 位于主视区），仅示意项目六 Tab、八步工作台及比较／报告跳转；使用内存样例数据，无后端、无真实计算，刷新重置，不代表前端技术栈已选定。

Web 平台设计草案（2026-09-09）：产品入口为项目管理与八步任务工作台；项目内含任务管理、版本树、版本比较、项目报告、文件管理和批量运行。产品稿见 `docs/PRD/ai4e-web/src/PRD.md`，Web / Server 架构 v2 见唯一架构文档第 19 节。一个任务对应一个版本，分别展示版本、来源、基线版本；运行尝试可多次，只有 new/fork 创建正式版本；工作目录可编辑，运行保留快照但不增加版本。task 保留研究管理与执行职责。上述为待评审设计，本轮未实现平台或确定技术栈 ADR；不得据此宣称 DOE、三维查看器、报告或版本平台已交付。

当前端到端验收（2026-09-09）：默认 recipe 为 rawprep → trainprep → train → post。冻结变换组合、点场整理与分块查询归 abilities；aero_cfd application 负责业务绑定。独立 post 默认从配置种子沿 global 流采样，隔离锚点/网格两路；兼容张量包、点云与表面原始身份已对齐。实跑规模、数值证据及范围见 `.context/mvp/abupt-end-to-end-acceptance.md`。



当前训练对齐切片：用户入口为 rawprep → trainprep → train。准备交付冻结数据摘要、归一化记录和采样/拼批声明；训练消费前校验。模型结构版本 3 修正 RMSNorm、绝对位置编码器、联合投影与初始化顺序，版本 2 权重不支持直接续训。完整官方等价性必须以 `.context/mvp/abupt-reference-acceptance.md` 的实际证据为准，不能用旧小模型验收替代。

多域 AB-UPT 使用结构版本 3：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。


当前实施状态（2026-09-08）：已交付五类业务、归一化与采样、正式 AB-UPT、训练评估与轮次恢复、可选归一化物化及 VTKHDF/PT 关联、监督比较方法、训练闭环剩余对齐，以及 post 锚点推理（只恢复权重、test 集评估、逐样本保存、可选锚点点云）与完整网格回贴。训练设备默认按 CUDA/MPS/CPU 选择，找不到加速器时警告后回退 CPU；MPS 默认两轮复制案例已实测，范围与结果见 `.context/mvp/framework-correctness-acceptance.md`。物理约束未进。验收范围、逐项用例与执行结果以 `.context/mvp/abupt-acceptance.md` 为准；云图、报告及生产规模训练不在本期验收范围。

AI4E_Dojo 是 AI4S/Engineering AI 研究框架。仓库已建立 uv workspace；另已交付普通 recipes、contrib 数据集适配、Dataset 按需执行、产物 manifest 和能力日志。除数据源下载、路径读取、VTK 家族/NPY 统一 VTK 内存适配、字段提取、有效点 mask、几何派生（点到最近顶点 / 点到网格表面 / 表面法向）、重合点标记与点数校验、具名场张量落盘与按对照表读回、外流 pre 单样本/批量编排与统计量、外流 train 选定 AB-UPT / 打开官方分片 / 按对照表读盘，并支持显式准备和正式训练、最小 Stage/Pipeline、run 开车与写入，以及 aero_cfd 案例前处理与训练准备入口、监督比较方法（均方误差、平均绝对误差、Huber、相对 L2）外，其余目录存在不代表功能已经实现。物理约束未进。

## 工作入口与阅读顺序

每次工作按以下顺序阅读，当前用户指令优先级最高：

1. `AGENTS.md`
2. `.context/index.md`：每次工作的仓库结构与功能检索入口
3. 与任务对应的 `.context/modules/*.md` 或 `.context/mvp/*.md`
4. 按目标 package 读取对应规则：算法包读 `ai4e-algorithm-architecture.mdc`，task 包读 `ai4e-task-architecture.mdc`，server 包读 `ai4e-backend-ddd.mdc`，Web 包读 `ai4e-web-architecture.mdc`
5. 写或改 PRD 时先读 `docs/PRD/README.md` 与 `.cursor/rules/prd-writing.mdc`；PRD 按 `docs/PRD/{包}/{模块}/PRD.md` 落文件，包与模块对齐 `packages/` 一级目录
6. 目标源码、调用方、产物契约、文档与测试

PRD 是模块功能的长期文档，须记录现行行为、设计原因、使用约定和迁移影响；按六节结构归入对应功能点，不另建平行功能说明。README/.context 负责导航，既有独立入口可保留跳转。

`docs/AI4E_Dojo_ARCHITECTURE (1).md` 是业务与代码架构设计文档，不是每次工作的必读文件。需要理解设计原因、整体数据流、Stage/Artifact/RunManifest/ExecutionBackend 或进行架构决策时，由 `.context/index.md` 按需进入。架构设计只在该文档维护；`.context` 负责索引当前仓库结构与文件用途，不复制第二份架构正文。

## 索引维护纪律

- `.context/index.md` 必须反映整个仓库的代码目录结构，并指向各模块上下文。
- `.context/modules/*.md` 必须列出对应模块的目录、文档路径及其含义，帮助 LLM 先定位再读取。
- 新增、删除、移动目录或文档，或改变文件职责时，必须同步对应模块索引和 `.context/index.md`。

## 修改与验收纪律

每次改动只针对本仓库，并遵守下面三条。未同时做到，不得视为完成。

1. **上下游整条链一起看。** 改一处必须想清谁提供输入、谁消费输出、中间交接什么、失败时谁感知。至少核对：调用方、被调用方、契约/配置、缓存或产物、文档读者。不得只改局部、默认上下游自己适应。
2. **同一改动必须带齐这些更新。** `AGENTS.md`（入口、边界或验收纪律受影响时）、`.context`、相关 PRD（按 `docs/PRD/README.md` 的模块目录补；没有则补上受影响模块的 PRD，不得只改代码）、以及测试用例。目录或职责变了还要按上面的索引维护纪律改模块索引。
3. **用相关测试验收，不跑全仓冒充验收。** 先圈定本次改动影响到的用例并跑通，才算验收。不要用全量测试代替「先圈相关用例」。尚无对应测试则先补再跑。用 `uv run pytest <相关路径>`。未跑通相关用例不得验收。

**重点：改配置树必须走完整交接链，不得只改案例 YAML 和眼前几个装配文件。** 漏核下游会引入静默误判，不是“改完眼前再补”。至少核到这三组：

1. **加载与默认注入。** 配置加载、相对路径、从其他目录启动、`--set`、独立脚本和程序调用入口都要读新树；所有模型的默认采样/归一化必须写进新位置，禁止再注入旧顶层键。旧键拒绝须覆盖配置文件、`--set`、脚本和程序入口，并测新旧键同时存在。内部装配键（如 rawprep 的 `pre:`）与已废弃的案例阶段名不是一回事，禁止误拒绝。
2. **对照与选择器。** 对照工具与 task 比较选择器必须指向新路径。已声明的比较条件取不到值就是不可比，禁止填 `None` 或空对象后仍判相同。缺键禁止 `get(..., {})` 静默回到默认种子或预算。对照脚本若加载案例模块、调用阶段函数，必须一起改，不能只改阶段字符串。
3. **用户配置 ≠ 冻结产物。** 用户配置可以拒绝旧格式；历史准备产物能否消费、要不要重新准备、旧检查点能否续训，必须分开定义。冻结声明按业务语义提取，不得把收组后的整段配置直接当作准备一致性、续训或数值比较条件。已有历史证据文件保留原样。验收必须覆盖准备消费、轮次恢复、独立 post、归一化物化、task 资产与指标比较、其他模型工作流，以及实际 wheel 安装后的复制 recipe；不能只用几个 recipe 脚本测试代替。

本切片相关验收入口：

```bash
uv run pytest tests/integration/test_train_resolved_config.py tests/integration/test_train_test_repeat.py tests/integration/test_train_code_snapshot.py tests/integration/test_train_interrupt.py tests/integration/test_train_diagnostics.py tests/integration/test_train_optim_align.py tests/integration/test_train_entry_init.py tests/integration/test_train_shapenet_contract.py tests/integration/test_train_reference_stats.py
uv run pytest tests/integration/test_train_loop.py tests/integration/test_train_checkpoint.py tests/integration/test_train_recipe.py tests/integration/test_constraint_losses.py tests/integration/test_train_online_loss.py tests/integration/test_model_evaluation.py
uv run pytest tests/integration/test_post_inference.py tests/integration/test_abupt_recipe.py tests/integration/test_post_mesh.py
uv run pytest tests/integration/test_train_formal_two_epoch.py
```

## 技术基线

- Python 基线为 3.12；根 `pyproject.toml` 管理 uv workspace，成员为 `ai4e-spec`、`ai4e-core`、`ai4e-contrib`、`ai4e-task`。
- `packages/` 下每个包只保留一层物理目录；根 `pyproject.toml` 必须把连字符目录显式映射为下划线 Python 导入名（如 `packages/ai4e-core/` → `ai4e_core`），不得重新创建内部同名目录。
- 所有 Python、pytest、ruff、mypy 和 Sphinx 命令必须使用 `uv run`。
- `ai4e-web` 技术栈尚未决定；在 ADR 明确前不得创建或替换前端框架。
- 依赖只允许进入各生态的唯一清单；本阶段不得创建临时依赖文件。

## 包依赖边界

```text
ai4e-spec
   ↑
ai4e-core
   ↑           ↑          ↑
recipes      task        viz
               ↑
            server → web
```

- `ai4e-spec` 不导入其他 ai4e 包，也不依赖 torch/numpy。
- `ai4e-core` 只依赖 spec；core 不导入 viz。
- `ai4e-contrib` 依赖 spec + core。
- `ai4e-task` 依赖 spec + core，不导入 recipes。
- `ai4e-viz` 只依赖 spec，通过稳定 run artifact 读取结果，不认识模型和 Trainer。
- `ai4e-server` 依赖 spec + task；`ai4e-web` 只消费 server API 或稳定 artifact schema。
- `applications/base` 只提供通用编排机制；领域 application 按 rawprep/trainprep/model/train/post 组织标准业务装配，但不得感知具体 modeling/constraint 内部实现。

## 三类代码结构原则

- **算法包**：`ai4e-spec`、`ai4e-core`、`ai4e-contrib`、`ai4e-viz`、`ai4e-contrib`。严格遵循 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 给出的 base、abilities、applications、Stage 和 Artifact 划分，以高内聚、低耦合约束实现；跳出 DDD 的 `api/domain/application/infrastructure` 目录表象。
- **任务包**：`ai4e-task` 按 cli/projects/tasks/versions/templates/storage 六类功能组织，不套用 DDD；Python API 与 CLI 共用实现。
- **后端包**：`ai4e-server`。围绕 Project、Experiment、Run、Artifact、Job、Execution 等业务生命周期采用轻量 DDD；先划分限界上下文，再按真实需要在上下文内部区分 domain/application/ports/adapters，不建立全局空壳层。
- **前端包**：`ai4e-web`。按数据接入、recipe 配置、run、对比、报告等用户任务形成微领域；每个微领域自治，并通过稳定 server API 或 Artifact schema 交互，不镜像后端目录。
- 三类原则不能互相套用：算法不包装成贫血领域对象，后端不实现数值算法，前端不承担训练与物理计算。

## 分层与修改纪律

- 原子能力按 data、transform、geometry、sampling、modeling、constraint、training、eval、postproc、report 分层。
- `data` 按六个阶段组织：`source` 来源读取与分片名单、`extract` 字段与记录、`validate` 对齐和输出门禁、`filter` 标记与筛选、`save` 张量读写与恢复、`stats` 数组流统计。不得恢复 clean/offline/online 的状态式划分。
- 同组字段声明来源、point/cell、实体数和原 ID 序列，无 mask 也必须校验行身份与数量；筛选统一更新组内字段与身份，点 mask 不适用于 CellData。编码器不猜组名后缀，`cell.pt` 是 recipe 的可选业务打包约定。
- `geometry` 保留完整 VTK，点到面与法向共用全二维面门禁，不抽取体外壳；按原 point ID 回贴法向，孤立点为零且有效性标记为 False。几何不依赖物理场，`pre.geometry.enabled` 显式选择，未启用不计算。fields 可显式为空。
- 外流 rawprep 保留 read/derive/select/save/stats 单样本能力，由 dataset 模块提供按需装配。recipe 使用 datapre(cfg) 显式登记步骤，run 内封装样本循环，application 不反向导入 run。
- 样本发现与统计样本/字段/缺失策略属于 application；通用样本循环、首错/继续和汇总属于 `run/execute`。Stage/Pipeline 沿用现有顺序调用，不另建 DAG。任何样本失败都不能汇总为完整成功，首错停止保留之前提交结果且跳过统计。
- dry-run 与提交共用输出预检，针对实际样本目标检查覆盖；张量使用同级临时目录、旧目录备份、提升与失败恢复，遗留路径显式处理。重算统计只用本次成功结果的实际路径，逐数组流累计；dry-run 不扫描旧张量或写统计量。
- `run/writer` 独占运行配置、日志与摘要写入；runner 不解释 pre 路径或业务字段，业务通过 reports 交付摘要。预处理张量写数据目录。外流 train 已有的分片读取与表面零距离处理保留，正式模型构建、监督更新、评估和轮次恢复由 model/train 装配。
- recipe 按 rawprep/trainprep/model/train/post 展开；infer 和最终 eval 由 post 调用，recipe 不写算法或训练循环。
- `run/writer` 是 run 目录唯一写入方；运行记录与数据目录独立配置；运行配置/日志由 writer 写入，数据产物由 save 写入，禁止写入包源码目录。
- 用户组件默认通过全限定 import 路径接入，不要求继承 core 基类。
- 修改功能时按「修改与验收纪律」同步 `AGENTS.md`、`.context`、PRD 与测试；新增、删除或移动文件时同步模块索引。
- Python 源码必须更新中文模块说明与公开 API Docstring；复杂数据语义、单位、拓扑和性能取舍解释原因。

## AB-UPT MVP1 边界

- `user_project/` 是历史验证资产，只作迁移参考，不得成为新包的公共依赖。
- AB-UPT 完整模型托管于 contrib；recipe 注入构造器，core 不导入 contrib。通用组件按验证后的等价实现提炼。模型迁入与小规模训练已验收。
- `packages/` 下的新代码不得导入 `noether`；如需参考行为，应重建最小契约并用测试证明等价。
- MVP1 目标与验收以 `.context/mvp/abupt-mvp1.md` 为准。

## 验证纪律

单次改动的验收以「修改与验收纪律」第 3 条为准：只跑相关用例。下面是仓库门禁，不是每次改动都要跑完全部：

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/
uv run sphinx-build -b html docs/source docs/_build/html
```

不得用目录存在、import 成功或构建成功替代对应功能测试。发现并核实错误时按 `.cursor/rules/error-log.mdc` 记录；没有错误时不得制造日志。

## 可复制 Recipe 与 Dataset

- `recipes/` 是普通模板集合，不是 Python 安装包；交付 README/config/pre/train/post/pipeline，不建 init/main、缓存或组件占位。
- `ai4e-contrib/application/datasets` 提供可安装的 manifest/adapter，recipe 可 import 或复制修改；core 不依赖 contrib。
- `${...}` 插值展开后按配置文件解析路径；数据根、各分片、normalize 路径和运行根独立可配。
- 原始 manifest 描述来源；产物 manifest 描述本次成功交付。统计默认仅用本次完整训练分片。覆盖开始撤下旧完整清单；部分失败不得继续发布完整清单。
- recipe 阶段日志使用 `[阶段/能力/事件]`（如 `[datapre/数据集/选择结果]`）；运行入口设置并恢复阶段上下文，原子能力不感知 recipe，后台心跳显式继承阶段与样本身份。阶段边界使用 `[datapre/阶段/开始]`；整体运行及无阶段的独立调用不强加阶段前缀。writer 统一写入并按事件元信息筛选控制台摘要。
- inputs 只保存一份最终生效 config.yaml；日志包含能力/工作流开始结束与长任务进度，不倾倒配置、数组和整批结果。
- 归一化正反变换、冻结记录与可选物化已实现；prepare/fit 对物理输入必须显式 execute=true。正式网络小规模拟合与恢复已验收，复制案例短训与恢复已验收，生产规模训练不在本期范围。训练设备默认 `auto`，无加速器时警告后继续用 CPU，MPS 的邻域检索和复数旋转显式经 CPU。
- PRD 增加 `docs/PRD/recipes/{案例}/PRD.md` 作为非安装模板集合的对应位置。

## Task 本地切片验收

相关用例：`uv run pytest tests/integration/test_task_management.py tests/integration/test_task_assets.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py tests/integration/test_task_recipe.py tests/integration/test_task_documents.py tests/integration/test_task_installation.py`。安装用例构建实际 wheel；运行和既有 core 的相关回归范围见 `.context/mvp/task-acceptance.md`。不可用全仓测试代替这些接口、资产和真实案例验收。
