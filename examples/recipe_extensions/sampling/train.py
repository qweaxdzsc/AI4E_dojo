"""训练：消费准备，构建模型、目标、优化和评价，再执行。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration
from trainprep import trainprep

from ai4e_core import run
from ai4e_core.applications.aero_cfd.train import fitting
from ai4e_core.run import TrainingRun


def train(cfg, prepared=None):
    """缺少准备引用时显式调用同一准备阶段，不隐藏另一套准备链。"""
    components = load_components(cfg)
    session = TrainingRun()
    config = application_parameters(cfg, session=run.TrainingRun())
    reference = prepared if prepared is not None else cfg.inputs.train.get("preparation")
    if session.dry_run or cfg.train.get("mode", "fit") in {"probe", "prepare"}:
        return fitting.check_or_prepare(
            config,
            reference=reference,
            model_component=components.model,
            prepare_stage=trainprep,
            session=session,
            public_config=cfg,
        )
    if reference is None:
        raise ValueError("train 需要显式 inputs.train.preparation；请先执行 trainprep")
    job = fitting.open_training(
        config,
        session,
        reference=reference,
        factory=components.model.construct,
        predict=components.model.predict,
        prepare=components.model.prepare_inputs,
        collate=components.model.collate,
        source=components.model.SOURCE,
    )
    job = fitting.build_model(job, settings=config["model"])
    job = fitting.configure_objectives(job, settings=cfg.model.get("supervision"))
    job = fitting.configure_optimization(job, settings=cfg.train)
    job = fitting.configure_evaluation(job, settings=cfg.train)
    job = fitting.configure_resume(job, checkpoint=cfg.inputs.train.get("resume"))
    return fitting.execute_training(job)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
