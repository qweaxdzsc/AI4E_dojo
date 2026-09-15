"""后处理消费固定推理结果；显式历史模式保留旧数值对照入口。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.post import stage as post_stage
from ai4e_core.run.training import TrainingRun


def post(cfg, trained=None):
    """连续或独立运行都消费固定结果；历史预测必须显式选择兼容模式。"""
    from ai4e_core.applications.aero_cfd.infer import open_results

    post_reference = cfg.post.get("results")
    infer_reference = (cfg.get("infer") or {}).get("results")
    if post_reference and infer_reference and post_reference != infer_reference:
        raise ValueError("post.results 与 infer.results 不能指向不同结果")
    reference = post_reference or infer_reference
    if isinstance(trained, dict) and "protocol" in trained and "results" in trained:
        reference = trained
    if reference is not None:
        return open_results(reference, session=TrainingRun())
    if "infer" in cfg.pipeline.stages or not cfg.post.get("legacy_predict", False):
        raise ValueError("后处理需要固定推理结果，不能重新运行模型")
    components = load_components(cfg)
    session = TrainingRun()
    if trained and trained.get("mode", "").endswith("_check"):
        result = {"mode": "post_check", "deferred": True, "reason": "训练检查未交付检查点"}
        session.report(result, stage="post")
        return result
    job = post_stage.open_post(
        application_parameters(cfg),
        trained=trained,
        dataset_component=components.dataset,
        model_component=components.model,
        session=session,
    )
    job = post_stage.configure_restore(job, settings=cfg.model)
    job = post_stage.configure_prediction(job, settings=cfg.post)
    job = post_stage.configure_physical_output(job)
    job = post_stage.configure_evaluation(job, settings=cfg.post)
    job = post_stage.configure_save(job, output=cfg.paths.datasets.predictions, settings=cfg.post)
    job = post_stage.configure_mesh_export(job, settings=cfg.post)
    if session.dry_run:
        return post_stage.check_report(job)
    return post_stage.execute(job)


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
