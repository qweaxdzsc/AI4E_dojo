"""核对准备及状态，再由显式重建函数预测、反变换和固定结果保存。"""

from configuration import component, fit_context, load_configuration, validate

from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared
from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.data.save.surrogate import read_state
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.base.config.conventions import resolve_input


def infer(cfg, prepared=None, trained=None):
    """在重建及计算前核对上下文；用户自定义状态由同一显式重建入口消费。"""
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
    record, _ = read_prepared(prepared, "test")
    state, context = read_state(checkpoint)
    if context != fit_context(cfg, prepared, record["metadata"]):
        raise ValueError("拟合状态与当前准备、字段、统计或组件声明不相容")
    model = component(cfg["components"]["rebuild"])(state)
    results = predict_prepared(
        state,
        prepared,
        session.output_dir("infer") / "fixed",
        batch_size=cfg["infer"]["batch_size"],
        predictor=model,
    )
    record_bundle(session, "prediction", results, kind="other", stage="infer")
    session.report({"results": results}, stage="infer")
    return results


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
