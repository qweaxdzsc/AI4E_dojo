"""独立 wheel 安装后的推理管理门面、排队执行与 HTTP 启动。"""

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from tests.integration.test_task_management import recipe


def test_installed_task_and_server_inference(tmp_path):
    repository = Path(__file__).resolve().parents[2]
    wheels = tmp_path / "wheels"
    products = ("ai4e-spec", "ai4e-core", "ai4e-contrib", "ai4e-task", "ai4e-server")
    for name in products:
        subprocess.run(
            ["uv", "build", "--package", name, "--wheel", "--out-dir", str(wheels)],
            cwd=repository,
            check=True,
            capture_output=True,
        )
    installed = tmp_path / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )

    def inventory():
        return {
            str(p.relative_to(installed)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in installed.rglob("*")
            if p.is_file()
        }

    before = inventory()
    template = recipe(tmp_path)
    script = tmp_path / "installed-check.py"
    script.write_text("""import sys
from pathlib import Path
import ai4e_task as task, ai4e_server, ai4e_spec, ai4e_core
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient
for module in (task, ai4e_server, ai4e_spec, ai4e_core):
    assert Path(module.__file__).is_relative_to(Path(sys.argv[1]))
project = Path.cwd() / 'installed-project'
task.create_project(project)
item = task.new_task(project, 'installed', source=sys.argv[2])
queued = task.submit_run(project, item['id'], start=False)
assert task.get_run(project, queued['id'])['status'] == 'queued'
task.start_captured_run(project, queued['id'])
assert task.wait_run(project, queued['id'])['status'] == 'succeeded'
assert task.list_inference_batches(project, item['id']) == []
assert task.list_inference_checkpoints(project, item['id']) == []
assert task.inference_devices(project)[0]['id'] == 'cpu'
with TestClient(create_app(Settings(Path.cwd()/'server', Path(sys.argv[2]), []))) as client:
    assert client.get('/api/v1/capabilities').json()['inference']['batch']
    assert '/api/v1/projects/{project}/tasks/{identity}/inference/batches' in client.get('/openapi.json').json()['paths']
print('installed inference management and execution passed')
""")
    result = subprocess.run(
        [sys.executable, "-B", str(script), str(installed), str(template)],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert inventory() == before
