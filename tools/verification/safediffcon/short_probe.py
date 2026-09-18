"""三小时配置计时：真实数据、更新、校准、反传适配和响应小探针。"""

import argparse
import json
import time
from pathlib import Path


def main():
    """必须由累计预算监督器调用，测量结果用于分配正式更新数。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    import torch

    from ai4e_contrib.ability.constraint.safediffcon.calibration import calibrate
    from ai4e_contrib.ability.inference.safediffcon.adaptation import adaptation_loss
    from ai4e_contrib.ability.inference.safediffcon.control import guidance, sample
    from ai4e_contrib.ability.model.safediffcon.adapters import build_model
    from ai4e_contrib.ability.transform.safediffcon.preparation import prepare_arrays
    from ai4e_contrib.application.datasets.safediffcon import arrays
    from ai4e_contrib.application.pde_control.safediffcon.training import seed_all

    seed_all(42)
    root = (
        "/Users/zonghui/work/datasets/1D_burger/1D Burgers_"
        if args.case == "burgers"
        else "/Users/zonghui/work/datasets/tokamak"
    )
    physical = getattr(arrays, "read_" + args.case)(root, "test")
    prepared = prepare_arrays(physical, case=args.case)
    state = torch.tensor(prepared["model"][:16], device="mps")
    target = torch.tensor(prepared["target"][:16], device="mps")
    model = build_model(case=args.case, dim=64, ddim_steps=50, device="mps")
    opt = torch.optim.Adam(model.parameters(), lr=1e-5, betas=(0.9, 0.99))
    start = time.monotonic()
    for step in range(10):
        opt.zero_grad()
        loss = model(state)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    torch.mps.synchronize()
    update_seconds = (time.monotonic() - start) / 10
    start = time.monotonic()
    q = calibrate(model, state[:2], target[:2], case=args.case, q=0.0, weight=1.0, alpha=0.9)
    cal_seconds = time.monotonic() - start
    opt.zero_grad()
    loss = adaptation_loss(
        model, state[:2], target[:2], case=args.case, q=q, weight=0.01, guide=guidance
    )
    loss.backward()
    opt.step()
    generated = sample(model, state[:2], target[:2], case=args.case, q=q, weight=0.01)
    result = {
        "case": args.case,
        "update_seconds": update_seconds,
        "calibration_two_seconds": cal_seconds,
        "q": q,
        "loss": float(loss.detach()),
        "shape": list(generated.shape),
        "parameters": sum(p.numel() for p in model.parameters()),
    }
    Path(args.output).write_text(json.dumps(result, indent=2))
    print(result)


if __name__ == "__main__":
    main()
