"""物理对象与视图命令；所有提交都经过同一场景事务。"""

from copy import deepcopy
from uuid import uuid4

from modules.visTaskManage import balanced_layout, normalize_physical_spec


def seed_surface_id(node):
    """流线引用的对象树种子面，文件命名块不进入删除依赖。"""
    seed = (node.get("parameters") or {}).get("seed_surface") or {}
    if seed.get("kind") == "object":
        return seed.get("id")
    return None


def descendants(spec, identity):
    """返回待删除对象及所有依赖对象，包含依赖它的 Probe 和流线种子面。"""
    found = {identity}
    changed = True
    while changed:
        changed = False
        for node in spec.get("pipeline", []) + spec.get("probes", []):
            depends = node.get("input") in found or seed_surface_id(node) in found
            if depends and node["id"] not in found:
                found.add(node["id"])
                changed = True
    return found


def split_leaf(tree, view, replacement):
    """替换指定叶子并保留其他视图的稳定身份。"""
    if tree.get("view") == view:
        return replacement
    if "children" in tree:
        return {**tree, "children": [split_leaf(c, view, replacement) for c in tree["children"]]}
    return tree


def remove_leaf(tree, view):
    """关闭视图时折叠其父分割，不删除任何计算对象。"""
    if tree.get("view") == view:
        return None
    if "children" not in tree:
        return tree
    children = [c for child in tree["children"] if (c := remove_leaf(child, view)) is not None]
    return children[0] if len(children) == 1 else {**tree, "children": children}


def execute(scene, command):
    """处理对象、布局及显示命令，未知命令返回 None 交由查询入口处理。"""
    op = command["operation"]
    if op == "plane_drag":
        from modules.visEngine import move_plane

        origin, normal = move_plane(
            command["origin"],
            command["normal"],
            command["handle"],
            command["start"],
            command["end"],
        )
        mesh = scene.datasets.get(command.get("input"))
        bounds = command.get("bounds") or (
            list(mesh.GetBounds()) if mesh is not None else [-1, 1, -1, 1, -1, 1]
        )
        scene.show_plane_widget(origin, normal, bounds, command.get("view"))
        return {"origin": origin, "normal": normal}
    if op == "plot_over_line":
        from modules.visEngine import sample_line

        mesh = scene.datasets.get(command["input"])
        if mesh is None:
            raise ValueError("plot_over_line_input_missing")
        rows = sample_line(
            mesh,
            command["point1"],
            command["point2"],
            int(command.get("resolution", 1000)),
            command.get("fields"),
        )
        scene.last_extraction = {"kind": "plot_over_line", "rows": rows}
        return {"rows": rows}
    if op == "probe_visibility":
        return scene.set_probe_visibility(
            command["id"], command["view"], command.get("visible"), command.get("label")
        )
    if op not in {
        "object_create",
        "object_update",
        "object_rename",
        "object_copy",
        "object_delete",
        "delete_preview",
        "display",
        "view_create",
        "view_close",
        "view_layout",
        "view_update",
        "link_views",
        "probe_create",
        "probe_update",
        "source_remove",
    }:
        return None
    if op == "display" and not any(
        key in command for key in ("field", "color", "style", "helpers")
    ):
        view = command["view"]
        identity = command["id"]
        layer = next(
            (
                item
                for item in scene.spec.get("layers", [])
                if item["input"] == identity and item["view"] == view
            ),
            None,
        )
        if layer is not None and layer["id"] in scene.actors:
            return scene.set_layer_visibility(layer["id"], command.get("visible", True))
    # 显示更新不需要重算画像或来源摘要；公开响应仍由场景返回完整快照。
    spec = deepcopy(scene.spec) if op == "display" else scene.snapshot()["spec"]
    objects = spec["pipeline"] + spec.get("probes", [])
    identity = command.get("id")
    node = next((n for n in objects if n["id"] == identity), None)
    if op == "delete_preview":
        affected = descendants(spec, identity)
        return {"affected": [n for n in objects if n["id"] in affected]}
    if op in ("object_create", "probe_create"):
        identity = command.get("id") or uuid4().hex
        node = {"id": identity, "name": command.get("name", identity), "input": command["input"]}
        if op == "probe_create":
            node.update(
                position=command["position"],
                fields=command.get("fields", []),
                views=deepcopy(
                    command.get(
                        "views",
                        {str(command.get("view", spec["views"][0]["id"])): {"visible": True}},
                    )
                ),
            )
            spec["probes"].append(node)
        else:
            node.update(type=command["type"], parameters=deepcopy(command.get("parameters", {})))
            if command.get("chart"):
                node["chart"] = deepcopy(command["chart"])
            spec["pipeline"].append(node)
            spec["layers"].append(
                {
                    "id": uuid4().hex,
                    "input": identity,
                    "view": command.get("view", spec["views"][0]["id"]),
                    "visible": True,
                    **deepcopy(command.get("display", {})),
                }
            )
    elif op in ("object_update", "probe_update", "object_rename", "object_copy"):
        if node is None:
            raise ValueError("object_missing")
        if op == "object_rename":
            if not str(command["name"]).strip():
                raise ValueError("object_name_required")
            node["name"] = str(command["name"]).strip()
        elif op == "object_update":
            node["parameters"] = deepcopy(command["parameters"])
            if "chart" in command:
                node["chart"] = deepcopy(command["chart"])
            if "display" in command:
                for layer in spec["layers"]:
                    if layer["input"] == identity and layer["view"] == command["view"]:
                        layer.update(deepcopy(command["display"]))
        elif op == "probe_update":
            for key in ("position", "fields", "views"):
                if key in command:
                    node[key] = deepcopy(command[key])
        else:
            copy = deepcopy(node)
            copy["id"] = uuid4().hex
            copy["name"] += " 副本"
            (spec["pipeline"] if "type" in node else spec["probes"]).append(copy)
            for layer in list(spec["layers"]):
                if layer["input"] == identity:
                    spec["layers"].append(
                        {**deepcopy(layer), "id": uuid4().hex, "input": copy["id"]}
                    )
    elif op in ("object_delete", "source_remove"):
        affected = descendants(spec, identity)
        if len(affected) > 1 and not command.get("cascade"):
            raise ValueError("dependent_objects_require_confirmation")
        spec["pipeline"] = [n for n in spec["pipeline"] if n["id"] not in affected]
        spec["probes"] = [n for n in spec["probes"] if n["id"] not in affected]
        spec["layers"] = [n for n in spec["layers"] if n["input"] not in affected]
        if op == "source_remove":
            spec["sources"] = [s for s in spec["sources"] if s["id"] != identity]
        return scene.remove_objects(spec, affected)
    elif op == "display":
        view = command["view"]
        view_record = next((item for item in spec["views"] if item["id"] == view), {})
        node = next((item for item in spec["pipeline"] if item["id"] == identity), None)
        if view_record.get("type") == "line_chart" and (node or {}).get("type") != "plot_over_line":
            raise ValueError("line_chart_only_plot_over_line")
        layer = next(
            (l for l in spec["layers"] if l["input"] == identity and l["view"] == view), None
        )
        if layer is None:
            layer = {"id": uuid4().hex, "input": identity, "view": view, "visible": True}
            spec["layers"].append(layer)
        for key in ("field", "color", "style", "visible", "helpers"):
            if key in command:
                layer[key] = deepcopy(command[key])
        return scene.update_display(spec, layer["id"])
    elif op == "view_create":
        if len(spec["views"]) >= 4:
            raise ValueError("maximum_four_views")
        current = command["view"]
        new_id = max(v["id"] for v in spec["views"]) + 1
        view_type = command.get("view_type") or "render"
        if view_type not in ("render", "line_chart"):
            raise ValueError("invalid_view_type")
        current_view = next(v for v in spec["views"] if v["id"] == current)
        if view_type == "line_chart":
            view = {
                "id": new_id,
                "name": f"LineChartView{new_id + 1}",
                "type": "line_chart",
                "background": deepcopy(current_view.get("background", [1, 1, 1])),
                "chart": {
                    "source": command.get("source") or "",
                    "x_array": command.get("x_array") or "arc_length",
                    "y_arrays": list(command.get("y_arrays") or []),
                },
            }
        else:
            render_src = next(
                (item for item in spec["views"] if item.get("type", "render") == "render"),
                current_view,
            )
            view = deepcopy(render_src)
            view.update(id=new_id, name=f"RenderView{new_id + 1}", type="render")
            view.pop("chart", None)
            source_view = render_src["id"]
            for layer in list(spec["layers"]):
                if layer["view"] == source_view:
                    spec["layers"].append({**deepcopy(layer), "id": uuid4().hex, "view": new_id})
        spec["views"].append(view)
        for probe in spec["probes"]:
            probe.setdefault("views", {})[str(new_id)] = deepcopy(
                probe.get("views", {}).get(str(current), {"visible": True})
            )
        spec["layout"] = balanced_layout([v["id"] for v in spec["views"]])
        if spec.get("link_groups"):
            spec["link_groups"] = [{"views": [v["id"] for v in spec["views"]]}]
    elif op == "view_close":
        if len(spec["views"]) == 1:
            raise ValueError("last_view_cannot_close")
        view = command["view"]
        if view not in [v["id"] for v in spec["views"]]:
            raise ValueError("view_missing")
        spec["views"] = [v for v in spec["views"] if v["id"] != view]
        spec["layers"] = [l for l in spec["layers"] if l["view"] != view]
        spec["layout"] = balanced_layout([v["id"] for v in spec["views"]])
        if spec.get("link_groups"):
            remaining = [v["id"] for v in spec["views"]]
            spec["link_groups"] = [{"views": remaining}] if len(remaining) > 1 else []
        for probe in spec["probes"]:
            probe.get("views", {}).pop(str(view), None)
    elif op == "view_layout":
        spec["layout"] = deepcopy(command["layout"])
    elif op == "view_update":
        view = next(v for v in spec["views"] if v["id"] == command["view"])
        view.update(
            {
                k: v
                for k, v in command["settings"].items()
                if k in ("name", "axes", "shadows", "background", "type", "chart")
            }
        )
        if set(command["settings"]) == {"background"}:
            spec = normalize_physical_spec(spec)
            index = next(i for i, v in enumerate(spec["views"]) if v["id"] == command["view"])
            scene.renderers[index].SetBackground(view["background"])
            scene.spec = spec
            return scene.snapshot()
    elif op == "link_views":
        spec["link_groups"] = [{"views": command["views"]}] if command.get("views") else []
    return scene.apply(spec)
