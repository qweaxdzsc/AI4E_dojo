"""主控诊断会话与隐藏worker预检；不充当四个正式研究单元。"""

import json
import subprocess
import sys
import tarfile
import uuid
from pathlib import Path

from ..io import digest, read_json, write_json
from .isolation import clean_environment, execute, policy
from .network import PublicProxy
from .sessions import invoke
from .worker_check import check_worker


def check_runtime(root, delivery):
    """同款沙箱实测Python HTTPS、SQLite、Dojo公共资料与组件，不给实验组产物。"""
    root, delivery = Path(root), Path(delivery)
    cfg = read_json(root / "comparison-protocol.json")
    workspace = root / "runtime-diagnostic" / str(uuid.uuid4())
    for name in ("home", "tmp", "cache", "agent-state"):
        (workspace / name).mkdir(parents=True)
    environment = workspace / "environment"
    subprocess.run(
        [sys.executable, "-m", "venv", "--without-pip", "--copies", str(environment)], check=True
    )
    site = (
        environment / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    with tarfile.open(delivery / "public-packages.tar") as archive:
        archive.extractall(site, filter="data")
    import zipfile

    for wheel in (delivery / "dojo-resources/wheels").glob("*.whl"):
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(site)
    script = workspace / "probe.py"
    script.write_text("""import json, pathlib, sqlite3, ssl, urllib.request, venv
import numpy as np
import torch
import ai4e_task as task
from ai4e_core.abilities.data.stats.population import PopulationMoments
root=pathlib.Path.cwd()
venv.create(root/'nested-environment',with_pip=False,symlinks=False)
with sqlite3.connect(root/'probe.sqlite3') as db:
    assert db.execute('select 1').fetchone()==(1,)
with urllib.request.urlopen('https://pypi.org/simple/',timeout=20) as response:
    assert response.status==200
cases=task.list_examples();assert cases
case=next(c for c in cases if c['type']=='standalone')
assert task.check_example(case['id'])['ok']
copy=task.copy_example(case['id'],root/'case-copy')
assert (root/'case-copy'/copy['documentation']['entry']).is_file()
assert task.read_help_topic('capability:training')['content']
project=task.create_project(root/'project',name='runtime precheck')
moments=PopulationMoments(2);moments.update(np.array([[1.,2.],[3.,6.]]))
assert moments.finalize()['mean']==[2.,4.]
x=torch.ones(4,device='mps'); assert float((x*x).sum().cpu())==4
torch.mps.synchronize()
print(json.dumps({'sqlite':True,'python_https':True,'venv_alias':True,'public_task_import':True,'example_copy':True,'help_read':True,'project_database':True,'core_component':True,'mps':True}))
""")
    with PublicProxy(workspace / "network.jsonl") as proxy:
        env = clean_environment(
            workspace,
            {
                "HTTPS_PROXY": f"http://127.0.0.1:{proxy.port}",
                "HTTP_PROXY": f"http://127.0.0.1:{proxy.port}",
                "NO_PROXY": "",
                "no_proxy": "",
            },
        )
        body = policy([workspace], cfg["runtime_readonly_roots"], proxy_port=proxy.port)
        (workspace / "policy.sbpl").write_text(body)
        process = execute(body, [environment / "bin/python", script], workspace, env, timeout=60)
    result = {
        "passed": process.returncode == 0,
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "script_sha256": digest(script),
        "workspace": str(workspace),
        "policy_sha256": digest(workspace / "policy.sbpl"),
    }
    write_json(root / "evidence/runtime-capability.json", result)
    return result


def check_cli(root):
    """真实新建/续接CLI，检查工具进程权限、原始usage和实际工作根。"""
    root = Path(root)
    cfg = read_json(root / "comparison-protocol.json")
    attempt_id = str(uuid.uuid4())
    workspace = root / "cli-diagnostic" / attempt_id
    experiment = workspace / "experiment-precheck"
    for name in ("home", "tmp", "cache", "agent-state", "evidence"):
        (experiment / name).mkdir(parents=True, exist_ok=True)
    forbidden = root / "cli-private-sentinel.txt"
    forbidden.write_text("controller-only")
    script = experiment / "diagnostic.py"
    script.write_text(f"""import json, pathlib, socket, subprocess, sys
own=pathlib.Path({str(experiment)!r})
assert pathlib.Path.cwd()==pathlib.Path({str(workspace)!r})
target=pathlib.Path({str(forbidden)!r})
checks={{}}
(own/'allowed').write_text('ok')
checks['own_read_write']=(own/'allowed').read_text()=='ok'
def denied(name, operation):
    try: operation()
    except PermissionError: checks[name]=True
    else: checks[name]=False
denied('forbidden_read',target.read_text)
denied('forbidden_write',lambda: target.write_text('not allowed'))
denied('parent_list',lambda:list(pathlib.Path({str(root)!r}).iterdir()))
link=own/'escape'
if not link.is_symlink() and not link.exists():link.symlink_to(target)
denied('link_read',link.read_text)
p=subprocess.run(['/bin/cat',str(target)],capture_output=True,text=True)
checks['child_denied']=p.returncode!=0 and 'Operation not permitted' in p.stderr
s=socket.socket();s.settimeout(2)
denied('local_service',lambda:s.connect(('127.0.0.1',8000)))
s.close()
assert all(checks.values()),checks
out=own/('probe-'+sys.argv[1]+'.json')
out.write_text(json.dumps(checks))
print(json.dumps(checks))
""")
    expected_digest = digest(script)
    protocol = {
        "session_workspace_root": str(workspace),
        "experiment_root": str(experiment),
        "model": cfg["model"],
        "reasoning": cfg["reasoning"],
        "runtime_readonly_roots": cfg["runtime_readonly_roots"],
    }
    interpreter = str(Path(sys.executable).resolve())
    session = None
    rows = []
    for number in (1, 2):
        evidence = root / f"evidence/cli-precheck/{attempt_id}/{number}"
        message = f"这是一项基础设施诊断，不是研究实验。保持工作目录{workspace}，不要修改脚本，实际执行：{interpreter} {script} {number}。只报告返回结果，不访问额外资料，不创建技能或任务。"
        result = invoke(protocol, message, evidence, session)
        if result["returncode"] != 0 or not result["session_id"]:
            raise RuntimeError(f"CLI启动失败，见{evidence}")
        if session is not None and result["session_id"] != session:
            raise ValueError("恢复未保持同会话")
        session = result["session_id"]
        checks = read_json(experiment / f"probe-{number}.json")
        if not all(checks.values()) or digest(script) != expected_digest:
            raise ValueError("诊断代码或权限不符合")
        usages = []
        for path in (evidence / "raw-rollouts").glob("*.jsonl"):
            for line in path.read_text().splitlines():
                event = json.loads(line)
                if event.get("type") == "token_usage_record":
                    usages.append(event["payload"])
        if not usages:
            raise ValueError("未捕获供应商原始请求usage，不能启动成本对照")
        rows.append(
            {
                "attempt": number,
                "session_id": session,
                "checks": checks,
                "request_usage_count": len(usages),
                "evidence": str(evidence),
            }
        )
    result = {
        "passed": True,
        "diagnostic_only": True,
        "attempts": rows,
        "same_session_resume": True,
    }
    write_json(root / "evidence/cli-capability.json", result)
    return result


def check_inference(root):
    """私有依赖只在主控安装，真实MPS重放与恶意读取/网络拒绝不交付组内。"""
    root = Path(root)
    destination = root / "evaluation-runtime"
    subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--no-sync",
            "--python",
            str(Path(sys.executable).resolve()),
            "python",
            "-m",
            "venv",
            "--without-pip",
            "--copies",
            str(destination),
        ],
        check=True,
    )
    site = (
        destination / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    with tarfile.open(root / "delivery/public-packages.tar") as archive:
        archive.extractall(site, filter="data")
    result = check_worker(root, latency_seed=42)
    if not result["passed"]:
        raise ValueError("真实隔离推理未通过")
    return result
