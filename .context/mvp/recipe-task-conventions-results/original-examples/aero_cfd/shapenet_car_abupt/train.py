"""训练：消费准备，构建模型、目标、优化和评价，再执行。"""

import sys

sys.dont_write_bytecode = True
from functools import partial

from configuration import application_parameters, load_components, load_configuration
from trainprep import trainprep

from ai4e_core import run
from ai4e_core.applications.aero_cfd.train import physical as fitting
from ai4e_core.run import TrainingRun


def train(cfg, prepared=None):
    """缺少准备引用时显式调用同一准备阶段，不隐藏另一套准备链。"""
    components = load_components(cfg)
    session = TrainingRun()
    config = application_parameters(cfg)
    reference = prepared or cfg.train.get("preparation")
    if reference and isinstance(reference, dict) and reference.get("mode", "").endswith("_check"):
        result = {"mode": "train_check", "deferred": True, "reason": "准备检查未发布产物"}
        session.report(result)
        return result
    if not session.dry_run and reference is None:
        reference = run.stage("trainprep", trainprep, cfg)
    job = fitting.open_training(
        config,
        reference=reference,
        dataset_component=components.dataset,
        model_component=components.model,
        session=session,
    )
    if session.dry_run:
        return fitting.check_report(job)
    job = fitting.build_model(job, settings=cfg.model)
    job = fitting.configure_objectives(job, settings=cfg.model.get("supervision"))
    job = fitting.configure_optimization(job, settings=cfg.train)
    job = fitting.configure_evaluation(job, settings=cfg.train)
    job = fitting.configure_resume(job, checkpoint=cfg.train.get("resume"))
    if cfg.post.get("snapshot_every", 0):
        job = fitting.configure_callbacks(job, callbacks=(partial(observe_epoch, cfg=cfg),))
    return fitting.execute_training(job)


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
    return run.stage("post", analyze_sample, snapshot, cfg=cfg, output=cfg.paths.datasets.post)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
