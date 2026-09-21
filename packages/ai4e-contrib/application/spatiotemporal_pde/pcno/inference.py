"""双圆柱固定权重联合预测连接；未来场只用于输出真值和离线评价。"""

import json
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.application.datasets.gencp.cylinder import read_window
from ai4e_core.abilities.data.save.array_manifest import digest

from .training import construct, contract, load_preparation


def load_networks(cfg, preparation, checkpoints):
    """校验三个最终分支及准备摘要，恢复本次真实构造器。"""
    prepared = load_preparation(preparation)
    record = json.loads(Path(checkpoints).read_text())
    if record.get("kind") != "pcno-cylinder-checkpoints-v1" or record[
        "preparation_sha256"
    ] != digest(preparation):
        raise ValueError("权重清单与准备不一致")
    saved = record["cfg"]
    if cfg["model"] != saved["model"] or cfg["components"] != saved["components"]:
        raise ValueError("推理构造器/结构与权重不相容")
    networks = {}
    for key, branch, arm in (
        ("supervised", "fluid", "supervised"),
        ("physics", "fluid", "physics"),
        ("structure", "structure", "supervised"),
    ):
        entry = record["branches"][key]
        if digest(entry["path"]) != entry["sha256"]:
            raise ValueError("权重内容已变化")
        state = torch.load(entry["path"], map_location="cpu", weights_only=False)
        if (
            state["contract"] != contract(saved, preparation, branch, arm)
            or state["updates"] != saved["train"]["updates"]
        ):
            raise ValueError("最终权重合同或更新预算不相容")
        model = construct(saved, branch)
        model.load_state_dict(state["model"])
        model.eval()
        networks[key] = model
    networks["initial_fluid"] = construct(saved, "fluid").eval()
    networks["initial_structure"] = construct(saved, "structure").eval()
    return prepared, networks, record


def evaluation_records(prepared, split):
    """确定性非重叠目标窗口名单，不根据测试效果选择窗口。"""
    return [
        (trajectory, start)
        for trajectory in prepared["splits"][split]
        for start in prepared["evaluation_starts"]
    ]


def reader(prepared):
    """返回领域窗口读取函数。"""
    return lambda record: read_window(prepared, *record)


def predictor(prepared, networks, provenance):
    """构造联合预测；网络调用仅收到input，不接收physical/target。"""
    mean = np.asarray(prepared["statistics"]["mean"], np.float32)
    scale = np.asarray(prepared["statistics"]["scale"], np.float32)

    def predict(sample):
        history = sample["input"]
        with torch.no_grad():
            structure = networks["structure"](history)[0].numpy() * scale[3:] + mean[3:]
            initial_structure = (
                networks["initial_structure"](history)[0].numpy() * scale[3:] + mean[3:]
            )
            arrays = {"truth": sample["physical"][0].numpy()}
            for key in ("supervised", "physics", "initial"):
                model = networks["initial_fluid"] if key == "initial" else networks[key]
                fluid = model(history)[0].numpy() * scale[:3] + mean[:3]
                arrays[key] = np.concatenate(
                    (fluid, initial_structure if key == "initial" else structure), axis=-1
                )
            last = history[0, -1].numpy() * scale + mean
            arrays["persistence"] = np.broadcast_to(last, arrays["truth"].shape).copy()
        return arrays, {
            "id": sample["id"],
            "start": sample["start"],
            "history": prepared["history"],
            "horizon": prepared["horizon"],
            "interval": prepared["interval"],
            "units": prepared["units"],
            "fields": prepared["fields"],
            "evaluation_geometry": "future reference SDF used only for offline common mask",
            "preparation_sha256": provenance["preparation_sha256"],
            "checkpoint_sha256": {k: v["sha256"] for k, v in provenance["branches"].items()},
        }

    return predict
