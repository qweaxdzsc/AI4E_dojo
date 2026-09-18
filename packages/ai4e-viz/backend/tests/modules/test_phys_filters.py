"""解析场数值验收，使用非零常矢量和线性标量验证真实计算。"""
import numpy as np
import pytest
import vtk
from vtk.util.numpy_support import numpy_to_vtk
from modules.visEngine import apply_filter, probe, entity, style_streamline_mesh, streamline_style


@pytest.fixture
def mesh():
    grid = vtk.vtkImageData()
    grid.SetDimensions(9, 9, 9)
    grid.SetOrigin(-1, -1, -1)
    grid.SetSpacing(.25, .25, .25)
    coords = np.asarray([grid.GetPoint(i) for i in range(grid.GetNumberOfPoints())])
    for name, values in [('pressure', coords[:, 0] + 2*coords[:, 1]), ('velocity', np.tile([1., 0., 0.], (len(coords), 1)))]:
        a = numpy_to_vtk(values, deep=True)
        a.SetName(name)
        grid.GetPointData().AddArray(a)
    return grid


def test_seed_defaults_land_inside_bounds(mesh):
    """新建流线的默认起点和积分长度落在输入包围盒尺度内。"""
    from modules.visEngine import seed_defaults

    bounds = mesh.GetBounds()
    defaults = seed_defaults(bounds)
    for key in ("seed_start", "seed_end", "seed_center", "seed_origin"):
        point = defaults[key]
        assert bounds[0] <= point[0] <= bounds[1]
        assert bounds[2] <= point[1] <= bounds[3]
        assert bounds[4] <= point[2] <= bounds[5]
    diagonal = (
        (bounds[1] - bounds[0]) ** 2 + (bounds[3] - bounds[2]) ** 2 + (bounds[5] - bounds[4]) ** 2
    ) ** 0.5
    assert 0 < defaults["length"] <= diagonal
    assert 0 < defaults["seed_radius"] <= diagonal


def test_streamline_seed_types(mesh):
    """球体、平面和切面种子都能积出流线；旧起终点仍按线段。"""
    from modules.visEngine import apply_filter, build_seed_source

    slice_mesh = apply_filter(mesh, {"type": "slice", "parameters": {"origin": [0, 0, 0], "normal": [1, 0, 0]}})
    for params in (
        {"field": {"name": "velocity"}, "seed_start": [0, -0.5, 0], "seed_end": [0, 0.5, 0], "length": 1},
        {
            "field": {"name": "velocity"},
            "seed_type": "sphere",
            "seed_center": [0, 0, 0],
            "seed_radius": 0.4,
            "seeds": 12,
            "length": 1,
        },
        {
            "field": {"name": "velocity"},
            "seed_type": "plane",
            "seed_origin": [0, 0, 0],
            "seed_normal": [0, 0, 1],
            "seed_width": 1,
            "seed_height": 1,
            "seeds": 16,
            "length": 1,
        },
        {
            "field": {"name": "velocity"},
            "seed_type": "surface",
            "seeds": 8,
            "length": 1,
        },
    ):
        seed = slice_mesh if params.get("seed_type") == "surface" else None
        output = apply_filter(mesh, {"type": "streamline", "parameters": params}, seed)
        assert output.GetNumberOfCells() > 0
        if params.get("seed_type") == "surface":
            assert build_seed_source(params, slice_mesh).GetNumberOfPoints() > 0


def test_streamline_snaps_off_domain_seeds(mesh):
    """域外种子先贴到网格再积分，避免薄表面或包围盒中心落空。"""
    output = apply_filter(
        mesh,
        {
            "type": "streamline",
            "parameters": {
                "field": {"name": "velocity"},
                "seed_start": [20, 0, 0],
                "seed_end": [20, 0.5, 0],
                "length": 1,
            },
        },
    )
    assert output.GetNumberOfCells() > 0


def test_surface_streamline_from_offset_seeds():
    """表面速度沿切向积分；种子在面外时仍能贴回。"""
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(-1, -1, 0)
    plane.SetPoint1(1, -1, 0)
    plane.SetPoint2(-1, 1, 0)
    plane.SetXResolution(8)
    plane.SetYResolution(8)
    plane.Update()
    surface = plane.GetOutput()
    vector = vtk.vtkDoubleArray()
    vector.SetName("velocity")
    vector.SetNumberOfComponents(3)
    for _ in range(surface.GetNumberOfPoints()):
        vector.InsertNextTuple3(1, 0, 0)
    surface.GetPointData().AddArray(vector)
    output = apply_filter(
        surface,
        {
            "type": "streamline",
            "parameters": {
                "field": {"name": "velocity"},
                "seed_start": [0, -0.4, 4],
                "seed_end": [0, 0.4, 4],
                "seeds": 6,
                "length": 1,
            },
        },
    )
    assert output.GetNumberOfCells() > 0


def test_named_region_and_empty_seed(mesh):
    """文字分区可抽出；缺种子面必须失败。"""
    from vtk.util.numpy_support import numpy_to_vtk
    from modules.visEngine import apply_filter, extract_named_region, list_named_regions

    names = vtk.vtkStringArray()
    names.SetName("patch")
    for _ in range(mesh.GetNumberOfCells()):
        names.InsertNextValue("inlet")
    mesh.GetCellData().AddArray(names)
    assert {item["name"] for item in list_named_regions(mesh)} == {"inlet"}
    region = extract_named_region(mesh, "inlet")
    assert region.GetNumberOfPoints() > 0
    with pytest.raises(ValueError, match="missing_seed_source"):
        apply_filter(
            mesh,
            {
                "type": "streamline",
                "parameters": {"field": {"name": "velocity"}, "seed_type": "surface", "length": 1},
            },
        )


def test_plane_widget_drag_does_not_cut(mesh):
    """拖动手柄只改原点和法向，不执行切开。"""
    from modules.visEngine import align_plane_normal, move_plane, pick_plane_handle, plane_widget_geometry

    origin, normal = [0.0, 0.0, 0.0], [1.0, 0.0, 0.0]
    handles = plane_widget_geometry(origin, normal, mesh.GetBounds())
    assert set(handles) >= {"plane", "axis_x", "axis_y", "axis_z", "rotate_x", "rotate_y", "rotate_z"}
    moved, same = move_plane(origin, normal, "axis_x", [[-2, 0, 0], [2, 0, 0]], [[-1, 0, 0], [3, 0, 0]])
    assert moved[0] != origin[0] and same == normal
    aligned_origin, aligned = align_plane_normal(origin, "y")
    assert aligned_origin == origin and aligned == [0.0, 1.0, 0.0]
    assert pick_plane_handle(handles, [[2, 0, 0], [-2, 0, 0]]) in {None, "axis_x", "rotate_x", "rotate_y", "rotate_z"}


def test_hex_slice_keeps_polygons(mesh):
    """平面切开关闭默认三角化，交面以四边形或多边形为主。"""
    sliced = apply_filter(
        mesh,
        {
            "type": "slice",
            "parameters": {"origin": [0, 0, 0], "normal": [1, 0, 0], "crinkle": False},
        },
    )
    sizes = [sliced.GetCell(i).GetNumberOfPoints() for i in range(sliced.GetNumberOfCells())]
    assert sizes
    assert any(count >= 4 for count in sizes)
    assert sum(count >= 4 for count in sizes) >= sum(count == 3 for count in sizes)


def test_slice_iso_glyph_streamline(mesh):
    slice = apply_filter(mesh, {'type': 'slice', 'parameters': {'origin': [0,0,0], 'normal': [1,0,0], 'crinkle': False}})
    assert slice.GetNumberOfPoints() > 0
    assert all(abs(slice.GetPoint(i)[0]) < 1e-7 for i in range(slice.GetNumberOfPoints()))
    iso = apply_filter(mesh, {'type': 'isosurface', 'parameters': {'field': {'name': 'pressure'}, 'values': [0.5]}})
    assert iso.GetNumberOfCells() > 0
    assert all(abs(iso.GetPoint(i)[0] + 2*iso.GetPoint(i)[1] - .5) < 1e-5 for i in range(iso.GetNumberOfPoints()))
    for kind in ('glyph', 'streamline'):
        output = apply_filter(mesh, {'type': kind, 'parameters': {'field': {'name': 'velocity'}, 'seed_start': [0,-.5,0], 'seed_end': [0,.5,0], 'length': 1}})
        assert output.GetNumberOfCells() > 0


def test_streamline_style_line_and_tube(mesh):
    """缺键按线；圆管改半径和圆周面数，不改积分结果身份。"""
    lines = apply_filter(
        mesh,
        {
            "type": "streamline",
            "parameters": {
                "field": {"name": "velocity"},
                "seed_start": [0, -0.5, 0],
                "seed_end": [0, 0.5, 0],
                "length": 1,
            },
        },
    )
    assert streamline_style({})["shape"] == "line"
    assert streamline_style({})["sides"] == 8
    assert style_streamline_mesh(lines, {}) is lines
    assert style_streamline_mesh(lines, {"streamline": {"shape": "line"}}) is lines
    tube = style_streamline_mesh(
        lines, {"streamline": {"shape": "tube", "thickness": 0.05, "sides": 8}}
    )
    coarse = style_streamline_mesh(
        lines, {"streamline": {"shape": "tube", "thickness": 0.05, "sides": 3}}
    )
    assert tube.GetNumberOfPolys() > 0
    assert coarse.GetNumberOfPolys() > 0
    assert tube.GetNumberOfPoints() > coarse.GetNumberOfPoints()
    assert lines.GetNumberOfLines() > 0
    assert lines.GetNumberOfPolys() == 0


def test_probe_validity_and_entity(mesh):
    rows = probe(mesh, [[.1,.2,.3], [100,100,100]])
    assert rows[0]['values']['pressure'][0] == pytest.approx(.5)
    assert rows[1] == {'position': [100,100,100], 'valid': False, 'values': None, 'fields':None}
    assert entity(mesh, 'point', 0)['values']['pressure'] == [-3.]


def _single_hex():
    grid = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    for z in (0.0, 1.0):
        for y in (0.0, 1.0):
            for x in (0.0, 1.0):
                points.InsertNextPoint(x, y, z)
    grid.SetPoints(points)
    ids = vtk.vtkIdList()
    for index in (0, 1, 3, 2, 4, 5, 7, 6):
        ids.InsertNextId(index)
    grid.InsertNextCell(vtk.VTK_HEXAHEDRON, ids)
    return grid


def test_crinkle_slice_keeps_hex_faces():
    """皱折切面保留被切到的六面体表面，不是平面三角交面。"""
    sliced = apply_filter(
        _single_hex(),
        {
            "type": "slice",
            "parameters": {"origin": [0.5, 0.5, 0.5], "normal": [1, 0, 0], "crinkle": True},
        },
    )
    sizes = [sliced.GetCell(i).GetNumberOfPoints() for i in range(sliced.GetNumberOfCells())]
    assert sizes
    assert any(count >= 4 for count in sizes)
    assert all(count != 3 for count in sizes) or sum(count >= 4 for count in sizes) >= sum(
        count == 3 for count in sizes
    )


def test_triangulate_slice_makes_triangles():
    """打开三角化后平面切开只剩三角面。"""
    sliced = apply_filter(
        _single_hex(),
        {
            "type": "slice",
            "parameters": {
                "origin": [0.5, 0.5, 0.5],
                "normal": [1, 0, 0],
                "crinkle": False,
                "triangulate": True,
            },
        },
    )
    sizes = [sliced.GetCell(i).GetNumberOfPoints() for i in range(sliced.GetNumberOfCells())]
    assert sizes
    assert all(count == 3 for count in sizes)


def test_crinkle_clip_keeps_hex_cells():
    """剖切皱折保留被切到的整格，不拆成四面体。"""
    clipped = apply_filter(
        _single_hex(),
        {
            "type": "clip",
            "parameters": {"origin": [0.5, 0.5, 0.5], "normal": [1, 0, 0], "crinkle": True},
        },
    )
    assert clipped.GetNumberOfCells() == 1
    assert clipped.GetCell(0).GetCellType() == vtk.VTK_HEXAHEDRON


def test_iso_values_can_exceed_field_range(mesh):
    """等值手填可越界，过滤器按填写值计算。"""
    output = apply_filter(
        mesh,
        {"type": "isosurface", "parameters": {"field": {"name": "pressure"}, "values": [99.0]}},
    )
    assert output.GetNumberOfCells() == 0


def test_actual_ray_pick(mesh):
    from modules.visEngine import pick_ray
    result=pick_ray(mesh, [[0,0,10],[0,0,-10]], 'cell')
    assert result['valid'] and result['association']=='cell'
    assert result['position'][2] == pytest.approx(1.)
    assert not pick_ray(mesh, [[20,0,10],[20,0,-10]])['valid']
