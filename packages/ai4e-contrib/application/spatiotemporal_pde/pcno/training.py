"""PCNO圆柱配对训练连接；更新循环、状态和记录复用core。"""

import copy
import json
import random
import time
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.application.datasets.gencp.cylinder import read_window
from ai4e_contrib.application.geothermal.pcno.training import component_identity
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream
from ai4e_core.applications.base.iteration_training import train_model

from .configuration import component
from .objective import objective


def load_preparation(path):
    """仅接受已准入双圆柱准备，验证原始来源未改变。"""
    prepared = json.loads(Path(path).read_text())
    if (
        prepared.get("kind") != "pcno-cylinder-prepared-v1"
        or prepared.get("admission") != "double-cylinder-source-staggered-20260921"
    ):
        raise ValueError("圆柱数据或物理约束尚未准入")
    for items in prepared["splits"].values():
        for item in items:
            if digest(item["path"]) != item["sha256"]:
                raise ValueError("准备引用的原始数据已变化")
    return prepared


def construct(cfg, branch):
    """固定模型随机性，显式使用用户选择的构造器。"""
    random.seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    torch.set_num_threads(cfg["train"]["threads"])
    return component(cfg["components"]["network"])(
        case=cfg["dataset"]["case"], branch=branch, **cfg["model"]
    )


def contract(cfg, preparation, branch, arm):
    """冻结影响恢复的科学参数及组件源码身份。"""
    return {
        "format": "pcno-cylinder-v1",
        "preparation": digest(preparation),
        "branch": branch,
        "arm": arm,
        "model": cfg["model"],
        "train": cfg["train"],
        "loss": cfg["loss"],
        "seed": cfg["seed"],
        "network": component_identity(component(cfg["components"]["network"])),
    }


def train_branch(
    cfg, preparation, branch, arm, *, session, resume=None, stop_after=None, cancelled=None
):
    """执行一个明确分支；stop_after用于测量/中断证据，不修改科学预算。"""
    if arm not in ("warmup", "supervised", "physics") or branch not in ("fluid", "structure"):
        raise ValueError("分支或对照身份非法")
    prepared = load_preparation(preparation)
    if any(prepared[k] != cfg["model"][k] for k in ("history", "horizon")):
        raise ValueError("准备窗口与网络配置不一致")
    model = construct(cfg, branch)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["train"]["learning_rate"])
    starts = prepared["train_starts"]
    stream = CountedIterationStream(
        len(starts) * len(prepared["splits"]["train"]), 1, seed=cfg["seed"]
    )
    target = objective(prepared, cfg, branch, arm)

    def batch(ids):
        index = int(ids[0])
        sample = prepared["splits"]["train"][index // len(starts)]
        item = read_window(prepared, sample, starts[index % len(starts)])
        item["update"] = stream.updates
        return item

    def finite(gradient):
        if not torch.isfinite(gradient).all():
            raise FloatingPointError("圆柱模型梯度非有限，未执行更新")
        return gradient

    for parameter in model.parameters():
        parameter.register_hook(finite)
    namespace = branch + "_" + arm
    start = time.monotonic()

    def evaluate(index, current):
        session.report(
            {"updates": index, "parts": target.last, "seconds": time.monotonic() - start},
            stage=namespace + "_loss",
        )

    target_updates = cfg["train"]["updates"] if stop_after is None else stop_after
    if not 0 <= target_updates <= cfg["train"]["updates"]:
        raise ValueError("阶段更新目标非法")
    result = train_model(
        model,
        optimizer,
        stream,
        batch,
        target,
        updates=target_updates,
        session=session,
        contract=contract(cfg, preparation, branch, arm),
        namespace=namespace,
        resume=resume,
        evaluate=evaluate,
        evaluate_every=50,
        max_grad_norm=1.0,
        cancelled=cancelled,
    )
    result.update(seconds=time.monotonic() - start, branch=branch, arm=arm)
    session.report({k: v for k, v in result.items() if k != "history"}, stage=namespace)
    return result


def fork_warmup(cfg, preparation, warmup, arm, session):
    """显式从共同预热分叉；仅在物理/梯度权重为零的预热边界允许。"""
    state = torch.load(warmup["checkpoint"], map_location="cpu", weights_only=False)
    expected = contract(cfg, preparation, "fluid", "warmup")
    if (
        state["contract"] != expected
        or state["updates"] != int(cfg["train"]["updates"] * cfg["loss"]["warmup_fraction"])
        or arm not in ("supervised", "physics")
    ):
        raise ValueError("只能从同合同的共同预热边界分叉")
    state = copy.deepcopy(state)
    state["contract"] = contract(cfg, preparation, "fluid", arm)
    state["forked_from"] = {"sha256": digest(warmup["checkpoint"]), "updates": state["updates"]}
    return str(session.checkpoint("last", state, namespace="fluid_" + arm + "_seed"))


def publish_checkpoints(cfg, preparation, branches, output):
    """交付检查点引用和摘要，不复制大权重。"""
    for name, result in branches.items():
        if result["updates"] != cfg["train"]["updates"] or result["status"] != "complete":
            raise ValueError("不能发布未完成分支: " + name)
    record = {
        "kind": "pcno-cylinder-checkpoints-v1",
        "cfg": cfg,
        "preparation_sha256": digest(preparation),
        "branches": {
            name: {
                "path": r["checkpoint"],
                "sha256": digest(r["checkpoint"]),
                "updates": r["updates"],
            }
            for name, r in branches.items()
        },
    }
    save_json(output, record)
    return str(Path(output).resolve())


def tracked_session(session, preparation, resume=None):
    """用公开checkpoint接口登记可恢复分支清单，记录仍由writer独占。"""
    from types import SimpleNamespace

    root = session.output_dir("train")
    ledger = (
        json.loads(Path(resume).read_text())
        if resume
        else {"preparation": digest(preparation), "branches": {}}
    )
    if ledger["preparation"] != digest(preparation):
        raise ValueError("恢复清单与准备不一致")

    def checkpoint(label, payload, *, namespace=None):
        path = session.checkpoint(label, payload, namespace=namespace)
        if label == "latest":
            ledger["branches"][namespace] = {
                "path": str(path),
                "sha256": digest(path),
                "updates": payload["updates"],
            }
            save_json(root / "resume.json", ledger)
        return path

    def lookup(namespace):
        entry = ledger["branches"].get(namespace)
        if entry and digest(entry["path"]) != entry["sha256"]:
            raise ValueError("恢复权重内容变化")
        return entry["path"] if entry else None

    proxy = SimpleNamespace(checkpoint=checkpoint, report=session.report)
    return proxy, lookup
