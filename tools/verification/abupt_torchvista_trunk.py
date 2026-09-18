"""用 TorchVista 渲染正式 AB-UPT 主干：默认只显示大盒，点开再展开子模块。"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import torch
from torchvista.enums import ExportFormat
from torchvista.graph_transforms import build_immediate_ancestor_map
from torchvista.render import plot_graph

from ai4e_core.applications.aero_cfd.inspection import _components, normalize_config

OUT = Path("/Users/zonghui/work/project_simulation/dojo_train/model-viewers/abupt-trunk.html")
CFG = Path("/tmp/abupt-task-config.json")

_TRUNK_EDGES = (
    ("encoder", "geometry_blocks"),
    ("geometry_blocks", "blocks"),
    ("blocks", "decoders"),
    ("decoders", "readouts"),
)


def _add_node(adj, module_info, display, attr, without, path, name, typ, params):
    adj[name] = {"edges": [], "failed": False, "node_type": "Module"}
    module_info[name] = {
        "type": typ,
        "parameters": {},
        "attributes": {"training": False, "parameters": params},
        "extra_repr": f"{params:,} params" if params else "",
    }
    display[name] = name.split(".")[-1]
    attr[name] = name.split(".")[-1]
    without[name] = typ
    path[name] = typ


def _walk(module, name, parent, adj, module_info, display, attr, without, path, ancestors, depth, max_depth):
    typ = type(module).__name__
    params = sum(item.numel() for item in module.parameters())
    _add_node(adj, module_info, display, attr, without, path, name, typ, params)
    if parent:
        ancestors[name].append(parent)
    if depth >= max_depth:
        return
    for child_name, child in module.named_children():
        child_id = f"{name}.{child_name}"
        _walk(
            child,
            child_id,
            name,
            adj,
            module_info,
            display,
            attr,
            without,
            path,
            ancestors,
            depth + 1,
            max_depth,
        )


def _module_tree(module, name, depth, max_depth):
    children = []
    if depth < max_depth:
        children = [
            _module_tree(child, f"{name}.{child_name}", depth + 1, max_depth)
            for child_name, child in module.named_children()
        ]
    return {
        "name": name,
        "short": name.split(".")[-1],
        "type": type(module).__name__,
        "params": sum(item.numel() for item in module.parameters()),
        "children": children,
    }


def _open_html(tree):
    payload = json.dumps(tree, ensure_ascii=False)
    return f"""<!doctype html>
<meta charset="utf-8" />
<title>正式 AB-UPT 主干</title>
<style>
  :root {{ color-scheme: light; font-family: "SF Pro Text", "PingFang SC", sans-serif; }}
  body {{ margin: 0; background: #f3f1ea; color: #1c2430; }}
  header {{ padding: 18px 22px 12px; background: #1c2430; color: #f3f1ea; }}
  h1 {{ margin: 0 0 6px; font-size: 20px; letter-spacing: .02em; }}
  p {{ margin: 0; font-size: 13px; opacity: .82; }}
  .flow {{ display: flex; gap: 10px; padding: 18px 22px; overflow-x: auto; align-items: stretch; }}
  .col {{ min-width: 168px; }}
  .box {{ background: #fff; border: 1px solid #c8c2b4; border-radius: 10px; padding: 10px 12px; cursor: pointer; box-shadow: 0 1px 0 #ddd6c8; }}
  .box:hover, .box.active {{ border-color: #1f6feb; box-shadow: 0 0 0 3px #1f6feb22; }}
  .box .k {{ font-size: 11px; color: #6b7280; }}
  .box .n {{ font-weight: 700; font-size: 15px; margin: 2px 0; }}
  .box .t {{ font-size: 12px; color: #374151; }}
  .box .p {{ font-variant-numeric: tabular-nums; color: #1f6feb; font-size: 12px; margin-top: 6px; }}
  #detail {{ margin: 0 22px 28px; background: #fff; border: 1px solid #c8c2b4; border-radius: 12px; padding: 14px 16px; min-height: 220px; }}
  details {{ margin: 3px 0 3px 16px; }}
  details.root {{ margin-left: 0; }}
  summary {{ cursor: pointer; display: flex; gap: 8px; align-items: baseline; padding: 4px 2px; }}
  .name {{ font-weight: 650; }}
  .type {{ color: #6b7280; font-size: 12px; }}
  .params {{ margin-left: auto; color: #1f6feb; font-variant-numeric: tabular-nums; font-size: 12px; }}
</style>
<header>
  <h1>正式 AB-UPT 主干</h1>
  <p>AnchoredBranchedUPT · 先看大阶段，再点开子模块。这是同一份官方网络的模块树，不再把几千个算子塞进 Graphviz。</p>
</header>
<div class="flow" id="flow"></div>
<div id="detail">点上面的主干盒，在这里展开子模块。</div>
<script>
const tree = {payload};
const fmt = (n) => n.toLocaleString("en-US");
const byShort = Object.fromEntries((tree.children || []).map((c) => [c.short, c]));
const stages = [
  {{ title: "输入", items: [
    {{ n: "geometry", t: "position / supernode / batch" }},
    {{ n: "anchors", t: "surface + volume" }},
    {{ n: "queries", t: "surface + volume" }},
  ]}},
  {{ title: "几何编码", key: "encoder" }},
  {{ title: "几何块", key: "geometry_blocks" }},
  {{ title: "物理块", key: "blocks", extra: "pscscscscsc" }},
  {{ title: "解码", key: "decoders" }},
  {{ title: "读出", key: "readouts" }},
];
function renderBox(stage) {{
  const node = stage.key ? byShort[stage.key] : null;
  const count = node ? node.children.length : stage.items.length;
  const params = node ? fmt(node.params) : "";
  const type = node ? node.type : "inputs";
  return `<button class="box" data-key="${{stage.key || ""}}">
    <div class="k">${{stage.title}}</div>
    <div class="n">${{node ? node.short : "inputs"}}</div>
    <div class="t">${{stage.extra || type}} · ${{count}} 项</div>
    <div class="p">${{params}}</div>
  </button>`;
}}
document.getElementById("flow").innerHTML = stages.map((s) => `<div class="col">${{renderBox(s)}}</div>`).join("");
function detailsOf(node, isRoot) {{
  const kids = node.children || [];
  return `<details class="${{isRoot ? "root" : ""}}" ${{isRoot ? "open" : ""}}>
    <summary><span class="name">${{node.short}}</span><span class="type">${{node.type}}</span><span class="params">${{fmt(node.params)}}</span></summary>
    ${{kids.map((c) => detailsOf(c, false)).join("")}}
  </details>`;
}}
function show(key) {{
  document.querySelectorAll(".box").forEach((el) => el.classList.toggle("active", el.dataset.key === key));
  const node = key ? byShort[key] : tree;
  document.getElementById("detail").innerHTML = detailsOf(node || tree, true);
}}
document.getElementById("flow").addEventListener("click", (e) => {{
  const box = e.target.closest(".box");
  if (box) show(box.dataset.key);
}});
show("encoder");
</script>
"""


def _edge(adj, source, target, dims, edge_id):
    adj[source]["edges"].append({"target": target, "dims": dims, "edge_data_id": edge_id})


def main():
    cfg = normalize_config(json.loads(CFG.read_text())["config"])
    _, model = _components(cfg)
    network = model.construct(**model.training_parameters(cfg)).cpu().eval()

    adj = {}
    module_info = {}
    func_info = {}
    display = {}
    attr = {}
    without = {}
    path = {}
    ancestors = defaultdict(list)
    parent_module_to_nodes = defaultdict(list)
    parent_module_to_depth = {}

    root = "ABUPT"
    _walk(network, root, None, adj, module_info, display, attr, without, path, ancestors, 0, 3)
    display[root] = "ABUPT"
    attr[root] = "ABUPT"

    inputs = [
        ("input_geometry_position", "geometry_position", "(48, 3)"),
        ("input_geometry_supernode_idx", "geometry_supernode_idx", "(12)"),
        ("input_geometry_batch_idx", "geometry_batch_idx", "(48)"),
        ("input_surface_anchor", "domain_anchor_positions.surface", "(1, 16, 3)"),
        ("input_volume_anchor", "domain_anchor_positions.volume", "(1, 16, 3)"),
        ("input_surface_query", "domain_query_positions.surface", "(1, 8, 3)"),
        ("input_volume_query", "domain_query_positions.volume", "(1, 8, 3)"),
    ]
    outputs = [
        ("output_surface_pressure", "surface_pressure"),
        ("output_query_surface_pressure", "query_surface_pressure"),
        ("output_volume_velocity", "volume_velocity"),
        ("output_query_volume_velocity", "query_volume_velocity"),
    ]
    edge_id = 1
    for key, label, dims in inputs:
        adj[key] = {"edges": [], "failed": False, "node_type": "Input"}
        display[key] = label
        _edge(adj, key, root, dims, edge_id)
        edge_id += 1
    for key, label in outputs:
        adj[key] = {"edges": [], "failed": False, "node_type": "Output"}
        display[key] = label
        _edge(adj, root, key, "", edge_id)
        edge_id += 1
    for source, target in _TRUNK_EDGES:
        src = f"{root}.{source}"
        dst = f"{root}.{target}"
        if src in adj and dst in adj:
            _edge(adj, src, dst, "", edge_id)
            edge_id += 1

    for child, parents in ancestors.items():
        parent_module_to_nodes[parents[0]].append(child)
        parent_module_to_depth[child] = child.count(".")

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
        1400,
        ExportFormat.HTML,
        True,
        set(),
        show_modular_view=False,
        export_path=str(OUT),
    )
    tree = _module_tree(network, "ABUPT", 0, 4)
    open_page = OUT.with_name("abupt-trunk-open.html")
    open_page.write_text(_open_html(tree), encoding="utf-8")
    print("HTML", OUT, "bytes", OUT.stat().st_size, "nodes", len(adj))
    print("OPEN", open_page, "bytes", open_page.stat().st_size)


if __name__ == "__main__":
    main()
