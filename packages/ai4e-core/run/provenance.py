"""可选托管运行上下文；独立 recipe 不需要 task 包。"""

from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from ai4e_spec.artifacts import RunContext

MANAGED = ContextVar("ai4e_managed_run", default=None)


@contextmanager
def managed_run(context: RunContext):
    """writer 提前落溯源，覆盖配置解析及启动失败；退出必须有真实会话摘要。"""
    from .writer import RunWriter

    if MANAGED.get() is not None:
        raise RuntimeError("nested_managed_run")
    roots = [Path(p).resolve() for p in (context.run_dir, context.data_dir, context.code_dir)]
    if any(
        a == b or a.is_relative_to(b) or b.is_relative_to(a)
        for i, a in enumerate(roots)
        for b in roots[i + 1 :]
    ):
        raise ValueError("overlapping_run_locations")
    directory = roots[0]
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "inputs").mkdir()
    (directory / "logs").mkdir()
    writer = RunWriter(directory)
    writer.write_provenance(context.to_dict())
    state = {"writer": writer, "context": context, "claimed": False}
    token = MANAGED.set(state)
    try:
        writer.write_code_snapshot([context.code_dir])
        yield writer
        if not state["claimed"] or not (directory / "summary.json").exists():
            raise RuntimeError("entry_did_not_complete_core_session")
    except BaseException as exc:
        # SystemExit(0) 也必须核对真实完成摘要，不能仅凭脚本退出码判成功。
        if (
            isinstance(exc, SystemExit)
            and exc.code in (0, None)
            and state["claimed"]
            and (directory / "summary.json").exists()
        ):
            pass
        else:
            import json

            summary_path = directory / "summary.json"
            summary = (
                json.loads(summary_path.read_text()) if summary_path.exists() else {"reports": {}}
            )
            writer.write_summary(
                {**summary, "failed": True, "error": str(exc), "run_dir": str(directory)}
            )
            raise
    finally:
        MANAGED.reset(token)
