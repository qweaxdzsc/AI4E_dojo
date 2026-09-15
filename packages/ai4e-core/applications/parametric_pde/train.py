"""参数化 PDE 的训练装配；复用现有训练循环及检查点。"""

from copy import deepcopy

import torch

from ai4e_core.abilities.training.loop import fit

from .contracts import load_component, open_preparation, read_prepared, source_identity
from .model import build_model


def training_contract(cfg, preparation, model_component):
    """冻结训练目标和更新协议；延长轮次/更换运行目录不改变恢复条件。"""
    user = cfg["train"].get("step")
    return {
        "preparation": preparation["content_id"],
        "model": cfg["model"],
        "model_source": source_identity(model_component),
        "user_step": source_identity(load_component(user)) if user else None,
        "training": {
            k: cfg["train"][k]
            for k in (
                "seed",
                "precision",
                "learning_rate",
                "betas",
                "weight_decay",
                "gradient_clip",
                "update_group",
            )
        },
    }


def train(cfg, *, dataset_component, model_component, session):
    """消费冻结准备并拟合；用户 step 接收 model 和已准备的单实例 batch。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])
    path, prepared = open_preparation(cfg, dataset, model_component)
    records = [r for r in prepared["samples"] if r["split"] == "train"]
    if session.dry_run or not cfg["train"]["execute"]:
        session.report({"status": "checked", "train_samples": len(records)}, stage="train")
        return None
    model = build_model(cfg, model_component)
    settings = cfg["train"]
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=settings["learning_rate"],
        betas=tuple(settings["betas"]),
        weight_decay=settings["weight_decay"],
    )
    contract = training_contract(cfg, prepared, model_component)
    internal = deepcopy(settings)
    internal.update(
        accumulate=1,
        accumulation_reduction="sum",
        evaluation_enabled=settings["evaluation"]["enabled"],
        validation_interval=settings["evaluation"]["interval"],
    )
    custom = load_component(settings["step"]) if settings.get("step") else None

    def batches(epoch):
        if settings["update_group"] == "epoch_sum":
            yield [read_prepared(path, record) for record in records]
        else:
            for record in records:
                yield read_prepared(path, record)

    def step(network, batch):
        def calculate(item):
            return custom(network, item) if custom else model_component.step(network, item, cfg)

        if settings["update_group"] != "epoch_sum":
            return calculate(batch)
        # 原整轮逻辑目标先顺序相加，再一次backward，避免逐实例反传改变舍入顺序。
        loss = 0.0
        terms = {}
        for item in batch:
            result = calculate(item)
            loss = loss + result["loss"]
            for name, value in result.get("losses", {}).items():
                terms[name] = terms.get(name, 0.0) + value.detach()
        return {"loss": loss, "losses": terms}

    def evaluate():
        values = []
        previous = model.training
        model.eval()
        try:
            with torch.no_grad():
                for record in prepared["samples"]:
                    if record["split"] != "test":
                        continue
                    batch = read_prepared(path, record)
                    prediction = model_component.predictions(model, batch, cfg)["u"]
                    truth = batch["sample"]["u"].to(prediction)
                    if not truth.norm():
                        raise ValueError("零真值不适用泛化相对误差")
                    error = prediction - truth
                    values.append(
                        (
                            float(error.square().mean()),
                            float(error.norm() / truth.norm()),
                            float(error.abs().max()),
                        )
                    )
        finally:
            model.train(previous)
        if not values:
            raise ValueError("泛化评价没有测试实例")
        return {
            "loss": sum(v[0] for v in values) / len(values),
            "relative_l2": sum(v[1] for v in values) / len(values),
            "max_absolute_error": max(v[2] for v in values),
            "samples": len(values),
        }

    result = fit(
        model, optimizer, batches, step, evaluate, session, config=internal, contract=contract
    )
    session.artifact(
        "training-protocol.json",
        {
            "contract": contract,
            "updates_per_epoch": 1 if settings["update_group"] == "epoch_sum" else len(records),
            "reported_epoch_loss": "sum_of_instance_losses"
            if settings["update_group"] == "epoch_sum"
            else "mean_of_instance_losses",
            "max_epochs": settings["max_epochs"],
        },
    )
    session.report(
        {"status": "complete", "max_epochs": settings["max_epochs"], "train_samples": len(records)},
        stage="train",
    )
    return result
