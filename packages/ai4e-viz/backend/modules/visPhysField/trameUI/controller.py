"""工作台选中对象与未应用草稿；UI 不拥有 VTK 处理算法。"""

import math
from copy import deepcopy
from uuid import uuid4

from .camera_controls import CameraControls
from .export_controls import ExportControls
from .object_controls import ObjectControls
from .session_controls import SessionControls

LABELS = {
    "surface": "基础显示",
    "glyph": "矢量图",
    "slice": "切面",
    "clip": "剖切",
    "streamline": "流线",
    "isosurface": "等值面",
    "contour": "等高线",
    "probe": "Probe",
    "plot_over_line": "线段提取",
}
LEGEND_FORM_KEYS = (
    "legend",
    "legend_position",
    "legend_orientation",
    "legend_length",
    "legend_thickness",
    "legend_title_size",
    "legend_label_size",
    "legend_x",
    "legend_y",
)
DISPLAY_KEYS = [
    "coloring",
    "component",
    "palette",
    "bands",
    "range_mode",
    "range_min",
    "range_max",
    "opacity",
    "display_mode",
    "lighting",
    "legend",
    "legend_position",
    "legend_orientation",
    "legend_length",
    "legend_thickness",
    "legend_title_size",
    "legend_label_size",
    "legend_x",
    "legend_y",
    "plane_visible",
    "seeds_visible",
    "solid_color",
    "line_width",
    "streamline_shape",
    "streamline_thickness",
    "streamline_sides",
    "lic_steps",
    "lic_step_size",
    "lic_enhanced",
    "lic_contrast",
    "lic_color_mode",
    "lic_intensity",
]
PARAM_KEYS = [
    "level_mode",
    "level_count",
    "level_min",
    "level_max",
    "plane_origin",
    "plane_normal",
    "inside_out",
    "crinkle_slice",
    "triangulate_slice",
    "compute_field",
    "compute_component",
    "iso_values",
    "iso_slider",
    "line_start",
    "line_end",
    "line_resolution",
    "line_fields",
    "glyph_shape",
    "glyph_scale_mode",
    "glyph_scale_field",
    "glyph_sampling",
    "glyph_spacing",
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
        self.camera_controls = CameraControls(self)
        self.session_controls = SessionControls(self)
        self.object_controls = ObjectControls(self)
        self.export_controls = ExportControls(self)
        self.drafts = {}
        self._remembered_ranges = {}
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
                "link_notice": "",
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
                "probe_pick_enabled": False,
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
                "seed_preview": False,
                "can_preview_seeds": False,
                "seeds_visible": True,
                "iso_slider": 0,
                "iso_field_min": 0,
                "iso_field_max": 1,
                "iso_range_text": "",
                "iso_range_hint": "",
                "line_resolution": 1000,
                "line_fields": [],
                "chart_x_array": "arc_length",
                "chart_y_arrays": [],
                "chart_x_items": [],
                "chart_y_items": [],
                "lic_steps": 40,
                "lic_step_size": 0.25,
                "lic_enhanced": True,
                "lic_contrast": "both",
                "lic_color_mode": "blend",
                "lic_intensity": 0.8,
                "use_remote_view": False,
                "remote_ready": False,
                "remote_handoff": False,
                "solid_color": "#ccc8e6",
                "line_width": 1,
                "streamline_shape": "line",
                "streamline_thickness": 1,
                "streamline_sides": 8,
                "plane_visible": True,
                "plane_widget": {"visible": False},
                "wheel_zooming": False,
                "camera_navigating": False,
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
        if state.selected in self.drafts:
            self.drafts[state.selected].setdefault("display_forms", {})[state.active_view] = {
                k: deepcopy(state[k]) for k in DISPLAY_KEYS
            }
        if values != self.baseline:
            draft = self.drafts.setdefault(
                state.selected, {"node": deepcopy(self.object()), "new": False}
            )
            draft["form"] = deepcopy(values)

    def select(self, identity):
        """树和场景拾取共用选择入口。"""
        if identity == self.server.state.selected:
            return
        self.stash()
        self.plane_release()
        self.scene.clear_preview()
        self.server.state.seed_preview = False
        self.server.state.selected = identity
        self.hydrate()
        self._sync_probe_pick_with_kind()
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
            state.range_mode = "custom" if color.get("range") else "automatic"
            remembered = self._parse_limits(*limits) if color.get("range") else None
            if remembered:
                self._remembered_ranges[self._range_memory_key()] = remembered
            state.opacity = style.get("opacity", 1)
            state.display_mode = style.get("mode", "surface")
            lic = style.get("lic") or {}
            state.lic_steps = lic.get("number_of_steps", 40)
            state.lic_step_size = lic.get("step_size", 0.25)
            state.lic_enhanced = lic.get("enhanced_lic", True)
            state.lic_contrast = lic.get("enhance_contrast", "both")
            state.lic_color_mode = lic.get("color_mode", "blend")
            state.lic_intensity = lic.get("intensity", 0.8)
            state.lighting = style.get("lighting", True)
            state.solid_color = self._rgb_to_hex(style.get("color", [0.8, 0.83, 0.9]))
            state.line_width = style.get("line_width", 1)
            stream = style.get("streamline") if isinstance(style.get("streamline"), dict) else {}
            state.streamline_shape = stream.get("shape", "line")
            state.streamline_thickness = stream.get("thickness", 1)
            state.streamline_sides = stream.get("sides", 8)
            self._fill_legend_from_color(color)
            state.plane_origin = ",".join(map(str, p.get("origin", [0, 0, 0])))
            state.plane_normal = ",".join(map(str, p.get("normal", [1, 0, 0])))
            state.inside_out = p.get("inside_out", False)
            state.crinkle_slice = p.get("crinkle", kind == "slice")
            state.triangulate_slice = p.get("triangulate", False)
            state.compute_field = field_key(p.get("field", {}))
            state.compute_component = p.get("field", {}).get("component", "magnitude")
            state.iso_values = ",".join(map(str, p.get("values", [0])))
            try:
                state.iso_slider = float(str(state.iso_values).split(",")[0])
            except (TypeError, ValueError):
                state.iso_slider = 0
            levels = p.get("levels") or {}
            state.level_mode = (
                "automatic"
                if levels or (kind == "contour" and not p.get("values"))
                else "custom"
            )
            state.level_count = levels.get("count", 10)
            state.level_min, state.level_max = levels.get("range") or ["", ""]
            state.plane_visible = layer.get("helpers", {}).get("plane_visible", True)
            state.seeds_visible = layer.get("helpers", {}).get("seeds_visible", True)
            shape = p.get("shape", {})
            state.glyph_shape = shape.get("type", "arrow")
            stored_scale = p.get("scale_mode", "vector")
            state.glyph_scale_mode = "constant" if stored_scale == "constant" else "quantity"
            if stored_scale == "scalar":
                state.glyph_scale_field = field_key(p.get("scale_field", {}))
            elif stored_scale == "vector":
                state.glyph_scale_field = field_key(p.get("field", {}))
            else:
                state.glyph_scale_field = field_key(p.get("scale_field", {}))
            state.glyph_sampling = p.get("sampling", {}).get("mode", "nodes")
            state.glyph_spacing = p.get("sampling", {}).get("spacing", 0.1)
            state.vector_scale = p.get("scale", 0.1)
            state.vector_stride = p.get("stride", 10)
            defaults = {}
            if kind == "streamline" and not p:
                source = self.scene.datasets.get((node or {}).get("input"))
                if source is not None:
                    from modules.visEngine import seed_defaults

                    defaults = seed_defaults(source.GetBounds())
            state.seed_start = ",".join(
                map(str, p.get("seed_start", defaults.get("seed_start", [0, 0, 0])))
            )
            state.seed_end = ",".join(
                map(str, p.get("seed_end", defaults.get("seed_end", [0, 1, 0])))
            )
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
            state.line_start = ",".join(
                map(str, p.get("point1", p.get("seed_start", [0, 0, 0])))
            )
            state.line_end = ",".join(map(str, p.get("point2", p.get("seed_end", [1, 0, 0]))))
            state.line_resolution = p.get("resolution", 1000)
            state.line_fields = p.get("fields") or []
            chart = (node or {}).get("chart") or {}
            view_chart = (
                next(
                    (item.get("chart") or {} for item in self.scene.spec.get("views", []) if item["id"] == state.active_view),
                    {},
                )
                if hasattr(self, "scene")
                else {}
            )
            state.chart_x_array = (
                view_chart.get("x_array") or chart.get("x_array") or "arc_length"
            )
            state.chart_y_arrays = list(
                view_chart.get("y_arrays") or chart.get("y_arrays") or []
            )
            state.probe_fields = (node or {}).get("fields", [])
            if state.selected in self.drafts and "form" in self.drafts[state.selected]:
                state.update(self.drafts[state.selected]["form"])
            if state.selected in self.drafts:
                state.update(
                    self.drafts[state.selected].get("display_forms", {}).get(state.active_view, {})
                )
            for key in (
                "plane_origin",
                "plane_normal",
                "seed_start",
                "seed_end",
                "seed_center",
                "seed_origin",
                "seed_normal",
                "probe_position",
                "line_start",
                "line_end",
            ):
                values = str(state[key]).split(",")
                for index in range(3):
                    state[f"{key}_{index}"] = values[index] if index < len(values) else "0"
            self.baseline = {k: deepcopy(state[k]) for k in PARAM_KEYS}
            state.pending = state.selected in self.drafts
            state.can_preview_seeds = kind == "streamline" and bool(
                self.drafts.get(state.selected, {}).get("new")
            )

    def refresh(self, **kwargs):
        """公开元数据，树只包含来源和真实创建的对象。"""
        update_view = kwargs.get("update_view", True)
        state = self.server.state
        snap = self.scene.snapshot()
        spec = snap["spec"]
        selected_layer = next(
            (
                l
                for l in spec["layers"]
                if l["input"] == state.selected and l["view"] == state.active_view
            ),
            {},
        )
        selected_actor = self.scene.actors.get(selected_layer.get("id"))
        state.automatic_range_text = "选择物理量并应用后显示"
        if selected_actor is not None and selected_layer.get("field"):
            state.automatic_range_text = " ～ ".join(
                f"{v:.6g}" for v in selected_actor.GetMapper().GetScalarRange()
            )
        background = next(
            (
                v.get("background", [0.14, 0.21, 0.29])
                for v in spec["views"]
                if v["id"] == state.active_view
            ),
            [0.14, 0.21, 0.29],
        )
        state.background_hex = "#" + "".join(f"{round(x * 255):02x}" for x in background)
        from ..modules.fieldVisualization.view import camera_spec

        # 普通 refresh 不得改写 render_cameras：添加平面后的悬停/选中刷新
        # 若带上服务端旧位姿，前端 syncCameras 会把轨道拉回固定视角。
        if kwargs.get("push_cameras") and not self._camera_interaction_active():
            state.render_cameras = [
                {
                    "layer": r.GetLayer(),
                    "viewport": list(r.GetViewport()),
                    "camera": camera_spec(r.GetActiveCamera()),
                    "clipping_range": list(r.GetActiveCamera().GetClippingRange()),
                    "view_angle": r.GetActiveCamera().GetViewAngle(),
                    "legend_styles": [
                        getattr(a, "_vis_style", {})
                        for a in r.GetViewProps()
                        if a.IsA("vtkScalarBarActor") and a.GetVisibility()
                    ],
                }
                for r in self.scene.renderers + self.scene.decorations
            ]
        roots, nodes = self._tree_payload(spec)
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
            state.scale_field_items = [
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
            state.can_lic = any(
                f["components"] == 3 and f.get("association") == "point" for f in fields
            )
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
            # 单位不一致只提示，不把联动开关打回去。
            state.link_notice = snap.get("camera_link_notice") or ""
            view = next(v for v in spec["views"] if v["id"] == state.active_view)
            state.axes = view.get("axes", True)
            state.shadows = view.get("shadows", False)
            import sys

            state.can_shadow = sys.platform == "linux" and spec.get("renderer") == "remote"
            self.sync_view_widget()
            self._fill_iso_limits()
            if state.kind == "plot_over_line":
                view = next((item for item in spec["views"] if item["id"] == state.active_view), None)
                if view is not None and view.get("type") == "line_chart":
                    bound = dict(view.get("chart") or {})
                    bound["source"] = state.selected
                    view["chart"] = bound
                if state.selected not in self.drafts:
                    mesh = self.scene.datasets.get(state.selected)
                    rows = getattr(mesh, "_vis_line_rows", None) if mesh is not None else None
                    if rows:
                        self.show_line_rows(rows)
                        state.view_frames = self.overlay_frames()
            # 快照已列出命名面；再调一次会在相机回写路径上重复读盘。
            state.seed_surface_items = [
                item
                for item in snap.get("seed_surfaces", [])
                if item.get("value") != f"object:{state.selected}"
            ]
            state.plane_widget = self.plane_widget_state()
            if state.kind == "probe":
                self.show_rows([snap.get("probes", {}).get(state.selected, {})])
        self.scene.show_selection(state.selected, state.active_view)
        self.sync_plane_widget()
        self.sync_preview(push=False)
        # 首次创建平面附件必须同步；同一草稿的重复选择由 begin 提前返回。
        if update_view and self.view:
            self._push_scene_view(push_cameras=bool(kwargs.get("push_cameras")))

    def descendants(self, identity):
        """委托领域依赖遍历，UI 不复制删除规则。"""
        return self.object_controls.descendants(identity)

    def command(self, body):
        """失败保留画面并在工作台内反馈。"""
        try:
            self.server.state.busy = True
            result = self.scene.command(body)
            self.server.state.error = ""
            return result
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            self.server.state.error = self._format_scene_error(exc, body=body)
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
            if (
                item.get("new")
                and node.get("type", "probe") == kind
                and node.get("input") == parent
            ):
                state.selected = key
                self.hydrate()
                self.set_probe_pick(kind == "probe")
                return
        self.stash()
        identity = uuid4().hex
        node = {
            "id": identity,
            "name": f"{LABELS[kind]} {1 + sum(n.get('type', 'probe') == kind for n in self.scene.spec['pipeline'] + self.scene.spec['probes'])}",
            "input": parent,
        }
        if kind == "probe":
            mesh = self.scene.datasets.get(parent)
            bounds = mesh.GetBounds() if mesh is not None else [-1, 1] * 3
            node.update(
                position=[(bounds[2 * i] + bounds[2 * i + 1]) / 2 for i in range(3)], fields=[]
            )
        else:
            node.update(type=kind, parameters={})
            if kind in ("slice", "clip"):
                source = self.scene.datasets.get(parent)
                if source is not None:
                    bounds = source.GetBounds()
                    node["parameters"] = {
                        "origin": [(bounds[2 * i] + bounds[2 * i + 1]) / 2 for i in range(3)],
                        "normal": [1, 0, 0],
                        "crinkle": kind == "slice",
                        "triangulate": False,
                    }
            if kind == "plot_over_line":
                source = self.scene.datasets.get(parent)
                bounds = source.GetBounds() if source is not None else [-1, 1, 0, 0, 0, 0]
                mid_y = (bounds[2] + bounds[3]) / 2
                mid_z = (bounds[4] + bounds[5]) / 2
                node["parameters"] = {
                    "point1": [bounds[0], mid_y, mid_z],
                    "point2": [bounds[1], mid_y, mid_z],
                    "resolution": 1000,
                    "fields": [],
                }
        self.drafts[identity] = {"node": node, "new": True}
        state.selected = identity
        self.hydrate()
        self.refresh()
        if state.compute_items:
            state.compute_field = state.compute_items[0]["value"]
            if kind == "glyph" and not state.glyph_scale_field:
                state.glyph_scale_field = state.compute_field
        if kind == "isosurface":
            # refresh 时计算场还没写入，必须在预填场之后按真实标量重算滑条。
            self._fill_iso_limits(follow_field=True)
        self.set_probe_pick(kind == "probe")

    @staticmethod
    def xyz(value):
        """将坐标表单解析为恰好三个有限数值。"""
        import math

        values = [float(x) for x in str(value).split(",")]
        if len(values) != 3 or not all(math.isfinite(x) for x in values):
            raise ValueError("需要三个有限坐标")
        return values

    def _selected_layer(self):
        """当前对象在活动视图的显示层，没有则返回空。"""
        state = self.server.state
        return next(
            (
                layer
                for layer in self.scene.spec.get("layers", [])
                if layer["input"] == state.selected and layer["view"] == state.active_view
            ),
            None,
        )

    def _selected_mesh(self):
        """当前对象或其来源网格，供 LIC 方向回退。"""
        state = self.server.state
        return self.scene.datasets.get(state.selected) or self.scene.datasets.get(
            (self.object() or {}).get("id")
        )

    def _lic_vectors_declaration(self, mesh, layer=None, field=None):
        """当前 LIC 方向声明；缺键时从着色场或网格点向量回退。"""
        from modules.visPhysField.rendering import resolve_lic_vectors

        array = resolve_lic_vectors(
            mesh,
            {
                "field": (layer or {}).get("field") if field is None else field,
                "style": (layer or {}).get("style") or {},
            },
        )
        if array is None:
            return None
        return {"name": array.GetName(), "association": "point"}

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

    def _glyph_scale_declaration(self, state):
        """界面两档映射为内部固定 / 矢量模长 / 标量绝对值。"""
        if state.glyph_scale_mode == "constant":
            return "constant", None
        if not state.glyph_scale_field:
            raise ValueError("请选择大小物理量")
        scale_field = self.field(state.glyph_scale_field, "magnitude")
        compute = self.field(state.compute_field, state.compute_component)
        if (
            scale_field["name"] == compute["name"]
            and scale_field.get("association", "point") == compute.get("association", "point")
        ):
            return "vector", None
        return "scalar", scale_field

    @staticmethod
    def _hex_to_rgb(value):
        """把 #RRGGBB 转成 0–1 分量，纯色显示与背景共用同一格式。"""
        text = str(value or "").strip()
        if len(text) == 7 and text.startswith("#"):
            try:
                return [int(text[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            except ValueError:
                pass
        raise ValueError("invalid_solid_color")

    @staticmethod
    def _rgb_to_hex(rgb):
        """把 0–1 颜色写成 #RRGGBB，缺省保持浅灰蓝。"""
        values = list(rgb or [0.8, 0.83, 0.9])
        if len(values) != 3:
            values = [0.8, 0.83, 0.9]
        return "#" + "".join(f"{max(0, min(255, round(float(x) * 255))):02x}" for x in values)

    def _range_memory_key(self):
        """自定义范围按对象、视图和当前着色物理量分别记忆。"""
        state = self.server.state
        return (state.selected, state.active_view, state.coloring or "", str(state.component))

    @staticmethod
    def _parse_limits(low, high):
        """合法自定义范围须为有限且下限不大于上限。"""
        try:
            limits = [float(low), float(high)]
        except (TypeError, ValueError):
            return None
        if not all(math.isfinite(v) for v in limits) or limits[0] > limits[1]:
            return None
        return limits

    @staticmethod
    def _format_limit(value):
        """表单回填与自动范围摘要使用同一精度。"""
        return f"{float(value):.6g}"

    def _remember_range(self, limits=None):
        """应用成功后记下本次自定义，改回自动也不删。"""
        parsed = limits or self._parse_limits(
            self.server.state.range_min, self.server.state.range_max
        )
        if parsed:
            self._remembered_ranges[self._range_memory_key()] = parsed

    def _automatic_limits(self):
        """当前着色物理量的数据最小、最大，不是已应用的自定义显示范围。"""
        state = self.server.state
        if not state.coloring:
            return None
        field = self.field(state.coloring, state.component)
        layer = next(
            (
                item
                for item in self.scene.spec["layers"]
                if item["input"] == state.selected and item["view"] == state.active_view
            ),
            {},
        )
        displayed = layer.get("field") or {}
        same = (
            displayed.get("name") == field["name"]
            and displayed.get("association", "point") == field["association"]
            and str(displayed.get("component", "magnitude")) == str(field["component"])
        )
        actor = self.scene.actors.get(layer.get("id"))
        mesh = actor.GetMapper().GetInput() if actor is not None else None
        if mesh is not None and same:
            data = mesh.GetCellData() if field["association"] == "cell" else mesh.GetPointData()
            array = data.GetArray("__vis_scalar")
            if array is not None:
                limits = list(array.GetRange())
                if all(math.isfinite(v) for v in limits) and limits[0] < limits[1]:
                    return limits
        node = self.object() or {}
        source = self.scene.datasets.get(state.selected) or self.scene.datasets.get(node.get("id"))
        if source is None and mesh is not None:
            source = mesh
        if source is None:
            return None
        from ..modules.fieldVisualization.scalarCloud import prepare_scalar

        prepared = prepare_scalar(source, field)
        array = prepared.GetPointData().GetArray("__vis_scalar") or prepared.GetCellData().GetArray(
            "__vis_scalar"
        )
        if array is None:
            return None
        limits = list(array.GetRange())
        if not all(math.isfinite(v) for v in limits) or limits[0] >= limits[1]:
            return None
        return limits

    def _fill_custom_range(self, *, force=False):
        """切到自定义时预填记忆值，没有记忆则用当前自动最小、最大。"""
        state = self.server.state
        if not force and self._parse_limits(state.range_min, state.range_max):
            return
        limits = self._remembered_ranges.get(self._range_memory_key()) or self._automatic_limits()
        if limits is None:
            if force:
                state.range_min, state.range_max = "", ""
            return
        state.range_min = self._format_limit(limits[0])
        state.range_max = self._format_limit(limits[1])

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
        previous = deepcopy(self.scene.spec)
        entering_lic = False
        try:
            p = {}
            kind = node.get("type", "probe")
            if kind in ("slice", "clip"):
                p.update(
                    origin=self.xyz(state.plane_origin),
                    normal=self.xyz(state.plane_normal),
                    inside_out=state.inside_out,
                    crinkle=bool(state.crinkle_slice),
                    triangulate=bool(state.triangulate_slice) if kind == "slice" else False,
                )
            if kind in ("glyph", "streamline", "isosurface", "contour"):
                p["field"] = self.field(state.compute_field, state.compute_component)
            if kind == "contour":
                limits = (
                    None
                    if state.level_min == "" and state.level_max == ""
                    else [float(state.level_min), float(state.level_max)]
                )
                p["levels"] = {
                    "mode": "automatic",
                    "count": int(state.level_count),
                    "range": limits,
                }
            elif kind == "isosurface":
                p["values"] = [float(x) for x in state.iso_values.split(",")]
            if kind == "glyph":
                scale_mode, scale_field = self._glyph_scale_declaration(state)
                p.update(
                    scale=float(state.vector_scale),
                    stride=int(state.vector_stride),
                    shape={"type": state.glyph_shape},
                    scale_mode=scale_mode,
                    sampling={
                        "mode": state.glyph_sampling,
                        **(
                            {"spacing": float(state.glyph_spacing)}
                            if state.glyph_sampling == "spatial"
                            else {}
                        ),
                    },
                )
                if scale_field is not None:
                    p["scale_field"] = scale_field
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
            if kind == "plot_over_line":
                p.update(
                    point1=self.xyz(state.line_start),
                    point2=self.xyz(state.line_end),
                    resolution=int(state.line_resolution),
                    fields=[],
                )
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
                body.update(type=kind, parameters=p, display=self.display_settings())
                if kind == "plot_over_line":
                    body["chart"] = {
                        "x_array": state.chart_x_array or "arc_length",
                        "y_arrays": list(state.chart_y_arrays or []),
                    }
                if new and kind == "isosurface" and not state.coloring:
                    body["display"]["field"] = deepcopy(p["field"])
            if kind == "surface":
                body = {
                    "operation": "display",
                    "id": node["id"],
                    "view": state.active_view,
                    **self.display_settings(),
                }
            entering_lic = state.display_mode == "surface_lic"
            if entering_lic:
                self._hold_remote_handoff()
            if self.command(body) is None:
                if entering_lic:
                    self._restore_view_mode(previous)
                return False
            finished = self.drafts.pop(node["id"], {})
            remaining = finished.get("display_forms", {})
            remaining.pop(state.active_view, None)
            if remaining:
                self.drafts[node["id"]] = {
                    "node": deepcopy(self.object()),
                    "new": False,
                    "display_forms": remaining,
                }
            self.scene.clear_preview()
            state.seed_preview = False
            if state.range_mode == "custom":
                self._remember_range()
            self.hydrate()
            self.refresh()
            if kind == "probe":
                self.query()
            if kind == "plot_over_line":
                self.query_line()
                self.ensure_line_chart_view(node["id"])
            return True
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            if entering_lic or self.scene.uses_surface_lic():
                try:
                    self.scene.apply(previous)
                    self._restore_view_mode(previous)
                    self.hydrate()
                    self.refresh()
                except Exception:
                    pass
            state.error = self._format_scene_error(exc, lic=entering_lic)
            return False

    def mark_dirty(self, *_):
        """输入计算参数仅标记草稿，不触发 VTK。"""
        self.stash()
        self.server.state.pending = True

    def display_settings(self):
        """从同一对象表单构造显示声明，新建与即时更新共用。"""
        state = self.server.state
        color = {
            "preset": state.palette,
            "bands": int(state.bands),
            "legend": state.legend,
            "legend_style": self._legend_style_from_state(),
        }
        if state.range_mode == "custom":
            limits = [float(state.range_min), float(state.range_max)]
            if not all(math.isfinite(v) for v in limits) or limits[0] > limits[1]:
                raise ValueError("显示范围须为有限数值，且最小值不大于最大值")
            color["range"] = limits
        style = {
            "opacity": float(state.opacity),
            "mode": state.display_mode,
            "lighting": state.lighting,
        }
        if state.display_mode == "surface_lic":
            field = self.field(state.coloring, state.component) if state.coloring else {}
            vectors = self._lic_vectors_declaration(
                self._selected_mesh(), self._selected_layer() or {}, field
            )
            if vectors is None:
                raise ValueError("请选择三维点向量场才能使用 Surface LIC")
            style["lic"] = {
                "number_of_steps": int(state.lic_steps),
                "step_size": float(state.lic_step_size),
                "enhanced_lic": bool(state.lic_enhanced),
                "enhance_contrast": state.lic_contrast,
                "color_mode": state.lic_color_mode,
                "intensity": float(state.lic_intensity),
                "vectors": vectors,
            }
        if not state.coloring:
            style["color"] = self._hex_to_rgb(state.solid_color)
        if state.kind == "contour":
            style["line_width"] = float(state.line_width)
        if state.kind == "streamline":
            thickness = float(state.streamline_thickness)
            shape = state.streamline_shape or "line"
            style["streamline"] = {
                "shape": shape,
                "thickness": thickness,
                "sides": int(float(state.streamline_sides)),
            }
            if shape == "line":
                style["line_width"] = thickness
        return {
            "field": self.field(state.coloring, state.component) if state.coloring else None,
            "color": color,
            "style": style,
            "helpers": {
                "plane_visible": bool(state.plane_visible),
                **(
                    {"seeds_visible": bool(getattr(state, "seeds_visible", True))}
                    if state.kind == "streamline"
                    else {}
                ),
            },
        }

    def set_background(self, value):
        """背景属于当前视图，空场景也可直接设置。"""
        try:
            if len(value) != 7 or not value.startswith("#"):
                raise ValueError("背景颜色格式无效")
            rgb = [int(value[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            self.scene.command(
                {
                    "operation": "view_update",
                    "view": self.server.state.active_view,
                    "settings": {"background": rgb},
                }
            )
            self.refresh()
        except ValueError as exc:
            self.server.state.error = str(exc)

    def _legend_style_from_state(self):
        """当前表单里的色标样式，只描述选中对象。"""
        state = self.server.state
        return {
            "position": state.legend_position,
            "orientation": state.legend_orientation,
            "length": float(state.legend_length),
            "thickness": float(state.legend_thickness),
            "title_font_size": int(state.legend_title_size),
            "label_font_size": int(state.legend_label_size),
            "x": float(state.legend_x),
            "y": float(state.legend_y),
        }

    def _fill_legend_from_color(self, color):
        """按一层 color 声明回填色标表单。"""
        state = self.server.state
        state.legend = color.get("legend", True)
        legend = color.get("legend_style") or {}
        for key, name, default in [
            ("position", "position", "right"),
            ("orientation", "orientation", "vertical"),
            ("length", "length", 0.6),
            ("thickness", "thickness", 25),
            ("title_size", "title_font_size", 25),
            ("label_size", "label_font_size", 25),
            ("x", "x", 0.8),
            ("y", "y", 0.2),
        ]:
            state["legend_" + key] = legend.get(name, default)

    def prepare_legend(self, identity=None):
        """打开色标时按当前对象回填，不沿用上一对象的厚度和字号。"""
        state = self.server.state
        if identity is not None and identity != state.selected:
            return
        layer = self._selected_layer() or {}
        self._fill_legend_from_color(layer.get("color") or {})
        draft = (
            self.drafts.get(state.selected, {})
            .get("display_forms", {})
            .get(state.active_view, {})
        )
        for key in LEGEND_FORM_KEYS:
            if key in draft:
                state[key] = draft[key]

    def cancel_legend(self, identity=None):
        """放弃未应用的色标草稿，回到当前对象已提交的样式。"""
        state = self.server.state
        if identity is not None and identity != state.selected:
            return
        layer = self._selected_layer() or {}
        self._fill_legend_from_color(layer.get("color") or {})
        forms = (
            self.drafts.get(state.selected, {})
            .get("display_forms", {})
            .get(state.active_view)
        )
        if forms:
            for key in LEGEND_FORM_KEYS:
                forms.pop(key, None)

    def apply_legend(self, identity=None):
        """只把色标写入当前选中对象的活动视图，不提交其他显示草稿。"""
        state = self.server.state
        if identity is not None and identity != state.selected:
            return False
        if not state.selected or state.kind in ("", "probe"):
            return False
        layer = self._selected_layer()
        if layer is None:
            return False
        try:
            color = deepcopy(layer.get("color") or {})
            color["legend"] = bool(state.legend)
            color["legend_style"] = self._legend_style_from_state()
            self.scene.command(
                {
                    "operation": "display",
                    "id": state.selected,
                    "view": state.active_view,
                    "color": color,
                }
            )
        except Exception as exc:  # noqa: BLE001 - 色标失败须保留原层并说明。
            state.error = str(exc)
            return False
        forms = self.drafts.setdefault(
            state.selected, {"node": deepcopy(self.object()), "new": False}
        ).setdefault("display_forms", {}).setdefault(state.active_view, {})
        for key in LEGEND_FORM_KEYS:
            forms[key] = state[key]
        self.refresh()
        state.error = ""
        return True

    def edit_display(self, key, value, identity=None):
        """属性只编辑当前对象草稿，应用前保持正式画面不变。"""
        state = self.server.state
        if identity is not None and identity != state.selected:
            return
        if not self.object():
            return
        self.drafts.setdefault(state.selected, {"node": deepcopy(self.object()), "new": False})
        state[key] = value
        if key == "range_mode" and value == "custom":
            self._fill_custom_range()
        elif key in ("coloring", "component") and state.range_mode == "custom":
            self._fill_custom_range(force=True)
        self.stash()
        state.pending = True

    def set_display(self, key, value, identity=None):
        """事件显式传递新值，避免 Vue change 先于 v-model 同步。"""
        if identity is not None and identity != self.server.state.selected:
            return
        state = self.server.state
        if self.drafts.get(state.selected, {}).get("new"):
            state[key] = value
            self.stash()
            if key == "plane_visible":
                self.sync_plane_widget()
                self._push_visibility_view()
            return
        layer = next(
            (
                l
                for l in self.scene.spec["layers"]
                if l["input"] == state.selected and l["view"] == state.active_view
            ),
            None,
        )
        if layer is None:
            return
        # 快捷操作只修改一个已提交字段，绝不消费属性面板其余草稿。
        changes = {}
        if key == "coloring":
            component = (layer.get("field") or {}).get("component", "magnitude")
            changes["field"] = self.field(value, component) if value else None
            if (layer.get("style") or {}).get("mode") == "surface_lic":
                style = deepcopy(layer.get("style", {}))
                lic = dict(style.get("lic") or {})
                if not lic.get("vectors"):
                    declared = self._lic_vectors_declaration(
                        self._selected_mesh(), layer, changes["field"] or {}
                    )
                    if declared is None:
                        state.error = "请选择三维点向量场才能使用 Surface LIC"
                        return
                    lic["vectors"] = declared
                    style["lic"] = lic
                    changes["style"] = style
        elif key == "plane_visible":
            changes["helpers"] = {**layer.get("helpers", {}), "plane_visible": bool(value)}
        elif key == "seeds_visible":
            changes["helpers"] = {**layer.get("helpers", {}), "seeds_visible": bool(value)}
        elif key == "legend" or key.startswith("legend_"):
            color = deepcopy(layer.get("color", {}))
            if key == "legend":
                color["legend"] = bool(value)
            else:
                names = {
                    "legend_position": "position",
                    "legend_orientation": "orientation",
                    "legend_length": "length",
                    "legend_thickness": "thickness",
                    "legend_title_size": "title_font_size",
                    "legend_label_size": "label_font_size",
                    "legend_x": "x",
                    "legend_y": "y",
                }
                if key not in names:
                    return
                style = dict(color.get("legend_style", {}))
                if key in (
                    "legend_length",
                    "legend_thickness",
                    "legend_x",
                    "legend_y",
                ):
                    style[names[key]] = float(value)
                elif key in ("legend_title_size", "legend_label_size"):
                    style[names[key]] = int(value)
                else:
                    style[names[key]] = value
                color["legend_style"] = style
            changes["color"] = color
        elif key in (
            "opacity",
            "display_mode",
            "lighting",
            "solid_color",
            "line_width",
            "lic_steps",
            "lic_step_size",
            "lic_enhanced",
            "lic_contrast",
            "lic_color_mode",
            "lic_intensity",
        ):
            style = deepcopy(layer.get("style", {}))
            if key == "solid_color":
                style["color"] = self._hex_to_rgb(value)
            elif key == "line_width":
                style["line_width"] = float(value)
            elif key == "display_mode":
                if value == "surface_lic":
                    declared = self._lic_vectors_declaration(
                        self._selected_mesh(), {**layer, "style": style}
                    )
                    if declared is None:
                        state.error = "请选择三维点向量场才能使用 Surface LIC"
                        return
                    lic = dict(style.get("lic") or {})
                    lic["vectors"] = declared
                    style["lic"] = lic
                style["mode"] = value
            elif key.startswith("lic_"):
                lic = dict(style.get("lic") or {})
                names = {
                    "lic_steps": "number_of_steps",
                    "lic_step_size": "step_size",
                    "lic_enhanced": "enhanced_lic",
                    "lic_contrast": "enhance_contrast",
                    "lic_color_mode": "color_mode",
                    "lic_intensity": "intensity",
                }
                lic[names[key]] = (
                    int(value)
                    if key == "lic_steps"
                    else float(value)
                    if key in ("lic_step_size", "lic_intensity")
                    else bool(value)
                    if key == "lic_enhanced"
                    else value
                )
                style["lic"] = lic
            else:
                style[key] = value
            changes["style"] = style
        else:
            return
        previous = deepcopy(self.scene.spec)
        entering_lic = key == "display_mode" and value == "surface_lic"
        leaving_lic = key == "display_mode" and value != "surface_lic" and (
            (layer.get("style") or {}).get("mode") == "surface_lic"
        )
        try:
            if entering_lic or leaving_lic:
                self._hold_remote_handoff()
            self.scene.command(
                {"operation": "display", "id": state.selected, "view": state.active_view, **changes}
            )
            self._push_visibility_view()
            state[key] = value
            if state.selected in self.drafts:
                self.drafts[state.selected].setdefault("display_forms", {}).setdefault(
                    state.active_view, {}
                )[key] = value
            if key == "plane_visible":
                self.sync_plane_widget()
            self.sync_view_widget()
            self.refresh()
            state.error = ""
        except Exception as exc:  # noqa: BLE001 - UI 边界保留草稿并反馈推送错误。
            try:
                self.scene.apply(previous)
                self._restore_view_mode(previous)
                self.hydrate()
                self._push_visibility_view()
                self.refresh()
            except Exception as recovery:  # noqa: BLE001 - 恢复连接失败须明确告知。
                state.error = f"{self._format_scene_error(exc, lic=entering_lic)}；画面同步失败：{recovery}，请重新连接"
            else:
                state.error = self._format_scene_error(exc, lic=entering_lic)

    def set_parameter(self, key, value, identity=None):
        """计算参数按事件值写入草稿，应用时不读取过时表单。"""
        if identity is not None and identity != self.server.state.selected:
            return
        self.server.state[key] = value
        if key == "seed_type" and value == "surface" and not self.server.state.seed_surface:
            items = self.server.state.seed_surface_items or []
            if items:
                self.server.state.seed_surface = items[0]["value"]
        if key in ("compute_field", "compute_component"):
            self._fill_iso_limits(follow_field=True)
        self.mark_dirty()
        self.sync_preview()

    def set_coordinate(self, key, index, value, identity=None):
        """独立坐标输入合并到既有三分量草稿，保持配置与应用校验不变。"""
        if identity is not None and identity != self.server.state.selected:
            return
        values = str(self.server.state[key]).split(",")
        values += ["0"] * (3 - len(values))
        values[index] = str(value)
        self.set_parameter(key, ",".join(values))
        if key in ("plane_origin", "plane_normal"):
            try:
                self.sync_plane_widget()
            except ValueError as exc:
                self.server.state.error = str(exc)
                return
            self.server.state.error = ""
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

    def cancel_selected(self):
        """丢弃当前对象草稿并释放临时附件，不影响其他草稿。"""
        state = self.server.state
        node = self.object() or {}
        draft = self.drafts.pop(state.selected, None)
        if draft and draft.get("new"):
            state.selected = node.get("input", "")
        state.seed_preview = False
        self.scene.clear_preview()
        self.plane_release()
        self.hydrate()
        self._sync_probe_pick_with_kind()
        self.refresh()

    def toggle_seed_preview(self):
        """预览只生成种子附件，不执行积分；关闭时立刻撤下预览。"""
        self.server.state.seed_preview = not self.server.state.seed_preview
        if not self.server.state.seed_preview:
            self.scene.clear_preview()
            self._push_visibility_view()
            return
        self.sync_preview()

    def sync_preview(self, push=True):
        """候选几何来自当前草稿，非法输入保留上一次有效附件。"""
        state = self.server.state
        node = self.object() or {}
        try:
            if node.get("type") == "streamline" and state.seed_preview:
                from modules.visEngine import build_seed_source, seed_preview_mesh, snap_seed_points

                params = {"seed_type": state.seed_type, "seeds": int(state.seed_count)}
                for key in ("seed_start", "seed_end", "seed_center", "seed_origin", "seed_normal"):
                    params[key] = self.xyz(state[key])
                for key in ("seed_radius", "seed_width", "seed_height"):
                    params[key] = float(state[key])
                if state.seed_type == "surface":
                    params["seed_surface"] = self.parse_seed_surface(state.seed_surface)
                candidate = {**node, "parameters": params}
                seed_mesh = self.scene.resolve_seed_mesh(
                    candidate, self.scene.datasets, self.scene.spec
                )
                mesh = seed_preview_mesh(params, seed_mesh)
                samples = snap_seed_points(
                    build_seed_source(params, seed_mesh), self.scene.datasets[node["input"]]
                )
                self.scene.show_preview(mesh, state.active_view, samples=samples)
            elif "position" in node and state.selected in self.drafts:
                import vtk

                from ..rendering import pixel_scale

                position = self.xyz(state.probe_position)
                renderer = self.scene.renderers[
                    next(
                        i
                        for i, v in enumerate(self.scene.spec["views"])
                        if v["id"] == state.active_view
                    )
                ]
                sphere = vtk.vtkSphereSource()
                sphere.SetCenter(position)
                sphere.SetRadius(pixel_scale(renderer, position, 6))
                sphere.SetThetaResolution(20)
                sphere.SetPhiResolution(16)
                sphere.Update()
                self.scene.show_preview(sphere.GetOutput(), state.active_view, point=True)
                state.query_table = [{"field": "位置", "value": "位置未应用"}]
            else:
                self.scene.clear_preview()
            if push:
                self._push_visibility_view()
        except (ValueError, TypeError) as exc:
            state.error = str(exc)

    def helper_widget_kind(self):
        """切面平面；线段提取不提供拖动手柄。"""
        node = self.object() or {}
        draft = self.drafts.get(node.get("id"), {})
        kind = node.get("type")
        if kind in ("slice", "clip") and self.server.state.plane_visible:
            if not draft.get("new"):
                layer = next(
                    (
                        item
                        for item in self.scene.spec["layers"]
                        if item["input"] == node["id"]
                        and item["view"] == self.server.state.active_view
                    ),
                    None,
                )
                if not layer or not layer.get("visible", True):
                    return None
            return "plane"
        return None

    def plane_widget_state(self):
        """只交出切面/剖切手柄；流线与线段提取没有拖动手柄。"""
        node = self.object()
        kind = self.helper_widget_kind()
        if not node or kind != "plane":
            return {"visible": False}
        mesh = self.scene.datasets.get(node.get("input"))
        bounds = list(mesh.GetBounds()) if mesh is not None else [-1, 1, -1, 1, -1, 1]
        try:
            origin = self.xyz(self.server.state.plane_origin)
            normal = self.xyz(self.server.state.plane_normal)
        except ValueError:
            return {"visible": False}
        return {
            "visible": True,
            "origin": origin,
            "normal": normal,
            "bounds": bounds,
            "kind": "plane",
            "object": node["id"],
            "view": self.server.state.active_view,
        }

    def sync_plane_widget(self):
        """选中切面或草稿手柄时显示附件，其它对象撤下。"""
        state = self.plane_widget_state()
        if not state.get("visible"):
            self.server.state.plane_widget = state
            self.scene.clear_plane_widget()
            return
        self.scene.show_plane_widget(
            state["origin"],
            state["normal"],
            state["bounds"],
            self.server.state.active_view,
            handles=state.get("handles"),
        )
        state["hitGeometry"] = self.scene.plane_hit_geometry
        self.server.state.plane_widget = state

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
                w, h = self.scene.window.GetSize()
                ray = []
                for depth in (0, 1):
                    renderer.SetDisplayPoint(x * w, y * h, depth)
                    renderer.DisplayToWorld()
                    point = renderer.GetWorldPoint()
                    ray.append([v / point[3] for v in point[:3]])
                return ray
        return None

    def plane_press(
        self, x, y, width=None, height=None, identity=None, token=None, requested=None, view=None
    ):
        """按下先分类：命中切面手柄才拖平面，不转视角、不切开。"""
        if identity is not None and identity != self.server.state.selected:
            return
        if view is not None and view != self.server.state.active_view:
            return
        if not self.plane_widget_state().get("visible"):
            return
        ray = self.screen_ray(x, y, width, height)
        handle = self.scene.pick_plane_widget(ray) if ray else None
        if requested is not None and handle != requested:
            return
        self.server.state.plane_dragging = handle or ""
        self._plane_drag_start = ray if handle else None
        self._plane_drag_token = token
        self._plane_drag_object = self.server.state.selected
        self._plane_drag_view = self.server.state.active_view
        self._helper_kind = self.helper_widget_kind() if handle else None
        if self._helper_kind == "plane":
            self._plane_initial = (
                self.xyz(self.server.state.plane_origin),
                self.xyz(self.server.state.plane_normal),
            )
        else:
            self._plane_initial = None
        return handle

    def plane_move(self, x, y, width=None, height=None, identity=None, token=None):
        """拖动只改可视平面和草稿数字。"""
        if identity is not None and (
            identity != self.server.state.selected
            or token != getattr(self, "_plane_drag_token", None)
        ):
            return
        if (
            getattr(self, "_plane_drag_object", self.server.state.selected)
            != self.server.state.selected
            or getattr(self, "_plane_drag_view", self.server.state.active_view)
            != self.server.state.active_view
        ):
            return
        handle = self.server.state.plane_dragging
        if not handle or not self._plane_drag_start:
            return
        ray = self.screen_ray(x, y, width, height)
        if not handle or not self._plane_drag_start or not ray:
            return
        node = self.object() or {}
        kind = getattr(self, "_helper_kind", None) or self.helper_widget_kind()
        if kind != "plane" or not getattr(self, "_plane_initial", None):
            return
        result = self.scene.command(
            {
                "operation": "plane_drag",
                "handle": handle,
                "origin": self._plane_initial[0],
                "normal": self._plane_initial[1],
                "start": self._plane_drag_start,
                "end": ray,
                "input": node.get("input"),
                "view": self.server.state.active_view,
            }
        )
        origin, normal = result["origin"], result["normal"]
        for key, values in (("plane_origin", origin), ("plane_normal", normal)):
            text = ",".join(map(str, values))
            self.server.state[key] = text
            for index, value in enumerate(values):
                self.server.state[f"{key}_{index}"] = str(value)
        from modules.visEngine import HANDLE_COLORS

        for actor in self.scene.plane_widget_actors:
            name = actor._plane_handle
            actor.GetProperty().SetColor((1, 0.90, 0.35) if name == handle else HANDLE_COLORS[name])
        self.mark_dirty()
        self.sync_plane_widget()
        if self.view:
            self.view.update()

    def plane_hover(self, handle=None, identity=None):
        """高亮只改附件颜色；轨道进行中不刷新，刷新也不推相机位姿。"""
        if (
            identity != self.server.state.selected
            or self.server.state.plane_dragging
            or self._camera_interaction_active()
        ):
            return
        from modules.visEngine import HANDLE_COLORS

        for actor in self.scene.plane_widget_actors:
            name = actor._plane_handle
            actor.GetProperty().SetColor((1, 0.90, 0.35) if name == handle else HANDLE_COLORS[name])
        self._push_visibility_view()

    def camera_navigate(self, active=False):
        """轨道占用是防御：期间不发平面悬停。几何刷新本身不得夹带相机。"""
        if active and not self._remote_interaction_ready() and getattr(
            self.server.state, "use_remote_view", False
        ):
            return
        flag = bool(active)
        self.server.state.camera_navigating = flag
        self.server.state.wheel_zooming = flag

    def wheel_zoom(self, active=False):
        """兼容旧滚轮事件名，与旋转/平移共用轨道占用。"""
        self.camera_navigate(active)

    def _camera_interaction_active(self):
        """轨道或平面拖动进行中，服务端不得用旧相机覆盖客户端。"""
        state = self.server.state
        return bool(
            getattr(state, "camera_navigating", False)
            or getattr(state, "wheel_zooming", False)
            or getattr(state, "plane_dragging", "")
        )

    def _push_scene_view(self, push_cameras=False):
        """推几何；仅服务端主动改相机且用户未在轨道中时才带位姿。"""
        if not self.view:
            return
        if self.scene.spec.get("renderer") != "remote":
            from ..rendering import install_local_serializers

            install_local_serializers()
        if push_cameras and not self._camera_interaction_active():
            from ..rendering import camera_pose_push

            with camera_pose_push():
                self.view.update()
            return
        self.view.update()

    def plane_release(self, identity=None, token=None):
        """松开只结束拖动，仍须应用才切开。"""
        if token is not None and token != getattr(self, "_plane_drag_token", None):
            return
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
        previous = deepcopy(self.scene.spec)
        layer_id = next(
            (
                l["id"]
                for l in previous["layers"]
                if l["input"] == state.selected and l["view"] == state.active_view
            ),
            None,
        )
        try:
            color = {"preset": state.palette, "bands": int(state.bands), "legend": state.legend}
            if state.range_min != "" and state.range_max != "":
                color["range"] = [float(state.range_min), float(state.range_max)]
            entering_lic = state.display_mode == "surface_lic"
            if entering_lic:
                self._hold_remote_handoff()
            self.scene.command(
                {
                    "operation": "display",
                    "helpers": {"plane_visible": bool(state.plane_visible)},
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
            self.sync_view_widget()
            self._push_visibility_view()
            state.error = ""
        except Exception as exc:  # noqa: BLE001 - UI 边界返回具体错误并保留当前画面。
            try:
                self.scene.apply(previous)
                self._restore_view_mode(previous)
                if layer_id:
                    self.hydrate()
                self._push_visibility_view()
            except Exception as recovery:  # noqa: BLE001 - 连接失败不能伪装显示成功。
                state.error = f"{self._format_scene_error(exc, lic=state.display_mode == 'surface_lic')}；画面同步失败：{recovery}，请重新连接"
            else:
                state.error = self._format_scene_error(
                    exc, lic=state.display_mode == "surface_lic"
                )

    def visible(self, identity, enabled=None):
        """显隐仅作用于单对象当前视图；失败恢复旧画面，并向用户返回原因。"""
        return self.object_controls.visible(identity, enabled)

    def _sync_tree_visible(self, identities, enabled):
        """对象树眼睛只改标记，不重新画像数据集。"""
        return self.object_controls._sync_tree_visible(identities, enabled)

    def _push_visibility_view(self):
        """把已有 actor 显隐推到客户端，不走 snapshot/refresh。"""
        return self.object_controls._push_visibility_view()

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
            self.command(
                {
                    "operation": "probe_visibility",
                    "id": node["id"],
                    "view": self.server.state.active_view,
                    "label": bool(value),
                }
            )
        self._push_visibility_view()

    def view_select(self, identity):
        """兼容旧入口：点窗切活跃并刷新左侧眼睛。"""
        self.activate_view(identity)

    def activate_view(self, identity):
        """切换活动视图，只重填树眼睛和属性，不重读网格。"""
        identity = self._view_identity(identity)
        if identity is None or identity == self.server.state.active_view:
            return
        self.stash()
        self.server.state.active_view = identity
        self.hydrate()
        self._sync_tree_for_active_view()
        self.scene.show_selection(self.server.state.selected, identity)
        self.sync_plane_widget()
        self.sync_view_widget()
        self._push_visibility_view()

    def _view_identity(self, identity):
        """标签点击、折线图和指针事件都可能传入编号或事件对象。"""
        if isinstance(identity, dict):
            identity = identity.get("id", identity.get("view"))
        try:
            return int(identity)
        except (TypeError, ValueError):
            return None

    def _active_view_record(self):
        """当前活跃窗记录；缺省按三维渲染读取。"""
        return next(
            (
                item
                for item in self.scene.spec.get("views", [])
                if item["id"] == self.server.state.active_view
            ),
            {},
        )

    def _tree_payload(self, spec):
        """按活跃窗组装对象树；折线图只留下线段提取及其来源分组。"""
        state = self.server.state
        nodes = {
            s["id"]: {
                "id": s["id"],
                "name": s.get("name", s["id"]),
                "children": [],
                "source": True,
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
                "draft": self.drafts.get(n["id"], {}).get("new", False),
                "visible": visible,
                "kind": "probe" if "position" in n else n.get("type", ""),
            }
            nodes[n["id"]] = item
            nodes.get(n["input"], {}).get("children", roots).append(item)
        if self._active_view_record().get("type") == "line_chart":
            roots = self._keep_plot_over_line_tree(roots)
        return roots, nodes

    def _keep_plot_over_line_tree(self, nodes):
        """折线图窗不展示切面等三维对象，来源行仅在仍有线段提取时保留。"""
        kept = []
        for node in nodes or []:
            children = self._keep_plot_over_line_tree(node.get("children") or [])
            if node.get("kind") == "plot_over_line":
                item = dict(node)
                item["children"] = children
                kept.append(item)
            elif node.get("source") and children:
                item = dict(node)
                item["children"] = children
                kept.append(item)
            else:
                # 基础显示/切面等中间行不进折线图树，其子线段提取上提。
                kept.extend(children)
        return kept

    def _sync_tree_for_active_view(self):
        """切窗后只改树过滤和眼睛，不走 snapshot。"""
        spec = self.scene.spec
        roots, nodes = self._tree_payload(spec)
        state = self.server.state
        state.tree_nodes = roots
        state.tree_open = list(nodes)
        state.view_items = spec["views"]
        state.view_frames = self.overlay_frames()
        state.view_ids = [item["id"] for item in spec["views"]]

    def view_action(self, operation, direction="horizontal", view_type="render"):
        """布局变更不删除对象，最大化属于临时 UI 状态。"""
        state = self.server.state
        result = self.command(
            {
                "operation": operation,
                "view": state.active_view,
                "direction": direction,
                "view_type": view_type,
                "source": state.selected if state.kind == "plot_over_line" else "",
                "x_array": state.chart_x_array or "arc_length",
                "y_arrays": list(state.chart_y_arrays or []),
            }
        )
        if result:
            ids = [v["id"] for v in self.scene.spec["views"]]
            state.active_view = (
                ids[-1]
                if operation == "view_create"
                else (state.active_view if state.active_view in ids else ids[0])
            )
            self.hydrate()
            self.refresh(push_cameras=True)

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
            self.refresh(push_cameras=True)

    def _is_probe_object(self):
        """Probe 节点用 position 标识，没有 type 字段。"""
        node = self.object() or {}
        return "position" in node

    def _sync_probe_pick_with_kind(self):
        """离开 Probe 后必须关掉点选，避免开关显示与后台不一致。"""
        if not self._is_probe_object():
            self.set_probe_pick(False)

    def set_probe_pick(self, enabled):
        """Probe 子模式：开则点选出球，关则恢复轨道，不另立分析工具。"""
        enabled = bool(enabled) and self._is_probe_object()
        if enabled:
            self.mode("probe")
            return
        if self.server.state.interaction_mode == "probe":
            self.mode("rotate")
        else:
            self.server.state.probe_pick_enabled = False

    def toggle_probe_pick(self):
        """属性区点选开关：再点一次按当前真实状态翻转。"""
        self.set_probe_pick(not bool(self.server.state.probe_pick_enabled))

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
        self.server.state.probe_pick_enabled = value == "probe" and self._is_probe_object()
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
        frames = view_overlay_frames(
            self.scene.spec["layout"],
            self.scene.spec["views"],
            maximize=state.maximize,
            active=state.active_view,
        )
        for frame in frames:
            view = next(item for item in self.scene.spec["views"] if item["id"] == frame["id"])
            view_type = view.get("type", "render")
            frame["view_type"] = view_type if view_type in ("render", "line_chart") else "render"
            frame["chart_html"] = self.chart_markup(view) if frame["view_type"] == "line_chart" else ""
            frame["has_chart"] = bool(frame["chart_html"])
        return frames

    def maximize(self):
        """临时最大化，不修改保存布局。"""
        from modules.visTaskManage import layout_rectangles

        state = self.server.state
        state.maximize = not state.maximize
        rectangles = layout_rectangles(self.scene.spec["layout"])
        for i, r in enumerate(self.scene.renderers):
            identity = self.scene.spec["views"][i]["id"]
            is_chart = self.scene.spec["views"][i].get("type", "render") == "line_chart"
            r.SetDraw(
                not is_chart and (not state.maximize or identity == state.active_view)
            )
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
        active_view = self.server.state.active_view
        if apply:
            for identity in list(self.drafts):
                self.server.state.selected = identity
                views = list(self.drafts[identity].get("display_forms", {})) or [active_view]
                for view in views:
                    self.server.state.active_view = view
                    self.hydrate()
                    if not self.apply_selected():
                        return
        else:
            self.drafts.clear()
        self.server.state.active_view = active_view
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
        return self.object_controls.rename()

    def delete(self):
        """用户确认后级联移除对象，源文件保持不变。"""
        return self.object_controls.delete()

    def camera(self, direction=None):
        """相机命令只作用于活动视图及其联动组。"""
        return self.camera_controls.camera(direction)

    def view_setting(self, key, value):
        """视图级开关与对象属性独立保存。"""
        return self.camera_controls.view_setting(key, value)

    def link(self, value):
        """开启后全体窗口共用相机，不要求共同坐标空间。"""
        return self.camera_controls.link(value)

    def seek(self, value=None):
        """选择真实时间值，缺帧由场景报告。"""
        return self.session_controls.seek(value)

    def step(self, direction):
        """逐帧有界前进/后退。"""
        return self.session_controls.step(direction)

    def visibility(self, visible):
        """隐藏暂停当前时间，返回只刷新视图，不清空对象或草稿。"""
        return self.session_controls.visibility(visible)

    def pause(self):
        """使旧播放循环失效。"""
        return self.session_controls.pause()

    def stop(self):
        """停止并恢复第一时间步。"""
        return self.session_controls.stop()

    def play(self, direction=1):
        """事件循环串行更新，避免跨线程访问 VTK。"""
        return self.session_controls.play(direction)

    def query(self, operation="probe"):
        """查询选定 Probe 的当前数值或时间曲线。"""
        return self.export_controls.query(operation)

    def query_line(self):
        """按当前线段参数取样，供折线图视口和侧栏表使用。"""
        node = self.object() or {}
        if node.get("type") != "plot_over_line":
            return
        state = self.server.state
        result = self.command(
            {
                "operation": "plot_over_line",
                "input": node.get("input"),
                "point1": self.xyz(state.line_start),
                "point2": self.xyz(state.line_end),
                "resolution": int(state.line_resolution),
                "fields": list((node.get("parameters") or {}).get("fields") or []),
            }
        )
        if result:
            self.show_line_rows(result["rows"])
            self.sync_line_chart()

    def show_line_rows(self, rows):
        """线段提取表；折线主图在视口 Line Chart View。"""
        from ..modules.dataOverview.basicCharts import profile_curve
        from ..modules.dataOverview.lineChart import axis_choices, default_y_arrays

        items = []
        for row in rows:
            prefix = f"s={row.get('distance', 0):g} · "
            values = row.get("fields") or row.get("values") or {}
            items.append(
                {
                    "field": prefix + "状态",
                    "value": "有效" if row.get("valid") else "域外或来源不可用",
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
        state = self.server.state
        state.query_table = items
        state.query_curve = profile_curve(rows)
        state.chart_x_items, state.chart_y_items = axis_choices(rows)
        if not state.chart_y_arrays:
            state.chart_y_arrays = default_y_arrays(rows)
        self._store_chart_extraction(rows)

    def line_rows(self, identity=None):
        """已应用线段对象上的取样行。"""
        node = self.object(identity) or {}
        mesh = self.scene.datasets.get(node.get("id"))
        rows = getattr(mesh, "_vis_line_rows", None) if mesh is not None else None
        return list(rows or [])

    def chart_settings(self, view=None, node=None):
        """视口显示优先，缺轴时 X=弧长、Y=第一条标量。"""
        from ..modules.dataOverview.lineChart import default_y_arrays

        view = view or next(
            (item for item in self.scene.spec["views"] if item["id"] == self.server.state.active_view),
            {},
        )
        node = node or self.object() or {}
        chart = dict(node.get("chart") or {})
        chart.update(view.get("chart") or {})
        rows = self.line_rows(chart.get("source") or node.get("id"))
        x_array = chart.get("x_array") or self.server.state.chart_x_array or "arc_length"
        y_arrays = list(chart.get("y_arrays") or self.server.state.chart_y_arrays or [])
        if not y_arrays:
            y_arrays = default_y_arrays(rows)
        return x_array, y_arrays, rows, chart.get("source") or node.get("id")

    def chart_markup(self, view):
        """为指定折线图视口生成 SVG，没有取样时为空。"""
        from ..modules.dataOverview.lineChart import line_chart_markup

        if view.get("type", "render") != "line_chart":
            return ""
        source = (view.get("chart") or {}).get("source") or ""
        node = next(
            (item for item in self.scene.spec.get("pipeline", []) if item["id"] == source),
            self.object() if self.server.state.kind == "plot_over_line" else None,
        )
        x_array, y_arrays, rows, _ = self.chart_settings(view, node)
        title = (node or {}).get("name") or "Line Chart View"
        return line_chart_markup(rows, x_array, y_arrays, title=title)

    def _persist_chart_axes(self):
        """X/Y 是显示属性，写入对象与当前折线图视口，不重算取样。"""
        state = self.server.state
        node = self.object()
        if not node or node.get("type") != "plot_over_line":
            return
        chart = {
            "x_array": state.chart_x_array or "arc_length",
            "y_arrays": list(state.chart_y_arrays or []),
        }
        if self.drafts.get(node["id"]):
            self.drafts[node["id"]].setdefault("node", node)["chart"] = deepcopy(chart)
        stored = next(
            (item for item in self.scene.spec.get("pipeline", []) if item["id"] == node["id"]),
            None,
        )
        if stored is not None:
            stored["chart"] = deepcopy(chart)
        view = next(
            (item for item in self.scene.spec["views"] if item["id"] == state.active_view),
            None,
        )
        if view is not None and view.get("type") == "line_chart":
            bound = dict(view.get("chart") or {})
            bound.update(chart)
            bound["source"] = node["id"]
            view["chart"] = bound

    def set_chart_axis(self, key, value, identity=None):
        """当前视口是折线图时立即重画；不触发计算应用。"""
        if identity is not None and identity != self.server.state.selected:
            return
        self.server.state[key] = value
        self._persist_chart_axes()
        self.sync_line_chart()

    def ensure_line_chart_view(self, source):
        """应用 Plot Over Line 后出现 Line Chart View，对齐 ParaView 自动开图。"""
        state = self.server.state
        charts = [item for item in self.scene.spec["views"] if item.get("type") == "line_chart"]
        x_array = state.chart_x_array or "arc_length"
        y_arrays = list(state.chart_y_arrays or [])
        if charts:
            chart = charts[0]
            bound = dict(chart.get("chart") or {})
            bound.update({"source": source, "x_array": x_array, "y_arrays": y_arrays})
            chart["chart"] = bound
            self.view_select(chart["id"])
            return
        if len(self.scene.spec["views"]) >= 4:
            state.error = "已达四个窗口，请关闭一个后再新增折线图"
            return
        self.view_action("view_create", "horizontal", view_type="line_chart")

    def sync_line_chart(self):
        """刷新各折线图窗体标记，不重建三维场景。"""
        self.server.state.view_frames = self.overlay_frames()
        rows = self.line_rows()
        if rows:
            self._store_chart_extraction(rows)

    def _store_chart_extraction(self, rows):
        """给显式 CSV 导出准备当前图的列。"""
        from ..modules.dataOverview.lineChart import line_chart_table

        x_array, y_arrays, _, source = self.chart_settings()
        headers, body = line_chart_table(rows, x_array, y_arrays)
        self.scene.last_extraction = {
            "operation": "plot_over_line",
            "kind": "plot_over_line",
            "input": (self.object() or {}).get("input"),
            "source": source,
            "x_array": x_array,
            "y_arrays": y_arrays,
            "chart": {"headers": headers, "body": body},
        }

    def export_line_chart_csv(self, path=None):
        """导出当前折线图的 X + 所选 Y，可写文件供读回。"""
        from ..modules.dataOverview.lineChart import line_chart_csv_text, write_line_chart_csv

        x_array, y_arrays, rows, _ = self.chart_settings()
        if not y_arrays or not rows:
            raise ValueError("line_chart_empty")
        self._store_chart_extraction(rows)
        if path is None:
            return line_chart_csv_text(rows, x_array, y_arrays)
        return write_line_chart_csv(path, rows, x_array, y_arrays)

    def export_chart_view(self, identity=None):
        """视口内导出当前或指定折线图。"""
        if identity is not None:
            self.view_select(identity)
        self.prepare_line_chart_export()
        self.request("export_csv")

    def prepare_line_chart_export(self):
        """把当前图写入提取快照，供宿主 CSV 对话框下载。"""
        rows = self.line_rows()
        if not rows:
            self.query_line()
            rows = self.line_rows()
        if rows:
            self._store_chart_extraction(rows)

    def set_iso_slider(self, value):
        """滑条改第一个等值，手填可越界并原样保留。"""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return
        self._write_iso_value(number)
        self.mark_dirty()
        self.sync_preview()

    def _write_iso_value(self, number):
        """把第一个等值写成物理量数值，不改写成 0–1 比例。"""
        text = format(float(number), "g")
        self.server.state.iso_slider = float(number)
        parts = [part.strip() for part in str(self.server.state.iso_values or "").split(",") if part.strip()]
        if parts:
            parts[0] = text
        else:
            parts = [text]
        self.server.state.iso_values = ",".join(parts)

    def _set_iso_range_fallback(self, reason):
        """范围无效时用占位 0–1，并写明这不是物理量。"""
        state = self.server.state
        state.iso_field_min = 0
        state.iso_field_max = 1
        state.iso_range_text = "占位范围 0 – 1（不是物理量）"
        state.iso_range_hint = reason

    def _follow_iso_value(self, limits):
        """换场后当前等值跟随该场；已在新范围内的值保持。"""
        low, high = float(limits[0]), float(limits[1])
        try:
            current = float(str(self.server.state.iso_values).split(",")[0])
        except (TypeError, ValueError, IndexError):
            current = None
        if current is not None and math.isfinite(current) and low <= current <= high:
            self.server.state.iso_slider = current
            return
        self._write_iso_value(low if high == low else (low + high) / 2)

    def _fill_iso_limits(self, follow_field=False):
        """等值滑条范围取当前计算场在输入网格上的实际标量范围。"""
        state = self.server.state
        if state.kind != "isosurface":
            state.iso_field_min, state.iso_field_max = 0, 1
            state.iso_range_text = ""
            state.iso_range_hint = ""
            return
        if not state.compute_field:
            self._set_iso_range_fallback("尚未选择等值物理量，滑条暂用占位上下限，请选择场或手填等值")
            return
        node = self.object() or {}
        mesh = self.scene.datasets.get(node.get("input"))
        if mesh is None:
            self._set_iso_range_fallback("读不到输入网格，无法按物理量取范围，请手填等值")
            return
        try:
            from modules.visEngine import scalar_mesh

            field = self.field(state.compute_field, state.compute_component)
            prepared = scalar_mesh(mesh, field)
            array = prepared.GetPointData().GetArray("__vis_scalar") or prepared.GetCellData().GetArray(
                "__vis_scalar"
            )
            if array is None:
                self._set_iso_range_fallback("所选物理量没有可用标量，滑条暂用占位上下限，请手填等值")
                return
            limits = [float(v) for v in array.GetRange()]
            if len(limits) != 2 or not all(math.isfinite(v) for v in limits) or limits[0] > limits[1]:
                self._set_iso_range_fallback("所选物理量范围无效，滑条暂用占位上下限，请手填等值")
                return
            state.iso_field_min, state.iso_field_max = limits
            state.iso_range_text = f"当前场范围 {limits[0]:g} – {limits[1]:g}"
            state.iso_range_hint = ""
            if follow_field:
                self._follow_iso_value(limits)
            else:
                try:
                    state.iso_slider = float(str(state.iso_values).split(",")[0])
                except (TypeError, ValueError, IndexError):
                    pass
        except (ValueError, TypeError) as exc:
            self._set_iso_range_fallback(f"无法读取物理量范围：{exc}。滑条暂用占位上下限，请手填等值")

    def _format_scene_error(self, exc, body=None, *, lic=False):
        """LIC 建图或出第一帧失败只对人说无法生成，其它错误保持原文。"""
        text = str(exc)
        if text.startswith("无法生成 Surface LIC") or "请选择三维点向量场" in text:
            return text
        style = (body or {}).get("style") or {}
        want_lic = lic or style.get("mode") == "surface_lic" or (
            (body or {}).get("operation") == "display" and self.scene.uses_surface_lic()
        )
        if want_lic:
            return f"无法生成 Surface LIC：{exc}"
        return text

    def _remote_interaction_ready(self):
        """远程静帧未就绪时不接收拖转、滚轮或结束事件。"""
        state = self.server.state
        return bool(
            getattr(state, "use_remote_view", False) and getattr(state, "remote_ready", False)
        )

    def _bind_view_widget(self):
        """按当前远程开关绑定本地或远程挂件，不在这里打开交互。"""
        remote = bool(getattr(self.server.state, "use_remote_view", False))
        view = getattr(self, "remote_view", None) if remote else getattr(self, "local_view", None)
        if view is not None:
            self.view = view

    def _set_remote_mode(self, active, *, interactive):
        """切换窗口挂件；interactive 为假时只出静帧、不接远程手势。"""
        state = self.server.state
        enabled = bool(active)
        state.use_remote_view = enabled
        state.remote_ready = bool(enabled and interactive)
        state.remote_handoff = bool(enabled and not interactive)
        self._bind_view_widget()

    def _hold_remote_handoff(self):
        """建图或切窗期间先停远程交互，避免未登记视图吃到拖转。"""
        state = self.server.state
        persisted = self.scene.spec.get("renderer") == "remote"
        if persisted:
            state.remote_ready = False
            state.remote_handoff = True
            return
        state.use_remote_view = False
        state.remote_ready = False
        state.remote_handoff = True
        self._bind_view_widget()
        flush = getattr(state, "flush", None)
        if callable(flush):
            flush()

    def _restore_view_mode(self, spec):
        """失败回退时按上一份声明恢复窗口，不停留半套远程。"""
        persisted = (spec or {}).get("renderer") == "remote"
        self._set_remote_mode(persisted, interactive=persisted)

    def _present_remote_still(self):
        """切远程后先出静帧，成功才允许拖转。"""
        self._set_remote_mode(True, interactive=False)
        flush = getattr(self.server.state, "flush", None)
        if callable(flush):
            flush()
        if self.view is not None:
            self.view.update()
        self._set_remote_mode(True, interactive=True)

    def sync_view_widget(self):
        """按声明或 LIC 选择窗口；LIC 临时远程须已出静帧才可交互。"""
        if self.scene.spec.get("renderer") == "remote":
            self._set_remote_mode(True, interactive=True)
            return
        if not self.scene.uses_surface_lic():
            self._set_remote_mode(False, interactive=False)
            return
        state = self.server.state
        if getattr(state, "use_remote_view", False) and getattr(state, "remote_ready", False):
            self._bind_view_widget()
            return
        self._present_remote_still()

    def show_rows(self, rows):
        """展示可读字段表，保留域外与缺帧状态而不填零。"""
        return self.export_controls.show_rows(rows)

    def export_probe(self):
        """固定当前 Probe 输入与空间位置后进入显式 CSV 输出。"""
        return self.export_controls.export_probe()

    def remote_end(self, *_):
        """远程交互结束后刷新可导出的场景注记。"""
        if not self._remote_interaction_ready():
            return None
        return self.camera_controls.remote_end(*_)

    def resize(self, size):
        """容器尺寸变化只重定位注记，不刷新对象树、不重读网格。"""
        return self.camera_controls.resize(size)

    def camera_event(self, event):
        """交互结束只回写活动相机，不走整屏 refresh，避免再次读盘和推场景。"""
        if not self._remote_interaction_ready() and getattr(
            self.server.state, "use_remote_view", False
        ):
            return None
        return self.camera_controls.camera_event(event)

    def camera_changed(self, value, pointer):
        """回传实际相机，固定修订导出与屏幕视角一致。"""
        return self.camera_controls.camera_changed(value, pointer)

    def pick_screen(self, x, y, width=None, height=None):
        """按实际点击视口与浏览器比例构造射线，本地/远程使用同一实体求交。"""
        if getattr(self.server.state, "remote_handoff", False) or (
            getattr(self.server.state, "use_remote_view", False)
            and not getattr(self.server.state, "remote_ready", False)
        ):
            return
        if self.scene.spec.get("renderer") != "remote" and width and height:
            self.scene.window.SetSize(int(width), int(height))
        for i, r in enumerate(self.scene.renderers):
            x0, y0, x1, y1 = r.GetViewport()
            if x0 <= x <= x1 and y0 <= y <= y1:
                view = self.scene.spec["views"][i]
                self.view_select(view["id"])
                if view.get("type", "render") == "line_chart":
                    return
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
        picking_probe = mode == "probe" and bool(state.probe_pick_enabled) and self._is_probe_object()
        if mode != "select" and not picking_probe:
            return
        hit = selection[0] if isinstance(selection, list) and selection else selection
        if not isinstance(hit, dict) or not hit.get("ray"):
            return
        candidates = [
            l
            for l in self.scene.spec["layers"]
            if l["view"] == state.active_view and l.get("visible", True)
        ]
        if picking_probe:
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
                self.sync_preview()
