"""声明式场景装配；一次 Apply 成功后才替换现有视图。"""

import json
from collections import OrderedDict
from copy import deepcopy

import vtk

from modules.visDatasets import describe_physical, load_physical
from modules.visEngine import entity
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
                result = operation(mesh, node, seed_mesh) if node["type"] != "glyph" else operation(mesh, node)
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
        for group in spec.get("link_groups", []):
            ids = group.get("views", [])
            if not ids or any(i not in view_indices for i in ids):
                raise ValueError("invalid_camera_link")
            spaces = {s.get("coordinate_space") for s in spec["sources"]}
            same_source = (
                len(
                    {
                        json.dumps([s["ref"], s.get("block"), s.get("part")], sort_keys=True)
                        for s in spec["sources"]
                    }
                )
                == 1
            )
            if not same_source and (None in spaces or len(spaces) != 1):
                raise ValueError("camera_link_requires_common_coordinate_space")
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
            renderer.SetDraw(True)
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

    def update_display(self, spec, layer_id):
        """只更换显示数据和属性，不执行上游过滤器，不重置相机。"""
        spec = normalize_physical_spec(validate_file_spec(spec))
        layer = next(l for l in spec["layers"] if l["id"] == layer_id)
        if layer["input"] in self.missing:
            self.spec = spec
            return self.snapshot()
        candidate, legend = self.build_display(self.datasets[layer["input"]], layer)
        renderer = self.renderers[
            next(i for i, v in enumerate(spec["views"]) if v["id"] == layer["view"])
        ]
        actor = self.actors.get(layer_id)
        if actor:
            if getattr(actor, "_legend", None):
                renderer.RemoveViewProp(actor._legend)
            actor.SetMapper(candidate.GetMapper())
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
        for actor in self.seed_actors.get(layer_id, []):
            actor.SetVisibility(candidate.GetVisibility())
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
        for seed in self.seed_actors.get(layer_id, []):
            seed.SetVisibility(enabled)
        return {"id": layer_id, "visible": enabled}

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
            node = next((n for n in self.spec.get("pipeline", []) if n["id"] == layer["input"]), None)
            if not node or node["type"] != "streamline":
                continue
            view = next(i for i, v in enumerate(self.spec["views"]) if v["id"] == layer["view"])
            preview = seed_preview_mesh(
                node.get("parameters", {}),
                self.resolve_seed_mesh(node, self.datasets, self.spec),
            )
            actor = build_seed_actor(preview)
            actor.SetVisibility(layer.get("visible", True))
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
            except Exception:  # noqa: BLE001 - 缺绑定只少一项，不阻断其他表面。
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

    def show_plane_widget(self, origin, normal, bounds, view_id=None):
        """选中切面时挂可视平面，不写配置、不切开。"""
        from modules.visEngine import plane_widget_geometry

        from .rendering import build_plane_handle_actor

        self.clear_plane_widget()
        if not self.renderers:
            return
        view_id = self.spec["views"][0]["id"] if view_id is None else view_id
        renderer = self.renderers[
            next(i for i, v in enumerate(self.spec["views"]) if v["id"] == view_id)
        ]
        self.plane_widget_handles = plane_widget_geometry(origin, normal, bounds)
        for name, mesh in self.plane_widget_handles.items():
            actor = build_plane_handle_actor(mesh, name)
            renderer.AddActor(actor)
            self.plane_widget_actors.append(actor)

    def clear_plane_widget(self):
        """取消选中或重建场景时撤下平面附件。"""
        for actor in self.plane_widget_actors:
            for renderer in self.renderers:
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
