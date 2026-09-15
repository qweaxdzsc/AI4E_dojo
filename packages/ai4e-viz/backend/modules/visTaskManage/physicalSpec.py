"""物理工作台配置版本转换与布局规则；历史文件始终保持原样。"""

import math
from copy import deepcopy


def balanced_layout(ids):
    """按 1 全幅、2 横排、3 上二下一、4 田字格生成单一布局。"""
    if len(ids) == 1:
        return {"view": ids[0]}
    if len(ids) == 2:
        return {
            "direction": "horizontal",
            "ratio": 0.5,
            "children": [{"view": ids[0]}, {"view": ids[1]}],
        }
    if len(ids) == 3:
        return {
            "direction": "vertical",
            "ratio": 0.5,
            "children": [balanced_layout(ids[:2]), {"view": ids[2]}],
        }
    return {
        "direction": "vertical",
        "ratio": 0.5,
        "children": [balanced_layout(ids[:2]), balanced_layout(ids[2:])],
    }


def layout_rectangles(layout, bounds=(0.0, 0.0, 1.0, 1.0)):
    """布局从上到下/从左到右分割，返回 VTK 左下坐标矩形。"""
    if "view" in layout:
        return {layout["view"]: bounds}
    direction, ratio = layout.get("direction"), layout.get("ratio", 0.5)
    if (
        direction not in ("horizontal", "vertical")
        or not isinstance(ratio, (int, float))
        or not math.isfinite(ratio)
        or not 0.1 <= ratio <= 0.9
    ):
        raise ValueError("invalid_layout_split")
    children = layout.get("children", [])
    if len(children) != 2:
        raise ValueError("layout_requires_two_children")
    x0, y0, x1, y1 = bounds
    if direction == "horizontal":
        mid = x0 + (x1 - x0) * ratio
        a, b = (x0, y0, mid, y1), (mid, y0, x1, y1)
    else:
        mid = y1 - (y1 - y0) * ratio
        a, b = (x0, mid, x1, y1), (x0, y0, x1, mid)
    left, right = layout_rectangles(children[0], a), layout_rectangles(children[1], b)
    if left.keys() & right.keys():
        raise ValueError("duplicate_layout_view")
    return {**left, **right}


def view_overlay_frames(layout, views, maximize=False, active=None):
    """把 VTK 左下矩形换成每个窗体左上角叠放标签用的 CSS 百分比。"""
    rectangles = layout_rectangles(layout)
    frames = []
    for view in views:
        identity = view["id"]
        if maximize and identity != active:
            continue
        x0, y0, x1, y1 = (
            (0.0, 0.0, 1.0, 1.0)
            if maximize and identity == active
            else rectangles[identity]
        )
        frames.append(
            {
                "id": identity,
                "name": view.get("name", f"RenderView{identity + 1}"),
                "css": (
                    f"left:{x0 * 100:.4f}%;top:{(1 - y1) * 100:.4f}%;"
                    f"width:{(x1 - x0) * 100:.4f}%;height:{(y1 - y0) * 100:.4f}%"
                ),
            }
        )
    return frames


def normalize_physical_spec(value):
    """把版本一显式转换为版本二；版本二不静默修复无效布局。"""
    spec = deepcopy(value)
    if spec.get("kind") != "phys_field":
        return spec
    version = spec.get("schema_version")
    if version not in (1, 2):
        raise ValueError("unsupported_visualization_schema")
    views = spec.setdefault("views", [{"id": 0}])
    if not 1 <= len(views) <= 4 or len({v["id"] for v in views}) != len(views):
        raise ValueError("invalid_view_count_or_identity")
    for v in views:
        v.setdefault("name", f"RenderView{v['id'] + 1}")
    if version == 1:
        spec["schema_version"] = 2
        spec["layout"] = balanced_layout([v["id"] for v in views])
        for layer in spec.get("layers", []):
            layer.setdefault("view", views[0]["id"])
        spec.setdefault("link_groups", [])
        spec.setdefault("time", {})
        pipeline = spec.setdefault("pipeline", [])
        for source in spec["sources"]:
            identity = "base-" + source["id"]
            if any(n["id"] == identity for n in pipeline):
                raise ValueError("base_identity_collision")
            pipeline.insert(
                0,
                {
                    "id": identity,
                    "name": "基础显示",
                    "input": source["id"],
                    "type": "surface",
                    "parameters": {},
                },
            )
            for layer in spec.get("layers", []):
                if layer["input"] == source["id"]:
                    layer["input"] = identity
        spec.setdefault("probes", [])
    ids = [v["id"] for v in views]
    if set(layout_rectangles(spec["layout"])) != set(ids):
        raise ValueError("layout_views_mismatch")
    available = {s["id"] for s in spec["sources"]}
    for node in spec.get("pipeline", []):
        if node["id"] in available or node["input"] not in available:
            raise ValueError("pipeline_input_missing_or_cycle")
        if node["type"] not in (
            "surface",
            "slice",
            "clip",
            "glyph",
            "streamline",
            "isosurface",
            "contour",
        ):
            raise ValueError("unsupported_filter")
        node.setdefault("name", node["id"])
        if node["type"] == "streamline":
            params = node.get("parameters") or {}
            kind = params.get("seed_type") or "line"
            if kind not in ("line", "sphere", "plane", "surface"):
                raise ValueError("invalid_seed_type")
            seed = params.get("seed_surface") or {}
            if kind == "surface" and seed.get("kind") == "object":
                identity = seed.get("id")
                if identity not in available or identity == node["id"]:
                    raise ValueError("invalid_seed_surface")
        available.add(node["id"])
    probe_ids = set()
    for probe in spec.get("probes", []):
        if probe["input"] not in available or probe["id"] in available | probe_ids:
            raise ValueError("invalid_probe_identity_or_input")
        xyz = probe.get("position", [])
        if len(xyz) != 3 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in xyz):
            raise ValueError("invalid_probe_position")
        probe_ids.add(probe["id"])
    layer_ids = set()
    pairs = set()
    for layer in spec.get("layers", []):
        pair = (layer["input"], layer["view"])
        if (
            layer["id"] in layer_ids
            or pair in pairs
            or layer["input"] not in available
            or layer["view"] not in ids
        ):
            raise ValueError("invalid_layer_identity_input_or_view")
        pairs.add(pair)
        layer_ids.add(layer["id"])
    spec.setdefault("implementation", {})["schema"] = 2
    return spec
