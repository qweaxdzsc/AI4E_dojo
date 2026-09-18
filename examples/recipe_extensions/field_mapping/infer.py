"""独立推理：显式登记恢复、预测、物理输出、评价与结果交付。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.infer import anchor as infer_stage
from ai4e_core.run import TrainingRun


def infer(cfg, trained=None):
    """连续运行消费训练引用，独立运行消费指定检查点。"""
    components = load_components(cfg)
    session = TrainingRun()
    if trained and trained.get("mode", "").endswith("_check"):
        result = {"mode": "infer_check", "deferred": True, "reason": "训练检查未交付检查点"}
        session.report(result, stage="infer")
        return result
    job = infer_stage.open_inference(
        application_parameters(cfg, session=run.TrainingRun()),
        trained=trained,
        dataset_component=components.dataset,
        model_component=components.model,
        session=session,
    )
    job = infer_stage.configure_restore(job, settings=cfg.model)
    job = infer_stage.configure_prediction(job, settings=cfg.infer)
    job = infer_stage.configure_physical_output(job)
    job = infer_stage.configure_selection(job, fields=cfg.infer.get("fields"))
    job = infer_stage.configure_evaluation(job, settings=cfg.infer)
    job = infer_stage.configure_save(job, output=session.output_dir("infer") / "predictions", settings=cfg.infer)
    job = infer_stage.configure_mesh_export(job, settings=cfg.infer)
    if session.dry_run:
        return infer_stage.check_report(job)
    return infer_stage.execute(job)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
