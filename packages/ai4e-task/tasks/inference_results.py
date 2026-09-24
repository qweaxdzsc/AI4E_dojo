"""按运行清单列出推理交付，不扫描旧文件或加载物理场数组。"""

from pathlib import Path

from ..storage.files import read_json
from .checkpoints import file_digest, inspect_inference
from .inference import read_inference_batch
from .records import get_run


def _member(path: Path, run: dict) -> dict:
    """结果成员必须属于本次子运行的数据或运行目录。"""
    resolved = path.resolve()
    roots = [Path(run[key]).resolve() for key in ("data_dir", "run_dir")]
    if not any(resolved.is_relative_to(root) for root in roots) or path.is_symlink():
        raise ValueError("inference_result_outside_run")
    if not resolved.is_file():
        raise ValueError("inference_result_missing: " + path.name)
    return {
        "name": path.name,
        "path": str(resolved),
        "size": resolved.stat().st_size,
        "revision": file_digest(resolved),
    }


def inference_results(project: str | Path, task_id: str, identity: str) -> dict:
    """应用解释固定结果；Task 只核对运行归属和返回文件引用。"""
    from ..storage.layout import inside, task_dir
    from .operation_sources import operation_context

    batch = read_inference_batch(project, task_id, identity)
    folder = inside(task_dir(project, task_id) / ".dojo/inference_batches", identity)
    request = read_json(folder / "request.json")
    children = [*request.get("inherited_children", []), *batch["children"]]
    runs = {child["run_id"]: get_run(project, child["run_id"]) for child in children}
    if any(run["task_id"] != task_id for run in runs.values()):
        raise ValueError("inference_run_task_mismatch")
    context = operation_context(project, task_id, batch_id=identity)
    result = inspect_inference(
        "read_results", context=context, payload={"batch": batch, "request": request, "runs": runs}
    )
    for item in result["items"]:
        if item["run_id"] not in runs:
            raise ValueError("inference_result_unknown_run")
        item["files"] = [
            _member(Path(member["path"]), runs[item["run_id"]]) for member in item["files"]
        ]
    return result
