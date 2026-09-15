# nasa_crm_abupt

一个独立模型实例，使用唯一 aero_cfd recipe 的共享阶段入口。复制本目录，修改数据与运行路径后运行。

- 已有物理 PT：配置 `train.manifest` 后执行 `uv run python pipeline.py`。
- 独立训练消费 `train.preparation`；独立后处理指定 `post.checkpoint`，沿用对应准备。
- 一轮完整训练，最后检查点；固定五个测试样本全点评价。前三个样本用于跨运行图表。
- NASA 只有表面场。汽车 Transolver 表面与体积各使用独立 example，复用同一物理数据。

本期交叉实跑已交付；结果与验收边界见仓库 `.context/mvp/cross-model-acceptance.md`。

NASA 只有表面域：使用坐标、法向和六维样本工况，预测 Cp 与 Cf 三分量。`blocks: pssssssssss` 使用已有单域自注意力，不能复用汽车需要双域的 c 块。正式参数规模为 19,736,644。

## 独立推理

`infer.py` 显式配置恢复、预测、评价与保存。设置 `infer.checkpoint`、`infer.preparation`、`infer.samples` 后执行 `uv run python infer.py`；调用 pipeline 时选择包含 infer 的阶段名单。原生 post-only 需要固定结果；明确设置 `post.legacy_predict=true` 才进入历史预测兼容模式，页面不会自动开启。

原生 infer 只解释 infer 参数；后处理以 `post.results` 或 `infer.results` 指向已经完成的 `physical-predictions.json`，不会再次预测。完整物理场五例交付同形预测与物理指标；旧锚点模板保留独立兼容结果，不冒充同一比较口径。进度为 `inference-progress.json`，所有运行文件由 writer 提交，数组写配置指定数据目录。

派生字段例子见 `examples/recipe_extensions/inference_fields/`；详细功能约定见 `docs/PRD/recipes/aero_cfd/PRD.md`。

### 推理字段与指标选择

`infer.fields` 使用 `域:字段:分量`，默认全部真实输出；显式空列表拒绝。`infer.metrics` 默认相对L2、MAE、RMSE、Max Error、R²。选择向量的部分分量仅限制评价，保存保留完整向量。`save_predictions=false`时需关闭`export_vtk`，仍交付轻量指标；新`inference-results.json`与旧结果保持可读，新post不重跑模型。研究者可在物理输出后显式登记派生字段及选择，再配置评价和保存。

普通用户逐场评价扩展示例见 `examples/recipe_extensions/inference_metrics/`。原生后处理缺少固定结果时拒绝；旧计算API保留，历史脚本按固定兼容指纹核验，不改写历史证据。
