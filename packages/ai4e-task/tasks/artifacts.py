"""运行产物公开目录：固定运行身份，试跑不成为默认正式输入。"""

from pathlib import Path

from .records import list_runs


def list_stage_artifacts(
    project, task_id: str, roots: dict | None = None, *, include_unmatched: bool = False
) -> list[dict]:
    """列出成功正式产物及终止运行已提交的恢复权重，不整文件核验。

    切步名单只回答还有没有、能不能列。字节是否仍是当初那份留给恢复训练、
    提交推理和读取准备；列举时再打检查点会把切步卡在半分钟。
    """
    from ai4e_spec.artifacts.indexes import INDEX_VERSION, validate_asset_record

    from ..storage.files import read_json
    from ..storage.layout import task_dir
    from .asset_matching import match_asset
    from .descriptions import describe_recipe

    folder = task_dir(project, task_id)
    description = describe_recipe(folder / "recipe", cache_dir=folder / ".dojo/descriptions")[
        "description"
    ]
    if description is None:
        return []
    result = []
    visible = {"project": Path(project).resolve()}
    if roots:
        visible.update({name: Path(root).resolve() for name, root in roots.items()})
    for run in list_runs(project, task_id):
        if (
            run["status"] not in {"succeeded", "stopped", "failed"}
            or run.get("operation_mode", "execute") != "execute"
        ):
            continue
        index_path = Path(run["run_dir"]) / "artifacts/assets.json"
        if not index_path.is_file():
            continue
        index = read_json(index_path)
        if index.get("schema_version") != INDEX_VERSION:
            continue
        for item in index.get("items", {}).values():
            try:
                validate_asset_record(item)
                path = Path(item["path"]).resolve()
            except (ValueError, TypeError, OSError):
                continue
            if not path.is_file() or any(
                not Path(p).exists()
                or not any(Path(p).resolve().is_relative_to(root) for root in visible.values())
                for p in item.get("dependencies", [])
            ):
                continue
            location = next(
                ((name, root) for name, root in visible.items() if path.is_relative_to(root)), None
            )
            if location is None:
                continue
            root_id, root = location
            for binding, requirement in description["inputs"].items():
                matched = match_asset(item, requirement, status=run["status"])
                if not matched["matches"] and not (
                    include_unmatched and matched["missing"] and not matched["conflicts"]
                ):
                    continue
                result.append(
                    {
                        "run_id": run["id"],
                        "task_id": task_id,
                        "binding": binding,
                        "root": root_id,
                        "path": str(path.relative_to(root)),
                        "name": item["name"],
                        "file_name": path.name,
                        "kind": item["kind"],
                        "stage": item["stage"],
                        "semantics": item.get("semantics", {}),
                        "matching": matched,
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
    from .operation_sources import invoke_source, operation_context

    try:
        context = operation_context(project, run["task_id"], run=run)
        description = invoke_source(
            context["source"], context["recipe"], {"operation": "run_metrics", "run": run}
        )
        result.update(
            {key: description[key] for key in ("evaluation", "post", "infer") if key in description}
        )
    except (ValueError, OSError) as exc:
        result["description_error"] = str(exc)
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
