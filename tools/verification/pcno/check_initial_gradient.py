"""比较两分支全分辨率首步分项与裁剪前梯度，参考为已冻结源码实跑产物。"""

import argparse
import json
from pathlib import Path

import torch

from ai4e_contrib.ability.model.pcno import build_model
from ai4e_contrib.application.geothermal.pcno.objective import loss_components
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig
from tools.verification.pcno.verify_first_step import compare


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("data", type=Path)
    p.add_argument("reference", type=Path)
    p.add_argument("branch", choices=["pres", "temp"])
    p.add_argument("output", type=Path)
    a = p.parse_args()
    torch.set_num_threads(4)
    stats = TrainConfig.stats_to_device(json.loads((a.data / "stats.json").read_text()), "cpu")
    model = build_model(branch=a.branch)
    model.load_state_dict(torch.load(a.reference / "initial.pt", weights_only=False))
    chunk = torch.load(a.data / "chunk_06.pt", weights_only=False)
    sample = {k: v[:1] for k, v in chunk.items()}
    components = loss_components(model, sample, branch=a.branch, epoch=1, stats=stats)
    expected = json.loads((a.reference / "updates.jsonl").read_text().splitlines()[0])
    for key, source in [
        ("loss", "loss"),
        ("mse", "mse_loss"),
        ("gradient", "grad_loss"),
        ("weighted", "weighted_loss"),
        ("physics", "loss_phys"),
        ("task", "loss_task"),
    ]:
        compare(components[key].detach(), torch.tensor(expected[source]), key)
    components["loss"].backward()
    compare(
        {k: p.grad for k, p in model.named_parameters()},
        torch.load(a.reference / "first-gradient.pt", weights_only=False),
        "gradients",
    )
    a.output.write_text(
        json.dumps(
            {
                "passed": True,
                "branch": a.branch,
                "components": list(components),
                "rtol": 1e-5,
                "atol": 1e-6,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
