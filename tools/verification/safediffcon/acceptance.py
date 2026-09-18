"""比较已完成的固定训练与响应产物，不启动新的训练或选优。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch


def assert_state_close(left, right):
    """递归核对优化器、调度器和采样游标；记录路径不混入数值状态。"""
    if isinstance(left, torch.Tensor):
        torch.testing.assert_close(left, right, rtol=1e-4, atol=1e-6)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            assert_state_close(left[key], right[key])
    elif isinstance(left, (tuple, list)):
        assert len(left) == len(right)
        for a, b in zip(left, right, strict=True):
            assert_state_close(a, b)
    else:
        assert left == right


def checkpoint_difference(left, right):
    """核对每个参数及训练历史；原训练器与Dojo允许记录路径不同。"""
    a = torch.load(left, map_location="cpu", weights_only=False)
    b = torch.load(right, map_location="cpu", weights_only=False)
    assert a["status"] == b["status"] == "complete"
    assert a["updates"] == b["updates"]
    np.testing.assert_allclose(a["history"], b["history"], rtol=1e-4, atol=1e-6)
    for state_key in ("optimizer", "scheduler", "stream"):
        assert_state_close(a[state_key], b[state_key])
    difference = 0.0
    for kind in ("model", "ema"):
        if a[kind] is None:
            assert b[kind] is None
            continue
        assert set(a[kind]) == set(b[kind])
        for name, value in a[kind].items():
            torch.testing.assert_close(value, b[kind][name], rtol=1e-4, atol=1e-6)
            if value.dtype != torch.bool:
                difference = max(difference, float((value - b[kind][name]).abs().max()))
    if a["algorithm_state"] != b["algorithm_state"]:
        for key in a["algorithm_state"]:
            if key == "q":
                np.testing.assert_allclose(
                    a["algorithm_state"][key], b["algorithm_state"][key], rtol=1e-4, atol=1e-6
                )
            else:
                assert a["algorithm_state"][key] == b["algorithm_state"][key]
    return {
        "updates": a["updates"],
        "last_loss": a["history"][-1],
        "max_model_ema_abs": difference,
        "history_exact": a["history"] == b["history"],
    }


def compare(reference, dojo, output, case, *, expected_samples=50):
    """固定50样本，身份/数量/安全分类精确，数值使用事前容差。"""
    from ai4e_contrib.ability.eval.safediffcon.control import metrics
    from ai4e_core.applications.pde_control.contracts import read_arrays

    a = json.loads(Path(reference).read_text())
    b = json.loads(Path(dojo).read_text())
    stages = {
        stage: checkpoint_difference(a[stage + "_checkpoint"], b[stage + "_checkpoint"])
        for stage in ("pretrain", "posttrain")
    }
    stages["posttrain_round_0"] = checkpoint_difference(
        Path(a["posttrain_checkpoint"]).parent.parent / "posttrain_0" / "latest.pt",
        Path(b["posttrain_checkpoint"]).parent.parent / "posttrain_0" / "latest.pt",
    )
    ra, xa = read_arrays(a["results"], kind="control_results_v1")
    rb, xb = read_arrays(b["results"], kind="control_results_v1")
    stages["adapt"] = checkpoint_difference(
        ra["metadata"]["checkpoint"], rb["metadata"]["checkpoint"]
    )
    assert len(xa["ids"]) == len(xb["ids"]) == expected_samples
    assert np.array_equal(xa["ids"], xb["ids"])
    fields = {}
    for name in ("target", "paper_target", "controls", "prediction", "response"):
        np.testing.assert_allclose(xa[name], xb[name], rtol=1e-4, atol=1e-6)
        fields[name] = float(np.max(np.abs(xa[name] - xb[name])))
    mask_a = np.abs(xa["response"]) > 0.8 if case == "burgers" else xa["response"][:, 1] < 4.98
    mask_b = np.abs(xb["response"]) > 0.8 if case == "burgers" else xb["response"][:, 1] < 4.98
    assert np.array_equal(mask_a, mask_b)
    result = metrics(xb["response"], xb["target"], case=case, paper_target=xb["paper_target"])
    for summary in (a, b):
        stored = json.loads(Path(summary["report"]).read_text())["metrics"]
        np.testing.assert_allclose(
            stored["per_sample_objective"], result["per_sample_objective"], rtol=1e-4, atol=1e-6
        )
    payload = {
        "case": case,
        "status": "passed",
        "scope": a["scope"],
        "shared_boundaries": "prepared arrays, batch stream, checkpoint schema, response solver, metrics and result storage",
        "paper_reproduction": False,
        "samples": expected_samples,
        "diagnostic_only": expected_samples != 50,
        "stages": stages,
        "arrays_max_abs": fields,
        "metrics": result,
        "reference": str(reference),
        "dojo": str(dojo),
        "tolerance": {"rtol": 1e-4, "atol": 1e-6, "identity_and_safety": "exact"},
    }
    Path(output).write_text(json.dumps(payload, indent=2))
    print({k: v for k, v in payload.items() if k not in ("metrics", "reference", "dojo")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--dojo", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--diagnostic-samples", type=int, choices=range(1, 50))
    args = parser.parse_args()
    compare(
        args.reference,
        args.dojo,
        args.output,
        args.case,
        expected_samples=args.diagnostic_samples or 50,
    )
