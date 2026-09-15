"""对象、显示增量、持久 Probe 与布局的真实 VTK 验收。"""

from copy import deepcopy

import pytest
import vtk
from modules.dataAssets import source_fingerprint
from modules.visPhysField import default_spec
from modules.visPhysField.scene import Scene
from modules.visTaskManage import normalize_physical_spec, validate_file_spec


@pytest.fixture
def scene(tmp_path):
    """标量为 x+y+z，矢量恒为正 X，提供可解析的真实体场。"""
    grid = vtk.vtkImageData()
    grid.SetDimensions(5, 5, 5)
    scalar = vtk.vtkDoubleArray()
    scalar.SetName("temperature")
    vector = vtk.vtkDoubleArray()
    vector.SetName("velocity")
    vector.SetNumberOfComponents(3)
    for i in range(grid.GetNumberOfPoints()):
        scalar.InsertNextValue(sum(grid.GetPoint(i)))
        vector.InsertNextTuple3(1, 0, 0)
    grid.GetPointData().AddArray(scalar)
    grid.GetPointData().AddArray(vector)
    path = tmp_path / "volume.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(grid)
    writer.Write()
    ref = {"asset_id": "a", "revision": source_fingerprint(path)}
    value = Scene([{"ref": ref, "path": str(path)}], default_spec([{"id": "s", "ref": ref}]))
    yield value
    value.close()


def create(scene, kind, identity, params, input="base-s"):
    """经公开命令创建分析对象。"""
    return scene.command(
        {
            "operation": "object_create",
            "id": identity,
            "name": identity,
            "input": input,
            "type": kind,
            "parameters": params,
            "view": 0,
        }
    )


def test_probe_label_fits_small_viewport(scene):
    """长字段标签限制在非等分视口内，几何文字可随导出保留。"""
    from modules.visPhysField.rendering import fit_probe_label

    scene.window.SetSize(900, 600)
    renderer = scene.renderers[0]
    renderer.SetViewport(0.5, 0, 1, 0.5)
    actor, _ = fit_probe_label(
        "Probe 1\npoint:temperature: 123.456\npoint:velocity: 1, 2, 3",
        [4, 4, 4],
        0.4,
        renderer,
    )
    actor.GetMapper().Update()
    mesh = actor.GetMapper().GetInput()
    for index in range(mesh.GetNumberOfPoints()):
        renderer.SetWorldPoint(*mesh.GetPoint(index), 1)
        renderer.WorldToDisplay()
        x, y, _ = renderer.GetDisplayPoint()
        assert 450 <= x <= 900
        assert 0 <= y <= 300


def test_restored_camera_clipping_contains_visible_mesh(scene):
    """远距离相机重开及分屏后，近远平面不能裁掉网格和表面 Probe。"""
    scene.command(
        {
            "operation": "camera",
            "camera": {
                "position": [120, 80, 60],
                "focal_point": [2, 2, 2],
                "view_up": [0, 0, 1],
            },
        }
    )
    scene.command({"operation": "view_create", "view": 0, "direction": "horizontal"})
    scene.apply(scene.snapshot()["spec"])
    for renderer in scene.renderers:
        camera = renderer.GetActiveCamera()
        near, far = camera.GetClippingRange()
        transform = camera.GetViewTransformMatrix()
        for index in range(scene.datasets["base-s"].GetNumberOfPoints()):
            point = scene.datasets["base-s"].GetPoint(index)
            depth = -transform.MultiplyPoint((*point, 1))[2]
            assert near < depth < far


def test_remove_last_source_preserves_file(scene):
    """移除最后来源后仍可导入，不删除磁盘原数据。"""
    from pathlib import Path

    binding = scene.bindings[0]
    source = scene.spec["sources"][0]
    scene.command({"operation": "source_remove", "id": "s", "cascade": True})
    assert scene.snapshot()["spec"]["pipeline"] == []
    assert Path(binding["path"]).exists()
    scene.command({"operation": "append_sources", "sources": [source], "bindings": []})
    assert scene.datasets["base-s"].GetNumberOfCells() > 0


def test_camera_identity_and_unlink(scene):
    """显示、时间或布局更新保留相机身份，解除联动恢复独立相机。"""
    camera = scene.renderers[0].GetActiveCamera()
    create(scene, "slice", "slice", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    assert scene.renderers[0].GetActiveCamera() is camera
    scene.command({"operation": "view_create", "view": 0})
    scene.command({"operation": "link_views", "views": [0, 1]})
    assert scene.renderers[0].GetActiveCamera() is scene.renderers[1].GetActiveCamera()
    scene.command({"operation": "link_views", "views": []})
    assert scene.renderers[0].GetActiveCamera() is not scene.renderers[1].GetActiveCamera()


def test_local_serialization_lifetime():
    """VTK wrapper 回收不改变 native 身份，新对象不能复用旧传输身份。"""
    import gc

    from modules.visPhysField.rendering import install_local_serializers

    install_local_serializers()
    from trame_vtk.modules.vtk.serializers.utils import reference_id

    actor = vtk.vtkActor()
    prop = actor.GetProperty()
    first = reference_id(prop)
    del prop
    gc.collect()
    assert reference_id(actor.GetProperty()) == first
    identities = {reference_id(vtk.vtkActor()) for _ in range(100)}
    assert len(identities) == 100


def test_fixed_view_export_across_time(scene, tmp_path, monkeypatch):
    """时间重装后仍只渲染指定视图，输出尺寸和注记随新视口计算。"""
    from pathlib import Path

    import imageio.v2 as imageio
    from modules.visPhysField import producer

    binding = deepcopy(scene.bindings[0])
    path = Path(binding["path"])
    binding["frames"] = [
        {"time": t, "path": str(path), "revision": binding["ref"]["revision"]} for t in (0.0, 1.0)
    ]
    scene.command({"operation": "view_create", "view": 0})
    scene.command({"operation": "view_update", "view": 0, "settings": {"background": [1, 0, 0]}})
    scene.command({"operation": "view_update", "view": 1, "settings": {"background": [0, 0, 1]}})
    original = producer.capture
    seen = []

    def capture(value, path, width, height):
        """检查真实输出时刻的活动渲染器并仍执行 PNG 生成。"""
        seen.append([r.GetDraw() for r in value.renderers])
        assert value.renderers[1].GetViewport() == (0, 0, 1, 1)
        return original(value, path, width, height)

    monkeypatch.setattr(producer, "capture", capture)
    files = producer.produce(
        [binding],
        scene.snapshot()["spec"],
        {"format": "png_sequence", "times": [1.0, 0.0], "view": 1, "width": 320, "height": 240},
        tmp_path,
    )
    assert seen == [[False, True], [False, True]]
    assert len(files) == 2
    for file in files:
        picture = imageio.imread(file)
        assert picture.shape[:2] == (240, 320)
        assert picture[5, 5, 2] > 200 and picture[5, 5, 0] < 20


def test_chain_and_transaction(scene):
    create(scene, "slice", "slice", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    create(
        scene,
        "contour",
        "contour",
        {"field": {"name": "temperature"}, "values": [6]},
        input="slice",
    )
    assert scene.datasets["contour"].GetNumberOfCells() > 0
    prior = scene.datasets["slice"]
    spec = scene.snapshot()["spec"]
    with pytest.raises(ValueError, match="normal|法向"):
        scene.command(
            {"operation": "object_update", "id": "slice", "parameters": {"normal": [0, 0, 0]}}
        )
    assert scene.datasets["slice"] is prior
    assert scene.snapshot()["spec"] == spec
    with pytest.raises(ValueError, match="confirmation"):
        scene.command({"operation": "object_delete", "id": "slice"})
    scene.command({"operation": "object_delete", "id": "slice", "cascade": True})
    assert "contour" not in scene.datasets


def test_begin_slice_twice_keeps_one_draft(scene):
    """连点切面只保留一份未应用草稿，输入仍是已导入对象。"""
    from modules.visPhysField.trameUI.controller import Workbench

    class State(dict):
        def __getattr__(self, name):
            return self[name]

        def __setattr__(self, name, value):
            self[name] = value

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    workbench = Workbench(type("Server", (), {"state": State()})(), scene)
    workbench.view = type("View", (), {"update": staticmethod(lambda: pytest.fail("创建草稿不应重推整屏"))})()
    parent = scene.spec["pipeline"][0]["id"]
    workbench.begin("slice")
    first = workbench.server.state.selected
    assert workbench.drafts[first]["node"]["input"] == parent
    workbench.begin("slice")
    assert workbench.server.state.selected == first
    assert len([d for d in workbench.drafts.values() if d["node"].get("type") == "slice"]) == 1
    workbench.begin("clip")
    clip = workbench.server.state.selected
    assert clip != first
    assert workbench.drafts[clip]["node"]["input"] == parent


def test_hide_base_display_does_not_rebuild_mesh(scene, monkeypatch):
    """隐藏基础显示只改 actor 显隐，不 snapshot、不重建映射。"""
    from copy import deepcopy

    from modules.visPhysField.trameUI.controller import Workbench

    spec = deepcopy(scene.spec)
    spec["pipeline"] = [
        {
            "id": "base-s",
            "name": "基础显示",
            "type": "surface",
            "input": "s",
            "parameters": {},
        }
    ]
    spec["layers"] = [
        {"id": "layer-base", "input": "base-s", "view": 0, "visible": True}
    ]
    scene.apply(spec)
    layer_id = next(item["id"] for item in scene.spec["layers"] if item["input"] == "base-s")
    actor = scene.actors[layer_id]
    mapper = actor.GetMapper()

    class State(dict):
        def __getattr__(self, name):
            return self[name]

        def __setattr__(self, name, value):
            self[name] = value

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    workbench = Workbench(type("Server", (), {"state": State(tree_nodes=[])})(), scene)
    workbench.refresh(update_view=False)
    reads = {"n": 0}
    builds = {"n": 0}
    original_snapshot = scene.snapshot
    original_build = scene.build_display

    def counted_snapshot():
        reads["n"] += 1
        return original_snapshot()

    def counted_build(mesh, layer):
        builds["n"] += 1
        return original_build(mesh, layer)

    monkeypatch.setattr(scene, "snapshot", counted_snapshot)
    monkeypatch.setattr(scene, "build_display", counted_build)
    monkeypatch.setattr(scene, "apply", lambda *_: pytest.fail("显隐不应整场景 apply"))
    workbench.visible("base-s")
    assert reads["n"] == 0
    assert builds["n"] == 0
    assert actor.GetMapper() is mapper
    assert not actor.GetVisibility()
    assert scene.spec["layers"][0]["visible"] is False
    workbench.visible("base-s")
    assert actor.GetVisibility()
    assert scene.spec["layers"][0]["visible"] is True


def test_asset_tree_exposes_named_delete_icon():
    """可视化资产树行内提供删除图标，确认框仍走级联删除。"""
    from pathlib import Path

    from modules.visPhysField.trameUI.controller import Workbench

    panel = Path(__file__).resolve().parents[2] / "modules/visPhysField/trameUI/pipelinePanel.py"
    text = panel.read_text(encoding="utf-8")
    assert "mdi-delete-outline" in text
    assert "request_delete" in text
    assert hasattr(Workbench, "request_delete")


def test_display_never_executes_filters(scene, monkeypatch):
    create(scene, "slice", "slice", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    from modules.visPhysField.modules.fieldVisualization import cutAnalysis

    monkeypatch.setattr(
        cutAnalysis, "execute_analysis", lambda *_: pytest.fail("显示修改不应运行过滤器")
    )
    mesh = scene.datasets["slice"]
    actor = next(scene.actors[l["id"]] for l in scene.spec["layers"] if l["input"] == "slice")
    camera = scene.renderers[0].GetActiveCamera()
    scene.command(
        {
            "operation": "display",
            "id": "slice",
            "view": 0,
            "field": {"name": "temperature"},
            "style": {"opacity": 0.3},
            "color": {"preset": "Rainbow", "bands": 16},
        }
    )
    assert scene.datasets["slice"] is mesh and scene.renderers[0].GetActiveCamera() is camera
    assert actor.GetProperty().GetOpacity() == 0.3
    assert actor.GetMapper().GetLookupTable().GetNumberOfTableValues() == 16


def test_clip_copy_and_field_separation(scene):
    create(scene, "clip", "clip", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    assert scene.datasets["clip"].GetBounds()[0] >= 2
    create(
        scene,
        "streamline",
        "stream",
        {
            "field": {"name": "velocity"},
            "seed_start": [1, 1, 1],
            "seed_end": [1, 3, 3],
            "length": 10,
        },
    )
    scene.command(
        {"operation": "display", "id": "stream", "view": 0, "field": {"name": "temperature"}}
    )
    assert (
        next(n for n in scene.spec["pipeline"] if n["id"] == "stream")["parameters"]["field"][
            "name"
        ]
        == "velocity"
    )
    scene.command({"operation": "object_copy", "id": "clip"})
    assert len([n for n in scene.spec["pipeline"] if n["type"] == "clip"]) == 2


def test_probe_layout_and_stable_ids(scene):
    scene.command(
        {
            "operation": "probe_create",
            "id": "p",
            "name": "Probe 1",
            "input": "base-s",
            "position": [1, 1, 1],
            "view": 0,
        }
    )
    assert scene.snapshot()["probes"]["p"]["values"]["temperature"] == [3]
    scene.command({"operation": "probe_update", "id": "p", "position": [100, 1, 1]})
    assert scene.snapshot()["probes"]["p"]["valid"] is False
    scene.command({"operation": "view_create", "view": 0})
    scene.command({"operation": "view_create", "view": 1, "direction": "vertical"})
    assert len(scene.renderers) == 3
    scene.command(
        {"operation": "display", "id": "base-s", "view": 2, "field": {"name": "temperature"}}
    )
    assert next(l for l in scene.spec["layers"] if l["view"] == 0).get("field") is None
    scene.command({"operation": "view_close", "view": 1})
    assert [v["id"] for v in scene.spec["views"]] == [0, 2]
    assert len(scene.spec["probes"]) == 1


def test_v1_upgrade_does_not_mutate_history(scene):
    old = {
        "schema_version": 1,
        "kind": "phys_field",
        "sources": deepcopy(scene.spec["sources"]),
        "pipeline": [],
        "layers": [{"id": "old", "input": "s"}],
        "views": [{"id": 0}],
    }
    before = deepcopy(old)
    new = normalize_physical_spec(old)
    assert old == before and new["schema_version"] == 2
    assert new["layers"][0]["input"] == "base-s"
    assert validate_file_spec(new) == new
    broken = deepcopy(new)
    broken["layout"] = {"view": 9}
    with pytest.raises(ValueError, match="layout"):
        validate_file_spec(broken)


def test_append_failure_preserves_bindings_and_scene(scene, tmp_path):
    before = scene.snapshot()["spec"]
    bindings = scene.bindings
    with pytest.raises(FileNotFoundError, match="source_missing"):
        scene.command(
            {
                "operation": "append_sources",
                "sources": [{"id": "bad", "ref": {"asset_id": "bad", "revision": "gone"}}],
                "bindings": [
                    {
                        "ref": {"asset_id": "bad", "revision": "gone"},
                        "path": str(tmp_path / "gone.vti"),
                    }
                ],
            }
        )
    assert scene.bindings is bindings and scene.snapshot()["spec"] == before


def test_geometry_reuse_keeps_current_frame_fields():
    """同拓扑复用不能清空新帧字段或恢复旧帧数值。"""
    from modules.visEngine import reuse_geometry

    first = vtk.vtkImageData()
    first.SetDimensions(2, 2, 2)
    second = vtk.vtkImageData()
    second.SetDimensions(2, 2, 2)
    for grid, value in [(first, 1), (second, 9)]:
        a = vtk.vtkDoubleArray()
        a.SetName("p")
        a.SetNumberOfTuples(8)
        a.Fill(value)
        grid.GetPointData().AddArray(a)
    previous = reuse_geometry(first, None)
    reuse_geometry(second, previous)
    assert first.GetPointData().GetArray("p").GetTuple1(0) == 1
    assert second.GetPointData().GetArray("p").GetTuple1(0) == 9


def test_probe_same_name_point_cell_fields(scene):
    """同名点场与单元场必须能够分别选择。"""
    from modules.visEngine import probe

    mesh = scene.datasets["s"]
    array = vtk.vtkDoubleArray()
    array.SetName("temperature")
    array.SetNumberOfTuples(mesh.GetNumberOfCells())
    array.Fill(100)
    mesh.GetCellData().AddArray(array)
    row = probe(mesh, [[1, 1, 1]])[0]
    assert row["fields"]["point:temperature"] == [3]
    assert row["fields"]["cell:temperature"] == [100]


def test_renderer_pool_is_bounded_and_stable(scene):
    """连续重建视图复用渲染器，避免 Trame 注册回调对象中途析构。"""
    first = scene.renderers[0]
    for _ in range(5):
        scene.command({"operation": "view_create", "view": 0})
        last = scene.spec["views"][-1]["id"]
        scene.command({"operation": "view_close", "view": last})
    assert scene.renderers[0] is first
    assert len(scene.renderer_pool) == 2


@pytest.mark.parametrize("extent", [0.001, 1, 1000])
def test_annotation_pixel_scale_is_independent_of_data_units(scene, extent):
    """毫米或千米尺度的模型均保持同样标签字号，导出尺寸变化也一致。"""
    from modules.visPhysField.rendering import pixel_scale

    renderer = scene.renderers[0]
    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, 0, 10 * extent)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 1, 0)
    for size in [(1280, 720), (1920, 1080)]:
        scene.window.SetSize(*size)
        step = pixel_scale(renderer, [0, 0, 0], 12)
        renderer.SetWorldPoint(0, 0, 0, 1)
        renderer.WorldToDisplay()
        start = renderer.GetDisplayPoint()[1]
        renderer.SetWorldPoint(0, step, 0, 1)
        renderer.WorldToDisplay()
        assert renderer.GetDisplayPoint()[1] - start == pytest.approx(12)


def test_multiple_legends_do_not_overlap(scene):
    """不同对象的自动范围可不同，色标必须分别保留而不是叠加或合并。"""
    from modules.visPhysField.rendering import arrange_legends

    renderer = scene.renderers[0]
    legends = [vtk.vtkScalarBarActor(), vtk.vtkScalarBarActor()]
    for legend in legends:
        renderer.AddViewProp(legend)
    arrange_legends(renderer)
    upper, lower = legends
    assert lower.GetPosition()[1] + lower.GetHeight() < upper.GetPosition()[1]
    assert 0 <= lower.GetPosition()[1]
    assert upper.GetPosition()[1] + upper.GetHeight() <= 1


def test_streamline_surface_seed_and_delete_dependency(scene):
    """切面可作为流线种子；删除切面需确认并带走流线。"""
    create(scene, "slice", "slice", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    create(
        scene,
        "streamline",
        "stream",
        {
            "field": {"name": "velocity"},
            "seed_type": "surface",
            "seed_surface": {"kind": "object", "id": "slice"},
            "seeds": 8,
            "length": 10,
        },
    )
    assert scene.datasets["stream"].GetNumberOfCells() > 0
    assert any(scene.snapshot()["attachments"]["seeds"].values())
    scene.command({"operation": "display", "id": "stream", "view": 0, "visible": False})
    assert not any(scene.snapshot()["attachments"]["seeds"].values())
    scene.command({"operation": "display", "id": "stream", "view": 0, "visible": True})
    values = {item["value"] for item in scene.seed_surface_items()}
    assert "object:slice" in values
    assert not any("clip" in item["value"] for item in scene.seed_surface_items())
    with pytest.raises(ValueError, match="confirmation"):
        scene.command({"operation": "object_delete", "id": "slice"})
    scene.command({"operation": "object_delete", "id": "slice", "cascade": True})
    assert "stream" not in scene.datasets


def test_old_streamline_line_seed_without_type(scene):
    """旧配置只有起终点时仍按线段计算。"""
    create(
        scene,
        "streamline",
        "legacy",
        {"field": {"name": "velocity"}, "seed_start": [1, 1, 1], "seed_end": [1, 3, 3], "length": 10},
    )
    assert scene.datasets["legacy"].GetNumberOfCells() > 0
    assert next(n for n in scene.spec["pipeline"] if n["id"] == "legacy")["parameters"].get(
        "seed_type"
    ) in (None, "line")


def test_plane_widget_preview_requires_apply(scene):
    """选中切面显示可视平面；拖动不切开，应用后才跟上。"""
    create(scene, "slice", "slice", {"origin": [2, 0, 0], "normal": [1, 0, 0]})
    prior = scene.datasets["slice"]
    assert not scene.snapshot()["attachments"]["plane_widget"]["visible"]
    scene.show_plane_widget([2, 0, 0], [1, 0, 0], scene.datasets["base-s"].GetBounds(), 0)
    assert set(scene.snapshot()["attachments"]["plane_widget"]["handles"]) >= {
        "plane",
        "axis_x",
        "axis_y",
        "axis_z",
        "rotate",
    }
    scene.clear_plane_widget()
    assert not scene.snapshot()["attachments"]["plane_widget"]["visible"]
    preview = scene.command(
        {
            "operation": "plane_drag",
            "handle": "axis_x",
            "origin": [2, 0, 0],
            "normal": [1, 0, 0],
            "start": [[0, 0, 0], [4, 0, 0]],
            "end": [[1, 0, 0], [5, 0, 0]],
            "input": "base-s",
            "view": 0,
        }
    )
    assert preview["origin"][0] != 2
    assert preview["normal"] == [1, 0, 0]
    assert scene.datasets["slice"] is prior
    assert scene.snapshot()["attachments"]["plane_widget"]["visible"]
    assert scene.pick_plane_widget([[80, 80, 80], [81, 80, 80]]) is None
    scene.command(
        {
            "operation": "object_update",
            "id": "slice",
            "parameters": {"origin": preview["origin"], "normal": preview["normal"]},
        }
    )
    assert scene.datasets["slice"] is not prior
    scene.command(
        {
            "operation": "display",
            "id": "slice",
            "view": 0,
            "style": {"opacity": 0.4},
        }
    )
    assert scene.actors[next(l["id"] for l in scene.spec["layers"] if l["input"] == "slice")].GetProperty().GetOpacity() == 0.4


def test_named_block_seed_from_authorized_file(tmp_path):
    """带名称的二维块可作为种子；无名块不出现。"""
    from pathlib import Path

    from modules.visDatasets import list_named_blocks
    from modules.dataAssets import source_fingerprint
    from modules.visPhysField.scene import Scene
    from modules.visPhysField import default_spec

    volume = vtk.vtkImageData()
    volume.SetDimensions(4, 4, 4)
    vector = vtk.vtkDoubleArray()
    vector.SetName("velocity")
    vector.SetNumberOfComponents(3)
    for _ in range(volume.GetNumberOfPoints()):
        vector.InsertNextTuple3(1, 0, 0)
    volume.GetPointData().AddArray(vector)
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(0, 0, 0)
    plane.SetPoint1(1, 0, 0)
    plane.SetPoint2(0, 1, 0)
    plane.Update()
    inlet = plane.GetOutput()
    names = vtk.vtkStringArray()
    names.SetName("RegionName")
    for _ in range(inlet.GetNumberOfCells()):
        names.InsertNextValue("inlet")
    inlet.GetCellData().AddArray(names)
    composite = vtk.vtkMultiBlockDataSet()
    composite.SetNumberOfBlocks(2)
    composite.SetBlock(0, volume)
    composite.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), "field")
    composite.SetBlock(1, inlet)
    composite.GetMetaData(1).Set(vtk.vtkCompositeDataSet.NAME(), "inlet")
    path = tmp_path / "named.vtm"
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(composite)
    writer.Write()
    blocks = list_named_blocks(Path(path))
    assert any(block["name"] == "inlet" for block in blocks)
    assert all(block.get("name") for block in blocks)
    ref = {"asset_id": "named", "revision": source_fingerprint(path)}
    scene = Scene(
        [{"ref": ref, "path": str(path)}],
        default_spec([{"id": "s", "ref": ref, "block": 0}]),
    )
    try:
        create(
            scene,
            "streamline",
            "from-block",
            {
                "field": {"name": "velocity"},
                "seed_type": "surface",
                "seed_surface": {"kind": "block", "index": 1, "name": "inlet"},
                "seeds": 6,
                "length": 2,
            },
        )
        assert scene.datasets["from-block"].GetNumberOfCells() >= 0
        assert any(item["value"].startswith("block:") for item in scene.seed_surface_items())
    finally:
        scene.close()


def test_named_blocks_cache_same_file(tmp_path, monkeypatch):
    """同一文件的命名块清单只读盘一次，内容变化后才重新列出。"""
    from ai4e_viz.inspect import mesh as mesh_mod
    from modules.visDatasets import list_named_blocks
    from modules.visDatasets import physicalDataset

    volume = vtk.vtkImageData()
    volume.SetDimensions(3, 3, 3)
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(0, 0, 0)
    plane.SetPoint1(1, 0, 0)
    plane.SetPoint2(0, 1, 0)
    plane.Update()
    inlet = plane.GetOutput()
    composite = vtk.vtkMultiBlockDataSet()
    composite.SetNumberOfBlocks(2)
    composite.SetBlock(0, volume)
    composite.GetMetaData(0).Set(vtk.vtkCompositeDataSet.NAME(), "field")
    composite.SetBlock(1, inlet)
    composite.GetMetaData(1).Set(vtk.vtkCompositeDataSet.NAME(), "inlet")
    path = tmp_path / "named.vtm"
    writer = vtk.vtkXMLMultiBlockDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(composite)
    writer.Write()
    physicalDataset._NAMED_BLOCK_CACHE.clear()
    reads = {"n": 0}
    original = mesh_mod._read

    def counted(target, reader=None):
        reads["n"] += 1
        return original(target, reader)

    monkeypatch.setattr(mesh_mod, "_read", counted)
    first = list_named_blocks(path)
    second = list_named_blocks(path)
    assert reads["n"] == 1
    assert first == second
    assert any(block["name"] == "inlet" for block in first)
    empty = tmp_path / "plain.vti"
    image = vtk.vtkXMLImageDataWriter()
    image.SetFileName(str(empty))
    image.SetInputData(volume)
    image.Write()
    assert list_named_blocks(empty) == []
    assert list_named_blocks(empty) == []
    assert reads["n"] == 2
