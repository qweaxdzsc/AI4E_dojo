"""运行产物公开目录：固定运行身份，试跑不成为默认正式输入。"""

from pathlib import Path

from .records import list_runs


def list_stage_artifacts(project, task_id: str, roots: dict | None = None) -> list[dict]:
    """列出成功正式产物及终止运行已提交的恢复权重，不整文件核验。

    切步名单只回答还有没有、能不能列。字节是否仍是当初那份留给恢复训练、
    提交推理和读取准备；列举时再打检查点会把切步卡在半分钟。
    """
    from ..projects.datasets import run_physical_manifest

    result = []
    visible = {"project": Path(project).resolve()}
    if roots:
        visible.update({name: Path(root).resolve() for name, root in roots.items()})
    for run in list_runs(project, task_id):
        if run["status"] not in {"succeeded", "stopped", "failed"} or run.get(
            "operation_mode", "execute"
        ) != "execute":
            continue
        recovery_only = run["status"] != "succeeded"
        from ..storage.files import read_json
        from ai4e_spec.artifacts.indexes import INDEX_VERSION, validate_asset_record

        index_path = Path(run["run_dir"]) / "artifacts/assets.json"
        targets = []
        if index_path.is_file():
            index = read_json(index_path)
            if index.get("schema_version") != INDEX_VERSION:
                continue
            for item in index.get("items", {}).values():
                try:
                    validate_asset_record(item)
                    path = Path(item["path"])
                except (ValueError, TypeError, OSError):
                    continue
                if item["kind"] == "checkpoint":
                    bindings = ["inputs.train.resume"]
                    if not recovery_only:
                        bindings.insert(0, "inputs.infer.checkpoint")
                elif recovery_only:
                    continue
                elif item["kind"] == "preparation":
                    bindings = ["inputs.train.preparation", "inputs.infer.preparation"]
                elif item["kind"] == "dataset":
                    bindings = ["inputs.trainprep.dataset"]
                elif item["stage"] == "infer" and item["name"] == "results":
                    bindings = ["inputs.post.results"]
                else:
                    bindings = []
                targets.extend((binding, path) for binding in bindings)
        shared = None if recovery_only else run_physical_manifest(project, run)
        if shared is not None and not any(p == shared for _, p in targets):
            targets.append(("inputs.trainprep.dataset", shared))
        for binding, path in targets:
            if path is None or not path.is_file():
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
