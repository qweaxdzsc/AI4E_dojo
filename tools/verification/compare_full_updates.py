"""正式网络、真实采样输入的逐更新差分；仅验收环境依赖 Noether。"""

import argparse
import json
from pathlib import Path

import torch
from aero_cfd.presets import ShapeNetCarPreset
from noether.core.optimizer.lion import Lion as ReferenceLion
from noether.modeling.models.ab_upt import AnchoredBranchedUPT as Reference
from recipe_config import load_application_config
from state_mapping import mapped_state

from ai4e_contrib.ability.model.abupt.batch import collate
from ai4e_contrib.ability.model.abupt.model import construct
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core.abilities.constraint.supervised import supervised
from ai4e_core.abilities.training.optimization import Lion, parameter_groups
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep import preparation
from ai4e_core.applications.aero_cfd.trainprep.dataset import iter_partition_batches

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
cfg = apply_resolved(load_application_config(args.config))
data = preparation.freeze_normalization(preparation.prepare_fields(preparation.open_dataset(cfg)))
refcfg = ShapeNetCarPreset().build_config(
    model_kind="noether.modeling.models.aerodynamics.AeroABUPT",
    model_params={
        "hidden_dim": 192,
        "geometry_depth": 6,
        "physics_blocks": ["perceiver"] + ["shared", "cross"] * 5,
    },
    trainer_kind="noether.training.trainers.WeightedLossTrainer",
    trainer_params={"field_weights": {"surface_pressure": 1.0, "volume_velocity": 1.0}},
    dataset_root="/tmp",
    output_path="/tmp",
    max_epochs=2,
    batch_size=1,
    accelerator="cpu",
    run_id="updates",
)
torch.manual_seed(42)
ref = Reference(refcfg.model)
torch.manual_seed(42)
model = construct(**cfg["model"]["parameters"], data_specs=cfg["model"]["data_specs"])
for k, v in model.state_dict().items():
    torch.testing.assert_close(v, mapped_state(ref, model)[k], rtol=0, atol=0)
ropt = ReferenceLion(parameter_groups(ref, weight_decay=0.05), lr=5e-5 / 79)
opt = Lion(parameter_groups(model, weight_decay=0.05), lr=5e-5 / 79)
rows = []
iterator = iter_partition_batches(
    data.index,
    "train",
    prepare=prepare_inputs,
    collate=collate,
    normalization=data.normalization,
    physical_prepare=data.physical_prepare,
    normalized_input=False,
    sampling=cfg["sampling"],
    config=cfg,
    batch_size=1,
    device="cpu",
)
for i, batch in enumerate(iterator):
    if i == 20:
        break
    losses = []
    for net, optimizer in [(ref, ropt), (model, opt)]:
        optimizer.zero_grad()
        out = net(**batch["inputs"])[0]
        if net is ref:
            loss = sum(
                (
                    torch.nn.functional.mse_loss(batch["targets"][k + "_target"], v)
                    for k, v in out.items()
                ),
                start=torch.zeros(()),
            )
        else:
            loss = supervised(out, batch["targets"], cfg["model"]["supervision"])["loss"]
        losses.append(float(loss.detach()))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        optimizer.step()
        for g in optimizer.param_groups:
            g["lr"] = 5e-5 * (i + 2) / 79
    expected = mapped_state(ref, model)
    error = max(
        float((v - expected[k]).abs().max()) for k, v in model.state_dict().items() if v.numel()
    )
    rows.append({"update": i + 1, "losses": losses, "max_abs": error})
    print(rows[-1], flush=True)
passed = all(row["max_abs"] == 0 and row["losses"][0] == row["losses"][1] for row in rows)
args.output.write_text(
    json.dumps(
        {
            "passed": passed,
            "scope": "Full official architecture, 20 real-data Lion updates",
            "rows": rows,
        },
        indent=2,
    )
)
if not passed:
    raise AssertionError("正式网络逐更新不一致")
