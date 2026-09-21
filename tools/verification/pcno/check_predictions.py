"""使用原模块同权重核对已落盘预测，包含两场、物理残差和井级量。"""

import argparse
import json
import sys
from pathlib import Path

import torch

from ai4e_core.applications.geothermal.post import read_results
from tools.verification.pcno.numerical_repair import apply_to_source_module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "checkpoints", "results", "output"]:
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    torch.set_num_threads(4)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(a.source))
    import PCNO_Model_4D as m
    import PCNO_Train_4D as t

    apply_to_source_module(m)
    record, arrays = read_results(a.results)
    states = json.loads(a.checkpoints.read_text())
    networks = {}
    for branch in ["pres", "temp"]:
        n = m.EnhancedP_T_Net(1, 1, 1, 1, 8, 8, train_mode=branch)
        state = torch.load(
            a.checkpoints.parent / states["branches"][branch]["file"], weights_only=False
        )
        n.load_state_dict(state["model"])
        networks[branch] = n.eval()
    stats = t.TrainConfig.stats_to_device(record["statistics"], "cpu")

    def compare(x, y):
        if isinstance(x, list):
            for left, right in zip(x, y, strict=True):
                compare(left, right)
        else:
            torch.testing.assert_close(x, y, rtol=1e-5, atol=1e-6)

    checked = []
    # First and last IDs exercise separate chunks/well counts without recomputing the whole set.
    with torch.no_grad():
        for index in sorted({0, len(arrays) - 1}):
            row = arrays[index]
            x, g = row["spatial_params"], row["global_params"]
            fields = {
                key: torch.nan_to_num(n(x, g), nan=0.0, posinf=1e4, neginf=-1e4)
                * stats[key + "_std"]
                + stats[key + "_mean"]
                for key, n in networks.items()
            }
            compare(fields["pres"], row["Pres"])
            compare(fields["temp"], row["Temp"])
            P, T, q, Ti, pwf, k, phi, d, Cp, lam, dz = t.ModelConfig.decode_inputs(x, g, stats)
            out = m.physical_loss(
                T_i=T,
                p_i=P,
                Cp_r=Cp,
                lam_r=lam,
                dz=dz,
                q_inj=q,
                T_inj=Ti,
                pwf=pwf,
                k=k,
                phi=phi,
                depth=d,
            ).phy_loss(fields["pres"], fields["temp"])
            for key, value in zip(["Twh", "Hwh", "Pinj", "Ewh", "Qout"], out[2:]):
                compare(value, row[key])
            compare(
                torch.tensor([float(out[0]), float(out[1])]),
                torch.tensor(
                    [record["samples"][index]["physics"][key] for key in ["mass", "energy"]]
                ),
            )
            checked.append(record["samples"][index]["id"])
    result = {
        "passed": True,
        "samples": checked,
        "rtol": 1e-5,
        "atol": 1e-6,
        "reference": "source with explicit inactive-viscosity-branch repair",
    }
    a.output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
