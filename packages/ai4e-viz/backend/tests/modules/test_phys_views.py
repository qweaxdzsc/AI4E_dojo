"""多结果视口、颜色范围、显隐与联动的场景事务验收。"""
from copy import deepcopy
from pathlib import Path
import vtk
import pytest
from modules.dataAssets import source_fingerprint
from modules.visPhysField import default_spec
from modules.visPhysField.scene import Scene


def test_layers_views_and_shared_camera(tmp_path):
    source = vtk.vtkRTAnalyticSource(); source.SetWholeExtent(-3,3,-3,3,-3,3); source.Update()
    path = tmp_path/'volume.vti'
    writer = vtk.vtkXMLImageDataWriter(); writer.SetInputData(source.GetOutput()); writer.SetFileName(str(path)); writer.Write()
    ref = {'asset_id':'a','revision':source_fingerprint(path)}
    spec = default_spec([{'id':'a','ref':ref}, {'id':'b','ref':{**ref,'asset_id':'b'}}])
    from modules.visTaskManage import balanced_layout
    spec['layout'] = balanced_layout([0,1])
    spec['views'] = [{'id':0},{'id':1}]
    spec['layers'][1].update(view=1, visible=False)
    spec['layers'][0].update(field={'name':'RTData'}, color={'preset':'coolwarm','bands':8,'range':[30,270]}, style={'opacity':.5,'mode':'surface_edges'})
    scene = Scene([{'ref':ref,'path':str(path)}, {'ref':{**ref,'asset_id':'b'},'path':str(path)}], spec)
    try:
        assert len(scene.renderers) == 2
        assert not scene.actors['layer-b'].GetVisibility()
        assert scene.actors['layer-a'].GetProperty().GetOpacity() == .5
        assert scene.actors['layer-a'].GetMapper().GetLookupTable().GetNumberOfTableValues() == 8
        linked = deepcopy(spec); linked['link_groups']=[{'views':[0,1]}]
        scene.apply(linked)
        assert scene.renderers[0].GetActiveCamera() is scene.renderers[1].GetActiveCamera()
        assert scene.snapshot()["camera_link_notice"] == ""
        mixed = deepcopy(linked)
        mixed['sources'][0]['coordinate_space'] = {'id': 'frame-a', 'unit': 'm'}
        mixed['sources'][1]['coordinate_space'] = {'id': 'frame-b', 'unit': 'mm'}
        scene.apply(mixed)
        assert scene.renderers[0].GetActiveCamera() is scene.renderers[1].GetActiveCamera()
        assert 'm' in scene.snapshot()['camera_link_notice'] and 'mm' in scene.snapshot()['camera_link_notice']
        bad = deepcopy(linked)
        bad['link_groups'] = [{'views': [0, 99]}]
        with pytest.raises(ValueError, match='invalid_camera_link'):
            scene.apply(bad)
        four=deepcopy(linked)
        four['views']=[{'id':i} for i in range(4)]
        four['layout']=balanced_layout([0,1,2,3])
        scene.apply(four)
        assert len(scene.renderers)==4
        bad=deepcopy(linked);bad['layers'][0]['style']['opacity']=2
        with pytest.raises(ValueError, match='opacity'):
            scene.apply(bad)
        assert scene.actors['layer-a'].GetProperty().GetOpacity()==.5
    finally:
        scene.close()


def test_window_tab_layout_sequence():
    """新增窗口按 1 全幅、2 横排、3 上二下一、4 田字格排列。"""
    from modules.visTaskManage import balanced_layout, layout_rectangles, view_overlay_frames

    one = layout_rectangles(balanced_layout([0]))
    assert one[0] == (0.0, 0.0, 1.0, 1.0)
    two = layout_rectangles(balanced_layout([0, 1]))
    assert two[0][2] == pytest.approx(0.5)
    assert two[1][0] == pytest.approx(0.5)
    three = layout_rectangles(balanced_layout([0, 1, 2]))
    assert three[0][1] == pytest.approx(0.5)
    assert three[1][1] == pytest.approx(0.5)
    assert three[2] == pytest.approx((0.0, 0.0, 1.0, 0.5))
    four = layout_rectangles(balanced_layout([0, 1, 2, 3]))
    assert four[0][2] == pytest.approx(0.5) and four[0][1] == pytest.approx(0.5)
    assert four[3][0] == pytest.approx(0.5) and four[3][3] == pytest.approx(0.5)
    frames = view_overlay_frames(balanced_layout([0, 1, 2]), [{"id": i, "name": f"RenderView{i + 1}"} for i in range(3)])
    assert frames[2]["name"] == "RenderView3"
    assert frames[2]["view_type"] == "render"
    assert frames[2]["css"].startswith("left:0.0000%;top:50.0000%;")
    chart_frames = view_overlay_frames(
        balanced_layout([0, 1]),
        [{"id": 0, "name": "RenderView1"}, {"id": 1, "name": "LineChartView2", "type": "line_chart"}],
    )
    assert chart_frames[1]["view_type"] == "line_chart"


def test_create_view_links_all_windows(tmp_path):
    """已开启联动时新增窗口必须加入全体相机组。"""
    source = vtk.vtkRTAnalyticSource(); source.SetWholeExtent(-3,3,-3,3,-3,3); source.Update()
    path = tmp_path/'volume.vti'
    writer = vtk.vtkXMLImageDataWriter(); writer.SetInputData(source.GetOutput()); writer.SetFileName(str(path)); writer.Write()
    ref = {'asset_id':'a','revision':source_fingerprint(path)}
    spec = default_spec([{'id':'a','ref':ref}])
    scene = Scene([{'ref':ref,'path':str(path)}], spec)
    try:
        scene.command({"operation": "view_create", "view": 0})
        scene.command({"operation": "link_views", "views": [0, 1]})
        scene.command({"operation": "view_create", "view": 0})
        assert scene.spec["link_groups"][0]["views"] == [0, 1, 2]
        assert scene.renderers[0].GetActiveCamera() is scene.renderers[2].GetActiveCamera()
        scene.command({"operation": "view_create", "view": 2})
        assert scene.spec["link_groups"][0]["views"] == [0, 1, 2, 3]
        assert len(scene.renderers) == 4
    finally:
        scene.close()


class _FakeState(dict):
    """只提供工作台需要的属性写入与上下文，不启动 Trame。"""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _FakeServer:
    def __init__(self):
        self.state = _FakeState()


def test_camera_event_does_not_rebuild_scene(tmp_path, monkeypatch):
    """轨道交互只回写相机，不能走 snapshot/refresh 再次读盘。"""
    source = vtk.vtkRTAnalyticSource()
    source.SetWholeExtent(-3, 3, -3, 3, -3, 3)
    source.Update()
    path = tmp_path / "volume.vti"
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInputData(source.GetOutput())
    writer.SetFileName(str(path))
    writer.Write()
    ref = {"asset_id": "a", "revision": source_fingerprint(path)}
    spec = default_spec([{"id": "a", "ref": ref}])
    scene = Scene([{"ref": ref, "path": str(path)}], spec)
    try:
        from modules.visPhysField.modules.fieldVisualization.view import camera_spec
        from modules.visPhysField.trameUI.controller import Workbench

        server = _FakeServer()
        workbench = Workbench(server, scene)
        reads = {"n": 0}
        original = scene.snapshot

        def counted():
            reads["n"] += 1
            return original()

        monkeypatch.setattr(scene, "snapshot", counted)
        current = camera_spec(scene.renderers[0].GetActiveCamera())
        moved = {**current, "position": [v + 2 for v in current["position"]]}
        workbench.camera_event({"view": spec["views"][0]["id"], "camera": moved})
        assert reads["n"] == 0
        assert scene.spec["views"][0]["camera"]["position"] == pytest.approx(moved["position"])
        workbench.resize({"width": 640, "height": 480})
        workbench.resize({"width": 640, "height": 480})
        assert reads["n"] == 0
    finally:
        scene.close()


from .test_phys_display_updates import workspace as workspace_fixture

workspace = workspace_fixture


def test_axes_follow_main_camera(workspace):
    """左下角方向轴相机必须跟随主视图旋转。"""
    _, scene, _ = workspace
    main = scene.renderers[0].GetActiveCamera()
    marker = next(
        renderer
        for renderer in scene.decorations
        if renderer.GetLayer() == 2 and renderer.GetActiveCamera() is not main
    )
    main.Azimuth(35)
    main.Elevation(20)
    main.Modified()
    axes = marker.GetActiveCamera()
    position, focal = main.GetPosition(), main.GetFocalPoint()
    assert axes.GetPosition() == pytest.approx([position[i] - focal[i] for i in range(3)])
    assert axes.GetViewUp() == pytest.approx(main.GetViewUp())


def test_surface_lic_parameters_restore_after_reopen(workspace):
    """保存再打开仍是 LIC 参数。"""
    from modules.visTaskManage import normalize_physical_spec

    ui, scene, _ = workspace
    mesh = scene.datasets["base-s"]
    vectors = vtk.vtkDoubleArray()
    vectors.SetName("velocity")
    vectors.SetNumberOfComponents(3)
    for _ in range(mesh.GetNumberOfPoints()):
        vectors.InsertNextTuple3(1, 0, 0)
    mesh.GetPointData().AddArray(vectors)
    path = Path(scene.bindings[0]["path"])
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(mesh)
    writer.Write()
    digest = source_fingerprint(path)
    scene.bindings[0]["ref"]["revision"] = digest
    for source in scene.spec.get("sources", []):
        source.setdefault("ref", {})["revision"] = digest
    ui.refresh(update_view=False)
    ui.set_display("coloring", "point|velocity")
    ui.set_display("display_mode", "surface_lic")
    ui.set_display("lic_steps", 22)
    ui.set_display("lic_intensity", 0.4)
    stored = deepcopy(scene.spec)
    restored = Scene(scene.bindings, normalize_physical_spec(stored))
    try:
        layer = restored.spec["layers"][0]
        assert layer["style"]["mode"] == "surface_lic"
        assert layer["style"]["lic"]["number_of_steps"] == 22
        assert layer["style"]["lic"]["intensity"] == 0.4
        assert "LIC" in restored.actors[layer["id"]].GetMapper().GetClassName()
    finally:
        restored.close()
