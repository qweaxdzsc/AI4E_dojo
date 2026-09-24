<!-- dojo-help: {"topic_id": "capability:inference", "title": "推理与多步滚动", "kind": "tutorial", "layer": "capability", "domain": "inference", "summary": "神经网络执行上下文、普通对象分批预测、多步滚动和设备同步计时", "tasks": ["推理", "多步滚动预测", "MPS 计时", "普通对象预测", "POD 代理预测"], "symbols": ["ai4e_core.abilities.inference.execution.inference_execution", "ai4e_core.abilities.inference.rollout.rollout", "ai4e_core.abilities.inference.timing.measure", "ai4e_core.abilities.inference.callable_prediction.predict_batches"], "navigation_order": 6} -->
# 推理与多步滚动

inference_execution 临时切换 eval/no_grad 并在异常或完成后恢复各子模块模式与 RNG；rollout 接收初态、步数及 advance 函数，返回时间轴在最前且包含初态的序列，逐步拒绝形状变化和非有限值。

多帧历史输入、多帧块输出需要研究脚本显式组装历史窗口，不能把普通 rollout 当作自动适配器。计时需要 warmup 和设备同步，报告完整预测窗口、归一化、反归一化、数据搬运边界。

## 普通对象与全局算子

[predict_batches](../api/core/abilities/inference/callable_prediction.md) 接收样本数组及普通 callable，返回数组或数组元组，保留顺序、尾批、精度，并复制可能复用的输出缓冲。RSM/RBF/Kriging/LightGBM 可传 `model.predict`；它不调用 `.eval()`、不自动关闭梯度或管理 RNG，调用方负责实际执行上下文。

FNO 每个样本的完整空间域不可切成独立小块计算；POD 系数预测后还需按同一基解码、反归一化，并恢复字段与实体顺序。DeepONet 查询布局与传感器身份由其连接负责。

## 直接入口

- `ai4e_core.abilities.inference.execution.inference_execution`
- `ai4e_core.abilities.inference.rollout.rollout`
- `ai4e_core.abilities.inference.timing.measure`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import torch
from ai4e_core.abilities.inference.execution import inference_execution
from ai4e_core.abilities.inference.rollout import rollout

model = torch.nn.Linear(2, 2)
model.train()
with inference_execution(model):
    states = rollout(torch.ones(3, 2), 4, lambda state, step: model(state))
    assert states.shape == (5, 3, 2)
    assert not states.requires_grad and not model.training
assert model.training

# 非梯度拟合与普通对象预测，不需要 torch.Module 协议。
from pathlib import Path
import numpy as np
from ai4e_core.abilities.training.algebraic import fit_rsm
from ai4e_core.abilities.modeling.models.rsm import ResponseSurface
from ai4e_core.abilities.data.save.surrogate import save_state, read_state
from ai4e_core.abilities.inference.callable_prediction import predict_batches

x = np.arange(7, dtype=np.float64)[:, None]
y = 1 + 2 * x + 3 * x**2
state = fit_rsm(x, y, degree=2)
context = {"features": ["x"], "targets": ["y"], "data": "demo-v1"}
manifest = save_state(Path.cwd() / "data" / "rsm", state, context=context)
restored, identity = read_state(manifest)
assert identity == context  # 真实应用还需与当前准备、归一化等声明比较
predictor = ResponseSurface.from_state(restored)
actual = predict_batches(x, predictor.predict, batch_size=3)
np.testing.assert_allclose(actual, y, rtol=1e-12, atol=1e-12)
```

## 继续阅读

[接入细节](../user-components/inference.md) · [帮助首页](../index.md)
