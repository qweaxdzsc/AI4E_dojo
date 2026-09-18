"""声明式场景装配；一次 Apply 成功后才替换现有视图。"""

import json
from collections import OrderedDict
from copy import deepcopy

import vtk

from modules.visDatasets import describe_physical, load_physical
from modules.visEngine import apply_paraview_light_kit, entity
from modules.visTaskManage import layout_rectangles, normalize_physical_spec, validate_file_spec


def default_spec(sources: list[dict]) -> dict:
    """构造无隐式对齐、无相机联动的初始工作台配置。"""
    return normalize_physical_spec(
        {
            "schema_version": 1,
            "kind": "phys_field",
            "sources": sources,
            "pipeline": [],
            "layers": [
                {"id": "layer-" + s["id"], "input": s["id"], "visible": True, "view": 0}
                for s in sources
            ],
            "views": [{"id": 0}],
            "link_groups": [],
            "time": {},
            "renderer": "local",
            "implementation": {"engine": "vtk", "schema": 1},
        }
    )


from .modules.fieldVisualization.view import camera_spec, set_camera


def camera_link_unit_notice(sources: list[dict]) -> str:
    """已声明坐标单位不一致时提示，不阻止全体窗口共用相机。"""
    units: set[str] = set()
    for source in sources:
        space = source.get("coordinate_space")
        if not isinstance(space, dict):
            continue
        unit = str(space.get("unit") or "").strip()
        if unit:
            units.add(unit)
    if len(units) > 1:
        return "相机已联动；来源单位不一致：" + "、".join(sorted(units))
    return ""


class Scene:
    """工作区独占 VTK 数据与渲染窗口，保存只返回配置。"""

    def __init__(self, bindings: list[dict], spec: dict):
        """创建独立管线；窗口只在渲染或明确导出时使用。"""
        self.bindings = bindings
        self.mesh_cache = OrderedDict()
        self.geometries = {}
        self.last_extraction = None
        self.filter_cache = {}
        self.decorations = []
        self.legends = {}
        self.renderer_pool = []
        self.camera_pool = []
        self.decoration_pool = []
        self.annotation_pool = []
        self.camera_observers = []
        self.window = vtk.vtkRenderWindow()
        self.window.SetOffScreenRendering(1)
        self.window.SetSize(1280, 720)
        self.window.SetMultiSamples(0)
        self.renderers = []
        self.datasets = {}
        self.spec = {}
        self.times = []
        self.missing = []
        self.seed_actors = {}
        self.plane_widget_actors = []
        self.plane_widget_handles = {}
        self.camera_link_notice = ""
        self.apply(spec)

    def apply(self, spec: dict) -> dict:
        """先完整验证和计算，再提交显示；无效 Apply 不破坏旧画面。"""
        spec = normalize_physical_spec(validate_file_spec(spec))
        if self.spec and self.spec.get("renderer", "local") != spec.get("renderer", "local"):
            raise ValueError("renderer_change_requires_new_session")
        views = spec.get("views") or [{"id": 0}]
        spec["views"] = views
        spec.setdefault("time", {})
        view_indices = {v["id"]: i for i, v in enumerate(views)}
        rectangles = layout_rectangles(spec["layout"])
        if spec.get("renderer", "local") not in ("local", "remote"):
            raise ValueError("invalid_renderer")
        datasets, times, missing = {}, set(), []
        from modules.dataAssets import resolve_external
        from modules.visDatasets import source_times

        declared_times = sorted(
            {
                t
                for source in spec["sources"]
                for t in source_times(resolve_external(source, self.bindings))
            }
        )
        if declared_times and spec["time"].get("value") is None:
            spec["time"]["value"] = declared_times[0]
        for source in spec["sources"]:
            try:
                from modules.dataAssets import resolve_external
                from modules.visDatasets import source_times as time_values

                binding = resolve_external(source, self.bindings)
                source_times = time_values(binding)
                times.update(source_times)
                selected_time = spec.get("time", {}).get("value")
                cache_key = json.dumps([source, selected_time], sort_keys=True)
                if cache_key in self.mesh_cache:
                    mesh = self.mesh_cache[cache_key]
                    self.mesh_cache.move_to_end(cache_key)
                else:
                    mesh, source_times = load_physical(source, self.bindings, selected_time)
                    from modules.visEngine import reuse_geometry

                    geometry_key = json.dumps(source, sort_keys=True)
                    self.geometries[geometry_key] = reuse_geometry(
                        mesh, self.geometries.get(geometry_key)
                    )
                    self.mesh_cache[cache_key] = mesh
                    while len(self.mesh_cache) > 8:
                        self.mesh_cache.popitem(last=False)
            except ValueError as exc:
                if str(exc) != "missing_time_frame":
                    raise
                missing.append(source["id"])
                continue
            datasets[source["id"]] = mesh
            times.update(source_times)
        staged_cache = {}
        for node in spec.get("pipeline", []):
            if node["id"] in datasets:
                raise ValueError("duplicate_pipeline_identity")
            if node["input"] in missing:
                missing.append(node["id"])
                continue
            if node["input"] not in datasets:
                raise ValueError("pipeline_input_missing_or_cycle")
            from .modules.fieldVisualization.cutAnalysis import execute_analysis
            from .modules.fieldVisualization.vectorField import execute_vector

            operation = execute_vector if node["type"] == "glyph" else execute_analysis
            mesh = datasets[node["input"]]
            seed_mesh = self.resolve_seed_mesh(node, datasets, spec)
            # 基础显示保留完整体网格；只有显式等高线在其表面提取。
            key = (
                id(mesh),
                id(seed_mesh) if seed_mesh is not None else None,
                json.dumps([node["type"], node.get("parameters", {})], sort_keys=True),
            )
            cached = self.filter_cache.get(node["id"])
            if node["type"] == "surface":
                result = mesh
            elif cached and cached[0] == key:
                result = cached[1]
            else:
                if node["type"] == "contour" and any(
                    n["id"] == node["input"] and n["type"] == "surface" for n in spec["pipeline"]
                ):
                    from modules.visEngine import apply_filter

                    mesh = apply_filter(mesh, {"type": "surface"})
                result = (
                    operation(mesh, node, seed_mesh)
                    if node["type"] != "glyph"
                    else operation(mesh, node)
                )
            datasets[node["id"]] = result
            staged_cache[node["id"]] = (key, result, mesh)
        renderers, actors = [], {}
        for i, view in enumerate(views):
            renderer = vtk.vtkRenderer()
            renderer.SetBackground(view.get("background", [0.14, 0.21, 0.29]))
            renderer.SetViewport(rectangles[view["id"]])
            renderers.append(renderer)
        layer_ids = set()
        for layer in spec.get("layers", []):
            if layer["id"] in layer_ids:
                raise ValueError("duplicate_layer_identity")
            layer_ids.add(layer["id"])
            if layer["input"] in missing:
                continue
            if layer["input"] not in datasets:
                raise ValueError("layer_input_missing")
            view_id = layer.get("view", views[0]["id"])
            if view_id not in view_indices:
                raise ValueError("layer_view_missing")
            view = view_indices[view_id]
            if views[view].get("type", "render") == "line_chart":
                continue
            actor, legend = self.build_display(datasets[layer["input"]], layer)
            renderers[view].AddActor(actor)
            if legend:
                renderers[view].AddViewProp(legend)
            actors[layer["id"]] = actor
        for i, renderer in enumerate(renderers):
            renderer.ResetCamera()
            if not views[i].get("camera"):
                camera = renderer.GetActiveCamera()
                focal = camera.GetFocalPoint()
                distance = camera.GetDistance()
                camera.SetPosition([focal[j] + distance for j in range(3)])
                camera.SetViewUp(0, 0, 1)
                renderer.ResetCamera()
            if views[i].get("camera"):
                set_camera(renderer.GetActiveCamera(), views[i]["camera"])
            if views[i].get("shadows"):
                if spec.get("renderer") != "remote":
                    raise ValueError("shadows_require_remote_renderer")
                from modules.visEngine import enable_shadows

                enable_shadows(renderer)
        # 相机联动覆盖当前全部窗口；缺共同坐标空间 ID 不再拒绝，单位不一致只提示。
        self.camera_link_notice = ""
        for group in spec.get("link_groups", []):
            ids = group.get("views", [])
            if not ids or any(i not in view_indices for i in ids):
                raise ValueError("invalid_camera_link")
            notice = camera_link_unit_notice(spec.get("sources") or [])
            if notice:
                self.camera_link_notice = notice
            for i in ids[1:]:
                renderers[view_indices[i]].SetActiveCamera(
                    renderers[view_indices[ids[0]]].GetActiveCamera()
                )
        # Trame 对 renderer 注册释放回调；持续复用至工作区关闭，避免同步过程中析构。
        for camera, observer in self.camera_observers:
            camera.RemoveObserver(observer)
        self.camera_observers = []
        for old in self.renderers + self.decorations:
            self.window.RemoveRenderer(old)
        persistent = []
        for i, candidate in enumerate(renderers):
            if i == len(self.renderer_pool):
                self.renderer_pool.append(vtk.vtkRenderer())
                self.camera_pool.append(vtk.vtkCamera())
            renderer = self.renderer_pool[i]
            renderer.RemoveAllViewProps()
            renderer.SetViewport(candidate.GetViewport())
            renderer.SetBackground(candidate.GetBackground())
            # Trame 会把首视图的相机身份缓存到客户端，更新必须保留身份。
            self.camera_pool[i].DeepCopy(candidate.GetActiveCamera())
            renderer.SetActiveCamera(self.camera_pool[i])
            renderer.SetPass(candidate.GetPass())
            renderer.SetDraw(views[i].get("type", "render") != "line_chart")
            # 持久渲染器不拷贝候选灯；每次提交按 ParaView 默认套件补灯。
            apply_paraview_light_kit(renderer)
            props = candidate.GetViewProps()
            props.InitTraversal()
            for _ in range(props.GetNumberOfItems()):
                renderer.AddViewProp(props.GetNextProp())
            self.window.AddRenderer(renderer)
            persistent.append(renderer)
        renderers = persistent
        for group in spec.get("link_groups", []):
            camera = renderers[view_indices[group["views"][0]]].GetActiveCamera()
            for identity in group["views"][1:]:
                renderers[view_indices[identity]].SetActiveCamera(camera)
        self.renderers, self.actors, self.datasets = renderers, actors, datasets
        self.spec, self.times, self.missing = deepcopy(spec), sorted(times), missing
        self.filter_cache = staged_cache
        self.attach_streamline_seeds()
        self.add_annotations()
        return self.snapshot()

    @staticmethod
    def build_display(mesh, layer):
        """构建候选显示对象，数值处理由相应业务能力负责。"""
        from .rendering import build_display

        return build_display(mesh, layer)

    def add_annotations(self):
        """注记在真实渲染管线内构建，截图和视频共用。"""
        from .rendering import add_annotations

        # 恢复相机后旧近远裁剪面不再有效；联动相机覆盖所有可见视图的合并边界。
        groups = {}
        for renderer in self.renderers:
            bounds = renderer.ComputeVisiblePropBounds()
            if not renderer.GetDraw() or bounds[0] > bounds[1]:
                continue
            camera = renderer.GetActiveCamera()
            group = groups.setdefault(camera, {"renderer": renderer, "bounds": list(bounds)})
            for axis in range(3):
                group["bounds"][2 * axis] = min(group["bounds"][2 * axis], bounds[2 * axis])
                group["bounds"][2 * axis + 1] = max(
                    group["bounds"][2 * axis + 1], bounds[2 * axis + 1]
                )
        for group in groups.values():
            group["renderer"].ResetCameraClippingRange(group["bounds"])
        for camera, observer in self.camera_observers:
            camera.RemoveObserver(observer)
        self.camera_observers = []
        for renderer in self.decorations:
            self.window.RemoveRenderer(renderer)
        from .rendering import arrange_legends

        for renderer in self.renderers:
            arrange_legends(renderer)
        add_annotations(self)
        # 重排文字会清空注记层；恢复已有手柄，不能让窗口缩放使操作轴消失。
        for actor in self.plane_widget_actors:
            if actor._plane_handle.startswith(("axis_", "rotate_")):
                index = next(
                    (
                        i
                        for i, v in enumerate(self.spec["views"])
                        if v["id"] == getattr(self, "plane_view_id", None)
                    ),
                    None,
                )
                if index is not None:
                    self.annotation_pool[index].AddActor(actor)

        for actor in getattr(self, "preview_actors", []):
            for index, view in enumerate(self.spec["views"]):
                if view["id"] == getattr(self, "preview_view_id", None):
                    self.annotation_pool[index].AddActor(actor)

    def remove_objects(self, spec, affected):
        """验证删除声明后只撤下相关显示，保留窗口、相机及其他映射身份。"""
        spec = normalize_physical_spec(validate_file_spec(spec))
        for layer in self.spec["layers"]:
            if layer["input"] not in affected:
                continue
            renderer = self.renderers[
                next(i for i, v in enumerate(self.spec["views"]) if v["id"] == layer["view"])
            ]
            actor = self.actors.pop(layer["id"], None)
            if actor is not None:
                renderer.RemoveActor(actor)
                if getattr(actor, "_legend", None):
                    renderer.RemoveViewProp(actor._legend)
            for actor in self.seed_actors.pop(layer["id"], []):
                renderer.RemoveActor(actor)
        for key in list(self.probe_actors):
            if key[0] in affected:
                parts = self.probe_actors.pop(key)
                for actors in parts.values():
                    for actor in actors if isinstance(actors, list) else [actors]:
                        for renderer in self.decorations:
                            renderer.RemoveViewProp(actor)
                self.probe_rows.pop(key[0], None)
        self.clear_plane_widget()
        self.show_selection(None)
        self.clear_preview()
        self.datasets = {k: v for k, v in self.datasets.items() if k not in affected}
        self.filter_cache = {k: v for k, v in self.filter_cache.items() if k not in affected}
        self.missing = [k for k in self.missing if k not in affected]
        if any(source["id"] in affected for source in self.spec["sources"]):
            self.mesh_cache.clear()
            self.geometries.clear()
        if not spec["sources"]:
            self.times = []
        self.spec = spec
        from .rendering import arrange_legends

        for renderer in self.renderers:
            arrange_legends(renderer)
        return self.snapshot()

    def show_selection(self, identity, view_id=None):
        """以独立轮廓强调当前资产，绝不覆盖物理量映射。"""
        previous = getattr(self, "selection_actor", None)
        if previous is not None:
            for renderer in self.renderers:
                renderer.RemoveActor(previous)
        self.selection_actor = None
        layer = next(
            (
                l
                for l in self.spec["layers"]
                if l["input"] == identity and l["view"] == view_id and l.get("visible", True)
            ),
            None,
        )
        if not layer or identity not in self.datasets:
            return
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(self.datasets[identity])
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 0.81, 0.36)
        actor.GetProperty().SetLineWidth(2)
        actor.GetProperty().LightingOff()
        actor.SetUseBounds(False)
        actor.PickableOff()
        self.renderers[
            next(i for i, v in enumerate(self.spec["views"]) if v["id"] == view_id)
        ].AddActor(actor)
        self.selection_actor = actor

    def clear_preview(self):
        """释放会话临时附件；不影响正式种子或探针。"""
        for actor in getattr(self, "preview_actors", []):
            for renderer in self.renderers + self.decorations:
                renderer.RemoveActor(actor)
        self.preview_actors = []

    def show_preview(self, mesh, view_id, *, point=False, samples=None):
        """候选种子与探针共用不可拾取的轻量附件。"""
        from .rendering import build_seed_actor

        actor = build_seed_actor(mesh)
        if point:
            actor.GetProperty().SetRepresentationToSurface()
        actor.GetProperty().LightingOff()
        self.clear_preview()
        self.preview_view_id = view_id
        # 编辑候选位于注记层，体网格内部的种子仍清晰可见。
        renderer = self.annotation_pool[
            next(i for i, v in enumerate(self.spec["views"]) if v["id"] == view_id)
        ]
        renderer.AddActor(actor)
        self.preview_actors = [actor]
        if samples is not None:
            points = vtk.vtkPolyData()
            points.SetPoints(samples.GetPoints())
            vertices = vtk.vtkCellArray()
            for index in range(points.GetNumberOfPoints()):
                vertices.InsertNextCell(1)
                vertices.InsertCellPoint(index)
            points.SetVerts(vertices)
            dots = build_seed_actor(points)
            dots.GetProperty().LightingOff()
            renderer.AddActor(dots)
            self.preview_actors.append(dots)

    def update_display(self, spec, layer_id):
        """只更换显示数据和属性，不执行上游过滤器，不重置相机。"""
        spec = normalize_physical_spec(validate_file_spec(spec))
        layer = next(l for l in spec["layers"] if l["id"] == layer_id)
        if layer["input"] in self.missing:
            self.spec = spec
            return self.snapshot()
        old_layer = next((l for l in self.spec["layers"] if l["id"] == layer_id), {})
        actor = self.actors.get(layer_id)
        if (
            actor is not None
            and old_layer.get("field") == layer.get("field")
            and old_layer.get("color") == layer.get("color")
            and (old_layer.get("style") or {}).get("mode")
            == (layer.get("style") or {}).get("mode")
            and (old_layer.get("style") or {}).get("lic")
            == (layer.get("style") or {}).get("lic")
            and (old_layer.get("style") or {}).get("streamline")
            == (layer.get("style") or {}).get("streamline")
        ):
            from .rendering import display_property

            prop = display_property(layer.get("style", {}))
            actor.SetProperty(prop)
            self.spec = spec
            self.set_layer_visibility(layer_id, layer.get("visible", True))
            return self.snapshot()
        candidate, legend = self.build_display(self.datasets[layer["input"]], layer)
        renderer = self.renderers[
            next(i for i, v in enumerate(spec["views"]) if v["id"] == layer["view"])
        ]
        actor = self.actors.get(layer_id)
        if actor:
            if getattr(actor, "_legend", None):
                renderer.RemoveViewProp(actor._legend)
            if actor.GetMapper().GetClassName() != candidate.GetMapper().GetClassName():
                actor.SetMapper(candidate.GetMapper())
            else:
                # 保持客户端 mapper 身份，字段选择只替换其输入与映射设置。
                from .rendering import copy_display_mapper

                actor.GetMapper().ShallowCopy(candidate.GetMapper())
                actor.GetMapper().SetInputData(candidate.GetMapper().GetInput())
                copy_display_mapper(actor.GetMapper(), candidate.GetMapper(), layer)
            actor.SetProperty(candidate.GetProperty())
            actor.SetVisibility(candidate.GetVisibility())
            actor._legend = legend
        else:
            actor = candidate
            renderer.AddActor(actor)
            self.actors[layer_id] = actor
        if legend:
            renderer.AddViewProp(legend)
        from .rendering import arrange_legends

        arrange_legends(renderer)
        for seed in self.seed_actors.get(layer_id, []):
            seed.SetVisibility(candidate.GetVisibility())
        # 建图成功后才提交层声明；LIC 失败时调用方回退上一画面，不留半成品层。
        self.spec = spec
        return self.snapshot()

    def set_layer_visibility(self, layer_id, visible):
        """只改已有 actor 显隐，不重建映射、不过滤、不重读网格。"""
        layer = next(item for item in self.spec.get("layers", []) if item["id"] == layer_id)
        enabled = bool(visible)
        layer["visible"] = enabled
        actor = self.actors.get(layer_id)
        if actor is not None:
            actor.SetVisibility(enabled)
            legend = getattr(actor, "_legend", None)
            if legend is not None:
                legend.SetVisibility(enabled and layer.get("color", {}).get("legend", True))
        seeds_visible = layer.get("helpers", {}).get("seeds_visible", True)
        for seed in self.seed_actors.get(layer_id, []):
            seed.SetVisibility(enabled and bool(seeds_visible))
        return {"id": layer_id, "visible": enabled}

    def uses_surface_lic(self):
        """当前可见层是否含 Surface LIC，用于同一会话切换远程出图。"""
        return any(
            (layer.get("style") or {}).get("mode") == "surface_lic" and layer.get("visible", True)
            for layer in self.spec.get("layers", [])
        )

    def set_probe_visibility(self, identity, view_id, visible=None, label=None):
        """只更新所属视图的 Probe 附件，不重新采样或应用计算管线。"""
        probe = next(p for p in self.spec["probes"] if p["id"] == identity)
        if view_id not in [v["id"] for v in self.spec["views"]]:
            raise ValueError("view_missing")
        settings = probe.setdefault("views", {}).setdefault(str(view_id), {})
        if visible is not None:
            settings["visible"] = bool(visible)
        if label is not None:
            settings["label"] = bool(label)
        parts = self.probe_actors.get((identity, view_id), {})
        enabled = settings.get("visible", False)
        for actor in parts.get("marker", []):
            actor.SetVisibility(enabled)
        for actor in parts.get("labels", []):
            actor.SetVisibility(enabled and settings.get("label", True))
        return {"id": identity, "view": view_id, **settings}

    def root_source_id(self, spec, identity):
        """沿处理链回到原始来源，命名块仍从同一授权文件读取。"""
        nodes = {n["id"]: n for n in spec.get("pipeline", [])}
        current = identity
        while current in nodes:
            current = nodes[current]["input"]
        return current

    def resolve_seed_mesh(self, node, datasets, spec):
        """对象树表面或授权文件命名面；内核不自己读路径。"""
        params = node.get("parameters") or {}
        if node.get("type") != "streamline" or (params.get("seed_type") or "line") != "surface":
            return None
        seed = params.get("seed_surface") or {}
        kind = seed.get("kind")
        if kind == "object":
            mesh = datasets.get(seed.get("id"))
            if mesh is None:
                raise ValueError("invalid_seed_surface")
            return mesh
        if kind == "patch":
            from modules.visEngine import extract_named_region

            for candidate in (
                datasets.get(node["input"]),
                datasets.get(self.root_source_id(spec, node["input"])),
            ):
                if candidate is None:
                    continue
                try:
                    return extract_named_region(candidate, seed["name"])
                except ValueError:
                    continue
            raise ValueError("named_region_missing")
        if kind == "block":
            from pathlib import Path

            from ai4e_viz.inspect.mesh import read_mesh

            from modules.dataAssets import resolve_external

            source = next(
                s for s in spec["sources"] if s["id"] == self.root_source_id(spec, node["input"])
            )
            binding = resolve_external(source, self.bindings)
            return read_mesh(Path(binding["path"]), int(seed["index"]), source.get("reader"))
        raise ValueError("missing_seed_source")

    def attach_streamline_seeds(self):
        """已应用流线在同视图画种子，不参与适窗，不能点选。"""
        from modules.visEngine import seed_preview_mesh

        from .rendering import build_seed_actor

        self.seed_actors = {}
        self.clear_plane_widget()
        for layer in self.spec.get("layers", []):
            node = next(
                (n for n in self.spec.get("pipeline", []) if n["id"] == layer["input"]), None
            )
            if not node or node["type"] != "streamline":
                continue
            view = next(i for i, v in enumerate(self.spec["views"]) if v["id"] == layer["view"])
            preview = seed_preview_mesh(
                node.get("parameters", {}),
                self.resolve_seed_mesh(node, self.datasets, self.spec),
            )
            actor = build_seed_actor(preview)
            visible = layer.get("visible", True) and layer.get("helpers", {}).get(
                "seeds_visible", True
            )
            actor.SetVisibility(visible)
            self.renderers[view].AddActor(actor)
            self.seed_actors.setdefault(layer["id"], []).append(actor)

    def seed_surface_items(self, exclude=None):
        """属性下拉：对象树表面加文件命名块/文字分区。"""
        from modules.visDatasets import list_named_surfaces

        items = []
        for node in self.spec.get("pipeline", []):
            if node["id"] == exclude or node["type"] not in (
                "surface",
                "slice",
                "contour",
                "isosurface",
            ):
                continue
            mesh = self.datasets.get(node["id"])
            if mesh is None or mesh.GetNumberOfPoints() <= 0:
                continue
            dimension = describe_physical(mesh).get("dimension", 0)
            if dimension > 2:
                continue
            items.append({"text": f"{node['name']}（对象）", "value": f"object:{node['id']}"})
        seen = {item["value"] for item in items}
        for source in self.spec.get("sources", []):
            from modules.dataAssets import resolve_external

            try:
                binding = resolve_external(source, self.bindings)
            except Exception:  # noqa: BLE001, S112 - 缺绑定只少一项，不阻断其他表面。
                continue
            for item in list_named_surfaces(
                binding.get("path"),
                self.datasets.get(source["id"]),
                source.get("reader"),
            ):
                if item["value"] in seen:
                    continue
                items.append({"text": item["text"], "value": item["value"]})
                seen.add(item["value"])
        return items

    def show_plane_widget(self, origin, normal, bounds, view_id=None, handles=None):
        """选中切面或草稿种子/线段时挂手柄，不写配置、不计算。"""
        from modules.visEngine import plane_widget_geometry

        from .rendering import build_plane_handle_actor

        if not self.renderers:
            return
        view_id = self.spec["views"][0]["id"] if view_id is None else view_id
        renderer = self.renderers[
            next(i for i, v in enumerate(self.spec["views"]) if v["id"] == view_id)
        ]
        handles = handles if handles is not None else plane_widget_geometry(origin, normal, bounds)
        actors = [build_plane_handle_actor(mesh, name) for name, mesh in handles.items()]
        # 参数或构造失败时保留上次有效手柄，与正式切面结果一起继续可用。
        self.clear_plane_widget()
        self.plane_widget_handles = handles
        self.plane_view_id = view_id
        self.plane_hit_geometry = {}
        for name, mesh in handles.items():
            if not name.startswith(("axis_", "rotate_")):
                continue
            triangles = vtk.vtkTriangleFilter()
            triangles.SetInputData(mesh)
            triangles.Update()
            poly = triangles.GetOutput()
            values = []
            for index in range(poly.GetNumberOfCells()):
                cell = poly.GetCell(index)
                if cell.GetNumberOfPoints() == 3:
                    for j in range(3):
                        values.extend(poly.GetPoint(cell.GetPointId(j)))
            self.plane_hit_geometry[name] = values
        overlay = self.annotation_pool[
            next(i for i, v in enumerate(self.spec["views"]) if v["id"] == view_id)
        ]
        for actor in actors:
            # 手柄位于注记层，模型遮挡不会让用户看不到已命中的操作轴。
            (
                overlay if actor._plane_handle.startswith(("axis_", "rotate_")) else renderer
            ).AddActor(actor)
            self.plane_widget_actors.append(actor)

    def clear_plane_widget(self):
        """取消选中或重建场景时撤下平面附件。"""
        for actor in self.plane_widget_actors:
            for renderer in self.renderers + self.decorations:
                renderer.RemoveActor(actor)
        self.plane_widget_actors = []
        self.plane_widget_handles = {}

    def pick_plane_widget(self, ray):
        """命中手柄名称，未点到返回空。"""
        from modules.visEngine import pick_plane_handle

        if not self.plane_widget_handles:
            return None
        return pick_plane_handle(self.plane_widget_handles, ray)

    def snapshot(self) -> dict:
        """返回轻量配置与字段画像，绝不返回场数组。"""
        spec = deepcopy(self.spec)
        for i, renderer in enumerate(self.renderers):
            spec["views"][i]["camera"] = camera_spec(renderer.GetActiveCamera())
        return {
            "spec": spec,
            "datasets": {key: describe_physical(mesh) for key, mesh in self.datasets.items()},
            "times": self.times,
            "missing": self.missing,
            "extraction": self.last_extraction,
            "probes": getattr(self, "probe_rows", {}),
            "seed_surfaces": self.seed_surface_items(),
            "attachments": {
                "seeds": {
                    key: any(actor.GetVisibility() for actor in actors)
                    for key, actors in self.seed_actors.items()
                },
                "plane_widget": {
                    "visible": bool(self.plane_widget_actors),
                    "handles": sorted(self.plane_widget_handles),
                },
            },
            "camera_link_notice": self.camera_link_notice,
        }

    def command(self, command: dict) -> dict:
        """UI 和脚本共用命令入口。"""
        from .commands import execute

        result = execute(self, command)
        if result is not None:
            return result
        operation = command["operation"]
        if operation == "apply":
            return self.apply(command["spec"])
        if operation == "snapshot":
            return self.snapshot()
        if operation == "pick":
            from modules.visEngine import pick_ray

            return pick_ray(
                self.datasets[command["input"]], command["ray"], command.get("association", "cell")
            )
        if operation == "append_sources":
            before = self.bindings
            spec = self.snapshot()["spec"]
            self.bindings = before + command["bindings"]
            try:
                for source in command["sources"]:
                    spec["sources"].append(source)
                    base = "base-" + source["id"]
                    spec["pipeline"].append(
                        {
                            "id": base,
                            "name": "基础显示",
                            "type": "surface",
                            "input": source["id"],
                            "parameters": {},
                        }
                    )
                    spec["layers"].append(
                        {
                            "id": "layer-" + source["id"],
                            "input": base,
                            "view": spec["views"][0]["id"],
                            "visible": True,
                        }
                    )
                return self.apply(spec)
            except Exception:
                self.bindings = before
                raise
        if operation == "temporal":
            from .modules.dataExtraction.temporal import sample_history

            if command["input"] not in [s["id"] for s in self.spec["sources"]]:
                self.last_extraction = {
                    key: command[key] for key in ("operation", "input", "positions")
                }
                saved = self.snapshot()["spec"]
                rows = []
                try:
                    for time in self.times:
                        self.command({"operation": "time", "value": time})
                        if command["input"] in self.missing:
                            rows.extend(
                                {
                                    "position": p,
                                    "values": None,
                                    "fields": None,
                                    "valid": False,
                                    "status": "missing_frame",
                                    "time": time,
                                }
                                for p in command["positions"]
                            )
                        else:
                            rows.extend(
                                {**r, "time": time}
                                for r in self.command({**command, "operation": "probe"})["rows"]
                            )
                finally:
                    self.apply(saved)
                    self.last_extraction = {
                        key: command[key] for key in ("operation", "input", "positions")
                    }
                return {"rows": rows}
            source = next(s for s in self.spec["sources"] if s["id"] == command["input"])
            self.last_extraction = {
                key: command[key] for key in ("operation", "input", "positions")
            }
            return {"rows": sample_history(source, self.bindings, command["positions"])}
        if operation in ("probe", "entity"):
            mesh = self.datasets[command["input"]]
            if operation == "probe":
                from .modules.dataExtraction.spatial import sample_positions

                self.last_extraction = {
                    key: command[key] for key in ("operation", "input", "positions")
                }
                return {"rows": sample_positions(mesh, command["positions"])}
            return entity(mesh, command["association"], int(command["id"]))
        if operation == "time":
            spec = self.snapshot()["spec"]
            spec["time"]["value"] = float(command["value"])
            return self.apply(spec)
        if operation == "camera":
            renderer = self.renderers[
                next(
                    i
                    for i, v in enumerate(self.spec["views"])
                    if v["id"] == command.get("view", self.spec["views"][0]["id"])
                )
            ]
            camera = renderer.GetActiveCamera()
            if command.get("camera"):
                set_camera(camera, command["camera"])
            elif command.get("direction"):
                direction = command["direction"]
                vectors = {
                    "+x": (1, 0, 0),
                    "-x": (-1, 0, 0),
                    "+y": (0, 1, 0),
                    "-y": (0, -1, 0),
                    "+z": (0, 0, 1),
                    "-z": (0, 0, -1),
                    "iso": (1, 1, 1),
                }
                delta = vectors[direction]
                focal = camera.GetFocalPoint()
                distance = max(camera.GetDistance(), 1)
                camera.SetPosition([focal[i] + delta[i] * distance for i in range(3)])
                camera.SetViewUp(0, 0, 1) if direction.endswith(("x", "y")) else camera.SetViewUp(
                    0, 1, 0
                )
                renderer.ResetCamera()
            else:
                renderer.ResetCamera()
            self.add_annotations()
            return self.snapshot()
        raise ValueError("unknown_phys_command")

    def close(self) -> None:
        """释放窗口所属本地资源。"""
        self.window.Finalize()
