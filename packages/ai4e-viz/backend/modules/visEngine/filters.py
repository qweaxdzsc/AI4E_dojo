"""VTK 过滤原语；所有输入输出保留完整物理数据，不接触会话或存储。"""

import math
from collections import OrderedDict

import vtk


def field_array(mesh, field: dict):
    """显式检查字段归属与分量，防止选错 point/cell。"""
    association = field.get("association", "point")
    if association not in ("point", "cell"):
        raise ValueError("invalid_field_association")
    data = mesh.GetPointData() if association == "point" else mesh.GetCellData()
    array = data.GetArray(field.get("name", ""))
    if array is None:
        raise ValueError("field_missing: " + str(field.get("name")))
    return array


def scalar_mesh(mesh, field: dict):
    """按模长或分量提取标量，保留原输入与原数组。"""
    import numpy as np
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    # 等值面的生成标量已经过插值；向量插值后再求模长会改变等值语义。
    contour = getattr(mesh, "_vis_contour_field", None)
    if contour == {
        "name": field.get("name"),
        "association": field.get("association", "point"),
        "component": field.get("component", "magnitude"),
    }:
        return mesh
    array = field_array(mesh, field)
    component = field.get("component", "magnitude")
    stamp = (mesh.GetMTime(), array.GetMTime())
    key = (*stamp, field.get("association", "point"), field["name"], component)
    cache = getattr(mesh, "_vis_scalar_cache", None)
    if cache is None:
        cache = mesh._vis_scalar_cache = OrderedDict()
    if key in cache:
        cache.move_to_end(key)
        return cache[key]
    values = vtk_to_numpy(array)
    if values.ndim == 2:
        if component == "magnitude":
            values = np.linalg.norm(values, axis=1)
        elif isinstance(component, int) and 0 <= component < values.shape[1]:
            values = values[:, component]
        else:
            raise ValueError("invalid_field_component")
    output = mesh.NewInstance()
    output.ShallowCopy(mesh)
    selected = numpy_to_vtk(np.asarray(values), deep=True)
    selected.SetName("__vis_scalar")
    attributes = (
        output.GetPointData()
        if field.get("association", "point") == "point"
        else output.GetCellData()
    )
    attributes.AddArray(selected)
    attributes.SetActiveScalars("__vis_scalar")
    cache[key] = output
    # 每数据对象最多保留四个字段选择，随对象释放；不建立跨会话数组库。
    while len(cache) > 4:
        cache.popitem(last=False)
    return output


def _cut_plane(params):
    """从切面参数构造平面；零法向拒绝。"""
    plane = vtk.vtkPlane()
    plane.SetOrigin(params.get("origin", [0, 0, 0]))
    normal = params.get("normal", [1, 0, 0])
    if sum(float(x) ** 2 for x in normal) == 0:
        raise ValueError("zero_plane_normal")
    plane.SetNormal(normal)
    return plane


def _extract_crinkle(mesh, plane, *, only_cut_cells, inside=True):
    """按平面抽出被切到的整格，不沿平面切开单元。"""
    extract = vtk.vtkExtractGeometry()
    extract.SetInputData(mesh)
    extract.SetImplicitFunction(plane)
    extract.SetExtractInside(bool(inside))
    extract.ExtractBoundaryCellsOn()
    extract.SetExtractOnlyBoundaryCells(bool(only_cut_cells))
    extract.Update()
    return extract.GetOutput()


def _dataset_surface(mesh):
    """体单元转成外表面，保留四边形或多边形面。"""
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(mesh)
    surface.Update()
    return surface.GetOutput()


def _maybe_triangulate(mesh, enabled):
    """仅在明确要求时拆成三角面。"""
    if not enabled:
        return mesh
    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputData(mesh)
    triangles.Update()
    return triangles.GetOutput()


def apply_filter(mesh, node: dict, seed_mesh=None):
    """计算切面、等值、箭头或流线；体/面和矢量语义显式验证。"""
    kind, params = node["type"], node.get("parameters", {})
    if kind == "surface":
        algorithm = vtk.vtkDataSetSurfaceFilter()
    elif kind in ("slice", "clip"):
        plane = _cut_plane(params)
        crinkle = bool(params.get("crinkle", kind == "slice"))
        triangulate = bool(params.get("triangulate", False))
        if kind == "slice" and crinkle:
            cells = _extract_crinkle(mesh, plane, only_cut_cells=True)
            return _maybe_triangulate(_dataset_surface(cells), triangulate)
        if kind == "clip" and crinkle:
            inside = not bool(params.get("inside_out", False))
            return _extract_crinkle(mesh, plane, only_cut_cells=False, inside=inside)
        if kind == "slice":
            algorithm = vtk.vtkCutter()
            algorithm.SetCutFunction(plane)
            if triangulate:
                algorithm.GenerateTrianglesOn()
            else:
                algorithm.GenerateTrianglesOff()
        else:
            algorithm = vtk.vtkTableBasedClipDataSet()
            algorithm.SetClipFunction(plane)
            algorithm.SetInsideOut(bool(params.get("inside_out", False)))
    elif kind in ("contour", "isosurface"):
        dimensions = {mesh.GetCell(i).GetCellDimension() for i in range(mesh.GetNumberOfCells())}
        if kind == "isosurface" and dimensions and max(dimensions) != 3:
            raise ValueError("isosurface_requires_volume")
        if kind == "contour" and dimensions and max(dimensions) > 2:
            raise ValueError("contour_requires_surface_or_slice")
        field = params["field"]
        mesh = scalar_mesh(mesh, field)
        if field.get("association", "point") == "cell" or (
            kind == "glyph"
            and params.get("scale_mode") == "scalar"
            and params.get("scale_field", {}).get("association") == "cell"
        ):
            convert = vtk.vtkCellDataToPointData()
            convert.SetInputData(mesh)
            convert.Update()
            mesh = convert.GetOutput()
        algorithm = vtk.vtkContourFilter()
        source_range = list(mesh.GetPointData().GetArray("__vis_scalar").GetRange())
        levels = params.get("levels")
        if levels is not None:
            if "values" in params or levels.get("mode") != "automatic":
                raise ValueError("conflicting_contour_levels")
            count = levels.get("count", 10)
            if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 256:
                raise ValueError("invalid_contour_count")
            limits = levels.get("range") or source_range
            if (
                len(limits) != 2
                or not all(math.isfinite(v) for v in limits)
                or limits[0] >= limits[1]
            ):
                raise ValueError("constant_or_invalid_contour_range")
            if source_range[0] >= source_range[1]:
                raise ValueError("constant_contour_field")
            values = [
                limits[0] + (limits[1] - limits[0]) * i / (count + 1) for i in range(1, count + 1)
            ]
        else:
            values = params.get("values", [0])
        if not values or len(values) > 256 or not all(math.isfinite(float(v)) for v in values):
            raise ValueError("invalid_contour_values")
        algorithm.SetNumberOfContours(len(values))
        for i, value in enumerate(values):
            algorithm.SetValue(i, float(value))
    elif kind in ("glyph", "streamline"):
        field = params["field"]
        if field_array(mesh, field).GetNumberOfComponents() != 3:
            raise ValueError("three_component_vector_required")
        if field.get("association", "point") == "cell" or (
            kind == "glyph"
            and params.get("scale_mode") == "scalar"
            and params.get("scale_field", {}).get("association") == "cell"
        ):
            convert = vtk.vtkCellDataToPointData()
            convert.SetInputData(mesh)
            convert.Update()
            mesh = convert.GetOutput()
        copy = mesh.NewInstance()
        copy.ShallowCopy(mesh)
        copy.GetPointData().SetActiveVectors(field["name"])
        mesh = copy
        if kind == "glyph":
            return glyph_mesh(mesh, params)
        from .seeds import (
            build_seed_source,
            is_surface_mesh,
            project_surface_vectors,
            snap_seed_points,
        )

        seeds = snap_seed_points(build_seed_source(params, seed_mesh), mesh)
        if seeds.GetNumberOfPoints() <= 0:
            raise ValueError("empty_seed_source")
        if is_surface_mesh(mesh):
            mesh = project_surface_vectors(mesh, field["name"])
        algorithm = vtk.vtkStreamTracer()
        algorithm.SetSourceData(seeds)
        algorithm.SetIntegratorTypeToRungeKutta45()
        if hasattr(algorithm, "SetCellLocatorToStaticCellLocator"):
            algorithm.SetCellLocatorToStaticCellLocator()
        elif hasattr(algorithm, "SetInterpolatorTypeToCellLocator"):
            algorithm.SetInterpolatorTypeToCellLocator()
        algorithm.SetIntegrationStepUnit(vtk.vtkStreamTracer.LENGTH_UNIT)
        length = max(1e-9, float(params.get("length", 10)))
        algorithm.SetMaximumPropagation(length)
        algorithm.SetInitialIntegrationStep(max(length * 0.002, 1e-9))
        algorithm.SetMinimumIntegrationStep(max(length * 1e-5, 1e-12))
        algorithm.SetMaximumIntegrationStep(max(length * 0.05, 1e-8))
        algorithm.SetMaximumNumberOfSteps(4000)
        algorithm.SetTerminalSpeed(1e-12)
        algorithm.SetComputeVorticity(False)
        direction = params.get("direction", "both")
        methods = {
            "both": algorithm.SetIntegrationDirectionToBoth,
            "forward": algorithm.SetIntegrationDirectionToForward,
            "backward": algorithm.SetIntegrationDirectionToBackward,
        }
        if direction not in methods:
            raise ValueError("invalid_streamline_direction")
        methods[direction]()
    elif kind == "plot_over_line":
        start = params.get("point1") or params.get("seed_start", [0, 0, 0])
        end = params.get("point2") or params.get("seed_end", [1, 0, 0])
        count = int(params.get("resolution", 1000))
        if not 2 <= count <= 20000:
            raise ValueError("invalid_line_resolution")
        from .sampling import sample_line

        rows = sample_line(mesh, start, end, count, params.get("fields"))
        line = vtk.vtkLineSource()
        line.SetPoint1(start)
        line.SetPoint2(end)
        line.SetResolution(max(1, count - 1))
        line.Update()
        result = line.GetOutput()
        result._vis_line_rows = rows
        return result
    else:
        raise ValueError("unsupported_filter: " + kind)
    algorithm.SetInputData(mesh)
    algorithm.Update()
    result = algorithm.GetOutput()
    if kind in ("contour", "isosurface"):
        result._vis_contour_field = {
            "name": field["name"],
            "association": field.get("association", "point"),
            "component": field.get("component", "magnitude"),
        }
        result._vis_contour_range = source_range
    return result


def glyph_mesh(mesh, params):
    """确定性采样与矢量符号生成，保留原节点字段，不改输入数组。"""
    import numpy as np
    from vtk.util.numpy_support import numpy_to_vtk

    sampling = params.get("sampling") or {"mode": "nodes"}
    mode = sampling.get("mode", "nodes")
    if mode == "spatial":
        spacing = float(sampling.get("spacing", 0))
        if not math.isfinite(spacing) or spacing <= 0:
            raise ValueError("invalid_glyph_spacing")
        bins = {}
        bounds = mesh.GetBounds()
        origin = np.asarray([bounds[0], bounds[2], bounds[4]])
        for i in range(mesh.GetNumberOfPoints()):
            point = np.asarray(mesh.GetPoint(i))
            cell = tuple(np.floor((point - origin) / spacing).astype(int))
            distance = float(np.sum((point - (origin + (np.asarray(cell) + 0.5) * spacing)) ** 2))
            if cell not in bins or (distance, i) < bins[cell]:
                bins[cell] = (distance, i)
        indices = [bins[key][1] for key in sorted(bins)]
    elif mode == "nodes":
        stride = params.get("stride", 1)
        if isinstance(stride, bool) or int(stride) != stride or stride < 1:
            raise ValueError("invalid_glyph_stride")
        indices = list(range(0, mesh.GetNumberOfPoints(), int(stride)))
    else:
        raise ValueError("invalid_glyph_sampling")
    sampled = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    sampled.GetPointData().CopyAllocate(mesh.GetPointData(), len(indices))
    for j, i in enumerate(indices):
        points.InsertNextPoint(mesh.GetPoint(i))
        sampled.GetPointData().CopyData(mesh.GetPointData(), i, j)
    sampled.SetPoints(points)
    sampled.GetPointData().SetActiveVectors(params["field"]["name"])
    shape = params.get("shape") or {}
    kind = shape.get("type", "arrow")
    if kind == "arrow":
        source = vtk.vtkArrowSource()
        for key, setter, default in [
            ("tip_length", source.SetTipLength, 0.35),
            ("tip_radius", source.SetTipRadius, 0.1),
            ("shaft_radius", source.SetShaftRadius, 0.03),
        ]:
            value = float(shape.get(key, default))
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError("invalid_glyph_shape_size")
            setter(value)
    elif kind == "cone":
        source = vtk.vtkConeSource()
        source.SetDirection(1, 0, 0)
        source.SetCenter(0.5, 0, 0)
        source.SetHeight(1)
        source.SetRadius(0.2)
    elif kind == "line":
        source = vtk.vtkLineSource()
        source.SetPoint1(0, 0, 0)
        source.SetPoint2(1, 0, 0)
    else:
        raise ValueError("invalid_glyph_shape")
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(sampled)
    glyph.SetSourceConnection(source.GetOutputPort())
    glyph.SetVectorModeToUseVector()
    scale_mode = params.get("scale_mode", "vector")
    if scale_mode == "vector":
        glyph.SetScaleModeToScaleByVector()
    elif scale_mode == "constant":
        glyph.SetScaleModeToDataScalingOff()
    elif scale_mode == "scalar":
        field = {**params.get("scale_field", {}), "association": "point"}
        scalar = scalar_mesh(mesh, field).GetPointData().GetArray("__vis_scalar")
        values = np.asarray([abs(scalar.GetTuple1(i)) for i in indices])
        if not np.all(np.isfinite(values)):
            raise ValueError("invalid_glyph_scale_values")
        array = numpy_to_vtk(values, deep=True)
        array.SetName("__vis_glyph_scale")
        sampled.GetPointData().AddArray(array)
        sampled.GetPointData().SetActiveScalars("__vis_glyph_scale")
        glyph.SetScaleModeToScaleByScalar()
    else:
        raise ValueError("invalid_glyph_scale_mode")
    scale = float(params.get("scale", 0.1))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("glyph_scale_must_be_positive")
    glyph.SetScaleFactor(scale)
    glyph.OrientOn()
    glyph.Update()
    result = glyph.GetOutput()
    result._vis_sampled_ids = indices
    return result


def streamline_style(style=None):
    """读取流线显示缺省：线、细、8 面。缺键不回写。"""
    block = (style or {}).get("streamline")
    if not isinstance(block, dict):
        block = {}
    shape = block.get("shape", "line")
    if shape not in ("line", "tube"):
        raise ValueError("invalid_streamline_shape")
    thickness = block.get("thickness", 1)
    if (
        isinstance(thickness, bool)
        or not isinstance(thickness, (int, float))
        or not math.isfinite(thickness)
        or thickness <= 0
        or (shape == "line" and thickness > 20)
        or (shape == "tube" and thickness > 1e6)
    ):
        raise ValueError("invalid_streamline_thickness")
    sides = block.get("sides", 8)
    if isinstance(sides, bool) or not isinstance(sides, int) or not 3 <= sides <= 64:
        raise ValueError("invalid_streamline_sides")
    return {"shape": shape, "thickness": float(thickness), "sides": int(sides)}


def style_streamline_mesh(mesh, style=None):
    """按 style.streamline 把积分折线画成线或圆管；线模式原样返回。"""
    values = streamline_style(style)
    if values["shape"] != "tube":
        return mesh
    tube = vtk.vtkTubeFilter()
    tube.SetInputData(mesh)
    tube.SetRadius(values["thickness"])
    tube.SetNumberOfSides(values["sides"])
    tube.CappingOn()
    tube.Update()
    # 圆管默认是三角带；转成三角面后着色和远程出图更稳。
    triangles = vtk.vtkTriangleFilter()
    triangles.SetInputData(tube.GetOutput())
    triangles.Update()
    return triangles.GetOutput()
