"""正式网络单批硬件探测：检查参考重复稳定性，不替代完整数据验收。"""

import argparse
import json
import sys
import time
from pathlib import Path

import torch

from tools.verification.transolver3.compare import compare


def main():
    """相同种子重新构造正式网络，记录前向、梯度及一次更新差异。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--points", type=int, default=5680)
    parser.add_argument("--paired", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.repository.resolve()))
    from models.Transolver_chunk_opt_matrix_mul import Model

    torch.set_num_threads(1)
    generator = torch.Generator().manual_seed(17)
    inputs = torch.randn(1, args.points, 12, generator=generator).to(args.device)
    target = torch.randn(1, args.points, 4, generator=generator).to(args.device)
    results, times = [], []
    for repeat in range(2):
        started = time.monotonic()
        torch.manual_seed(2)
        from ai4e_contrib.ability.model.transolver3.model import construct, predict

        factory = construct if args.paired and repeat == 1 else Model
        model = (
            factory(
                n_hidden=256,
                n_layers=24,
                n_head=8,
                mlp_ratio=2,
                slice_num=64,
                space_dim=12,
                fun_dim=0,
                out_dim=4,
                unified_pos=False,
            )
            .to(args.device)
            .float()
        )
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0)
        output = (
            predict(model, {"features": inputs})["fields"]
            if args.paired and repeat == 1
            else model([inputs], use_checkpoint=True)[0]
        )
        loss = (output - target).square().mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        gradients = {
            k: v.grad.detach().cpu().numpy().copy()
            for k, v in model.named_parameters()
            if v.grad is not None
        }
        optimizer.step()
        results.append(
            {
                "output": output.detach().cpu().numpy(),
                "gradients": gradients,
                "weights": {
                    k: v.detach().cpu().numpy().copy() for k, v in model.state_dict().items()
                },
            }
        )
        times.append(time.monotonic() - started)
        print(
            json.dumps(
                {"repeat": repeat, "seconds": times[-1], "loss": float(loss.detach().cpu())}
            ),
            flush=True,
        )
        del model, optimizer, output, loss
    reports = [
        compare(results[0]["output"], results[1]["output"], identity="reference_repeat/output")
    ]
    for kind in ("gradients", "weights"):
        for key, value in results[0][kind].items():
            reports.append(
                compare(value, results[1][kind][key], identity=f"reference_repeat/{kind}/{key}")
            )
    result = {
        "scope": "formal_network_one_batch_paired"
        if args.paired
        else "formal_network_one_batch_reference_repeat",
        "full_acceptance": False,
        "device": args.device,
        "torch": torch.__version__,
        "points": args.points,
        "seconds": times,
        "passed": all(r["passed"] for r in reports),
        "comparisons": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "comparisons"}), flush=True)


if __name__ == "__main__":
    main()
