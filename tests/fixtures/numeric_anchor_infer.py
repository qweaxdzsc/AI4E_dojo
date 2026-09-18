"""锚点数值回归入口；不通过已移除的 post 模型预测入口。"""

from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.infer import anchor_stage


def evaluate(cfg):
    """显式装配保留参考两次遍历的锚点算法，用于原数值断言。"""
    component = load_components(cfg).model
    config = application_parameters(cfg, session=run.TrainingRun())
    config["post"]["checkpoint"] = cfg.inputs.infer.get("checkpoint")
    config.pop("infer", None)
    return anchor_stage.run(
        config,
        run.TrainingRun(),
        construct=component.construct,
        predict=component.predict,
        prepare_inputs=component.prepare_inputs,
        collate=component.collate,
        context_factory=component.InferenceContext,
    )


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"post": evaluate}, script=__file__, only=["post"], config_loader=load_configuration
        )
    )
