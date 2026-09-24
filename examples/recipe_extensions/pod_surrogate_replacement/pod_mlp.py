"""用户POD系数代理：复用经典MLP及公开训练器，安全数组状态由数据能力保存。"""

import numpy as np
import torch

from ai4e_core import run
from ai4e_core.abilities.inference.randomness import seeded_randomness
from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.applications.base.iteration_training import train_model


class CoefficientPredictor:
    """普通NumPy预测对象；不要求研究者继承统一估计器。"""

    def __init__(self, model):
        self.model = model

    def predict(self, values):
        """系数输入输出保持FP64；模式保护与梯度策略属于此普通对象。"""
        with torch.no_grad():
            return self.model(torch.as_tensor(np.array(values), dtype=torch.float64)).numpy()


def rebuild(state):
    """仅重建本地明确声明的模型，不执行序列化代码。"""
    if state["kind"] != "local-pod-mlp-v1":
        raise ValueError("不是本扩展的系数状态")
    model = MLP(state["input_dim"], state["output_dim"], tuple(state["hidden"])).double()
    model.load_state_dict({k: torch.as_tensor(v) for k, v in state["weights"].items()}, strict=True)
    return CoefficientPredictor(model)


def fit(family, x, y, params=None, *, deadline=None, cancelled=None):
    """fit替换位置接入真正的共享迭代训练；family仅是基案例的选择标签。

    POD基底在准备中冻结；MLP学习历史系数到下一帧系数。该入口从头拟合，
    最终状态用于预测恢复；完整优化器接续可使用生成的训练检查点另行研究。
    """
    options = dict(params or {})
    hidden = options.pop("hidden", [16])
    updates, seed = options.pop("updates", 20), options.pop("seed", 42)
    if options:
        raise ValueError(f"未使用的系数MLP参数: {sorted(options)}")
    x = torch.as_tensor(np.array(x), dtype=torch.float64)
    y = torch.as_tensor(np.array(y), dtype=torch.float64)
    with seeded_randomness(seed):
        model = MLP(x.shape[1], y.shape[1], tuple(hidden)).double()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        stream = IterationStream(len(x), 2 if len(x) % 2 == 0 else 1, seed=seed)

        def batch(ids):
            return x[ids], y[ids]

        def objective(network, item):
            return (network(item[0]) - item[1]).square().mean()

        report = train_model(
            model,
            optimizer,
            stream,
            batch,
            objective,
            updates=updates,
            session=run.TrainingRun(),
            contract={"hidden": hidden, "seed": seed},
            namespace="coefficient",
            deadline=deadline,
            cancelled=cancelled,
            max_grad_norm=None,
            checkpoint_every=max(1, updates),
        )
    if report["updates"] != updates or report["status"] != "complete":
        raise RuntimeError("系数MLP训练未完整完成")
    state = {
        "kind": "local-pod-mlp-v1",
        "input_dim": x.shape[1],
        "output_dim": y.shape[1],
        "hidden": hidden,
        "weights": {k: v.detach().numpy().copy() for k, v in model.state_dict().items()},
    }
    return CoefficientPredictor(model), state, {"updates": updates, "loss": report["loss"]}
