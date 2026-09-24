"""控制轨迹的训练、校准、测试及后训练权重需求。"""


def describe_task(config: dict) -> dict:
    """公开控制流程管理描述，不在 Task 增加控制算法分支。"""
    inputs = {"inputs.rawprep.source": {"kind": "dataset", "semantics": {"type": "control.source"}}}
    for split in ("train", "cal", "test"):
        inputs[f"inputs.trainprep.dataset_{split}"] = {
            "kind": "dataset",
            "semantics": {"type": "control.trajectory", "split": split},
            "provided_by": "rawprep",
        }
        for stage in ("train", "posttrain", "infer"):
            inputs[f"inputs.{stage}.preparation_{split}"] = {
                "kind": "preparation",
                "semantics": {"type": "control.preparation", "split": split},
                "provided_by": "trainprep",
            }
    for stage, phase, producer in (
        ("train", "pretrain", None),
        ("posttrain", "pretrain", "train"),
        ("infer", "posttrain_1", "posttrain"),
    ):
        name = "resume" if stage == "train" else "checkpoint"
        inputs[f"inputs.{stage}.{name}"] = {
            "kind": "checkpoint",
            "semantics": {"type": "control.checkpoint", "phase": phase},
            **(
                {"provided_by": producer}
                if producer
                else {"statuses": ["succeeded", "failed", "stopped"]}
            ),
        }
    inputs["inputs.infer.solver_assets"] = {"kind": "other"}
    inputs["inputs.post.results"] = {
        "kind": "other",
        "semantics": {"type": "control.results"},
        "provided_by": "infer",
    }
    return {
        "schema_version": 1,
        "stages": ["rawprep", "trainprep", "train", "posttrain", "infer", "post"],
        "inputs": inputs,
        "resume_inputs": ["inputs.train.resume"],
        "shared_outputs": {},
        "operations": ["inspect"],
    }
