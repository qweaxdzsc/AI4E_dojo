# AI4E_Dojo 开发入口

历史进度原文见 [.context/history/development-updates-20260917.md](.context/history/development-updates-20260917.md)。研究任务先从 [.context/tasks/research.md](.context/tasks/research.md) 按需阅读；本页保留当前规则与授权边界。

当前仓库：七个正式包，外流 CFD、参数化 PDE、耦合物理场、控制轨迹、时空预测与地热六类应用；可安装 AB-UPT、Transolver-3、PI-BSNet、GenCP（CNO/SiT-FNO）、SafeDiffCon、WDNO（基础预测缩小预算）和 MeshGraphNet（CylinderFlow 及 ShapeNet-Car/NASA CRM 静态外流工程接入；两例已完成真实小样本短训与完整推理，未完成论文复现或生产精度）。GeoTransolver 已接入 Darcy/公开保险杠，并支持 ShapeNet-Car 双域和 NASA CRM 表面的普通 GALE 基础配置（无局部编码）；计算能力沉淀 core，外流五轮真实参考、全点预测、恢复与安装后 Python/Task 对照通过，未复现论文精度。外流专项及回归边界见 `.context/mvp/geotransolver-aero-acceptance.md`。另已接入 PCNO 发布小数据双场流程（短预算验证，含明确数值修正，非论文复现）。平台模型选择仍只开放原登记外流案例，生成式 PDE、MeshGraphNet、GeoTransolver 与 PCNO 走 Python；NASA 数据准备已支持 VTKHDF。缺失产品功能不因架构整理自动实施。

历史数值验收按 `.context/mvp/` 原记录保留，当前入口不复制历史进度。全局架构唯一正文为 `docs/AI4E_Dojo_ARCHITECTURE (1).md`，本轮源码—功能—文档—测试核对及最终结果见 `.context/mvp/architecture-alignment-acceptance.md`。

## 注意事项

默认禁止 `uv sync`。不要为跑测试、改普通源码或“保险起见”重装环境。测试一律 `uv run --no-sync pytest <相关路径>`。

只有这两种情况才允许 sync / `--reinstall-package`：

1. 刚改了 hatch `force-include` 包（spec / core / contrib / task / server / viz）。官方 8000 读的是 `.venv` 安装副本，不是 `packages/` 源码。
2. 当前环境已确认被不含 visualization 的 sync 卸掉了工作台依赖（后处理报 `vis_service_start_failed`，缺 `trame` / `pandas`）。会话已 200、页面却是 Connection error，是 8000 缺 WebSocket 库（`uvicorn[standard]` / `websockets`），不是 Vis 没启动；包已在环境里时只重启 8000，不要再 sync。

允许重装时必须写成 `uv sync --group dev --group visualization --reinstall-package <包>`。禁止只跑 `uv sync --group dev` 或裸 `uv sync --reinstall-package …`：uv 按当前指定组对齐环境，会卸掉 Trame 工作台，官方 8000 再拉后处理就会失败。`dev` 已含 `ai4e-viz[workbench]`，默认组含 `dev` 与 `visualization`，不要再拆开。

正式 `8000` / `5173` 由用户控制。未获当次明确同意，不得对其 `uv sync --reinstall-package`、杀进程或重启。8000 无热重载，装新包后旧 Vis 子进程仍是旧代码，要等用户同意再重启 8000 或只回收其 Vis；只刷新 5173 不够。有 Web 消费链时，Agent 必须自己在用户实际 8000/5173 做正式冒烟；隔离 `7999` / `5172` 只能并行核对，不能替代。未重装受影响 force-include 包、未更新正式进程/Vis 会话时，正式 Web **验收不了**，工作停在未完成，必须当时申请授权，不得把「待发布」当交付结束。切步产物名单只确认文件还在与受控路径，不在列举时整文件核验检查点；恢复训练和提交推理仍核内容修订。

## 组件自由与稳定公开边界

core 另提供可选 FLARE++ 注意力组件，普通张量显式调用，不默认替换已有模型，不表示平台或 GeoTransolver 已开放该后端。组件验收见 `.context/mvp/flare-attention-acceptance.md`。

- 不建立全仓统一组件协议。普通函数/对象自行定义输入输出，recipe 或局部连接负责转换，application 负责领域绑定；只有选用特定业务步骤才承担其实际调用约定。
- 稳定门面为 `ai4e_core.run` 的 launch、stage、TrainingRun、execute_operation、managed_run。配置加载器显式传入，不在通用运行器解释外流、模型或 PDE 参数。可选 configuration_adapter 仅在显式托管上下文生效，退出恢复。
- 不读取框架私有会话字典或跨层内部实现。新官方模板的配置转换及模型专属参数归 contrib/application；自由研究脚本不需要使用官方配置树。
- 平台操作按任务声明调用；源码摘要用于来源记录，新增能力文件或编辑连接不以模板全文/AST 不同拒绝。缺 operations 的旧副本只复用创建来源已有声明，显式空声明不回填；不迁移历史任务目录。
- 新外流 infer 负责预测，post 只读固定结果；历史公开导入保留薄门面，计算实现在 infer。组件中间值不强制 Artifact 化。
- 改内部实现须运行固定用户源码基线及安装测试；不得同步修改基线摘要来通过测试。真正公开接口变更逐项记录参数、返回值、异常及迁移范围。

## 工作入口与阅读顺序

模型集成使用仓库 skill [dojo-integrate-model](.agents/skills/dojo-integrate-model/SKILL.md)，完整标准见 [模型集成目标与验收原则](docs/model-integration-goals.md)。Codex 可调用 `$dojo-integrate-model`；其他 Agent 可直接阅读同一 SKILL.md。先阅读 Dojo 框架、模型原仓库与论文，数据集、明确指标、对应源码三项齐备才考虑集成；原代码按论文设置复现通过后才正式迁移。已有记录按证据续接，技能调用不扩大本次授权范围。 阶段交付按 skill 追加[改进日志](.context/model-integration-learning.md)，区分事实错误与流程候选；后续更新遵循 skill 的三个部分，不把个案方法自动变成通用要求。

一般研究使用 [dojo-research](.agents/skills/dojo-research/SKILL.md)，无 skill 环境从 `DOJO_AGENT_GUIDE.md` 进入同一 [Agent Help Center](docs/agent-help/index.md)。首屏按数据、几何采样、模型、损失、训练恢复、推理、评价、后处理、run/Task 九类能力直达教程；这些菜单从能力教程元数据生成。先选能力和接入深度：单个工具直接调用；已有研究代码保留模型与科学目标，优先用公开批次/损失连接复用训练；需要完整流程才复制 standalone 并物化 extension。调用前核对现行签名、输入输出、设备和数值/恢复语义，适配成本小且语义一致时优先复用，具体缺口允许自定义并说明。需要运行记录时 direct-core；有版本、资产、后台、停止、恢复或比较需求时再用同目录 Task。CLI 是便利包装，读取帮助或导入成功不能替代真实调用和产物读回证据。

每次工作按以下顺序阅读，当前用户指令优先级最高：

1. `AGENTS.md`
2. `.context/index.md`：每次工作的仓库结构与功能检索入口
3. 与任务对应的 `.context/modules/*.md` 或 `.context/mvp/*.md`
4. 修改 recipe、案例配置或扩展入口时读取 `.cursor/rules/ai4e-recipe-authoring.mdc`。按目标 package 读取对应规则：算法包读 `ai4e-algorithm-architecture.mdc`，task 包读 `ai4e-task-architecture.mdc`，server 包读 `ai4e-backend-ddd.mdc`，Web 包读 `ai4e-web-architecture.mdc`
5. 写或改 PRD 时先读 `docs/PRD/README.md` 与 `.cursor/rules/prd-writing.mdc`；PRD 按 `docs/PRD/{包}/{模块}/PRD.md` 落文件，包与模块对齐 `packages/` 一级目录
6. 目标源码、调用方、产物契约、文档与测试

PRD 是模块功能的长期文档，须记录现行行为、设计原因、使用约定和迁移影响；按六节结构归入对应功能点，不另建平行功能说明。README/.context 负责导航，既有独立入口可保留跳转。

`docs/AI4E_Dojo_ARCHITECTURE (1).md` 是业务与代码架构设计文档，不是每次工作的必读文件。需要理解设计原因、整体数据流、Stage/Artifact/RunManifest/ExecutionBackend 或进行架构决策时，由 `.context/index.md` 按需进入。架构设计只在该文档维护；`.context` 负责索引当前仓库结构与文件用途，不复制第二份架构正文。

## 索引维护纪律

- `.context/index.md` 必须反映整个仓库的代码目录结构，并指向各模块上下文。
- `.context/modules/*.md` 必须列出对应模块的目录、文档路径及其含义，帮助 LLM 先定位再读取。
- 新增、删除、移动目录或文档，或改变文件职责时，必须同步对应模块索引和 `.context/index.md`。

## 修改与验收纪律

每次改动只针对本仓库，并遵守下面四条。未同时做到，不得视为完成。

1. **上下游整条链一起看。** 改一处必须想清谁提供输入、谁消费输出、中间交接什么、失败时谁感知。至少核对：调用方、被调用方、契约/配置、缓存或产物、文档读者。不得只改局部、默认上下游自己适应。
2. **同一改动必须带齐这些更新。** `AGENTS.md`（入口、边界或验收纪律受影响时）、`.context`、相关 PRD（按 `docs/PRD/README.md` 的模块目录补；没有则补上受影响模块的 PRD，不得只改代码）、以及测试用例。目录或职责变了还要按上面的索引维护纪律改模块索引。
3. **用相关测试验收，不跑全仓冒充验收。** 先圈定本次改动影响到的用例并跑通，才算验收。不要用全量测试代替「先圈相关用例」。尚无对应测试则先补再跑。用 `uv run --no-sync pytest <相关路径>`，不要先 sync。未跑通相关用例不得验收。
4. **有 Web 消费链则必须自己能在正式入口验收。** 源码测过、隔离 7999/5172 过了、标「待发布」都不算完成。官方 8000 读 `.venv` 安装副本；未按规定重装受影响 force-include 包并更新正式进程/Vis 时，正式 Web 根本验收不了。未获当次同意仍不得擅自重装/重启 8000/5173，但必须当时申请授权，工作停在未验收。细则见下文「发布与正式 Web 冒烟验收」。

**重点：改配置树必须走完整交接链，不得只改案例 YAML 和眼前几个装配文件。** 漏核下游会引入静默误判，不是“改完眼前再补”。至少核到这三组：

1. **加载与默认注入。** 配置加载、相对路径、从其他目录启动、`--set`、独立脚本和程序调用入口都要读新树；所有模型的默认采样/归一化必须写进新位置，禁止再注入旧顶层键。旧键拒绝须覆盖配置文件、`--set`、脚本和程序入口，并测新旧键同时存在。内部装配键（如 rawprep 的 `pre:`）与已废弃的案例阶段名不是一回事，禁止误拒绝。
2. **对照与选择器。** 对照工具与 task 比较选择器必须指向新路径。已声明的比较条件取不到值就是不可比，禁止填 `None` 或空对象后仍判相同。缺键禁止 `get(..., {})` 静默回到默认种子或预算。对照脚本若加载案例模块、调用阶段函数，必须一起改，不能只改阶段字符串。
3. **用户配置 ≠ 冻结产物。** 用户配置可以拒绝旧格式；历史准备产物只判断能否导入平台使用（可读、现行 `version=2`、摘要完整），不得在选中后再拿冻结声明去挡当前平台或 core 参数。计算按当前平台页面与 core 模板组配置，冻结记录只提供清单、统计和物化场；字段角色、数据规格、采样方法、模型字典或组件来源不同也不能因此拒绝跟踪、开训或推理。模型页采样预算（几何 `max_points`、超节点点数、域锚点点数）不属于准备冻结：新 `preparation.json` 的 `declarations` 不得写入这些键。随机种子和训练批次同样不参与导入判断。`version=1` 旧物理准备仍须按现行数据准备重新生成；检查点仍核权重结构，dim/blocks 对不上拒绝恢复该检查点。每一步只校验自己的输入，不得用后一步默认值卡当前步。已有历史证据文件保留原样。验收必须覆盖准备导入、轮次恢复、独立 post、归一化物化、task 资产与指标比较、其他模型工作流，以及实际 wheel 安装后的复制 recipe；不能只用几个 recipe 脚本测试代替。
4. **原始处理输入 / 处理配置 / 输出分开。** 输入是绑定数据集及其官方或自身分片，不因某次任务执行改写。页面只保存可见处理配置（字段、格式、workers、processed_name、全部或指定样本）。当次 run 或发布的样本名单只属于该次输出/历史，不得写回绑定源或下次 catalog/execute。`samples=all` 且页面未指定样本时读官方/自身分片，不吃任务里看不见的 `dataset.partitions` 子集。平台提交 ShapeNet 等非 NASA 案例时运行覆盖写 `unsplit`：产物不按官方 train/test 落盘，切分只在数据准备划分。准备记录固定带 train/test/eval 三个切片（空切片人数为 0）；训练设置选已准备数据集后再选其中切片，默认训练集；推理样本目录读这些切片，不回退源清单官方分片。打开、检查、提交或推理预检时写回缺的训练切片和旧 `validation` 别名，不新建研究版本，已显式选过的切片不覆盖；历史准备记录不改字节。`unsplit` 与 `official` 一样是分片模式名，配置加载不得把它展开成文件路径。页面上没有的键保存时不得改写。2026-09-18 无切分导入冒烟见 `.context/mvp/preparation-import-acceptance.md`；切片选择与旧任务写回见 `.context/mvp/prepared-slices-acceptance.md`。

本切片相关验收入口：

```bash
uv run pytest tests/integration/test_train_resolved_config.py tests/integration/test_train_test_repeat.py tests/integration/test_train_code_snapshot.py tests/integration/test_train_interrupt.py tests/integration/test_train_diagnostics.py tests/integration/test_train_optim_align.py tests/integration/test_train_entry_init.py tests/integration/test_train_shapenet_contract.py tests/integration/test_train_reference_stats.py
uv run pytest tests/integration/test_train_loop.py tests/integration/test_train_checkpoint.py tests/integration/test_train_recipe.py tests/integration/test_constraint_losses.py tests/integration/test_train_online_loss.py tests/integration/test_model_evaluation.py
uv run pytest tests/integration/test_post_inference.py tests/integration/test_abupt_recipe.py tests/integration/test_post_mesh.py
uv run pytest tests/integration/test_train_formal_two_epoch.py
```

## 技术基线

- Python 基线为 3.12；根 `pyproject.toml` 管理 uv workspace，成员以根 workspace 清单为准，含 spec/core/contrib/task/server/viz；Web 由 npm 管理。
- `packages/` 下每个包只保留一层物理目录；根 `pyproject.toml` 必须把连字符目录显式映射为下划线 Python 导入名（如 `packages/ai4e-core/` → `ai4e_core`），不得重新创建内部同名目录。
- 所有 Python、pytest、ruff、mypy 和 Sphinx 命令必须使用 `uv run`。
- `ai4e-web` 使用 ADR 0004 已确定的 React/TypeScript/Vite/Ant Design；依赖只进入 package.json 与 package-lock.json。
- 依赖只允许进入各生态的唯一清单；本阶段不得创建临时依赖文件。环境与 `uv sync` 纪律见上文「注意事项」。

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
- `applications/base` 只提供通用编排机制；领域 application 按 rawprep/trainprep/model/train/infer/post 组织标准业务装配，但不得感知具体 modeling/constraint 内部实现。

## 三类代码结构原则

- **算法包**：`ai4e-spec`、`ai4e-core`、`ai4e-contrib`，以及 `ai4e-viz` 现有算法库目录。严格遵循 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 给出的 base、abilities、applications、Stage 和 Artifact 划分，以高内聚、低耦合约束实现；跳出 DDD 的 `api/domain/application/infrastructure` 目录表象。
- **任务包**：`ai4e-task` 按 cli/projects/tasks/versions/templates/storage 六类功能组织，不套用 DDD；Python API 与 CLI 共用实现。
- **后端包**：`ai4e-server`。围绕 Project、Experiment、Run、Artifact、Job、Execution 等业务生命周期采用轻量 DDD；先划分限界上下文，再按真实需要在上下文内部区分 domain/application/ports/adapters，不建立全局空壳层。
- **前端包**：`ai4e-web`。按数据接入、recipe 配置、run、对比、报告等用户任务形成微领域；每个微领域自治，并通过稳定 server API 或 Artifact schema 交互，不镜像后端目录。
- 三类原则不能互相套用：算法不包装成贫血领域对象，后端不实现数值算法，前端不承担训练与物理计算。

## 分层与修改纪律

- 原子能力按 data、transform、geometry、sampling、modeling、constraint、training、inference、eval、postproc、report 分层。
- 能力归属默认进入 `ai4e-core/abilities`，按行为、输入输出和潜在复用判断，不按源码来源判断。来自单个模型源码的组件也必须先审查是否可中立化；只有依赖具体模型结构/私有状态、数据集字段或步骤/业务流且无法中立表达时，才放入 `ai4e-contrib/ability`。`contrib/application` 负责数据适配、配置和专属业务连接。新能力不确定时先将实际计算实现放入 core，再由贡献侧绑定语义；不等待多个使用者出现，不以 core 门面反向导入贡献算法。
- `data` 按六个阶段组织：`source` 来源读取与分片名单、`extract` 字段与记录、`validate` 对齐和输出门禁、`filter` 标记与筛选、`save` 张量读写与恢复、`stats` 数组流统计。不得恢复 clean/offline/online 的状态式划分。
- 原始来源存在网格或可重建 connectivity 时，平台数据必须同时交付逐场 PT、VTKHDF、实体身份和 manifest 网格引用；只有来源本身确实是无拓扑点云时才允许缺少 VTKHDF。模型需要的图边、诱导子图、核心分区和 halo 属于 trainprep 派生缓存，不写回共享平台数据。
- 同组字段声明来源、point/cell、实体数和原 ID 序列，无 mask 也必须校验行身份与数量；筛选统一更新组内字段与身份，点 mask 不适用于 CellData。编码器不猜组名后缀，`cell.pt` 是 recipe 的可选业务打包约定。
- `geometry` 保留完整 VTK，点到面与法向共用全二维面门禁，不抽取体外壳；按原 point ID 回贴法向，孤立点为零且有效性标记为 False。几何不依赖物理场，`pre.geometry.enabled` 显式选择，未启用不计算。`nearest_vertex` 只出最近距离，`volume_normals` 独立出体积法向。fields 可显式为空。
- 外流 rawprep 保留 read/derive/select/save/stats 单样本能力，由 dataset 模块提供按需装配。recipe 使用 datapre(cfg) 显式登记步骤，run 内封装样本循环，application 不反向导入 run。
- 样本发现与统计样本/字段/缺失策略属于 application；通用样本循环、首错/继续和汇总属于 `run/execute`。Stage/Pipeline 沿用现有顺序调用，不另建 DAG。任何样本失败都不能汇总为完整成功，首错停止保留之前提交结果且跳过统计。
- dry-run 与提交共用输出预检，针对实际样本目标检查覆盖；张量使用同级临时目录、旧目录备份、提升与失败恢复，遗留路径显式处理。重算统计只用本次成功结果的实际路径，逐数组流累计；dry-run 不扫描旧张量或写统计量。
- `run/writer` 独占运行配置、日志与摘要写入；runner 不解释 pre 路径或业务字段，业务通过 reports 交付摘要。预处理张量写数据目录。外流 train 已有的分片读取与表面零距离处理保留，正式模型构建、监督更新、评估和轮次恢复由 model/train 装配。
- 外流 recipe 按 rawprep/trainprep/model/train/infer/post 展开；infer 业务组合原子推理、评价与数据输出，post 消费固定结果。旧 post API 仅保留兼容调用语义，不能使新 post 静默重跑模型。recipe 不写算法或训练循环，PI-BSNet 等其他案例不因本次外流拆分自动迁移。
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

JOREK RMHD 双组实验使用 `tools/verification/dojo_validity/rmhd/` 独立协议：组级工作根隔离，round-00 的环境、原始数据准备和训练由各组新 CLI 会话实际完成。隐藏测试只由主控在双方最终候选冻结后评价；推理进程不持有真值且断网，评分器不执行候选代码。完整40帧推理 P95 上限50ms。圈定 `test_dojo_validity_rmhd.py` 与既有 `test_dojo_validity.py`、`test_dojo_validity_cli.py`，真实进度见 `.context/mvp/jorek-rmhd-validity-acceptance.md`；不以预实验或工具测试代替五轮正式结果。

单次改动的验收以「修改与验收纪律」第 3 条为准：先圈定相关用例；架构全仓对齐需复跑全部新增/修改测试并集及必要回归，最终代码变更后重新跑受影响集合。skip、失败、缺环境不能计为通过。下面是仓库门禁，不是每次改动都要跑完全部：

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/
uv run sphinx-build -b html docs/source docs/_build/html
```

不得用目录存在、import 成功或构建成功替代对应功能测试。发现并核实错误时按 `.cursor/rules/error-log.mdc` 记录；没有错误时不得制造日志。

## 可复制 Recipe 与 Dataset

Recipe 是研究者可阅读、可编辑、可扩展的流程正文。打开阶段脚本应能看清处理顺序、参数和交接；Python 决定顺序，YAML 提供参数。Application 提供业务步骤，ability 实现计算，run 承担通用执行与运行记录。

不以脚本行数少作为目标，不允许新模板退化成整段 workflow 转发。自定义能力通过公开接口接入，新增输出必须完成保存、读回和下游消费。

修改 recipe 时读取专项规则，并以“仓库外复制、接入用户能力、实跑交付下游”为验收项。五例允许明确的局部步骤差异；旧整段入口作为共用公开步骤的兼容包装。历史配置、准备、检查点和证据分别判断，不批量改写。

2026-09-11 显式流程切片已完成圈定验收：五例 CPU 小规模两轮、完整预测与旧检查点恢复逐值对齐；两个用户能力目录、真实 wheel 外部复制及相关平台回归通过。实际规模与验收状态见 `.context/mvp/recipe-explicit-acceptance.md`；下方历史切片记录只代表各自当时范围，不能作为新扩展已交付证据。

- `recipes/` 是普通模板集合，不是 Python 安装包；外流模板交付 README/config/configuration/rawprep/trainprep/train/infer/post/pipeline，不建 init/main、缓存或组件占位。
- `ai4e-contrib/application/datasets` 提供可安装的 manifest/adapter，recipe 可 import 或复制修改；core 不依赖 contrib。
- `${...}` 插值展开后按配置文件解析路径；数据根、各分片、normalize 路径和运行根独立可配。
- 原始 manifest 描述来源；产物 manifest 描述本次成功交付。统计默认仅用本次完整训练分片。覆盖开始撤下旧完整清单；部分失败不得继续发布完整清单。
- recipe 阶段日志使用 `[阶段/能力/事件]`（如 `[rawprep/数据集/选择结果]`）；运行入口设置并恢复阶段上下文，原子能力不感知 recipe，后台心跳显式继承阶段与样本身份。阶段边界使用 `[rawprep/阶段/开始]`；整体运行及无阶段的独立调用不强加阶段前缀。循环原子默认 debug，整轮只保留阶段/批量摘要与稀疏进度；失败仍为错误。writer 统一写入并按事件元信息筛选控制台摘要，默认不写 debug。
- inputs 只保存一份最终生效 config.yaml；日志包含能力/工作流开始结束与长任务进度，不倾倒配置、数组和整批结果。
- 归一化正反变换、冻结记录与可选物化已实现；prepare/fit 对物理输入必须显式 execute=true。正式网络小规模拟合与恢复已验收，复制案例短训与恢复已验收，生产规模训练不在本期范围。训练设备默认 `auto`，无加速器时警告后继续用 CPU，MPS 的邻域检索显式经 CPU，复数旋转保持原设备。
- PRD 增加 `docs/PRD/recipes/{案例}/PRD.md` 作为非安装模板集合的对应位置。

## Task 本地切片验收

相关用例：`uv run pytest tests/integration/test_task_management.py tests/integration/test_task_assets.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py tests/integration/test_task_recipe.py tests/integration/test_task_documents.py tests/integration/test_task_installation.py`。安装用例构建实际 wheel；运行和既有 core 的相关回归范围见 `.context/mvp/task-acceptance.md`。不可用全仓测试代替这些接口、资产和真实案例验收。

服务器操作手册：`docs/aero-cfd-server-runbook.md` 记录五案例 CUDA/50 epoch 配置、物理清单迁移、独立阶段与报告格式；这是待执行操作说明，不代表服务器验收。报告不再写死单轮，预算以源运行产物为准；相关验证为 `test_comparison_visualization.py`。

五例50轮实跑进度见 `.context/mvp/cross-model-50-acceptance.md`；测试 `test_cross_model_acceptance.py` 支持 `DOJO_CROSS_MODEL_EPOCHS` 与 `DOJO_CROSS_MODEL_DEVICE` 显式预算，默认仍为历史1轮MPS。执行中不得宣称报告完成。

## Web / Server 圈定验收

```bash
uv run pytest tests/integration/test_web_project_task.py tests/integration/test_web_rawprep.py tests/integration/test_web_rawprep_handoff.py tests/integration/test_web_research_records.py tests/integration/test_web_runtime.py tests/integration/test_web_architecture.py tests/integration/test_viz_file_preview.py tests/integration/test_task_configuration.py tests/integration/test_task_management.py tests/integration/test_task_execution.py tests/integration/test_web_design_documents.py
npm run --prefix packages/ai4e-web build
npm run --prefix packages/ai4e-web check:architecture
npm run --prefix packages/ai4e-web test:e2e
```

真实样本缺失导致 skip 时不得声称真实链路完成。当前安装采用单层 wheel 映射，源码变更后核对安装副本或重装受影响包。

本机平台已完成一份真实 ShapeNet-Car 样本的页面执行、PT/VTKHDF 文件预览和原数据准备读取；48 项圈定后端用例与三条浏览器流程通过。仅声明上述范围，尚未开放批量及其他工作台执行。详见 web-rawprep-acceptance.md。

## 本机训练与缓存存放约定（2026-09-10）

用户指定后续训练相关文件统一放在 `/Users/zonghui/work/project_simulation/`；Dojo 使用其下 `dojo_train/`。新建实验时显式将运行、检查点、预测、比较报告及本次产生的数据/准备产物写入 `dojo_train/<实验名>/`，相关工具缓存也放在 dojo_train 下，不再新建到 `/private/tmp`。使用明确的 run_root、数据输出与缓存路径实现，不将本机绝对路径硬编码进可移植框架默认值。已有输入数据与历史冻结记录不批量改写；旧 tmp 位置的兼容符号链接仅用于历史引用，新配置直接使用真实目录。

## 本机正式入口与 Agent 测试端口（2026-09-16）

`8000`（API）与 `5173`（Vite）由用户自己启动、停止和重启，供用户并行测试。Agent 不得 kill、重启、改绑或占用这两个端口；未获当次明确同意，也不得对正在使用的正式环境执行会打断服务的 `uv sync --reinstall-package`。用户未说「重启 8000 / 5173」时，即使改了 Python 包也不自动重启正式入口。没有授权时正式冒烟做不了，交付只能停在未验收，必须当场申请，不能默认为结束。

Agent 需要本机另起服务核对时只用 `7999`（API）和 `5172`（前端），独立进程、独立端口，不代理、不覆盖正式入口。前端 HMR 只作用于用户自己的 5173；8000 无热重载，装新包或重装 force-include 包不会更新已运行的正式进程，旧 Vis 子进程仍是旧代码。正式入口的后处理依赖纪律见上文「注意事项」。

圈定 pytest / e2e 默认仍用夹具，不依赖 8000/5173。隔离 7999/5172 的证据只证明隔离入口，**不能替代** Agent 自己在正式 8000/5173 上的冒烟。有 Web 消费链时，验收步骤就是在用户实际入口操作，不是占用端口写隔离记录后收工。


整合平台圈定验证：主 Agent 使用 `uv run pytest tests/integration/test_web_integrated_pipeline.py tests/integration/test_web_platform_operations.py tests/integration/test_web_project_task.py tests/integration/test_web_research_records.py tests/integration/test_web_runtime.py tests/integration/test_web_architecture.py tests/integration/test_web_design_documents.py tests/integration/test_task_configuration.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py`。文件交接另圈 `test_web_rawprep.py`、`test_web_recipe_compatibility.py`、`test_web_rawprep_handoff.py`、`test_viz_file_preview.py`、`test_viz_pipeline.py`、`test_viz_extended.py`。真实四组合、模型大小、样本预算与浏览器证据统一见整合验收记录；不以少样本正式网络短训声明生产规模精度。

任务创建与数据绑定修正：新建明确选择案例，原始处理「修改绑定」选择 contrib 公开数据集及本机完整副本，一次接上处理方式与受控地址；配置编辑不新增版本，未绑定或失效来源不可执行。历史缺 `components.dataset` 的外流任务按 NASA 文件键或模板默认目录识别，绑定接口不再因缺声明返回 400。相关验收使用 `uv run --no-sync pytest tests/integration/test_web_dataset_binding.py tests/integration/test_web_binding_real.py tests/integration/test_web_stage_consistency.py tests/integration/test_web_project_task.py tests/integration/test_task_configuration.py tests/integration/test_web_rawprep.py tests/integration/test_web_rawprep_handoff.py`（真实绑定显式指定 `DOJO_BINDING_REAL_ROOT`），以及 `packages/ai4e-web/e2e/task-dataset-binding.spec.ts`、`rawprep-consistency.spec.ts`、`home-entry.spec.ts`、`project-task.spec.ts`、`navigation.spec.ts`。单层force-include包修改后刷新可编辑安装，再核验安装源码；不要让普通同步复用旧构建替代当前源码。

PI-BSNet 文献参数验证：参考配置不得额外加入原目标没有的初值/周期罚项；完整 PDE 网格包含初边界。论文优先、源码补缺，不调参掩盖精度失败。新增圈定 `test_pibsnet_physical_reference.py`、`test_pibsnet_reference_protocol.py`，当前 Neumann 精度失败及正式运行见 `.context/mvp/pibsnet-acceptance.md`。

平台一致性切片（2026-09-14，圈定验收通过）：任务表与工作台共用真实阶段摘要；检查、试跑、执行和结构生成先保存修订，固定绑定保存在原配置。阶段文件限定清单/运行，PT/Zarr互斥、VTKHDF独立附加；导航不推断完成。数据准备字段按模型 `data_specs` 与物理清单下拉匹配并校验张量形状。圈定 `test_web_stage_consistency.py`、`test_web_platform_operations.py`、`test_web_binding_real.py`、`test_web_rawprep_handoff.py` 与受影响项目、配置、运行、资产、架构及文档测试；浏览器圈定 `stage-consistency`、`stage-files`、`rawprep-consistency`、`prototype-consistency`、`execution-monitor` 及首页/任务绑定回归。当前证据见 `.context/mvp/web-integrated-results/ui-consistency/`，夹具不算真实数值交接。

模型设置进页（2026-09-17）：已保存参数随配置先出，不必等候选列表；`model-options` 只读官方 YAML 与预设目录，点选再描述目标默认值与能力，同任务短时复用。不把结构跟踪或全量核验准备产物当作列出下拉的前提。圈定 `test_web_stage_consistency.py`、`packages/ai4e-web/e2e/model-picker.spec.ts`。改 `ai4e-server` 后须重装该包，正式 8000 才出快目录。

模型设置两档结构图（2026-09-18）：可视化模块按官方 TorchVista 参数一次写出阶段主干与阶段压缩块；网络公开编码器/几何块/物理块/解码/读出时，先按这些子模块收成阶段盒再出图，不跟踪正式 predict 里的校验算子。检查进程在案例检查取出网络后引用 viz 出图，core 不写 HTML、不设看图参数。页面两按钮切换已发布档，生成或载入时视窗只显示加载样式；历史单图不假切换。圈定 `tests/integration/test_algorithm_platform_contract.py`、`tests/integration/test_viz_model_graph.py`、`packages/ai4e-web/e2e/model-inspection.spec.ts`。2026-09-18 15:08 按当次授权重装 `ai4e-viz` 并只重启 8000（PID **5784**，5173 未动）；对照任务重新生成后阶段主干 17 节点与 E 一致，阶段压缩块见 encoder/物理块与 REPEAT，无 isfinite。证据 `.context/mvp/model-picker-acceptance.md`。

推理 VTK 与后处理对照（2026-09-17）：平台推理默认写出 VTK（锚点场名 `.prediction`/`.truth`，完整网格 `pred_`/`gt_`）；用户关闭导出须在清单、日志和页面写明原因。缺拓扑或点数对不上则该样本失败，原因进清单，整批不冒充全部成功。后处理结果文件并列平台数据集、训练 run 与推理批次，样本 ID 用 `param1/<设计号>`。圈定 `test_infer_vtk_identity.py`、`test_infer_stage.py`、`test_task_post_results.py`、`test_post_mesh.py`、`e2e/post-files.spec.ts`。正式 8000 须重装 `ai4e-core`/`ai4e-server`/`ai4e-contrib`/`ai4e-task` 并重启后才生效。源码圈定 133 项通过、2 项跳过，e2e 29 项通过。2026-09-17 23:50 已按当次授权重装并只重启 8000（PID 33633，5173 未动）；对照任务五页冒烟通过：全部 889、准备可见归一化副本、模型参数先出且点数不挡检查、推理仍报权重结构、后处理三根与「未写出VTK」。新默认网格因结构不对未新跑，历史关网格批次不回写。证据 `.context/mvp/post-workspace-acceptance.md`。

推理点云与网格化导出拆分（2026-09-18）：ability 只提供通用 VTK 写出与拓扑种类；application 按数据集适配 VTK/VTKHDF/连接关系，并判断网格化能否还原；recipe 只调用 application。页面两项为「导出点云数据」「导出VTK网格化数据」，默认勾选且含真值。置灰只认来源文件名或已绑定连接关系路径，不认空槽位或原始处理 VTKHDF 输出开关。样本接口必须带 `vtk_exports`，服务列样本不得丢掉；页面缺该字段按不可用。旧键/新键只在契约包解释一份，HTTP 未写的新键不得先填成开。圈定 `tests/integration/test_infer_vtk_exports.py`、`test_web_inference.py`、`test_infer_compatibility.py`、`test_infer_vtk_identity.py`、`test_infer_stage.py`、`packages/ai4e-web/e2e/inference-layout.spec.ts`。正式 8000 须重装 `ai4e-spec`/`ai4e-core`/`ai4e-server` 并只重启 8000 后才验收。


## 独立可视化应用迁移（2026-09-14）

`ai4e-viz` 包含原 AI4E_Vis 十三模块、JSX 前端、完整规则/索引/文档/资源及原 Dojo 库。包内应用读 `packages/ai4e-viz/AGENTS.md` 和根 `ai4e-vis-*` 规则入口：后端轻量 DDD、前端微领域；原 inspect/preview 等库仍按算法能力组织。Vis 只依赖 spec，不导入 task/core/server。

任务公开 `visualization_storage` 提供受控任务目录，server 经独立 Vis 进程交付上下文。配置保存在 `tasks/<task>/visualizations/<id>/asset.json + revisions/<revision>/spec.json`，图片/视频/CSV 仅显式导出到 exports。保存不复制原数据、不自动截图、不改任务版本、研究配置或 runs。项目上下文逐请求传递，不能用进程环境变量切换目标任务。宿主iframe只在拿到会话地址后渲染；重开先关闭再创建，满员先回收无心跳空闲会话。

圈定验收入口：`tests/integration/test_viz_host_bindings.py` 与 `packages/ai4e-viz/backend/tests/modules/test_vis_asset_storage.py`、`test_phys_filters.py`、`test_phys_session.py`、`test_vis_exports.py`。完整迁入、统一配置资产链路、三维功能分别报告；当前事实见包内 `docs/migration/dojo-integration.md`，不可用目录或构建替代真实浏览器/视频/数值验收。

Vis迁移验收（2026-09-14）：原393份治理/源码/资源按清单迁入，具体范围见 `.context/mvp/vis-migration-acceptance.md`。新可视化保存仅写任务visualizations配置修订，显式导出独立提交。独立应用按包内轻量DDD/前端微领域规则治理；旧viz库仍按算法边界。Linux阴影和完整科研页面新链路不得用本机构建或组件验收替代。

## 数据集声明驱动原始处理（2026-09-14）

历史任务兼容：页面映射比较代码语法与已核验版本；格式/注释不阻断，已知旧配置加载入口消费完整有效默认值。逻辑/入口变化继续拒绝并列出文件。冻结任务未声明 `operations.inspect` 时回落现行平台检查入口，不改写 `task-entry.json`。圈定 `test_web_recipe_compatibility.py`、`test_web_rawprep.py`、`test_web_architecture.py`，旧任务脚本与创建快照不自动替换。

ShapeNet-Car/NASA 的 manifest 提供默认处理参数、字段与绑定槽位；Web 展示生效配置并按样本执行，文件浏览不再决定新入口的执行范围。描述和校验经 task 独立检查，server 不导入数据集；旧文件请求、容器和历史产物分别兼容。新输出为逐场张量且清单记录实际布局，缺失字段不能冒充可训练。验收见 `.context/mvp/manifest-rawprep-acceptance.md`；圈定新 descriptor/configuration/catalog/selection 用例及真实 `test_manifest_rawprep_real.py`、`manifest-rawprep-real.spec.ts`，同时回归 recipe、扩展、安装、配置、绑定、物理读盘与恢复。真实数据用例不接受 skip 作为通过。

三维对象工作台（2026-09-14）：Trame 基于用户确认布局重构；导入自动创建纯色基础显示，着色是对象属性，不预建压力/温度节点。计算参数应用后生效，显示设置即时更新；物理配置版本 2 的旧版适配不重写历史修订。流线可选线段/球体/平面/命名面起点，本期暂时不做拖种子，应用后可用「显示种子」隐藏；显示可选线或圆管；切面与剖切选中时用可视平面三向拖动和轴对齐，拖动只预览、应用才切开。验收入口为 `.context/mvp/phys-workbench-acceptance.md`、`test_phys_objects.py`、`viz_objects_browser.cjs`，不以旧界面浏览器记录替代新工作台验收。 真实 ShapeNet/NASA 表面结果补充验收与裁剪面/Probe/CSV 修复见同一记录；新增入口 `viz_real_results_browser.cjs`，不以静态表面结果声明生产体场时序或并发性能。

三维参考图样式校正：圈定 `tests/integration/viz_visual_browser.cjs` 的真实四尺寸截图，并联验 `viz_objects_browser.cjs`、`viz_real_results_browser.cjs`；视觉与物理计算分别验收，记录见 `.context/mvp/phys-workbench-acceptance.md`。

Web服务响应错误回归：`packages/ai4e-web/e2e/http-errors.spec.ts` 圈定空代理响应、网络断开、业务detail、无效成功正文与204；不得用空数组掩盖服务失败。恢复原平台后另以真实项目列表验证。

平台默认三维入口修正（2026-09-14）：网格文件预览和后处理直接打开 Trame，已有旧场景显式兼容。任务上下文自动带入，未选结果允许空工作台内导入；关闭预览和平台路由退出释放所属会话，迟到响应也须回收。网格预览弹窗默认加高，可放大到视口全屏；放大后对象树、属性和三维窗口须露出，属性框可滚动。后处理三维页相对原 820px 至少加高 40% 并尽量铺满剩余视口，嵌套 iframe 贴合该窗口，不能只剩工具条和白底，页面可向下滚动。宿主不再放「打开已保存配置」下拉。原始处理字段提取按每个 `.pt` 一张卡片，对话框只勾选一个物理量或坐标；再点执行立刻清掉完成态和进度条，日志同页叠加。圈定 `packages/ai4e-web/e2e/trame-entry.spec.ts`、`preview-dialog.spec.ts`、`rawprep.spec.ts`、`rawprep-consistency.spec.ts`、`manifest-rawprep-real.spec.ts`、`http-errors.spec.ts` 与 `tests/integration/test_viz_host_bindings.py`；真实项目/任务环境变量缺失导致 skip 不算实际入口验收。证据见 `.context/mvp/phys-workbench-acceptance.md`。

案例驱动的架构比较参考：`docs/ai4s-framework-comparison.md`；比较建议仍须由真实案例需求触发，不能当成已交付能力。

## GenCP 代码接入（2026-09-16，缩小验收完成）

新增 core coupled_physics 领域、contrib GenCP 模型/条件能力及可复制 recipe，不涉及平台登记。每场独立训练、writer namespace 检查点、固定权重组与异形时空数组交接；旧检查点默认路径兼容。三套数据×两骨干各场 1,000 次更新通过缩小对照，含准备/重试和共享验证预留的最长组合 113.42 分钟；107 项相关测试通过，含实际 wheel 外部复制、条件替换、派生输出和单场重训重新组合。不能把缩小实验工程一致称论文复现。圈定 `test_gencp*.py`、能力文档、训练/检查点、推理随机状态、固定用户 API 和实际安装；证据与未验边界见 `.context/mvp/gencp-acceptance.md`。


工作台色标、Probe 与视图联动（2026-09-17）：色标入口在属性「显示设置」图标，弹层带对象名和「应用」，只写当前选中对象；Probe 点选只留一个开关；加号菜单贴按钮；点窗切活跃并刷新左侧眼睛；折线图树只列线段提取；去掉取样物理量。圈定 `test_phys_display_settings.py`、`test_phys_interaction.py`、`test_phys_display_updates.py`、`test_phys_plot_over_line.py`、`test_phys_views.py` 与前端 `interaction.test.js`。色标下移后须再重装并换 Vis 才能在正式入口看到。证据见 `.context/mvp/phys-workbench-acceptance.md`。

Surface LIC 远程交接防崩（2026-09-17）：选 Surface LIC 先出远程静帧再开拖转；无向量、建图或第一帧失败只提示并回退，不切半套远程、不弄死会话。圈定 `test_phys_display_settings.py`、`test_phys_display_updates.py`、`test_phys_views.py` 与前端 `interaction.test.js`。18:42 已重装并换 Vis，正式后处理三维页点 LIC 后会话仍在，缺向量只提示。证据见 `.context/mvp/phys-workbench-acceptance.md`。

Probe 点选拾取可见开关（2026-09-17）：Probe 属性「点选拾取」开/关；开着点模型出球、应用出表，关着不拾取。切到其他工具开关回到关。圈定 `test_phys_interaction.py`。已重装 `ai4e-viz`，正式 8000/5173 须用户重启后才能冒烟。

三维工作台十二项优化（2026-09-17）：切面命中才锁相机且不挡缩放，色标入口改到右上角弹窗，矢量只留固定/物理量两档，等高线界面无自定义等值。圈定 `test_phys_display_settings.py`、`test_phys_filters.py`、`test_phys_interaction.py`、`test_phys_views.py` 与前端 `interaction.test.js`。正式8000/5173不自动更新。

三维工作台十一项增强（2026-09-17）：Surface LIC 仅该项走服务端出图；切面默认皱折、可选三角化，剖切提供皱折；流线本期暂时不做拖种子、应用后用「显示种子」隐藏，显示可选线或圆管；本地坐标轴在轨道中实时跟转；导入在任务产物/共享数据/数据根内选网格；等值滑条可越界手填；色标允许最小等于最大；Probe 即刻出球、应用后出表；分析图标缩小并增加线段提取。圈定 `test_phys_display_settings.py`、`test_phys_filters.py`、`test_phys_interaction.py`、`test_phys_views.py`、`test_phys_objects.py`、`test_phys_plot_over_line.py`、`test_viz_host_bindings.py` 与前端 `interaction.test.js`。正式 8000/5173 须当次同意。证据见 `.context/mvp/phys-workbench-acceptance.md`。

三维交互与对象隔离（2026-09-16）：新对象计算和显示草稿一起提交；辅助平面独立显隐，三轴平移与三轴旋转仅命中手柄启动；删除局部清理不重建背景和相机。种子和Probe有候选预览，等高线支持自动分层，同标量等值面保留生成标量。圈定 `test_phys_interaction.py`、`test_phys_objects.py`、`test_phys_display_updates.py`、`test_phys_filters.py`、配置/存储用例与 `viz_interaction_browser.cjs`；最终范围见根 `.context/mvp/phys-workbench-acceptance.md`，正式8000/5173不自动更新。

着色与显示设置（2026-09-16）：属性计算/显示均应用后生效，顶部快捷操作只提交自身字段；映射器更新必须显式替换输入，不能以标量可见或色标变化代替模型像素验收。色标、范围和背景可保存，透明PNG/序列读回校验alpha。圈定 `test_phys_display_settings.py`、显示/对象/过滤器/配置/存储用例及真实本地、远程与宿主浏览器；源码、隔离安装、正式发布分别记录，正式8000/5173不自动更新。


## 发布与正式 Web 冒烟验收（硬规则）

- 每份实施计划必须把「发布到实际使用入口」与「Agent 自己做正式 Web 冒烟」写成两项独立硬验收，写明目标地址、受影响功能、发布方式、回退方式与证据位置。纯文档或没有 Web 消费链的改动可写不适用，但须说明理由；有 Web 消费链的后端、Vis 改动不能免。
- Agent 必须自己在用户实际 5173→8000 做正式冒烟。源码测过、隔离 7999/5172 过了、接口 200、构建成功、隔离截图、标「待发布」都**不是**验收完成。
- 官方 8000 读 `.venv` 安装副本，不是 `packages/`。未对受影响 force-include 包执行规定的 `uv sync --group dev --group visualization --reinstall-package <包>`，正式 Web **验收不了**。8000 无热重载；改 `ai4e-viz` 还须回收/重启后旧 Vis 子进程才换新代码。只刷新 5173 不够。
- 开始先确认用户实际入口、安装路径和运行版本；交付前逐层核对源码/构建 → 安装副本 → 运行进程/旧会话 → 浏览器加载资源。源码、隔离安装与正式生效分别记录，不能互相替代。
- 获得授权并完成发布后，Agent 从用户实际 Web 入口进入受影响页面、实际操作每项改动、核对可见结果及错误反馈；涉及保存则保存后重开，涉及导出则下载读回。
- 验收记录须含时间、入口 URL、部署版本或文件摘要、运行进程/会话身份、逐项操作和结果、截图及必要日志；每项明确通过、失败或未验证。不得沿用旧版本截图证明新版生效。
- 正式 8000/5173 的安装、重启或会话回收仍须本次用户授权；已有明确授权不重复询问。此规则本身不构成今后发布的长期授权。没有授权时先完成可审阅发布准备，**当时就申请授权**；在重装+进程/Vis 更新+Agent 正式冒烟完成之前，状态只能是未验收。「待发布」只描述卡在授权或发布，**不得当作可以结束的交付**。
- 用户反馈「没有生效」时，优先检查实际入口、安装版本、旧进程、会话及浏览器资源，先定位运行链路，再决定是否继续改代码。


## 共享训练执行与研究导航（实施中）

研究任务走 `.context/tasks/research.md`，模型接入仍走已有集成技能。轮次/更新入口默认兼容，局部策略不接管保存与数据流；共享重构不批量改写 Recipe/Example。逐个核验受影响入口，按独立训练语义圈定实跑，不逐例重复完整长训。每轮结束发布进行中训练报告、在线分项/测试评估分列和关闭评估仍有曲线的现行行为须保持。圈定 `test_training_execution`、`test_training_strategy_extensions`、原训练/模型恢复、固定公开基线、安装复制、导航文档与实际执行监控；源码、安装和正式入口分别记录于 `.context/mvp/training-execution-acceptance.md`，本轮最终去重256项通过、3项跳过，真实历史WDNO恢复另有逐值对照；用户已授权并更新 core/contrib、重启8000；正式页面开训、实时曲线/在线分项/测试评估与停止已实测。2026-09-18 08:41 按当次授权重装 `ai4e-core` 并只重启 8000（PID **34128**，5173 未动）；对照任务开训写出预测通过，run `b3d788acfa8a4392bb355229ff3647c9` 成功，不再走旧物理准备接口。停止运行的恢复候选修正已通过7项检查，追加 task 发布仍待当次授权，固定目标页面恢复未验收，整体未收口。


训练指标与曲线（2026-09-18）：现行外流训练设置可选实际计算的 MSE／MAE／相对 L2；未声明兼容原三项、清空只保留评估 Loss。运行页新增 Loss／更新步／学习率页签及空配置入口。圈定 `test_model_evaluation.py`、`test_train_loop.py`、`test_train_online_loss.py`、`test_train_recipe.py`、`test_public_api_stability.py`、`test_web_configuration_composition.py` 与 `e2e/execution-monitor.spec.ts`、`e2e/stage-consistency.spec.ts`。正式发布须当次授权更新 core/server 并重启8000；状态见 `.context/mvp/training-metrics-ui-acceptance.md`。

## PCNO 小数据集成实施（2026-09-20）

用户已授权24例、双分支各250轮的原版与Dojo代码对照，不含Web。当前参考工具、真实数据/经济回放和双分支首步对照通过，原版长训练进行中；尚未交付正式PCNO模型。继续前读 `.context/mvp/pcno-acceptance.md` 与 `.cursor/plans/pcno-small-data-integration.plan.md`，不要重复启动既有250轮运行，不以单步/首轮通过替代完整基线。实时状态及后续预测链位于 `dojo_train/pcno/reference/`。圈定前置测试为 `test_pcno_data.py`、`test_pcno_reference.py`、`test_pcno_reference_prediction.py`、`test_pcno_reference_artifacts.py`；它们不代表未来Dojo/Task/wheel验收通过。

## PCNO 本机快速集成

用户已改为先迁移、后短训，原250轮任务停止；模型组合与数据语义在contrib，主要计算在core。圈定 `test_pcno_*.py`、共享训练/API以及案例/Task安装回归。原版温度训练有非有限梯度问题，必须区分原版失败证据与显式数值修正参考，不以同为NaN判一致。范围与当前证据见 `.context/mvp/pcno-acceptance.md`。本次无Web消费链。


## Neumann 双组有效性实验

实验会话工作根分别为 `dojo_train/neumann-plain/` 与 `dojo_train/neumann-dojo/`，本次实验各自位于独立的 `experiment-UUID/`；不绑定共同父目录或互相读取。baseline、环境与产物独立，比较资料仅主会话访问；可选前提材料只读且位于两组根外。Dojo 组使用本组复制的 `DOJO_AGENT_GUIDE.md` 和 Agent Help Center，首次文档学习计入成本。正式五轮必须有覆盖整个会话的访问隔离和真实计量，命令沙箱或 fake runner 不能替代。工具与圈定用例见 `.context/modules/repository.md`，当前阻塞/实测见 `.context/mvp/dojo-validity-acceptance.md`。本验证工具不涉及正式 Web 服务，不为此 sync 或重启 8000/5173。

Neumann 双组实验正式 CLI 由整进程 Seatbelt 限定各组工作根，专用 Codex 状态与工具副本保存在组内；CLI 内部沙箱关闭仅避免 macOS 重复施加，不能作为取消外层权限的选项。公网可用、本机服务与跨组读取须实测拒绝。正式会话和五轮完成状态见 `.context/mvp/dojo-validity-acceptance.md`，不以初始化成功代替完整实验。

## PCNO 圆柱变体

新增core二维时空谱/U-Net、连续性与窗口评价，贡献侧绑定Double Cylinder五训练/一验证轨迹。实际短训、安装及扩展证据见`.context/mvp/pcno-cylinder-acceptance.md`；CylinderFlow官方8/2/2轨迹已取得，P1散度未通过准入，未开放训练。仅Python/Task，无Web登记，不改变地热PCNO验收边界。
