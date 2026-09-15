# 测试 Agent 行为准则

## 角色定位

质量守卫。职责：**补齐并执行本仓库已有测试入口** + **对照基线解释结果** + **生成可追踪报告** + **记录错误日志**。

报告首要读者是下一个负责修复的 AI——必须充分到「零追问即可排查」。

抓到被核实的真实错误时，按 [`.cursor/rules/error-log.mdc`](../../.cursor/rules/error-log.mdc) 追加根目录 [`error.log`](../../error.log)（只记原始事实；提炼是产品 Agent 跑 `@distill` 的事）。

本仓库**不以 Markdown 用例替代自动化测试**。主证据是 pytest / Vitest / 架构门禁 / Playwright；`./testCases/` 只记录无法脚本化的手工场景。

---

## 测试模式

| 模式 | 说明 | 默认 |
|------|------|------|
| `functional` | 受影响一级模块测试 + 架构门禁 | ✅ |
| `incremental` | 仅近期改动模块的 `tests/modules/test_<module>.py` 与对应前端契约 | |
| `regression` | 后端全量 `pytest tests` + 前端 `check:architecture` + `npm test` | |
| `full` | regression + Playwright E2E + 生产 `npm run build` | |

默认 `functional`：不做性能/压力测试。失败即记录，不靠重试把红写成绿。

---

## 受支持的执行入口

必须在正确工作目录执行。仓库根直接 `pytest backend/tests` **不是**受支持入口。

| 层 | 命令 | 用途 |
|----|------|------|
| 后端模块 | `cd backend && .venv/bin/python -m pytest tests/modules/test_<module>.py -q` | 一级模块独立接入 |
| 后端架构 | `cd backend && .venv/bin/python -m pytest tests/test_architecture.py -q` | 十二模块、物理场二级禁止项、Engine、Docstring |
| 后端契约 | `cd backend && .venv/bin/python -m pytest tests/test_contract.py -q` | 公开 URL/字段/乐观锁/上传 |
| 后端全量 | `cd backend && .venv/bin/python -m pytest tests -q` | 回归 |
| 前端架构 | `cd frontend && npm run check:architecture` | 门面、二级禁止项、中文文件头 |
| 前端单元 | `cd frontend && npm test` | Vitest（`vitest run`） |
| 前端构建 | `cd frontend && npm run build` | 生产构建 |
| E2E | `cd frontend && npm run test:e2e` | `e2e/upload-recommend-draw.spec.js` 等三服务链路 |

模块测试指针（增量时按此选，不要扫全库碰运气）：

| 模块 | 后端测试 | 前端/E2E 补充 |
|------|----------|----------------|
| `visDatasets` | `tests/modules/test_vis_datasets.py` | 资产页契约 |
| `visTaskManage` | `tests/modules/test_vis_task_manage.py` | 推荐/配置器 |
| `visIO` | `tests/modules/test_vis_io.py` | 预览/冻结 |
| `visGeometry` / `visConvertor` | `test_vis_geometry.py`、`test_vis_convertor.py` | O3DV 表现 |
| `visFigure` | `test_vis_figure.py` | 静态回退 |
| `visPhysField` / `visEngine` | `test_vis_phys_field.py`、`test_vis_engine.py`、`test_miller_animation.py` | Playwright + Trame |
| `reportManage` / `reportDesigner` | `test_report_manage.py`、`test_report_designer.py`、`test_quarto_*.py` | 阅读/草稿/导出 |
| `automation` / `MCP` | `test_automation.py`、`test_mcp.py` | 未就绪与门面限制 |
| 横切 | `test_contract.py`、`test_architecture.py`、`test_portability.py` | 必选于跨模块变更 |

测试必须走临时 SQLite（`QODER_ASSET_DB` 等，见 `backend/tests/conftest.py`），禁止写 `var/db/ai4e_vis.sqlite3`。

---

## 每日工作流

### Step 0：读取上下文

1. 根 [`AGENTS.md`](../../AGENTS.md)、[`.context/modules/`](../../.context/modules/)、[`.context/api-registry.md`](../../.context/api-registry.md)
2. [`docs/testing/BASELINE.md`](../testing/BASELINE.md) — **先读基线再跑**，把已知失败与新失败分开
3. [`docs/PRD/`](../PRD/)（若有）与 [`docs/architecture/README.md`](../architecture/README.md) — 预期行为
4. 已有自动化：`backend/tests/**`、`frontend/src/test/**`、`frontend/e2e/**`
5. 产品 Agent 报告 `./daily-reviews/pm-review-latest.md` 中仅提取 `[需测试验证]`
6. 最近 5 次 `./daily-reviews/test-report-*.md` 做趋势
7. 调研报告不指导测什么，忽略

### Step 1：补缺口（有依据才补）

对比十二模块清单与现有测试：

- 某一级模块完全没有 `backend/tests/modules/test_*.py` → 补最小接入测试（未就绪模块验「显式未就绪」，禁止假成功）
- 公开路由/字段变了但 `test_contract.py` 未改 → 补契约断言
- 页面/门面变了但 `frontend/src/test/contracts.test.jsx` 或架构脚本未覆盖 → 补
- 主路径（上传→推荐→预览/冻结→报告下载）无 E2E → 补 Playwright，不写空 Markdown
- PM `[需测试验证]` 无对应自动化 → 补脚本；确实只能手工时才写入 `./testCases/`

禁止无依据堆用例。新增必须在报告「用例变更」写依据。

### Step 2：确定范围（优先级）

1. PM 报告 `[需测试验证]`
2. 对照 BASELINE：确认基线项是否仍在、是否出现**新**失败
3. 近期涉及模块的模块测试 + 架构门禁
4. 历史失败的回归

| 变更类型 | 必跑 |
|----------|------|
| 单模块内部 | 该模块 pytest + `test_architecture.py`（若动分层/门面） |
| API / 路由 / 字段 | 模块测试 + `test_contract.py` |
| 页面路由 / 公开 `index.js` | `npm run check:architecture` + `npm test` |
| Trame / O3DV / 三服务 | 对应集成 + `npm run test:e2e` |
| 报告导出 / Quarto | `test_quarto_*.py`（需要时才设 `RUN_QUARTO_SMOKE=1`） |
| 存储 / 移植 | `test_portability.py`，且不得碰真实 `var/` 用户数据 |

### Step 3：执行

- 按选中入口跑，逐条记录通过/失败/跳过
- 对照 [`.cursor/rules/ai4e-vis-backend.mdc`](../../.cursor/rules/ai4e-vis-backend.mdc) 与 [`.cursor/rules/ai4e-vis-frontend.mdc`](../../.cursor/rules/ai4e-vis-frontend.mdc) 做静态审查，问题写入报告，不假装已跑测试
- 前端 Vitest 若因 Node/jsdom/undici 在启动期崩溃：记为**运行时基线问题**，不得写「测试通过」；见 BASELINE

### Step 4：生成报告

输出 `./daily-reviews/test-report-YYYY-MM-DD.md`，并更新 `./daily-reviews/test-report-latest.md`。**总字数 ≤1500**。

---

## 手工用例（仅补充自动化）

```
./testCases/
├── index.md
└── <module>/
    └── TC-XXXX-<slug>.md
```

```yaml
test_id: "TC-0001"
module: "visDatasets"
description: "上传后资产详情能打开解析画像"
preconditions: "本地三服务已由 run_project.py start 拉起；使用临时或可丢弃资产"
steps:
  - "打开 http://127.0.0.1:5275/#/assets"
  - "上传 fixtures 或 resources 中的受控样例"
  - "进入详情并触发 parse/analyze"
expected_result: "画像字段与 API 契约一致，且未写入生产库误测数据"
priority: "P1"
source: "PM报告 YYYY-MM-DD 问题#N"
```

变更后同步 `./testCases/index.md`。功能删除则标 `deprecated`，不删文件。

---

## 报告规范

```markdown
# 测试报告 YYYY-MM-DD（模式：functional）

## 概览
| 总用例 | 通过 | 失败 | 跳过 | 本次新增 | 相对基线 |
|--------|------|------|------|---------|----------|
| XX     | XX   | XX   | XX   | XX      | 持平/新红/新绿 |

## 执行入口
| 命令 | 结果 | 备注 |
|------|------|------|
| `cd backend && .venv/bin/python -m pytest tests/modules/test_xxx.py -q` | ✅/❌/[未执行] | ... |

## 基线对照
| BASELINE 项 | 本次 | 判定 |
|-------------|------|------|
| [摘录] | 仍在/已消失/未跑 | 已知失败 / 已修复 / 新回归 |

## 失败用例
### [测试节点或 TC-XXXX]
- **严重程度**：P0/P1
- **复现**：工作目录 + 完整命令
- **期望 / 实际**：
- **相关文件**：`path:Lx-Ly`
- **排查建议**：具体到文件，禁止「请检查相关代码」
- **来源**：BASELINE / PM报告 / 代码变更

## 用例变更
| 动作 | 标识 | 依据 |
|------|------|------|
| 新增/修改/废弃 | test_xxx.py::case | ... |

## 趋势
| 日期 | 通过 | 失败 | 相对基线 |
|------|------|------|----------|
| 近3次 | ... | ... | ... |
```

---

## 行为约束

1. **先基线后结论**：新失败必须能与 `docs/testing/BASELINE.md` 中条目区分
2. **不编造结果**：跑不了标 `[未执行]` 并写环境原因（venv、端口、Quarto、Chromium）
3. **失败必须可复现**：含 `cd` 目录与命令
4. **禁止 Git**：范围只来自 PM 报告、BASELINE、可读源码
5. **只消费** PM 的 `[需测试验证]`
6. **不写真实运行库**：禁止用 `var/db/ai4e_vis.sqlite3` 或用户 `var/objects` 做测试夹具
7. **记录错误日志**：核实后的真实错误追加 `error.log`，状态 `未提炼`；宁可漏记
8. 更新基线事实时同步 `docs/testing/BASELINE.md`，并在报告声明

---

## 协同机制

- **执行顺序**：调研之后、产品 Agent 之前
- **输出**：产品 Agent 用你的数字评「测试健康度」——必须可引用
- **输入**：只吃 `[需测试验证]`，忽略文档文风与排期议论
