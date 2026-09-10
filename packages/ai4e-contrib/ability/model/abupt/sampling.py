"""按域绑定字段、独立抽点、样本级条件与监督目标准备。"""

import json
from pathlib import Path

import torch

from ai4e_core.abilities.sampling.points import point_indices

from .domains import DomainLayout


def prepare_inputs(
    fields,
    config,
    *,
    sample,
    data_specs,
    bindings,
    normalization=None,
    geometry_conditioning_dims=None,
    epoch=0,
    evaluation=False,
    repeat=None,
    indices=None,
    sample_index=0,
):
    """输入为归一化点场；固定下标可用于参考对齐，生产默认独立随机流。"""
    layout = DomainLayout(data_specs, geometry_conditioning_dims)
    if (
        config.get("train_randomness", "per_epoch") != "per_epoch"
        or config.get("evaluation_randomness", "fixed") != "fixed"
    ):
        raise ValueError("需要逐轮训练和固定评估采样")
    epoch = repeat if repeat is not None else (0 if evaluation else epoch)
    if epoch < 0:
        raise ValueError("采样轮次必须非负")
    supplied = indices or {}

    def choose(operation, count, declaration, geometry=False):
        if (
            declaration.get("method", "uniform") != "uniform"
            or declaration.get("replacement", False)
            or declaration.get("insufficient", "error") != "error"
        ):
            raise ValueError("只支持均匀无放回采样，候选不足失败")
        budget = int(declaration.get("max_points" if geometry else "num_points", 0))
        if budget < 0:
            raise ValueError("采样预算不能为负")
        if geometry:
            budget = min(count, budget)
        if operation in supplied:
            selected = torch.as_tensor(supplied[operation])
            if selected.dtype not in (torch.int32, torch.int64):
                raise ValueError("固定采样下标必须是整数")
            selected = selected.long()
            if (
                selected.ndim != 1
                or len(selected) != budget
                or len(selected.unique()) != budget
                or (selected < 0).any()
                or (selected >= count).any()
            ):
                raise ValueError("固定采样下标错误")
            return selected
        if budget == 0:
            return torch.empty(0, dtype=torch.long)
        stream = config.get("random_stream", "independent")
        if stream not in {"independent", "global"}:
            raise ValueError("未知采样随机流")
        if stream == "global":
            if budget > count:
                raise ValueError("候选不足")
            if operation != "supernodes" and budget == count:
                return torch.arange(count)
            seed = config.get("pipeline_seed")
            generator = None
            if seed is not None:
                offset = (
                    1
                    if operation == "geometry"
                    else 2
                    if operation == "supernodes"
                    else 3 + list(layout.domains).index(operation.rsplit("_", 1)[0])
                )
                generator = torch.Generator().manual_seed(int(seed) + int(sample_index) + offset)
            return torch.randperm(count, generator=generator)[:budget]
        return point_indices(
            count,
            budget,
            seed=int(config["seed"]),
            sample=sample,
            operation=operation,
            epoch=epoch,
            keep_all=geometry and declaration.get("keep_order_when_all", True),
        )

    def field(name, width, count=None):
        if name not in fields:
            raise ValueError(f"绑定字段不存在: {name}")
        if normalization is not None and name not in normalization.transforms:
            raise ValueError(f"绑定字段必须声明变换或恒等变换: {name}")
        value = fields[name]
        if value.ndim == 1 and width == 1:
            value = value[:, None]
        if (
            value.ndim != 2
            or value.shape[1] != width
            or (count is not None and len(value) != count)
        ):
            raise ValueError(f"绑定字段形状不一致: {name}")
        return value

    geometry = field(bindings["geometry_field"], 3)
    gids = choose("geometry", len(geometry), config["geometry"], True)
    supernodes = choose("supernodes", len(gids), config["supernodes"])
    if not len(gids) or not len(supernodes):
        raise ValueError("几何及超节点不能为空")
    inputs = {
        "geometry_position": geometry[gids],
        "geometry_supernode_idx": supernodes,
        "domain_anchor_positions": {},
        "domain_query_positions": {},
        "domain_anchor_features": {},
        "domain_query_features": {},
    }
    targets, selected, rows = {}, {}, {}
    if set(bindings["domains"]) != set(layout.domains) or set(config["domains"]) != set(
        layout.domains
    ):
        raise ValueError("准备绑定和采样域与模型声明不一致")
    for domain in layout.domains:
        binding = bindings["domains"][domain]
        pos = field(binding["position"], 3)
        rows[domain] = {}
        for kind in ("anchor", "query"):
            ids = choose(
                f"{domain}_{kind}", len(pos), config["domains"][domain].get(kind, {"num_points": 0})
            )
            if kind == "anchor" and not len(ids):
                raise ValueError("每域 anchors 必须非空")
            rows[domain][kind] = ids
            if not len(ids):
                continue
            inputs[f"domain_{kind}_positions"][domain] = pos[ids]
            features = []
            for name, width in (
                layout.features[domain] if bindings.get("use_physics_features", True) else ()
            ):
                if name not in binding.get("features", {}):
                    raise ValueError("缺少显式特征来源")
                features.append(field(binding["features"][name], width, len(pos))[ids])
            if features:
                inputs[f"domain_{kind}_features"][domain] = torch.cat(features, dim=-1)
            for name, width in layout.outputs[domain]:
                source = binding.get("targets", {}).get(name)
                if source is None or (kind == "query" and not binding.get("query_targets", False)):
                    continue
                key = f"{'query_' if kind == 'query' else ''}{domain}_{name}"
                value = field(source, width, len(pos))[ids]
                selected[key] = value
                targets[key + "_target"] = value.clone()
    for input_key, binding_key, dims in [
        ("conditioning_inputs", "conditioning", layout.conditions),
        (
            "geometry_conditioning_inputs",
            "geometry_conditioning",
            (() if layout.inherit_geometry else layout.geometry_conditions),
        ),
    ]:
        declarations = bindings.get(binding_key, {})
        if set(declarations) != {n for n, _ in dims}:
            raise ValueError("条件来源与声明不一致")
        values = {}
        for name, width in dims:
            declaration = declarations[name]
            if ("constant" in declaration) == ("path" in declaration):
                raise ValueError("条件必须且只能选择一种来源")
            raw = declaration.get("constant")
            if "path" in declaration:
                records = json.loads(Path(declaration["path"]).read_text())
                if sample not in records:
                    raise ValueError(f"条件缺样本: {sample}")
                raw = records[sample][name]
            tensor = torch.as_tensor(raw, dtype=torch.float32).reshape(1, -1)
            if tensor.shape != (1, width) or not torch.isfinite(tensor).all():
                raise ValueError("条件宽度或数值错误")
            key = declaration.get("normalization", name)
            if normalization is None or key not in normalization.transforms:
                raise ValueError("条件必须声明冻结变换或恒等变换")
            values[name] = normalization.transforms[key].apply(tensor).squeeze(0)
        if values:
            inputs[input_key] = values
    inputs = {k: v for k, v in inputs.items() if not isinstance(v, dict) or v}
    return {
        "inputs": inputs,
        "targets": targets,
        "fields": selected,
        "metadata": {
            "sample": sample,
            "index": int(sample_index),
            "state": "normalized",
            "geometry_rows": gids,
            "domain_rows": rows,
            "normalization_digest": normalization.digest if normalization else None,
        },
    }
