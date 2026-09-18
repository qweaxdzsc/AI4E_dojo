"""任务创建与本地执行命令。"""

from ..tasks.create import fork_task, new_task
from ..tasks.execution import resume_run, stop_run, submit_run, wait_run
from ..tasks.query import get_run, import_run, list_runs, list_tasks, read_log


def register(commands, common) -> None:
    """注册任务与运行命令，参数不包含算法实现。"""
    p = commands.add_parser("new")
    common(p)
    p.add_argument("name")
    p.add_argument("--from", dest="source")
    p.add_argument("--key")
    p.set_defaults(
        action=lambda a: new_task(a.project, a.name, source=a.source, idempotency_key=a.key)
    )
    p = commands.add_parser("fork")
    common(p)
    p.add_argument("task_id")
    p.add_argument("--name")
    p.add_argument("--source", default="worktree", choices=["worktree", "version", "run"])
    p.add_argument("--run-id")
    p.add_argument("--baseline")
    p.add_argument("--key")
    for flag in ("datasets", "preparation", "checkpoints"):
        p.add_argument("--copy-" + flag, action="store_true")
    p.set_defaults(
        action=lambda a: fork_task(
            a.project,
            a.task_id,
            name=a.name,
            source=a.source,
            run_id=a.run_id,
            baseline_version_id=a.baseline,
            copy_datasets=a.copy_datasets,
            copy_preparation=a.copy_preparation,
            copy_checkpoints=a.copy_checkpoints,
            idempotency_key=a.key,
        )
    )
    p = commands.add_parser("run")
    common(p)
    p.add_argument("task_id")
    p.add_argument("--set", action="append", default=[])
    p.add_argument("--key")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--timeout", type=float, default=60)
    p.set_defaults(action=_run)
    for name, function in [
        ("status", get_run),
        ("stop", stop_run),
        ("wait", wait_run),
        ("logs", read_log),
    ]:
        p = commands.add_parser(name)
        common(p)
        p.add_argument("run_id")
        p.set_defaults(action=lambda a, fn=function: fn(a.project, a.run_id))
    p = commands.add_parser("resume")
    common(p)
    p.add_argument("run_id")
    p.add_argument("--checkpoint", default="latest.pt")
    p.add_argument("--key")
    p.set_defaults(
        action=lambda a: resume_run(
            a.project, a.run_id, checkpoint=a.checkpoint, idempotency_key=a.key
        )
    )
    p = commands.add_parser("tasks")
    common(p)
    p.set_defaults(action=lambda a: list_tasks(a.project))
    p = commands.add_parser("runs")
    common(p)
    p.add_argument("--task-id")
    p.set_defaults(action=lambda a: list_runs(a.project, a.task_id))
    p = commands.add_parser("import-run")
    common(p)
    p.add_argument("directory")
    p.add_argument("--task-id")
    p.set_defaults(action=lambda a: import_run(a.project, a.directory, task_id=a.task_id))


def _run(args) -> dict:
    """可选择等待运行，保持提交与执行结果的区别。"""
    value = submit_run(
        args.project,
        args.task_id,
        overrides=args.set,
        idempotency_key=args.key,
        overwrite=args.overwrite,
    )
    return wait_run(args.project, value["id"], timeout=args.timeout) if args.wait else value
