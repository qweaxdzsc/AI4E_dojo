"""后处理：显式登记恢复、预测、物理输出、评价与交付。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.post import stage as post_stage
from ai4e_core.run.training import TrainingRun


def post(cfg, trained=None):
    """连续运行消费训练引用，独立运行消费指定检查点。"""
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
