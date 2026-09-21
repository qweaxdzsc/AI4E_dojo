<!-- dojo-help: {"domain": "all", "kind": "concept", "layer": "concept", "summary": "说明 YAML 参数、Python 顺序和跨阶段路径。", "title": "配置与阶段输入", "topic_id": "concept:configuration-inputs"} -->
# 配置与阶段输入

`config.yaml` 是复制目录的最终用户配置。Python pipeline 决定步骤顺序；`pipeline.stages` 只选择范围。公共外部输入使用 `inputs.<stage>.<name>`，运行记录和科学数据分别使用 `run_root` 与 `data_root`。

同一 pipeline 内优先用普通 Python 返回值交接。独立阶段必须显式指定固定上游来源；缺键不能静默回退到默认数据或检查点。
