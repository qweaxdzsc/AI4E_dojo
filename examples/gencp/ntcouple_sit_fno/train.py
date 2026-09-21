"""各物理场独立训练，Python 正文明确表达场顺序与权重组交接。"""


from configuration import component, load_configuration, plain

from ai4e_contrib.application.coupled_physics.gencp.cases import dataset_adapter
from ai4e_contrib.application.coupled_physics.gencp.validation import (
    generate_single,
    selection_metric,
    validation_batch,
)
from ai4e_core import run
from ai4e_core.applications.coupled_physics.model import bind_checkpoint_group
from ai4e_core.applications.coupled_physics.train import train_field
from ai4e_core.applications.coupled_physics.trainprep import open_preparation
from ai4e_core.base.config.conventions import resolve_input


def resume_field(group, field):
    """从显式权重组取得各场完整恢复状态，不猜测最近权重。"""
    if group is None:
        return None
    from ai4e_core.applications.coupled_physics.contracts import file_digest, read_record
    record = read_record(group, "coupled_weights_v1")
    member = record["fields"][field]
    if file_digest(member["path"]) != member["sha256"]:
        raise ValueError("恢复权重组成员内容变化")
    return member["path"]


def fit_field(cfg, prepared, field):
    """场设置来自配置；能力来自可替换的公开导入路径。"""
    settings = {
        **cfg["train"],
        **cfg["fields"][field],
        "seed": cfg["seed"],
        "resume": resume_field(cfg["inputs"]["train"].get("resume"), field),
    }
    preparation = open_preparation(prepared)
    batch = validation_batch(preparation, field, settings["device"])

    def validate(model):
        prediction = generate_single(
            model, batch, dataset=cfg["dataset"]["name"], field=field, settings=settings
        )
        return selection_metric(
            prediction,
            batch["target"],
            field,
            dataset=cfg["dataset"]["name"],
            normalization=preparation["descriptions"][field + "/val"]["normalization"],
        )

    return train_field(
        settings,
        prepared,
        field=field,
        validate=validate,
        construct=component(cfg["components"]["model"]),
        reader=dataset_adapter(cfg["dataset"]["name"]).read_sample,
        objective=component(cfg["components"]["objective"]),
        session=run.TrainingRun(),
    )


def train(cfg, prepared=None):
    """只消费明确准备引用，不静默重做数据准备。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = resolve_input(prepared, cfg["inputs"]["train"]["preparation"], name="train.preparation")
    if not prepared:
        raise ValueError("train 需要先执行 trainprep 并绑定准备记录")
    if cfg["dataset"]["name"] == "ntcouple":
        neutron = run.stage("train", fit_field, cfg, prepared, "neutron")
        solid = run.stage("train", fit_field, cfg, prepared, "solid")
        fluid = run.stage("train", fit_field, cfg, prepared, "fluid")
        checkpoints = {"neutron": neutron, "solid": solid, "fluid": fluid}
    else:
        fluid = run.stage("train", fit_field, cfg, prepared, "fluid")
        structure = run.stage("train", fit_field, cfg, prepared, "structure")
        checkpoints = {"fluid": fluid, "structure": structure}
    # 新训练形成新组合，不覆盖以前的模型组。
    path = session.output_dir("train") / "weights.json"
    reference = bind_checkpoint_group(checkpoints, path, required_fields=tuple(cfg["fields"]))
    session.record_asset("weights", reference, kind="checkpoint", stage="train", dependencies=checkpoints.values())
    session.report({"checkpoints": reference}, stage="train")
    return reference


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
