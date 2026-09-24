"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from pathlib import Path

from configuration import component, load_configuration, plain

from ai4e_contrib.application.pde_control.safediffcon.handoff import (
    register_checkpoint,
    resolve_splits,
)
from ai4e_contrib.application.pde_control.safediffcon.inference import adapt, generate, inputs
from ai4e_contrib.application.pde_control.safediffcon.solver import solve
from ai4e_core import run
from ai4e_core.applications.pde_control.infer import save_results
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, checkpoint=None):
    """显式适配、生成控制、求解响应、评价和保存。"""
    cfg = plain(cfg, stage="infer")
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_splits(prepared, cfg["data"]["prepared"], name="infer")
    checkpoint = resolve_input(checkpoint, cfg["infer"]["checkpoint"], name="infer.checkpoint")
    if not prepared or not checkpoint:
        raise ValueError("infer 缺少准备或后训练权重")
    values = inputs(cfg, prepared)
    guide = component(cfg["components"]["guide"])
    model, effective, q = adapt(
        cfg,
        prepared,
        checkpoint,
        values,
        construct=component(cfg["components"]["model"]),
        guide=guide,
        session=session,
    )
    controls, prediction = generate(cfg, model, values, q=q, guide=guide)
    target = values["target"].cpu().numpy()
    response = solve(target, controls, case=cfg["case"], settings=cfg["solver"])
    evaluate = component(cfg["components"]["metrics"])
    metrics = evaluate(response, target, case=cfg["case"], paper_target=values["paper_target"])
    derive = component(cfg["components"]["derived"])
    derived = derive(response, case=cfg["case"]) if derive else None
    output = session.output_dir("infer") / "results"
    value = save_results(
        output,
        case=cfg["case"],
        ids=values["ids"],
        target=target,
        paper_target=values["paper_target"],
        controls=controls,
        prediction=prediction,
        response=response,
        checkpoint=effective,
        q=q,
        metrics=metrics,
        derived=derived,
    )
    session.record_asset(
        "results",
        value,
        kind="other", semantics={"type": "control.results"},
        stage="infer",
        dependencies=[Path(value).parent],
        bundle_root=Path(value).parent,
    )
    register_checkpoint(
        session,
        effective,
        stage="infer",
        phase="adapt" if cfg["infer"]["adaptation_updates"] else "posttrain_1",
    )
    session.report(
        {"results": value, "metrics": metrics, "effective_checkpoint": effective, "q": q},
        stage="infer",
    )
    return value


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
