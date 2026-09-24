"""冻结权重推理与物理预测交付；全窗口延迟包含正反变换与传输。"""

import torch
from configuration import component
from local_data import read_record
from local_evaluation import Predictor, Validation, latency

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.modeling.construction import construct
from ai4e_core.abilities.modeling.weights import load_mapped_weights
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.run import TrainingRun


def infer(cfg, prepared=None, trained=None):
    """只读取指定检查点，不查找最新权重或重训。"""
    session = TrainingRun()
    path = resolve_input(prepared, cfg["inputs"]["infer"]["preparation"], name="infer.preparation")
    data = read_record(path)
    checkpoint = resolve_input(
        trained["checkpoint"] if trained else None,
        cfg["inputs"]["infer"]["checkpoint"],
        name="infer.checkpoint",
    )
    model, _ = construct(component(cfg["components"]["model"]), cfg["model"])
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    load_mapped_weights(model, state.get("model", state))
    model.to(cfg["infer"]["device"])
    advance = component(cfg["components"]["advance"])
    validation = Validation(data["validation"], data["statistics"], advance, cfg["infer"]["device"])
    output = session.output_dir("infer")
    result = validation.evaluate(model, output=output / "predictions")
    result["latency"] = latency(
        Predictor(model, data["statistics"], advance, cfg["infer"]["device"]),
        validation,
        cfg["infer"]["device"],
    )
    result["checkpoint"] = checkpoint
    summary = output / "evaluation.json"
    save_json(summary, result)
    session.record_asset(
        "predictions",
        result["arrays"],
        kind="other",
        stage="infer",
        dependencies=[checkpoint, path],
    )
    session.report(result, stage="infer")
    return str(summary)
