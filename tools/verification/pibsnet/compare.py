"""核对物理真值、测试身份和预算后重算指标；缺协议即拒绝比较。"""

import argparse
import json
from pathlib import Path

import torch
import yaml


def validate_objective(config, reference):
    """配点范围及正权重目标必须明确一致；缺证据不得判定同协议。"""
    model = config["model"]
    sampling = model["sampling"]
    if reference.get("pde_points") != "complete_dataset_grid":
        raise ValueError("参考缺少完整 PDE 配点协议")
    if sampling["interior"] != {"method": "all", "include_boundary": True}:
        raise ValueError("PDE 配点协议不同")
    if sampling["supervised"] != {"method": "all"}:
        raise ValueError("监督点协议不同")
    c = model["constraints"]
    actual = {
        "pde": c["equations"]["weight"],
        "data": c["supervision"]["weight"],
        "initial": c["initial_conditions"]["weight"],
        "periodic": c["periodic_boundary_conditions"]["weight"],
    }
    if config["case"] == "neumann_diffusion":
        actual["boundary"] = c["boundary_conditions"]["weight"]
    if reference.get("loss_weights") != actual:
        raise ValueError("损失权重不同或参考缺少目标协议")


def compare(dojo, reference, output):
    """比较 CD 隔离参考和 Dojo 全测试预测，不把结果包装为普遍复现通过。"""
    d = json.loads((dojo / "predictions.json").read_text())
    r = json.loads((reference / "reference.json").read_text())
    checkpoint = torch.load(d["checkpoint"], map_location="cpu", weights_only=False)
    contract = checkpoint["contract"]
    required = ("dataset_id", "epochs", "updates", "seed", "device", "precision", "source_sha256")
    if any(key not in r for key in required):
        raise ValueError("原仓库协议不完整，不可比")
    if d["status"] != "complete" or r["status"] != "complete":
        raise ValueError("存在部分预测，不可比")
    protocol = contract["training"]
    if d["epoch"] != r["epochs"] or checkpoint["updates"] != r["updates"]:
        raise ValueError("训练预算不同，不可作同预算比较")
    if protocol["seed"] != r["seed"] or protocol["precision"] != r["precision"]:
        raise ValueError("随机种子或数值精度不同")
    config = yaml.safe_load(
        (Path(d["checkpoint"]).parent.parent / "inputs/config.yaml").read_text()
    )
    # 运行 writer 的用户快照保存实际路径及计算设备。
    if config != checkpoint["effective_config"]:
        raise ValueError("运行配置与检查点冻结快照不一致")
    if config["train"]["device"] != r["device"]:
        raise ValueError("设备协议不同")
    validate_objective(config, r)
    preparation = json.loads((Path(config["trainprep"]["output"]) / "preparation.json").read_text())
    if preparation["contract"]["data"] != r["dataset_id"]:
        raise ValueError("训练数据身份不同")
    ids = [s["id"] for s in d["samples"]]
    if set(ids) != {s["id"] for s in r["samples"]} or len(ids) != len(set(ids)):
        raise ValueError("测试实例不一致")
    metrics = []
    for sample_id in ids:
        a = torch.load(dojo / f"{sample_id}.pt", weights_only=True)
        b = torch.load(reference / f"{sample_id}.pt", weights_only=True)
        if not torch.equal(a["target"], b["target"]):
            raise ValueError("物理真值不相同")
        truth = a["target"].double()
        if not truth.norm():
            raise ValueError("零真值不适用相对L2比较")
        errors = {
            name: float((bundle["prediction"].double() - truth).norm() / truth.norm())
            for name, bundle in (("dojo", a), ("reference", b))
        }
        metrics.append({"id": sample_id, **errors})
    report = {
        "status": "comparison_complete",
        "case": config["case"],
        "dataset_id": r["dataset_id"],
        "epochs": r["epochs"],
        "updates": r["updates"],
        "precision": r["precision"],
        "reference_execution": r["execution"],
        "pde_points": r["pde_points"],
        "loss_weights": r["loss_weights"],
        "samples": metrics,
        "interpretation": "相同数据和更新预算；Dojo修正物理导数及初边界，CD自由输出600/原576，不主张初始化或轨迹等价。未预设跨案例精度验收阈值。",
    }
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("dojo", "reference", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    args = parser.parse_args()
    compare(args.dojo, args.reference, args.output)
