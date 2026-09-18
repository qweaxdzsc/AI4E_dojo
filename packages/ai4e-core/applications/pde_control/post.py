"""只读固定控制结果的评价与导出，不导入网络或响应计算。"""

from pathlib import Path

from ai4e_core.abilities.data.save.arrays import save_json

from .contracts import read_arrays


def analyze(results: str | Path, output: str | Path, *, evaluate) -> str:
    """读取已冻结数组重算指标，附加字段一并读回消费。"""
    record, arrays = read_arrays(results, kind="control_results_v1")
    values = evaluate(
        arrays["response"],
        arrays["target"],
        case=record["metadata"]["case"],
        paper_target=arrays["paper_target"],
    )
    derived = {}
    for name, declaration in (record["metadata"]["derived_fields"] or {}).items():
        valid = arrays[declaration["valid"]]
        if valid.shape != arrays[name].shape or not valid.any():
            raise ValueError("派生字段有效性与固定数组不符")
        derived[name] = {
            "minimum": float(arrays[name][valid].min()),
            "maximum": float(arrays[name][valid].max()),
            "units": declaration["units"],
            "axes": declaration["axes"],
            "identity": declaration["identity"],
        }
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "scope": record["metadata"]["scope"],
        "metrics": values,
        "derived": derived,
        "source": str(results),
    }
    save_json(output / "metrics.json", report)
    return str((output / "metrics.json").resolve())
