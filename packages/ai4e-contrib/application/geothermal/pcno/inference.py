"""PCNO 准备、检查点与双场预测的专属连接。"""

import json
import shutil
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.applications.geothermal.data import read_bundle
from ai4e_core.applications.geothermal.inference import predict_fields, predict_wells, save_sample

from .protocol import ModelConfig, TrainConfig


def publish_checkpoints(pressure, temperature, output):
    """只有两个分支预算都完成才发布可独立消费的权重组合。"""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    for branch, value in [("pres", pressure), ("temp", temperature)]:
        if value["status"] != "complete":
            raise ValueError("分支训练未完成")
        path = output / (branch + ".pt")
        shutil.copyfile(value["checkpoint"], path)
        records[branch] = {"file": path.name, "sha256": digest(path), "updates": value["updates"]}
    path = output / "checkpoints.json"
    save_json(path, {"version": 1, "branches": records})
    return str(path)


def load_networks(cfg, preparation, checkpoints, construct):
    """核对固定分支来源、数据和结构后加载，只导入明确指定的权重。"""
    record = read_bundle(preparation, kind="preparation")
    path = Path(checkpoints)
    declared = json.loads(path.read_text())
    if declared.get("version") != 1 or set(declared["branches"]) != {"pres", "temp"}:
        raise ValueError("双分支清单不完整")
    networks = {}
    for branch, item in declared["branches"].items():
        target = path.parent / item["file"]
        if Path(item["file"]).name != item["file"] or digest(target) != item["sha256"]:
            raise ValueError("检查点来源已变化")
        state = torch.load(target, map_location="cpu", weights_only=False)
        if any(not torch.isfinite(v).all() for v in state["model"].values()):
            raise ValueError("检查点含非有限权重，拒绝以nan_to_num掩盖无效模型")
        contract = state["contract"]
        if (
            contract["branch"] != branch
            or contract["data"] != record["sha256"]
            or contract["model"] != cfg["model"]
        ):
            raise ValueError("检查点数据、统计量或模型结构不相容")
        network = construct(
            branch=branch, modes=cfg["model"]["modes"], width=cfg["model"][branch + "_width"]
        )
        network.load_state_dict(state["model"], strict=True)
        networks[branch] = network.to(cfg["infer"]["device"]).eval()
    return networks


def predict_cases(cfg, preparation, networks, *, session):
    """按显式名单预测或回放作者结果；标签仅进入保存后的评价字段。"""
    torch.set_num_threads(cfg["train"]["threads"])
    record = read_bundle(preparation, kind="preparation")
    root = Path(preparation).parent
    source = cfg["infer"]["source"]
    available = [r["id"] for r in record["training" if source == "training24" else "demonstration"]]
    selected = cfg["infer"]["sample_ids"] or available
    if not set(selected) <= set(available):
        raise ValueError("推理名单不属于选定数据集")
    device = cfg["infer"]["device"]
    stats = TrainConfig.stats_to_device(record["statistics"], device)
    output = session.output_dir("infer")
    cache = {}
    author = (
        torch.load(root / "Prob_Pred.pt", map_location="cpu", weights_only=False)
        if source == "author18"
        else None
    )

    def one(sample_id):
        chunk, index = sample_id.split("/")
        index = int(index)
        filename = chunk + ".pt"
        if cache.get("name") != filename:
            cache.clear()
            cache.update(
                name=filename,
                value=torch.load(root / filename, map_location="cpu", weights_only=False),
            )
        sample = {k: v[index : index + 1] for k, v in cache["value"].items()}
        x, g = sample["spatial_params"].to(device), sample["global_params"].to(device)
        if author is not None:
            result = {key: value[index : index + 1] for key, value in author.items()}
            physical = None
        else:
            fields = predict_fields(networks, x, g, stats)
            Pini, Tini, qinj, Tinj, pwf, k, phi, depth, Cp, lam, dz = ModelConfig.decode_inputs(
                x, g, stats
            )
            well, physical = predict_wells(
                fields,
                dict(  # noqa: C408 -- 与物理构造器的具名参数保持直接对应
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
                ),
            )
            result = {"Pres": fields["pres"], "Temp": fields["temp"], **well}
        result.update(spatial_params=x, global_params=g)
        if source == "training24":
            result["truth"] = {
                k: sample[k].to(device) * stats[k + "_std"] + stats[k + "_mean"]
                for k in ["pres", "temp"]
            }
            result["truth"].update({k: sample[k] for k in ["Temp_wh", "Heat_wh", "P_inj"]})
        target = output / (sample_id.replace("/", "_") + ".pt")
        save_sample(target, result)
        return {"id": sample_id, "file": target.name, "sha256": digest(target), "physics": physical}

    results = session.execute_samples(selected, one, stage="infer")
    path = output / "results.json"
    save_json(
        path,
        {
            "version": 1,
            "kind": "results",
            "source": source,
            "statistics": record["statistics"],
            "data_identity": record["sha256"],
            "samples": results,
            "truth_available": source == "training24",
            "units": {
                "Pres": "MPa",
                "Temp": "degC",
                "Twh": "degC",
                "Hwh": "W",
                "Pinj": "Pa",
                "Ewh": "kJ/kg",
                "Qout": "kg/s",
            },
            "field_space": "physical",
            "scope": "training universe, not independent test"
            if source == "training24"
            else "no independent truth",
        },
    )
    session.record_asset(
        "geothermal_results",
        path,
        kind="other",
        stage="infer",
        dependencies=[output / r["file"] for r in results],
        bundle_root=output,
    )
    return str(path)
