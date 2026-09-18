"""六手柄、独立草稿和候选预览的数值及真实状态验收。"""

from copy import deepcopy

import pytest
import vtk
from modules.visEngine import apply_filter, move_plane, plane_widget_geometry, scalar_mesh
from modules.visTaskManage import normalize_physical_spec

from .test_phys_display_updates import workspace as workspace_fixture

workspace = workspace_fixture


def test_six_handles_and_axis_rotation():
    """绕 Z 旋转九十度必须改变法向，平面边长为旧值的 2.5 倍。"""
    handles = plane_widget_geometry([0, 0, 0], [1, 0, 0], [-2, 2] * 3)
    assert set(handles) == {
        "plane",
        "border",
        "axis_x",
        "axis_y",
        "axis_z",
        "rotate_x",
        "rotate_y",
        "rotate_z",
    }
    assert handles["plane"].GetBounds()[3] - handles["plane"].GetBounds()[2] == pytest.approx(5.5)
    origin, normal = move_plane(
        [0, 0, 0], [1, 0, 0], "rotate_z", [[1, 0, 5], [1, 0, -5]], [[0, 1, 5], [0, 1, -5]]
    )
    assert origin == [0, 0, 0]
    assert normal == pytest.approx([0, 1, 0])
    with pytest.raises(ValueError):
        move_plane(origin, normal, "plane", [[0, 0, 1], [0, 0, -1]], [[1, 0, 1], [1, 0, -1]])


def test_plane_helper_and_late_display_event(workspace):
    """辅助显隐保存到显示层，迟到颜色事件不能写入父对象。"""
    ui, scene, _ = workspace
    ui.begin("slice")
    child = ui.server.state.selected
    ui.set_display("plane_visible", False)
    assert not scene.plane_widget_actors
    assert ui.apply_selected()
    layer = next(l for l in scene.spec["layers"] if l["input"] == child)
    assert layer["helpers"]["plane_visible"] is False
    ui.select("base-s")
    before = deepcopy(scene.spec)
    ui.set_display("coloring", "point|temperature", child)
    assert scene.spec == before
    scene.apply(before)
    ui.select(child)
    assert not ui.server.state.plane_visible
    assert not scene.plane_widget_actors


def test_probe_candidate_and_cancel(workspace):
    """候选球显示在草稿位置，取消不留下球或正式探针。"""
    ui, scene, _ = workspace
    ui.begin("probe")
    assert ui.xyz(ui.server.state.probe_position) == [2, 2, 2]
    assert len(scene.preview_actors) == 1
    ui.set_coordinate("probe_position", 0, "1")
    assert scene.preview_actors[0].GetMapper().GetInput().GetCenter()[0] == pytest.approx(1)
    assert scene.spec["probes"] == []
    ui.cancel_selected()
    assert scene.preview_actors == []
    assert not ui.drafts


@pytest.mark.parametrize("kind", ["line", "sphere", "plane"])
def test_seed_preview_without_filter(workspace, kind):
    """三类种子预览不创建流线计算结果。"""
    ui, scene, _ = workspace
    ui.begin("streamline")
    ui.set_parameter("seed_type", kind)
    before = dict(scene.filter_cache)
    ui.toggle_seed_preview()
    assert scene.preview_actors
    scene.add_annotations()
    assert all(scene.annotation_pool[0].HasViewProp(a) for a in scene.preview_actors)
    assert scene.filter_cache == before
    assert len(scene.spec["pipeline"]) == 1
    ui.select("base-s")
    assert not scene.preview_actors


def test_applied_streamline_hides_seeds_without_preview(workspace):
    """应用后关显示种子只藏附件，不复活预览按钮。"""
    ui, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for i in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1, 0, 0)
    mesh.GetPointData().AddArray(vectors)
    ui.refresh(update_view=False)
    ui.begin("streamline")
    ui.set_parameter("compute_field", "point|velocity")
    assert ui.apply_selected(), ui.server.state.error
    assert not ui.server.state.can_preview_seeds
    layer = next(item for item in scene.spec["layers"] if item["input"] == ui.server.state.selected)
    assert scene.seed_actors[layer["id"]]
    ui.set_display("seeds_visible", False)
    layer = next(item for item in scene.spec["layers"] if item["input"] == ui.server.state.selected)
    assert layer["helpers"]["seeds_visible"] is False
    assert all(not actor.GetVisibility() for actor in scene.seed_actors[layer["id"]])


def test_draft_seed_handles_are_disabled(workspace):
    """本期不做拖种子：草稿也不提供球体/线段/平面手柄。"""
    ui, scene, _ = workspace
    ui.begin("streamline")
    for kind in ("sphere", "line", "plane"):
        ui.set_parameter("seed_type", kind)
        ui.sync_plane_widget()
        assert ui.helper_widget_kind() is None
        assert ui.helper_widget_kind() not in ("seed", "line")
        assert ui.plane_widget_state().get("visible") is not True
    ui.plane_move(0.6, 0.5, 400, 300)
    assert ui.server.state.plane_dragging == ""


def test_plot_over_line_and_streamline_ignore_line_seed_drag(workspace):
    """平面移动只认切面手柄；残留的线/种子种类不得改线段或种子。"""
    ui, _, _ = workspace
    ui.begin("plot_over_line")
    start = ui.server.state.line_start
    end = ui.server.state.line_end
    ui.server.state.plane_dragging = "axis_x"
    ui._plane_drag_start = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
    ui._helper_kind = "line"
    ui.plane_move(0.6, 0.5, 400, 300)
    assert ui.server.state.line_start == start
    assert ui.server.state.line_end == end
    assert ui.helper_widget_kind() is None
    ui.begin("streamline")
    center = ui.server.state.seed_center
    ui.server.state.plane_dragging = "axis_x"
    ui._plane_drag_start = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
    ui._helper_kind = "seed"
    ui.plane_move(0.6, 0.5, 400, 300)
    assert ui.server.state.seed_center == center
    assert ui.helper_widget_kind() is None


def test_probe_apply_fills_table(workspace):
    """应用后按所选物理量出表，不必先点当前数值。"""
    ui, scene, _ = workspace
    ui.begin("probe")
    ui.server.state.probe_fields = ["point:temperature"]
    assert ui.apply_selected(), ui.server.state.error
    assert any("temperature" in item["field"] for item in ui.server.state.query_table)
    probe = scene.spec["probes"][0]
    assert probe["fields"] == ["point:temperature"]


def test_probe_pick_switch_matches_backend(workspace):
    """点选开关必须看得见且与后台拾取一致；关着点模型不出球。"""
    from modules.visTaskManage import probe_pick_enabled

    ui, scene, _ = workspace
    assert probe_pick_enabled({}) is False
    assert probe_pick_enabled({"position": [0, 0, 0]}) is False
    ui.begin("probe")
    assert ui.server.state.probe_pick_enabled
    assert ui.server.state.interaction_mode == "probe"
    before = ui.xyz(ui.server.state.probe_position)
    ui.set_probe_pick(False)
    assert not ui.server.state.probe_pick_enabled
    assert ui.server.state.interaction_mode == "rotate"
    ui.pick({"ray": [[1, 3, 10], [1, 3, -10]]})
    assert ui.xyz(ui.server.state.probe_position) == before
    ui.toggle_probe_pick()
    assert ui.server.state.probe_pick_enabled
    ui.pick({"ray": [[1, 3, 10], [1, 3, -10]]})
    picked = ui.xyz(ui.server.state.probe_position)
    assert picked != before
    assert scene.preview_actors
    ui.mode("rotate")
    assert not ui.server.state.probe_pick_enabled
    ui.set_probe_pick(True)
    ui.begin("slice")
    assert not ui.server.state.probe_pick_enabled
    assert ui.server.state.interaction_mode != "probe"
    ui.select("base-s")
    ui.begin("probe")
    ui.server.state.probe_fields = ["point:temperature"]
    assert ui.apply_selected(), ui.server.state.error
    probe = scene.spec["probes"][0]
    assert "pick_enabled" not in probe
    assert probe_pick_enabled(probe) is False
    stored = deepcopy(scene.spec)
    restored = normalize_physical_spec(stored)
    assert "pick_enabled" not in restored["probes"][0]
    assert stored["probes"][0] == scene.spec["probes"][0]


def test_iso_slider_keeps_overrange_value(workspace):
    """滑条改值，手填超过场范围后应用仍用该值。"""
    ui, _, _ = workspace
    ui.begin("isosurface")
    ui.set_parameter("compute_field", "point|temperature")
    ui.refresh(update_view=False)
    over = float(ui.server.state.iso_field_max) + 8
    ui.set_parameter("iso_values", str(over))
    assert ui.apply_selected(), ui.server.state.error
    node = next(item for item in ui.scene.spec["pipeline"] if item["type"] == "isosurface")
    assert node["parameters"]["values"] == [over]


def test_iso_slider_uses_selected_field_range(workspace):
    """滑条上下限等于所选场实际 min/max，值是物理量不是 0–1 归一化。"""
    ui, scene, _ = workspace
    ui.begin("isosurface")
    assert ui.server.state.compute_field == "point|temperature"
    assert float(ui.server.state.iso_field_min) == pytest.approx(0.0)
    assert float(ui.server.state.iso_field_max) == pytest.approx(12.0)
    assert float(ui.server.state.iso_slider) == pytest.approx(0.0)
    assert "12" in ui.server.state.iso_range_text
    assert ui.server.state.iso_range_hint == ""

    mesh = scene.datasets["base-s"]
    pressure = vtk.vtkDoubleArray()
    pressure.SetName("pressure")
    count = mesh.GetNumberOfPoints()
    for i in range(count):
        pressure.InsertNextValue(20 + 60 * i / max(count - 1, 1))
    mesh.GetPointData().AddArray(pressure)
    ui.refresh(update_view=False)
    ui.set_parameter("compute_field", "point|pressure")
    assert float(ui.server.state.iso_field_min) == pytest.approx(20)
    assert float(ui.server.state.iso_field_max) == pytest.approx(80)
    assert float(ui.server.state.iso_slider) == pytest.approx(50)
    assert float(ui.server.state.iso_values.split(",")[0]) == pytest.approx(50)
    assert float(ui.server.state.iso_field_max) > 1
    assert "20" in ui.server.state.iso_range_text and "80" in ui.server.state.iso_range_text
    assert ui.server.state.iso_range_hint == ""


def test_iso_slider_fallback_explains_invalid_range(workspace):
    """读不到场范围时占位 0–1 并说明，不冒充物理量。"""
    ui, _, _ = workspace
    ui.begin("isosurface")
    ui.set_parameter("compute_field", "point|missing")
    assert float(ui.server.state.iso_field_min) == 0
    assert float(ui.server.state.iso_field_max) == 1
    assert "不是物理量" in ui.server.state.iso_range_text
    assert ui.server.state.iso_range_hint


def test_iso_slider_recomputes_range_without_rewriting_spec(workspace):
    """旧对象没有保存范围时按当前网格现算，不写回 spec。"""
    ui, scene, _ = workspace
    ui.begin("isosurface")
    ui.set_parameter("iso_values", "6")
    assert ui.apply_selected(), ui.server.state.error
    node = next(item for item in scene.spec["pipeline"] if item["type"] == "isosurface")
    assert "iso_field_min" not in node
    assert "iso_field_min" not in node.get("parameters", {})
    before = deepcopy(node)
    ui.hydrate()
    ui.refresh(update_view=False)
    assert float(ui.server.state.iso_field_min) == pytest.approx(0.0)
    assert float(ui.server.state.iso_field_max) == pytest.approx(12.0)
    assert float(ui.server.state.iso_slider) == pytest.approx(6)
    node = next(item for item in scene.spec["pipeline"] if item["type"] == "isosurface")
    assert node == before


def test_automatic_contour_and_legacy(workspace):
    """自动生成内部级别，自定义列表兼容，冲突声明必须失败。"""
    ui, scene, _ = workspace
    ui.begin("contour")
    ui.set_parameter("level_count", 3)
    assert ui.apply_selected(), ui.server.state.error
    mesh = scene.datasets[ui.server.state.selected]
    arr = mesh.GetPointData().GetArray("__vis_scalar")
    assert sorted({round(arr.GetValue(i), 8) for i in range(arr.GetNumberOfTuples())}) == [3, 6, 9]
    spec = deepcopy(scene.spec)
    spec["pipeline"][-1]["parameters"]["values"] = [3]
    with pytest.raises(ValueError, match="levels"):
        normalize_physical_spec(spec)


def test_vector_magnitude_contour_keeps_computed_scalar():
    """先插值模长与插值向量后求模不同；显示必须消费等值计算标量。"""
    mesh = vtk.vtkImageData()
    mesh.SetDimensions(3, 3, 3)
    array = vtk.vtkDoubleArray()
    array.SetName("v")
    array.SetNumberOfComponents(3)
    for i in range(mesh.GetNumberOfPoints()):
        x, y, z = mesh.GetPoint(i)
        array.InsertNextTuple3(x - 0.8, y - 0.8, z - 0.8)
    mesh.GetPointData().AddArray(array)
    field = {"name": "v", "association": "point", "component": "magnitude"}
    iso = apply_filter(
        mesh, {"type": "isosurface", "parameters": {"field": field, "values": [1.0]}}
    )
    assert iso.GetNumberOfPoints() > 0
    colored = scalar_mesh(iso, field)
    assert colored.GetPointData().GetArray("__vis_scalar").GetRange() == pytest.approx((1, 1))
    assert colored is iso
    different = scalar_mesh(iso, {**field, "component": 0})
    assert different.GetPointData().GetArray("__vis_scalar").GetRange() != (1, 1)


def test_resize_keeps_six_handles(workspace):
    """重排注记不会吃掉覆盖层手柄。"""
    ui, scene, _ = workspace
    ui.begin("slice")
    scene.window.SetSize(1440, 900)
    scene.add_annotations()
    for actor in scene.plane_widget_actors:
        if actor._plane_handle.startswith(("axis_", "rotate_")):
            assert scene.annotation_pool[0].HasViewProp(actor)


def test_helpers_saved_and_export_has_no_transient_actors(workspace, tmp_path):
    """正式修订保存开关，重建导出场景不携带候选预览或手柄。"""
    from modules.visIO import read_asset, save_asset
    from modules.visPhysField.scene import Scene

    ui, scene, _ = workspace
    ui.begin("slice")
    assert ui.apply_selected()
    ui.set_display("plane_visible", False)
    scope = {
        "scope_id": "p:t",
        "project_id": "p",
        "task_id": "t",
        "root": str(tmp_path / "visualizations"),
        "writable": True,
    }
    saved = save_asset(scope, scene.snapshot()["spec"], name="辅助开关")
    spec = read_asset(scope, saved["visualization_id"])["spec"]
    assert spec["layers"][-1]["helpers"]["plane_visible"] is False
    exported = Scene(scene.bindings, spec)
    try:
        assert not exported.plane_widget_actors
        assert not getattr(exported, "preview_actors", [])
        assert not getattr(exported, "selection_actor", None)
    finally:
        exported.close()


def test_sphere_seed_preview_and_compute_share_points():
    """独立球面点源不能借用进程全局随机状态，使预览和计算错位。"""
    from modules.visEngine import build_seed_source

    params = {"seed_type": "sphere", "seeds": 20, "seed_center": [0, 0, 0], "seed_radius": 2}
    first = build_seed_source(params)
    second = build_seed_source(params)
    assert [first.GetPoint(i) for i in range(20)] == [second.GetPoint(i) for i in range(20)]


def test_empty_renderer_is_serialized_with_old_actor_removal():
    """最后对象消失后仍发送背景、相机和旧依赖移除，不能令客户端丢失渲染器。"""
    from modules.visPhysField.rendering import install_local_serializers
    from trame_vtk.modules.vtk.serializers.serialize import serialize
    from trame_vtk.modules.vtk.serializers.synchronization_context import SynchronizationContext

    install_local_serializers()
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.14, 0.21, 0.29)
    context = SynchronizationContext()
    context.set_new_dependency_list("empty-props", ["deleted-actor"])
    result = serialize(None, renderer, "empty", context, 0)
    assert result is not None
    assert result["properties"]["background"] == (0.14, 0.21, 0.29)
    assert ["removeViewProp", ["instance:${deleted-actor}"]] in result["calls"]
    assert len(result["dependencies"]) == 1


@pytest.mark.parametrize("count", [0, 257, True, 1.5])
def test_invalid_automatic_level_count(workspace, count):
    """层数边界在计算入口拒绝，不能静默取整或生成空结果。"""
    _, scene, _ = workspace
    with pytest.raises(ValueError, match="invalid_contour_count"):
        apply_filter(
            apply_filter(scene.datasets["base-s"], {"type": "surface"}),
            {
                "type": "contour",
                "parameters": {
                    "field": {"name": "temperature"},
                    "levels": {"mode": "automatic", "count": count},
                },
            },
        )


def test_constant_levels_and_legacy_form(workspace):
    """常量场明确失败；历史显式值恢复自定义模式。"""
    ui, scene, _ = workspace
    mesh = scene.datasets["base-s"].NewInstance()
    mesh.DeepCopy(scene.datasets["base-s"])
    mesh.GetPointData().GetArray("temperature").Fill(1)
    with pytest.raises(ValueError, match="constant"):
        apply_filter(
            apply_filter(mesh, {"type": "surface"}),
            {
                "type": "contour",
                "parameters": {
                    "field": {"name": "temperature"},
                    "levels": {"mode": "automatic", "count": 10},
                },
            },
        )
    ui.begin("contour")
    ui.set_parameter("iso_values", "3,6")
    assert ui.apply_selected(), ui.server.state.error
    identity = ui.server.state.selected
    parent = next(node for node in scene.spec["pipeline"] if node["id"] == identity)["input"]
    scene.command(
        {
            "operation": "object_create",
            "id": "legacy-contour",
            "type": "contour",
            "input": parent,
            "view": 0,
            "parameters": {"field": {"name": "temperature"}, "values": [3.0, 6.0]},
        }
    )
    ui.refresh(update_view=False)
    ui.select("legacy-contour")
    assert ui.server.state.level_mode == "custom"
    assert [float(v) for v in ui.server.state.iso_values.split(",")] == [3, 6]
    params = next(node for node in scene.spec["pipeline"] if node["id"] == identity)[
        "parameters"
    ]
    assert "levels" in params
    assert "values" not in params


def test_seed_preview_shape_switch(workspace):
    """连续切换种子形状替换附件，而不是只更新表单。"""
    ui, scene, _ = workspace
    ui.begin("streamline")
    ui.toggle_seed_preview()
    ui.set_parameter("seed_type", "sphere")
    sphere = scene.preview_actors[0]
    assert sphere.GetMapper().GetInput().GetNumberOfPolys() > 100
    ui.set_parameter("seed_type", "plane")
    assert not ui.server.state.error, ui.server.state.error
    assert scene.preview_actors[0].GetMapper().GetInput().GetNumberOfPolys() == 1
    assert not scene.annotation_pool[0].HasViewProp(sphere)


def test_hide_seed_preview_clears_actors(workspace):
    """隐藏预览必须撤下预览附件；已应用后不再提供该按钮。"""
    ui, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for index in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1, 0, 0)
    mesh.GetPointData().AddArray(vectors)
    ui.refresh(update_view=False)
    ui.select("base-s")
    ui.begin("streamline")
    assert ui.server.state.can_preview_seeds
    ui.toggle_seed_preview()
    assert scene.preview_actors
    ui.toggle_seed_preview()
    assert not scene.preview_actors
    assert not ui.server.state.seed_preview
    assert ui.apply_selected(), ui.server.state.error
    assert not ui.server.state.can_preview_seeds


def test_plane_press_miss_does_not_lock(workspace):
    """未命中手柄不进入拖动，视角保持可转。"""
    ui, scene, _ = workspace
    ui.begin("slice")
    handle = ui.plane_press(0.01, 0.99, 200, 200)
    assert not handle
    assert ui.server.state.plane_dragging == ""


def test_camera_serializer_omits_pose_unless_pushed():
    """官方相机序列化默认带位姿；本地刷新不得在未声明时写出轨道。"""
    from modules.visPhysField.rendering import camera_pose_push, install_local_serializers
    from trame_vtk.modules.vtk.serializers.registry import SERIALIZERS
    from trame_vtk.modules.vtk.serializers.synchronization_context import SynchronizationContext

    install_local_serializers()
    camera = vtk.vtkCamera()
    camera.SetPosition(9, 8, 7)
    camera.SetFocalPoint(1, 2, 3)
    serializer = SERIALIZERS[camera.GetClassName()]
    context = SynchronizationContext()
    skipped = serializer(None, camera, "cam", context, 0)
    assert skipped["properties"] == {}
    with camera_pose_push():
        pushed = serializer(None, camera, "cam", context, 0)
    assert list(pushed["properties"]["position"]) == pytest.approx([9, 8, 7])


def test_plane_visible_orbit_does_not_restore_old_camera(workspace):
    """辅助平面可见时，hover/refresh/滚轮/旋转都不得用添加平面时的旧相机覆盖。"""
    from modules.visPhysField.modules.fieldVisualization.view import camera_spec

    ui, scene, calls = workspace
    ui.begin("slice")
    camera = scene.renderers[0].GetActiveCamera()
    frozen = camera_spec(camera)
    ui.server.state.render_cameras = [{"camera": frozen, "stale": True}]
    moved = {**frozen, "position": [value + 4 for value in frozen["position"]]}
    ui.camera_event({"view": scene.spec["views"][0]["id"], "camera": moved})
    assert scene.spec["views"][0]["camera"]["position"] == pytest.approx(moved["position"])
    before_updates = list(calls)
    ui.plane_hover("axis_x", ui.server.state.selected)
    ui.refresh()
    ui.wheel_zoom(True)
    ui.refresh()
    ui.camera_navigate(True)
    ui.plane_hover("axis_x", ui.server.state.selected)
    ui.refresh(push_cameras=True)
    ui.camera_event({"view": scene.spec["views"][0]["id"], "camera": moved})
    assert scene.spec["views"][0]["camera"]["position"] == pytest.approx(moved["position"])
    assert ui.server.state.render_cameras == [{"camera": frozen, "stale": True}]
    assert camera_spec(camera)["position"] == pytest.approx(moved["position"])
    assert calls[len(before_updates) :].count("update") >= 1
    ui.camera_navigate(False)
    ui.refresh(push_cameras=True)
    assert ui.server.state.render_cameras[0]["camera"]["position"] == pytest.approx(
        moved["position"]
    )


def test_plane_press_hit_only_updates_draft(workspace):
    """服务端确认命中后拖动只改草稿，不切开。"""
    from modules.visEngine import pick_plane_handle

    ui, scene, _ = workspace
    ui.begin("slice")
    origin = ui.xyz(ui.server.state.plane_origin)
    ray = [[origin[0] + 2, origin[1], origin[2]], [origin[0] - 2, origin[1], origin[2]]]
    name = pick_plane_handle(scene.plane_widget_handles, ray)
    assert name
    ui.screen_ray = lambda *_, **__: ray
    handle = ui.plane_press(0.5, 0.5, 400, 300, requested=name)
    assert handle == name
    assert ui.server.state.plane_dragging == name
    moved = [[origin[0] + 3, origin[1], origin[2]], [origin[0] - 1, origin[1], origin[2]]]
    ui.screen_ray = lambda *_, **__: moved
    ui.plane_move(0.6, 0.5, 400, 300)
    assert ui.server.state.pending
    assert ui.xyz(ui.server.state.plane_origin)[0] != pytest.approx(origin[0])
    assert len(scene.spec["pipeline"]) == 1
