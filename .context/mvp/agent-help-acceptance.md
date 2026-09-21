# Dojo Agent Help Center 验收记录

## 交付范围

- `docs/agent-help/index.md` 是唯一详细使用正文；支持 Agent Skills 的环境从 `.agents/skills/dojo-research/SKILL.md` 进入，无 skill 环境从 `DOJO_AGENT_GUIDE.md` 进入。
- 帮助树包含 getting-started、concepts、五类纵向 workflow、core/contrib/Task API、六类 recipe、十个用户组件主题、逐案例页面、troubleshooting 和 reference。
- 十个用户组件主题已经补齐接入层选择、普通函数/对象示例、配置连接、真实调用证明、恢复边界和科学证据边界；五类 workflow 均从具体 standalone 走到 direct-core、组件变体、Task、恢复、固定结果和比较。
- `tools/docs/build_agent_help.py` 使用 AST、Markdown 元数据和案例清单生成确定性 API 页面与四个机器索引，不 import 研究代码。`--write` 显式更新，`--check` 只核对漂移。
- `ai4e_task` 包根导出 `help_info`、`list_help_topics`、`search_help`、`read_help_topic`、`describe_help_symbol` 和 `export_help`；CLI 的 `guide search/topic/symbol/export` 只包装这些 Python API。
- Hatch build hook 将完整帮助中心、guide、skill、案例清单和全部发布 examples 写入 wheel；recipes、`.context`、缓存和本机路径不进入安装资源。

## 当前覆盖

2026-09-20 最终生成快照包含：

- 31 个案例主题：21 个 `standalone`、10 个 `extension`；
- 1,508 个公开符号记录；
- 1,958 个可检索主题；
- 451 个 Markdown 页面，其中 397 个文件由生成器维护。

覆盖门禁扫描 `ai4e_core.abilities`、`ai4e_core.applications`、`ai4e_contrib.ability`、`ai4e_contrib.application` 和 `recipes/**/*.py` 的公开函数、类与公开方法，并单独核对 `ai4e_core.run.__all__` 与 `ai4e_task.__all__`。每个符号拥有独立 topic、页面锚点、现行签名、参数表、返回标注、显式异常、稳定性、源码路径/行号及关联案例。

## 运行与安装证据

- `uv run --no-sync python tools/docs/build_agent_help.py --check`：397 个生成文件无漂移。
- 隔离构建 `ai4e_task-0.1.0-py3-none-any.whl`，解压到 `/tmp/dojo-agent-help-site-20260920-d` 后运行帮助、案例、扩展与 Task 圈定集合：51 passed，2 skipped；随后新增的五类 workflow 入口检查 5 passed，合并圈定结果为 56 passed，2 skipped。两个 skip 是默认未显式开启的 Neumann 数值 smoke，不计作通过。
- 显式开启 `DOJO_EXAMPLE_SMOKE=1` 后，Neumann direct-core 与 Task smoke：2 passed。Task 流程固定第一次 preparation，完成两轮训练，从第一轮 `best.pt` 恢复到第二轮，再完成独立 infer、post 和结果读回；恢复运行没有重新执行 trainprep。
- Task 项目、资产、执行、合同回归已包含在上述 51 项中；恢复、快照和版本边界保持通过。
- `tests/integration/test_task_installation.py`：1 passed。该用例构建四个真实 workspace wheel，在源码目录外新环境安装；帮助搜索返回 `ai4e_core.run.launch` 第一命中，符号签名与参数化 PDE workflow 可读，查询过程未加载 Torch 或 contrib，并继续通过 CLI、Task 运行及字段扩展案例。
- 资源 CLI 额外验证 `guide search`、`guide topic`、`guide symbol` 和 `guide export`；导出目录包含完整帮助树且不创建 `AGENTS.md`。
- 相关 Python 文件 Ruff check 与 format check 通过。

## 回归处理

旧测试曾把 guide 当成完整 API 正文，并写死旧导出内容；现行合同改为 `Skill → Agent Help Center → standalone`，无 skill 环境为 `Guide → Agent Help Center → standalone`，因此更新旧断言和 PRD。案例数量随已登记 MeshGraphNet standalone 从 19 增至 21，帮助索引与资源测试按现行清单更新。

Neumann Task 的首次恢复失败不是过时测试：原 smoke 在 `resume_run` 时重放包含 trainprep 的整条流水线，重新序列化 preparation 后 content ID 改变，检查点合同正确拒绝。修复是固定 preparation，并把训练、恢复、infer 和 post 分为明确输入的独立阶段，没有放宽检查点身份。

## 入口分流强化（2026-09-20）

- `DOJO_AGENT_GUIDE.md` 与 `.agents/skills/dojo-research/SKILL.md` 在标题后的首屏直接链接同一 `docs/agent-help/index.md`，并明确自身只负责分流和导航，不充当 API 手册。
- 两个入口都列出 getting-started、concepts、workflows、api、user-components、examples、recipe、troubleshooting 和 reference 的适用问题，并说明 Markdown 浏览、Python 检索、精确符号查询与 JSON/JSONL 离线索引的选择方式。
- `tests/integration/test_example_contract.py` 与 `tests/integration/test_agent_help.py`：14 passed；首屏文案、帮助类型、Python 检索入口和仓库内相对链接均通过。
- 隔离 wheel 解压后，Guide 链接与 skill 的三级相对链接都解析到安装资源中的同一个帮助正文；以该 wheel 作为 `PYTHONPATH` 运行 `tests/integration/test_task_resources.py`：8 passed。
- 帮助生成漂移检查、相关 Ruff check 和 format check 通过。当前 `.venv` 的旧安装副本仍不包含新增资源门面，未执行未经授权的重装；本次安装证据来自隔离 wheel。

## 未宣称

本验收不表示 21 个 standalone 都完成真实数据训练，也不表示所有生成 API 条目的研究语义可以脱离关联源码和案例独立使用。AST 页面负责完整发现、签名和定位，人工 workflow、用户组件、recipe 与案例页面负责使用语义；Agent 调用前仍需读取所选案例和安装源码。

本验收不宣称学习效果、生产预算、论文级精度或 Web 行为。当前 `.venv` 未重装，正式 8000/5173 未修改或重启；交付证据来自隔离 wheel、仓库外帮助/案例资源、direct-core、Task Python API 和固定产物读回。
