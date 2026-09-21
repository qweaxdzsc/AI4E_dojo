<!-- dojo-help: {"topic_id": "capability:loss", "title": "损失与物理约束", "kind": "tutorial", "layer": "capability", "domain": "loss", "summary": "监督项、权重、可微比较和自定义物理残差", "tasks": ["损失函数", "物理约束", "多场加权"], "symbols": ["ai4e_core.abilities.constraint.supervised.supervised", "ai4e_core.abilities.constraint.compare.compare"], "navigation_order": 4} -->
# 损失与物理约束

supervised 接收预测字典、目标字典和目标项列表，返回标量 loss 与逐项 losses。可选 MSE、MAE、Huber、relative_l2；形状不一致不允许广播，权重必须有限非负且至少一项为正。

PDE 残差、边界条件与采样语义属于科学设置，可通过普通 objective 函数组合现有 constraint 能力。不存在自动适配任意 PDE 的约束。训练的整场 relative_l2 与逐样本等权评价不是同一归约；修改损失须保存定义和权重。

## 直接入口

- `ai4e_core.abilities.constraint.supervised.supervised`
- `ai4e_core.abilities.constraint.compare.compare`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import torch
from ai4e_core.abilities.constraint.supervised import supervised

p = torch.tensor([1., 3.], requires_grad=True)
result = supervised({"u": p}, {"u": torch.tensor([1., 2.])},
    [{"name": "fit", "prediction": "u", "target": "u", "weight": 2.0}])
assert result["loss"].item() == 1.0
result["loss"].backward()
torch.testing.assert_close(p.grad, torch.tensor([0., 2.]))
```

## 继续阅读

[接入细节](../user-components/loss-and-constraint.md) · [帮助首页](../index.md)
