"""显示草稿、真实映射输入、色标、背景和透明输出的整链检查。"""

from copy import deepcopy
from types import SimpleNamespace

import pytest
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from modules.visEngine import apply_filter
from modules.visPhysField.producer import capture, produce
from modules.visTaskManage import normalize_physical_spec
from .test_phys_display_updates import workspace as workspace_fixture

workspace = workspace_fixture


def test_display_draft_apply_cancel_and_quick_field(workspace):
    ui, scene, _ = workspace
    original = deepcopy(scene.spec)
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "2")
    ui.edit_display("range_max", "10")
    assert scene.spec == original
    # 顶部仅提交字段，不能把尚未应用的范围一起提交。
    ui.set_display("coloring", "point|temperature")
    assert "range" not in scene.spec["layers"][0].get("color", {})
    assert ui.server.state.range_min == "2"
    assert ui.apply_selected(), ui.server.state.error
    layer = scene.spec["layers"][0]
    assert layer["color"]["range"] == [2, 10]
    mapper = scene.actors[layer["id"]].GetMapper()
    assert mapper.GetInput().GetPointData().GetArray("__vis_scalar").GetRange() == (0, 12)
    assert mapper.GetScalarRange() == (2, 10)
    ui.edit_display("range_max", "1")
    assert not ui.apply_selected()
    assert scene.spec["layers"][0]["color"]["range"] == [2, 10]
    ui.cancel_selected()
    assert ui.server.state.range_max == 10
    ui.edit_display("range_mode", "automatic")
    assert ui.apply_selected()
    assert "range" not in scene.spec["layers"][0].get("color", {})
    assert mapper.GetScalarRange() == (0, 12)


def test_legend_apply_follows_selected_object(workspace):
    """色标草稿不立刻生效；应用只写当前对象，切对象后回填该层厚度和字号。"""
    ui, scene, _ = workspace
    ui.select("base-s")
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("legend_thickness", 40)
    ui.edit_display("legend_title_size", 12)
    layer = next(item for item in scene.spec["layers"] if item["input"] == "base-s")
    assert (layer.get("color") or {}).get("legend_style", {}).get("thickness") != 40
    assert ui.apply_legend("base-s")
    stored = next(item for item in scene.spec["layers"] if item["input"] == "base-s")
    assert stored["color"]["legend_style"]["thickness"] == 40
    assert stored["color"]["legend_style"]["title_font_size"] == 12
    ui.begin("slice")
    assert ui.apply_selected(), ui.server.state.error
    slice_id = ui.server.state.selected
    ui.prepare_legend(slice_id)
    assert ui.server.state.legend_thickness == 25
    assert ui.server.state.legend_title_size == 25
    slice_layer = next(item for item in scene.spec["layers"] if item["input"] == slice_id)
    assert (slice_layer.get("color") or {}).get("legend_style", {}).get("thickness") != 40
    ui.edit_display("legend_thickness", 8)
    ui.cancel_legend(slice_id)
    assert ui.server.state.legend_thickness == 25
    ui.select("base-s")
    ui.prepare_legend("base-s")
    assert ui.server.state.legend_thickness == 40
    assert ui.server.state.legend_title_size == 12
    assert ui.apply_legend("slice") is False
    assert next(item for item in scene.spec["layers"] if item["input"] == "base-s")[
        "color"
    ]["legend_style"]["thickness"] == 40


def test_legend_and_empty_background(workspace):
    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("legend_position", "custom")
    ui.edit_display("legend_orientation", "horizontal")
    ui.edit_display("legend_title_size", 22)
    ui.edit_display("legend_x", 0.1)
    assert ui.apply_selected()
    actor = scene.actors[scene.spec["layers"][0]["id"]]
    assert actor._legend.GetTitleTextProperty().GetFontSize() == 22
    assert actor._legend.GetOrientation() == 0
    renderer = scene.renderers[0]
    camera = renderer.GetActiveCamera()
    ui.set_background("#102030")
    assert scene.renderers[0] is renderer
    assert renderer.GetActiveCamera() is camera
    assert renderer.GetBackground() == pytest.approx([16 / 255, 32 / 255, 48 / 255])
    ui.delete()
    assert renderer.GetBackground() == pytest.approx([16 / 255, 32 / 255, 48 / 255])
    ui.set_background("#ffffff")
    assert renderer.GetBackground() == (1, 1, 1)


def test_transparent_png_readback(workspace, tmp_path):
    _, scene, _ = workspace
    path = tmp_path / "transparent.png"
    capture(scene, path, 320, 240, True)
    reader = vtk.vtkPNGReader()
    reader.SetFileName(str(path))
    reader.Update()
    pixels = vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars())
    assert pixels.shape[1] == 4
    assert pixels[:, 3].min() == 0
    assert pixels[:, 3].max() > 0
    with pytest.raises(ValueError, match="transparent_format"):
        produce(
            scene.bindings, scene.spec, {"format": "mp4", "transparent_background": True}, tmp_path
        )


@pytest.mark.parametrize("shape", ["arrow", "cone", "line"])
@pytest.mark.parametrize("mode", ["constant", "vector", "scalar"])
def test_glyph_shapes_scaling_and_spatial_sampling(workspace, shape, mode):
    _, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for i in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1 + i / 100, 0, 0)
    mesh.GetPointData().AddArray(vectors)
    params = {
        "field": {"name": "velocity"},
        "scale": 0.2,
        "scale_mode": mode,
        "scale_field": {"name": "temperature"},
        "shape": {"type": shape},
        "sampling": {"mode": "spatial", "spacing": 2},
    }
    result = apply_filter(mesh, {"type": "glyph", "parameters": params})
    assert result.GetNumberOfPoints() > 0
    assert len(result._vis_sampled_ids) == 27
    assert len(set(result._vis_sampled_ids)) == 27
    again = apply_filter(mesh, {"type": "glyph", "parameters": params})
    assert again._vis_sampled_ids == result._vis_sampled_ids
    assert mesh.GetPointData().GetArray("__vis_glyph_scale") is None


@pytest.mark.parametrize("changes", [{"background": [2, 0, 0]}, {"background": [0, 0]}])
def test_background_validation(workspace, changes):
    _, scene, _ = workspace
    spec = deepcopy(scene.spec)
    spec["views"][0].update(changes)
    with pytest.raises(ValueError, match="background"):
        normalize_physical_spec(spec)


def test_shortcuts_do_not_submit_property_drafts(workspace):
    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "3")
    ui.edit_display("range_max", "8")
    ui.set_display("opacity", 0.5)
    assert scene.spec["layers"][0].get("field") is None
    assert "range" not in scene.spec["layers"][0].get("color", {})
    ui.set_display("legend", False)
    assert scene.spec["layers"][0].get("field") is None
    assert ui.server.state.range_min == "3"


def test_display_drafts_are_view_local(workspace):
    ui, scene, _ = workspace
    scene.command({"operation": "view_create", "view": 0})
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "3")
    ui.edit_display("range_max", "8")
    ui.view_select(1)
    assert ui.server.state.range_mode == "automatic"
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "4")
    ui.edit_display("range_max", "9")
    ui.view_select(0)
    assert ui.server.state.range_min == "3"
    ui.view_select(1)
    assert ui.server.state.range_min == "4"


def test_color_changes_final_pixels(workspace, tmp_path):
    import numpy as np

    ui, scene, _ = workspace

    def pixels(name):
        path = tmp_path / name
        capture(scene, path, 320, 240)
        reader = vtk.vtkPNGReader()
        reader.SetFileName(str(path))
        reader.Update()
        return vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars()).copy()

    plain = pixels("plain.png")
    ui.edit_display("coloring", "point|temperature")
    ui.apply_selected()
    colored = pixels("colored.png")
    # 不把新增色标当成模型着色证据，只检查画面中央模型区域。
    delta = np.abs(
        plain.reshape(240, 320, 3).astype(int) - colored.reshape(240, 320, 3).astype(int)
    )
    assert (delta[60:180, 100:220].max(axis=2) > 30).sum() > 2000


def test_transparent_sequence_preserves_workspace(workspace, tmp_path):
    _, scene, _ = workspace
    before = deepcopy(scene.spec)
    files = produce(
        scene.bindings,
        scene.spec,
        {"format": "png_sequence", "width": 320, "height": 240, "transparent_background": True},
        tmp_path,
    )
    assert files
    for path in files:
        reader = vtk.vtkPNGReader()
        reader.SetFileName(str(path))
        reader.Update()
        pixels = vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars())
        assert pixels.shape[1] == 4
        assert pixels[:, 3].min() == 0 and pixels[:, 3].max() > 0
    assert scene.spec == before


@pytest.mark.parametrize("mode,expected", [("constant", 0.5), ("vector", 1.0), ("scalar", 1.5)])
def test_glyph_length_and_direction(mode, expected):
    mesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    mesh.SetPoints(points)
    vector = vtk.vtkDoubleArray()
    vector.SetName("v")
    vector.SetNumberOfComponents(3)
    vector.InsertNextTuple3(0, 2, 0)
    scalar = vtk.vtkDoubleArray()
    scalar.SetName("s")
    scalar.InsertNextValue(-3)
    mesh.GetPointData().AddArray(vector)
    mesh.GetPointData().AddArray(scalar)
    result = apply_filter(
        mesh,
        {
            "type": "glyph",
            "parameters": {
                "field": {"name": "v"},
                "shape": {"type": "line"},
                "scale_mode": mode,
                "scale": 0.5,
                "scale_field": {"name": "s"},
            },
        },
    )
    assert result.GetBounds() == pytest.approx((0, 0, 0, expected, 0, 0), abs=1e-7)
    vector.SetTuple3(0, 0, 0, 0)
    zero = apply_filter(
        mesh,
        {
            "type": "glyph",
            "parameters": {"field": {"name": "v"}, "shape": {"type": "line"}, "scale": 0.5},
        },
    )
    assert max(abs(v) for v in zero.GetBounds()) < 1e-8


def test_display_settings_reopen(workspace):
    from modules.visPhysField.scene import Scene

    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("legend_length", 0.4)
    ui.edit_display("legend_label_size", 18)
    assert ui.apply_selected()
    ui.set_background("#123456")
    stored = deepcopy(scene.snapshot()["spec"])
    restored = Scene(scene.bindings, normalize_physical_spec(stored))
    try:
        assert restored.spec["layers"] == scene.spec["layers"]
        legend = restored.actors[stored["layers"][0]["id"]]._legend
        assert legend.GetLabelTextProperty().GetFontSize() == 18
        assert restored.renderers[0].GetBackground() == scene.renderers[0].GetBackground()
    finally:
        restored.close()


def test_applying_one_view_keeps_other_view_draft(workspace):
    ui, scene, _ = workspace
    scene.command({"operation": "view_create", "view": 0})
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "2")
    ui.edit_display("range_max", "8")
    ui.view_select(1)
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "4")
    ui.edit_display("range_max", "9")
    assert ui.apply_selected()
    ui.view_select(0)
    assert ui.server.state.range_min == "2"
    assert ui.apply_selected()
    assert [l["color"]["range"] for l in scene.spec["layers"]] == [[2, 8], [4, 9]]


def test_custom_range_prefills_automatic_then_remembers(workspace):
    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    assert ui.apply_selected(), ui.server.state.error
    ui.edit_display("range_mode", "custom")
    assert ui.server.state.range_min == "0"
    assert ui.server.state.range_max == "12"
    ui.edit_display("range_min", "3")
    ui.edit_display("range_max", "8")
    assert ui.apply_selected(), ui.server.state.error
    ui.edit_display("range_mode", "automatic")
    assert ui.apply_selected(), ui.server.state.error
    assert "range" not in scene.spec["layers"][0].get("color", {})
    ui.edit_display("range_mode", "custom")
    assert ui.server.state.range_min == "3"
    assert ui.server.state.range_max == "8"


def test_custom_range_follows_new_field(workspace):
    ui, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    pressure = vtk.vtkDoubleArray()
    pressure.SetName("pressure")
    for index in range(mesh.GetNumberOfPoints()):
        pressure.InsertNextValue(index + 20)
    mesh.GetPointData().AddArray(pressure)
    ui.edit_display("coloring", "point|temperature")
    assert ui.apply_selected(), ui.server.state.error
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "3")
    ui.edit_display("range_max", "8")
    assert ui.apply_selected(), ui.server.state.error
    ui.edit_display("coloring", "point|pressure")
    assert ui.server.state.range_min == "20"
    assert ui.server.state.range_max == "144"


def test_legend_defaults_are_twenty_five(workspace):
    ui, scene, _ = workspace
    assert ui.server.state.legend_thickness == 25
    assert ui.server.state.legend_title_size == 25
    assert ui.server.state.legend_label_size == 25
    ui.edit_display("coloring", "point|temperature")
    assert ui.apply_selected(), ui.server.state.error
    style = scene.spec["layers"][0]["color"]["legend_style"]
    assert style["thickness"] == 25
    assert style["title_font_size"] == 25
    assert style["label_font_size"] == 25
    legend = scene.actors[scene.spec["layers"][0]["id"]]._legend
    assert legend.GetTitleTextProperty().GetFontSize() == 25
    assert legend.GetLabelTextProperty().GetFontSize() == 25


@pytest.mark.parametrize(
    "parameter",
    [
        {"shape": []},
        {"sampling": []},
        {"scale": float("nan")},
        {"stride": 1.5},
        {"shape": {"type": "arrow", "tip_length": 2}},
        {"sampling": {"mode": "spatial", "spacing": 0}},
    ],
)
def test_invalid_glyph_declarations(workspace, parameter):
    _, scene, _ = workspace
    spec = deepcopy(scene.spec)
    spec["pipeline"].append(
        {"id": "glyph", "input": "base-s", "type": "glyph", "parameters": parameter}
    )
    with pytest.raises(ValueError, match="glyph"):
        normalize_physical_spec(spec)


def test_cone_ignores_leftover_arrow_sizes(workspace):
    """圆锥不校验也不要求箭头尺寸，旧残留数值不能挡住应用。"""
    _, scene, _ = workspace
    spec = deepcopy(scene.spec)
    spec["pipeline"].append(
        {
            "id": "glyph",
            "input": "base-s",
            "type": "glyph",
            "parameters": {
                "field": {"name": "temperature"},
                "shape": {"type": "cone", "tip_length": 2},
            },
        }
    )
    normalize_physical_spec(spec)


def _add_velocity(scene):
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for i in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1, 0, 0)
    mesh.GetPointData().AddArray(vectors)


def test_cone_glyph_apply_without_tip_sizes(workspace):
    """圆锥只写形状，不因隐藏的箭头尺寸报错。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.select("base-s")
    ui.begin("glyph")
    ui.set_parameter("glyph_shape", "cone")
    ui.set_parameter("glyph_scale_mode", "constant")
    ui.server.state.glyph_tip_length = 2
    assert ui.apply_selected(), ui.server.state.error
    shape = scene.spec["pipeline"][-1]["parameters"]["shape"]
    assert shape == {"type": "cone"}


def test_glyph_quantity_uses_selected_field(workspace):
    """物理量选场后按该场缩放；与计算矢量相同则保持矢量模长。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.select("base-s")
    ui.begin("glyph")
    ui.set_parameter("glyph_scale_mode", "quantity")
    ui.set_parameter("glyph_scale_field", "point|temperature")
    assert ui.apply_selected(), ui.server.state.error
    params = scene.spec["pipeline"][-1]["parameters"]
    assert params["scale_mode"] == "scalar"
    assert params["scale_field"]["name"] == "temperature"
    ui.set_parameter("glyph_scale_field", "point|velocity")
    assert ui.apply_selected(), ui.server.state.error
    assert scene.spec["pipeline"][-1]["parameters"]["scale_mode"] == "vector"
    assert "scale_field" not in scene.spec["pipeline"][-1]["parameters"]


def test_solid_color_apply_changes_actor(workspace):
    """纯色选色后物体用该颜色，不再做色条映射。"""
    ui, scene, _ = workspace
    ui.edit_display("coloring", "")
    ui.edit_display("solid_color", "#ff0000")
    assert ui.apply_selected(), ui.server.state.error
    layer = scene.spec["layers"][0]
    assert layer.get("field") is None
    assert layer["style"]["color"] == pytest.approx([1, 0, 0])
    actor = scene.actors[layer["id"]]
    assert actor.GetMapper().GetScalarVisibility() == 0
    assert actor.GetProperty().GetColor() == pytest.approx((1, 0, 0))
    assert actor._legend is None


def test_legend_style_shortcut_writes_current_layer(workspace):
    """工具条色标弹窗即时写入当前层，不消费属性草稿。"""
    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "3")
    ui.edit_display("range_max", "8")
    assert ui.apply_selected(), ui.server.state.error
    ui.edit_display("range_max", "9")
    ui.set_display("legend_title_size", 18)
    assert scene.spec["layers"][0]["color"]["legend_style"]["title_font_size"] == 18
    assert "range" in scene.spec["layers"][0]["color"]
    assert scene.spec["layers"][0]["color"]["range"] == [3, 8]
    assert ui.server.state.range_max == "9"
    legend = scene.actors[scene.spec["layers"][0]["id"]]._legend
    assert legend.GetTitleTextProperty().GetFontSize() == 18


def test_contour_line_width_does_not_recompute(workspace):
    """线宽只改线条粗细，不重算等值。"""
    ui, scene, _ = workspace
    ui.begin("contour")
    ui.set_parameter("level_count", 3)
    assert ui.apply_selected(), ui.server.state.error
    identity = ui.server.state.selected
    before = scene.filter_cache[identity][1]
    ui.edit_display("line_width", 4)
    assert ui.apply_selected(), ui.server.state.error
    layer = next(item for item in scene.spec["layers"] if item["input"] == identity)
    assert layer["style"]["line_width"] == 4
    assert scene.actors[layer["id"]].GetProperty().GetLineWidth() == 4
    assert scene.filter_cache[identity][1] is before
    assert scene.datasets[identity] is before


def test_custom_range_allows_equal_limits(workspace):
    """自定义色标最小等于最大可保存，最小大于最大拒绝。"""
    ui, scene, _ = workspace
    ui.edit_display("coloring", "point|temperature")
    ui.edit_display("range_mode", "custom")
    ui.edit_display("range_min", "5")
    ui.edit_display("range_max", "5")
    assert ui.apply_selected(), ui.server.state.error
    assert scene.spec["layers"][0]["color"]["range"] == [5, 5]
    ui.edit_display("range_max", "4")
    assert not ui.apply_selected()
    assert scene.spec["layers"][0]["color"]["range"] == [5, 5]


def test_streamline_tube_style_does_not_recompute(workspace):
    """流线圆管/线/面数只改显示，不重跑积分；旧修订缺键按线读取。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.begin("streamline")
    ui.set_parameter("compute_field", "point|velocity")
    assert ui.apply_selected(), ui.server.state.error
    identity = ui.server.state.selected
    layer = next(item for item in scene.spec["layers"] if item["input"] == identity)
    assert layer["style"]["streamline"]["shape"] == "line"
    assert layer["style"]["streamline"]["thickness"] == 1
    assert layer["style"]["streamline"]["sides"] == 8
    before = scene.filter_cache[identity][1]
    line_polys = scene.actors[layer["id"]].GetMapper().GetInput().GetNumberOfPolys()
    ui.edit_display("streamline_shape", "tube")
    ui.edit_display("streamline_thickness", 0.05)
    ui.edit_display("streamline_sides", 6)
    assert ui.apply_selected(), ui.server.state.error
    layer = next(item for item in scene.spec["layers"] if item["input"] == identity)
    assert layer["style"]["streamline"] == {"shape": "tube", "thickness": 0.05, "sides": 6}
    assert scene.filter_cache[identity][1] is before
    assert scene.datasets[identity] is before
    assert scene.actors[layer["id"]].GetMapper().GetInput().GetNumberOfPolys() > line_polys
    stored = deepcopy(scene.spec)
    stored["layers"][
        next(i for i, item in enumerate(stored["layers"]) if item["id"] == layer["id"])
    ]["style"].pop("streamline", None)
    restored = normalize_physical_spec(stored)
    assert "streamline" not in restored["layers"][
        next(i for i, item in enumerate(restored["layers"]) if item["id"] == layer["id"])
    ].get("style", {})


def _add_velocity(scene):
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for i in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1, 0, 0)
    mesh.GetPointData().AddArray(vectors)
    return mesh


def test_surface_lic_requires_point_vector_and_switches_remote(workspace):
    """无点向量拒绝 LIC；选中后 mapper 为表面 LIC 且窗口改远程。"""
    ui, scene, _ = workspace
    ui.set_display("display_mode", "surface_lic")
    assert ui.server.state.error
    assert scene.spec["layers"][0].get("style", {}).get("mode") != "surface_lic"
    assert not ui.server.state.use_remote_view
    assert not ui.server.state.remote_ready
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.set_display("coloring", "point|velocity")
    ui.set_display("display_mode", "surface_lic")
    assert ui.server.state.error == ""
    layer = scene.spec["layers"][0]
    assert layer["style"]["mode"] == "surface_lic"
    mapper = scene.actors[layer["id"]].GetMapper()
    assert "LIC" in mapper.GetClassName()
    assert scene.uses_surface_lic()
    assert ui.server.state.use_remote_view
    assert ui.server.state.remote_ready
    assert not ui.server.state.remote_handoff
    ui.set_display("display_mode", "surface")
    layer = scene.spec["layers"][0]
    assert layer["style"]["mode"] == "surface"
    assert not scene.uses_surface_lic()
    assert not ui.server.state.use_remote_view
    assert not ui.server.state.remote_ready
    assert ui.server.state.error == ""


def test_surface_lic_build_or_still_failure_stays_local(workspace, monkeypatch):
    """建图或第一帧失败只提示无法生成，恢复原显示，不切半套远程。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.set_display("coloring", "point|velocity")
    before = deepcopy(scene.spec)
    from modules.visPhysField import rendering

    def fail_build(*args, **kwargs):
        raise RuntimeError("mapper boom")

    monkeypatch.setattr(rendering, "build_lic_display", fail_build)
    ui.set_display("display_mode", "surface_lic")
    assert "无法生成 Surface LIC" in ui.server.state.error
    assert "mapper boom" in ui.server.state.error
    assert scene.spec["layers"][0].get("style", {}).get("mode") != "surface_lic"
    assert not scene.uses_surface_lic()
    assert not ui.server.state.use_remote_view
    assert not ui.server.state.remote_ready
    assert scene.window is not None
    monkeypatch.undo()
    ui.server.state.error = ""

    def fail_still(**_):
        raise RuntimeError("still frame failed")

    ui.view = SimpleNamespace(update=fail_still)
    ui.set_display("display_mode", "surface_lic")
    assert "无法生成 Surface LIC" in ui.server.state.error
    assert "still frame failed" in ui.server.state.error
    assert scene.spec["layers"][0].get("style", {}).get("mode") != "surface_lic"
    assert not scene.uses_surface_lic()
    assert not ui.server.state.use_remote_view
    assert (scene.spec["layers"][0].get("style") or {}).get("mode") == (
        (before["layers"][0].get("style") or {}).get("mode")
    )
    assert scene.window is not None


def test_lic_parameters_are_saved_on_apply(workspace):
    """LIC 参数写入当前对象显示并随配置保存。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.set_display("coloring", "point|velocity")
    ui.edit_display("display_mode", "surface_lic")
    ui.edit_display("lic_steps", 22)
    ui.edit_display("lic_intensity", 0.4)
    assert ui.apply_selected(), ui.server.state.error
    lic = scene.spec["layers"][0]["style"]["lic"]
    assert lic["number_of_steps"] == 22
    assert lic["intensity"] == 0.4


def test_surface_lic_coloring_follows_scalar_field(workspace):
    """LIC 方向仍用点向量，改着色物理量后 mapper 使用新标量，不是纯色。"""
    ui, scene, _ = workspace
    _add_velocity(scene)
    ui.refresh(update_view=False)
    ui.set_display("coloring", "point|velocity")
    ui.set_display("display_mode", "surface_lic")
    assert ui.server.state.error == ""
    layer = scene.spec["layers"][0]
    mapper = scene.actors[layer["id"]].GetMapper()
    assert "LIC" in mapper.GetClassName()
    assert mapper.GetScalarVisibility()
    assert mapper.GetArrayName() == "__vis_scalar"
    assert mapper.GetInput().GetPointData().GetArray("__vis_scalar") is not None
    assert mapper.GetInput().GetPointData().GetVectors().GetName() == "velocity"
    ui.edit_display("coloring", "point|temperature")
    assert layer["field"]["name"] == "velocity"
    assert ui.apply_selected(), ui.server.state.error
    layer = scene.spec["layers"][0]
    assert layer["field"]["name"] == "temperature"
    assert layer["style"]["mode"] == "surface_lic"
    assert (layer["style"].get("lic") or {}).get("vectors", {}).get("name") == "velocity"
    mapper = scene.actors[layer["id"]].GetMapper()
    assert "LIC" in mapper.GetClassName()
    assert mapper.GetScalarVisibility()
    assert mapper.GetArrayName() == "__vis_scalar"
    scalars = mapper.GetInput().GetPointData().GetArray("__vis_scalar")
    assert scalars is not None
    low, high = scalars.GetRange()
    assert high - low > 1
    assert mapper.GetScalarRange() == (low, high)
    assert mapper.GetInput().GetPointData().GetVectors().GetName() == "velocity"
    ui.set_display("coloring", "point|velocity")
    ui.set_display("coloring", "point|temperature")
    assert ui.server.state.error == ""
    mapper = scene.actors[scene.spec["layers"][0]["id"]].GetMapper()
    assert mapper.GetScalarVisibility()
    assert mapper.GetInput().GetPointData().GetArray("__vis_scalar").GetRange() == (low, high)
    assert mapper.GetInput().GetPointData().GetVectors().GetName() == "velocity"


def test_default_view_uses_paraview_light_kit_without_shadows(workspace):
    """旧视图缺灯/阴影键时按 ParaView 默认读：五灯套件，阴影关，不回写历史 spec。"""

    ui, scene, _ = workspace
    view = scene.spec["views"][0]
    assert "shadows" not in view
    assert "light_kit" not in view
    assert ui.server.state.shadows is False
    renderer = scene.renderers[0]
    assert renderer.GetAutomaticLightCreation() == 0
    assert renderer.GetLights().GetNumberOfItems() == 5
    assert renderer.GetPass() is None
    before = deepcopy(scene.spec)
    scene.apply(before)
    assert scene.spec["views"][0] == before["views"][0]
    assert scene.renderers[0].GetLights().GetNumberOfItems() == 5
