"""用 TorchVista 官方折叠导出正式 AB-UPT：默认最粗模块盒，点 + 展开。"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path

import torch
from torchvista.engine import process_graph
from torchvista.enums import ExportFormat
from torchvista.graph_transforms import build_immediate_ancestor_map
from torchvista.render import plot_graph

from ai4e_core.abilities.modeling.inspection import fit_graph_viewport
from ai4e_core.applications.aero_cfd.inspection import _components, normalize_config

OUT = Path("/Users/zonghui/work/project_simulation/dojo_train/model-viewers/abupt-torchvista-skeleton.html")
CFG = Path("/tmp/abupt-task-config.json")


class DomainStep(torch.nn.Module):
    """官方 DomainBlock 走的是 forward_domains，这里补 .forward 才能被 TorchVista 收成模块盒。"""

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
        return values["geometry"]


class EmbedStage(torch.nn.Module):
    def __init__(self, network):
        super().__init__()
        self.pos_embed = network.pos_embed
        self.bias_surface = network.biases["surface"]
        self.bias_volume = network.biases["volume"]

    def forward(self, surface_anchor, volume_anchor, surface_query, volume_query):
        surface = torch.cat(
            [self.bias_surface(self.pos_embed(part)) for part in (surface_anchor, surface_query)],
            dim=1,
        )
        volume = torch.cat(
            [self.bias_volume(self.pos_embed(part)) for part in (volume_anchor, volume_query)],
            dim=1,
        )
        return surface, volume


class PhysicsStage(torch.nn.Module):
    def __init__(self, steps, rope):
        super().__init__()
        self.blocks = torch.nn.ModuleList(steps)
        object.__setattr__(self, "rope", rope)

    def forward(self, surface, volume, geometry):
        values = {"surface": surface, "volume": volume}
        dummy = {
            "surface": torch.rand(surface.shape[0], surface.shape[1], 3),
            "volume": torch.rand(volume.shape[0], volume.shape[1], 3),
        }
        frequencies = {domain: self.rope(dummy[domain]) for domain in dummy}
        sizes = {"surface": surface.shape[1] // 2, "volume": volume.shape[1] // 2}
        geometry_rope = self.rope(dummy["surface"][:, : geometry.shape[1]])
        for step in self.blocks:
            values = step(
                values,
                frequencies,
                sizes,
                geometry=geometry,
                geometry_frequencies=geometry_rope,
            )
        return values["surface"], values["volume"]


class DecoderStage(torch.nn.Module):
    def __init__(self, steps, rope, domain):
        super().__init__()
        self.blocks = torch.nn.ModuleList(steps)
        object.__setattr__(self, "rope", rope)
        object.__setattr__(self, "domain", domain)

    def forward(self, tokens):
        frequencies = self.rope(torch.rand(tokens.shape[0], tokens.shape[1], 3))
        values = {self.domain: tokens}
        freq = {self.domain: frequencies}
        sizes = {self.domain: tokens.shape[1] // 2}
        for step in self.blocks:
            values = step(values, freq, sizes)
        return values[self.domain]


class ABUPTFlow(torch.nn.Module):
    def __init__(self, network):
        super().__init__()
        self.encoder = network.encoder
        self.geometry_blocks = GeometryStage(
            [DomainStep(block, "s") for block in network.geometry_blocks],
            network.rope,
        )
        self.embed = EmbedStage(network)
        self.blocks = PhysicsStage(
            [DomainStep(block, kind) for kind, block in zip(network.block_types, network.blocks, strict=True)],
            network.rope,
        )
        self.decoders_surface = DecoderStage(
            [DomainStep(block, "s") for block in network.decoders["surface"]],
            network.rope,
            "surface",
        )
        self.decoders_volume = DecoderStage(
            [DomainStep(block, "s") for block in network.decoders["volume"]],
            network.rope,
            "volume",
        )
        self.readouts_surface = network.readouts["surface"]
        self.readouts_volume = network.readouts["volume"]

    def forward(
        self,
        geometry_position,
        geometry_supernode_idx,
        geometry_batch_idx,
        surface_anchor,
        volume_anchor,
        surface_query,
        volume_query,
    ):
        geometry = self.encoder(geometry_position, geometry_supernode_idx, geometry_batch_idx)
        geometry = self.geometry_blocks(geometry, geometry_position, geometry_supernode_idx, geometry_batch_idx)
        surface, volume = self.embed(surface_anchor, volume_anchor, surface_query, volume_query)
        surface, volume = self.blocks(surface, volume, geometry)
        return (
            self.readouts_surface(self.decoders_surface(surface)),
            self.readouts_volume(self.decoders_volume(volume)),
        )


def main():
    cfg = normalize_config(json.loads(CFG.read_text())["config"])
    _, model = _components(cfg)
    network = model.construct(**model.training_parameters(cfg)).cpu().eval()
    viewed = ABUPTFlow(network).eval()
    inputs = (
        torch.rand(48, 3),
        torch.arange(12, dtype=torch.long),
        torch.zeros(48, dtype=torch.long),
        torch.rand(1, 16, 3),
        torch.rand(1, 16, 3),
        torch.rand(1, 8, 3),
        torch.rand(1, 8, 3),
    )
    adj, module_info, func_info = {}, {}, {}
    parent_module_to_nodes = defaultdict(list)
    parent_module_to_depth = {}
    without, display, path = {}, {}, {}
    ancestors = defaultdict(list)
    repeats, attr = set(), {}
    with redirect_stdout(sys.stderr):
        process_graph(
            viewed,
            inputs,
            adj,
            module_info,
            func_info,
            path,
            parent_module_to_nodes,
            parent_module_to_depth,
            without,
            display,
            ancestors,
            repeats,
            attr,
            show_non_gradient_nodes=False,
            forced_module_tracing_depth=None,
            show_module_attr_names=True,
            show_compressed_view=True,
        )
    rename = {
        "input_0": "geometry_position",
        "input_1": "geometry_supernode_idx",
        "input_2": "geometry_batch_idx",
        "input_3": "surface_anchor",
        "input_4": "volume_anchor",
        "input_5": "surface_query",
        "input_6": "volume_query",
        "output_0": "surface_pressure",
        "output_1": "volume_velocity",
    }
    for key, label in rename.items():
        display[key] = label
    ancestor_map = build_immediate_ancestor_map(ancestors, adj)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plot_graph(
        adj,
        module_info,
        func_info,
        path,
        parent_module_to_nodes,
        parent_module_to_depth,
        without,
        display,
        attr,
        ancestor_map,
        0,
        920,
        1600,
        ExportFormat.HTML,
        True,
        repeats,
        show_modular_view=True,
        export_path=str(OUT),
    )
    html = OUT.read_text(encoding="utf-8")
    try:
        html = fit_graph_viewport(html)
    except RuntimeError:
        pass
    if "<meta charset" not in html:
        html = (
            '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            "<title>正式 AB-UPT · TorchVista 官方折叠</title></head><body>\n"
            '<p style="margin:10px 16px;font:13px/1.5 sans-serif;color:#5b6d8d;">'
            "TorchVista 官方折叠：collapse_modules_after_depth=0，先显示最粗模块盒，点盒子上的 + 展开。"
            "</p>\n"
            + html
            + "\n</body></html>"
        )
    OUT.write_text(html, encoding="utf-8")
    print("HTML", OUT, "nodes", len(adj), "containers", len(set(ancestor_map.values()) - {None}), "repeats", len(repeats))


if __name__ == "__main__":
    main()
