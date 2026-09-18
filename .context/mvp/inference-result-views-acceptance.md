# 推理结果表格与图表配置验收（2026-09-15）

本次对应用户新增的两个配置弹窗要求。已通过本次UI与固定结果功能验收；此前推理计算、模型和Trame的验收保留原记录，本次未重复训练或预测。

## 已交付行为

- 表格配置：Checkpoint / 样本两模式；Checkpoint默认汇集本批全部分片样本，Mean / Median / P90 / Max可多选；样本模式选择一个Checkpoint，无聚合控件，保留分片身份。
- 物理量下选择已交付指标，允许多个物理量及各自不同指标。每个组合及聚合方式成为独立列；跨域同名字段不覆盖。
- 独立坐标配置：X由表格模式确定，Y多选当前表格数值列，提供线性/对数尺度、轴刻度显隐与疏密、网格线开关、点数值开关；删除失效系列。取消与关闭丢弃弹窗草稿。刻度与网格默认开，点数值默认关。应用后写入该任务图表配置，刷新仍在。
- 指标表高度 460px、图表卡片 420px、绘图区 368px，均不低于原 218/194/154 的两倍；卡片 `max-height` 不截断，区内滚动。
- CSV下载当前表格；XLSX首表为当前表格，同时保留统计、逐样本指标、指标说明与来源。性能值使用已登记的预测计时。
- 全样本聚合由core从逐样本指标计算，不能平均各分片均值；Task传递包含缺失分片的预期总量。视图操作不创建推理运行。

## 验收证据

证据目录：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/result-views/`。

1. 浏览器固定夹具3项通过：聚合多选、模式切换、跨分片同名样本、多物理量指标配对、Y轴多选、草稿取消、空配置禁用、三种图形与导出请求。
2. 正式5173前端与8000后端，从首页进入真实任务，读取既有批次 `a33115cf9cd148b4979c27c6fa1cbe41`。两份权重×训练/验证/测试三分片，共6份固定结果。实际切换Checkpoint、样本模式，选择第二份权重与3项指标，下载两种模式CSV/XLSX，刷新恢复批次。浏览器无未处理异常、无失败API请求、推理提交为0。见 `real-browser-evidence.json`。
3. CSV/XLSX真实读回：Checkpoint表2行8列、样本表3行5列；21个指标单元用独立NumPy float64从固定逐样本值复核，P90线性插值。数值容差1e-12，页面显示按五位有效数舍入另行核对。见 `download-verification.json`。
4. 弹窗按1672×941、1440×900、1920×1080检查边界与页面横向溢出，实际查看截图确认布局、字段换行、滚动和按钮可见；坐标见 `dialog-bounds.json`。用户新截图没有弹窗视觉稿，因此新增弹窗沿用现有Ant Design风格，不声称不存在基准的像素还原百分比。指标表字段增多时在卡片内横向滚动，图表配置按钮保持右侧。
5. 安装的core/task与工作区源码哈希一致，见 `loaded-sources.json`；正式8000服务已刷新，5173真实入口验收通过。生产前端构建及微领域边界检查通过。

截图：`real-table-checkpoint.png`、`real-table-sample.png`、`real-chart-checkpoint.png`、`real-chart-sample.png`、`real-sample-view.png`；多视口为 `table-{1672,1440,1920}.png` 和 `chart-{1672,1440,1920}.png`。已有主验收目录中的原图、叠加图及历史证据没有覆写。

## 功能—文件—测试映射

- 固定值和统计：`packages/ai4e-core/applications/aero_cfd/infer/{__init__,evaluation,exports}.py`；公开 `result_views`、保留原分片统计默认行为，新增两模式列展开及导出。
- Task交接：`packages/ai4e-task/tasks/{inference_results,inference_inspection}.py`；全批预期数量、独立进程结果查询。
- 页面状态和配置：`packages/ai4e-web/src/modules/inference/{useInferenceResults.ts,InferenceWorkspace.tsx,ResultViewSettings.tsx,ChartViewSettings.tsx,InferenceMetricTable.tsx,InferenceCharts.tsx,inference.css}`；其中坐标弹窗为新增文件。
- 新数值验收：`tests/integration/test_infer_result_views.py`，覆盖不均分片聚合、缺失分片计数、无计数注解兼容、样本身份、两模式CSV/XLSX、性能值与同名物理量。
- 浏览器验收：`packages/ai4e-web/e2e/{inference-fixture.ts,inference-results.spec.ts,inference-result-views-real.spec.ts}`；最后一项为新增真实固定结果用例，使用 `DOJO_INFER_RESULT_VIEWS_REAL=1` 显式启用。
- 独立下载复核工具：`tools/verification/inference_result_views.py`。
- 长期功能同步至Web/src、core/applications、task/tasks三份PRD；同步AGENTS、`.context/index.md`及core/task/web模块导航。
- 同工作树构建发现的附带修复：StageFiles与PostResultFilesPanel补充列表类型；files/index公开listFiles，BoundDatasetFiles改从公开入口导入。保留原文件树功能，未回退其他并行修改。

## 专项执行记录

- 第一组：`test_infer_result_views.py`、`test_infer_metric_aggregation.py`、`test_infer_exports.py`、`test_task_infer_partitions.py`、`test_task_infer_batches.py`、`test_web_inference.py`，16项通过（当时新增结果视图用例3项）。
- 最终算法/文档组：`test_infer_result_views.py`（扩展为5项）、`test_infer_metric_aggregation.py`、`test_infer_exports.py`、`test_infer_results.py`、`test_web_architecture.py`、`test_web_design_documents.py`，33项通过。两组有重复覆盖，不相加冒充独立数量。
- 浏览器：两个专项文件共4项通过；多视口补测包含在3项夹具用例中。Python均使用 `uv run --no-sync`；相关ruff、Web build和check:architecture通过。
- 本次视图与导出要求无未完成项。表格字段仍是当前页面状态，刷新后回到默认列；图表刻度、网格、点数值与坐标选择按任务写入浏览器，刷新仍在。不改变已提交推理选择。

2026-09-17 正式 5173 源码冒烟（未重启 8000）：`http://127.0.0.1:5173` 任务 `7142b2dc…` / `9c1dac25…` 推理页指标表 460px、图表 420px、`max-height:none`；图表配置可见刻度/网格线/点数值与疏密档。该任务尚无批次，无绘点。截图 `official-20260917-2035-chart-config.png`。
