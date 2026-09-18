# 准备导入、脚本迁移与无切分原始处理验收

日期：2026-09-18。对照任务 `测试09182`（逻辑项目 `179ed1fe447b415b8870c45b6a89a296`，磁盘项目 `8ef5b810780b4d50bc1311be0db90156`，任务 `01400e5e5b8a4bd88d43f658ddc2fb9f`）。正式入口 `http://127.0.0.1:5173` 代理 `http://127.0.0.1:8000`。隔离 `7999`/`5172` 未作为本切片验收。

产品规则：冻结准备只负责导入（可读、现行 `version=2`、摘要完整）；计算与切分走当前平台页面和核心模板。`version=1` 仍须重做。检查点 `dim`/`blocks` 对不上仍拒绝该权重。历史 `preparation.json` 与任务绑定未改字节。

## 发布

按当次授权执行 `uv sync --group dev --group visualization --reinstall-package …`，只重启 8000，5173 未动（PID **23629**）。

1. 本切片先前已重装 `ai4e-core` / `ai4e-server` / `ai4e-task`，并重启过 8000。当时模型结构图与数据准备归一化目录已在正式页通过；原始处理两样本因 `resolve_paths` 把 `unsplit` 展开成 `{code}/unsplit` 失败（run `3f0a0201b475420bac26201204c2b374`）。
2. 2026-09-18 **15:13** 再重装 `ai4e-core` 与 `ai4e-contrib`（`unsplit` 保留为模式名，不再当路径）。新 8000 PID **21508**，启动参数仍是平台根 `/Users/zonghui/work/project_simulation/dojo_train/platform`、模板 `recipes/aero_cfd`、三组已授权 data-root。

安装副本与源码前 16 位摘要一致：

| 文件 | 摘要 |
| --- | --- |
| `configuration.py` | `d36303741efc7ab3` |
| `trainprep/preparation.py` | `9f6212254524d915` |
| `inputs.py` | `8f57516e9c860f55` |
| `shapenet_car/adapter.py` | `667f3e02224a6e5a` |
| `rawprep/application.py` | `ffdb32649902d876` |
| `trace_source.py` | `a8926a6c0aa0d73f` |
| `official_scripts.py` | `a9005cccc0f432e7` |

回退：重装变更前包版本并再只重启 8000。

## 圈定 pytest

对重装后环境执行（`--no-sync`）：`test_trainprep_consume.py`、`test_train_export.py`、`test_algorithm_platform_contract.py`、`test_task_configuration.py`、`test_aero_cfd_documents.py`、`test_infer_inspect_contract.py`、`test_web_stage_consistency.py`、`test_web_rawprep.py`，以及补测 `test_train_shapenet_contract.py` 的 `unsplit` 路径/展平两项。`test_contrib_inspect_keeps_historical_dataset_root` 不纳入本切片。通过标准以当时重装后跑通记录为准，不把无关 recipe 缺 `task-entry.json` 算进来。

## 正式 Web 冒烟（5173→8000）

入口：`http://127.0.0.1:5173/projects/179ed1fe447b415b8870c45b6a89a296/tasks/01400e5e5b8a4bd88d43f658ddc2fb9f/`。截图在 [preparation-import-results](preparation-import-results/)。

| 项 | 操作 | 结果 |
| --- | --- | --- |
| A 模型结构 | 模型设置点「生成真实模型结构」 | **通过**。文案「真实模型结构已生成 · 配置修订 df1ae368」，无「须重新生成」。阶段主干可见，页面报 17 个检查点节点。截图 `formal-smoke-model-graph-trunk.png`。此前同任务已出过主干 8 / 压缩块 65；本次重启后复点生成仍成功。 |
| B 数据准备产物 | 打开数据准备「处理结果」，展开归一化目录 | **通过**。现行脚本 run `44ddd2c4c41d4b12986ace0d8b4f53fe` 勾选「保存归一化副本」后写出 `data/.../trainprep/normalize/`（哈希目录 + `train`），页面见 `normalize` 与 `preparation.json`（5.2KB）。截图 `formal-smoke-trainprep-normalize.png`。历史只写 JSON 的旧运行未回写。 |
| C 原始处理无官方切分 | 新名称 `shapenet_car_unsplit_smoke` 提交指定 2 样本 | **通过**。run `e896240c49d84052a3b542d11fdfabe8` 成功；生效配置 `partitions: unsplit`；产物目录只有 `train/` + `manifest.json`，无 `test`/`eval`；清单 `partitions.train=2`。页面处理结果选该数据集后同样只有 `train`。截图 `formal-smoke-rawprep-unsplit.png`。 |

说明：绑定源仍是官方已切分的 ShapeNet，catalog「处理样本 889」读的是绑定宇宙，不是本次发布布局。切分只在数据准备页（冒烟后仍为 train 789 / test 100 / eval 0）。历史共享数据集 `shapenet_car`（889，train+test）未覆盖。冒烟用的 `processed_name` 已恢复为 `shapenet_car`，配置修订回到 `28719021846c9205`。`shapenet_car_unsplit_smoke` 留在共享数据集目录作证据。

未验：未对 889 全量重跑原始处理；未重跑正式网络训练或推理精度；NASA 案例保持原切分行为，本任务未再提交 NASA。

## 当次授权复验（2026-09-18 15:28–15:32）

用户明确授权重装、重启与冒烟。Experience 检索 `receipt_4a156eda7d9f4839beabc613a330f3b6`：无覆盖本切片的技术条目。

`uv sync --group dev --group visualization --reinstall-package ai4e-core --reinstall-package ai4e-contrib --reinstall-package ai4e-server --reinstall-package ai4e-task`。停旧 8000 PID **34563**，新 8000 PID **48179**，5173 仍为 **23629**。上表七个文件摘要与源码仍一致。

入口仍是对照任务 `测试09182`。三项再过：

| 项 | 结果 |
| --- | --- |
| A | 生成成功，文案「真实模型结构已生成 · 配置修订 34e4216d」，无「须重新生成」，17 检查点节点。截图 `auth-smoke-model-graph.png`。 |
| B | 处理结果仍见 `normalize` 与 `preparation.json`（5.2KB）。截图 `auth-smoke-trainprep-normalize.png`。 |
| C | 新名称 `shapenet_car_unsplit_auth`、run `cb9f0517bd574bc4be69992859d039f3` 成功；`partitions: unsplit`；产物只有 `train`（2 样本），无 `test`。页面选该数据集同样只有 `train`。截图 `auth-smoke-rawprep-unsplit.png`。 |

`processed_name` 已恢复 `shapenet_car`，修订回到 `28719021846c9205`，数据准备划分仍是 789 / 100 / 0。`shapenet_car_unsplit_auth` 留作证据。

## 未改写边界

- 历史准备记录字节未改。
- 任务 `config.yaml` 数据绑定在冒烟后恢复为 `shapenet_car`。
- 检查点结构核验未放宽。
