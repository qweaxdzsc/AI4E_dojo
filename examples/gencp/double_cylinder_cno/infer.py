"""显式绑定各场速度与耦合更新，生成固定物理结果。"""

from functools import partial

import torch
from configuration import component, load_configuration, plain

from ai4e_contrib.ability.inference.gencp.velocity import fsi_synchronous_step
from ai4e_contrib.ability.transform.gencp.boundaries import neutron_inpainting
from ai4e_contrib.application.coupled_physics.gencp.cases import (
    bind_velocity,
    inference_inputs,
    physical_predictions,
)
from ai4e_core import run
from ai4e_core.abilities.inference.coupled_steps import (
    sequential_euler_step,
)
from ai4e_core.abilities.inference.randomness import seeded_randomness
from ai4e_core.applications.coupled_physics.contracts import component_identity
from ai4e_core.applications.coupled_physics.infer import (
    bind_field,
    configure_integration,
    execute_prediction,
    save_results,
)
from ai4e_core.applications.coupled_physics.model import load_checkpoint_group
from ai4e_core.applications.coupled_physics.trainprep import open_preparation
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, checkpoints=None):
    """独立入口固定准备与权重，不选择目录中最新模型。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(prepared, cfg["inputs"]["infer"]["preparation"], name="infer.preparation")
    checkpoints = resolve_input(checkpoints, cfg["inputs"]["infer"]["checkpoint"], name="infer.checkpoint")
    if not prepared or not checkpoints:
        raise ValueError("infer 需要明确准备和权重组")
    preparation = open_preparation(prepared)
    models, weights = load_checkpoint_group(
        checkpoints,
        system_id=preparation["content_id"],
        construct=component(cfg["components"]["model"]),
        device=cfg["infer"]["device"],
    )
    with seeded_randomness(cfg["infer"]["seed"]):
        job, context, targets = inference_inputs(
            preparation,
            models,
            device=cfg["infer"]["device"],
            flow_steps=cfg["infer"]["flow_steps"],
        )

        def velocity(field):
            condition = (
                component(cfg["components"][field + "_condition"])
                if cfg["dataset"]["name"] == "ntcouple"
                else None
            )
            return bind_velocity(
                models[field],
                dataset=cfg["dataset"]["name"],
                field=field,
                context=context,
                condition=condition,
            )

        if cfg["dataset"]["name"] == "ntcouple":
            job = bind_field(job, "neutron", velocity=velocity("neutron"))
            job = bind_field(job, "solid", velocity=velocity("solid"))
            job = bind_field(job, "fluid", velocity=velocity("fluid"))
            boundary = None
            if cfg["infer"]["boundary"] == "neutron_inpainting":
                clean = context["boundary"]["neutron"]
                boundary = partial(neutron_inpainting, noise=torch.randn_like(clean), clean=clean)
            elif cfg["infer"]["boundary"] != "none":
                raise ValueError("未知边界策略")
            job = configure_integration(
                job,
                step=sequential_euler_step,
                order=("neutron", "solid", "fluid"),
                boundary=boundary,
            )
        else:
            job = bind_field(job, "fluid", velocity=velocity("fluid"))
            job = bind_field(job, "structure", velocity=velocity("structure"))
            job = configure_integration(
                job, step=fsi_synchronous_step, order=("fluid", "structure")
            )
        predicted = execute_prediction(job)
    physical = physical_predictions(predicted, preparation)
    output = session.output_dir("infer") / "results"
    reference = save_results(
        physical,
        targets,
        output,
        metadata={
            **job.metadata,
            "weights": weights["content_id"],
            "model_sources": {
                name: component_identity(type(model)) for name, model in models.items()
            },
            "seed": cfg["infer"]["seed"],
            "flow_steps": cfg["infer"]["flow_steps"],
            "components": {
                name: component_identity(component(path))
                for name, path in cfg["components"].items()
            },
            "update": component_identity(job.step),
            "boundary": cfg["infer"]["boundary"],
            "boundary_source": "reference_neutron_and_solid_left"
            if cfg["dataset"]["name"] == "ntcouple"
            else "history",
        },
    )
    session.record_asset("results", reference, kind="other", stage="infer", dependencies=[output])
    session.report({"results": reference}, stage="infer")
    return reference


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
