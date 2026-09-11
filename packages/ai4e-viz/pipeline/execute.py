"""有限 VTK 显示管线，保留原始体拓扑直到显示转换。"""


def execute_pipeline(dataset, pipeline: list[dict]):
    """执行显式过滤器；不猜测单元场到点场或跨网格插值。"""
    import numpy as np
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    current = dataset.NewInstance()
    current.DeepCopy(dataset)
    for association, attrs, count in [
        ("point", current.GetPointData(), current.GetNumberOfPoints()),
        ("cell", current.GetCellData(), current.GetNumberOfCells()),
    ]:
        if attrs.GetArray("__dojo_original_" + association) is not None:
            continue
        declared = attrs.GetArray("original_" + association + "_id")
        if declared is not None:
            values = vtk_to_numpy(declared)
            if values.ndim != 1 or len(values) != count or values.dtype.kind not in "iu":
                raise ValueError("invalid_original_entity_ids")
            if len(np.unique(values)) != count:
                raise ValueError("duplicate_original_entity_ids")
            ids = declared.NewInstance()
            ids.DeepCopy(declared)
        else:
            ids = numpy_to_vtk(np.arange(count, dtype=np.int64), deep=True)
        ids.SetName("__dojo_original_" + association)
        attrs.AddArray(ids)
    generated = False
    for node in pipeline:
        kind = node["type"]
        if kind == "surface":
            algorithm = vtk.vtkDataSetSurfaceFilter()
        elif kind in {"slice", "clip"}:
            plane = vtk.vtkPlane()
            normal = node.get("normal", [1, 0, 0])
            if len(normal) != 3 or not any(normal):
                raise ValueError("invalid_plane_normal")
            plane.SetNormal(*normal)
            plane.SetOrigin(*node.get("origin", [0, 0, 0]))
            if kind == "slice":
                algorithm = vtk.vtkCutter()
                algorithm.SetCutFunction(plane)
            else:
                algorithm = vtk.vtkClipDataSet()
                algorithm.SetClipFunction(plane)
                algorithm.SetInsideOut(bool(node.get("invert", False)))
            generated = True
        elif kind in {"threshold", "contour"}:
            association, name = node.get("field", "").split(":", 1)
            if association not in {"point", "cell"}:
                raise ValueError("unsupported_field_association")
            data = current.GetPointData() if association == "point" else current.GetCellData()
            array = data.GetArray(name)
            if array is None or array.GetNumberOfComponents() != 1:
                raise ValueError("filter_requires_scalar_field")
            if kind == "contour":
                if association != "point" or current.GetNumberOfCells() == 0:
                    raise ValueError("contour_requires_point_scalar_topology")
                algorithm = vtk.vtkContourFilter()
                algorithm.SetValue(0, float(node["value"]))
                generated = True
            else:
                algorithm = vtk.vtkThreshold()
                low, high = float(node["lower"]), float(node["upper"])
                if low > high:
                    raise ValueError("invalid_threshold_range")
                algorithm.SetLowerThreshold(low)
                algorithm.SetUpperThreshold(high)
                algorithm.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
                algorithm.SetAllScalars(True)
            algorithm.SetInputArrayToProcess(0, 0, 0, 0 if association == "point" else 1, name)
        else:
            raise ValueError(f"unsupported_filter: {kind}")
        algorithm.SetInputData(current)
        algorithm.Update()
        current = algorithm.GetOutput()
    return current, generated
