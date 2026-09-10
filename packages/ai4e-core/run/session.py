"""脚本运行会话：一次配置、一次记录；为普通阶段函数设置并恢复日志上下文。"""

import argparse
import contextvars
import time
from copy import deepcopy
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.events import LOGGER, event, operation, phase

from .writer import RunWriter

CURRENT = contextvars.ContextVar("ai4e_session", default=None)


def load_recipe_config(path, overrides=None):
    """旧外流配置加载兼容入口；新案例通过 config_loader 提供自己的解析。"""
    from ai4e_core.applications.aero_cfd.configuration import load_configuration

    return load_configuration(path, overrides)


def launch(stages, *, script, argv=None, only=None, resolver=None, config_loader=None) -> int:
    """通用启动入口；config_loader 接收配置路径和覆盖，返回完整生效配置。"""
    parser = argparse.ArgumentParser(description="按 config.yaml 运行实验")
    parser.add_argument("--config", default=str(Path(script).with_name("config.yaml")))
    parser.add_argument("--set", action="append", default=[])
    parser.add_argument("--dry-run", "--check", dest="dry_run", action="store_true", default=None)
    parser.add_argument("--overwrite", action="store_true", default=None)
    parser.add_argument("--continue-on-error", action="store_true", default=None)
    args = parser.parse_args(argv)
    cfg = OmegaConf.create((config_loader or load_recipe_config)(args.config, args.set))
    return run_recipe(
        cfg,
        stages=stages,
        script=script,
        only=only,
        source_config=args.config,
        resolver=resolver,
        flags={
            "dry_run": args.dry_run
            if args.dry_run is not None
            else bool(cfg.get("execution", {}).get("dry_run", False)),
            "overwrite": args.overwrite
            if args.overwrite is not None
            else bool(cfg.get("execution", {}).get("overwrite", False)),
            "continue_on_error": args.continue_on_error
            if args.continue_on_error is not None
            else bool(cfg.get("execution", {}).get("continue_on_error", False)),
        },
    )


def run_recipe(
    cfg, *, stages, script, only=None, flags=None, source_config=None, resolver=None
) -> int:
    """在各自日志阶段中执行已选函数并汇总；恢复阶段上下文，异常返回非零。"""
    cfg = OmegaConf.create(cfg)
    selected = list(only or cfg.pipeline.stages)
    if (
        not selected
        or len(selected) != len(set(selected))
        or (not callable(stages) and set(selected) - set(stages))
    ):
        raise ValueError(f"未知、重复或空阶段选择: {selected}")
    config = OmegaConf.to_container(cfg, resolve=True)
    if resolver is not None:
        config = resolver(config, validate=bool(set(selected) & {"train", "trainprep"}))
    flags = flags or {"dry_run": False, "overwrite": False, "continue_on_error": False}
    config["execution"] = dict(flags)
    config["pipeline"]["stages"] = selected
    cfg = OmegaConf.create(config)
    code = Path(script).resolve().parent
    run_root = Path(config["run_root"]).resolve()
    if run_root == code or run_root.is_relative_to(code):
        raise ValueError("运行记录目录不能位于 recipe 代码目录内")
    writer = RunWriter.create(config["run_root"], nested=False)
    writer.write_inputs(source_config, config)
    if "train" in selected and config.get("train", {}).get("snapshot", True):
        import importlib.util

        trees = [code, Path(__file__).resolve().parents[1]]
        for module in config.get("snapshot_modules", ["ai4e_spec"]):
            spec = importlib.util.find_spec(module)
            if spec is None or spec.origin is None:
                raise ValueError(f"源码快照无法定位组件: {module}")
            trees.append(
                Path(spec.origin).parent if spec.submodule_search_locations else Path(spec.origin)
            )
        writer.write_code_snapshot(trees)
    handlers = writer.attach_logs(LOGGER)
    state = {
        "config": deepcopy(config),
        "flags": flags,
        "writer": writer,
        "script": str(Path(script).resolve()),
    }
    token = CURRENT.set(state)
    failed = False
    started = time.monotonic()
    event(
        "运行",
        "开始",
        脚本=str(Path(script).resolve()),
        运行目录=str(writer.run_dir),
        生效配置="inputs/config.yaml",
    )
    try:
        if callable(stages):
            stages(cfg)
        else:
            for name in selected:
                stage(name, stages[name], cfg)
    except Exception as exc:  # noqa: BLE001 - CLI 边界记录任意用户阶段错误并返回失败
        failed = True
        LOGGER.exception("运行失败：%s", exc)
    finally:
        batch = state.get("batch", {})
        summary = {k: batch.get(k, 0) for k in ("total", "attempted", "success", "unexecuted")}
        summary.update(
            failed=failed or bool(batch.get("failed")),
            failed_count=batch.get("failed", 0),
            failures=batch.get("failures", []),
            dry_run=flags["dry_run"],
            run_dir=str(writer.run_dir),
        )
        summary["reports"] = state.get("reports", {})
        writer.write_summary(summary)
        event(
            "运行",
            "结束",
            状态="失败"
            if summary["failed"]
            else ("检查完成，未写数据" if flags["dry_run"] else "成功"),
            成功=summary["success"],
            失败=summary["failed_count"],
            未执行=summary["unexecuted"],
            耗时=f"{time.monotonic() - started:.3f}秒",
        )
        CURRENT.reset(token)
        for handler in handlers:
            LOGGER.removeHandler(handler)
            handler.close()
    return int(summary["failed"])


def stage(name, function, *args, **kwargs):
    """在当前会话执行一个业务阶段，返回交付物并恢复日志上下文。"""
    if CURRENT.get() is None:
        raise RuntimeError("阶段必须在运行会话内执行")
    with phase(name), operation("阶段"):
        return function(*args, **kwargs)
