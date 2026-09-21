<!-- dojo-help: {"domain": "run", "kind": "api-guide", "layer": "core.run", "summary": "用 launch、stage 和 TrainingRun 建立直接研究流程并交付证据。", "symbols": ["ai4e_core.run.launch", "ai4e_core.run.stage", "ai4e_core.run.TrainingRun"], "tasks": ["直接运行", "阶段执行", "产物登记"], "title": "Core 运行 API 指引", "topic_id": "api-guide:core-run"} -->
# Core 运行 API 指引

## `launch`

```python
from ai4e_core import run
status = run.launch(pipeline, script=__file__, config_loader=load_configuration)
```

`pipeline` 可以是一个接收最终配置的函数，也可以使用阶段映射。`script` 定位默认配置和来源；`config_loader(path, overrides)` 必须应用点号覆盖并解析相对路径。阶段内异常会进入失败摘要并返回非零；配置解析发生在会话建立前时可直接抛错。

## `stage`

```python
result = run.stage("train", train, cfg, prepared)
```

`stage` 只能在 `launch` 会话中调用，它设置阶段日志上下文、原样返回函数结果并登记成功或失败。普通 Python 值用于同一流程交接，固定路径用于独立阶段交接。

## `TrainingRun`

```python
session = run.TrainingRun()
out = session.output_dir("post") / "metrics.json"
session.record_asset("metrics", out, kind="other", stage="post")
session.report({"metrics": str(out)}, stage="post")
```

使用 `output_dir`、`report`、`artifact`、`record_asset`、`record_metric` 和 `checkpoint` 写入受管理的运行记录。不能让 application 或用户组件直接伪造 `summary.json`、资产索引或检查点登记。

逐符号现行签名和源码位置见 `module:ai4e_core.run` 以及 `api:ai4e_core.run.<name>`。
