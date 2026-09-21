"""分别构造、训练两个分支，再发布明确的双分支检查点组合。"""

from pathlib import Path

from configuration import component, load_configuration, validate

from ai4e_contrib.application.geothermal.pcno.inference import publish_checkpoints
from ai4e_contrib.application.geothermal.pcno.training import train_branch
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
    construct = component(cfg["components"]["network"])
    objective = component(cfg["components"]["objective"])
    with cancellation() as stopped:
        pressure = train_branch(
            cfg,
            prepared,
            "pres",
            construct=construct,
            objective=objective,
            session=session,
            resume=cfg["inputs"]["train"]["pres_resume"],
            cancelled=stopped,
        )
        temperature = train_branch(
            cfg,
            prepared,
            "temp",
            construct=construct,
            objective=objective,
            session=session,
            resume=cfg["inputs"]["train"]["temp_resume"],
            cancelled=stopped,
        )
    checkpoints = publish_checkpoints(pressure, temperature, session.output_dir("train"))
    root = Path(checkpoints).parent
    session.record_asset(
        "paired_checkpoints",
        checkpoints,
        kind="checkpoint",
        stage="train",
        dependencies=[root / "pres.pt", root / "temp.pt"],
        bundle_root=root,
    )
    session.report(
        {
            "checkpoints": checkpoints,
            "pressure_updates": pressure["updates"],
            "temperature_updates": temperature["updates"],
            "schedule_epochs": 250,
        },
        stage="train",
    )
    return checkpoints


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
