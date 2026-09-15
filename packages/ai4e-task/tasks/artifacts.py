"""运行产物公开目录：固定运行身份，试跑不成为默认正式输入。"""

from pathlib import Path

from .query import list_runs


def list_stage_artifacts(project, task_id: str, roots: dict | None = None) -> list[dict]:
    """列出成功正式运行的可交接产物；可见根内文件即可，不猜测缺失文件。"""
    result = []
    visible = {"project": Path(project).resolve()}
    if roots:
        visible.update({name: Path(root).resolve() for name, root in roots.items()})
    for run in list_runs(project, task_id):
        if run["status"] != "succeeded" or run.get("operation_mode", "execute") != "execute":
            continue
        preferred = Path(run["run_dir"]) / "artifacts/inference-results.json"
        if not preferred.is_file():
            preferred = Path(run["run_dir"]) / "artifacts/physical-predictions.json"
        targets = [
            ("train.manifest", Path(run["data_dir"]) / "manifest.json"),
            ("train.preparation", Path(run["run_dir"]) / "artifacts/preparation.json"),
            ("post.results", preferred),
        ]
        targets += [
            ("post.checkpoint", p)
            for p in sorted((Path(run["run_dir"]) / "checkpoints").glob("*.pt"))
        ]
        for binding, path in targets:
            if not path.is_file():
                continue
            resolved = path.resolve()
            match = next(
                ((name, root) for name, root in visible.items() if resolved.is_relative_to(root)),
                None,
            )
            if not match:
                continue
            root_id, root = match
            result.append(
                {
                    "run_id": run["id"],
                    "task_id": task_id,
                    "binding": binding,
                    "root": root_id,
                    "path": str(resolved.relative_to(root)),
                    "name": path.name,
                }
            )
    return result


def read_run_metrics(project, run_id: str) -> dict:
    """读取现有训练和后处理记录，不从日志推测不存在的指标。"""
    from ..storage.files import read_json
    from .query import get_run

    run = get_run(project, run_id)
    result = {
        "run_id": run_id,
        "status": run["status"],
        "created_at": run.get("created_at"),
        "history": [],
        "post": None,
        "resources": None,
    }
    root = Path(run["run_dir"])
    training = root / "artifacts/training.json"
    if training.is_file():
        record = read_json(training)
        result["training"] = record
        result["history"] = record.get("history", [])
    elif isinstance(run.get("summary", {}).get("reports", {}).get("train"), dict):
        record = run["summary"]["reports"]["train"]
        result["training"] = record
        result["history"] = record.get("history", [])
    result["evaluation"] = (
        run.get("summary", {}).get("reports", {}).get("post", {}).get("evaluation")
    )
    physical = root / "artifacts/inference-results.json"
    if not physical.is_file():
        physical = root / "artifacts/physical-predictions.json"
    if physical.is_file():
        record = read_json(physical)
        result["evaluation"] = {
            "metrics": record.get("metrics", {}),
            "status": record.get("status"),
        }
    if physical.is_file():
        result["evaluation"]["samples"] = [
            {"sample": r.get("sample", r.get("sample_id")), "metrics": r.get("metrics", {})}
            for r in record.get("results", [])
        ]
    post = root / "artifacts/post-progress.json"
    if post.is_file():
        result["post"] = read_json(post)
    infer = root / "artifacts/inference-progress.json"
    if infer.is_file():
        result["infer"] = read_json(infer)
    if run.get("pid") and run["status"] in {"running", "stopping"}:
        import subprocess

        measured = subprocess.run(
            ["ps", "-p", str(run["pid"]), "-o", "%cpu=,rss="],
            capture_output=True,
            text=True,
            check=False,
        )
        fields = measured.stdout.split()
        if measured.returncode == 0 and len(fields) == 2:
            result["resources"] = {
                "cpu_percent": float(fields[0]),
                "resident_bytes": int(fields[1]) * 1024,
            }
    return result
