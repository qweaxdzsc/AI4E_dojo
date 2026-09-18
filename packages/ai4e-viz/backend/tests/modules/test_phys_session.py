"""真实独立 Trame 进程的连接、命令和隔离验收。"""
from pathlib import Path
import httpx
import vtk
from modules.visPhysField import Sessions, default_spec
from modules.dataAssets import source_fingerprint


def test_two_sessions_and_invalid_apply(tmp_path):
    path = tmp_path/'grid.vti'
    grid = vtk.vtkImageData()
    grid.SetDimensions(4,4,4)
    field = vtk.vtkDoubleArray()
    field.SetName('pressure')
    for i in range(64):
        field.InsertNextValue(i)
    grid.GetPointData().AddArray(field)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInputData(grid)
    writer.SetFileName(str(path))
    writer.Write()
    ref = {'asset_id':'a', 'revision':source_fingerprint(path)}
    context = {'context_id':'ctx','bindings':[{'ref':ref,'path':str(path)}]}
    spec = default_spec([{'id':'s','ref':ref}])
    manager = Sessions(maximum=2)
    try:
        one = manager.create(context, spec)
        two = manager.create(context, spec)
        first = manager.get(one['session_id'], 'ctx')
        second = manager.get(two['session_id'], 'ctx')
        assert first['process'].pid != second['process'].pid
        assert httpx.get(f"http://127.0.0.1:{first['port']}", follow_redirects=True).status_code == 200
        changed = manager.command(one['session_id'], 'ctx', {'operation':'camera','direction':'+x'})
        independent = manager.command(two['session_id'], 'ctx', {'operation':'snapshot'})
        assert changed['spec']['views'][0]['camera'] != independent['spec']['views'][0]['camera']
        # 隐藏保持会话；模拟超过回收阈值后心跳更新，再执行清理。
        assert manager.command(one['session_id'], 'ctx', {'operation':'visibility','visible':False}) == {'visible':False}
        first['last_seen'] -= manager.ttl + 1
        manager.get(one['session_id'], 'ctx')
        manager.reap()
        assert one['session_id'] in manager.items
        manager.command(one['session_id'], 'ctx', {'operation':'visibility','visible':True})
        assert manager.command(one['session_id'], 'ctx', {'operation':'snapshot'})['spec']['views'] == changed['spec']['views']
        import pytest
        with pytest.raises(ValueError, match='capacity'):
            manager.create(context, spec)
        bad = {**spec, 'views':[{'id':0}, {'id':1}, {'id':2}]}
        with pytest.raises(ValueError, match='layout_views_mismatch'):
            manager.command(one['session_id'], 'ctx', {'operation':'apply', 'spec':bad})
        assert manager.command(one['session_id'], 'ctx', {'operation':'snapshot'})['spec']['views'] == changed['spec']['views']
    finally:
        manager.shutdown()
    assert manager.items == {}


def test_idle_session_yields_capacity(tmp_path):
    path = tmp_path/'grid.vti'
    grid = vtk.vtkImageData()
    grid.SetDimensions(3,3,3)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInputData(grid)
    writer.SetFileName(str(path))
    writer.Write()
    ref = {'asset_id':'a', 'revision':source_fingerprint(path)}
    context = {'context_id':'ctx','bindings':[{'ref':ref,'path':str(path)}]}
    spec = default_spec([{'id':'s','ref':ref}])
    manager = Sessions(maximum=1, idle=0)
    try:
        one = manager.create(context, spec)
        manager.items[one['session_id']]['last_seen'] -= 1
        two = manager.create(context, spec)
        assert one['session_id'] not in manager.items
        assert two['session_id'] in manager.items
        assert httpx.get(f"http://127.0.0.1:{manager.items[two['session_id']]['port']}", follow_redirects=True).status_code == 200
    finally:
        manager.shutdown()
    assert manager.items == {}


def test_session_links_views_without_coordinate_space(tmp_path):
    """会话里两个来源开联动，不必声明共同坐标空间。"""
    from modules.visTaskManage import balanced_layout

    path = tmp_path / "grid.vti"
    grid = vtk.vtkImageData()
    grid.SetDimensions(3, 3, 3)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetInputData(grid)
    writer.SetFileName(str(path))
    writer.Write()
    ref = {"asset_id": "a", "revision": source_fingerprint(path)}
    other = {**ref, "asset_id": "b"}
    context = {
        "context_id": "ctx",
        "bindings": [{"ref": ref, "path": str(path)}, {"ref": other, "path": str(path)}],
    }
    spec = default_spec([{"id": "a", "ref": ref}, {"id": "b", "ref": other}])
    spec["views"] = [{"id": 0}, {"id": 1}]
    spec["layout"] = balanced_layout([0, 1])
    spec["layers"][1]["view"] = 1
    manager = Sessions(maximum=1)
    try:
        session = manager.create(context, spec)
        linked = manager.command(
            session["session_id"], "ctx", {"operation": "link_views", "views": [0, 1]}
        )
        assert linked["spec"]["link_groups"][0]["views"] == [0, 1]
        assert linked["camera_link_notice"] == ""
    finally:
        manager.shutdown()
    assert manager.items == {}
