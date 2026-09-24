"""外流应用的任务输入、输出与管理操作声明。"""


def describe_task(config: dict) -> dict:
    """输入需求由实际领域步骤声明，Task 仅做标签等值匹配。"""
    preparation = {
        "kind": "preparation",
        "semantics": {"type": "aero.preparation", "format_version": 2},
    }
    checkpoint = {"kind": "checkpoint", "semantics": {"type": "aero.checkpoint"}}
    inputs = {
        "inputs.rawprep.source": {"kind": "dataset", "semantics": {"type": "aero.source"}},
        "inputs.trainprep.dataset": {
            "kind": "dataset",
            "semantics": {"type": "aero.physical", "format_version": 1},
            "provided_by": "rawprep",
        },
        "inputs.trainprep.statistics": {"kind": "other", "semantics": {"type": "aero.statistics"}},
        "inputs.train.preparation": {**preparation, "provided_by": "trainprep"},
        "inputs.train.resume": {**checkpoint, "statuses": ["succeeded", "failed", "stopped"]},
        "inputs.infer.preparation": {**preparation, "provided_by": "trainprep"},
        "inputs.infer.checkpoint": {**checkpoint, "provided_by": "train"},
        "inputs.post.results": {
            "kind": "other",
            "semantics": {"type": "aero.inference"},
            "provided_by": "infer",
        },
    }
    return {
        "schema_version": 1,
        "stages": ["rawprep", "trainprep", "model", "train", "infer", "post"],
        "inputs": inputs,
        "resume_inputs": ["inputs.train.resume"],
        "shared_outputs": {
            "physical_dataset": {
                "kind": "dataset",
                "stage": "rawprep",
                "name_key": "dataset.processed_name",
                "manifest": "manifest.json",
                "consumer_binding": "inputs.trainprep.dataset",
                "semantics": {"type": "aero.physical", "format_version": 1},
            }
        }
        if "processed_name" in config.get("dataset", {})
        else {},
        "operations": ["inspect", "infer", "evaluate", "export"],
        "resources": {
            "device": next(
                (
                    config.get(stage, {}).get("device", "auto")
                    for stage in config.get("pipeline", {}).get("stages", [])
                    if stage in {"train", "infer"}
                ),
                None,
            )
        },
    }
