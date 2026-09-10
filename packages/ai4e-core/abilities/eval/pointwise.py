"""逐点监督评估；按实际元素累计，保留参考浮点运算空间。"""

import numpy as np
import torch

from ai4e_core.abilities.training.batch import to_device
from ai4e_core.base.events import sample_context


@torch.no_grad()
def evaluate(model, batches, predict, normalization):
    """完整验证块一次前向，标准化空间和物理空间分别记账。"""
    modes = {module: module.training for module in model.modules()}
    total, elements, points = 0.0, 0, 0
    width = len(normalization.record["labels"]["mean"])
    squared, absolute = np.zeros(width, dtype=np.float64), np.zeros(width, dtype=np.float64)
    device = next(model.parameters()).device
    try:
        model.eval()
        for batch in batches:
            with sample_context("完整分块验证", batch["metadata"]):
                inputs = to_device(batch["inputs"], device)
                target = batch["targets"]["fields"].to(device)
                output = predict(model, inputs)["fields"]
                if output.shape != target.shape or not torch.isfinite(output).all():
                    raise ValueError("验证预测形状不符或非有限")
                difference = output - target
                total += float(difference.square().sum().cpu())
                elements += difference.numel()
                mean = torch.tensor(
                    normalization.record["labels"]["mean"], device=device, dtype=output.dtype
                )
                std = torch.tensor(
                    normalization.record["labels"]["std"], device=device, dtype=output.dtype
                )
                physical_difference = (output * std + mean).cpu().numpy() - batch[
                    "physical"
                ].numpy()
                squared += np.square(physical_difference, dtype=np.float64).sum(axis=(0, 1))
                absolute += np.abs(physical_difference).sum(axis=(0, 1))
                points += physical_difference.shape[0] * physical_difference.shape[1]
    finally:
        for module, mode in modes.items():
            module.training = mode
    if not elements or not points:
        raise ValueError("验证数据为空")
    return {
        "loss": total / elements,
        "normalized_mse": total / elements,
        "physical_mse": (squared / points).tolist(),
        "physical_mae": (absolute / points).tolist(),
        "element_count": elements,
        "point_count": points,
    }
