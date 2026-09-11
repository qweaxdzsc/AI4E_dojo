"""服务重建不重复启动任务，停止与事件读取仍来自同一 task 收据。"""

import time
from fastapi.testclient import TestClient
import ai4e_task as task
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from tests.integration.test_task_management import recipe


def test_restart_stop_and_event_recovery(tmp_path):
    settings = Settings(tmp_path / "platform", recipe(tmp_path))
    app = create_app(settings)
    with TestClient(app) as c:
        p = c.post("/api/v1/projects", json={"name": "runtime"}).json()["id"]
        t = c.post(f"/api/v1/projects/{p}/tasks", json={"name": "run"}).json()["id"]
        project = app.state.services.project(p)
        r = task.submit_run(project, t, overrides=["delay=20"], idempotency_key="one")
    with TestClient(create_app(settings)) as c:
        url = f"/api/v1/projects/{p}/runs/{r['id']}"
        assert c.get(url).json()["id"] == r["id"]
        deadline = time.monotonic() + 10
        while not task.read_log(project, r["id"]) and time.monotonic() < deadline:
            time.sleep(0.05)
        assert task.read_log(project, r["id"])
        stopped = c.post(url + "/stop")
        assert stopped.status_code == 200, stopped.text
        assert stopped.json()["status"] == "stopped"
        events = c.get(url + "/events")
        assert '"status": "stopped"' in events.text
        assert len(c.get(f"/api/v1/projects/{p}/runs").json()) == 1


def test_fixed_report_evidence_and_missing_comparison(tmp_path):
    """新运行不替换报告的旧证据，失败指标不当作零。"""
    settings=Settings(tmp_path/'platform',recipe(tmp_path))
    app=create_app(settings)
    with TestClient(app) as c:
        p=c.post('/api/v1/projects',json={'name':'evidence'}).json()['id']
        t=c.post(f'/api/v1/projects/{p}/tasks',json={'name':'baseline'}).json()['id']
        base=app.state.services.project(p)
        a=task.wait_run(base,task.submit_run(base,t)['id'])
        assert a['status']=='succeeded'
        body={'title':'固定证据','text':'第一轮结果','run_ids':[a['id']]}
        saved=c.put(f'/api/v1/projects/{p}/report',json=body).json()
        b=task.wait_run(base,task.submit_run(base,t,overrides=['fail=true'])['id'])
        comparison=c.post(f'/api/v1/projects/{p}/compare',json={'mode':'runs','left':a['id'],'right':b['id']}).json()
        assert comparison['metrics']['score']['status']=='missing'
        assert comparison['metrics']['score']['right']['value'] is None
        repeated=c.put(f'/api/v1/projects/{p}/report',json=body).json()
        assert repeated['evidence']==saved['evidence']
    with TestClient(create_app(settings)) as c:
        assert c.get(f'/api/v1/projects/{p}/report').json()['evidence']==saved['evidence']
