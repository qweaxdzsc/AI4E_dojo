# 训练评估指标与运行曲线（2026-09-18）

## 本轮实现追加（2026-09-18）

- 训练报告保留 epoch `history`，新增 `curves.loss` 和 `curves.learning_rate`，每个真实 optimizer update 写入一条曲线点；恢复训练沿 update 继续。
- 训练配置新增 `loss_x_axis`、`validation_unit`、`evaluation_fields`、`evaluation_aggregate`；训练页评估选择物理量和指标，运行页移除独立更新步 Tab。
- 本轮圈定验证：`test_train_loop.py`、`test_model_evaluation.py`、`test_train_online_loss.py`、`test_infer_vtk_identity.py`、`test_physical_mesh_export.py` 共 38 passed；`ai4e-web` build 通过。
- 正式 8000/5173/Vis 尚未重启或冒烟；安装副本仅按规则重装了 `ai4e-core` 用于测试，不能替代正式入口验收。

## 范围与当前状态

用户要求训练设置选择实际计算的指标；运行曲线增加 Loss、更新步、学习率页签，各有配置图标，配置内容暂空。源码和隔离 wheel 验证完成，**正式指标计算链尚未验收，等待当次授权更新 core/server 并只重启 8000**。5173 已直接读取 Web 源码；未操作正式环境安装或进程。

## 实现与交接

- `abilities/eval/metrics.py` 提供原三项 MSE、MAE、相对 L2 的选择校验与按需计算；`evaluation.py` 新增可选关键字 `metric_names`，默认 None 保持旧调用，空序列只算 loss；返回结构不变，未知/重复项抛 ValueError。
- `applications/aero_cfd/train/fitting.py` 将 `train.evaluation_metrics` 传给普通及重复评价。仍按现有物理反变换、逐样本聚合、随机流规则计算。开启评价但分片为空时在更新前明确拒绝。指标选择不进入恢复合同，不改变 loss/选优；默认不注入新键、不批量改写历史配置或报告。旧物理训练路径原限制保留。
- `inspection.py` 提供指标目录与缺省项；server 配置合成允许该叶子的明确编辑，空列表保持为空。`TrainingPanel.tsx` 保存真实选择与间隔。
- `TrainingMonitor.tsx` 展示三个独立维度，epoch 优先、缺少时使用 updates；更新步纵轴为累计有效更新数。维度独立过滤有限值，不依赖 loss 是否存在；保留单点与零学习率。配置弹窗无输入项、无保存动作。
- 更新 core abilities/applications、server modules、web src PRD，根入口与对应模块索引。

## 验证与证据

证据目录 `/Users/zonghui/work/project_simulation/dojo_train/training_metrics_ui/`。

- `verified.xml`：68 passed，0 skipped。范围：`test_model_evaluation.py`、`test_train_loop.py`、`test_train_online_loss.py`、`test_web_configuration_composition.py`、`test_public_api_stability.py`、`test_train_resolved_config.py`、`test_train_recipe.py`，以及 `test_algorithm_platform_contract.py` 的当前训练能力/模型采样能力两项。
- 新交接测试真正执行三轮更新并写训练报告，验证选中/空选择、验证间隔、再改指标从检查点继续一轮；数值测试独立验证反归一化后的预期值。线性夹具验证工程行为，不作为正式 CFD 精度证据。
- 固定用户源码基线通过实际 core/spec wheel 运行，未改 baseline 或摘要。
- `release/wheels/` 为当前 core/server wheel，`release/installed/` 为隔离目标安装；`wheel-tests.xml` 为实际安装包的指标与配置交接验证。
- 浏览器两文件 `execution-monitor.spec.ts`、`stage-consistency.spec.ts` 共 19 项：初次 18 passed，新增指标断言修正后二次 1 passed，合计 19 项唯一用例通过。覆盖三个维度的真实坐标、零值、缺失值、各图空面板，指标多选、明确编辑路径、清空与刷新回显。接口夹具不等于正式数值链。
- 前端构建、微领域架构检查与本轮 Python 文件 ruff 通过。
- 最初数值夹具少了反变换声明导致 3 个失败，已修正并包含在最终 68 项内；记录在 `tests.xml`。扩大检查 `tests-final.xml` 为 99 passed / 1 failed：`test_contrib_inspect_keeps_historical_dataset_root` 在未修改的 `contrib/application/aero_cfd/inputs.py → core/base/config/conventions.py` 拒绝旧 `dataset.root`，尚未进入本轮更改的能力描述。没有改此历史用例或放宽废弃键门禁，不计为通过。

## 正式入口只读核对及待验收

2026-09-18 通过真实 5173→8000 浏览项目 `32cdee6900924df096838663a4a70a05`、任务 `beab7b5ab1414787b8cc6a288e6db0cc`：三个页签可见，学习率配置打开为空面板，更新步页签与无数据态正确。该旧验收任务当前运行返回空 history；最近旧运行显示 `missing_or_invalid_completion`，停止运行同样无曲线记录。因此这里只证明正式 UI/空态，不能声称真实三条曲线已验。

正式 8000 当前读取安装副本，查询时 PID 3619；该值发布前须重新核查。core/server 原安装备份及源码/安装逐文件摘要见 `release/installed-ai4e-*.zip`、`release/before.json`。发布使用根 AGENTS 要求的 dev+visualization 两组同步，重装 core/server，随后只重启8000。授权后须创建独立小预算验收运行，正式页面保存指标、开训、观察三条真实曲线与所选指标；不改用户原任务预算，不用旧空数据记录代替。

## 正式发布与冒烟（2026-09-18，用户授权）

- 按仓库规则重装 `ai4e-core`、`ai4e-server`、`ai4e-task`、`ai4e-viz`，保留 `dev` 与 `visualization` 组；正式 API 8000 已更新并重启，PID **34563**。5173 未重启，HMR 已读取当前 Web 源码。
- 正式任务 `179ed1fe447b415b8870c45b6a89a296 / 01400e5e5b8a4bd88d43f658ddc2fb9f` 的训练运行页显示 epoch 2、优化步数 1578；Loss 横轴选择器可见，Tab 仅有 Loss 与学习率，无独立更新步 Tab；在线诊断与测试评估和 Loss 分区显示。
- 正式推理与后处理冒烟见同批次记录：双 checkpoint、单平台数据集、三维工作台加载均通过。
- 失败边界：`tests/integration/test_infer_stage.py` 的 8 项 rawprep 失败来自旧 `ai4e-contrib` 安装副本（NASA 缺 `open_dataset`、ShapeNet 分片类型错误），未进入本次训练曲线/评估逻辑；不计为本次功能失败，也未将其冒充通过。
- 后续检查 `GET /api/v1/health` 返回 `{"status":"ok"}`；正式服务当前进程 PID 为 **48179**（发布冒烟记录中的 34563 已由本机进程管理重新拉起）。
