"""真实 Trame 状态与 VTK 场景的交互回归，不用字典替身掩盖状态契约。"""

from copy import deepcopy
from types import SimpleNamespace
from uuid import uuid4

import pytest
import vtk
from modules.dataAssets import source_fingerprint
from modules.visDatasets import describe_physical
from modules.visPhysField.scene import Scene, default_spec
from modules.visPhysField.trameUI.controller import Workbench
from trame.app import get_server


@pytest.fixture
def workspace(tmp_path):
    """解析体场搭配真正的 Trame State，只有网络推送替换为计数器。"""
    mesh = vtk.vtkImageData()
    mesh.SetDimensions(5, 5, 5)
    values = vtk.vtkDoubleArray()
    values.SetName("temperature")
    for i in range(mesh.GetNumberOfPoints()):
        values.InsertNextValue(sum(mesh.GetPoint(i)))
    mesh.GetPointData().AddArray(values)
    path = tmp_path / "volume.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(mesh)
    writer.Write()
    ref = {"asset_id": "volume", "revision": source_fingerprint(path)}
    scene = Scene([{"ref": ref, "path": str(path)}], default_spec([{"id": "s", "ref": ref}]))
    ui = Workbench(get_server(name=uuid4().hex, client_type="vue2"), scene)
    ui.refresh(update_view=False)
    calls = []
    ui.view = SimpleNamespace(update=lambda **_: calls.append("update"))
    yield ui, scene, calls
    scene.close()


def test_real_state_visibility_is_independent(workspace):
    ui, scene, calls = workspace
    scene.command(
        {
            "operation": "object_create",
            "id": "slice",
            "type": "slice",
            "input": "base-s",
            "view": 0,
            "parameters": {"origin": [2, 2, 2], "normal": [1, 0, 0]},
        }
    )
    ui.refresh(update_view=False)
    ui.visible("base-s", False)
    assert ui.server.state.error == ""
    assert [l["visible"] for l in scene.spec["layers"]] == [False, True]
    assert calls == ["update"]
    ui.visible("slice", False)
    ui.visible("base-s", True)
    assert [l["visible"] for l in scene.spec["layers"]] == [True, False]
    before = deepcopy(scene.spec)
    ui.visible("s", False)
    assert scene.spec == before  # 来源分组没有显示实例，更不能批量操作。
    scene.apply(before)
    assert [l["visible"] for l in scene.spec["layers"]] == [True, False]


def test_visibility_failure_rolls_back_and_reports(workspace, monkeypatch):
    ui, scene, _ = workspace
    before = deepcopy(scene.spec)
    tree = deepcopy(ui.server.state.tree_nodes)
    original = ui._sync_tree_visible

    def fail(*_):
        raise RuntimeError("tree sync failed")

    monkeypatch.setattr(ui, "_sync_tree_visible", fail)
    ui.visible("base-s", False)
    assert scene.spec == before
    assert ui.server.state.tree_nodes == tree
    assert "tree sync failed" in ui.server.state.error
    assert scene.actors[scene.spec["layers"][0]["id"]].GetVisibility()
    monkeypatch.setattr(ui, "_sync_tree_visible", original)
    ui.visible("base-s", False)
    assert ui.server.state.error == ""


def test_slice_draft_pushes_handles_once(workspace):
    ui, scene, calls = workspace
    ui.begin("slice")
    assert scene.plane_widget_actors
    assert calls == ["update"]
    assert len(scene.spec["pipeline"]) == 1
    ui.begin("slice")
    assert len(ui.drafts) == 1
    assert calls == ["update"]


def test_parent_child_grandchild_visibility_never_propagates(workspace):
    ui, scene, _ = workspace
    scene.command(
        {
            "operation": "object_create",
            "id": "slice",
            "type": "slice",
            "input": "base-s",
            "view": 0,
            "parameters": {"origin": [2, 2, 2], "normal": [1, 0, 0]},
        }
    )
    scene.command(
        {
            "operation": "object_create",
            "id": "contour",
            "type": "contour",
            "input": "slice",
            "view": 0,
            "parameters": {"field": {"name": "temperature"}, "values": [6]},
        }
    )
    ui.refresh(update_view=False)
    ui.visible("slice", False)
    assert {l["input"]: l["visible"] for l in scene.spec["layers"]} == {
        "base-s": True,
        "slice": False,
        "contour": True,
    }
    ui.visible("base-s", False)
    assert scene.spec["layers"][-1]["visible"]
    assert scene.datasets["contour"].GetNumberOfPoints() > 0


def test_invalid_normal_retains_last_result_and_handles(workspace):
    ui, scene, _ = workspace
    ui.begin("slice")
    assert ui.apply_selected()
    previous = deepcopy(scene.spec)
    result = scene.datasets[ui.server.state.selected]
    handles = list(scene.plane_widget_actors)
    ui.set_coordinate("plane_normal", 0, "0")
    assert "normal" in ui.server.state.error
    assert scene.plane_widget_actors == handles
    assert not ui.apply_selected()
    assert scene.spec == previous and scene.datasets[ui.server.state.selected] is result
    ui.set_coordinate("plane_normal", 0, "1")
    assert ui.server.state.error == ""
    assert ui.apply_selected()


def test_hover_and_same_view_do_not_refresh(workspace, monkeypatch):
    ui, scene, calls = workspace

    def forbidden(*_, **__):
        pytest.fail("普通移动不得调用画像/刷新")

    monkeypatch.setattr(scene, "snapshot", forbidden)
    for _ in range(60):
        ui.plane_move(0.4, 0.5, 1000, 650)
        ui.view_select(ui.server.state.active_view)
    assert calls == []


def test_opacity_reuses_mapper_and_coloring_array(workspace):
    _, scene, _ = workspace
    scene.command(
        {"operation": "display", "id": "base-s", "view": 0, "field": {"name": "temperature"}}
    )
    actor = scene.actors[scene.spec["layers"][0]["id"]]
    mapper = actor.GetMapper()
    mesh = mapper.GetInput()
    scene.command({"operation": "display", "id": "base-s", "view": 0, "style": {"opacity": 0.3}})
    assert actor.GetMapper() is mapper
    assert mapper.GetInput() is mesh
    assert actor.GetProperty().GetOpacity() == 0.3
    old = deepcopy(scene.spec)
    with pytest.raises(ValueError):
        scene.command({"operation": "display", "id": "base-s", "view": 0, "style": {"opacity": 5}})
    assert scene.spec == old
    assert actor.GetProperty().GetOpacity() == 0.3


def test_profile_cache_invalidates_fields_and_does_not_expose_mutable_cache(workspace, monkeypatch):
    _, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    original = mesh.GetCell
    counts = []
    monkeypatch.setattr(mesh, "GetCell", lambda i: (counts.append(i), original(i))[1])
    first = describe_physical(mesh)
    counts.clear()
    first["fields"][0]["range"][0] = -999
    assert describe_physical(mesh)["fields"][0]["range"][0] == 0
    assert counts == []
    array = mesh.GetPointData().GetArray("temperature")
    array.SetValue(0, -2)
    array.Modified()
    assert describe_physical(mesh)["fields"][0]["range"][0] == -2


def test_probe_visibility_does_not_apply_pipeline(workspace, monkeypatch):
    ui, scene, _ = workspace
    scene.command(
        {
            "operation": "probe_create",
            "id": "p",
            "input": "base-s",
            "position": [2, 2, 2],
            "view": 0,
        }
    )
    ui.refresh(update_view=False)
    monkeypatch.setattr(scene, "apply", lambda *_: pytest.fail("Probe 显隐不得重建管线"))
    ui.visible("p", False)
    assert ui.server.state.error == ""
    assert not scene.spec["probes"][0]["views"]["0"]["visible"]
    ui.visible("base-s", False)
    ui.visible("p", True)
    assert scene.spec["probes"][0]["views"]["0"]["visible"]
    assert not scene.spec["layers"][0]["visible"]


def test_first_display_in_another_view_shares_computed_data(workspace):
    ui, scene, _ = workspace
    scene.command({"operation": "view_create", "view": 0})
    second = scene.spec["views"][-1]["id"]
    scene.command(
        {
            "operation": "object_create",
            "id": "slice",
            "type": "slice",
            "input": "base-s",
            "view": second,
            "parameters": {"origin": [2, 2, 2], "normal": [1, 0, 0]},
        }
    )
    result = scene.datasets["slice"]
    ui.refresh(update_view=False)
    ui.visible("slice", True)
    assert ui.server.state.error == ""
    assert scene.datasets["slice"] is result
    assert {l["view"] for l in scene.spec["layers"] if l["input"] == "slice"} == {0, second}
    ui.visible("slice", False)
    assert next(l for l in scene.spec["layers"] if l["input"] == "slice" and l["view"] == second)[
        "visible"
    ]


def test_push_failure_restores_old_visibility(workspace):
    ui, scene, _ = workspace
    attempts = []

    def push():
        attempts.append(True)
        if len(attempts) == 1:
            raise RuntimeError("transport unavailable")

    ui.view.update = push
    ui.visible("base-s", False)
    assert len(attempts) == 2
    assert scene.spec["layers"][0]["visible"]
    assert "transport unavailable" in ui.server.state.error


def test_scalar_cache_separates_components_and_invalidates_modified_values(workspace):
    import numpy as np
    from modules.visEngine import scalar_mesh
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    _, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    a = numpy_to_vtk(np.tile([3.0, 4.0, 0.0], (mesh.GetNumberOfCells(), 1)), deep=True)
    a.SetName("velocity")
    mesh.GetCellData().AddArray(a)
    field = {"association": "cell", "name": "velocity"}
    first = scalar_mesh(mesh, field)
    assert scalar_mesh(mesh, field) is first
    assert vtk_to_numpy(first.GetCellData().GetArray("__vis_scalar"))[0] == 5
    component = scalar_mesh(mesh, {**field, "component": 0})
    assert vtk_to_numpy(component.GetCellData().GetArray("__vis_scalar"))[0] == 3
    a.SetTuple3(0, 0, 0, 0)
    a.Modified()
    assert vtk_to_numpy(scalar_mesh(mesh, field).GetCellData().GetArray("__vis_scalar"))[0] == 0
    assert vtk_to_numpy(first.GetCellData().GetArray("__vis_scalar"))[0] == 5


def test_probe_labels_visibility_is_per_view(workspace, monkeypatch):
    ui, scene, _ = workspace
    scene.command(
        {
            "operation": "probe_create",
            "id": "p",
            "input": "base-s",
            "position": [2, 2, 2],
            "view": 0,
        }
    )
    scene.command({"operation": "view_create", "view": 0})
    second = scene.spec["views"][-1]["id"]
    monkeypatch.setattr(scene, "apply", lambda *_: pytest.fail("显隐不应重新应用"))
    ui.refresh(update_view=False)
    scene.set_probe_visibility("p", 0, label=False)
    assert not any(a.GetVisibility() for a in scene.probe_actors[("p", 0)]["labels"])
    assert all(a.GetVisibility() for a in scene.probe_actors[("p", second)]["labels"])
    scene.set_probe_visibility("p", 0, label=True)
    assert all(a.GetVisibility() for a in scene.probe_actors[("p", 0)]["labels"])


def test_new_child_commits_display_without_changing_parent(workspace):
    """新对象应用前的着色必须一起提交，父对象声明保持不变。"""
    ui, scene, _ = workspace
    parent = deepcopy(scene.spec['layers'][0])
    ui.begin('slice')
    ui.set_display('coloring', 'point|temperature')
    assert ui.apply_selected()
    child = next(l for l in scene.spec['layers'] if l['input'] == ui.server.state.selected)
    assert child.get('field', {}).get('name') == 'temperature'
    assert scene.spec['layers'][0] == parent


def test_delete_preserves_renderer_and_hidden_parent(workspace):
    """删除最后可见对象不能重建背景、相机或隐藏父对象映射。"""
    ui, scene, _ = workspace
    ui.begin('slice')
    assert ui.apply_selected()
    ui.visible('base-s', False)
    renderer = scene.renderers[0]
    camera = renderer.GetActiveCamera()
    mapper = scene.actors[scene.spec['layers'][0]['id']].GetMapper()
    before = (camera.GetPosition(), camera.GetClippingRange(), renderer.GetBackground())
    ui.delete()
    assert scene.renderers[0] is renderer
    assert scene.actors[scene.spec['layers'][0]['id']].GetMapper() is mapper
    assert (camera.GetPosition(), camera.GetClippingRange(), renderer.GetBackground()) == before
    assert len(scene.spec['pipeline']) == 1
    assert not scene.spec['layers'][0]['visible']


def test_base_coloring_connects_actual_scalar_input(workspace):
    """色标和开关不能代替实际输入数组；初始资产必须连接着色后的数据。"""
    ui, scene, _ = workspace
    ui.set_display('coloring', 'point|temperature')
    mapper = scene.actors[scene.spec['layers'][0]['id']].GetMapper()
    array = mapper.GetInput().GetPointData().GetArray('__vis_scalar')
    assert array is not None
    assert array.GetRange() == (0, 12)


def _tree_item(nodes, identity):
    """按身份取树节点。"""
    for node in nodes or []:
        if node["id"] == identity:
            return node
        found = _tree_item(node.get("children") or [], identity)
        if found:
            return found
    return None


def test_activate_view_refreshes_tree_eyes_without_snapshot(workspace, monkeypatch):
    """点第二窗后左侧眼睛跟随该窗，且不重读网格。"""
    ui, scene, _ = workspace
    scene.command({"operation": "view_create", "view": 0})
    second = scene.spec["views"][-1]["id"]
    ui.refresh(update_view=False)
    ui.visible("base-s", False)
    assert _tree_item(ui.server.state.tree_nodes, "base-s")["visible"] is False
    second_layer = next(
        layer
        for layer in scene.spec["layers"]
        if layer["input"] == "base-s" and layer["view"] == second
    )
    assert second_layer["visible"] is True
    monkeypatch.setattr(scene, "snapshot", lambda *_, **__: pytest.fail("切窗不得 snapshot"))
    ui.activate_view(second)
    assert ui.server.state.active_view == second
    assert _tree_item(ui.server.state.tree_nodes, "base-s")["visible"] is True
    ui.visible("base-s", False)
    assert second_layer["visible"] is False
    first_layer = next(
        layer
        for layer in scene.spec["layers"]
        if layer["input"] == "base-s" and layer["view"] == 0
    )
    assert first_layer["visible"] is False


def test_remote_handoff_ignores_camera_and_remote_end(workspace):
    """静帧未就绪时相机和远程结束事件不得刷新远程视图。"""
    ui, scene, calls = workspace
    ui.server.state.use_remote_view = True
    ui.server.state.remote_ready = False
    ui.server.state.remote_handoff = True
    calls.clear()
    ui.remote_end()
    ui.camera_event(
        {
            "view": 0,
            "camera": {
                "position": [10, 10, 10],
                "focal_point": [0, 0, 0],
                "view_up": [0, 0, 1],
            },
        }
    )
    ui.camera_navigate(True)
    assert calls == []
    assert ui.server.state.camera_navigating is False
    ui.server.state.remote_ready = True
    ui.server.state.remote_handoff = False
    ui.remote_end()
    assert calls == ["update"]
