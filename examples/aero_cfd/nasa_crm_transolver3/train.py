"""训练：消费准备，构建模型、目标、优化和评价，再执行。"""

import sys

sys.dont_write_bytecode = True
from functools import partial

from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.run import TrainingRun


def train(cfg, prepared=None):
    """缺少准备引用时显式调用同一准备阶段，不隐藏另一套准备链。"""
    from ai4e_core.applications.aero_cfd.train import physical as fitting

    components = load_components(cfg)
    session = TrainingRun()
    config = application_parameters(cfg, session=run.TrainingRun())
    reference = prepared if prepared is not None else cfg.inputs.train.get("preparation")
    if reference is None:
        raise ValueError("train 需要显式 inputs.train.preparation；请先执行 trainprep")
    job = fitting.open_training(
        config,
        reference=reference,
        dataset_component=components.dataset,
        model_component=components.model,
        session=session,
    )
    if session.dry_run:
        return fitting.check_report(job)
    job = fitting.build_model(job, settings=config["model"])
    job = fitting.configure_objectives(job, settings=cfg.model.get("supervision"))
    job = fitting.configure_optimization(job, settings=cfg.train)
    job = fitting.configure_evaluation(job, settings=cfg.train)
    job = fitting.configure_resume(job, checkpoint=cfg.inputs.train.get("resume"))
    if cfg.post.get("snapshot_every", 0):
        job = fitting.configure_callbacks(job, callbacks=(partial(observe_epoch, cfg=cfg),))
    result = fitting.execute_training(job)
    if cfg.train.get("export_predictions") or cfg.train.get("export_vtk"):
        from ai4e_core.applications.aero_cfd.train.export import export_training_fields

        export_training_fields(
            application_parameters(cfg, session=session),
            trained=result,
            session=session,
            dataset_component=components.dataset,
            model_component=components.model,
            predictions=bool(cfg.train.get("export_predictions")),
            meshes=bool(cfg.train.get("export_vtk")),
            split=cfg.train.get("export_split", "test"),
            preparation=reference,
        )
    return result


def observe_epoch(context, *, cfg):
    """在指定轮次生成当前模型快照，再执行与独立推理相同的分析正文。"""
    from post import analyze_sample

    from ai4e_core.applications.aero_cfd.infer import predict_snapshot

    every = cfg.post.get("snapshot_every", 0)
    if every <= 0 or context.epoch % every:
        return None
    snapshot = predict_snapshot(
        context.model,
        prepared=context.prepared,
        model_component=context.component,
        dataset_component=context.dataset_component,
        sample=cfg.post.snapshot_sample,
        split=cfg.post.get("snapshot_split", "test"),
        origin=context.origin,
    )
    return run.stage(
        "post",
        analyze_sample,
        snapshot,
        cfg=cfg,
        output=TrainingRun().output_dir("post") / "analysis",
    )


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
