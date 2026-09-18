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
            (0.0, 0.0, 1.0, 1.0) if maximize and identity == active else rectangles[identity]
        )
        view_type = view.get("type", "render")
        frames.append(
            {
                "id": identity,
                "name": view.get("name", f"RenderView{identity + 1}"),
                "view_type": view_type if view_type in ("render", "line_chart") else "render",
                "css": (
                    f"left:{x0 * 100:.4f}%;top:{(1 - y1) * 100:.4f}%;"
                    f"width:{(x1 - x0) * 100:.4f}%;height:{(y1 - y0) * 100:.4f}%"
                ),
            }
        )
    return frames


def probe_pick_enabled(probe):
    """点选拾取是会话开关；历史修订缺键视为关，不回写 spec。"""
    if not isinstance(probe, dict):
        return False
    return probe.get("pick_enabled") is True


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
        background = v.get("background", [0.14, 0.21, 0.29])
        if (
            not isinstance(background, (list, tuple))
            or len(background) != 3
            or not all(
                isinstance(x, (int, float))
                and not isinstance(x, bool)
                and math.isfinite(x)
                and 0 <= x <= 1
                for x in background
            )
        ):
            raise ValueError("invalid_view_background")
        # 旧修订缺 type 按三维渲染读取，不回写历史文件。
        view_type = v.get("type", "render")
        if view_type not in ("render", "line_chart"):
            raise ValueError("invalid_view_type")
        v.setdefault("name", f"RenderView{v['id'] + 1}")
        chart = v.get("chart")
        if chart is not None:
            if not isinstance(chart, dict):
                raise ValueError("invalid_chart_view")
            x_array = chart.get("x_array", "arc_length")
            y_arrays = chart.get("y_arrays", [])
            if not isinstance(x_array, str) or not x_array:
                raise ValueError("invalid_chart_x_array")
            if not isinstance(y_arrays, list) or any(not isinstance(item, str) for item in y_arrays):
                raise ValueError("invalid_chart_y_arrays")
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
            "plot_over_line",
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
        if node["type"] in ("slice", "clip"):
            params = node.get("parameters") or {}
            if "crinkle" in params and not isinstance(params["crinkle"], bool):
                raise ValueError("invalid_crinkle")
            if node["type"] == "slice" and "triangulate" in params and not isinstance(
                params["triangulate"], bool
            ):
                raise ValueError("invalid_triangulate")
        if node["type"] == "plot_over_line":
            params = node.get("parameters") or {}
            for key in ("point1", "point2"):
                point = params.get(key, [0, 0, 0] if key == "point1" else [1, 0, 0])
                if (
                    not isinstance(point, (list, tuple))
                    or len(point) != 3
                    or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in point)
                ):
                    raise ValueError("invalid_line_points")
            count = params.get("resolution", 1000)
            if isinstance(count, bool) or not isinstance(count, int) or not 2 <= count <= 20000:
                raise ValueError("invalid_line_resolution")
        params = node.get("parameters") or {}
        if "levels" in params:
            levels = params["levels"]
            if (
                node["type"] != "contour"
                or "values" in params
                or not isinstance(levels, dict)
                or levels.get("mode") != "automatic"
            ):
                raise ValueError("invalid_contour_levels")
            count = levels.get("count", 10)
            if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 256:
                raise ValueError("invalid_contour_count")
            limits = levels.get("range")
            if limits is not None and (
                not isinstance(limits, list)
                or len(limits) != 2
                or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in limits)
                or limits[0] >= limits[1]
            ):
                raise ValueError("invalid_contour_range")
        if node["type"] == "glyph":
            p = node.get("parameters", {})
            if p.get("scale_mode", "vector") not in ("constant", "vector", "scalar"):
                raise ValueError("invalid_glyph_scale_mode")
            if not isinstance(p.get("shape", {}), dict) or p.get("shape", {}).get(
                "type", "arrow"
            ) not in ("arrow", "cone", "line"):
                raise ValueError("invalid_glyph_shape")
            for key, default in [("scale", 0.1), ("stride", 1)]:
                value = p.get(key, default)
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value <= 0
                    or (key == "stride" and value != int(value))
                ):
                    raise ValueError("invalid_glyph_" + key)
            if p.get("shape", {}).get("type", "arrow") == "arrow":
                for key, default in [
                    ("tip_length", 0.35),
                    ("tip_radius", 0.1),
                    ("shaft_radius", 0.03),
                ]:
                    value = p.get("shape", {}).get(key, default)
                    if (
                        isinstance(value, bool)
                        or not isinstance(value, (int, float))
                        or not math.isfinite(value)
                        or not 0 < value <= 1
                    ):
                        raise ValueError("invalid_glyph_shape_size")
            if p.get("scale_mode") == "scalar" and not (p.get("scale_field") or {}).get("name"):
                raise ValueError("glyph_scale_field_required")
            sampling = p.get("sampling", {})
            if not isinstance(sampling, dict) or sampling.get("mode", "nodes") not in (
                "nodes",
                "spatial",
            ):
                raise ValueError("invalid_glyph_sampling")
            if sampling.get("mode") == "spatial":
                spacing = sampling.get("spacing")
                if (
                    not isinstance(spacing, (int, float))
                    or not math.isfinite(spacing)
                    or spacing <= 0
                ):
                    raise ValueError("invalid_glyph_spacing")
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
        color = layer.get("color", {})
        limits = color.get("range")
        if limits is not None and (
            not isinstance(limits, (list, tuple))
            or len(limits) != 2
            or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in limits)
            or limits[0] > limits[1]
        ):
            raise ValueError("invalid_color_range")
        legend = color.get("legend_style", {})
        if (
            not isinstance(legend, dict)
            or legend.get("position", "right") not in ("left", "right", "top", "bottom", "custom")
            or legend.get("orientation", "vertical") not in ("vertical", "horizontal")
        ):
            raise ValueError("invalid_legend_style")
        for key, default, lo, hi in [
            ("length", 0.6, 0.05, 0.9),
            ("thickness", 25, 2, 100),
            ("title_font_size", 25, 6, 72),
            ("label_font_size", 25, 6, 72),
            ("x", 0.8, 0, 0.95),
            ("y", 0.2, 0, 0.95),
        ]:
            value = legend.get(key, default)
            if (
                not isinstance(value, (float, int))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or not lo <= value <= hi
            ):
                raise ValueError("invalid_legend_" + key)
        style = layer.get("style", {})
        if not isinstance(style, dict):
            raise ValueError("invalid_display_style")
        solid = style.get("color")
        if solid is not None and (
            not isinstance(solid, (list, tuple))
            or len(solid) != 3
            or not all(isinstance(x, (int, float)) and math.isfinite(x) and 0 <= x <= 1 for x in solid)
        ):
            raise ValueError("invalid_solid_color")
        width = style.get("line_width", 1)
        if (
            isinstance(width, bool)
            or not isinstance(width, (int, float))
            or not math.isfinite(width)
            or not 0 < width <= 20
        ):
            raise ValueError("invalid_line_width")
        stream = style.get("streamline")
        if stream is not None:
            if not isinstance(stream, dict):
                raise ValueError("invalid_streamline_style")
            shape = stream.get("shape", "line")
            if shape not in ("line", "tube"):
                raise ValueError("invalid_streamline_shape")
            if "thickness" in stream:
                thickness = stream["thickness"]
                if (
                    isinstance(thickness, bool)
                    or not isinstance(thickness, (int, float))
                    or not math.isfinite(thickness)
                    or thickness <= 0
                    or (shape == "line" and thickness > 20)
                    or (shape == "tube" and thickness > 1e6)
                ):
                    raise ValueError("invalid_streamline_thickness")
            if "sides" in stream:
                sides = stream["sides"]
                if isinstance(sides, bool) or not isinstance(sides, int) or not 3 <= sides <= 64:
                    raise ValueError("invalid_streamline_sides")
        helpers = layer.get("helpers", {})
        if not isinstance(helpers, dict) or (
            "plane_visible" in helpers and not isinstance(helpers["plane_visible"], bool)
        ):
            raise ValueError("invalid_plane_visibility")
        if "seeds_visible" in helpers and not isinstance(helpers["seeds_visible"], bool):
            raise ValueError("invalid_seed_visibility")
        mode = style.get("mode", "surface")
        if mode not in ("surface", "wireframe", "surface_edges", "surface_lic"):
            raise ValueError("invalid_display_mode")
        lic = style.get("lic")
        if lic is not None:
            if not isinstance(lic, dict):
                raise ValueError("invalid_lic")
            vectors = lic.get("vectors")
            if vectors is not None and (
                not isinstance(vectors, dict)
                or not str(vectors.get("name") or "").strip()
                or vectors.get("association", "point") != "point"
            ):
                raise ValueError("invalid_lic_vectors")
        pairs.add(pair)
        layer_ids.add(layer["id"])
    spec.setdefault("implementation", {})["schema"] = 2
    return spec
