"""空间插值与实体查询是两个独立的数值操作。"""

import vtk


def probe(mesh, positions: list) -> list[dict]:
    """域外位置保留 valid=false，不以零值冒充有效样本。"""
    points = vtk.vtkPoints()
    for position in positions:
        points.InsertNextPoint(position)
    samples = vtk.vtkPolyData()
    samples.SetPoints(points)
    query = vtk.vtkProbeFilter()
    query.SetInputData(samples)
    query.SetSourceData(mesh)
    query.Update()
    data = query.GetOutput().GetPointData()
    mask = data.GetArray("vtkValidPointMask")
    # 显式前缀避免同名 PointData / CellData 被 vtkProbeFilter 覆盖。
    copy = mesh.NewInstance()
    copy.ShallowCopy(mesh)
    for association, getter in [("point", "GetPointData"), ("cell", "GetCellData")]:
        original = getattr(mesh, getter)()
        target = getattr(copy, getter)()
        target.Initialize()
        for j in range(original.GetNumberOfArrays()):
            a = original.GetArray(j)
            if a is None:
                continue
            named = a.NewInstance()
            named.DeepCopy(a)
            named.SetName(association + ":" + a.GetName())
            target.AddArray(named)
    qualified = vtk.vtkProbeFilter()
    qualified.SetInputData(samples)
    qualified.SetSourceData(copy)
    qualified.Update()
    typed = qualified.GetOutput().GetPointData()
    return [
        {
            "position": list(position),
            "valid": bool(mask.GetTuple1(i)),
            "values": {
                data.GetArrayName(j): list(data.GetArray(j).GetTuple(i))
                for j in range(data.GetNumberOfArrays())
                if data.GetArrayName(j) != "vtkValidPointMask" and data.GetArray(j)
            }
            if mask.GetTuple1(i)
            else None,
            "fields": {
                typed.GetArrayName(j): list(typed.GetArray(j).GetTuple(i))
                for j in range(typed.GetNumberOfArrays())
                if typed.GetArrayName(j) != "vtkValidPointMask" and typed.GetArray(j)
            }
            if mask.GetTuple1(i)
            else None,
        }
        for i, position in enumerate(positions)
    ]


def entity(mesh, association: str, identity: int) -> dict:
    """按当前网格实体序号查询，同时返回已有原始 ID 字段。"""
    if association not in ("point", "cell"):
        raise ValueError("invalid_entity_association")
    count = mesh.GetNumberOfPoints() if association == "point" else mesh.GetNumberOfCells()
    if not 0 <= identity < count:
        raise ValueError("entity_outside_range")
    attributes = mesh.GetPointData() if association == "point" else mesh.GetCellData()
    return {
        "association": association,
        "id": identity,
        "values": {
            attributes.GetArrayName(j): list(attributes.GetArray(j).GetTuple(identity))
            for j in range(attributes.GetNumberOfArrays())
        },
    }


def pick_ray(mesh, ray: list, association="cell") -> dict:
    """射线求交定位真实实体，区别于空间坐标的插值 Probe。"""
    if len(ray) != 2 or any(len(p) != 3 for p in ray):
        raise ValueError("invalid_pick_ray")
    locator = vtk.vtkCellLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    t, sub, cell = vtk.mutable(0.0), vtk.mutable(0), vtk.mutable(-1)
    position, pcoords = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    found = locator.IntersectWithLine(ray[0], ray[1], 1e-6, t, position, pcoords, sub, cell)
    if not found:
        return {"valid": False, "values": None}
    identity = int(cell)
    if association == "point":
        points = vtk.vtkPointLocator()
        points.SetDataSet(mesh)
        points.BuildLocator()
        identity = points.FindClosestPoint(position)
    return {"valid": True, "position": position, **entity(mesh, association, identity)}
