"""将具名物理域组织为点流、几何条件及监督目标，计算不绑定模型名。"""

import torch

from ai4e_core.abilities.data.validate.physical import validate_bindings
from ai4e_core.abilities.sampling.points import point_indices, select_aligned
from ai4e_core.abilities.transform.point_features import concatenate_fields


def prepare_point_sample(sample, config, normalization, *, evaluation=False, epoch=0):
    """返回 inputs/targets/metadata；几何固定、查询按轮次采样，评价保留全点。

    配置显式声明域顺序、特征顺序及采样预算；节点真值不进入 inputs。
    """
    validate_bindings(sample, config["trainprep"])
    fields = normalization.apply(sample["fields"])
    sampling = config["sampling"]
    identity = sample["identity"]
    sample_key = f"{identity.get('partition', '')}/{identity['sample']}"
    embeddings, targets, metadata = [], {}, {**identity, "domains": {}}
    for domain, specs in config["model"]["data_specs"]["domains"].items():
        binding = config["trainprep"]["domains"][domain]
        ids = sample["domains"][domain]["ids"]
        names = [binding["position"], *[binding["features"][k] for k in specs["feature_dim"]]]
        widths = [config["model"]["data_specs"]["position_dim"], *specs["feature_dim"].values()]
        for name, width in zip(names, widths, strict=True):
            if fields[name].ndim != 2 or fields[name].shape[1] != width:
                raise ValueError(f"{name}: 特征宽度与声明不一致")
        for name, width in specs["output_dims"].items():
            value = fields[binding["targets"][name]]
            if value.ndim != 2 or value.shape != (len(ids), width):
                raise ValueError(f"{domain}.{name}: 目标形状与声明不一致")
        features = concatenate_fields(fields, names, ids=ids)
        budget = len(ids) if evaluation else sampling["domains"][domain]["train"]["max_points"]
        selected = point_indices(
            len(ids),
            min(len(ids), budget),
            seed=sampling["seed"],
            sample=sample_key,
            operation=domain,
            epoch=epoch,
            keep_all=True,
        )
        aligned = select_aligned(
            {"features": features, **{k: fields[v] for k, v in binding["targets"].items()}},
            selected,
        )
        embeddings.append(aligned.pop("features").unsqueeze(0).float())
        for name, value in aligned.items():
            targets[f"{domain}_{name}_target"] = value.float()
        metadata["domains"][domain] = {"node_ids": selected, "entity_ids": ids[selected]}
    geometry = fields[config["trainprep"]["geometry_field"]]
    geometry_ids = point_indices(
        len(geometry),
        min(len(geometry), sampling["geometry"]["max_points"]),
        seed=sampling["seed"],
        sample=sample_key,
        operation="geometry",
        keep_all=True,
    )
    conditions = []
    for name in config["model"]["data_specs"].get("conditioning_dims", {}):
        source = config["trainprep"]["conditioning"][name]["field"]
        value = normalization.transforms[source].apply(sample["conditions"][source])
        if (
            value.numel() != config["model"]["data_specs"]["conditioning_dims"][name]
            or not torch.isfinite(value).all()
        ):
            raise ValueError(f"{source}: 工况宽度或有限性不符")
        conditions.append(value.reshape(1, -1))
    inputs = {
        "local_embedding": tuple(embeddings),
        "geometry": geometry[geometry_ids].unsqueeze(0).float(),
    }
    if conditions:
        inputs["global_embedding"] = torch.cat(conditions, -1).unsqueeze(0).float()
    metadata["geometry_ids"] = geometry_ids
    return {"inputs": inputs, "targets": targets, "metadata": [metadata]}


def collate_point_samples(items):
    """单样本变长点流拼批，不隐式复制大型网格。"""
    if len(items) != 1:
        raise ValueError("当前点流装配要求 batch_size=1")
    return items[0]


def decode_point_outputs(raw, domains):
    """按显式域和输出通道声明，将网络流转换为监督使用的具名字段。"""
    streams = (raw,) if isinstance(raw, torch.Tensor) else raw
    if len(streams) != len(domains):
        raise ValueError("输出流数量与域声明不一致")
    result = {}
    for (domain, spec), value in zip(domains.items(), streams, strict=True):
        if value.ndim != 3 or value.shape[0] != 1:
            raise ValueError("网络输出须为单样本三维张量")
        offset = 0
        for name, width in spec["output_dims"].items():
            result[f"{domain}_{name}"] = value[0, :, offset : offset + width]
            offset += width
        if value.ndim != 3 or value.shape[0] != 1 or value.shape[-1] != offset:
            raise ValueError("网络输出通道或批次不符")
    return result
