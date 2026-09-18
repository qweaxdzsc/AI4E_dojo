"""独立时空预测，固定物理结果在数据目录交付。"""

from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays, save_arrays


def predict_split(
    model, physical: str, output: str, predict, *, batch_size: int, provenance: dict, derived=None
) -> str:
    """逐批预测保留样本身份；任何批次失败均不发布完整清单。"""
    record, arrays = read_arrays(physical, kind="spatiotemporal-physical-v1")
    fields = []
    for offset in range(0, len(arrays["u"]), batch_size):
        u = torch.from_numpy(arrays["u"][offset : offset + batch_size].copy())
        f = torch.from_numpy(arrays["f"][offset : offset + batch_size].copy())
        fields.append(predict(model, u, f, batch_index=offset // batch_size).numpy())
    field = np.concatenate(fields)
    output_arrays = {
        "prediction": field[:, 0],
        "target": arrays["u"],
        "forcing": field[:, 1, :80],
        "ids": arrays["ids"],
    }
    extra, descriptions = derived(output_arrays) if derived else ({}, {})
    if set(extra) != set(descriptions) or any(
        set(item) != {"units", "axes"} for item in descriptions.values()
    ):
        raise ValueError("派生场须逐项声明 units 和 axes")
    if set(extra) & set(output_arrays):
        raise ValueError("派生场不能覆盖预测、真值或身份")
    for value in extra.values():
        if len(value) != len(arrays["ids"]):
            raise ValueError("派生输出须保留样本身份")
    return save_arrays(
        Path(output),
        {**output_arrays, **extra},
        kind="spatiotemporal-result-v1",
        metadata={
            "physical_sha256": digest(physical),
            "source": record["metadata"],
            "provenance": provenance,
            "derived_fields": descriptions,
        },
    )
