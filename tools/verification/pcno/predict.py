"""原仓库双分支独立推理：只用预测场求井级输出，标签只用于诊断指标。"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import torch

from tools.verification.pcno.reference import digest


def errors(prediction: torch.Tensor, truth: torch.Tensor) -> dict:
    """物理空间单例指标；字段调用者先去掉第零年，井级已为第 1—20 年。"""
    if prediction.shape != truth.shape or truth.numel() == 0:
        raise ValueError("Metric shape mismatch or empty truth")
    if not torch.isfinite(prediction).all() or not torch.isfinite(truth).all():
        raise ValueError("Metrics require finite values")
    residual = prediction.double() - truth.double()
    return {
        "mae": residual.abs().mean().item(),
        "rmse": residual.square().mean().sqrt().item(),
        "mare": (residual.abs() / (truth.double().abs() + 1e-8)).mean().item(),
    }


def require_complete(state: dict) -> None:
    """最终基线必须完成约定的全部更新，原权重导入不能冒充训练通过。"""
    if state.get("epoch") != 250 or state.get("updates") != 5250:
        raise ValueError("Reference final prediction requires 250 epochs / 5250 updates per branch")


def owned_arrays(value):
    """切断样本视图的整批 storage，防止单例结果隐含保存整个来源分片。"""
    if isinstance(value, torch.Tensor):
        return value.detach().clone()
    if isinstance(value, dict):
        return {key: owned_arrays(item) for key, item in value.items()}
    if isinstance(value, list):
        return [owned_arrays(item) for item in value]
    return value


def samples(root: Path, selection: str):
    """保留发布分片和例内顺序，每次只交付一个完整分辨率样本。"""
    paths = (
        sorted(root.glob("chunk_*.pt")) if selection == "training24" else [root / "Prob_Data.pt"]
    )
    for path in paths:
        chunk = torch.load(path, map_location="cpu", weights_only=False)
        for i in range(chunk["spatial_params"].shape[0]):
            yield f"{path.stem}/{i}", {key: value[i : i + 1] for key, value in chunk.items()}


def predict(
    source: Path, data: Path, pressure: Path, temperature: Path, output: Path, selection: str
):
    """加载完整双分支基线、逐例预测和物理计算，保存自包含结果。"""
    identities = [
        json.loads((p.parent / "identity.json").read_text()) for p in [pressure, temperature]
    ]
    for identity, branch in zip(identities, ["pres", "temp"]):
        if identity["branch"] != branch:
            raise ValueError("Checkpoint branch identity mismatch")
        for name, sha in identity["source"].items():
            if digest(source / name) != sha:
                raise ValueError("Source drift: " + name)
        for name, sha in identity["data"].items():
            if digest(data / name) != sha:
                raise ValueError("Data drift: " + name)
    for key in ["data", "source", "packages", "modes", "width", "threads", "device"]:
        if identities[0][key] != identities[1][key]:
            raise ValueError("Incompatible branch contract: " + key)
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(identities[0]["threads"])
    torch.set_num_interop_threads(1)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source.resolve()))
    model_source = importlib.import_module("PCNO_Model_4D")
    trainer = importlib.import_module("PCNO_Train_4D")
    networks = []
    for checkpoint, branch in zip([pressure, temperature], ["pres", "temp"]):
        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        require_complete(state)
        model = model_source.EnhancedP_T_Net(1, 1, 1, 1, 8, 8, train_mode=branch)
        model.load_state_dict(state["model"], strict=True)
        networks.append(model.eval())
    stats = trainer.TrainConfig.stats_to_device(
        json.loads((data / "stats.json").read_text()), "cpu"
    )
    records = []
    with torch.no_grad():
        for sample_id, sample in samples(data, selection):
            x, g = sample["spatial_params"], sample["global_params"]
            fields = []
            for model, key in zip(networks, ["pres", "temp"]):
                normalized = torch.nan_to_num(model(x, g), nan=0.0, posinf=1e4, neginf=-1e4)
                # Like source physics: decode before the clamp used only by supervised loss.
                fields.append(normalized * stats[key + "_std"] + stats[key + "_mean"])
            p, t = fields
            Pini, Tini, qinj, Tinj, pwf, k, phi, depth, Cp, lam, dz = (
                trainer.ModelConfig.decode_inputs(x, g, stats)
            )
            physics = model_source.physical_loss(
                T_i=Tini,
                p_i=Pini,
                Cp_r=Cp,
                lam_r=lam,
                dz=dz,
                q_inj=qinj,
                T_inj=Tinj,
                pwf=pwf,
                k=k,
                phi=phi,
                depth=depth,
            )
            mass, energy, twh, hwh, pinj, ewh, qout = physics.phy_loss(p, t)
            result = {
                "Pres": p,
                "Temp": t,
                "Twh": twh,
                "Hwh": hwh,
                "Pinj": pinj,
                "Ewh": ewh,
                "Qout": qout,
                "spatial_params": x,
                "global_params": g,
            }
            for key, value in result.items():
                arrays = value if isinstance(value, list) else [value]
                if any(not torch.isfinite(a).all() for a in arrays):
                    raise ValueError(f"{sample_id}: nonfinite {key}")
            metrics = None
            if selection == "training24":
                metrics = {}
                result["truth"] = {}
                for predicted, field in zip([p, t], ["pres", "temp"]):
                    truth = sample[field] * stats[field + "_std"] + stats[field + "_mean"]
                    result["truth"][field] = truth
                    metrics[field] = errors(predicted[..., 1:], truth[..., 1:])
                for predicted, key in [(twh, "Temp_wh"), (hwh, "Heat_wh"), (pinj, "P_inj")]:
                    metrics[key] = errors(predicted[0], sample[key][0])
                    result["truth"][key] = sample[key]
            filename = sample_id.replace("/", "_") + ".pt"
            torch.save(owned_arrays(result), output / filename)
            records.append(
                {
                    "id": sample_id,
                    "file": filename,
                    "sha256": digest(output / filename),
                    "metrics": metrics,
                    "production_wells": len(twh[0]),
                    "injection_wells": len(pinj[0]),
                    "mass_residual": mass.item(),
                    "energy_residual": energy.item(),
                }
            )
    expected = 24 if selection == "training24" else 18
    if len(records) != expected:
        raise ValueError("Incomplete prediction universe")
    aggregate = None
    if selection == "training24":
        aggregate = {
            field: {
                metric: sum(r["metrics"][field][metric] for r in records) / len(records)
                for metric in ["mae", "rmse", "mare"]
            }
            for field in records[0]["metrics"]
        }
    manifest = {
        "version": 1,
        "source": selection,
        "data_identity": identities[0]["data"],
        "statistics": {key: value.tolist() for key, value in stats.items()},
        "samples": records,
        "aggregate": aggregate,
        "checkpoints": {str(p): digest(p) for p in [pressure, temperature]},
        "years": list(range(1, 21)),
        "aggregation": "per-case then equal-case mean; wells equal within each case",
        "truth_scope": "training universe, not independent test"
        if selection == "training24"
        else "no independent truth",
        "joint_physics_uses": "both predicted fields; no companion truth",
    }
    (output / "results.json").write_text(json.dumps(manifest, indent=2, allow_nan=False))
    return manifest


def main():
    """以两份完成态检查点运行原版独立预测。"""
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "data", "pressure", "temperature", "output"]:
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--selection", choices=["training24", "demonstration18"], required=True)
    args = parser.parse_args()
    predict(args.source, args.data, args.pressure, args.temperature, args.output, args.selection)


if __name__ == "__main__":
    main()
