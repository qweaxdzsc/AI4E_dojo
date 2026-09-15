"""固定复合文件的完整数据依赖，禁止静默使用修改过的子网格。"""
import pytest
from modules.dataAssets import source_fingerprint, resolve_external, dependency_snapshot
from server.runtime import Runtime


def test_nested_composite_revision_is_frozen(tmp_path):
    leaf = tmp_path / 'leaf.vtu'
    leaf.write_text('first data revision')
    block = tmp_path / 'block.vtm'
    block.write_text('<VTKFile><DataSet file="leaf.vtu"/></VTKFile>')
    series = tmp_path / 'series.pvd'
    series.write_text('<VTKFile><DataSet timestep="0" file="block.vtm"/></VTKFile>')
    ref = {'asset_id': 'series', 'revision': source_fingerprint(series)}
    runtime = Runtime()
    registered = runtime.register({'bindings': [{'ref': ref, 'path': str(series)}], 'sources': [{'id': 's', 'ref': ref}]})
    context = runtime.context(registered['context_id'])
    assert len(context['bindings'][0]['dependencies']) == 2
    resolve_external(context['sources'][0], context['bindings'])
    leaf.write_text('second data revision')
    with pytest.raises(ValueError, match='source_revision_mismatch'):
        resolve_external(context['sources'][0], context['bindings'])


def test_composite_cannot_escape_authorized_directory(tmp_path):
    folder = tmp_path / 'approved'
    folder.mkdir()
    (tmp_path / 'outside.vtu').write_text('unapproved')
    composite = folder / 'blocks.vtm'
    composite.write_text('<VTKFile><DataSet file="../outside.vtu"/></VTKFile>')
    with pytest.raises(ValueError, match='outside_root'):
        dependency_snapshot(composite)
