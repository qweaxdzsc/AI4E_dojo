"""实际 wheel 安装后的独立 CLI、资产保存与 Trame 工作进程验收。"""
import hashlib
import os
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import httpx
import vtk

ROOT = Path(__file__).resolve().parents[2]


def test_workbench_dependency_preflight(monkeypatch):
    """缺可选依赖时提示当前环境的正确安装入口。"""
    import importlib.util

    import pytest
    spec = importlib.util.spec_from_file_location("viz_cli_preflight", ROOT / "packages/ai4e-viz/cli.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    monkeypatch.setattr(cli, "find_spec", lambda name: None if name in {"trame", "pandas"} else object())
    with pytest.raises(RuntimeError, match=r"trame, pandas.*ai4e-viz\[workbench\]"):
        cli.check_workbench_dependencies()
    monkeypatch.setattr(cli, "find_spec", lambda _: object())
    cli.check_workbench_dependencies()


def test_installed_wheel_has_resources_and_never_writes_installation(tmp_path):
    wheel_dir=tmp_path/'wheels'
    subprocess.run(['uv','build','--package','ai4e-viz','--wheel','--out-dir',str(wheel_dir)],cwd=ROOT,check=True,capture_output=True)
    wheel=next(wheel_dir.glob('ai4e_viz-*.whl'))
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist()
        assert 'ai4e_viz/frontend/dist/index.html' in names
        assert 'ai4e_viz/backend/modules/visPhysField/worker.py' in names
        assert not any('node_modules' in n or '__pycache__' in n or n.endswith('.sqlite3') for n in names)
    installed=tmp_path/'installed'
    subprocess.run(['uv','pip','install','--no-deps','--target',str(installed),str(wheel)],check=True,capture_output=True)
    before={str(p.relative_to(installed)):hashlib.sha256(p.read_bytes()).hexdigest() for p in installed.rglob('*') if p.is_file()}
    source=tmp_path/'field.vti'
    grid=vtk.vtkImageData();grid.SetDimensions(3,3,3)
    writer=vtk.vtkXMLImageDataWriter();writer.SetInputData(grid);writer.SetFileName(str(source));writer.Write()
    ref={'asset_id':'wheel-source','revision':hashlib.sha256(source.read_bytes()).hexdigest()}
    scope={'scope_id':'p:t','project_id':'p','task_id':'t','root':str(tmp_path/'tasks/t/visualizations'),'writable':True}
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    env={**os.environ,'PYTHONPATH':str(installed),'PYTHONDONTWRITEBYTECODE':'1','AI4E_VIS_CONTROL_TOKEN':'installation-test-token'}
    with (tmp_path/'wheel-service.log').open('w') as log:
        process=subprocess.Popen([sys.executable,'-B','-m','ai4e_viz.cli','--port',str(port),'--runtime-root',str(tmp_path/'runtime')],cwd=tmp_path,env=env,stdout=log,stderr=log)
        try:
            base=f'http://127.0.0.1:{port}'
            with httpx.Client(base_url=base,timeout=90) as client:
                for _ in range(200):
                    assert process.poll() is None,(tmp_path/'wheel-service.log').read_text()
                    try:
                        if client.get('/api/phys/capabilities',timeout=.5).is_success:break
                    except httpx.HTTPError:pass
                    time.sleep(.1)
                assert client.get('/workspace/').status_code==200
                context=client.post('/internal/contexts',headers={'x-vis-control':'installation-test-token'},json={'scope':scope,'sources':[{'id':'s','ref':ref}],'bindings':[{'ref':ref,'path':str(source)}]}).json()['context_id']
                created=client.post('/api/phys/sessions',json={'context_id':context})
                assert created.is_success,created.text
                session=created.json()
                command_url='/api/phys/sessions/'+session['session_id']+'/commands'
                base_id=session['snapshot']['spec']['pipeline'][0]['id']
                sliced=client.post(command_url,json={'context_id':context,'command':{'operation':'object_create','id':'slice','name':'切面','type':'slice','input':base_id,'view':0,'parameters':{'origin':[1,1,1],'normal':[1,0,0]}}})
                assert sliced.is_success,sliced.text
                hidden=client.post(command_url,json={'context_id':context,'command':{'operation':'display','id':base_id,'view':0,'visible':False}})
                assert hidden.is_success,hidden.text
                snapshot=client.post(command_url,json={'context_id':context,'command':{'operation':'snapshot'}}).json()
                saved=client.post('/api/visualizations',json={'context_id':context,'name':'wheel','spec':snapshot['spec']})
                assert saved.is_success,saved.text
                assert client.delete('/api/phys/sessions/'+session['session_id'],params={'context_id':context}).is_success
                asset=saved.json()
                loaded=client.get('/api/visualizations/'+asset['visualization_id'],params={'context_id':context}).json()
                reopened=client.post('/api/phys/sessions',json={'context_id':context,'spec':loaded['spec']})
                assert reopened.is_success,reopened.text
                assert reopened.json()['snapshot']['spec']['schema_version']==2
                assert [l['visible'] for l in reopened.json()['snapshot']['spec']['layers']]==[False,True]
                job=client.post('/api/visualizations/'+asset['visualization_id']+'/exports',json={'context_id':context,'revision':asset['revision'],'options':{'format':'png','width':320,'height':240}})
                assert job.is_success,job.text
                export_id=job.json()['export_id']
                for _ in range(300):
                    output=client.get(f"/api/visualizations/{asset['visualization_id']}/exports/{export_id}",params={'context_id':context}).json()
                    if output['status']!='running':break
                    time.sleep(.1)
                assert output['status']=='succeeded',output
                content=client.get(f"/api/visualizations/{asset['visualization_id']}/exports/{export_id}/files/view.png",params={'context_id':context})
                assert content.is_success and content.content.startswith(b'\x89PNG')
                assert client.delete('/api/phys/sessions/'+reopened.json()['session_id'],params={'context_id':context}).is_success
        finally:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
    after={str(p.relative_to(installed)):hashlib.sha256(p.read_bytes()).hexdigest() for p in installed.rglob('*') if p.is_file()}
    assert before==after
    root=Path(scope['root'])/saved.json()['visualization_id']
    assert (root/'asset.json').exists() and (root/'revisions/000001/spec.json').exists()
    assert len(list((root/'exports').rglob('view.png')))==1
    assert not list(root.rglob('*.vti'))
