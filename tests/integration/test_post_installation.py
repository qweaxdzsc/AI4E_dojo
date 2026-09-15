"""实际安装副本可从仓库外调用，运行数据不写包安装目录。"""

import json
import subprocess
import sys


def test_installed_public_evaluation(tmp_path):
    code = """import json, pathlib
import ai4e_core.applications.aero_cfd.post as post
import ai4e_task
print(json.dumps({"path":post.__file__,"metrics":post.metric_catalog(),"task_api":callable(ai4e_task.submit_post_metrics)}))
"""
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True, check=True
    )
    value = json.loads(result.stdout)
    assert "site-packages" in value["path"], "需要先安装实际wheel后验收"
    assert len(value["metrics"]) == 5 and value["task_api"]
    assert not list(tmp_path.iterdir())


from tests.integration.test_task_post_metrics import (
    results_project as results_project,  # noqa: PLC0414 - pytest跨模块夹具
)


def test_installed_worker_from_external_directory(results_project, tmp_path):
    """真实安装进程从仓库外提交、查询和导出，不能只验证import。"""
    import os

    directory = tmp_path / "external"
    directory.mkdir()
    code = """import sys,json,time,pathlib
import ai4e_task as task
root=pathlib.Path(sys.argv[1])
items=task.post_results(root,'t')['items'][:2]
job=task.submit_post_metrics(root,'t',{'results':[{'id':i['id'],'revision':i['revision']} for i in items],'fields':['surface:pressure:scalar'],'metrics':['mae'],'idempotency_key':'installed-post'})
for _ in range(200):
    job=task.read_post_metrics(root,'t',job['id'])
    if job['status'] in {'succeeded','failed','partial','interrupted'}: break
    time.sleep(.1)
assert job['status']=='succeeded',job
assert all(r['values']['mae']==2 for r in job['rows'])
output=task.export_post_metrics(root,'t',job['id'],{'format':'csv'})
assert pathlib.Path(output['path']).is_relative_to(root/'tasks/t/data/post')
assert pathlib.Path(output['path']).read_text(encoding='utf-8-sig').count('succeeded')==2
assert 'site-packages' in task.__file__
print(json.dumps({'job':job['id'],'output':output,'module':task.__file__}))
"""
    response = subprocess.run(
        [sys.executable, "-c", code, str(results_project)],
        cwd=directory,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert response.returncode == 0, response.stderr
    assert json.loads(response.stdout)["output"]["name"].endswith(".csv")
    assert not list(directory.iterdir())
