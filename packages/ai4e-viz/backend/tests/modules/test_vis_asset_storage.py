"""任务配置资产的真实文件事务与来源身份验收。"""
from copy import deepcopy
from pathlib import Path
import pytest
from modules.visIO import save_asset, read_asset, list_assets
from modules.visIO import save as saving
from modules.dataAssets import source_fingerprint, resolve_external


@pytest.fixture
def scope(tmp_path):
    return {'scope_id': 'p:t', 'project_id': 'p', 'task_id': 't', 'root': str(tmp_path/'tasks'/'t'/'visualizations'), 'writable': True}


@pytest.fixture
def spec():
    return {'schema_version': 1, 'kind': 'phys_field', 'sources': [{'id': 's', 'ref': {'asset_id': 'mesh', 'revision': 'hash'}}], 'views': [{'id': 0}], 'pipeline': [], 'layers': [], 'time': {}}


def test_only_config_and_atomic_revisions(scope, spec, monkeypatch):
    first = save_asset(scope, spec, name='压力', request_id='one')
    assert save_asset(scope, spec, name='压力', request_id='one') == first
    assert len(list_assets(scope)) == 1
    root = Path(scope['root'])
    assert sorted(p.name for p in root.rglob('*') if p.is_file() and '.runtime' not in p.parts) == ['asset.json', 'spec.json']
    assert not (root / first['visualization_id'] / 'exports').exists()
    with pytest.raises(ValueError, match='revision_conflict'):
        save_asset(scope, spec, name='x', visualization_id=first['visualization_id'])
    commit = saving.commit_index
    def fail(*args):
        raise OSError('disk_failed')
    monkeypatch.setattr(saving, 'commit_index', fail)
    with pytest.raises(OSError):
        save_asset(scope, spec, name='x', visualization_id=first['visualization_id'], expected_revision=1)
    assert read_asset(scope, first['visualization_id'])['revision'] == 1
    monkeypatch.setattr(saving, 'commit_index', commit)
    changed = deepcopy(spec)
    changed['time']['value'] = 1
    saved = save_asset(scope, changed, name='x', visualization_id=first['visualization_id'], expected_revision=1)
    assert saved['revision'] == 2
    assert read_asset(scope, first['visualization_id'], 1)['content_hash'] == first['content_hash']


def test_source_identity_and_missing(scope, spec, tmp_path):
    path = tmp_path/'input.vtu'
    path.write_text('unchanged input')
    digest = source_fingerprint(path)
    spec['sources'][0]['ref']['revision'] = digest
    binding = {'ref': spec['sources'][0]['ref'], 'path': str(path)}
    first = save_asset(scope, spec, name='a')
    resolve_external(read_asset(scope, first['visualization_id'])['spec']['sources'][0], [binding])
    assert source_fingerprint(path) == digest
    path.write_text('changed')
    with pytest.raises(ValueError, match='revision_mismatch'):
        resolve_external(spec['sources'][0], [binding])
    path.unlink()
    with pytest.raises(FileNotFoundError, match='source_missing'):
        resolve_external(spec['sources'][0], [binding])


def test_reject_raw_data_and_escape(scope, spec, tmp_path):
    for value in [{'payload': [1]}, {'url': 'https://example.org/x'}]:
        changed = deepcopy(spec)
        changed['parameters'] = value
        with pytest.raises(ValueError):
            save_asset(scope, changed, name='bad')
    with pytest.raises(ValueError):
        save_asset(scope, spec, name='bad', visualization_id='../escape')
    with pytest.raises(ValueError, match='read_only'):
        save_asset({**scope, 'writable': False}, spec, name='bad')


def test_cache_removal_copy_and_configuration_tamper(scope, spec, tmp_path):
    import shutil
    import json
    first=save_asset(scope,spec,name='copy')
    root=Path(scope['root'])
    shutil.rmtree(root/'.runtime')
    assert list_assets(scope)[0]['content_hash']==first['content_hash']
    copied=tmp_path/'copied-project/tasks/t/visualizations'
    shutil.copytree(root,copied)
    assert read_asset({**scope,'root':str(copied)},first['visualization_id'])['spec']==spec
    path=root/first['visualization_id']/'revisions/000001/spec.json'
    altered=json.loads(path.read_text());altered['time']['value']=999;path.write_text(json.dumps(altered))
    with pytest.raises(ValueError,match='configuration_tampered'):
        read_asset(scope,first['visualization_id'])


def test_symlink_asset_manifest_is_rejected(scope, spec, tmp_path):
    first=save_asset(scope,spec,name='symlink')
    path=Path(scope['root'])/first['visualization_id']/'asset.json'
    outside=tmp_path/'outside.json';outside.write_bytes(path.read_bytes())
    path.unlink();path.symlink_to(outside)
    with pytest.raises(ValueError,match='storage_path_escape'):
        read_asset(scope,first['visualization_id'])
