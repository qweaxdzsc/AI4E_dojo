"""阶段规则：允许阶段、只读统计、输入选择与试跑门禁，不依赖 HTTP 或存储。"""

from dataclasses import dataclass, field

STAGES = {"rawprep", "trainprep", "model", "train", "post"}
ALLOWED_BINDINGS = {
    "train.manifest",
    "train.preparation",
    "post.checkpoint",
    "trainprep.normalization.statistics",
}


@dataclass
class OperationCommand:
    """固定修订和资产的业务操作命令。"""

    expected_revision: str
    mode: str
    inputs: list[dict] = field(default_factory=list)
    selection: dict = field(default_factory=dict)
    idempotency_key: str | None = None


def validate_stage(stage):
    """拒绝没有登记的阶段。"""
    if stage not in STAGES:
        raise ValueError("unknown_stage")


def reject_statistics(value, path=""):
    """定位并拒绝用户配置中手写的拟合统计量。"""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "mean",
                "std",
                "min",
                "max",
                "minimum",
                "maximum",
                "variance",
                "fitted_statistics",
            }:
                raise ValueError("readonly_statistics: " + path + key)
            reject_statistics(child, path + key + ".")
    elif isinstance(value, list):
        for child in value:
            reject_statistics(child, path)


def execution_stages(stage, mode, selection):
    """确定允许的已有阶段顺序，并校验试跑范围。"""
    validate_stage(stage)
    if mode not in {"trial", "execute"} or stage == "model":
        raise ValueError("unsupported_stage_operation")
    if mode == "trial" and not selection.get("samples"):
        raise ValueError("trial_samples_required")
    if "samples" in selection and not selection["samples"]:
        raise ValueError("empty_sample_selection")
    return (
        ["trainprep", "train"] if stage == "train" and selection.get("prepare_first") else [stage]
    )


def required_inputs(stage, stages):
    """阶段消费的上游业务产物。"""
    return (
        ["train.manifest"]
        if "trainprep" in stages
        else ["train.preparation"]
        if stage == "train"
        else ["train.preparation", "post.checkpoint"]
        if stage == "post"
        else []
    )


def selected_input_keys(stages, declared):
    """仅捕获当前执行链所需输入，未来阶段产物不提前索取。"""
    needed = set()
    if "rawprep" in stages:
        needed.update(key for key in declared if key.startswith("dataset."))
    if "trainprep" in stages:
        if "rawprep" not in stages:
            needed.add("train.manifest")
        needed.update(["trainprep.normalization.statistics", "dataset.partition"])
    if "train" in stages:
        needed.update(["train.resume", "model.initial_weights"])
        if "trainprep" not in stages:
            needed.add("train.preparation")
    if "post" in stages and "train" not in stages:
        needed.update(["train.preparation", "post.checkpoint"])
    return sorted(needed & set(declared))
