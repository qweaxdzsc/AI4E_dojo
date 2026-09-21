"""冻结三角形连续性算子后扫描官方训练/验证轨迹，不读取测试标签。"""

import argparse
import json
import time
from pathlib import Path

import torch

from ai4e_contrib.application.datasets.cylinder_flow.adapter import decode_trajectory
from ai4e_core.abilities.constraint.continuity import triangle_geometry, triangle_gradient
from ai4e_core.abilities.data.source.tfrecord import iter_tfrecord


def audit(root):
    root = Path(root)
    meta = json.loads((root / "meta.json").read_text())
    report = {
        "threshold": 0.01,
        "operator": "P1 triangle area-weighted gradient",
        "trajectories": [],
    }
    for split in ("train", "valid"):
        for path in sorted((root / split).glob("*.tfrecord")):
            sample = decode_trajectory(next(iter_tfrecord(path)), meta)
            p, cells = sample["position"].double(), sample["cells"]
            inverse, area = triangle_geometry(p, cells)
            valid = (sample["node_type"][cells] == 0).all(-1)
            area = area * valid
            if area.sum() <= 0:
                raise ValueError("没有内部流体三角形")
            divsq, gradsq, ratios = 0.0, 0.0, []
            for chunk in sample["velocity"].split(30):
                grad = triangle_gradient(chunk.double(), cells, inverse)
                div = grad[..., 0, 0] + grad[..., 1, 1]
                d = (div.square() * area).sum(-1)
                g = (grad.square().sum((-2, -1)) * area).sum(-1)
                ratios.extend(torch.sqrt(d / g).tolist())
                divsq += d.sum().item()
                gradsq += g.sum().item()
            ratio = (divsq / gradsq) ** 0.5
            item = {
                "id": f"{split}/{path.stem}",
                "frames": 600,
                "nodes": len(p),
                "triangles": len(cells),
                "valid_triangles": int(valid.sum()),
                "ratio": ratio,
                "frame_ratios": ratios,
                "passed": ratio <= 0.01,
            }
            report["trajectories"].append(item)
            print(item["id"], ratio, flush=True)
    report["passed"] = bool(report["trajectories"]) and all(
        x["passed"] for x in report["trajectories"]
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("output")
    args = parser.parse_args()
    torch.set_num_threads(4)
    start = time.monotonic()
    report = audit(args.source)
    report["seconds"] = time.monotonic() - start
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
