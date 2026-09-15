"""原图表渲染保留，新保存轻量配置到任务目录。"""
from fastapi.testclient import TestClient
from server.api import app


def test_existing_chart_save_requires_scope_and_replays(tmp_path):
    scope={'scope_id':'p:t','project_id':'p','task_id':'t','root':str(tmp_path/'visualizations'),'writable':True}
    with TestClient(app) as client:
        assert client.get('/api/catalog').status_code==200
        result=client.get('/api/artifacts/A-1025/recommendations').json()
        candidate=result.get('detected_candidates', result.get('candidates'))[0]
        payload={'recommendation_id':candidate['recommendation_id'],'parameters':candidate.get('default_parameters',{})}
        assert client.post('/api/artifacts/A-1025/visualizations',json=payload).status_code==422
        context=app.state.runtime.register({'scope':scope,'bindings':[],'sources':[]})['context_id']
        saved=client.post('/api/artifacts/A-1025/visualizations',json={**payload,'context_id':context})
        assert saved.status_code==201,saved.text
        record=saved.json()
        replay=client.get('/api/visualizations/'+record['visualization_id'],params={'context_id':context})
        assert replay.status_code==200,replay.text
        assert replay.json()['payload']['data']
        from pathlib import Path
        files=[p for p in Path(scope['root']).rglob('*') if p.is_file() and '.runtime' not in p.parts]
        assert sorted(p.name for p in files)==['asset.json','spec.json']
        assert all('payload' not in p.read_text() for p in files)
