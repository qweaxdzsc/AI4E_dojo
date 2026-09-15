"""真实图像、CSV 与视频文件验收，配置摘要不因输出变化。"""
import time
from pathlib import Path
import vtk
import imageio.v2 as imageio
from modules.dataAssets import source_fingerprint
from modules.visPhysField import default_spec
from modules.visIO import save_asset, read_asset, Exports, get_export, export_root


def test_explicit_outputs(tmp_path):
    source = tmp_path/'mesh.vti'
    grid = vtk.vtkImageData()
    grid.SetDimensions(4,4,4)
    array = vtk.vtkDoubleArray()
    array.SetName('p')
    for i in range(64): array.InsertNextValue(i)
    grid.GetPointData().AddArray(array)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(source)); writer.SetInputData(grid); writer.Write()
    ref = {'asset_id':'a','revision':source_fingerprint(source)}
    spec = default_spec([{'id':'s','ref':ref}])
    spec['layers'][0]['field'] = {'name':'p'}
    scope = {'scope_id':'p:t','project_id':'p','task_id':'t','root':str(tmp_path/'visualizations'),'writable':True}
    saved = save_asset(scope, spec, name='场')
    context = {'scope':scope,'bindings':[{'path':str(source),'ref':ref}]}
    exports = Exports()
    for kind in ('png','csv','mp4','png_sequence'):
        output = exports.create(context, saved['visualization_id'], 1, {'format':kind,'width':320,'height':240,'input':'s','positions':[[.5,.5,.5],[999,999,999]],'cameras':[spec['views'][0].get('camera', {}), {}]})
        for _ in range(300):
            status = get_export(scope, saved['visualization_id'], output['export_id'])
            if status['status'] != 'running': break
            time.sleep(.1)
        assert status['status'] == 'succeeded', status
        path = export_root(scope, saved['visualization_id'], output['export_id'])/status['files'][0]['name']
        if kind == 'png':
            assert imageio.imread(path).shape[:2] == (240,320)
        elif kind == 'png_sequence':
            assert len(status['files']) == 2
            assert imageio.imread(path).shape[:2] == (240,320)
        elif kind == 'csv':
            import csv
            with path.open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            assert float(rows[0]['point:p']) == 10.5
            assert rows[1]['valid'] == 'False'
            assert rows[1]['point:p'] == ''
        else:
            with imageio.get_reader(path) as movie:
                assert movie.get_data(0).shape[:2] == (240,320)
        assert read_asset(scope, saved['visualization_id'])['content_hash'] == saved['content_hash']
    assert source_fingerprint(source) == ref['revision']
    # 报告引用 r1；后续编辑到 r2 不改变报告所选配置或独立 PNG 输出。
    from modules.visIO import materialize_reference
    save_asset(scope, {**spec, 'views': [{**spec['views'][0], 'background': [1,1,1]}]}, name='新版', visualization_id=saved['visualization_id'], expected_revision=1)
    reference = {key: saved[key] for key in ('project_id','task_id','visualization_id','revision','content_hash')}
    report_output = materialize_reference(context, reference, exports)
    assert report_output['manifest']['revision'] == 1
    assert imageio.imread(report_output['path']).shape[:2] == (720,1280)
    exports.shutdown()


def test_failed_and_canceled_exports_never_publish_files(tmp_path):
    scope={'scope_id':'p:t','project_id':'p','task_id':'t','root':str(tmp_path/'visualizations'),'writable':True}
    spec=default_spec([{'id':'s','ref':{'asset_id':'missing','revision':'fixed'}}])
    asset=save_asset(scope,spec,name='failure')
    manager=Exports()
    context={'scope':scope,'bindings':[]}
    try:
        failed=manager.create(context,asset['visualization_id'],1,{'format':'png'})
        for _ in range(100):
            value=get_export(scope,asset['visualization_id'],failed['export_id'])
            if value['status']!='running':break
            time.sleep(.1)
        assert value['status']=='failed' and not value['files']
        canceled=manager.create(context,asset['visualization_id'],1,{'format':'png'})
        manager.cancel(scope,asset['visualization_id'],canceled['export_id'])
        assert get_export(scope,asset['visualization_id'],canceled['export_id'])['status']=='canceled'
        assert read_asset(scope,asset['visualization_id'])['content_hash']==asset['content_hash']
    finally:
        manager.shutdown()
