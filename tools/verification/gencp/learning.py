"""在固定验证样本和同一初始噪声上比较训练前后生成误差。"""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import torch

from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from tools.verification.gencp.reference import construct, load_reference


def measure(root, source, dataset, backbone, device="mps"):
    """固定归一化验证误差；与最终物理量/论文指标分别命名。"""
    root = Path(root)
    ns = load_reference(source)
    fields = ("neutron", "solid", "fluid") if dataset == "ntcouple" else ("fluid", "structure")
    report = {
        "space": "normalized",
        "seed": 43,
        "samples": 16,
        "fields": {},
        "paper_eligible": False,
    }
    for field in fields:
        checkpoint = torch.load(
            root / "reference" / f"{field}.pt", map_location="cpu", weights_only=False
        )
        fixed = torch.load(
            root / "reference" / f"{field}_single.pt", map_location=device, weights_only=False
        )
        model = construct(ns, dataset, backbone, field).to(device)
        model.load_state_dict(checkpoint["initial"])
        model.eval()
        trainer = SimpleNamespace(
            model=model, args=SimpleNamespace(**checkpoint["settings"]), device=device
        )
        endpoint = (
            torch.cat((fixed["inputs"], fixed["target"]), dim=-1)
            if dataset == "ntcouple"
            else fixed["target"]
        )
        torch.manual_seed(43)
        with torch.no_grad():
            prediction = ns["sample"](
                trainer,
                torch.randn_like(endpoint),
                fixed["target"],
                {"x0": fixed["inputs"], "cond": {}},
                model,
            )
        selected = (
            slice(None)
            if dataset == "ntcouple"
            else (slice(0, 3) if field == "fluid" else slice(3, 4))
        )
        target = fixed["target"][..., selected].cpu()
        before = trajectory_metrics(prediction[..., selected].cpu(), target)
        after = trajectory_metrics(fixed["prediction"][..., selected].cpu(), target)
        report["fields"][field] = {
            "before": before,
            "after": after,
            "improved": after["field_relative_l2"] < before["field_relative_l2"],
        }
        del model, trainer, fixed
    (root / "learning.json").write_text(json.dumps(report, indent=2, allow_nan=False))
    print(
        json.dumps(
            {
                field: {
                    "before": v["before"]["field_relative_l2"],
                    "after": v["after"]["field_relative_l2"],
                    "improved": v["improved"],
                }
                for field, v in report["fields"].items()
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "source", "dataset", "backbone"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--device", default="mps")
    args = parser.parse_args()
    measure(**vars(args))
