"""控制推理结果交付；采样与响应计算由 recipe 显式串联。"""

import numpy as np

from .contracts import digest, save_arrays


def save_results(
    output,
    *,
    case,
    ids,
    target,
    paper_target,
    controls,
    prediction,
    response,
    checkpoint,
    q,
    metrics,
    derived=None,
):
    """固定物理数组及来源，不把参考状态冒作生成控制的响应。"""
    count = len(ids)
    arrays = {
        "ids": np.asarray(ids),
        "target": target,
        "paper_target": paper_target,
        "controls": controls,
        "prediction": prediction,
        "response": response,
    }
    declarations = {}
    for name, field in (derived or {}).items():
        if name in arrays or name + "_valid" in arrays:
            raise ValueError("派生字段不得覆盖已有物理结果")
        if not isinstance(field, dict) or set(field) != {"values", "valid", "units", "axes"}:
            raise ValueError("派生字段必须声明 values/valid/units/axes")
        value, valid = np.asarray(field["values"]), np.asarray(field["valid"])
        if valid.dtype != np.bool_ or valid.shape != value.shape or not valid.any():
            raise ValueError("派生字段有效性必须逐实体对齐且至少一项有效")
        if not field["units"] or not field["axes"].startswith("B"):
            raise ValueError("派生字段缺少单位或样本轴")
        arrays[name], arrays[name + "_valid"] = value, valid
        declarations[name] = {
            "valid": name + "_valid",
            "units": field["units"],
            "axes": field["axes"],
            "identity": "ids",
            "space": "physical",
        }
    if any(len(value) != count for value in arrays.values()):
        raise ValueError("控制结果样本身份不对齐")
    if (
        len(set(ids)) != count
        or prediction.shape != response.shape
        or target.shape != response.shape
    ):
        raise ValueError("控制结果样本或状态形状不符")
    return save_arrays(
        output,
        arrays,
        kind="control_results_v1",
        metadata={
            "case": case,
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": digest(checkpoint),
            "q": q,
            "metrics": metrics,
            "target_source": "outputs",
            "paper_target_separate": True,
            "scope": "three_hour_integration_not_paper_reproduction",
            "state_axes": "B,T,X" if case == "burgers" else "B,C,T",
            "control_axes": "B,T,X" if case == "burgers" else "B,T,C",
            "time_start": 0.0,
            "time_step": 0.1,
            "units": "original_physical_units",
            "derived_fields": declarations,
        },
    )
