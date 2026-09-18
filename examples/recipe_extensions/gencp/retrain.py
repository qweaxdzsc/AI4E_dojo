"""独立重训流体场，保留其他场权重后重新生成并分析。"""


from configuration import component, load_configuration, plain
from infer import infer
from post import post
from train import fit_field

from ai4e_core import run
from ai4e_core.applications.coupled_physics.model import (
    bind_checkpoint_group,
    load_checkpoint_group,
)
from ai4e_core.applications.coupled_physics.trainprep import open_preparation


def retrain(cfg):
    """复用固定准备和旧组，只更新 fluid；本脚本明确表达研究选择。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = cfg["inputs"]["train"]["preparation"]
    preparation = open_preparation(prepared)
    models, old = load_checkpoint_group(
        cfg["inputs"]["infer"]["checkpoint"],
        system_id=preparation["content_id"],
        construct=component(cfg["components"]["model"]),
        device="cpu",
    )
    del models
    fluid = run.stage("train", fit_field, cfg, prepared, "fluid")
    members = {name: value["path"] for name, value in old["fields"].items()}
    members["fluid"] = fluid
    destination = session.output_dir("retrain") / "weights.json"
    replacement = bind_checkpoint_group(members, destination, required_fields=tuple(old["fields"]))
    session.report(
        {
            "previous_group": old["content_id"],
            "checkpoints": replacement,
            "retrained_field": "fluid",
        },
        stage="retrain",
    )
    session.record_asset("weights", replacement, kind="checkpoint", stage="retrain", dependencies=members.values())
    cfg["inputs"]["infer"]["checkpoint"] = replacement
    results = run.stage("infer", infer, cfg, prepared, replacement)
    return run.stage("post", post, cfg, results)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"retrain": retrain},
            script=__file__,
            only=["retrain"],
            config_loader=load_configuration,
        )
    )
