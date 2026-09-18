"""原单场条件生成的验证装配；已知其他场只用于单场验证。"""

import torch

from ai4e_contrib.ability.inference.gencp.velocity import single_field
from ai4e_core.abilities.inference.execution import inference_execution
from ai4e_core.abilities.inference.randomness import seeded_randomness
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples

from .cases import dataset_adapter


def validation_batch(preparation, field, device):
    """按冻结验证身份读取实际样本。"""
    data = FieldSamples(
        preparation["descriptions"][field + "/val"],
        dataset_adapter(preparation["dataset"]).read_sample,
    )
    return data.batch(range(len(data)), device)


def generate_single(model, batch, *, dataset, field, settings, seed=43):
    """复现原单场生成网格，隔离验证对训练随机流的影响。"""
    with inference_execution(model), seeded_randomness(seed):
        return single_field(
            model,
            batch["input"],
            batch["target"],
            dataset=dataset,
            field=field,
            points=settings.get("single_points", 10),
            clean_neutron=settings["objective"].get("clean_neutron", True),
            clean_solid=settings["objective"].get("clean_solid", False),
        )


def selection_metric(prediction, target, field, *, dataset, normalization=None):
    """原选优口径：物理空间 FSI 的 u/SDF，NT 逐分量平均。"""
    from ai4e_contrib.ability.transform.gencp.normalization import fsi_normalize, nt_normalize

    if dataset != "ntcouple":
        prediction = fsi_normalize(prediction, normalization, inverse=True)
        target = fsi_normalize(target, normalization, inverse=True)
        selection = slice(0, 1) if field == "fluid" else slice(3, 4)
        prediction, target = prediction[..., selection], target[..., selection]
    else:
        prediction, target = (
            nt_normalize(prediction, field, inverse=True),
            nt_normalize(target, field, inverse=True),
        )
    axes = (1, 2, 3)
    error = (prediction - target).square().sum(dim=axes).sqrt()
    norm = target.square().sum(dim=axes).sqrt()
    if torch.any(norm == 0):
        raise ValueError("验证真值范数为零")
    return float((error / norm).mean())
