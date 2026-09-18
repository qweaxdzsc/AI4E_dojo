"""独立原函数数值对照：采样、输入引导、加权校准及真实响应。"""

import argparse
import ast
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from compare import setup_source, source_model


def extract(path, names, namespace):
    """执行固定原文件中指定定义，隔离原脚本的 TensorFlow 顶层依赖。"""
    tree = ast.parse(Path(path).read_text())
    nodes = [
        n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    if len(nodes) != len(names):
        raise ValueError("原定义不完整")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)  # noqa: S102 - verified frozen source
    return namespace


def verify(case, snapshot, output):
    """固定输入噪声，逐值比较原采样与迁入采样，校准用原类计算。"""
    setup_source(snapshot, case)
    from ai4e_contrib.ability.constraint.safediffcon.calibration import calibrate
    from ai4e_contrib.ability.constraint.safediffcon.objective import reweights
    from ai4e_contrib.ability.inference.safediffcon.control import guidance, sample
    from ai4e_contrib.ability.model.safediffcon.adapters import build_model
    from ai4e_contrib.ability.transform.safediffcon.preparation import TOKAMAK_SCALE, prepare_arrays
    from ai4e_contrib.application.datasets.safediffcon import arrays

    torch.set_num_threads(4)
    source = Path(snapshot) / ("1D" if case == "burgers" else "tokamak")
    root = (
        "/Users/zonghui/work/datasets/1D_burger/1D Burgers_"
        if case == "burgers"
        else "/Users/zonghui/work/datasets/tokamak"
    )
    values = prepare_arrays(getattr(arrays, "read_" + case)(root, "test"), case=case)
    state = torch.tensor(values["model"][:4])
    target = torch.tensor(values["target"][:4])
    torch.manual_seed(42)
    reference = source_model(case=case, dim=8, ddim_steps=50, device="cpu")
    dojo = build_model(case=case, dim=8, ddim_steps=50, device="cpu")
    dojo.load_state_dict(reference.state_dict())
    torch.manual_seed(16)
    expected = sample(reference, state, target, case=case, q=0.2, weight=0.3)
    torch.manual_seed(16)
    actual = sample(dojo, state, target, case=case, q=0.2, weight=0.3)
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    scope = {
        "torch": torch,
        "np": np,
        "logging": logging,
        "Tuple": tuple,
        "SCALER": 10 if case == "burgers" else torch.tensor(TOKAMAK_SCALE)[None, :, None],
    }
    if case == "burgers":
        scope["InferenceConfig"] = object
        extract(
            source / "inference/guidance.py",
            {"calculate_guidance", "get_weight", "normalize_weights"},
            scope,
        )
        config = SimpleNamespace(
            device="cpu",
            num_cal_batch=2,
            nt=11,
            use_max_safety=True,
            u_bound=0.8,
            guidance_weights={"w_score": 0.3},
            InfFT_Q=0.1,
        )
        get_weight = lambda x, q: scope["get_weight"](x, q, config)
        extract(source / "inference/conformal.py", {"ConformalCalculator"}, scope)
    else:
        scope["InferenceConfig"] = object
        extract(source / "utils/metrics.py", {"calculate_safety_score"}, scope)
        extract(source / "utils/guidance.py", {"calculate_weight", "normalize_weights"}, scope)
        config = SimpleNamespace(
            device="cpu",
            num_cal_batch=2,
            nt_total=122,
            guidance_weights={"w_obj": 0.0, "w_safe": 1.0},
            guidance_scaler=0.3,
            safety_threshold=4.98,
            finetune_set="test",
            wo_post_train=False,
            finetune_quantile=0.1,
            finetune_guidance_weights={"w_obj": 0.0, "w_safe": 1.0},
            finetune_guidance_scaler=0.3,
        )
        get_weight = lambda x, q: scope["calculate_weight"](x, target, 122, q, 4.98, 0.0, 1.0, 0.3)
        extract(source / "inference/conformal.py", {"ConformalCalculator"}, scope)
    expected_weight = scope["normalize_weights"](get_weight(state, 0.2))
    torch.testing.assert_close(
        reweights(state, target, case=case, q=0.2, weight=0.3), expected_weight, rtol=0, atol=0
    )
    x = state.clone().requires_grad_()
    raw = get_weight(x, 0.2)
    # 原代价是 -log(weight)；选温和权重避免下溢，求输入梯度独立对照。
    expected_gradient = torch.autograd.grad(-raw.log().sum(), x)[0]
    actual_gradient = guidance(state, target, case=case, q=0.2, weight=0.3)
    torch.testing.assert_close(actual_gradient, expected_gradient, rtol=1e-6, atol=1e-7)
    calculator = scope["ConformalCalculator"](reference, config)
    batches = (
        iter([state[:2], state[2:]])
        if case == "burgers"
        else iter([(state[:2], torch.arange(2)), (state[2:], torch.arange(2, 4))])
    )
    torch.manual_seed(123)
    scores, weights, states = (
        calculator.get_conformal_scores(batches, 0.2)
        if case == "burgers"
        else calculator.get_conformal_scores(batches, target, 0.2)
    )
    quantile = calculator.calculate_quantile(scores, weights, states, 0.9)
    torch.manual_seed(123)
    actual_q = calibrate(
        dojo,
        state,
        target,
        case=case,
        q=0.2,
        weight=0.3,
        alpha=0.9,
        batch_size=2,
        previous_q=0.1,
        previous_weight=0.3,
    )
    np.testing.assert_allclose(actual_q, float(quantile), rtol=1e-6, atol=1e-6)
    result = {
        "case": case,
        "sampling_max_abs": float((expected - actual).abs().max()),
        "guidance_max_abs": float((actual_gradient - expected_gradient).abs().max()),
        "q_reference": float(quantile),
        "q_dojo": actual_q,
        "status": "passed",
        "scope": "original source definitions; dim8 CPU, same random inputs; full-size pretrain checked separately",
    }
    Path(output).write_text(json.dumps(result, indent=2))
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    verify(args.case, args.snapshot, args.output)
