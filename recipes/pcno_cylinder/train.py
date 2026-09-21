"""显式表达共同预热、两组流体训练及共用结构分支。"""

from configuration import load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.pcno.training import (
    fork_warmup,
    publish_checkpoints,
    tracked_session,
    train_branch,
)
from ai4e_core import run
from ai4e_core.abilities.training.cancellation import cancellation
from ai4e_core.base.config.conventions import resolve_input


def train(cfg, preparation=None):
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        preparation, cfg["inputs"]["train"]["preparation"], name="train.preparation"
    )
    tracking, lookup = tracked_session(session, prepared, cfg["inputs"]["train"]["resume"])
    with cancellation() as stopped:
        warmup = train_branch(
            cfg,
            prepared,
            "fluid",
            "warmup",
            session=tracking,
            resume=lookup("fluid_warmup"),
            stop_after=int(cfg["train"]["updates"] * cfg["loss"]["warmup_fraction"]),
            cancelled=stopped,
        )
        supervised_start = lookup("fluid_supervised") or fork_warmup(
            cfg, prepared, warmup, "supervised", tracking
        )
        supervised = train_branch(
            cfg,
            prepared,
            "fluid",
            "supervised",
            session=tracking,
            resume=supervised_start,
            cancelled=stopped,
        )
        physics_start = lookup("fluid_physics") or fork_warmup(
            cfg, prepared, warmup, "physics", tracking
        )
        physics = train_branch(
            cfg,
            prepared,
            "fluid",
            "physics",
            session=tracking,
            resume=physics_start,
            cancelled=stopped,
        )
        structure = train_branch(
            cfg,
            prepared,
            "structure",
            "supervised",
            session=tracking,
            resume=lookup("structure_supervised"),
            cancelled=stopped,
        )
    result = publish_checkpoints(
        cfg,
        prepared,
        {"supervised": supervised, "physics": physics, "structure": structure},
        session.output_dir("train") / "checkpoints.json",
    )
    session.record_asset(
        "checkpoints",
        result,
        kind="checkpoint",
        stage="train",
        dependencies=[supervised["checkpoint"], physics["checkpoint"], structure["checkpoint"]],
    )
    session.report(
        {
            "checkpoints": result,
            "resume": str(session.output_dir("train") / "resume.json"),
            "updates": cfg["train"]["updates"],
        },
        stage="train",
    )
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
