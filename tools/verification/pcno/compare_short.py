"""比较短切片的模型、AdamW、调度、随机流和逐次损失。"""

import argparse
import json
from pathlib import Path

import torch


def compare(reference, candidate):
    """固定CPU容差；任何超差直接失败，不调整容差。"""
    r = torch.load(Path(reference) / "slice.pt", map_location="cpu", weights_only=False)
    d = torch.load(candidate, map_location="cpu", weights_only=False)

    def check(a, b):
        if isinstance(a, torch.Tensor):
            torch.testing.assert_close(a, b, rtol=1e-5, atol=1e-6)
        elif isinstance(a, dict):
            assert a.keys() == b.keys()
            for k in a:
                check(a[k], b[k])
        elif isinstance(a, (list, tuple)):
            assert len(a) == len(b)
            for x, y in zip(a, b):
                check(x, y)
        else:
            assert a == b, (a, b)

    for key in ["model", "optimizer", "scheduler"]:
        check(r[key], d[key])
    check(r["random"], d["python_rng"])
    check(r["torch"], d["torch_rng"])
    assert r["paths"] == d["stream"]["chunks"]
    losses = [
        json.loads(line)["loss"]
        for line in (Path(reference) / "updates.jsonl").read_text().splitlines()
    ]
    torch.testing.assert_close(
        torch.tensor(losses), torch.tensor(d["history"]), rtol=1e-5, atol=1e-6
    )
    return {
        "passed": True,
        "updates": d["updates"],
        "rtol": 1e-5,
        "atol": 1e-6,
        "checks": [
            "model",
            "optimizer",
            "scheduler",
            "python_rng",
            "torch_rng",
            "chunk_order",
            "losses",
        ],
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reference", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    result = compare(a.reference, a.candidate)
    a.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
