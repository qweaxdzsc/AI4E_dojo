"""GenCP 数据、模型与领域步骤的局部连接；数值计算委托 ability。"""

from functools import partial

import torch

from ai4e_contrib.ability.inference.gencp.velocity import fsi_velocity, nt_velocity
from ai4e_contrib.ability.transform.gencp.normalization import fsi_normalize, nt_normalize
from ai4e_contrib.ability.transform.gencp.state import split_fsi
from ai4e_contrib.application.datasets.gencp import fsi, ntcouple
from ai4e_core.applications.coupled_physics.infer import CoupledPrediction
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples


def dataset_adapter(dataset):
    """返回原生读取与来源描述模块，不在 core 判断数据集名称。"""
    return ntcouple if dataset == "ntcouple" else fsi


def descriptions(cfg, root):
    """准备分场训练/验证和耦合评价来源。"""
    dataset = cfg["dataset"]["name"]
    adapter = dataset_adapter(dataset)
    output = {}
    for field in cfg["fields"]:
        for phase, count in (
            ("train", cfg["data"]["train_count"]),
            ("val", cfg["data"]["val_count"]),
        ):
            split = "decouple_" + phase if dataset == "ntcouple" else phase
            output[field + "/" + phase] = adapter.describe(
                root, dataset, field, split, count, seed=cfg["seed"]
            )
        if dataset == "ntcouple":
            output[field + "/couple"] = adapter.describe(
                root, dataset, field, "couple_val", cfg["data"]["val_count"]
            )
    if dataset != "ntcouple":
        output["couple"] = adapter.describe(
            root, dataset, "couple", "val", cfg["data"]["val_count"]
        )
    return output


def inference_inputs(preparation, models, *, device, flow_steps):
    """提取配对样本与明确外部边界，再初始化各场生成噪声。"""
    dataset = preparation["dataset"]
    adapter = dataset_adapter(dataset)
    descriptions = preparation["descriptions"]
    if dataset == "ntcouple":
        batches = {}
        for field in ("neutron", "solid", "fluid"):
            data = FieldSamples(descriptions[field + "/couple"], adapter.read_sample)
            batches[field] = data.batch(range(len(data)), device)
        states = {field: torch.randn_like(batch["target"]) for field, batch in batches.items()}
        boundary = {
            "neutron": batches["neutron"]["input"][:, :, :, 0:1, 1:2],
            "solid": batches["solid"]["target"][:, :, :, 0:1, :],
        }
        targets = {field: batch["physical"] for field, batch in batches.items()}
        context = {"boundary": boundary, "history": None}
        times = torch.linspace(0, 1, flow_steps + 1).to(device)
    else:
        data = FieldSamples(descriptions["couple"], adapter.read_sample)
        batch = data.batch(range(len(data)), device)
        initial = torch.randn_like(batch["target"])
        states = split_fsi(initial)
        targets = split_fsi(batch["physical"])
        context = {"history": batch["input"], "initial": initial, "boundary": {}}
        # 原 FSI 使用 Python s/N；避免 linspace FP32 改变流时间舍入。
        times = [s / flow_steps for s in range(flow_steps + 1)]
    # 逐窗口物理帧可追溯；生成流时间另由 job.times 表达。
    physical_frames = {}
    for key, description in descriptions.items():
        if key != "couple" and not key.endswith("/couple"):
            continue
        physical_frames[key] = [
            {
                "id": record["id"],
                "history": [record["window"] + i * record["interval"] for i in range(3)],
                "prediction": [record["window"] + (3 + i) * record["interval"] for i in range(12)],
            }
            if "window" in record
            else {"id": record["id"], "prediction": description["time_indices"]}
            for record in description["records"]
        ]
    coordinates = (
        adapter.coordinates(descriptions["couple"])
        if dataset != "ntcouple"
        else {
            "kind": "published_array_indices",
            "field_shapes": {name: list(value.shape[1:]) for name, value in states.items()},
        }
    )
    job = CoupledPrediction(
        models,
        states,
        times,
        metadata={
            "system_id": preparation["content_id"],
            "dataset": dataset,
            "physical_frames": physical_frames,
            "coordinates": coordinates,
            "trajectories": {
                key: {
                    k: v
                    for k, v in value.items()
                    if k in ("records", "time_indices", "units", "axes", "normalization")
                }
                for key, value in descriptions.items()
                if key.endswith("/couple") or key == "couple"
            },
        },
    )
    return job, context, targets


def bind_velocity(model, *, dataset, field, context, condition=None):
    """连接当前场模型与条件函数，返回普通速度回调。"""
    if dataset == "ntcouple":
        return partial(
            nt_velocity, model, field=field, condition=condition, boundary=context["boundary"]
        )
    return partial(fsi_velocity, model, history=context["history"])


def physical_predictions(states, preparation):
    """按各场冻结变换恢复物理空间，保留不同空间形状。"""
    if preparation["dataset"] == "ntcouple":
        return {field: nt_normalize(value, field, inverse=True) for field, value in states.items()}
    from ai4e_contrib.ability.transform.gencp.state import join_fsi

    result = fsi_normalize(
        join_fsi(states), preparation["descriptions"]["couple"]["normalization"], inverse=True
    )
    return split_fsi(result)
