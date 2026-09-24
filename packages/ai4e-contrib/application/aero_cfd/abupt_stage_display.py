"""把公开子模块收成阶段盒，供平台两档图阅读；不实现模型前向合同。"""

from __future__ import annotations

import torch

_STAGE_ATTRS = (
    "encoder",
    "geometry_blocks",
    "blocks",
    "block_types",
    "decoders",
    "readouts",
    "rope",
    "pos_embed",
    "biases",
)


def can_organize_stages(network: torch.nn.Module) -> bool:
    """网络公开编码器、几何块、物理块、解码和读出时，才能收成与选中 E/F 相同的阶段盒。"""
    if any(not hasattr(network, name) for name in _STAGE_ATTRS):
        return False
    blocks = network.blocks
    try:
        blocks = list(blocks)
    except TypeError:
        return False
    return bool(blocks) and all(hasattr(block, "forward_domains") for block in blocks)


def flatten_display_inputs(values):
    """正式预测输入或已摊平的阶段输入都收成单层张量字典，给 TorchVista 当一份前向参数。"""
    if not isinstance(values, dict):
        return values
    if any(key.endswith("_anchor") for key in values):
        return values
    anchors = values.get("domain_anchor_positions")
    if not isinstance(anchors, dict):
        return values
    queries = values.get("domain_query_positions") or {}
    flat = {
        "geometry_position": values["geometry_position"],
        "geometry_supernode_idx": values["geometry_supernode_idx"],
        "geometry_batch_idx": values["geometry_batch_idx"],
    }
    for domain, tensor in anchors.items():
        flat[f"{domain}_anchor"] = tensor
        query = queries.get(domain)
        if query is None:
            query = tensor.new_zeros(tensor.shape[0], 0, tensor.shape[-1])
        flat[f"{domain}_query"] = query
    return flat


class DomainStep(torch.nn.Module):
    """让 DomainBlock 以模块盒出现，避免校验算子散在图上。"""

    def __init__(self, block, kind):
        super().__init__()
        object.__setattr__(self, "block", block)
        object.__setattr__(self, "kind", kind)
        for name, child in block.named_children():
            self.add_module(name, child)

    def forward(self, values, frequencies, sizes, geometry=None, geometry_frequencies=None):
        result, _ = self.block.forward_domains(
            values,
            frequencies,
            sizes,
            kind=self.kind,
            geometry=geometry,
            geometry_frequencies=geometry_frequencies,
        )
        return result


class EncoderStage(torch.nn.Module):
    """多包一层，forced=1 时 encoder 仍收成盒，不把邻域检索算子洒到图上。"""

    def __init__(self, encoder):
        super().__init__()
        self.pool = encoder

    def forward(self, position, supernode_idx, batch_idx):
        return self.pool(position, supernode_idx, batch_idx)


class GeometryStage(torch.nn.Module):
    def __init__(self, steps, rope):
        super().__init__()
        self.blocks = torch.nn.ModuleList(steps)
        object.__setattr__(self, "rope", rope)

    def forward(self, geometry, pos, idx, batch):
        frequencies = self.rope(pos[idx].reshape(geometry.shape[0], -1, 3))
        values = {"geometry": geometry}
        freq = {"geometry": frequencies}
        sizes = {"geometry": geometry.shape[1]}
        for step in self.blocks:
            values = step(values, freq, sizes)
        return values["geometry"], frequencies


class EmbedStage(torch.nn.Module):
    def __init__(self, network, domains):
        super().__init__()
        self.pos_embed = network.pos_embed
        self.domains = tuple(domains)
        for domain in self.domains:
            self.add_module(f"bias_{domain}", network.biases[domain])

    def forward(self, values):
        tokens, positions = {}, {}
        for domain in self.domains:
            anchor = values[f"{domain}_anchor"]
            query = values[f"{domain}_query"]
            parts = (anchor, query) if query.shape[1] else (anchor,)
            tokens[domain] = torch.cat(
                [getattr(self, f"bias_{domain}")(self.pos_embed(part)) for part in parts],
                dim=1,
            )
            positions[domain] = torch.cat(parts, dim=1)
        return tokens, positions


class PhysicsStage(torch.nn.Module):
    def __init__(self, steps, rope, domains):
        super().__init__()
        self.blocks = torch.nn.ModuleList(steps)
        self.domains = tuple(domains)
        object.__setattr__(self, "rope", rope)

    def forward(self, tokens, positions, geometry, geometry_freq, sizes):
        values = dict(tokens)
        frequencies = {domain: self.rope(positions[domain]) for domain in self.domains}
        for step in self.blocks:
            values = step(
                values,
                frequencies,
                sizes,
                geometry=geometry,
                geometry_frequencies=geometry_freq,
            )
        return values


class DecoderStage(torch.nn.Module):
    def __init__(self, steps, rope, domain):
        super().__init__()
        self.blocks = torch.nn.ModuleList(steps)
        object.__setattr__(self, "rope", rope)
        object.__setattr__(self, "domain", domain)

    def forward(self, tokens, positions, size):
        frequencies = self.rope(positions)
        values = {self.domain: tokens}
        freq = {self.domain: frequencies}
        sizes = {self.domain: size}
        for step in self.blocks:
            values = step(values, freq, sizes)
        return values[self.domain]


class ReadoutStage(torch.nn.Module):
    def __init__(self, readout):
        super().__init__()
        self.head = readout

    def forward(self, tokens):
        return self.head(tokens)


class StageDisplay(torch.nn.Module):
    """按公开子模块暴露阶段盒；只用于看图，不替代正式预测。"""

    def __init__(self, network: torch.nn.Module):
        super().__init__()
        domains = tuple(network.decoders.keys())
        self.encoder = EncoderStage(network.encoder)
        self.geometry_blocks = GeometryStage(
            [DomainStep(block, "s") for block in network.geometry_blocks],
            network.rope,
        )
        self.embed = EmbedStage(network, domains)
        self.physics_blocks = PhysicsStage(
            [
                DomainStep(block, kind)
                for kind, block in zip(network.block_types, network.blocks, strict=True)
            ],
            network.rope,
            domains,
        )
        for domain in domains:
            self.add_module(
                f"decoder_{domain}",
                DecoderStage(
                    [DomainStep(block, "s") for block in network.decoders[domain]],
                    network.rope,
                    domain,
                ),
            )
            self.add_module(f"readout_{domain}", ReadoutStage(network.readouts[domain]))
        object.__setattr__(self, "domains", domains)

    def forward(self, values):
        payload = flatten_display_inputs(values)
        geometry = self.encoder(
            payload["geometry_position"],
            payload["geometry_supernode_idx"],
            payload["geometry_batch_idx"],
        )
        geometry, geometry_freq = self.geometry_blocks(
            geometry,
            payload["geometry_position"],
            payload["geometry_supernode_idx"],
            payload["geometry_batch_idx"],
        )
        tokens, positions = self.embed(payload)
        sizes = {domain: payload[f"{domain}_anchor"].shape[1] for domain in self.domains}
        tokens = self.physics_blocks(tokens, positions, geometry, geometry_freq, sizes)
        return {
            domain: getattr(self, f"readout_{domain}")(
                getattr(self, f"decoder_{domain}")(tokens[domain], positions[domain], sizes[domain])
            )
            for domain in self.domains
        }


def organize_for_display(network: torch.nn.Module, inputs):
    """能收成阶段盒时不再走正式 predict；否则由调用方做通用 forward 适配。"""
    if can_organize_stages(network) and isinstance(inputs, dict):
        return StageDisplay(network), flatten_display_inputs(inputs)
    return None
