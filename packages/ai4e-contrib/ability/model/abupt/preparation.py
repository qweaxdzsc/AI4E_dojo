"""AB-UPT 在物理数据视图上的输入准备与完整域查询。"""

import torch

from ai4e_core.abilities.inference.query import query_model
from ai4e_core.abilities.training.batch import to_device

from .batch import collate
from .inference import InferenceContext
from .model import predict
from .sampling import prepare_inputs


def prepare_sample(
    sample: dict, config: dict, normalization, *, evaluation: bool = False, epoch: int = 0
) -> dict:
    """复用原采样和拼批，样本条件保持单行，在模型内进行调制。"""
    from ai4e_core.abilities.transform.fields import prepare_fields

    fields = normalization.apply(
        prepare_fields(
            sample["fields"],
            zero_fields=config["trainprep"].get("physical_rules", {}).get("zero_fields"),
        )
    )
    fields.update(sample["conditions"])
    item = prepare_inputs(
        fields,
        config["sampling"],
        sample=sample["identity"]["sample"],
        sample_index=sample["identity"]["index"],
        data_specs=config["model"]["data_specs"],
        bindings=config["trainprep"],
        normalization=normalization,
        geometry_conditioning_dims=config["model"].get("geometry_conditioning_dims"),
        epoch=epoch,
        evaluation=evaluation,
    )
    return collate([item])


def loss(model, batch: dict, config: dict) -> dict:
    """按模型的具名监督声明复用监督能力。"""
    from ai4e_core.abilities.constraint.supervised import supervised

    return supervised(
        predict(model, batch["inputs"]), batch["targets"], config["model"]["supervision"]
    )


@torch.no_grad()
def predict_sample(
    model, sample: dict, config: dict, normalization, *, preparation_id: str
) -> dict:
    """用固定锚点缓存查询全部物理点，不以训练抽样代替全点评价。"""
    batch = prepare_sample(sample, config, normalization, evaluation=True)["inputs"]
    batch.pop("domain_query_positions", None)
    batch.pop("domain_query_features", None)
    from ai4e_core.abilities.transform.fields import prepare_fields

    fields = normalization.apply(
        prepare_fields(
            sample["fields"],
            zero_fields=config["trainprep"].get("physical_rules", {}).get("zero_fields"),
        )
    )
    positions, features = {}, {}
    for domain, binding in config["trainprep"]["domains"].items():
        positions[domain] = fields[binding["position"]][None]
        names = config["model"]["data_specs"]["domains"][domain].get("feature_dim") or {}
        if names and config["trainprep"].get("use_physics_features", True):
            features[domain] = torch.cat([fields[binding["features"][n]] for n in names], -1)[None]
    device = next(model.parameters()).device
    result = query_model(
        model,
        to_device(batch, device),
        to_device(positions, device),
        context_factory=InferenceContext,
        features=to_device(features, device) or None,
        preparation_id=preparation_id,
        chunk_size=int((config.get("infer") or config["post"]).get("query_chunk_size", 10000)),
    )
    return {
        source: normalization.inverse(source, result[f"query_{domain}_{name}"][0]).cpu()
        for domain, binding in config["trainprep"]["domains"].items()
        for name, source in binding["targets"].items()
    }
