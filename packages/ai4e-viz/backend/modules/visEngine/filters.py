"""VTK 过滤原语；所有输入输出保留完整物理数据，不接触会话或存储。"""

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

    array = field_array(mesh, field)
    values = vtk_to_numpy(array)
    component = field.get("component", "magnitude")
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
    return output


def apply_filter(mesh, node: dict, seed_mesh=None):
    """计算切面、等值、箭头或流线；体/面和矢量语义显式验证。"""
    kind, params = node["type"], node.get("parameters", {})
    if kind == "surface":
        algorithm = vtk.vtkDataSetSurfaceFilter()
    elif kind in ("slice", "clip"):
        plane = vtk.vtkPlane()
        plane.SetOrigin(params.get("origin", [0, 0, 0]))
        normal = params.get("normal", [1, 0, 0])
        if sum(float(x) ** 2 for x in normal) == 0:
            raise ValueError("zero_plane_normal")
        plane.SetNormal(normal)
        if kind == "slice":
            algorithm = vtk.vtkCutter()
            algorithm.SetCutFunction(plane)
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
        if field.get("association", "point") == "cell":
            convert = vtk.vtkCellDataToPointData()
            convert.SetInputData(mesh)
            convert.Update()
            mesh = convert.GetOutput()
        algorithm = vtk.vtkContourFilter()
        values = params.get("values", [0])
        if not values or len(values) > 256:
            raise ValueError("invalid_contour_values")
        algorithm.SetNumberOfContours(len(values))
        for i, value in enumerate(values):
            algorithm.SetValue(i, float(value))
    elif kind in ("glyph", "streamline"):
        field = params["field"]
        if field_array(mesh, field).GetNumberOfComponents() != 3:
            raise ValueError("three_component_vector_required")
        if field.get("association", "point") == "cell":
            convert = vtk.vtkCellDataToPointData()
            convert.SetInputData(mesh)
            convert.Update()
            mesh = convert.GetOutput()
        copy = mesh.NewInstance()
        copy.ShallowCopy(mesh)
        copy.GetPointData().SetActiveVectors(field["name"])
        mesh = copy
        if kind == "glyph":
            mask = vtk.vtkMaskPoints()
            mask.SetInputData(mesh)
            mask.SetOnRatio(max(1, int(params.get("stride", 1))))
            mask.RandomModeOff()
            arrow = vtk.vtkArrowSource()
            algorithm = vtk.vtkGlyph3D()
            algorithm.SetInputConnection(mask.GetOutputPort())
            algorithm.SetSourceConnection(arrow.GetOutputPort())
            algorithm.SetVectorModeToUseVector()
            algorithm.SetScaleModeToScaleByVector()
            scale = float(params.get("scale", 0.1))
            if scale <= 0:
                raise ValueError("glyph_scale_must_be_positive")
            algorithm.SetScaleFactor(scale)
            algorithm.OrientOn()
            algorithm.Update()
            return algorithm.GetOutput()
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
    else:
        raise ValueError("unsupported_filter: " + kind)
    algorithm.SetInputData(mesh)
    algorithm.Update()
    return algorithm.GetOutput()
