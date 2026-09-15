"""流线种子几何；只消费网格与参数，不读文件、不认会话。"""

import math

import vtk


SEED_TYPES = ("line", "sphere", "plane", "surface")


def seed_type(params: dict) -> str:
    """缺省按线段，兼容只有起终点的旧流线。"""
    kind = params.get("seed_type") or "line"
    if kind not in SEED_TYPES:
        raise ValueError("invalid_seed_type")
    return kind


def seed_count(params: dict) -> int:
    """种子数限制在可积分的范围内，避免一次放出过多轨迹。"""
    return max(1, min(1000, int(params.get("seeds", 20))))


def seed_defaults(bounds) -> dict:
    """按输入包围盒给出落在域内的起点和几何积分长度。"""
    xmin, xmax, ymin, ymax, zmin, zmax = [float(v) for v in bounds]
    center = [(xmin + xmax) / 2, (ymin + ymax) / 2, (zmin + zmax) / 2]
    extents = [xmax - xmin, ymax - ymin, zmax - zmin]
    diagonal = math.sqrt(sum(value * value for value in extents)) or 1.0
    axis = max(range(3), key=lambda index: extents[index])
    half = 0.3 * (extents[axis] or diagonal)
    start, end = list(center), list(center)
    start[axis] -= half
    end[axis] += half
    return {
        "seed_start": start,
        "seed_end": end,
        "seed_center": list(center),
        "seed_radius": max(1e-6, 0.12 * diagonal),
        "seed_origin": list(center),
        "seed_normal": [0.0, 0.0, 1.0],
        "seed_width": max(1e-6, 0.4 * (extents[0] or diagonal)),
        "seed_height": max(1e-6, 0.4 * (extents[1] or diagonal)),
        "seeds": 20,
        "length": max(1e-6, 0.6 * diagonal),
    }


def _vector(values, default):
    """要求恰好三个有限分量。"""
    point = list(values if values is not None else default)
    if len(point) != 3 or not all(math.isfinite(float(x)) for x in point):
        raise ValueError("invalid_seed_vector")
    return [float(x) for x in point]


def _normalize(vector):
    """法向必须能定义方向，零向量拒绝。"""
    length = math.sqrt(sum(x * x for x in vector))
    if length == 0:
        raise ValueError("zero_plane_normal")
    return [x / length for x in vector]


def _plane_corners(origin, normal, width, height):
    """用法向和两个切向搭出有限矩形，供种子和预览共用。"""
    normal = _normalize(normal)
    helper = [1.0, 0.0, 0.0] if abs(normal[0]) < 0.9 else [0.0, 1.0, 0.0]
    tangent = [
        normal[1] * helper[2] - normal[2] * helper[1],
        normal[2] * helper[0] - normal[0] * helper[2],
        normal[0] * helper[1] - normal[1] * helper[0],
    ]
    tangent = _normalize(tangent)
    bitangent = [
        normal[1] * tangent[2] - normal[2] * tangent[1],
        normal[2] * tangent[0] - normal[0] * tangent[2],
        normal[0] * tangent[1] - normal[1] * tangent[0],
    ]
    origin = _vector(origin, [0, 0, 0])
    start = [
        origin[i] - 0.5 * width * tangent[i] - 0.5 * height * bitangent[i] for i in range(3)
    ]
    point1 = [start[i] + width * tangent[i] for i in range(3)]
    point2 = [start[i] + height * bitangent[i] for i in range(3)]
    return start, point1, point2


def _polydata_from_source(source):
    source.Update()
    return source.GetOutput()


def is_surface_mesh(mesh) -> bool:
    """体网格不投影；多边形表面才沿切向积分。"""
    if mesh.IsA("vtkImageData") or mesh.IsA("vtkRectilinearGrid") or mesh.IsA("vtkStructuredGrid"):
        if hasattr(mesh, "GetDimensions"):
            dimensions = [0, 0, 0]
            mesh.GetDimensions(dimensions)
            return sum(value > 1 for value in dimensions) <= 2
        return False
    if mesh.IsA("vtkPolyData"):
        return mesh.GetNumberOfPolys() > 0 or mesh.GetNumberOfStrips() > 0
    if mesh.GetNumberOfCells() <= 0:
        return False
    sample = {0, mesh.GetNumberOfCells() // 2, mesh.GetNumberOfCells() - 1}
    return max(mesh.GetCell(index).GetCellDimension() for index in sample) <= 2


def snap_seed_points(seeds, mesh):
    """把种子贴到速度网格最近处，避免包围盒中心线段错过薄表面。"""
    if seeds.GetNumberOfPoints() <= 0 or mesh.GetNumberOfCells() <= 0:
        return seeds
    locator = vtk.vtkCellLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    snapped = vtk.vtkPolyData()
    snapped.DeepCopy(seeds)
    points = snapped.GetPoints()
    closest = [0.0, 0.0, 0.0]
    cell_id = vtk.mutable(0)
    sub_id = vtk.mutable(0)
    distance = vtk.mutable(0.0)
    for index in range(points.GetNumberOfPoints()):
        locator.FindClosestPoint(points.GetPoint(index), closest, cell_id, sub_id, distance)
        points.SetPoint(index, closest)
    points.Modified()
    return snapped


def project_surface_vectors(mesh, name: str):
    """表面速度去掉法向分量，避免一步就离开网格后积分为空。"""
    import numpy as np
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    surface = mesh
    if not mesh.IsA("vtkPolyData"):
        extract = vtk.vtkDataSetSurfaceFilter()
        extract.SetInputData(mesh)
        extract.Update()
        surface = extract.GetOutput()
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(surface)
    normals.ComputePointNormalsOn()
    normals.SplittingOff()
    normals.Update()
    oriented = vtk.vtkPolyData()
    oriented.DeepCopy(normals.GetOutput())
    vectors = oriented.GetPointData().GetArray(name)
    normal = oriented.GetPointData().GetNormals()
    if vectors is None or normal is None:
        return oriented
    values = vtk_to_numpy(vectors).astype(float)
    if values.ndim != 2 or values.shape[1] != 3:
        return oriented
    unit = vtk_to_numpy(normal).astype(float)
    tangent = values - unit * np.sum(values * unit, axis=1)[:, None]
    array = numpy_to_vtk(tangent, deep=True)
    array.SetName(name)
    oriented.GetPointData().RemoveArray(name)
    oriented.GetPointData().AddArray(array)
    oriented.GetPointData().SetActiveVectors(name)
    return oriented


def sample_seed_points(mesh, count: int):
    """优先抽单元中心，面太大时不把全部顶点当作种子。"""
    source = mesh
    if mesh.GetNumberOfCells() > 0:
        centers = vtk.vtkCellCenters()
        centers.SetInputData(mesh)
        centers.VertexCellsOn()
        centers.Update()
        if centers.GetOutput().GetNumberOfPoints() > 0:
            source = centers.GetOutput()
    total = source.GetNumberOfPoints()
    if total <= 0:
        raise ValueError("empty_seed_source")
    count = max(1, min(1000, int(count)))
    points = vtk.vtkPoints()
    step = 1 if total <= count else total / count
    taken = total if total <= count else count
    for index in range(taken):
        points.InsertNextPoint(source.GetPoint(min(total - 1, int(index * step))))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    verts = vtk.vtkCellArray()
    for index in range(points.GetNumberOfPoints()):
        verts.InsertNextCell(1)
        verts.InsertCellPoint(index)
    poly.SetVerts(verts)
    return poly


def list_named_regions(mesh) -> list[dict]:
    """只收集文字分区名；无名整数分区不猜测。"""
    regions = []
    seen = set()
    for association, data in (("point", mesh.GetPointData()), ("cell", mesh.GetCellData())):
        for index in range(data.GetNumberOfArrays()):
            array = data.GetAbstractArray(index)
            if array is None or not array.IsA("vtkStringArray"):
                continue
            array_name = array.GetName() or f"array_{index}"
            for row in range(array.GetNumberOfValues()):
                name = array.GetValue(row)
                if not name or (association, array_name, name) in seen:
                    continue
                seen.add((association, array_name, name))
                regions.append(
                    {"name": name, "association": association, "array": array_name}
                )
    return regions


def extract_named_region(mesh, name: str):
    """按文字名称抽出对应点或单元，供流线当作种子面。"""
    if not name:
        raise ValueError("missing_seed_source")
    for association, data in (("cell", mesh.GetCellData()), ("point", mesh.GetPointData())):
        for index in range(data.GetNumberOfArrays()):
            array = data.GetAbstractArray(index)
            if array is None or not array.IsA("vtkStringArray"):
                continue
            ids = vtk.vtkIdList()
            for row in range(array.GetNumberOfValues()):
                if array.GetValue(row) == name:
                    ids.InsertNextId(row)
            if ids.GetNumberOfIds() == 0:
                continue
            if association == "cell":
                extract = vtk.vtkExtractCells()
                extract.SetInputData(mesh)
                extract.SetCellList(ids)
                extract.Update()
                result = extract.GetOutput()
            else:
                points = vtk.vtkPoints()
                for row in range(ids.GetNumberOfIds()):
                    points.InsertNextPoint(mesh.GetPoint(ids.GetId(row)))
                result = vtk.vtkPolyData()
                result.SetPoints(points)
            if result.GetNumberOfPoints() == 0:
                raise ValueError("empty_seed_source")
            return result
    raise ValueError("named_region_missing")


def build_seed_source(params: dict, seed_mesh=None):
    """生成积分用的种子点集；命名面必须由调用方先取出网格。"""
    kind = seed_type(params)
    count = seed_count(params)
    if kind == "line":
        start = _vector(params.get("seed_start"), [0, 0, 0])
        end = _vector(params.get("seed_end"), [0, 1, 0])
        if count == 1:
            source = vtk.vtkPointSource()
            source.SetCenter([(start[i] + end[i]) / 2 for i in range(3)])
            source.SetRadius(0)
            source.SetNumberOfPoints(1)
            return _polydata_from_source(source)
        source = vtk.vtkLineSource()
        source.SetPoint1(start)
        source.SetPoint2(end)
        source.SetResolution(count - 1)
        return _polydata_from_source(source)
    if kind == "sphere":
        source = vtk.vtkPointSource()
        source.SetCenter(_vector(params.get("seed_center"), [0, 0, 0]))
        source.SetRadius(max(0.0, float(params.get("seed_radius", 1))))
        source.SetNumberOfPoints(count)
        source.SetDistributionToShell()
        return _polydata_from_source(source)
    if kind == "plane":
        width = max(1e-6, float(params.get("seed_width", 1)))
        height = max(1e-6, float(params.get("seed_height", 1)))
        origin, point1, point2 = _plane_corners(
            params.get("seed_origin") or params.get("origin") or [0, 0, 0],
            params.get("seed_normal") or params.get("normal") or [0, 0, 1],
            width,
            height,
        )
        axis_u = [point1[i] - origin[i] for i in range(3)]
        axis_v = [point2[i] - origin[i] for i in range(3)]
        columns = max(1, int(round(math.sqrt(count))))
        rows = max(1, math.ceil(count / columns))
        points = vtk.vtkPoints()
        verts = vtk.vtkCellArray()
        taken = 0
        for row in range(rows):
            for column in range(columns):
                if taken >= count:
                    break
                su = 0.0 if columns == 1 else column / (columns - 1)
                sv = 0.0 if rows == 1 else row / (rows - 1)
                points.InsertNextPoint(
                    [origin[i] + su * axis_u[i] + sv * axis_v[i] for i in range(3)]
                )
                verts.InsertNextCell(1)
                verts.InsertCellPoint(taken)
                taken += 1
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        poly.SetVerts(verts)
        return poly
    if seed_mesh is None:
        raise ValueError("missing_seed_source")
    return sample_seed_points(seed_mesh, count)


def seed_preview_mesh(params: dict, seed_mesh=None):
    """显示用几何：线/球/面画形状，命名面只标采样点。"""
    kind = seed_type(params)
    if kind == "sphere":
        source = vtk.vtkSphereSource()
        source.SetCenter(_vector(params.get("seed_center"), [0, 0, 0]))
        source.SetRadius(max(0.0, float(params.get("seed_radius", 1))))
        source.SetPhiResolution(16)
        source.SetThetaResolution(16)
        return _polydata_from_source(source)
    if kind == "plane":
        width = max(1e-6, float(params.get("seed_width", 1)))
        height = max(1e-6, float(params.get("seed_height", 1)))
        origin, point1, point2 = _plane_corners(
            params.get("seed_origin") or params.get("origin") or [0, 0, 0],
            params.get("seed_normal") or params.get("normal") or [0, 0, 1],
            width,
            height,
        )
        source = vtk.vtkPlaneSource()
        source.SetOrigin(origin)
        source.SetPoint1(point1)
        source.SetPoint2(point2)
        source.SetXResolution(1)
        source.SetYResolution(1)
        return _polydata_from_source(source)
    return build_seed_source(params, seed_mesh)
