"""单场与耦合推理装配，能力通过普通回调注入。"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.arrays import save_json, save_npy
from ai4e_core.abilities.inference.execution import inference_group
from ai4e_core.abilities.inference.integration import integrate

from .contracts import component_identity, digest, file_digest


@dataclass
class CoupledPrediction:
    """只在耦合业务使用的装配对象；不作为全仓组件协议。"""

    models: dict
    states: dict
    times: object
    metadata: dict
    velocities: dict = field(default_factory=dict)
    boundary: object = None
    step: object = None
    order: tuple = ()


def bind_field(job, name, *, velocity):
    """绑定一个场速度能力，返回当前装配对象。"""
    if name not in job.models or name in job.velocities:
        raise ValueError("物理场不存在或重复绑定")
    job.velocities[name] = velocity
    return job


def configure_integration(job, *, step, order, boundary=None):
    """绑定积分策略与显式场顺序。"""
    job.step, job.order, job.boundary = step, tuple(order), boundary
    return job


def execute_prediction(job, *, observe=None, cancelled=None):
    """只执行已绑定积分，不从真值猜条件。"""
    job.metadata["integration"] = {
        "time_grid": [float(t) for t in job.times],
        "order": list(job.order),
        "step": component_identity(job.step),
        "completed_steps": 0,
    }

    def record_step(index, time, states):
        job.metadata["integration"]["completed_steps"] = index
        if observe:
            observe(index, time, states)

    with inference_group(job.models.values()):
        return integrate(
            job.states,
            job.times,
            step=job.step,
            velocities=job.velocities,
            order=job.order,
            boundary=job.boundary,
            observe=record_step,
            cancelled=cancelled,
        )


def save_results(predictions, targets, output, *, metadata):
    """固定分场数组与来源，返回独立 post 所需清单。"""
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    fields = {}
    for name, prediction in predictions.items():
        target = targets[name]
        if prediction.shape != target.shape:
            raise ValueError("预测和真值形状不匹配")
        for role, value in (("prediction", prediction), ("target", target)):
            array = (
                value.detach().cpu().numpy()
                if isinstance(value, torch.Tensor)
                else np.asarray(value)
            )
            save_npy(output / f"{name}_{role}.npy", array)
        fields[name] = {
            "prediction": f"{name}_prediction.npy",
            "target": f"{name}_target.npy",
            "shape": list(prediction.shape),
            "sha256": {
                role: file_digest(output / f"{name}_{role}.npy")
                for role in ("prediction", "target")
            },
        }
    result = {"kind": "coupled_results_v1", "fields": fields, "metadata": metadata}
    result["content_id"] = digest(result)
    save_json(output / "results.json", result)
    return str((output / "results.json").resolve())
