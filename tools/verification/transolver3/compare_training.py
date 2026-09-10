"""逐张量比较完整训练与恢复产物，完整记录最大误差和全部超差数。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from tools.verification.transolver3.compare import compare


def compare_state(actual, expected, prefix, reports):
    """递归比较模型、优化器、调度器和数值历史，结构差异也拒绝。"""
    if isinstance(actual, np.ndarray) and isinstance(expected, np.ndarray):
        reports.append(compare(actual, expected, identity=prefix))
    elif isinstance(actual, torch.Tensor) and isinstance(expected, torch.Tensor):
        reports.append(compare(actual.cpu().numpy(), expected.cpu().numpy(), identity=prefix))
    elif isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual) != set(expected):
            reports.append({"identity": prefix, "passed": False, "reason": "keys_or_order"})
            return
        for key in actual:
            compare_state(actual[key], expected[key], f"{prefix}/{key}", reports)
    elif isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            reports.append({"identity": prefix, "passed": False, "reason": "length"})
            return
        for i, (left, right) in enumerate(zip(actual, expected, strict=True)):
            compare_state(left, right, f"{prefix}/{i}", reports)
    elif isinstance(actual, (float, int, np.number)) and isinstance(
        expected, (float, int, np.number)
    ):
        reports.append(compare(actual, expected, identity=prefix))
    else:
        reports.append({"identity": prefix, "passed": actual == expected})


def run(actual_path, expected_path, *, reference_repeat=False):
    """独立运行产物比较，不将参考权重加载到 Dojo 来绕过训练。"""
    actual = torch.load(actual_path, map_location="cpu", weights_only=False)
    expected = torch.load(expected_path, map_location="cpu", weights_only=False)
    reports = []
    mapping = {
        "model": "model_state_dict",
        "optimizer": "optimizer_state_dict",
        "scheduler": "scheduler_state_dict",
        "best": "best_validation_mse",
    }
    for key, ref in mapping.items():
        compare_state(actual[ref if reference_repeat else key], expected[ref], key, reports)
    left = actual["history"]
    right = expected["history"]
    if len(left) != len(right):
        reports.append({"identity": "history", "passed": False, "reason": "length"})
    for i, (a, b) in enumerate(zip(left, right)):
        if reference_repeat:
            compare_state(a, b, f"history/{i}", reports)
        else:
            for field, ref in (
                ("loss", "train_normalized_mse"),
                ("learning_rate", "learning_rate"),
            ):
                compare_state(a[field], b[ref], f"history/{i}/{field}", reports)
            for field in ("normalized_mse", "physical_mse", "physical_mae"):
                compare_state(
                    a["evaluation"][field], b["validation"][field], f"history/{i}/{field}", reports
                )
    report = {
        "actual": str(actual_path),
        "expected": str(expected_path),
        "reference_repeat": reference_repeat,
        "passed": all(r["passed"] for r in reports),
        "comparisons": reports,
        "mismatch_count": sum(r.get("mismatch_count", int(not r["passed"])) for r in reports),
        "max_absolute_error": max((r.get("max_absolute_error") or 0) for r in reports),
    }
    return report


def main():
    """命令行失败返回非零，输出完整差异便于定位。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-repeat", action="store_true")
    args = parser.parse_args()
    report = run(args.actual, args.expected, reference_repeat=args.reference_repeat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "comparisons"}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
