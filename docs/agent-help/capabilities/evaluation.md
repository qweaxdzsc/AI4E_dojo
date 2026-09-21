<!-- dojo-help: {"topic_id": "capability:evaluation", "title": "评价与误差指标", "kind": "tutorial", "layer": "capability", "domain": "evaluation", "summary": "具名样本、物理帧和字段的 FP64 误差，显式定义聚合", "tasks": ["NumPy 预测计算相对 L2", "相对 L2", "评价指标", "FP64", "逐样本"], "symbols": ["ai4e_core.abilities.eval.trajectory.named_frame_metrics", "ai4e_core.abilities.eval.trajectory.trajectory_metrics"], "navigation_order": 7} -->
# 评价与误差指标

已有 NumPy 预测不必进入训练框架：named_frame_metrics 直接接收 [B,T,N,C] 数组及样本/时间/字段/单位，CPU FP64 返回逐帧逐场 rows、mse、sample_relative_l2 和 mean_relative_l2。零范数标为 None，非有限值和维度错误失败。

其 mean_relative_l2 是混合所有通道后的逐样本范数比；单位不同的多物理场通常应逐场调用，再按协议等权聚合，不能用大数值字段支配主指标。trajectory_metrics 则提供分量等权口径；两者不可同名互换。评价端另外校验完整样本身份和数量，不能因缺样本或 None 删除记录后仍宣称官方平均。

## 直接入口

- `ai4e_core.abilities.eval.trajectory.named_frame_metrics`
- `ai4e_core.abilities.eval.trajectory.trajectory_metrics`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import numpy as np
from ai4e_core.abilities.eval.trajectory import named_frame_metrics

truth = np.ones((2, 3, 4, 1))
prediction = truth * 1.1
metrics = named_frame_metrics(prediction, truth, ids=["a", "b"],
    times=[0., 1., 2.], fields=["u"], units=["1"])
assert len(metrics["rows"]) == 6
assert abs(metrics["mean_relative_l2"] - 0.1) < 1e-12
```

## 继续阅读

[接入细节](../reference/artifact-layout.md) · [帮助首页](../index.md)
