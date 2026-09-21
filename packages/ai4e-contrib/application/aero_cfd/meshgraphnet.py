"""静态外流 MeshGraphNet 的字段、工况、分区训练和完整推理连接。"""

from __future__ import annotations

from copy import deepcopy

import torch

from ai4e_contrib.ability.model.meshgraphnet.static import StaticMeshGraphNet
from ai4e_core.abilities.geometry.mesh_graph import edge_features, induced_subgraph
from ai4e_core.abilities.sampling.graph import partition_with_halo

SOURCE = "Dojo/static-aero-meshgraphnet-v1"


def resolve(config: dict, *, validate: bool = True) -> dict:
    """补齐静态图网络训练默认值，并校验 halo 与 Processor 感受野。"""
    cfg = deepcopy(config)
    parameters = cfg.setdefault("model", {}).setdefault("parameters", {})
    parameters.setdefault("hidden_dim", 128)
    parameters.setdefault("processor_layers", 15)
    cfg["model"].setdefault("initial_weights", None)
    cfg["model"].setdefault("freeze", [])
    train = cfg.setdefault("train", {})
    defaults = {
        "max_epochs": 2,
        "batch_size": 1,
        "num_workers": 0,
        "device": "auto",
        "precision": "fp32",
        "optimizer": "adamw",
        "learning_rate": 1e-4,
        "weight_decay": 0.0,
        "betas": [0.9, 0.999],
        "scheduler": "warmup_cosine",
        "warmup_ratio": 0.05,
        "min_lr": 1e-6,
        "accumulate": 1,
        "gradient_clip": 1.0,
        "evaluation_enabled": False,
        "snapshot": True,
        "save_on_interrupt": True,
    }
    for key, value in defaults.items():
        train.setdefault(key, value)
    sampling = cfg.setdefault("sampling", {})
    sampling.setdefault("seed", 42)
    layers = int(parameters["processor_layers"])
    if validate:
        if layers < 1 or int(parameters["hidden_dim"]) < 1:
            raise ValueError("MeshGraphNet 隐藏宽度和 Processor 层数必须为正")
        for domain, roles in (sampling.get("domains") or {}).items():
            for role, spec in roles.items():
                if spec.get("method", "full") == "core_halo" and int(spec["halo_hops"]) != layers:
                    raise ValueError(f"{domain}/{role}: halo_hops 必须等于 processor_layers")
    return cfg


def training_parameters(config: dict) -> dict:
    """从数据规格计算中立域网络宽度。"""
    specs = config["model"]["data_specs"]
    condition_width = sum(int(v) for v in (specs.get("conditioning_dims") or {}).values())
    domains = {}
    for name, spec in specs["domains"].items():
        domains[name] = {
            "node_input_dim": int(specs["position_dim"])
            + sum(int(v) for v in (spec.get("feature_dim") or {}).values())
            + condition_width,
            "edge_input_dim": int(specs["position_dim"]) + 1,
            "output_dim": sum(int(v) for v in spec["output_dims"].values()),
            "outputs": dict(spec["output_dims"]),
        }
    return {**config["model"]["parameters"], "domains": domains}


def construct(**parameters):
    """构造静态单域或多域网络。"""
    return StaticMeshGraphNet(**parameters)


def describe(model) -> dict:
    """返回检查点结构身份和公开输入布局。"""
    return {
        "model_version": model.structure_version,
        "input_layout": {
            name: {
                "node_input_dim": spec["node_input_dim"],
                "edge_input_dim": spec["edge_input_dim"],
                "outputs": spec["outputs"],
            }
            for name, spec in model.layouts.items()
        },
        "processor_layers": model.processor_layers,
    }


construct.describe = describe


def _node_features(sample, config, normalization, domain, binding):
    fields = normalization.apply(sample["fields"])
    positions = fields[binding["position"]]
    chunks = [positions]
    for feature in config["model"]["data_specs"]["domains"][domain].get("feature_dim", {}):
        chunks.append(fields[binding["features"][feature]])
    for condition in config["model"]["data_specs"].get("conditioning_dims", {}):
        source = config["trainprep"]["conditioning"][condition]["field"]
        value = normalization.transforms[source].apply(sample["conditions"][source])
        chunks.append(value.expand(len(positions), -1))
    return fields, positions, torch.cat(chunks, dim=-1)


def prepare_sample(
    sample: dict, config: dict, normalization, *, evaluation: bool = False, epoch: int = 0
) -> dict:
    """按域组装节点、边、核心监督与样本工况。"""
    graphs, targets, metadata = {}, {}, {**sample["identity"], "domains": {}}
    role = "infer" if evaluation else "train"
    for domain, binding in config["trainprep"]["domains"].items():
        graph = sample["domains"][domain].get("graph")
        if graph is None:
            raise ValueError(f"{domain}: 物理样本未绑定图拓扑")
        fields, positions, nodes = _node_features(sample, config, normalization, domain, binding)
        full_edges = graph["edge_index"]
        sampling = config["sampling"]["domains"][domain].get(role) or {"method": "full"}
        parts = _parts(graph, len(positions), sampling, role=role)
        selected = parts[epoch % len(parts)] if not evaluation else parts[0]
        node_ids, core_mask = selected["node_ids"], selected["core_mask"]
        local_edges, _ = induced_subgraph(full_edges, node_ids, node_count=len(positions))
        graphs[domain] = {
            "node_features": nodes[node_ids],
            "edge_features": edge_features(positions[node_ids], local_edges),
            "edge_index": local_edges,
            "core_mask": core_mask,
        }
        metadata["domains"][domain] = {
            "node_ids": node_ids,
            "core_ids": node_ids[core_mask],
            "topology_digest": graph["topology_digest"],
        }
        for output, source in binding["targets"].items():
            targets[f"{domain}_{output}_target"] = fields[source][node_ids][core_mask]
    return {"inputs": {"graphs": graphs}, "targets": targets, "metadata": [metadata]}


def collate(items):
    """静态图外流案例保留单样本批次，避免跨大图隐式复制。"""
    if len(items) != 1:
        raise ValueError("静态 MeshGraphNet 当前要求 batch_size=1")
    return items[0]


def predict(model, inputs: dict) -> dict[str, torch.Tensor]:
    """执行网络并只交付核心节点的具名输出。"""
    raw = model(inputs["graphs"])
    result = {}
    for domain, values in raw.items():
        offset = 0
        mask = inputs["graphs"][domain]["core_mask"]
        for name, width in model.layouts[domain]["outputs"].items():
            result[f"{domain}_{name}"] = values[mask, offset : offset + int(width)]
            offset += int(width)
    return result


def loss(model, batch: dict, config: dict) -> dict:
    """按现有外流监督声明汇总各域核心节点损失。"""
    from ai4e_core.abilities.constraint.supervised import supervised

    return supervised(
        predict(model, batch["inputs"]), batch["targets"], config["model"]["supervision"]
    )


@torch.no_grad()
def predict_sample(
    model, sample: dict, config: dict, normalization, *, preparation_id: str
) -> dict:
    """按核心块和足够 halo 推理，并按平台行顺序完整拼回。"""
    del preparation_id
    device = next(model.parameters()).device
    output = {}
    for domain, binding in config["trainprep"]["domains"].items():
        graph = sample["domains"][domain]["graph"]
        _fields, positions, nodes = _node_features(sample, config, normalization, domain, binding)
        spec = config["sampling"]["domains"][domain].get("infer") or {"method": "full"}
        parts = _parts(graph, len(nodes), spec, role="infer")
        domain_result = torch.empty(
            len(nodes), model.layouts[domain]["output_dim"], dtype=nodes.dtype
        )
        written = torch.zeros(len(nodes), dtype=torch.bool)
        for part in parts:
            node_ids, mask = part["node_ids"], part["core_mask"]
            edges, _ = induced_subgraph(graph["edge_index"], node_ids, node_count=len(nodes))
            values = model(
                {
                    domain: {
                        "node_features": nodes[node_ids].to(device),
                        "edge_features": edge_features(positions[node_ids], edges).to(device),
                        "edge_index": edges.to(device),
                    }
                }
            )[domain].cpu()[mask]
            core = node_ids[mask]
            if written[core].any():
                raise ValueError(f"{domain}: 核心分区重复写入")
            domain_result[core] = values
            written[core] = True
        if not written.all():
            raise ValueError(f"{domain}: 核心分区未覆盖完整域")
        offset = 0
        for name, width in model.layouts[domain]["outputs"].items():
            source = binding["targets"][name]
            output[source] = normalization.inverse(
                source, domain_result[:, offset : offset + int(width)]
            )
            offset += int(width)
    return output


def _parts(graph: dict, count: int, settings: dict, *, role: str) -> list[dict[str, torch.Tensor]]:
    edge_index = graph["edge_index"]
    method = settings.get("method", "full")
    if method == "full":
        ids = torch.arange(count)
        return [
            {"core_ids": ids, "node_ids": ids, "core_mask": torch.ones(count, dtype=torch.bool)}
        ]
    if method != "core_halo":
        raise ValueError(f"未知图采样方法: {method}")
    expected = {
        "method": "core_halo",
        "core_nodes": int(settings["core_nodes"]),
        "halo_hops": int(settings["halo_hops"]),
    }
    cached = (graph.get("partitions") or {}).get(role)
    if cached and cached.get("settings") == expected:
        return cached["items"]
    return partition_with_halo(edge_index, count, expected["core_nodes"], expected["halo_hops"])


PLATFORM_LOSSES = {"configurable": True, "allowed": ["mse", "mae", "huber"]}
PLATFORM_SAMPLING = {"configurable": True}
INFERENCE_CAPABILITIES = {"query_chunk_size": False, "physical_fields": True}
