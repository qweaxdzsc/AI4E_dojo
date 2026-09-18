"""真实 wheel 的仓库外跨任务字段扩展、准备、训练与独立推理。"""

import json
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

from tests.integration.test_recipe_extensions import extension_case


def test_installed_shared_extension_two_tasks(tmp_path):
    root = Path(__file__).resolve().parents[2]
    wheels = tmp_path / "wheels"
    subprocess.run(
        ["uv", "build", "--all-packages", "--wheel", "--out-dir", str(wheels)],
        cwd=root,
        check=True,
        capture_output=True,
    )
    envdir = tmp_path / "installed"
    subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", str(envdir)],
        check=True,
        capture_output=True,
    )
    python = envdir / "bin/python"
    site = (
        envdir
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    (site / "third_party.pth").write_text(sysconfig.get_path("purelib") + "\n")
    packages = [
        next(wheels.glob(name + "-*.whl"))
        for name in ("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task")
    ]
    clean = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
    clean.update(OMP_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--force-reinstall",
            *map(str, packages),
        ],
        check=True,
        capture_output=True,
        env=clean,
    )
    source, cfg = extension_case(tmp_path / "extension", "field_mapping")
    cfg["dataset"]["processed_name"] = "extended_fields"
    import yaml

    (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    script = tmp_path / "verify.py"
    script.write_text("""import json,sys,shutil
from pathlib import Path
import ai4e_task as task
assert str(Path(sys.executable).parent.parent) in task.__file__
project=Path(sys.argv[1]); source=Path(sys.argv[2])
task.create_project(project)
a=task.new_task(project,"producer",source=source)
b=task.new_task(project,"consumer",source=source)
def execute(item, overrides):
    run=task.wait_run(project,task.submit_run(project,item["id"],overrides=overrides)["id"],timeout=180)
    assert run["status"]=="succeeded",run
    return run
first=execute(a,["pipeline.stages=[rawprep]"])
shared=task.get_shared_dataset(project,"extended_fields")
assert shared["status"]=="available"
from ai4e_core.abilities.data.source.manifest import ManifestIndex
index=ManifestIndex(shared["manifest_path"])
assert "volume_speed" in index.read("train")
current=task.read_configuration(project,b["id"])
task.bind_shared_dataset(project,b["id"],"extended_fields",revision=current["revision"])
# 原始网格不可见后，另一个任务仍能准备、训练和独立推理。
raw=Path(current["config"]["dataset"]["root"])
raw.rename(raw.with_name(raw.name+"-not-visible"))
second=execute(b,["pipeline.stages=[trainprep,train]"])
prep=Path(second["run_dir"])/"artifacts/preparation.json"
weight=Path(second["run_dir"])/"checkpoints/last.pt"
record=json.loads(prep.read_text())
assert "volume_speed" in record["normalization"]["fields"]
third=execute(b,["pipeline.stages=[infer]","infer.checkpoint="+str(weight),"infer.preparation="+str(prep),"train.preparation="+str(prep),"infer.query=false"])
assert (Path(third["run_dir"])/"artifacts/inference-results.json").is_file()
# 显式重做物理数据后，消费任务的配置、准备、检查点与推理结果不得被回写。
frozen=[project/"tasks"/b["id"]/"recipe/config.yaml",prep,weight,Path(third["run_dir"])/"artifacts/inference-results.json"]
before={str(p):p.read_bytes() for p in frozen}
raw.with_name(raw.name+"-not-visible").rename(raw)
replacement=task.wait_run(project,task.submit_run(project,a["id"],overrides=["pipeline.stages=[rawprep]"],overwrite=True)["id"],timeout=180)
assert replacement["status"]=="succeeded",replacement
assert all(p.read_bytes()==before[str(p)] for p in frozen)
assert task.run_physical_manifest(project,first) is None
print(json.dumps({"producer":first["id"],"consumer":second["id"],"inference":third["id"],"shared":shared["manifest_path"]}))
""")
    result = subprocess.run(
        [str(python), str(script), str(tmp_path / "project"), str(source)],
        cwd=tmp_path,
        env=clean,
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "shared" in json.loads(result.stdout.strip().splitlines()[-1])
