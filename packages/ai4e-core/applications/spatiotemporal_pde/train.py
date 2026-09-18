"""时空模型训练绑定，循环和持久化使用共享运行能力。"""

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from ai4e_core.applications.base.iteration_training import train_model


def fit(
    model,
    prepared: str,
    optimizer,
    stream,
    objective,
    *,
    device,
    session,
    contract,
    updates,
    scheduler=None,
    ema=None,
    resume=None,
    deadline=None,
    cancelled=None,
    update_step=None,
) -> dict:
    """从已校验准备取批并执行完整状态恢复。"""
    _, arrays = read_arrays(prepared, kind="spatiotemporal-prepared-v1")

    def batch(ids):
        return torch.from_numpy(np.array(arrays["values"][ids.tolist()], copy=True)).to(device)

    return train_model(
        model,
        optimizer,
        stream,
        batch,
        objective,
        updates=updates,
        session=session,
        contract=contract,
        namespace="train",
        scheduler=scheduler,
        ema=ema,
        resume=resume,
        deadline=deadline,
        cancelled=cancelled,
        update_step=update_step,
    )
