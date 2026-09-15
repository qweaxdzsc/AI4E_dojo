"""同一场景的显示对象和导出注记，保持计算字段与着色字段独立。"""

import math

import vtk

from .modules.fieldVisualization.colorMapping import build_color_mapping
from .modules.fieldVisualization.scalarCloud import prepare_scalar


def build_seed_actor(mesh):
    """流线种子附件：看得见、不参与适窗、不能点选。"""
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(mesh)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 0.75, 0.2)
    actor.GetProperty().SetOpacity(0.9)
    actor.GetProperty().SetLineWidth(2)
    only_points = mesh.GetNumberOfPolys() == 0 and mesh.GetNumberOfLines() == 0
    if only_points:
        actor.GetProperty().SetRepresentationToPoints()
        actor.GetProperty().SetPointSize(8)
        if hasattr(actor.GetProperty(), "SetRenderPointsAsSpheres"):
            actor.GetProperty().SetRenderPointsAsSpheres(True)
    else:
        actor.GetProperty().SetRepresentationToWireframe()
    actor.SetUseBounds(False)
    actor.PickableOff()
    return actor


def build_plane_handle_actor(mesh, name):
    """切面可视平面手柄，颜色区分轴、平面和旋转环。"""
    from modules.visEngine import HANDLE_COLORS

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mesh)
    mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(HANDLE_COLORS[name])
    actor.GetProperty().SetOpacity(0.35 if name == "plane" else 1)
    actor.GetProperty().SetLineWidth(3 if name.startswith("axis") or name == "rotate" else 1)
    actor.GetProperty().SetRepresentationToWireframe()
    if name == "plane":
        actor.GetProperty().SetRepresentationToSurface()
        actor.GetProperty().SetOpacity(0.22)
    actor.SetUseBounds(False)
    actor._plane_handle = name
    return actor


def build_display(mesh, layer):
    """完整验证显示参数后创建候选显示对象，失败不影响旧画面。"""
    mapper = vtk.vtkDataSetMapper()
    mapper.ScalarVisibilityOff()
    field = layer.get("field")
    legend = None
    if field:
        mesh = prepare_scalar(mesh, field)
        if field.get("association", "point") == "cell":
            mapper.SetScalarModeToUseCellFieldData()
            data = mesh.GetCellData()
        else:
            mapper.SetScalarModeToUsePointFieldData()
            data = mesh.GetPointData()
        mapper.SelectColorArray("__vis_scalar")
        mapper.ScalarVisibilityOn()
        lut, limits, bands = build_color_mapping(
            data.GetArray("__vis_scalar"), layer.get("color", {})
        )
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(limits)
        if layer.get("color", {}).get("legend", True) and layer.get("visible", True):
            legend = vtk.vtkScalarBarActor()
            legend.SetLookupTable(lut)
            title = field["name"] + (f" ({field['unit']})" if field.get("unit") else "")
            legend.SetTitle(title)
            legend.SetNumberOfLabels(min(6, bands))
            legend.SetPosition(0.025, 0.30)
            legend.SetWidth(0.10)
            legend.SetHeight(0.60)
            legend.UnconstrainedFontSizeOn()
            legend.SetMaximumWidthInPixels(130)
            legend.SetBarRatio(0.22)
            legend.SetTextPositionToSucceedScalarBar()
            legend.GetLabelTextProperty().SetFontSize(12)
            legend.GetTitleTextProperty().SetFontSize(14)
            for prop in (legend.GetLabelTextProperty(), legend.GetTitleTextProperty()):
                prop.SetFontFamilyToArial()
                prop.ItalicOff()
                prop.BoldOff()
                prop.ShadowOff()
    mapper.SetInputData(mesh)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetVisibility(layer.get("visible", True))
    style = layer.get("style", {})
    opacity = float(style.get("opacity", 1))
    if not math.isfinite(opacity) or not 0 <= opacity <= 1:
        raise ValueError("opacity_out_of_range")
    prop = actor.GetProperty()
    prop.SetOpacity(opacity)
    prop.SetColor(style.get("color", [0.8, 0.83, 0.9]))
    prop.SetLighting(style.get("lighting", True))
    prop.SetSpecular(float(style.get("specular", 0.2)))
    mode = style.get("mode", "surface")
    if mode == "wireframe":
        prop.SetRepresentationToWireframe()
    elif mode == "surface_edges":
        prop.EdgeVisibilityOn()
    elif mode != "surface":
        raise ValueError("invalid_display_mode")
    actor._legend = legend
    return actor, legend


def arrange_legends(renderer):
    """同一视图的多个色标纵向分配位置，避免各对象刻度相互覆盖。"""
    props = renderer.GetViewProps()
    props.InitTraversal()
    legends = []
    for _ in range(props.GetNumberOfItems()):
        prop = props.GetNextProp()
        if prop.IsA("vtkScalarBarActor") and prop.GetVisibility():
            legends.append(prop)
    slot = min(0.65, 0.85 / max(1, len(legends)))
    for index, legend in enumerate(legends):
        legend.SetPosition(0.025, 0.94 - (index + 1) * slot + 0.05)
        legend.SetHeight(slot - 0.05)


def text_actor(text, position, scale, camera):
    """文字使用真实几何，可在本地渲染与离屏输出中一并保留。"""
    source = vtk.vtkVectorText()
    source.SetText(text)
    mapper = vtk.vtkPolyDataMapper()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    matrix = vtk.vtkMatrix4x4()
    matrix.DeepCopy(camera.GetViewTransformMatrix())
    matrix.Invert()
    for i in range(3):
        matrix.SetElement(i, 3, 0)
    for i in range(3):
        matrix.SetElement(i, 3, position[i])
    # 把姿态烘焙为世界坐标几何；避免 VTK/VTK.js 对 UserMatrix 的差异。
    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix)
    transform.Scale(scale, scale, scale)
    transformed = vtk.vtkTransformPolyDataFilter()
    transformed.SetTransform(transform)
    transformed.SetInputConnection(source.GetOutputPort())
    mapper.SetInputConnection(transformed.GetOutputPort())
    source.Update()
    actor._text_bounds = source.GetOutput().GetBounds()
    actor._text_transform = transform
    actor.GetProperty().SetColor(1, 1, 1)
    actor.GetProperty().LightingOff()
    actor.SetUseBounds(False)
    actor.PickableOff()
    return actor


def fit_probe_label(text, position, scale, renderer):
    """按视口限制标签尺寸与位置，采样锚点不变，由引线连接标签。"""
    camera = renderer.GetActiveCamera()
    width, height = renderer.GetRenderWindow().GetSize()
    x0, y0, x1, y1 = renderer.GetViewport()
    limits = (x0 * width + 8, y0 * height + 8, x1 * width - 8, y1 * height - 8)

    def rectangle(actor):
        """投影文字及背景的四角，获得像素范围。"""
        bounds = actor._text_bounds
        points = []
        for x in (bounds[0] - 0.3, bounds[1] + 0.3):
            for y in (bounds[2] - 0.3, bounds[3] + 0.3):
                world = actor._text_transform.TransformPoint(x, y, 0)
                renderer.SetWorldPoint(*world, 1)
                renderer.WorldToDisplay()
                points.append(renderer.GetDisplayPoint())
        return [
            min(p[0] for p in points),
            min(p[1] for p in points),
            max(p[0] for p in points),
            max(p[1] for p in points),
        ]

    actor = text_actor(text, position, scale, camera)
    rect = rectangle(actor)
    ratio = min(
        1,
        max(1, limits[2] - limits[0]) / max(1, rect[2] - rect[0]),
        max(1, limits[3] - limits[1]) * 0.45 / max(1, rect[3] - rect[1]),
    )
    scale *= ratio
    actor = text_actor(text, position, scale, camera)
    rect = rectangle(actor)
    dx = max(limits[0] - rect[0], min(0, limits[2] - rect[2]))
    dy = max(limits[1] - rect[1], min(0, limits[3] - rect[3]))
    renderer.SetWorldPoint(*position, 1)
    renderer.WorldToDisplay()
    x, y, z = renderer.GetDisplayPoint()
    renderer.SetDisplayPoint(x + dx, y + dy, z)
    renderer.DisplayToWorld()
    world = renderer.GetWorldPoint()
    position = [world[i] / world[3] for i in range(3)]
    return text_actor(text, position, scale, camera), position


def pixel_scale(renderer, position, pixels):
    """在指定深度把屏幕像素换成世界长度，使文字不随网格尺寸膨胀。"""
    renderer.SetWorldPoint(*position, 1)
    renderer.WorldToDisplay()
    x, y, depth = renderer.GetDisplayPoint()
    renderer.SetDisplayPoint(x, y + pixels, depth)
    renderer.DisplayToWorld()
    world = renderer.GetWorldPoint()
    return math.sqrt(sum((world[i] / world[3] - position[i]) ** 2 for i in range(3)))


def add_annotations(scene):
    """添加固定空间 Probe 和各视口方向轴；数值均来自当前完整数据。"""
    from .modules.dataExtraction.spatial import sample_positions

    scene.decorations = []
    scene.probe_rows = {}
    scene.window.SetNumberOfLayers(3)
    for index, renderer in enumerate(scene.renderers):
        if not renderer.GetDraw():
            continue
        view = scene.spec["views"][index]
        while index >= len(scene.annotation_pool):
            scene.annotation_pool.append(vtk.vtkRenderer())
        annotation = scene.annotation_pool[index]
        annotation.RemoveAllViewProps()
        annotation.SetLayer(1)
        annotation.SetInteractive(False)
        annotation.SetDraw(True)
        annotation.SetViewport(renderer.GetViewport())
        annotation.SetPreserveColorBuffer(True)
        annotation.SetPreserveDepthBuffer(False)
        annotation.SetActiveCamera(renderer.GetActiveCamera())
        scene.window.AddRenderer(annotation)
        scene.decorations.append(annotation)
        for probe in scene.spec.get("probes", []):
            visible = probe.get("views", {}).get(str(view["id"]), {}).get("visible", False)
            if not visible:
                continue
            mesh = scene.datasets.get(probe["input"])
            row = (
                sample_positions(mesh, [probe["position"]])[0]
                if mesh is not None
                else {"position": probe["position"], "valid": False, "values": None}
            )
            scene.probe_rows[probe["id"]] = row
            values = row.get("fields") or row.get("values") or {}
            selected = probe.get("fields") or list(values)
            labels = [
                probe.get("name", probe["id"]),
                "XYZ: " + ", ".join(f"{v:.4g}" for v in probe["position"]),
            ]
            if not row["valid"]:
                labels.append("missing frame" if mesh is None else "outside domain")
            else:
                for key in selected:
                    value = values.get(key)
                    label = key.split(":", 1)[-1]
                    if sum(k.split(":", 1)[-1] == label for k in selected) > 1:
                        label = key
                    if isinstance(value, list):
                        value = (
                            value[0] if len(value) == 1 else ", ".join(f"{x:.4g}" for x in value)
                        )
                    labels.append(
                        f"{label}: {value:.5g}"
                        if isinstance(value, (int, float))
                        else f"{label}: {value if value is not None else 'missing field'}"
                    )
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(probe["position"])
            sphere.SetRadius(pixel_scale(renderer, probe["position"], 3))
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1, 0.8, 0.2)
            actor.SetUseBounds(False)
            annotation.AddActor(actor)
            if not probe.get("views", {}).get(str(view["id"]), {}).get("label", True):
                continue
            camera = renderer.GetActiveCamera()
            rotation = vtk.vtkMatrix4x4()
            rotation.DeepCopy(camera.GetViewTransformMatrix())
            rotation.Invert()
            anchor = probe["position"]
            label_scale = pixel_scale(renderer, anchor, 12)
            label_position = [
                anchor[i]
                + label_scale * (2 * rotation.GetElement(i, 0) + rotation.GetElement(i, 1))
                for i in range(3)
            ]
            text, label_position = fit_probe_label(
                "\n".join(labels), label_position, label_scale, renderer
            )
            text.GetMapper().Update()
            bounds = text._text_bounds
            plane = vtk.vtkPlaneSource()
            plane.SetOrigin(bounds[0] - 0.3, bounds[2] - 0.3, -0.02)
            plane.SetPoint1(bounds[1] + 0.3, bounds[2] - 0.3, -0.02)
            plane.SetPoint2(bounds[0] - 0.3, bounds[3] + 0.3, -0.02)
            background = vtk.vtkActor()
            mapper = vtk.vtkPolyDataMapper()
            transformed = vtk.vtkTransformPolyDataFilter()
            transformed.SetTransform(text._text_transform)
            transformed.SetInputConnection(plane.GetOutputPort())
            mapper.SetInputConnection(transformed.GetOutputPort())
            background.SetMapper(mapper)
            background.GetProperty().SetColor(0.035, 0.09, 0.16)
            background.GetProperty().LightingOff()
            background.SetUseBounds(False)
            background.PickableOff()
            annotation.AddActor(background)
            annotation.AddActor(text)
            leader = vtk.vtkLineSource()
            leader.SetPoint1(anchor)
            leader.SetPoint2(label_position)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(leader.GetOutputPort())
            line = vtk.vtkActor()
            line.SetMapper(mapper)
            line.GetProperty().SetColor(1, 1, 1)
            line.SetUseBounds(False)
            annotation.AddActor(line)
        current = scene.spec.get("time", {}).get("value")
        text = (
            f"t = {current:g}   ({scene.times.index(current) + 1}/{len(scene.times)})"
            if current in scene.times
            else "Static"
        )
        if scene.missing:
            text += "  missing frame"
        camera = renderer.GetActiveCamera()

        # 时间读数使用固定像素大小，并保留到原生截图/视频中。
        width, height = scene.window.GetSize()
        x0, y0, x1, y1 = renderer.GetViewport()
        renderer.SetDisplayPoint(x1 * width - max(128, len(text) * 7 + 16), y0 * height + 16, 0.1)
        renderer.DisplayToWorld()
        world = renderer.GetWorldPoint()
        position = [world[i] / world[3] for i in range(3)]
        size = pixel_scale(renderer, position, 12)
        annotation.AddActor(text_actor(text, position, size, camera))
        if view.get("axes", True):
            while index >= len(scene.decoration_pool):
                scene.decoration_pool.append(vtk.vtkRenderer())
            marker = scene.decoration_pool[index]
            marker.RemoveAllViewProps()
            marker.SetDraw(True)
            marker.SetLayer(2)
            marker.SetInteractive(False)
            marker.SetPreserveColorBuffer(True)
            x0, y0, x1, y1 = renderer.GetViewport()
            marker.SetViewport(
                x0 + 0.015 * (x1 - x0),
                y0 + 0.02 * (y1 - y0),
                x0 + 0.18 * (x1 - x0),
                y0 + 0.22 * (y1 - y0),
            )
            axes = vtk.vtkAxesActor()
            axes.SetTotalLength(1, 1, 1)
            axes.SetShaftTypeToCylinder()
            axes.AxisLabelsOff()
            marker.AddActor(axes)
            camera = renderer.GetActiveCamera()

            def sync(*_, camera=camera, marker=marker):
                """使方向标记跟随当前视图相机方向。"""
                p, f = camera.GetPosition(), camera.GetFocalPoint()
                mc = marker.GetActiveCamera()
                mc.SetPosition([p[i] - f[i] for i in range(3)])
                mc.SetFocalPoint(0, 0, 0)
                mc.SetViewUp(camera.GetViewUp())
                mc.ParallelProjectionOn()
                mc.SetParallelScale(1.4)

            sync()
            for label, position in [("X", (1.08, 0, 0)), ("Y", (0, 1.08, 0)), ("Z", (0, 0, 1.08))]:
                marker.AddActor(text_actor(label, position, 0.18, marker.GetActiveCamera()))
            scene.camera_observers.append((camera, camera.AddObserver("ModifiedEvent", sync)))
            scene.window.AddRenderer(marker)
            scene.decorations.append(marker)


def install_local_serializers():
    """补齐 Trame 相机传输的平行投影字段，避免方向轴被当透视远景缩小。"""
    # 原库用裸内存地址作客户端 ID。对象释放后地址可能被不同类型复用，
    # 导致客户端对旧 LookupTable 调用 Actor.setMapper。VTK 保留 Python
    # 附加属性直到 native 对象释放，因此身份随对象存活且不必保留旧网格。
    import sys
    from uuid import uuid4

    from trame_vtk.modules.vtk.serializers import utils
    from trame_vtk.modules.vtk.serializers.registry import register_instance_serializer
    from trame_vtk.modules.vtk.serializers.render_windows import (
        camera_serializer,
        renderer_serializer,
    )

    if not getattr(utils.reference_id, "_phys_identity", False):
        original = utils.reference_id

        def object_identity(obj):
            """单个 VTK 对象的稳定身份，不随内存地址回收而复用。"""
            if obj is None:
                return "0x0"
            if not hasattr(obj, "GetClassName"):
                return original(obj)
            if not hasattr(obj, "_phys_serial_id"):
                obj._phys_serial_id = uuid4().hex
            return obj._phys_serial_id

        object_identity._phys_identity = True
        for name, module in list(sys.modules.items()):
            if name.startswith("trame_vtk.") and getattr(module, "reference_id", None) is original:
                module.reference_id = object_identity

    def serialize_camera(parent, camera, identity, context, depth):
        """使用官方相机序列化并补充缺失的投影参数。"""
        value = camera_serializer(parent, camera, identity, context, depth)
        value["properties"].update(
            parallelProjection=bool(camera.GetParallelProjection()),
            parallelScale=camera.GetParallelScale(),
            viewAngle=camera.GetViewAngle(),
            clippingRange=list(camera.GetClippingRange()),
        )
        return value

    for name in ("vtkCamera", "vtkOpenGLCamera"):
        register_instance_serializer(name, serialize_camera)

    def serialize_renderer(parent, renderer, identity, context, depth):
        """传递视图最大化时的绘制状态，隐藏视图不参与本地渲染。"""
        value = renderer_serializer(parent, renderer, identity, context, depth)
        if value:
            value["properties"]["draw"] = bool(renderer.GetDraw())
        return value

    for name in ("vtkRenderer", "vtkOpenGLRenderer"):
        register_instance_serializer(name, serialize_renderer)
