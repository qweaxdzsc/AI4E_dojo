"""推理传输边界；工作路径和模型配置不进入浏览器批次。"""


def checkpoint(value: dict) -> dict:
    """只交付可选择身份和兼容信息。"""
    result = {
        key: value[key]
        for key in (
            "id",
            "run_id",
            "name",
            "revision",
            "epoch",
            "updates",
            "size",
            "status",
            "created_at",
            "compatibility",
            "aliases",
            "evaluation",
        )
        if key in value
    }
    if value.get("preparation"):
        result["preparation"] = {
            key: value["preparation"].get(key) for key in ("digest", "revision")
        }
    return result


def batch(value: dict) -> dict:
    """去除固定权重路径，进度只保留计数与运行状态。"""
    result = {k: v for k, v in value.items() if k not in {"children", "inherited_children"}}
    result["children"] = []
    for child in value.get("children", []):
        item = {
            k: child[k]
            for k in ("run_id", "status", "error", "execution_mode", "split", "samples")
            if k in child
        }
        item["checkpoint"] = checkpoint(child.get("checkpoint", {}))
        progress = child.get("progress", {})
        item["progress"] = {
            k: progress[k]
            for k in ("completed", "total", "status", "operation", "sample")
            if k in progress
        }
        item["progress"]["operations"] = {
            name: {k: op[k] for k in ("status", "completed", "expected", "error") if k in op}
            for name, op in progress.get("operations", {}).items()
        }
        result["children"].append(item)
    result["inherited_children"] = (
        [
            {**child, "inherited": True}
            for child in batch({"children": value.get("inherited_children", [])})["children"]
        ]
        if value.get("inherited_children")
        else []
    )
    return result
