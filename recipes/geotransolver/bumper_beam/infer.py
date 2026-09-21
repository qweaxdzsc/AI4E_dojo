"""固定权重批量预测、物理反变换、拓扑及派生结果交付。"""

from functools import partial

import torch
from configuration import component, validate

from ai4e_contrib.application.geotransolver import build_model
from ai4e_contrib.application.spatiotemporal_pde.geotransolver import binding
from ai4e_core import run
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
from ai4e_core.abilities.inference.prediction import named_array_batch
from ai4e_core.abilities.modeling.weights import load_mapped_weights
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs
from ai4e_core.applications.spatiotemporal_pde.infer import predict_named_trajectories
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, trained=None):
    """末批不丢弃，保存固定预测供独立 post 消费。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(
        prepared, cfg["inputs"]["infer"]["preparation"], name="infer.preparation"
    )
    checkpoint = resolve_input(
        trained["checkpoint"] if trained else None,
        cfg["inputs"]["infer"]["checkpoint"],
        name="infer.checkpoint",
    )
    record, arrays = read_field_inputs(prepared, binding.EVALUATION)
    model = build_model(cfg["model"]).to(resolve_device(cfg["infer"]["device"]))
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if (
        state["contract"]["model"] != cfg["model"]
        or state["contract"]["metadata"]["statistics"] != record["metadata"]["statistics"]
    ):
        raise ValueError("固定权重结构或归一化身份不匹配")
    load_mapped_weights(model, state["model"])
    if cfg["model"].get("include_local_features", False):
        install_prepared_queries(
            model,
            arrays,
            radii=cfg["model"]["radii"],
            neighbors=cfg["model"]["neighbors_in_radius"],
            cache_spec={
                "radii": record["metadata"]["declaration"]["model"]["radii"],
                "neighbors": record["metadata"]["declaration"]["model"]["neighbors_in_radius"],
            },
        )
    batch = partial(
        named_array_batch,
        arrays,
        device=resolve_device(cfg["infer"]["device"]),
        names=binding.INPUT_NAMES,
    )
    result = predict_named_trajectories(
        model,
        prepared,
        session.output_dir("infer") / "fixed",
        split=binding.EVALUATION,
        batch=batch,
        input_names=binding.INPUT_NAMES,
        decode=binding.decoder(record["metadata"]["statistics"], physical=True),
        batch_size=cfg["infer"]["batch_size"],
        fields=binding.FIELDS,
        units=binding.UNITS,
        times=binding.TIMES,
        provenance={"updates": state["updates"], "model": cfg["model"]},
        derived=component(cfg["components"]["derived"]),
    )
    record_bundle(session, "prediction", result, kind="other", stage="infer")
    session.report({"results": result}, stage="infer")
    return result


if __name__ == "__main__":
    from configuration import load_configuration

    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
