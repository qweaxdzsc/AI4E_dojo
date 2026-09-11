# AI4E_Dojo

面向 Engineering AI / AI4S 的研究框架。仓库分两层入口：

- **使用者**：复制案例、改路径、跑四阶段流水线；需要版本树时再用 `ai4e` 管项目。
- **开发者**：在 uv workspace 里改 `packages/`，按模块索引和验收纪律提交。

Python 3.12。命令一律在仓库根用 `uv run`。

- [给使用者](#给使用者)
- [给开发者](#给开发者)

---

# 给使用者

用户入口是**复制一份案例配置，改路径后跑流水线**。不要在仓库源码树上直接当实验目录改。

## 安装

```bash
# 汽车 / AB-UPT
uv sync --all-packages --extra abupt --inexact

# 机翼 / Transolver-3
uv sync --all-packages --extra transolver3 --inexact
```

两种模型都要用时，把两个 `--extra` 写在同一条 `uv sync` 上。完整开发环境：`uv sync --locked --all-packages --all-extras`。

## 选案例并改路径

| 案例 | 复制这个目录 | 依赖 extra |
|---|---|---|
| ShapeNet-Car + AB-UPT | `examples/aero_cfd/shapenet_car_abupt/` | `abupt` |
| NASA CRM + Transolver-3 | `examples/aero_cfd/nasa_crm_transolver3/` | `transolver3` |

打开复制后的 `config.yaml`，至少改这三项（脚本目录、数据目录、运行目录必须分开）：

```yaml
dataset.root: /你的原始数据根
data_root: /你的产物根          # 张量、统计、预测、网格
run_root: /你的运行记录根        # 配置快照、日志、检查点、摘要
```

`--set dataset.root=...` 可临时覆盖。相对路径按**配置文件所在目录**解析。字段细节见 [recipes/aero_cfd](recipes/aero_cfd/README.md)。

## 跑起来

```bash
uv run --no-sync python /个人实验目录/pipeline.py --check
uv run --no-sync python /个人实验目录/pipeline.py
```

默认顺序：`rawprep → trainprep → train → post`。分阶段：

```bash
uv run --no-sync python /个人实验目录/rawprep.py
uv run --no-sync python /个人实验目录/trainprep.py
uv run --no-sync python /个人实验目录/train.py --set train.preparation=/某次trainprep运行/artifacts/preparation.json
uv run --no-sync python /个人实验目录/post.py --set post.checkpoint=/某次train运行/checkpoints/last.pt
```

- `--set key=value`：覆盖配置（可多次）
- `--check` / `--dry-run`：只预检
- `--overwrite`：允许替换已有产物（默认不覆盖）
- `--continue-on-error`：样本失败后继续，整次运行仍算失败

`train.device` 默认 `auto`（CUDA → MPS → CPU）。Apple GPU 请在复制后的配置里写成 `mps`。

## 结果在哪看

| 你要找的 | 位置 |
|---|---|
| 本次生效配置 | `<run_root>/<本次运行>/inputs/config.yaml` |
| 日志 | `<run_root>/<本次运行>/logs/run.log` |
| 训练摘要、检查点 | `<run_root>/<本次运行>/artifacts/training.json`、`checkpoints/{best,latest,last}.pt` |
| 后处理进度（失败时先看） | `<run_root>/<本次运行>/artifacts/post-progress.json` |
| 预处理张量与清单 | `<data_root>/manifest.json`、`train/` `test/` |
| 预测与网格 | `<data_root>/predictions/` |

已有数据时，`pipeline.stages` 可写成 `[trainprep, train, post]`。

## 用项目管多次实验（可选）

```bash
uv run --no-sync ai4e project new /个人项目/study
uv run --no-sync ai4e new baseline --project /个人项目/study --from recipes/aero_cfd
uv run --no-sync ai4e run TASK_ID --project /个人项目/study --wait
uv run --no-sync ai4e tree --project /个人项目/study
uv run --no-sync ai4e compare runs RUN_A RUN_B --project /个人项目/study --save
```

只有 `new` / `fork` 创建正式版本；改工作目录或再次 `run` 不增加版本。完整命令见 [ai4e-task](packages/ai4e-task/README.md)。

管理库是 SQLite：`<project>/.dojo/task.sqlite`。它只记项目、任务、版本和运行索引，不在本 git 仓库里。检查点、网格、预测在该项目的 `tasks/<task_id>/data/` 与 `runs/`。直接跑 `pipeline.py` **不会**建这份库。缺库文件时打开项目会失败，不会自动建空库；备份请带走整个项目目录。

## 使用者需要知道的边界

已交付：外流四阶段、AB-UPT 结构版本 3、Transolver-3 正式规模对标、锚点评估与完整网格回贴、本地 task。

整合 Web / Server 已接入真实项目任务、阶段配置与运行、TorchVista 和有限 VTK 工作区；四组真实数据/模型短训与产物交接证据见 [整合平台验收](.context/mvp/web-integrated-acceptance.md)。启动见 [服务端](packages/ai4e-server/README.md) 与 [前端](packages/ai4e-web/README.md)。

未交付：物理约束、生产规模训练、正式报告、批量派生和排队。有限 VTK 工作区不等同完整 ParaView。旧公开 Transolver 配置兼容政策未定。

---

# 给开发者

这里是仓库怎么组织、改哪里、怎么验收。细则在 [AGENTS.md](AGENTS.md)，不要把本页当成第二份架构正文。

## 仓库结构

```text
AI4E_Dojo/
├── packages/           正式包（单层物理目录，导入名为下划线）
│   ├── ai4e-spec       稳定契约；不依赖其他 ai4e 包，不依赖 torch/numpy
│   ├── ai4e-core       原子能力、业务装配、run 唯一写入
│   ├── ai4e-contrib    共享数据集与完整模型
│   ├── ai4e-task       本地项目 / 版本 / 执行（不套 DDD，不导入 recipes）
│   ├── ai4e-viz        占位
│   ├── ai4e-server     占位
│   └── ai4e-web        占位；技术栈未定，不得先选前端框架
├── recipes/            可复制模板，不是安装包
├── examples/           汽车与 NASA 两个配置案例
├── tests/              contract / integration / regression
├── tools/              对照与仓库维护，不承载框架运行
├── docs/               架构、ADR、PRD
├── .context/           模块与 MVP 检索索引
└── AGENTS.md           开发入口、边界、验收纪律
```

uv workspace 成员目前是 `ai4e-spec`、`ai4e-core`、`ai4e-contrib`、`ai4e-task`。`packages/ai4e-core/` 映射为导入名 `ai4e_core`，不要再套一层同名目录。

`user_project/`、`dos/` 若出现，只作历史迁移参考。新 packages **不得导入 Noether**；对照行为要回到源码、产物和测试。

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

`contrib` 通过与私有插件相同的组件契约接入。`applications/base` 只做通用编排；领域 application 按 rawprep / trainprep / model / train / post 装配，不感知 modeling / constraint 内部实现。`run/writer` 是运行目录唯一写入方。

三类结构原则不能混用：算法包按 abilities / applications / Stage；task 按 cli / projects / tasks / versions / templates / storage；未来 server 才用轻量 DDD，web 按用户任务微领域。

## 开发怎么开始

1. 读 [AGENTS.md](AGENTS.md)
2. 用 [.context/index.md](.context/index.md) 定位模块，再读 `.context/modules/*.md` 或 `.context/mvp/*.md`
3. 按包读规则：算法看 `ai4e-algorithm-architecture.mdc`，task 看 `ai4e-task-architecture.mdc`
4. 改功能时同步受影响的 PRD（`docs/PRD/{包}/{模块}/PRD.md`）、`.context` 和相关测试
5. 需要设计理由或全局数据流时再读 [架构文档](<docs/AI4E_Dojo_ARCHITECTURE (1).md>)

改一处必须看上下游交接（谁提供输入、谁消费输出、失败谁感知）。改配置树必须核加载入口、对照选择器、以及「用户配置 ≠ 冻结产物」。

## 常用命令

```bash
uv sync --locked --all-packages --all-extras
uv run pytest tests/integration/test_xxx.py    # 只跑本次相关用例
uv run ruff check .
uv run ruff format --check .
uv run mypy packages/
```

不要用全仓测试冒充验收。尚无对应用例就先补再跑。MPS 相关用例必须在真实 Apple GPU 上跑，skip 不算硬件验收。

## 文档与证据放哪

| 材料 | 位置 |
|---|---|
| 开发纪律与包边界 | `AGENTS.md` |
| 目录 / 模块导航 | `.context/index.md`、`.context/modules/` |
| 切片验收与 JSON 证据 | `.context/mvp/` |
| 产品行为与迁移 | `docs/PRD/` |
| 架构与已定决策 | `docs/AI4E_Dojo_ARCHITECTURE (1).md`、`docs/adr/` |

Git 只归档源码快照（`.git/objects` 的 blob / tree / commit）。task 的 SQLite 是运行时项目库，不进本仓库；`.venv/`、`runs/`、`outputs/`、各类缓存也不提交。
