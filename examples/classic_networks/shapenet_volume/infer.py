"""恢复固定权重、预测、反变换及可替换派生数组保存。"""

from functools import partial

import torch
from configuration import component, load_configuration, validate

from ai4e_contrib.application.classic_networks.binding import batch, construct
from ai4e_contrib.application.classic_networks.prediction import predict_fields
from ai4e_contrib.application.classic_networks.preparation import original_samples, read_prepared
from ai4e_core import run
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, trained=None):
    """末批与完整窗口均不丢弃，固定结果不依赖原始来源。"""
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
    record, arrays = read_prepared(prepared, "test")
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if (
        state["contract"]["model"] != cfg["model"]
        or state["contract"]["metadata"]["statistics"] != record["metadata"]["statistics"]
    ):
        raise ValueError("权重结构或训练统计不相容")
    device = resolve_device(cfg["infer"]["device"])
    model = construct(cfg).to(device)
    model.load_state_dict(state["model"], strict=True)
    get_batch = partial(
        batch,
        arrays,
        device=device,
        case=cfg["dataset"]["case"],
        sample_points=None,
        point_sequence=cfg["model"]["family"] == "rnn",
    )
    results = predict_fields(
        model,
        arrays,
        record,
        get_batch,
        session.output_dir("infer") / "fixed",
        derived=component(cfg["components"]["derived"]),
        originals=(
            original_samples(prepared, "test", record["metadata"]["ids"])
            if cfg["dataset"]["case"] == "shapenet_volume"
            else None
        ),
    )
    record_bundle(session, "prediction", results, kind="other", stage="infer")
    session.report({"results": results, "updates": state["updates"]}, stage="infer")
    return results


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
