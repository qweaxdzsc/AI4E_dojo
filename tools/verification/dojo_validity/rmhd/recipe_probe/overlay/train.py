"""公开组件装配；训练迭代与完整状态保存交给 Dojo，不在 recipe 写循环。"""

import random
from pathlib import Path

import numpy as np
import torch
from configuration import component
from local_data import read_record
from local_evaluation import Validation

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, source_fingerprint
from ai4e_core.abilities.modeling.construction import construct
from ai4e_core.abilities.modeling.weights import initialize_weights
from ai4e_core.abilities.training.diagnostics import parameter_count
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.applications.base.iteration_training import train_model
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.run import TrainingRun


def train(cfg, prepared=None):
    """从显式准备和组件声明装配，恢复目标为累计更新数。"""
    session = TrainingRun()
    preparation = resolve_input(
        prepared, cfg["inputs"]["train"]["preparation"], name="train.preparation"
    )
    data = read_record(preparation)
    settings = cfg["train"]
    torch.set_num_threads(cfg["science"]["threads"])
    torch.manual_seed(settings["seed"])
    np.random.seed(settings["seed"])
    random.seed(settings["seed"])
    model, parameters = construct(component(cfg["components"]["model"]), cfg["model"])
    initialize_weights(model, path=cfg["inputs"]["train"]["initial"])
    model.to(settings["device"])
    optimizer = component(cfg["components"]["optimizer"])(
        model.parameters(), lr=settings["learning_rate"]
    )
    stream = component(cfg["components"]["stream"])(
        len(data["train"]), settings["batch_size"], seed=settings["seed"], mixed=settings["mixed"]
    )
    batch = component(cfg["components"]["batch"])(data["train"], settings["device"])
    objective = component(cfg["components"]["objective"])
    if settings["relative_objective"]:
        objective = objective(data["statistics"], settings["device"])
    validation = Validation(
        data["validation"],
        data["statistics"],
        component(cfg["components"]["advance"]),
        settings["device"],
    )
    ema = (
        MovingAverage(model, decay=settings["ema"], buffer_policy="copy")
        if settings["ema"]
        else None
    )
    contract = {
        "science": cfg["science"],
        "model": parameters,
        "components": cfg["components"],
        "training": {k: v for k, v in settings.items() if k not in ["updates", "evaluate_every"]},
        "preparation_sha256": file_fingerprint(preparation),
        "source_sha256": source_fingerprint(Path(__file__).parent),
        "initial_sha256": file_fingerprint(cfg["inputs"]["train"]["initial"]),
    }
    result = train_model(
        model,
        optimizer,
        stream,
        batch,
        objective,
        updates=settings["updates"],
        session=session,
        contract=contract,
        namespace="train",
        resume=cfg["inputs"]["train"]["resume"],
        max_grad_norm=None,
        ema=ema,
        evaluate=validation,
        evaluate_every=settings["evaluate_every"],
    )
    session.artifact("validation_curve.json", {"curve": validation.curve})
    session.report(
        {
            **result,
            "parameter_count": parameter_count(model),
            "epochs": stream.epoch,
            "preparation": preparation,
        },
        stage="train",
    )
    return {**result, "preparation": preparation}
