"""验收专用比较门禁；缺少证据时不得把数值差异解释为模型性能。"""

import json
from pathlib import Path

MODES = ("contract", "inference", "training")


def read_protocol(path):
    """历史产物无协议时保留未知，不从目录名或时间戳推断。"""
    if path is None or not Path(path).is_file():
        return None
    return json.loads(Path(path).read_text())


def assess(actual, reference, mode):
    """按比较目的检查共同条件；不同软件来源单独展示，绝不隐去。"""
    if mode not in MODES:
        raise ValueError(f"未知比较目的: {mode}")
    result = {"mode": mode, "status": "contract_only", "reasons": [], "provenance_differences": {}}
    if mode == "contract":
        return result
    if actual is None or reference is None:
        result.update(status="not_comparable", reasons=["缺少比较协议：只能核验已有产物契约"])
        return result
    if actual.get("version") != 1 or reference.get("version") != 1:
        result["reasons"].append("比较协议版本缺失或不受支持")
    required = ["dataset", "partitions", "normalization", "layout", "model", "sampling", "bindings"]
    if mode == "training":
        required += ["initialization", "training"]
    else:
        required += ["weights", "inputs", "inference"]
    for key in required:
        if actual.get(key) is None or reference.get(key) is None:
            result["reasons"].append(f"缺少证据: {key}")
        elif actual[key] != reference[key]:
            result["reasons"].append(f"对照条件不一致: {key}")
    if mode == "inference" and not any((actual.get("inputs") or {}).values()):
        result["reasons"].append("缺少实际几何、锚点与查询输入证据")
    for key in ("execution", "source"):
        for side, record in (("actual", actual), ("reference", reference)):
            if not record.get(key) or any(
                value in (None, "unknown", "") for value in record[key].values()
            ):
                result["reasons"].append(f"缺少来源证据: {side}.{key}")
        if actual.get(key) != reference.get(key):
            result["provenance_differences"][key] = {
                "actual": actual.get(key),
                "reference": reference.get(key),
            }
    for side, record in (("actual", actual), ("reference", reference)):
        for key in ("device", "precision", "torch", "python", "entrypoint", "constructor"):
            if not record.get("execution", {}).get(key):
                result["reasons"].append(f"缺少执行证据: {side}.{key}")
    for key in ("device", "precision", "torch"):
        if actual.get("execution", {}).get(key) != reference.get("execution", {}).get(key):
            result["reasons"].append(f"执行条件不一致: {key}；应作为独立实验报告")
    result["status"] = "not_comparable" if result["reasons"] else "comparable"
    return result
