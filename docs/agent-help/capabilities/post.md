<!-- dojo-help: {"topic_id": "capability:post", "title": "后处理、图表与结果导出", "kind": "tutorial", "layer": "capability", "domain": "post", "summary": "固定预测读回、误差曲线、物理场图、差值和网格导出", "tasks": ["后处理", "误差曲线", "可视化", "固定预测"], "symbols": ["ai4e_core.abilities.postproc.visualization.trajectory.plot_named_frames", "ai4e_core.abilities.postproc.visualization.trajectory.plot_frame", "ai4e_core.abilities.postproc.difference.difference"], "navigation_order": 8} -->
# 后处理、图表与结果导出

post 读取固定预测与评价，不重新训练或推理。plot_named_frames 接收 named_frame_metrics 的结果，绘制各场随物理时间的 MSE 并返回文件路径；plot_frame 对 [B,T,H,W,C] 数据绘制真值/预测/误差。更完整的曲面、截面、探针和导出通过 postproc/visualization、postproc/export 选择。

图表保留来源、字段、单位、样本身份与色标；图像存在不能替代数值验证。仅绘图不要求启动 Web/Vis 服务。

## 直接入口

- `ai4e_core.abilities.postproc.visualization.trajectory.plot_named_frames`
- `ai4e_core.abilities.postproc.visualization.trajectory.plot_frame`
- `ai4e_core.abilities.postproc.difference.difference`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
from pathlib import Path
import numpy as np
from ai4e_core.abilities.eval.trajectory import named_frame_metrics
from ai4e_core.abilities.postproc.visualization.trajectory import plot_named_frames

truth = np.ones((1, 3, 4, 1))
metrics = named_frame_metrics(truth * 1.1, truth, ids=["a"], times=[0., 1., 2.],
    fields=["u"], units=["1"])
path = Path("error-curve.png").resolve()
assert plot_named_frames(path, metrics, time_unit="s") == str(path)
assert path.read_bytes().startswith(b"\x89PNG")
```

## 继续阅读

[接入细节](../user-components/post.md) · [帮助首页](../index.md)
