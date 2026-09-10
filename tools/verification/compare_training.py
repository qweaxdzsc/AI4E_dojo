"""冻结官方重复运行容差、对照完整训练与恢复权重；无需安装 Noether。"""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import torch
from comparison_protocol import assess, read_protocol
from state_mapping import mapped_state


def load(path):
    """仅读取本地可信验收检查点。"""
    return torch.load(path, map_location="cpu", weights_only=False)


def freeze(first, second, output):
    """官方自身必须先完全重现，才发布预声明的 CPU FP32 容差。"""
    a, b = load(first), load(second)
    assert a["training_iteration"] == b["training_iteration"]
    a, b = a["state_dict"], b["state_dict"]
    assert a.keys() == b.keys()
    exact = all(torch.equal(value, b[key]) for key, value in a.items())
    report = {
        "reference_a": str(first),
        "reference_b": str(second),
        "reference_repeat_exact": exact,
        "rtol": 1e-5,
        "atol": 1e-6,
        "passed": exact,
        "reason": "Predeclared CPU FP32 tolerance; official repeated run must be exact; never relaxed after Dojo comparison.",
    }
    output.write_text(json.dumps(report, indent=2))
    if not exact:
        raise AssertionError("官方自身未精确重现，不能发布本环境的对照容差")


def compare(
    reference, checkpoint, tolerance, output, *, actual_protocol=None, reference_protocol=None
):
    """核对正式规模、总更新数与全部参数和缓冲区。"""
    eligibility = assess(
        read_protocol(
            actual_protocol or checkpoint.parent.parent / "artifacts/training-protocol.json"
        ),
        read_protocol(reference_protocol),
        "training",
    )
    if eligibility["status"] != "comparable":
        output.write_text(
            json.dumps(
                {"passed": False, "eligibility": eligibility, "numerical_status": "not_comparable"},
                indent=2,
            )
        )
        raise AssertionError("不具备数值可比条件，见对照协议报告")
    threshold = json.loads(tolerance.read_text()) if tolerance else {"rtol": 1e-5, "atol": 1e-6}
    if threshold["rtol"] != 1e-5 or threshold["atol"] != 1e-6:
        raise ValueError("本验收不得改动既定数值容差")
    origin, actual = load(reference), load(checkpoint)
    source = {k.removeprefix("backbone."): v for k, v in origin["state_dict"].items()}
    config = actual["effective_config"]["model"]["parameters"]
    expected = mapped_state(
        SimpleNamespace(state_dict=lambda: source),
        SimpleNamespace(state_dict=lambda: actual["model"], block_types=config["blocks"]),
    )
    errors = {
        k: float((v - expected[k]).abs().max()) if v.numel() else 0.0
        for k, v in actual["model"].items()
    }
    failures = [
        k
        for k, v in actual["model"].items()
        if not torch.allclose(v, expected[k], rtol=threshold["rtol"], atol=threshold["atol"])
    ]
    same_iteration = (
        actual["epoch"] == origin["training_iteration"]["epoch"]
        and actual["updates"] == origin["training_iteration"]["update"]
    )
    reference_entries = load(reference.parent.parent / "tracker/entries.th")
    history = json.loads((checkpoint.parent.parent / "artifacts/training.json").read_text())[
        "history"
    ]
    rows = []
    for epoch in history:
        update = epoch["updates"]
        values = {
            "loss/online/total/E1": epoch["loss"],
            "loss/test/total": epoch["evaluation"]["loss"],
        }
        for name, value in epoch["evaluation"]["losses"].items():
            values["loss/test/" + name + "_loss"] = value
        for name, metric in epoch["evaluation"]["metrics"].items():
            field, method = name.split("/")
            values[
                "loss/test/" + field + "_" + ("l2err" if method == "relative_l2" else method)
            ] = metric["value"]
        for key, value in values.items():
            expected_value = float(reference_entries[key][update])
            close = abs(value - expected_value) <= threshold["atol"] + threshold["rtol"] * abs(
                expected_value
            )
            rows.append(
                {
                    "epoch": epoch["epoch"],
                    "metric": key,
                    "actual": value,
                    "reference": expected_value,
                    "passed": close,
                }
            )
    metrics_passed = all(row["passed"] for row in rows)
    report = {
        "reference": str(reference),
        "checkpoint": str(checkpoint),
        "tolerance": threshold,
        "eligibility": eligibility,
        "epoch": actual["epoch"],
        "updates": actual["updates"],
        "same_iteration": same_iteration,
        "model_parameters": config,
        "max_abs": max(errors.values()),
        "failed_tensors": failures,
        "passed": same_iteration and not failures and metrics_passed,
        "metrics": rows,
    }
    output.write_text(json.dumps(report, indent=2))
    if not report["passed"]:
        raise AssertionError(f"完整训练未对齐，最大绝对误差 {report['max_abs']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["freeze", "compare"])
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tolerance", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--actual-protocol", type=Path)
    parser.add_argument("--reference-protocol", type=Path)
    args = parser.parse_args()
    if args.mode == "freeze":
        freeze(args.reference, args.checkpoint, args.output)
    else:
        compare(
            args.reference,
            args.checkpoint,
            args.tolerance,
            args.output,
            actual_protocol=args.actual_protocol,
            reference_protocol=args.reference_protocol,
        )
