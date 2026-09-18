"""交付启动器经 CLI 创建任务，消费历史固定结果，并核对 worker 包来源。"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def execute(root: Path, case: str):
    """只在验收副本加入环境记录；发布模板和历史科学产物保持原字节。"""
    release = root / "public-conventions"
    output = release / f"{case}-cli"
    output.mkdir(exist_ok=False)
    total = 5000 if case == "burgers" else 8000
    prior = json.loads((root / f"continuation/{case}-dojo-{total}-final/summary.json").read_text())
    results = Path(prior["results"])
    hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in results.parent.iterdir()
        if p.is_file()
    }

    def cli(*args):
        response = subprocess.run(
            [str(release / "run.sh"), "-m", "ai4e_task", *args, "--json"],
            cwd=output,
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
        return json.loads(response.stdout)

    project = output / "project"
    cli("project", "new", str(project))
    records = {}
    for name in ["recipe", "burgers"] if case == "burgers" else ["tokamak"]:
        copied = output / name
        shutil.copytree(release / "release" / name, copied)
        # 在用户可编辑正文追加只读诊断；算法调用仍是已交付的 post。
        post = copied / "post.py"
        diagnostic = """
    import sys, hashlib
    import ai4e_spec, ai4e_core, ai4e_contrib, ai4e_task
    modules = [ai4e_spec, ai4e_core, ai4e_contrib, ai4e_task]
    origins = {m.__name__: {"path": m.__file__, "sha256": hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()} for m in modules}
    environment = session.output_dir("post") / "environment.json"
    environment.write_text(json.dumps({"python": sys.executable, "modules": origins}))
    session.report({"environment": str(environment)}, stage="environment")
"""
        post.write_text(
            post.read_text().replace("    return value\n", diagnostic + "    return value\n")
        )
        item = cli("new", name, "--from", str(copied), "--project", str(project))
        job = cli(
            "run",
            item["id"],
            "--project",
            str(project),
            "--wait",
            "--timeout",
            "50",
            "--set",
            "pipeline.stages=[post]",
            "--set",
            f"inputs.post.results={results}",
        )
        assert job["status"] == "succeeded", job
        env = json.loads(Path(job["summary"]["reports"]["environment"]["environment"]).read_text())
        assert env["python"] == sys.executable
        for info in env["modules"].values():
            path = Path(info["path"])
            assert path.is_relative_to(release / "installed"), info
            assert hashlib.sha256(path.read_bytes()).hexdigest() == info["sha256"]
        metrics = json.loads(Path(job["summary"]["reports"]["post"]["metrics_file"]).read_text())
        assert metrics["metrics"] == json.loads(results.read_text())["metadata"]["metrics"]
        records[name] = {"task_id": item["id"], "run": job, "environment": env}
    assert hashes == {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in hashes}
    (output / "report.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "case": case,
                "historical_results": str(results),
                "historical_hashes": hashes,
                "entries": records,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--case", required=True, choices=["burgers", "tokamak"])
    args = parser.parse_args()
    execute(args.root, args.case)
