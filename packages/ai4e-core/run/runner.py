"""开车：读配置、接日志、调用管道、请写入方落记录。"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ai4e_core.applications.base import Pipeline, Stage, StageError
from ai4e_core.base.config import load_config
from ai4e_core.run.writer import RunWriter

LOGGER = logging.getLogger("ai4e_core.run")


def run_from_config(
    config_path: str | Path,
    *,
    builders: Mapping[str, Callable[[Mapping[str, Any]], Stage]],
    overrides: Mapping[str, Any] | Sequence[str] | None = None,
    run_root: str | Path | None = None,
    recipe_dir: str | Path | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    continue_on_error: bool = False,
) -> dict[str, Any]:
    """读配置并执行已选阶段，留下运行记录。

    Args:
        config_path: 案例 YAML 路径。
        builders: 阶段名到装配函数。
        overrides: 点号覆盖。
        run_root: 运行根目录；缺省读 ``run.root`` 或当前目录。
        recipe_dir: 案例目录，用于解析相对的随包统计量路径。
        dry_run: 为真时不写训练 ``.pt``。
        overwrite: 将允许覆盖的执行意图传给业务写入步骤。
        continue_on_error: 逐项执行遇错时是否继续。

    Returns:
        含运行目录、展开配置、批量计数和业务报告的作业上下文。
    """
    source = Path(config_path)
    config = load_config(source, overrides)
    root = Path(run_root) if run_root is not None else _run_root(config)
    writer = RunWriter.create(root)
    writer.write_inputs(source, config)
    handler = writer.attach_log(LOGGER)
    ctx: dict[str, Any] = {
        "config": config,
        "dry_run": dry_run,
        "overwrite": overwrite,
        "continue_on_error": continue_on_error,
        "recipe_dir": None if recipe_dir is None else Path(recipe_dir),
        "run_dir": writer.run_dir,
        "summary": {},
    }
    LOGGER.info("开始运行 %s", writer.run_dir)
    try:
        pipeline = Pipeline.from_config(config, builders)
        ctx = pipeline.run(ctx)
        ctx["summary"] = _job_summary(ctx, failed=bool(ctx.get("batch", {}).get("failed")))
        writer.write_summary(ctx["summary"])
        LOGGER.info(
            "运行完成：成功=%s；失败=%s；未执行=%s",
            ctx["summary"]["success"],
            ctx["summary"]["failed_count"],
            ctx["summary"]["unexecuted"],
        )
        return ctx
    except StageError as exc:
        ctx = getattr(exc, "context", ctx)
        ctx["summary"] = _job_summary(ctx, failed=True, error=exc)
        writer.write_summary(ctx["summary"])
        LOGGER.exception("阶段失败: %s / %s", exc.stage, exc.step_name)
        raise
    except Exception as exc:
        ctx["summary"] = _job_summary(ctx, failed=True, error=exc)
        writer.write_summary(ctx["summary"])
        LOGGER.exception("运行失败")
        raise
    finally:
        LOGGER.removeHandler(handler)
        handler.close()


def _run_root(config: Mapping[str, Any]) -> Path:
    """读取 ``run.root``，缺省为当前目录。"""
    section = config.get("run")
    if isinstance(section, Mapping) and section.get("root"):
        return Path(str(section["root"]))
    return Path.cwd()


def _job_summary(
    ctx: Mapping[str, Any],
    *,
    failed: bool,
    error: BaseException | None = None,
) -> dict[str, Any]:
    """整理作业摘要：计数、逻辑名、业务报告与失败步骤。"""
    batch = ctx.get("batch", {})
    summary = {
        "failed": failed,
        "run_dir": str(ctx.get("run_dir", "")),
        "dry_run": bool(ctx.get("dry_run")),
        **{key: batch.get(key, 0) for key in ("total", "attempted", "success", "unexecuted")},
        "failed_count": batch.get("failed", 0),
        "failures": batch.get("failures", []),
        "results": batch.get("results", []),
        "names": list(ctx.get("names") or batch.get("names") or []),
        "reports": ctx.get("reports", {}),
    }
    if isinstance(error, StageError):
        summary.update(stage=error.stage, step=error.step_name, error=str(error.cause))
    elif error is not None:
        summary["error"] = str(error)
    return summary
