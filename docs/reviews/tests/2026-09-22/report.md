# 2026-09-22 Dojo 增量测试报告

## 结论

- 状态：**有新可行动发现，未通过**。
- 去重后的当前源码/当前主环境结果为 `85 passed / 3 failed / 5 errors / 2 skipped`；新鲜 Task wheel 的同 nodeid 诊断性复测另有 `1 passed`，不重复计入趋势总数。
- 上轮 Agent Help 生成物过期已恢复；`ManifestIndex.remap_partitions` 的随机重划回归仍失败，持续 2 天。
- 新发现：公开 aero 示例配置与现行加载门禁不一致；主 `.venv` 的 Task 安装资源落后于当前源码；PCNO 仍因缺少可选依赖 `iapws` 阻断。
- RMHD 双组/Skill 单组验证工具的新增与改动用例 `32 passed`。
- 正式 `8000/5173` 均未监听，因此没有正式页面冒烟；本轮未启动、重启或重装任何正式服务。

## 源码与环境身份

- 开始：2026-09-22 02:02 CST；结束：2026-09-22 02:07 CST（周二增量轮次）。
- Git HEAD：`9b53fc4cc4e38c128b18489f0b95f85055ceafaf`（2026-09-21T17:09:47+08:00）。相对上次 HEAD `477c47bc4cba83fd1e903800034d7d58286ee6d8` 有 1 个提交，包含 1,353 个文件变更；该提交主要收纳上轮已在脏工作区中抽样测试的交付内容。
- 排除 `docs/reviews/tests` 后，工作区有 18 个已跟踪修改、24 个未跟踪文件；状态身份 SHA-256：`703ab1d0edb7a5461e42d316d758c7cfc98baaaa4c646e3b041cef23946f21eb`。
- Python 3.12.14；uv 0.12.5；pytest 9.1.1；macOS / Apple M5 Pro。
- `ai4e_core`、`ai4e_contrib`、`ai4e_task`、`ai4e_server` 均从 `.venv/lib/python3.12/site-packages` 导入。随机切分与配置加载涉及的 Core 源码/安装副本 SHA-256 一致；Task 资源清单不一致，详见下文。
- 数据盘约余 276 GiB（70% 使用），`dojo_train` 约 163 GiB；相比上轮约余 14 GiB/99% 已明显恢复。未发现 pytest 或训练进程；长期隔离服务 `8011` 及其 Vis 子进程仍在，未操作。

## 测试结果

| 分组 | 结果 | 时间 | 证据 |
| --- | --- | ---: | --- |
| Agent Help / examples / Task 资源 /研究导航 / 固定公开 API / recipe 约定 | 48 pass, 2 fail, 2 skip | 14.15 s | `public-api-recipe.xml` |
| RMHD 双组与 Skill 单组验证工具 | 32 pass | 1.42 s | `rmhd-skill-study.xml` |
| 上轮随机切分回归 + Task 实际 wheel 外部安装 | 1 pass, 1 fail | 14.68 s | `prior-regressions-install.xml` |
| PCNO post / equivalence 拆分复测 | 4 pass, 4 error | 0.23 s | `pcno-post-equivalence.xml` |
| PCNO inference 收集 | 1 collection error | 0.13 s | `pcno-collection.xml` |
| 当前源码构建的新鲜 Task wheel 资源诊断 | 1 pass（诊断复测，不计总数） | 0.05 s | `fresh-wheel-resource.xml` |

JUnit 文件位于本目录。没有运行全量 pytest、Web 构建/E2E、长训练或论文复现；周二增量轮次不以这些缺项冒充通过。

## 趋势与发现

1. **已恢复：Agent Help 生成物与当前源码一致。**
   - `tests/integration/test_agent_help.py::test_generated_help_is_current` 本轮通过；上轮首次失败，持续在本轮终止。

2. **持续回归：随机切分不能把原 test 样本重划到 train。**
   - nodeid：`tests/integration/test_trainprep_split.py::test_open_dataset_applies_random_split`。
   - 首次失败：2026-09-21；最近通过：无；持续：2 天。
   - `ManifestIndex.remap_partitions` 仍在目标非 `test` 时排除唯一的原 test 记录，样本 `c` 报“重划分片找不到样本”。源码与安装副本一致，不是安装漂移。
   - 最小建议：保留同名跨来源优先级，同时允许显式重划消费唯一原 test 记录，并补同名多来源用例。

3. **新回归：公开 aero 示例配置无法通过现行加载器。**
   - nodeid：`tests/integration/test_recipe_conventions.py::test_aero_public_inputs_preserve_domain_defaults`；首次失败：2026-09-22。
   - 7 个示例把 `data_root`/数据产物改成 recipe 目录内相对路径，触发“数据产物不能位于 recipe 代码目录内”：NASA CRM AB-UPT/Transolver-3/MeshGraphNet，ShapeNet-Car AB-UPT/Transolver-3 surface/volume/MeshGraphNet。
   - 2 个 GeoTransolver 示例另带加载器不接受的 `infer.seed`：NASA CRM 与 ShapeNet-Car。
   - 最小建议：统一“仓库内模板可加载”与“复制后相对输出”的路径语义；移除或正式接入 `infer.seed`，并让配置测试遍历所有 standalone aero 示例而非首错停止。

4. **安装漂移：主 `.venv` 的 Task 资源少 3 个源码案例。**
   - nodeid：`tests/integration/test_task_resources.py::test_resource_manifest_and_checks`；首次失败：2026-09-22，最近通过：2026-09-21。
   - 主安装缺 `pcno.double_cylinder`、`aero_cfd.shapenet_car_geotransolver`、`aero_cfd.nasa_crm_geotransolver`。
   - 当前源码构建的新鲜 `ai4e-task` wheel 在隔离目标中包含全部 3 项，同 nodeid 通过；说明打包源码完整，正式安装副本未刷新。
   - 按仓库规则，本轮没有 sync/reinstall。若要让正式 Python/Task/8000 消费当前资源，需要用户另行授权按规定重装 `ai4e-task`，并在有 Web 消费链时更新正式进程后冒烟。

5. **持续环境阻断：PCNO 缺 `iapws==1.5.4`。**
   - `test_pcno_inference.py` 仍在收集阶段报 `ModuleNotFoundError: iapws`；`test_pcno_equivalence.py` 的 4 个原源码对照节点也因此 setup error。
   - 拆分后确认 `test_pcno_post.py` 3 项与 equivalence 的源码表达式检查 1 项通过。
   - 依赖已声明在 `ai4e-core[geothermal]` 和锁文件中，但当前环境未安装。本轮未 sync、未单独安装依赖。

## Skip / Not run

- 2 个 Neumann 仓库外 direct-core / Task smoke：需要显式 `DOJO_EXAMPLE_SMOKE`。
- 正式 Web：`8000`、`5173` 均未监听；未以隔离端口替代正式验收。
- Web 架构/类型/构建/E2E、全量 pytest、其他未变模型数值回归、长训练、大下载和论文复现均未运行。
- 新鲜 wheel 仅用于临时隔离诊断；构建和安装目录已移至系统废纸篓，可恢复，未改主环境。

## 执行命令

- `uv run --no-sync pytest tests/integration/test_agent_help.py ... tests/integration/test_public_api_stability.py tests/integration/test_recipe_conventions.py`
- `uv run --no-sync pytest tests/integration/test_dojo_validity_rmhd.py tests/integration/test_dojo_skill_study.py`
- `uv run --no-sync pytest tests/integration/test_trainprep_split.py::test_open_dataset_applies_random_split tests/integration/test_task_installation.py`
- `uv run --no-sync pytest --collect-only tests/integration/test_pcno_inference.py tests/integration/test_pcno_post.py tests/integration/test_pcno_equivalence.py`
- `uv run --no-sync pytest tests/integration/test_pcno_post.py tests/integration/test_pcno_equivalence.py`
- `uv build --package ai4e-task --wheel ...` 后隔离 `--target` 安装并复测 Task 资源 nodeid；未安装到主 `.venv`。
