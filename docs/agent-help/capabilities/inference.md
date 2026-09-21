<!-- dojo-help: {"topic_id": "capability:inference", "title": "推理与多步滚动", "kind": "tutorial", "layer": "capability", "domain": "inference", "summary": "无梯度推理、模式与随机状态保护、滚动预测和设备同步计时", "tasks": ["推理", "多步滚动预测", "MPS 计时"], "symbols": ["ai4e_core.abilities.inference.execution.inference_execution", "ai4e_core.abilities.inference.rollout.rollout", "ai4e_core.abilities.inference.timing.measure"], "navigation_order": 6} -->
# 推理与多步滚动

inference_execution 临时切换 eval/no_grad 并在异常或完成后恢复各子模块模式与 RNG；rollout 接收初态、步数及 advance 函数，返回时间轴在最前且包含初态的序列，逐步拒绝形状变化和非有限值。

多帧历史输入、多帧块输出需要研究脚本显式组装历史窗口，不能把普通 rollout 当作自动适配器。计时需要 warmup 和设备同步，报告完整预测窗口、归一化、反归一化、数据搬运边界。

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
```

## 继续阅读

[接入细节](../user-components/inference.md) · [帮助首页](../index.md)
