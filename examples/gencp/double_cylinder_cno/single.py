"""固定场权重和已知条件的单场生成；输出与耦合生成分开保存。"""


from configuration import component, load_configuration, plain

from ai4e_contrib.application.coupled_physics.gencp.validation import (
    generate_single,
    validation_batch,
)
from ai4e_core import run
from ai4e_core.applications.coupled_physics.infer import save_results
from ai4e_core.applications.coupled_physics.model import load_checkpoint_group
from ai4e_core.applications.coupled_physics.trainprep import open_preparation
from ai4e_core.base.config.conventions import resolve_input


def single(cfg, prepared=None, checkpoints=None):
    """按明确权重组逐场验证，固定归一化预测供独立对照。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    preparation = open_preparation(resolve_input(prepared, cfg["inputs"]["single"]["preparation"], name="single.preparation"))
    models, weights = load_checkpoint_group(
        resolve_input(checkpoints, cfg["inputs"]["single"]["checkpoint"], name="single.checkpoint"),
        system_id=preparation["content_id"],
        construct=component(cfg["components"]["model"]),
        device=cfg["infer"]["device"],
    )
    predictions, targets = {}, {}
    for field in cfg["fields"]:
        batch = validation_batch(preparation, field, cfg["infer"]["device"])
        predictions[field] = generate_single(
            models[field],
            batch,
            dataset=cfg["dataset"]["name"],
            field=field,
            settings={**cfg["train"], **cfg["fields"][field]},
            seed=cfg["infer"]["seed"],
        )
        targets[field] = batch["target"]
    output = session.output_dir("single") / "results"
    path = save_results(
        predictions,
        targets,
        output,
        metadata={
            "dataset": cfg["dataset"]["name"],
            "space": "normalized",
            "scope": "single_field_known_conditions",
            "system_id": preparation["content_id"],
            "weights": weights["content_id"],
        },
    )
    session.record_asset("results", path, kind="other", stage="single", dependencies=[output])
    session.report({"single_results": path}, stage="single")
    return path


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"single": single}, script=__file__, only=["single"], config_loader=load_configuration
        )
    )
