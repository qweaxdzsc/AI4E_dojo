"""同一场景的显示对象和导出注记，保持计算字段与着色字段独立。"""

import math
from contextlib import contextmanager

import vtk

# 本地 VTK.js 相机由客户端轨道维护；只有服务端主动改视角才推位姿。
# 见 https://discourse.vtk.org/t/update-camera-in-trame-vtklocalview/15979
_CAMERA_POSE_PUSH_DEPTH = 0


@contextmanager
def camera_pose_push():
    """允许本次本地序列化带上相机位姿；嵌套调用共用同一开关。"""
    global _CAMERA_POSE_PUSH_DEPTH
    _CAMERA_POSE_PUSH_DEPTH += 1
    try:
        yield
    finally:
        _CAMERA_POSE_PUSH_DEPTH -= 1


def camera_pose_push_enabled() -> bool:
    """当前是否允许把服务端相机位姿写进本地场景。"""
    return _CAMERA_POSE_PUSH_DEPTH > 0

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
    actor.GetProperty().SetOpacity(0.28 if name == "plane" else 1)
    actor.GetProperty().SetLineWidth(3 if name.startswith("axis") or name == "rotate" else 1)
    actor.GetProperty().SetRepresentationToSurface()
    actor.GetProperty().LightingOff()
    actor.PickableOff()
    if name == "border":
        actor.GetProperty().SetLineWidth(2)
    if name == "plane":
        actor.GetProperty().SetRepresentationToSurface()
        actor.GetProperty().SetOpacity(0.28)
    actor.SetUseBounds(False)
    actor._plane_handle = name
    return actor


def _point_vector(mesh, field):
    """Surface LIC 只接受三维点向量。"""
    if mesh is None or not field or field.get("association", "point") != "point":
        return None
    array = mesh.GetPointData().GetArray(field.get("name", ""))
    if array is None or array.GetNumberOfComponents() != 3:
        return None
    return array


def first_point_vector(mesh):
    """网格上第一个三维点向量，供旧修订或缺声明时回退。"""
    if mesh is None:
        return None
    data = mesh.GetPointData()
    for index in range(data.GetNumberOfArrays()):
        array = data.GetArray(index)
        if array is not None and array.GetNumberOfComponents() == 3 and array.GetName():
            return array
    return None


def resolve_lic_vectors(mesh, layer):
    """LIC 方向：已声明向量，否则着色场若是点向量，再否则网格上第一个点向量。"""
    declared = ((layer or {}).get("style") or {}).get("lic") or {}
    array = _point_vector(mesh, declared.get("vectors"))
    if array is not None:
        return array
    array = _point_vector(mesh, (layer or {}).get("field"))
    if array is not None:
        return array
    return first_point_vector(mesh)


def _ensure_point_vectors(mesh, vectors):
    """抽表面后可能丢掉原向量，着色副本也要保留同一方向场。"""
    data = mesh.GetPointData()
    if data.GetArray(vectors.GetName()) is None:
        copied = vectors.NewInstance()
        copied.DeepCopy(vectors)
        copied.SetName(vectors.GetName())
        data.AddArray(copied)
    data.SetActiveVectors(vectors.GetName())


def _surface_mesh(mesh):
    """LIC 映射器只要表面，体网格先抽表面。"""
    if mesh.IsA("vtkPolyData"):
        return mesh
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(mesh)
    surface.Update()
    return surface.GetOutput()


def _apply_lic(mapper, style):
    """按 ParaView 常用项配置表面 LIC，缺省与旧修订兼容。"""
    interface = mapper.GetLICInterface()
    settings = style.get("lic") or {}
    steps = int(settings.get("number_of_steps", 40))
    if not 1 <= steps <= 400:
        raise ValueError("invalid_lic_steps")
    step = float(settings.get("step_size", 0.25))
    if not math.isfinite(step) or not 0 < step <= 10:
        raise ValueError("invalid_lic_step_size")
    intensity = float(settings.get("intensity", 0.8))
    if not math.isfinite(intensity) or not 0 <= intensity <= 1:
        raise ValueError("invalid_lic_intensity")
    interface.SetNumberOfSteps(steps)
    interface.SetStepSize(step)
    interface.SetEnhancedLIC(bool(settings.get("enhanced_lic", True)))
    contrast = {"off": 0, "lic": 1, "color": 2, "both": 3}.get(
        str(settings.get("enhance_contrast", "both")), 3
    )
    interface.SetEnhanceContrast(contrast)
    interface.SetColorMode(0 if settings.get("color_mode", "blend") == "blend" else 1)
    interface.SetLICIntensity(intensity)


def build_display(mesh, layer):
    """完整验证显示参数后创建候选显示对象，失败不影响旧画面。"""
    style = layer.get("style", {})
    if style.get("mode") == "surface_lic":
        return build_lic_display(mesh, layer)
    mapper = vtk.vtkDataSetMapper()
    mapper.ScalarVisibilityOff()
    field = layer.get("field")
    legend = None
    if field:
        mesh = prepare_scalar(mesh, field)
        contour_field = getattr(mesh, "_vis_contour_field", None)
        same_contour = contour_field == {
            "name": field.get("name"),
            "association": field.get("association", "point"),
            "component": field.get("component", "magnitude"),
        }
        if field.get("association", "point") == "cell" and not same_contour:
            mapper.SetScalarModeToUseCellFieldData()
            data = mesh.GetCellData()
        else:
            mapper.SetScalarModeToUsePointFieldData()
            data = mesh.GetPointData()
        mapper.SelectColorArray("__vis_scalar")
        mapper.ScalarVisibilityOn()
        lut, limits, bands = build_color_mapping(
            data.GetArray("__vis_scalar"),
            (
                {
                    **layer.get("color", {}),
                    "range": layer.get("color", {}).get("range") or mesh._vis_contour_range,
                }
                if same_contour
                else layer.get("color", {})
            ),
        )
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(limits)
        if layer.get("color", {}).get("legend", True) and layer.get("visible", True):
            legend = vtk.vtkScalarBarActor()
            legend.SetLookupTable(lut)
            title = field["name"] + (f" ({field['unit']})" if field.get("unit") else "")
            legend.SetTitle(title)
            legend._vis_style = dict(layer.get("color", {}).get("legend_style", {}))
            legend.SetNumberOfLabels(min(6, bands))
            legend.SetPosition(0.025, 0.30)
            legend.SetWidth(0.10)
            legend.SetHeight(0.60)
            legend.UnconstrainedFontSizeOn()
            legend.SetMaximumWidthInPixels(130)
            legend.SetBarRatio(0.22)
            legend.SetTextPositionToSucceedScalarBar()
            style = legend._vis_style
            legend.GetLabelTextProperty().SetFontSize(int(style.get("label_font_size", 25)))
            legend.GetTitleTextProperty().SetFontSize(int(style.get("title_font_size", 25)))
            for prop in (legend.GetLabelTextProperty(), legend.GetTitleTextProperty()):
                prop.SetFontFamilyToArial()
                prop.ItalicOff()
                prop.BoldOff()
                prop.ShadowOff()
    display_style = layer.get("style", {})
    stream = display_style.get("streamline") if isinstance(display_style, dict) else None
    if (stream or {}).get("shape") == "tube":
        from modules.visEngine import style_streamline_mesh

        mesh = style_streamline_mesh(mesh, display_style)
    mapper.SetInputData(mesh)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetVisibility(layer.get("visible", True))
    actor.SetProperty(display_property(layer.get("style", {})))
    actor._legend = legend
    return actor, legend


def copy_display_mapper(target, source, layer=None):
    """ShallowCopy 后补齐标量与 LIC 着色，避免换场后 mapper 仍走纯色。"""
    target.SetScalarVisibility(source.GetScalarVisibility())
    target.SetScalarMode(source.GetScalarMode())
    target.SetColorMode(source.GetColorMode())
    name = source.GetArrayName()
    if name:
        target.SelectColorArray(name)
    lut = source.GetLookupTable()
    if lut is not None:
        target.SetLookupTable(lut)
    target.SetScalarRange(source.GetScalarRange())
    if layer and (layer.get("style") or {}).get("mode") == "surface_lic" and hasattr(
        target, "GetLICInterface"
    ):
        _apply_lic(target, layer.get("style", {}))


def build_lic_display(mesh, layer):
    """Surface LIC：方向用点向量，着色跟随当前物理量；缺向量拒绝。"""
    vectors = resolve_lic_vectors(mesh, layer)
    if vectors is None:
        raise ValueError("请选择三维点向量场才能使用 Surface LIC")
    surface = _surface_mesh(mesh)
    _ensure_point_vectors(surface, vectors)
    mapper = vtk.vtkSurfaceLICMapper()
    field = layer.get("field")
    legend = None
    if field:
        colored = prepare_scalar(surface, {**field, "component": field.get("component", "magnitude")})
        _ensure_point_vectors(colored, vectors)
        contour_field = getattr(colored, "_vis_contour_field", None)
        same_contour = contour_field == {
            "name": field.get("name"),
            "association": field.get("association", "point"),
            "component": field.get("component", "magnitude"),
        }
        if field.get("association", "point") == "cell" and not same_contour:
            mapper.SetScalarModeToUseCellFieldData()
            data = colored.GetCellData()
        else:
            mapper.SetScalarModeToUsePointFieldData()
            data = colored.GetPointData()
        array = data.GetArray("__vis_scalar")
        if array is not None:
            mapper.SelectColorArray("__vis_scalar")
            mapper.SetColorModeToMapScalars()
            mapper.ScalarVisibilityOn()
            lut, limits, bands = build_color_mapping(
                array,
                (
                    {
                        **layer.get("color", {}),
                        "range": layer.get("color", {}).get("range") or colored._vis_contour_range,
                    }
                    if same_contour
                    else layer.get("color", {})
                ),
            )
            mapper.SetLookupTable(lut)
            mapper.SetScalarRange(limits)
            if layer.get("color", {}).get("legend", True) and layer.get("visible", True):
                legend = vtk.vtkScalarBarActor()
                legend.SetLookupTable(lut)
                title = field["name"] + (f" ({field['unit']})" if field.get("unit") else "")
                legend.SetTitle(title)
                legend._vis_style = dict(layer.get("color", {}).get("legend_style", {}))
                legend.SetNumberOfLabels(min(6, bands))
        mapper.SetInputData(colored)
    else:
        mapper.SetInputData(surface)
        mapper.ScalarVisibilityOff()
    _apply_lic(mapper, layer.get("style", {}))
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetVisibility(layer.get("visible", True))
    actor.SetProperty(display_property({**layer.get("style", {}), "mode": "surface"}))
    actor._legend = legend
    return actor, legend


def display_property(style):
    """先验证并构造属性；失败不修改现有 actor 或 mapper。"""
    opacity = float(style.get("opacity", 1))
    if not math.isfinite(opacity) or not 0 <= opacity <= 1:
        raise ValueError("opacity_out_of_range")
    prop = vtk.vtkProperty()
    prop.SetOpacity(opacity)
    prop.SetColor(style.get("color", [0.8, 0.83, 0.9]))
    prop.SetLighting(style.get("lighting", True))
    prop.SetSpecular(float(style.get("specular", 0.2)))
    stream = style.get("streamline") if isinstance(style.get("streamline"), dict) else {}
    if stream.get("shape", "line") == "line" and "thickness" in stream:
        width = float(stream["thickness"])
    else:
        width = float(style.get("line_width", 1))
    if not math.isfinite(width) or not 0 < width <= 20:
        raise ValueError("invalid_line_width")
    prop.SetLineWidth(width)
    mode = style.get("mode", "surface")
    if mode == "wireframe":
        prop.SetRepresentationToWireframe()
    elif mode == "surface_edges":
        prop.EdgeVisibilityOn()
    elif mode not in ("surface", "surface_lic"):
        raise ValueError("invalid_display_mode")
    return prop


def arrange_legends(renderer):
    """同一视图的多个色标纵向分配位置，避免各对象刻度相互覆盖。"""
    props = renderer.GetViewProps()
    props.InitTraversal()
    legends = []
    for _ in range(props.GetNumberOfItems()):
        prop = props.GetNextProp()
        if prop.IsA("vtkScalarBarActor") and prop.GetVisibility():
            legends.append(prop)
    width, height = renderer.GetSize()
    width, height = max(width, 1), max(height, 1)
    for index, legend in enumerate(legends):
        style = getattr(legend, "_vis_style", {})
        horizontal = style.get("orientation", "vertical") == "horizontal"
        length = float(style.get("length", 0.6))
        thickness = float(style.get("thickness", 25))
        position = style.get("position", "right")
        # 自动位置分配槽位；自定义位置不被自动避让覆盖。
        if position != "custom":
            length = min(length, 0.8 / max(1, len(legends)) - 0.03)
        w, h = (
            (length, max(0.08, thickness / height * 3))
            if horizontal
            else (max(0.08, thickness / width * 5), length)
        )
        positions = {
            "right": (1 - w - 0.025, 0.92 - h - index * 0.8 / max(1, len(legends)) - 0.03),
            "left": (0.025, 0.92 - h - index * 0.8 / max(1, len(legends)) - 0.03),
            "top": (0.12 + index * 0.8 / max(1, len(legends)), 1 - h - 0.07),
            "bottom": (0.12 + index * 0.8 / max(1, len(legends)), 0.04),
        }
        x, y = positions.get(position, (style.get("x", 0.8), style.get("y", 0.2)))
        legend.SetOrientationToHorizontal() if horizontal else legend.SetOrientationToVertical()
        legend.SetPosition(min(float(x), 1 - w - 0.01), min(float(y), 1 - h - 0.01))
        legend.SetWidth(w)
        legend.SetHeight(h)
        legend.SetMaximumWidthInPixels(width)
        legend.SetMaximumHeightInPixels(height)
        legend.SetBarRatio(min(0.8, thickness / (h * height if horizontal else w * width)))
        legend.GetTitleTextProperty().SetFontSize(int(style.get("title_font_size", 25)))
        legend.GetLabelTextProperty().SetFontSize(int(style.get("label_font_size", 25)))


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
    scene.probe_actors = {}
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
            mesh = scene.datasets.get(probe["input"])
            row = (
                sample_positions(mesh, [probe["position"]])[0]
                if mesh is not None
                else {"position": probe["position"], "valid": False, "values": None}
            )
            scene.probe_rows[probe["id"]] = row
            values = row.get("fields") or row.get("values") or {}
            selected = probe.get("fields") or list(values)
            labels = []
            if not row["valid"]:
                labels.append("状态    缺帧" if mesh is None else "状态    域外")
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
                    text = (
                        f"{value:.5g}"
                        if isinstance(value, (int, float))
                        else (value if value is not None else "缺失")
                    )
                    labels.append(f"{label:<8} {text}")
            if not labels:
                labels.append("无选中物理量")
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(probe["position"])
            sphere.SetRadius(pixel_scale(renderer, probe["position"], 5))
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.25, 0.60, 1.0)
            actor.SetUseBounds(False)
            annotation.AddActor(actor)
            parts = {"marker": [actor], "labels": []}
            scene.probe_actors[(probe["id"], view["id"])] = parts
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
            parts["labels"] = [background, text, line]
            label_visible = probe.get("views", {}).get(str(view["id"]), {}).get("label", True)
            actor.SetVisibility(visible)
            for item in parts["labels"]:
                item.SetVisibility(visible and label_visible)
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
        """保留相机身份；默认不写轨道位姿，避免 hover/refresh 覆盖客户端。"""
        value = camera_serializer(parent, camera, identity, context, depth)
        if not camera_pose_push_enabled():
            # 官方 serializer 每次都带 position/focalPoint/viewUp/clippingRange。
            # VtkLocalView.update 会把这份服务端快照推给 vtk.js；辅助平面悬停
            # 若夹带添加平面时的旧位姿，旋转/平移/缩放会概率性被拉回。
            value["properties"] = {}
            return value
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
        # 官方序列化在只剩相机时返回空，导致最后对象隐藏/删除后客户端撤下背景。
        # 先保留公开依赖清单，空场景也要发送移除旧资产的调用和同一相机身份。
        old_props = list(context.get_last_dependency_list(f"{identity}-props"))
        old_lights = list(context.get_last_dependency_list(f"{identity}-lights"))
        value = renderer_serializer(parent, renderer, identity, context, depth)
        if value is None:
            from trame_vtk.modules.vtk.serializers.registry import class_name

            camera = renderer.GetActiveCamera()
            camera_id = utils.reference_id(camera)
            value = {
                "parent": utils.reference_id(parent),
                "id": identity,
                "type": class_name(renderer),
                "properties": {
                    "background": renderer.GetBackground(),
                    "background2": renderer.GetBackground2(),
                    "viewport": renderer.GetViewport(),
                    "layer": renderer.GetLayer(),
                    "preserveColorBuffer": bool(renderer.GetPreserveColorBuffer()),
                    "preserveDepthBuffer": bool(renderer.GetPreserveDepthBuffer()),
                    "interactive": bool(renderer.GetInteractive()),
                },
                "dependencies": [serialize_camera(renderer, camera, camera_id, context, depth + 1)],
                "calls": [["setActiveCamera", [utils.wrap_id(camera_id)]]]
                + [["removeViewProp", [utils.wrap_id(key)]] for key in old_props]
                + [["removeLight", [utils.wrap_id(key)]] for key in old_lights],
            }
        value["properties"]["draw"] = bool(renderer.GetDraw())
        return value

    for name in ("vtkRenderer", "vtkOpenGLRenderer"):
        register_instance_serializer(name, serialize_renderer)
