"""宿主 task→server→独立 Vis 的真实配置交接验收。"""
from pathlib import Path
import hashlib
import pytest
from fastapi.testclient import TestClient
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings

ROOT = Path(__file__).resolve().parents[2]


def test_task_scoped_save_restart_and_no_training_changes(tmp_path):
    data = tmp_path/'data'
    data.mkdir()
    mesh = data/'sample.vti'
    import vtk
    grid = vtk.vtkImageData()
    grid.SetDimensions(3,3,3)
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(str(mesh))
    writer.SetInputData(grid)
    writer.Write()
    digest = hashlib.sha256(mesh.read_bytes()).hexdigest()
    settings = Settings(tmp_path/'platform', ROOT/'recipes/aero_cfd', [data])
    with TestClient(create_app(settings)) as client:
        project = client.post('/api/v1/projects', json={'name':'物理场'}).json()['id']
        base = '/api/v1/projects/'+project
        task = client.post(base+'/tasks', json={'name':'目标任务'}).json()
        ref = client.post(base+'/assets', json={'root':'data0','path':'sample.vti'}).json()
        api = base+'/tasks/'+task['id']+'/visualizations'
        before = client.get(base+'/lineage').json()
        spec = {'schema_version':1,'kind':'phys_field','sources':[{'id':'s','ref':ref}], 'views':[{'id':0}], 'pipeline':[], 'layers':[{'id':'layer','input':'s'}], 'time':{}}
        response = client.post(api, json={'name':'压力','spec':spec})
        assert response.status_code == 200, response.text
        saved = response.json()
        assert client.get(api).json()['items'][0]['visualization_id'] == saved['visualization_id']
        service = client.app.state.services
        project_path = service.project(project)
        target = project_path/'tasks'/task['id']/'visualizations'/saved['visualization_id']
        assert sorted(p.name for p in target.rglob('*') if p.is_file()) == ['asset.json','spec.json']
        assert not (target/'exports').exists()
        assert client.get(base+'/lineage').json() == before
        assert hashlib.sha256(mesh.read_bytes()).hexdigest() == digest
        assert client.post('/vis/internal/contexts', json={'scope':{}}).status_code == 404
        opened = client.post(api+'/sessions', json={'visualization_id': saved['visualization_id']})
        assert opened.status_code == 200, opened.text
        session = opened.json()
        assert '/vis/workspace/' in session['embed_url']
        command_url='/vis/api/phys/sessions/'+session['session_id']+'/commands'
        def snapshot():
            return client.post(command_url,json={'context_id':session['context_id'],'command':{'operation':'snapshot'}}).json()
        initial=snapshot()
        appended=client.post(api+'/sessions/'+session['session_id']+'/sources',json={'sources':[{'ref':ref}]})
        assert appended.status_code==200, appended.text
        assert appended.json()["status"] == "already_added"
        assert len(snapshot()["spec"]["sources"]) == 1
        second = data / "second.vti"
        writer.SetFileName(str(second))
        writer.Write()
        other = client.post(base+'/assets', json={'root':'data0','path':'second.vti'}).json()
        appended = client.post(api+'/sessions/'+session['session_id']+'/sources',json={'sources':[{'ref':other}]})
        assert appended.status_code == 200, appended.text
        updated=snapshot()
        assert len(updated['spec']['sources'])==2
        assert updated['spec']['views'][0]['camera']==initial['spec']['views'][0]['camera']
        denied=client.post(command_url,json={'context_id':session['context_id'],'command':{'operation':'append_sources','bindings':[],'sources':[]}})
        assert denied.status_code==422
        assert client.get(base+'/lineage').json()==before
        bad_ref={**ref,'project_id':'another-project'}
        bad=client.post(api+'/sessions/'+session['session_id']+'/sources',json={'sources':[{'ref':bad_ref}]})
        assert bad.status_code>=400
        assert len(snapshot()['spec']['sources'])==2
        assert client.delete(api+'/sessions/'+session['session_id']).status_code == 200
        assert client.patch(base+'/tasks/'+task['id'], json={'archived': True}).status_code == 200
        denied=client.post('/vis/api/visualizations', json={'context_id':session['context_id'],'name':'should fail','spec':spec})
        assert denied.status_code == 400, denied.text
        assert client.get(api).status_code == 200
        client.patch(base+'/tasks/'+task['id'], json={'archived': False})
    with TestClient(create_app(settings)) as client:
        restored = client.get(api+'/'+saved['visualization_id']).json()
        assert restored['content_hash'] == saved['content_hash']
        mesh.unlink()
        assert client.get(api+'/'+saved['visualization_id']).status_code == 200
        assert client.post(api+'/sessions', json={'visualization_id': saved['visualization_id']}).status_code == 404
