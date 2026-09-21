<!-- dojo-help: {"domain": "direct-core", "errors": ["运行摘要失败"], "kind": "tutorial", "layer": "core.run", "outputs": ["summary.json"], "summary": "用案例自己的配置加载器和 ai4e_core.run.launch 执行 Python 流程。", "tasks": ["直接运行", "阶段交接"], "title": "第一次 direct-core 运行", "topic_id": "getting-started:first-direct-core-run"} -->
# 第一次 direct-core 运行

完整案例的 `pipeline.py` 是阶段顺序真源：

```python
from ai4e_core import run
from configuration import load_configuration


def pipeline(cfg):
    prepared = run.stage("trainprep", trainprep, cfg)
    trained = run.stage("train", train, cfg, prepared)
    return run.stage("infer", infer, cfg, prepared, trained)


status = run.launch(
    pipeline,
    script=__file__,
    config_loader=load_configuration,
    argv=["--set", "train.device=cpu"],
)
```

`launch` 返回 0 仍需读取 `summary.json`、阶段事件和登记产物。单阶段脚本使用同一配置加载器和阶段函数，不能另写一套运行逻辑。路径通过最终配置、普通返回值和 `inputs.<stage>.<name>` 交接，不依赖 cwd。
