<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "从固定预测和网格读入数据，产生指标、图表或导出文件。", "tasks": ["编写用户组件", "组件调用证明"], "title": "Post 组件", "topic_id": "user-component:post"} -->
# Post 组件

post 不加载训练模型。它读取 infer 已提交的固定结果，计算派生指标或可视化，并通过 `record_asset`、`record_metric` 和阶段报告登记。

指标语义至少声明 field、unit、split、statistic 和 data_identity；图片存在不能替代数值和来源清单。

## 输入和输出

独立 post 的输入应是固定结果清单，而不是 checkpoint：

```yaml
pipeline:
  stages: [post]
inputs:
  post:
    results: /absolute/predictions/predictions.json
```

阶段脚本先拒绝空输入、未完成清单、越界路径和摘要不一致，再读取逐样本预测。输出写入 `TrainingRun().output_dir("post")`，最后登记资产和指标。

## 最小结构

```python
from pathlib import Path
from ai4e_core.run import TrainingRun


def post(cfg, results=None):
    source = Path(results or cfg.inputs.post.results)
    if not source.is_file():
        raise FileNotFoundError(source)
    session = TrainingRun()
    output = session.output_dir("post") / "metrics.json"
    # read_fixed_results 必须校验清单状态、样本身份和内容摘要。
    report = read_fixed_results(source)
    output.write_text(serialize(report), encoding="utf-8")
    session.record_asset(
        "metrics", output, kind="other", stage="post", dependencies=[source, source.parent]
    )
    session.report({"metrics": str(output)}, stage="post")
    return report
```

`read_fixed_results` 和 `serialize` 代表案例自己的普通函数；真实实现可参考参数化 PDE、GenCP、SafeDiffCon、WDNO 或 MeshGraphNet 的 `post.py`，不能把骨架原样当成可运行实现。

## 自定义可视化

`recipe_extensions.physical_visualization` 展示普通绘图函数：

```python
from ai4e_core.abilities.postproc.visualization import render_field


def render_with_edges(mesh, **parameters):
    import pyvista as pv

    modified = pv.wrap(mesh).copy(deep=True)
    return render_field(
        modified,
        **{**parameters, "show_edges": True, "background": "white"},
    )
```

绘图函数只修改显示副本，不改固定预测。图像资产应依赖结果清单和数组；颜色范围、单位、字段、分量和视角应进入可复核配置。

## 指标登记

`record_metric` 的语义至少包括：

```python
session.record_metric(
    "mean_relative_l2",
    value,
    stage="post",
    assets=[source.parent],
    semantics={
        "field": "u",
        "unit": "1",
        "split": "test",
        "statistic": "mean_relative_l2",
        "data_identity": manifest["dataset_identity"],
    },
)
```

## 验证

1. 单独运行 post，监测进程不应 import 模型组件或读取 checkpoint。
2. 从固定结果重新计算关键指标，并与报告逐值比较。
3. 修改一个预测字节后，摘要门禁应拒绝，而不是继续生成图表。
4. 检查资产索引的 dependencies 和 metric semantics。
5. 重跑 post 生成新的运行记录，不修改历史 infer 或历史报告。

图片适合解释空间分布，但不能替代数值、样本清单、指标定义和数据身份。
