"""工作台选中对象与未应用草稿；UI 不拥有 VTK 处理算法。"""

import asyncio
from copy import deepcopy
from uuid import uuid4

LABELS = {
    "surface": "基础显示",
    "glyph": "矢量图",
    "slice": "切面",
    "clip": "剖切",
    "streamline": "流线",
    "isosurface": "等值面",
    "contour": "等高线",
    "probe": "Probe",
}
PARAM_KEYS = [
    "plane_origin",
    "plane_normal",
    "inside_out",
    "compute_field",
    "compute_component",
    "iso_values",
    "vector_scale",
    "vector_stride",
    "seed_start",
    "seed_end",
    "seed_count",
    "seed_type",
    "seed_center",
    "seed_radius",
    "seed_origin",
    "seed_normal",
    "seed_width",
    "seed_height",
    "seed_surface",
    "flow_length",
    "flow_direction",
    "probe_position",
    "probe_fields",
]


class Workbench:
    """每个会话独立选择、草稿、播放任务与活动视图。"""

    def __init__(self, server, scene):
        """初始化 UI 状态，计算仅通过场景命令入口执行。"""
        self.server, self.scene = server, scene
        self.drafts = {}
        self.playing = 0
        self.view = None
        self.pending_action = None
        self._plane_drag_start = None
        state = server.state
        state.update(
            {
                "selected": scene.spec["pipeline"][0]["id"] if scene.spec["pipeline"] else "",
                "active_view": scene.spec["views"][0]["id"],
                "error": "",
                "busy": False,
                "search": "",
                "tree_nodes": [],
                "tree_open": [],
                "draft_dialog": False,
                "delete_dialog": False,
                "delete_names": "",
                "rename_dialog": False,
                "object_name": "",
                "pending": False,
                "interaction_mode": "rotate",
                "maximize": False,
                "query_rows": "",
                "query_curve": "",
                "time_index": 0,
                "playing": False,
                "dirty_names": "",
                "ratio": 0.5,
                "view_frames": [],
                "seed_type": "line",
                "seed_surface": "",
                "seed_surface_items": [],
                "plane_dragging": "",
                "plane_widget": {"visible": False},
                "mode_items": [
                    {"text": "选择", "value": "select"},
                    {"text": "旋转", "value": "rotate"},
                    {"text": "平移", "value": "pan"},
                    {"text": "缩放", "value": "zoom"},
                ],
            }
        )
        self._plane_drag_start = None
        self.hydrate()

    def object(self, identity=None):
        """选择来源或计算对象，草稿对象仍然只存在于本次工作区。"""
        identity = identity or self.server.state.selected
        return self.drafts.get(identity, {}).get("node") or next(
            (
                n
                for n in self.scene.spec["pipeline"] + self.scene.spec["probes"]
                if n["id"] == identity
            ),
            None,
        )

    def stash(self):
        """切换对象时保留各自参数草稿，不污染已保存的声明。"""
        state = self.server.state
        if not state.selected or not hasattr(self, "baseline"):
            return
        values = {k: state[k] for k in PARAM_KEYS}
        if values != self.baseline:
            draft = self.drafts.setdefault(
                state.selected, {"node": deepcopy(self.object()), "new": False}
            )
            draft["form"] = deepcopy(values)

    def select(self, identity):
        """树和场景拾取共用选择入口。"""
        self.stash()
        self.server.state.selected = identity
        self.hydrate()
        self.refresh()

    def hydrate(self):
        """仅回填当前对象的属性；显示字段和计算字段分别回填。"""
        state = self.server.state
        node = self.object()
        kind = node.get("type", "probe") if node else ""
        p = (node or {}).get("parameters", {})
        layer = next(
            (
                l
                for l in self.scene.spec["layers"]
                if l["input"] == state.selected and l["view"] == state.active_view
            ),
            {},
        )
        field = layer.get("field") or {}
        color = layer.get("color") or {}
        style = layer.get("style") or {}

        def field_key(f):
            """字段选择键同时包含归属和名称。"""
            return f.get("association", "point") + "|" + f["name"] if f.get("name") else ""

        with state:
            state.kind = kind
            state.object_name = (node or {}).get("name", state.selected)
            state.coloring = field_key(field)
            state.component = field.get("component", "magnitude")
            state.palette = {
                "turbo": "Turbo",
                "coolwarm": "Cool to Warm",
                "rainbow": "Rainbow",
                "jet": "Jet",
            }.get(color.get("preset"), color.get("preset", "Turbo"))
            state.bands = color.get("bands", 32)
            limits = color.get("range") or ["", ""]
            state.range_min, state.range_max = limits
            state.opacity = style.get("opacity", 1)
            state.display_mode = style.get("mode", "surface")
            state.lighting = style.get("lighting", True)
            state.legend = color.get("legend", True)
            state.plane_origin = ",".join(map(str, p.get("origin", [0, 0, 0])))
            state.plane_normal = ",".join(map(str, p.get("normal", [1, 0, 0])))
            state.inside_out = p.get("inside_out", False)
            state.compute_field = field_key(p.get("field", {}))
            state.compute_component = p.get("field", {}).get("component", "magnitude")
            state.iso_values = ",".join(map(str, p.get("values", [0])))
            state.vector_scale = p.get("scale", 0.1)
            state.vector_stride = p.get("stride", 10)
            defaults = {}
            if kind == "streamline" and not p:
                source = self.scene.datasets.get((node or {}).get("input"))
                if source is not None:
                    from modules.visEngine import seed_defaults

                    defaults = seed_defaults(source.GetBounds())
            state.seed_start = ",".join(map(str, p.get("seed_start", defaults.get("seed_start", [0, 0, 0]))))
            state.seed_end = ",".join(map(str, p.get("seed_end", defaults.get("seed_end", [0, 1, 0]))))
            state.seed_count = p.get("seeds", defaults.get("seeds", 20))
            state.seed_type = p.get("seed_type") or "line"
            state.seed_center = ",".join(
                map(str, p.get("seed_center", defaults.get("seed_center", [0, 0, 0])))
            )
            state.seed_radius = p.get("seed_radius", defaults.get("seed_radius", 1))
            state.seed_origin = ",".join(
                map(str, p.get("seed_origin", defaults.get("seed_origin", [0, 0, 0])))
            )
            state.seed_normal = ",".join(
                map(str, p.get("seed_normal", defaults.get("seed_normal", [0, 0, 1])))
            )
            state.seed_width = p.get("seed_width", defaults.get("seed_width", 1))
            state.seed_height = p.get("seed_height", defaults.get("seed_height", 1))
            seed = p.get("seed_surface") or {}
            if seed.get("kind") == "object":
                state.seed_surface = f"object:{seed.get('id', '')}"
            elif seed.get("kind") == "block":
                state.seed_surface = f"block:{seed.get('index', 0)}:{seed.get('name', '')}"
            elif seed.get("kind") == "patch":
                state.seed_surface = f"patch:{seed.get('name', '')}"
            else:
                state.seed_surface = ""
            state.flow_length = p.get("length", defaults.get("length", 10))
            state.flow_direction = p.get("direction", "both")
            state.probe_position = ",".join(map(str, (node or {}).get("position", [0, 0, 0])))
            state.probe_label = (
                (node or {}).get("views", {}).get(str(state.active_view), {}).get("label", True)
            )
            state.probe_fields = (node or {}).get("fields", [])
            if state.selected in self.drafts and "form" in self.drafts[state.selected]:
                state.update(self.drafts[state.selected]["form"])
            for key in (
                "plane_origin",
                "plane_normal",
                "seed_start",
                "seed_end",
                "seed_center",
                "seed_origin",
                "seed_normal",
                "probe_position",
            ):
                values = str(state[key]).split(",")
                for index in range(3):
                    state[f"{key}_{index}"] = values[index] if index < len(values) else "0"
            self.baseline = {k: deepcopy(state[k]) for k in PARAM_KEYS}
            state.pending = state.selected in self.drafts

    def refresh(self, **kwargs):
        """公开元数据，树只包含来源和真实创建的对象。"""
        update_view = kwargs.get("update_view", True)
        state = self.server.state
        snap = self.scene.snapshot()
        spec = snap["spec"]
        from ..modules.fieldVisualization.view import camera_spec

        state.render_cameras = [
            {
                "layer": r.GetLayer(),
                "viewport": list(r.GetViewport()),
                "camera": camera_spec(r.GetActiveCamera()),
                "clipping_range": list(r.GetActiveCamera().GetClippingRange()),
            }
            for r in self.scene.renderers + self.scene.decorations
        ]
        nodes = {
            s["id"]: {
                "id": s["id"],
                "name": s.get("name", s["id"]),
                "children": [],
                "source": True,
                "visible": any(
                    l.get("visible", True)
                    for l in spec["layers"]
                    if l["view"] == state.active_view and l["input"] in self.descendants(s["id"])
                ),
            }
            for s in spec["sources"]
        }
        roots = list(nodes.values())
        objects = (
            spec["pipeline"]
            + spec["probes"]
            + [d["node"] for d in self.drafts.values() if d.get("new")]
        )
        for n in objects:
            visible = next(
                (
                    l.get("visible", True)
                    for l in spec["layers"]
                    if l["input"] == n["id"] and l["view"] == state.active_view
                ),
                False,
            )
            if "position" in n:
                visible = n.get("views", {}).get(str(state.active_view), {}).get("visible", False)
            item = {
                "id": n["id"],
                "name": n.get("name", n["id"]) + (" *" if n["id"] in self.drafts else ""),
                "children": [],
                "probe": "position" in n,
                "visible": visible,
            }
            nodes[n["id"]] = item
            nodes.get(n["input"], {}).get("children", roots).append(item)
        node = self.object()
        # Probe 只有坐标和字段声明，元数据属于它的输入，保存后也不产生独立网格。
        use_input = state.selected in self.drafts or "position" in (node or {})
        mesh_id = (node or {}).get("input") if use_input else state.selected
        metadata = snap["datasets"].get(mesh_id, {})
        fields = metadata.get("fields", [])
        input_meta = snap["datasets"].get((node or {}).get("input"), metadata)
        input_fields = input_meta.get("fields", [])
        selected_meta = snap["datasets"].get(state.selected, input_meta)
        selected_fields = selected_meta.get("fields", [])
        with state:
            state.view_ids = [v["id"] for v in spec["views"]]
            state.tree_nodes = roots
            state.tree_open = list(nodes)
            state.view_items = spec["views"]
            state.view_frames = self.overlay_frames()
            state.dirty_names = ", ".join(d["node"]["name"] for d in self.drafts.values())
            state.field_items = [{"text": "纯色", "value": ""}] + [
                {
                    "text": f"{f['name']} ({f['association']})",
                    "value": f"{f['association']}|{f['name']}",
                }
                for f in fields
            ]
            state.compute_items = [
                {
                    "text": f"{f['name']} ({f['association']})",
                    "value": f"{f['association']}|{f['name']}",
                }
                for f in input_fields
                if state.kind not in ("glyph", "streamline") or f["components"] == 3
            ]
            state.probe_field_items = [f"{f['association']}:{f['name']}" for f in fields]
            state.can_vector = any(f["components"] == 3 for f in selected_fields)
            state.can_iso = selected_meta.get("dimension", 0) == 3 and bool(selected_fields)
            state.can_contour = bool(selected_fields) and (
                selected_meta.get("dimension", 0) <= 2 or state.kind == "surface"
            )
            state.can_create = bool(selected_meta) and state.kind != "probe"
            state.pending = state.selected in self.drafts
            state.time_values = snap["times"]
            state.time_items = [
                {"text": f"{i + 1}/{len(snap['times'])}", "value": i}
                for i, t in enumerate(snap["times"])
            ]
            state.time_index = (
                snap["times"].index(spec["time"]["value"])
                if spec.get("time", {}).get("value") in snap["times"]
                else 0
            )
            state.missing_text = "缺帧: " + ", ".join(snap["missing"]) if snap["missing"] else ""
            state.status_text = (
                "结果为空"
                if metadata.get("points") == 0
                else f"{metadata.get('points', 0)} 点 · {metadata.get('cells', 0)} 单元"
            )
            state.link_cameras = bool(spec["link_groups"])
            view = next(v for v in spec["views"] if v["id"] == state.active_view)
            state.axes = view.get("axes", True)
            state.shadows = view.get("shadows", False)
            import sys

            state.can_shadow = sys.platform == "linux" and spec.get("renderer") == "remote"
            # 快照已列出命名面；再调一次会在相机回写路径上重复读盘。
            state.seed_surface_items = [
                item
                for item in snap.get("seed_surfaces", [])
                if item.get("value") != f"object:{state.selected}"
            ]
            state.plane_widget = self.plane_widget_state()
            if state.kind == "probe":
                self.show_rows([snap.get("probes", {}).get(state.selected, {})])
        self.sync_plane_widget()
        # 创建草稿不必重推整屏；连点切面会把工作进程再次打满。
        if update_view and self.view:
            if self.scene.spec.get("renderer") != "remote":
                from ..rendering import install_local_serializers

                install_local_serializers()
            self.view.update()

    def descendants(self, identity):
        """委托领域依赖遍历，UI 不复制删除规则。"""
        from ..commands import descendants

        return descendants(self.scene.spec, identity)

    def command(self, body):
        """失败保留画面并在工作台内反馈。"""
        try:
            self.server.state.busy = True
            result = self.scene.command(body)
            self.server.state.error = ""
            return result
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            self.server.state.error = str(exc)
            return None
        finally:
            self.server.state.busy = False

    def begin(self, kind):
        """同一输入只留一份未应用草稿；连点不嵌套、不重推整屏。"""
        state = self.server.state
        if state.busy:
            return
        parent = state.selected
        current = self.drafts.get(parent)
        if current and current.get("new"):
            parent = current["node"].get("input") or parent
        for key, item in self.drafts.items():
            node = item.get("node") or {}
            if item.get("new") and node.get("type", "probe") == kind and node.get("input") == parent:
                state.selected = key
                self.hydrate()
                return
        self.stash()
        identity = uuid4().hex
        node = {
            "id": identity,
            "name": f"{LABELS[kind]} {1 + sum(n.get('type', 'probe') == kind for n in self.scene.spec['pipeline'] + self.scene.spec['probes'])}",
            "input": parent,
        }
        if kind == "probe":
            node.update(position=[0, 0, 0], fields=[])
        else:
            node.update(type=kind, parameters={})
        self.drafts[identity] = {"node": node, "new": True}
        state.selected = identity
        self.hydrate()
        self.refresh(update_view=False)
        if state.compute_items:
            state.compute_field = state.compute_items[0]["value"]
        if kind == "probe":
            self.mode("probe")

    @staticmethod
    def xyz(value):
        """将坐标表单解析为恰好三个有限数值。"""
        import math

        values = [float(x) for x in str(value).split(",")]
        if len(values) != 3 or not all(math.isfinite(x) for x in values):
            raise ValueError("需要三个有限坐标")
        return values

    @staticmethod
    def field(value, component):
        """显式解析字段归属，避免同名 point/cell 字段混淆。"""
        if not value:
            raise ValueError("请选择计算物理量")
        association, name = value.split("|", 1)
        return {
            "name": name,
            "association": association,
            "component": int(component) if str(component).isdigit() else component,
        }

    def apply_selected(self):
        """把表单草稿提交为对象参数，事务失败保留草稿。"""
        state = self.server.state
        if state.busy or getattr(self, "_applying", False):
            return False
        node = self.object()
        if not node:
            return False
        self._applying = True
        try:
            return self._apply_selected(state, node)
        finally:
            self._applying = False

    def _apply_selected(self, state, node):
        """实际提交切面等对象；调用方负责防重入。"""
        try:
            p = {}
            kind = node.get("type", "probe")
            if kind in ("slice", "clip"):
                p.update(
                    origin=self.xyz(state.plane_origin),
                    normal=self.xyz(state.plane_normal),
                    inside_out=state.inside_out,
                )
            if kind in ("glyph", "streamline", "isosurface", "contour"):
                p["field"] = self.field(state.compute_field, state.compute_component)
            if kind in ("isosurface", "contour"):
                p["values"] = [float(x) for x in state.iso_values.split(",")]
            if kind == "glyph":
                p.update(scale=float(state.vector_scale), stride=int(state.vector_stride))
            if kind == "streamline":
                seed_kind = state.seed_type or "line"
                p.update(
                    seed_type=seed_kind,
                    seeds=int(state.seed_count),
                    length=float(state.flow_length),
                    direction=state.flow_direction,
                )
                if seed_kind == "line":
                    p.update(
                        seed_start=self.xyz(state.seed_start),
                        seed_end=self.xyz(state.seed_end),
                    )
                elif seed_kind == "sphere":
                    p.update(
                        seed_center=self.xyz(state.seed_center),
                        seed_radius=float(state.seed_radius),
                    )
                elif seed_kind == "plane":
                    p.update(
                        seed_origin=self.xyz(state.seed_origin),
                        seed_normal=self.xyz(state.seed_normal),
                        seed_width=float(state.seed_width),
                        seed_height=float(state.seed_height),
                    )
                else:
                    surface = self.parse_seed_surface(state.seed_surface)
                    if not surface:
                        raise ValueError("请选择命名面")
                    p["seed_surface"] = surface
            new = self.drafts.get(node["id"], {}).get("new", False)
            body = {
                "operation": ("probe_create" if new else "probe_update")
                if kind == "probe"
                else ("object_create" if new else "object_update"),
                "id": node["id"],
                "name": node["name"],
                "input": node["input"],
                "view": state.active_view,
            }
            if kind == "probe":
                body.update(
                    position=self.xyz(state.probe_position),
                    fields=state.probe_fields,
                    views=node.get("views", {str(state.active_view): {"visible": True}}),
                )
            else:
                body.update(type=kind, parameters=p)
            if self.command(body) is None:
                return False
            self.drafts.pop(node["id"], None)
            self.hydrate()
            self.refresh()
            return True
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            state.error = str(exc)
            return False

    def mark_dirty(self, *_):
        """输入计算参数仅标记草稿，不触发 VTK。"""
        self.stash()
        self.server.state.pending = True

    def set_display(self, key, value):
        """事件显式传递新值，避免 Vue change 先于 v-model 同步。"""
        self.server.state[key] = value
        self.display()

    def set_parameter(self, key, value):
        """计算参数按事件值写入草稿，应用时不读取过时表单。"""
        self.server.state[key] = value
        if key == "seed_type" and value == "surface" and not self.server.state.seed_surface:
            items = self.server.state.seed_surface_items or []
            if items:
                self.server.state.seed_surface = items[0]["value"]
        self.mark_dirty()

    def set_coordinate(self, key, index, value):
        """独立坐标输入合并到既有三分量草稿，保持配置与应用校验不变。"""
        values = str(self.server.state[key]).split(",")
        values += ["0"] * (3 - len(values))
        values[index] = str(value)
        self.set_parameter(key, ",".join(values))
        if key in ("plane_origin", "plane_normal"):
            self.sync_plane_widget()
            if self.view:
                self.view.update()

    @staticmethod
    def parse_seed_surface(value):
        """把下拉键还原为配置里的种子面引用。"""
        if not value:
            return {}
        kind, rest = str(value).split(":", 1)
        if kind == "object":
            return {"kind": "object", "id": rest}
        if kind == "patch":
            return {"kind": "patch", "name": rest}
        if kind == "block":
            index, name = rest.split(":", 1)
            return {"kind": "block", "index": int(index), "name": name}
        raise ValueError("invalid_seed_surface")

    def plane_widget_state(self):
        """把当前切面草稿交给客户端做手柄命中，避免两套几何。"""
        node = self.object()
        if not node or node.get("type") not in ("slice", "clip"):
            return {"visible": False}
        try:
            origin = self.xyz(self.server.state.plane_origin)
            normal = self.xyz(self.server.state.plane_normal)
        except ValueError:
            return {"visible": False}
        mesh = self.scene.datasets.get(node.get("input"))
        bounds = list(mesh.GetBounds()) if mesh is not None else [-1, 1, -1, 1, -1, 1]
        return {"visible": True, "origin": origin, "normal": normal, "bounds": bounds}

    def sync_plane_widget(self):
        """选中切面时显示可视平面，其它对象撤下。"""
        state = self.plane_widget_state()
        self.server.state.plane_widget = state
        if not state.get("visible"):
            self.scene.clear_plane_widget()
            return
        self.scene.show_plane_widget(
            state["origin"], state["normal"], state["bounds"], self.server.state.active_view
        )

    def align_plane_axis(self, axis):
        """属性 X/Y/Z 只改法向并回填草稿，仍须应用才切开。"""
        from modules.visEngine import align_plane_normal

        origin, normal = align_plane_normal(self.xyz(self.server.state.plane_origin), axis)
        self.set_parameter("plane_origin", ",".join(map(str, origin)))
        self.set_parameter("plane_normal", ",".join(map(str, normal)))
        for key, values in (("plane_origin", origin), ("plane_normal", normal)):
            self.server.state[key] = ",".join(map(str, values))
            for index, value in enumerate(values):
                self.server.state[f"{key}_{index}"] = str(value)
        self.sync_plane_widget()
        if self.view:
            self.view.update()

    def screen_ray(self, x, y, width=None, height=None):
        """与拾取共用窗口比例，本地远程同一条射线。"""
        if self.scene.spec.get("renderer") != "remote" and width and height:
            self.scene.window.SetSize(int(width), int(height))
        for i, renderer in enumerate(self.scene.renderers):
            x0, y0, x1, y1 = renderer.GetViewport()
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.view_select(self.scene.spec["views"][i]["id"])
                w, h = self.scene.window.GetSize()
                ray = []
                for depth in (0, 1):
                    renderer.SetDisplayPoint(x * w, y * h, depth)
                    renderer.DisplayToWorld()
                    point = renderer.GetWorldPoint()
                    ray.append([v / point[3] for v in point[:3]])
                return ray
        return None

    def plane_press(self, x, y, width=None, height=None):
        """按下时命中手柄则开始拖动，不切开。"""
        ray = self.screen_ray(x, y, width, height)
        handle = self.scene.pick_plane_widget(ray) if ray else None
        self.server.state.plane_dragging = handle or ""
        self._plane_drag_start = ray if handle else None
        return handle

    def plane_move(self, x, y, width=None, height=None):
        """拖动只改可视平面和草稿数字。"""
        handle = self.server.state.plane_dragging
        ray = self.screen_ray(x, y, width, height)
        if not handle or not self._plane_drag_start or not ray:
            return
        node = self.object() or {}
        result = self.scene.command(
            {
                "operation": "plane_drag",
                "handle": handle,
                "origin": self.xyz(self.server.state.plane_origin),
                "normal": self.xyz(self.server.state.plane_normal),
                "start": self._plane_drag_start,
                "end": ray,
                "input": node.get("input"),
                "view": self.server.state.active_view,
            }
        )
        origin, normal = result["origin"], result["normal"]
        self._plane_drag_start = ray
        for key, values in (("plane_origin", origin), ("plane_normal", normal)):
            text = ",".join(map(str, values))
            self.server.state[key] = text
            for index, value in enumerate(values):
                self.server.state[f"{key}_{index}"] = str(value)
        self.mark_dirty()
        self.sync_plane_widget()
        if self.view:
            self.view.update()

    def plane_release(self):
        """松开只结束拖动，仍须应用才切开。"""
        self.server.state.plane_dragging = ""
        self._plane_drag_start = None

    def display(self, *_):
        """显示属性即时提交；草稿分析对象先应用再着色。"""
        state = self.server.state
        if (
            not self.object()
            or state.kind == "probe"
            or self.drafts.get(state.selected, {}).get("new")
        ):
            return
        try:
            color = {"preset": state.palette, "bands": int(state.bands), "legend": state.legend}
            if state.range_min != "" and state.range_max != "":
                color["range"] = [float(state.range_min), float(state.range_max)]
            self.command(
                {
                    "operation": "display",
                    "id": state.selected,
                    "view": state.active_view,
                    "field": self.field(state.coloring, state.component)
                    if state.coloring
                    else None,
                    "color": color,
                    "style": {
                        "opacity": float(state.opacity),
                        "mode": state.display_mode,
                        "lighting": state.lighting,
                    },
                }
            )
            self.refresh()
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            state.error = str(exc)

    def visible(self, identity):
        """显隐只改活动视图已有 actor，不重建映射、不重读网格。"""
        state = self.server.state
        spec = self.scene.spec
        affected = self.descendants(identity)
        node = next((item for item in spec.get("probes", []) if item["id"] == identity), None)
        if node:
            current = node.get("views", {}).get(str(state.active_view), {}).get("visible", False)
            enabled = not current
            node.setdefault("views", {}).setdefault(str(state.active_view), {})["visible"] = enabled
            self.command({"operation": "apply", "spec": spec})
            self._sync_tree_visible(affected, enabled)
            return
        layers = [
            item
            for item in spec.get("layers", [])
            if item["input"] in affected and item["view"] == state.active_view
        ]
        enabled = not any(item.get("visible", True) for item in layers)
        if not layers and self.object(identity):
            self.command(
                {
                    "operation": "display",
                    "id": identity,
                    "view": state.active_view,
                    "visible": True,
                }
            )
            self._sync_tree_visible({identity}, True)
            self._push_visibility_view()
            return
        for layer in layers:
            self.scene.set_layer_visibility(layer["id"], enabled)
        if identity in [source["id"] for source in spec.get("sources", [])]:
            for probe in spec.get("probes", []):
                if probe["id"] in affected:
                    probe.setdefault("views", {}).setdefault(str(state.active_view), {})[
                        "visible"
                    ] = enabled
        self._sync_tree_visible(affected, enabled)
        self._push_visibility_view()

    def _sync_tree_visible(self, identities, enabled):
        """对象树眼睛只改标记，不重新画像数据集。"""
        found = set(identities)

        def walk(nodes):
            updated = []
            for node in nodes or []:
                item = dict(node)
                if item.get("id") in found:
                    item["visible"] = enabled
                children = item.get("children") or []
                if children:
                    item["children"] = walk(children)
                updated.append(item)
            return updated

        self.server.state.tree_nodes = walk(self.server.state.get("tree_nodes") or [])

    def _push_visibility_view(self):
        """把已有 actor 显隐推到客户端，不走 snapshot/refresh。"""
        if not self.view:
            return
        if self.scene.spec.get("renderer") != "remote":
            from ..rendering import install_local_serializers

            install_local_serializers()
        self.view.update()

    def probe_label(self, value):
        """标签显隐为当前视图即时属性，不改变固定采样位置。"""
        node = self.object()
        if not node or "position" not in node:
            return
        views = deepcopy(node.get("views", {}))
        views.setdefault(str(self.server.state.active_view), {"visible": True})["label"] = bool(
            value
        )
        if self.drafts.get(node["id"], {}).get("new"):
            node["views"] = views
        else:
            self.command({"operation": "probe_update", "id": node["id"], "views": views})
        self.refresh()

    def view_select(self, identity):
        """切换活动视图并恢复对应的显示属性。"""
        self.stash()
        self.server.state.active_view = identity
        self.hydrate()
        self.refresh()

    def view_action(self, operation, direction="horizontal"):
        """布局变更不删除对象，最大化属于临时 UI 状态。"""
        state = self.server.state
        result = self.command(
            {"operation": operation, "view": state.active_view, "direction": direction}
        )
        if result:
            ids = [v["id"] for v in self.scene.spec["views"]]
            state.active_view = (
                ids[-1]
                if operation == "view_create"
                else (state.active_view if state.active_view in ids else ids[0])
            )
            self.hydrate()
            self.refresh()

    def layout_ratio(self, value):
        """调整活动视图最近一级分割比例。"""
        layout = deepcopy(self.scene.spec["layout"])

        def replace(node):
            """递归定位活动叶子的直接父分割。"""
            if "children" not in node:
                return False
            if any(c.get("view") == self.server.state.active_view for c in node["children"]):
                node["ratio"] = float(value)
                return True
            return any(replace(c) for c in node["children"])

        if replace(layout):
            self.command({"operation": "view_layout", "layout": layout})
            self.refresh()

    def mode(self, value):
        """本地使用 VTK.js 公开手势配置，远程使用 VTK 原生交互状态。"""
        actions = {
            "rotate": "Rotate",
            "pan": "Pan",
            "zoom": "Zoom",
            "select": "Select",
            "probe": "Select",
        }
        self.server.state.interaction_mode = value
        self.server.state.interaction_settings = [
            {"button": 1, "action": actions[value]},
            {"button": 2, "action": "Pan"},
            {"button": 3, "action": "Zoom", "scrollEnabled": True},
        ]
        if value in ("select", "probe"):
            self.server.state.interaction_settings = self.server.state.interaction_settings[1:]
        interactor = self.scene.window.GetInteractor()
        if interactor:
            import vtk

            style = vtk.vtkInteractorStyleTrackballCamera()

            def press(*_):
                """按当前模式启动原生 VTK 相机交互。"""
                x, y = interactor.GetEventPosition()
                style.FindPokedRenderer(x, y)
                mode = self.server.state.interaction_mode
                if mode == "pan":
                    style.StartPan()
                elif mode == "zoom":
                    style.StartDolly()
                elif mode == "rotate":
                    style.OnLeftButtonDown()

            def release(*_):
                """释放鼠标时结束当前交互状态。"""
                style.EndPan()
                style.EndDolly()
                style.OnLeftButtonUp()

            style.AddObserver("LeftButtonPressEvent", press)
            style.AddObserver("LeftButtonReleaseEvent", release)
            interactor.SetInteractorStyle(style)

    def overlay_frames(self):
        """窗体标签跟随当前布局矩形，最大化时只保留活动窗口。"""
        from modules.visTaskManage import view_overlay_frames

        state = self.server.state
        return view_overlay_frames(
            self.scene.spec["layout"],
            self.scene.spec["views"],
            maximize=state.maximize,
            active=state.active_view,
        )

    def maximize(self):
        """临时最大化，不修改保存布局。"""
        from modules.visTaskManage import layout_rectangles

        state = self.server.state
        state.maximize = not state.maximize
        rectangles = layout_rectangles(self.scene.spec["layout"])
        for i, r in enumerate(self.scene.renderers):
            identity = self.scene.spec["views"][i]["id"]
            r.SetDraw(not state.maximize or identity == state.active_view)
            r.SetViewport(
                (0, 0, 1, 1)
                if state.maximize and identity == state.active_view
                else rectangles[identity]
            )
        state.view_frames = self.overlay_frames()
        for r in self.scene.decorations:
            r.SetDraw(not state.maximize)
        if self.view:
            self.view.update()

    def request(self, action):
        """保存和导出前处理未应用草稿，再通知拥有资产表单的 React。"""
        self.stash()
        if self.drafts:
            self.pending_action = action
            self.server.state.draft_dialog = True
            return
        self.emit(action)

    def emit(self, action):
        """发送有请求身份的同源嵌入消息。"""
        self.bridge.call(
            "dispatch",
            {
                "action": action,
                "payload": {
                    "view": self.server.state.active_view,
                    "times": self.scene.times,
                    "selected": self.server.state.selected,
                },
            },
        )

    def resolve_drafts(self, apply):
        """应用全部或丢弃草稿，取消按钮不调用本操作。"""
        selected = self.server.state.selected
        if apply:
            for identity in list(self.drafts):
                self.server.state.selected = identity
                self.hydrate()
                if not self.apply_selected():
                    return
        else:
            self.drafts.clear()
        self.server.state.selected = (
            selected
            if self.object(selected)
            else next((n["id"] for n in self.scene.spec["pipeline"]), "")
        )
        self.hydrate()
        self.refresh()
        self.server.state.draft_dialog = False
        self.emit(self.pending_action)

    def request_delete(self, identity):
        """行内删除先选中该对象，再打开同一确认框。"""
        self.select(identity)
        self.menu("delete")

    def menu(self, action):
        """菜单只暴露可执行的对象操作和宿主表单。"""
        state = self.server.state
        if action in ("save", "open", "import", "configuration", "animation", "export", "record"):
            self.request(action)
            return
        if action == "rename":
            state.rename_dialog = True
            return
        if action == "copy":
            self.command({"operation": "object_copy", "id": state.selected})
            self.refresh()
        if action == "delete":
            affected = self.descendants(state.selected)
            state.delete_names = ", ".join(
                n.get("name", n["id"])
                for n in self.scene.spec["pipeline"] + self.scene.spec["probes"]
                if n["id"] in affected
            )
            state.delete_dialog = True

    def rename(self):
        """名称更新不改变对象身份。"""
        if self.command(
            {
                "operation": "object_rename",
                "id": self.server.state.selected,
                "name": self.server.state.object_name,
            }
        ):
            self.server.state.rename_dialog = False
            self.refresh()

    def delete(self):
        """用户确认后级联移除对象，源文件保持不变。"""
        state = self.server.state
        affected = self.descendants(state.selected)
        # 草稿尚未进入正式依赖图，也要随父对象一起移除。
        while any(
            d["node"]["input"] in affected and k not in affected for k, d in self.drafts.items()
        ):
            affected.update(k for k, d in self.drafts.items() if d["node"]["input"] in affected)
        op = (
            "source_remove"
            if state.selected in [s["id"] for s in self.scene.spec["sources"]]
            else "object_delete"
        )
        if self.command({"operation": op, "id": state.selected, "cascade": True}):
            self.drafts = {k: d for k, d in self.drafts.items() if k not in affected}
            state.selected = next((n["id"] for n in self.scene.spec["pipeline"]), "")
            state.delete_dialog = False
            self.hydrate()
            self.refresh()

    def camera(self, direction=None):
        """相机命令只作用于活动视图及其联动组。"""
        self.command(
            {
                "operation": "camera",
                "view": self.server.state.active_view,
                **({"direction": direction} if direction else {}),
            }
        )
        self.refresh()

    def view_setting(self, key, value):
        """视图级开关与对象属性独立保存。"""
        self.command(
            {
                "operation": "view_update",
                "view": self.server.state.active_view,
                "settings": {key: value},
            }
        )
        self.refresh()

    def link(self, value):
        """开启后全体窗口共用相机，仍经坐标空间门禁。"""
        self.command(
            {
                "operation": "link_views",
                "views": [v["id"] for v in self.scene.spec["views"]] if value else [],
            }
        )
        self.refresh()

    def seek(self, value=None):
        """选择真实时间值，缺帧由场景报告。"""
        values = self.scene.times
        if values:
            self.command(
                {
                    "operation": "time",
                    "value": values[int(self.server.state.time_index if value is None else value)],
                }
            )
            self.refresh()

    def step(self, direction):
        """逐帧有界前进/后退。"""
        if self.scene.times:
            self.seek(
                max(
                    0, min(len(self.scene.times) - 1, int(self.server.state.time_index) + direction)
                )
            )

    def visibility(self, visible):
        """隐藏暂停当前时间，返回只刷新视图，不清空对象或草稿。"""
        if not isinstance(visible, bool):
            raise ValueError("visibility_requires_boolean")
        if not visible:
            self.pause()
        elif self.view:
            self.view.update()
        return {"visible": visible}

    def pause(self):
        """使旧播放循环失效。"""
        self.playing += 1
        self.server.state.playing = False

    def stop(self):
        """停止并恢复第一时间步。"""
        self.pause()
        self.seek(0)

    def play(self, direction=1):
        """事件循环串行更新，避免跨线程访问 VTK。"""
        if not self.scene.times:
            return
        self.pause()
        token = self.playing
        self.server.state.playing = True

        async def run():
            """按实际时间索引连续播放，旧循环可失效。"""
            while token == self.playing:
                nxt = int(self.server.state.time_index) + direction
                if not 0 <= nxt < len(self.scene.times):
                    break
                self.seek(nxt)
                await asyncio.sleep(0.1)
            if token == self.playing:
                self.server.state.playing = False

        asyncio.create_task(run())

    def query(self, operation="probe"):
        """查询选定 Probe 的当前数值或时间曲线。"""
        node = self.object()
        if not node or "position" not in node:
            return
        result = self.command(
            {"operation": operation, "input": node["input"], "positions": [node["position"]]}
        )
        if result:
            self.show_rows(result["rows"])
            from ..modules.dataOverview.basicCharts import history_curve

            self.server.state.query_curve = (
                history_curve(result["rows"]) if operation == "temporal" else ""
            )

    def show_rows(self, rows):
        """展示可读字段表，保留域外与缺帧状态而不填零。"""
        items = []
        for row in rows:
            prefix = f"t={row['time']:g} · " if "time" in row else ""
            values = row.get("fields") or row.get("values") or {}
            items.append(
                {
                    "field": prefix + "位置",
                    "value": ", ".join(f"{x:g}" for x in row.get("position", [])),
                }
            )
            items.append(
                {
                    "field": prefix + "状态",
                    "value": "有效"
                    if row.get("valid")
                    else "缺帧"
                    if row.get("status") == "missing_frame"
                    else "域外或来源不可用",
                }
            )
            for key, value in values.items():
                items.append(
                    {
                        "field": prefix + key,
                        "value": ", ".join(f"{v:.6g}" for v in value)
                        if isinstance(value, list)
                        else str(value),
                    }
                )
        self.server.state.query_table = items

    def export_probe(self):
        """固定当前 Probe 输入与空间位置后进入显式 CSV 输出。"""
        self.query()
        self.request("export_csv")

    def remote_end(self, *_):
        """远程交互结束后刷新可导出的场景注记。"""
        self.scene.add_annotations()
        self.refresh()

    def resize(self, size):
        """容器尺寸变化只重定位注记，不刷新对象树、不重读网格。"""
        width, height = int(size["width"]), int(size["height"])
        if min(width, height) < 1 or self.scene.window.GetSize() == (width, height):
            return
        self.scene.window.SetSize(width, height)
        self.scene.add_annotations()
        if self.view:
            if self.scene.spec.get("renderer") != "remote":
                from ..rendering import install_local_serializers

                install_local_serializers()
            self.view.update()

    def camera_event(self, event):
        """交互结束只回写活动相机，不走整屏 refresh，避免再次读盘和推场景。"""
        views = self.scene.spec["views"]
        if event.get("view") not in [v["id"] for v in views]:
            return
        index = next(i for i, v in enumerate(views) if v["id"] == event["view"])
        import numpy as np

        from ..modules.fieldVisualization.view import camera_spec, set_camera

        camera = self.scene.renderers[index].GetActiveCamera()
        current = camera_spec(camera)
        incoming = event.get("camera") or {}
        if incoming and all(
            k in current and np.allclose(current[k], value, rtol=1e-4, atol=1e-5)
            for k, value in incoming.items()
        ):
            return
        if incoming:
            set_camera(camera, incoming)
        views[index]["camera"] = camera_spec(camera)
        self.server.state.active_view = event["view"]

    def camera_changed(self, value, pointer):
        """回传实际相机，固定修订导出与屏幕视角一致。"""
        from ..modules.fieldVisualization.view import set_camera

        mapping = {
            "position": "position",
            "focalPoint": "focal_point",
            "viewUp": "view_up",
            "parallelScale": "parallel_scale",
            "parallelProjection": "parallel_projection",
        }
        translated = {
            target: value[source] for source, target in mapping.items() if source in value
        }
        for i, r in enumerate(self.scene.renderers):
            x0, y0, x1, y1 = r.GetViewport()
            if x0 <= pointer[0] <= x1 and y0 <= pointer[1] <= y1:
                set_camera(r.GetActiveCamera(), translated)
                self.server.state.active_view = self.scene.spec["views"][i]["id"]
                break
        if self.scene.spec.get("link_groups"):
            self.refresh()

    def pick_screen(self, x, y, width=None, height=None):
        """按实际点击视口与浏览器比例构造射线，本地/远程使用同一实体求交。"""
        if self.scene.spec.get("renderer") != "remote" and width and height:
            self.scene.window.SetSize(int(width), int(height))
        for i, r in enumerate(self.scene.renderers):
            x0, y0, x1, y1 = r.GetViewport()
            if x0 <= x <= x1 and y0 <= y <= y1:
                self.view_select(self.scene.spec["views"][i]["id"])
                w, h = self.scene.window.GetSize()
                ray = []
                for depth in (0, 1):
                    r.SetDisplayPoint(x * w, y * h, depth)
                    r.DisplayToWorld()
                    p = r.GetWorldPoint()
                    ray.append([v / p[3] for v in p[:3]])
                self.pick({"ray": ray})
                return

    def pick(self, selection):
        """鼠标选择与 Probe 创建分开；射线求交由完整网格执行。"""
        state = self.server.state
        mode = state.interaction_mode
        if mode not in ("select", "probe"):
            return
        hit = selection[0] if isinstance(selection, list) and selection else selection
        if not isinstance(hit, dict) or not hit.get("ray"):
            return
        candidates = [
            l
            for l in self.scene.spec["layers"]
            if l["view"] == state.active_view and l.get("visible", True)
        ]
        if mode == "probe" and self.object():
            candidates = [{"input": self.object()["input"]}]
        hits = []
        hit_ray = hit["ray"]
        for layer in candidates:
            if layer["input"] in self.scene.missing:
                continue
            result = self.command(
                {
                    "operation": "pick",
                    "input": layer["input"],
                    "ray": hit["ray"],
                    "association": "cell",
                }
            )
            if result and result.get("valid"):
                hits.append((result, layer["input"]))
        if not hits:
            return
        point, input_id = min(
            hits,
            key=lambda hit: sum((hit[0]["position"][i] - hit_ray[0][i]) ** 2 for i in range(3)),
        )
        if mode == "select":
            self.select(input_id)
        else:
            position = point.get("position")
            if position:
                self.server.state.probe_position = ",".join(map(str, position))
                for index, value in enumerate(position):
                    self.server.state[f"probe_position_{index}"] = str(value)
                self.mark_dirty()
