# 2026-09-21 Dojo 增量测试报告

## 结论

- 状态：**有新可行动发现，未通过**。
- 本轮是 `docs/reviews/tests` 的首次可用趋势基线；上次自动化运行没有留下 `latest.md` / `history.jsonl`，因此不能可靠计算逐 nodeid 的历史变化。
- 唯一口径去重后：`202 passed / 2 failed / 1 collection error / 4 skipped`；另有两次针对失败范围的重复复核，不计入趋势总数。
- Web 架构检查与生产构建通过；正式 `8000/5173` 均未监听，因此没有正式页面冒烟。

## 源码与环境身份

- 开始：2026-09-21 02:03 CST；结束：2026-09-21 02:17 CST。
- Git HEAD：`477c47bc4cba83fd1e903800034d7d58286ee6d8`（2026-09-18T16:47:17+08:00）。
- 用户工作区（排除本报告目录）：193 个已跟踪修改、243 个未跟踪项；状态身份 SHA-256：`8d063fe45330497283c81ef00b650fe9691d995c01c288e98ee91c039f9db04c`。
- Python 3.12.14；uv 0.12.5；pytest 9.1.1；macOS / Apple M5 Pro。
- Python 导入来自 `.venv/lib/python3.12/site-packages/ai4e_{core,contrib,task,server}`。逐文件核对显示 Core 299、Contrib 205、Spec 13、Server 67 个 Python/YAML/JSON 文件与源码一致；Task 的运行时代码一致，`.hatch-resources` 属于构建暂存资源，另由实际 wheel 安装测试验证。
- 数据盘仅余约 14 GiB，容量 99%；未发现 pytest 或训练进程。存在长期隔离服务 `8011` 及其 Vis 子进程，未操作。

## 测试结果

| 分组 | 结果 | 时间 | 证据 |
| --- | --- | ---: | --- |
| Agent Help / examples / Task 资源 / 研究导航 | 32 pass, 1 fail, 2 skip | 8.55 s | `public-api.xml` |
| rawprep / split / Task / Web 配置交接 | 117 pass, 1 fail, 2 skip | 481.08 s | `config-handoff.xml` |
| PCNO / GeoTransolver / MeshGraphNet 轻量数值与 recipe | 52 pass | 3.21 s | `new-model-numeric.xml` |
| Task 真实 wheel 外部安装 | 1 pass | 13.92 s | `task-installation.xml` |
| PCNO 推理相关收集 | 1 error | 2.81 s | `new-model-and-install.xml` |
| Web `check:architecture` + `tsc --noEmit` + Vite build | pass | 4.8 s | 命令输出；构建仅有 >500 kB chunk 警告 |

JUnit 文件位于本目录。`source-public-api.xml` 与 `source-config-core.xml` 是失败复核，结果分别仍为 `32 pass / 1 fail / 2 skip` 和 `22 pass / 1 fail`，不重复计数。

## 新发现与最小建议

1. **回归：Agent Help 生成物过期。**
   - nodeid：`tests/integration/test_agent_help.py::test_generated_help_is_current`
   - 首次失败：2026-09-21；最近通过：无；持续：1 天。
   - `tools/docs/build_agent_help.py --check` 报 8 个过期目标：`api/core/abilities/sampling/graph.md`、`api/core/applications/aero_cfd/trainprep/{physical,topology}.md`、`api/contrib/applications/aero_cfd/operations.md`，以及 `indexes/{topics,cases}.json`、`indexes/{symbols,source-map}.jsonl`。
   - 最小建议：确认当前公开符号后重新生成 Agent Help，并复跑该 nodeid；不要只手改索引。

2. **回归：随机切分不能把原 test 样本重划到 train。**
   - nodeid：`tests/integration/test_trainprep_split.py::test_open_dataset_applies_random_split`
   - 首次失败：2026-09-21；最近通过：无；持续：1 天。
   - `ManifestIndex.remap_partitions` 对目标非 `test` 分片排除了原 `test` 记录，导致样本 `c` 在随机全集重划时错误报“找不到样本 c”。源码与安装副本哈希一致，排除安装漂移。
   - 最小建议：在保持同名样本来源优先级的前提下，允许显式重划把唯一原 test 记录移入 train/eval，并补同名跨来源回归。

3. **环境阻断：PCNO 推理套件缺 `iapws`。**
   - 收集 `test_pcno_inference.py` 时由 `ai4e_core.abilities.postproc.wellbore` 报 `ModuleNotFoundError: iapws`；相关 `test_pcno_inference.py`、`test_pcno_post.py`、`test_pcno_equivalence.py` 共 9 个函数级测试未运行。
   - 最小建议：在获准按仓库规则更新主环境后再复跑；本轮未 sync、未安装依赖。

4. **运行资源：磁盘 99%。**
   - 仅余约 14 GiB；`dojo_train` 约 219 GiB。继续 wheel、浏览器或训练测试前应由用户清理/归档明确目标，自动化未删除任何文件。

## Skip / Not run

- 2 个 Neumann 仓库外 direct-core / Task smoke：需要显式 `DOJO_EXAMPLE_SMOKE`。
- 2 个真实模型换模准备交接：需要显式 `DOJO_MODEL_PICKER_REAL=1`。
- PCNO 推理、post、equivalence：因缺 `iapws` 未运行。
- 正式 Web：`8000`、`5173` 均未监听；未启动、未重启，也未用隔离端口替代正式验收。
- 未运行长训练、全量 pytest、浏览器 E2E、大下载及论文复现；周一增量轮次不以这些缺项冒充通过。

## 执行命令

- `uv run --no-sync pytest ... test_agent_help.py test_example_contract.py test_example_core_runs.py test_example_task_runs.py test_task_resources.py test_research_navigation.py`
- `uv run --no-sync pytest ... test_rawprep_manifest_configuration.py test_nasa_crm_data.py test_trainprep_split.py test_task_assets.py test_task_recipe.py test_web_recipe_compatibility.py test_web_stage_consistency.py`
- `uv run --no-sync pytest ...`（PCNO / GeoTransolver / MeshGraphNet 轻量测试清单，见 `new-model-numeric.xml`）
- `uv run --no-sync pytest tests/integration/test_task_installation.py`
- `npm run --prefix packages/ai4e-web check:architecture`
- `npm run --prefix packages/ai4e-web build`

