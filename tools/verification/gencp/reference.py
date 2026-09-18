"""锁定原仓库定义的独立参考入口；不导入 Dojo 数值能力。"""

import argparse
import ast
import hashlib
import json
import sys
import time
from collections import OrderedDict
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from typing import Union

import numpy as np
import torch
import yaml


def definitions(path, names, namespace, *, repair=False):
    """提取原函数/类，保留函数正文；仅修复已确认的缺失 print 语法。"""
    text = Path(path).read_text()
    if repair:
        text = text.replace(
            '                                      f"vt_joint shape:',
            '                                print(f"vt_joint shape:',
        )
    tree = ast.parse(text)
    nodes = [node for node in tree.body if getattr(node, "name", None) in names]
    if {node.name for node in nodes} != set(names):
        raise ValueError(f"原定义缺失: {path}")
    exec(compile(ast.Module(nodes, type_ignores=[]), str(path), "exec"), namespace)  # noqa: S102 - 已核验原仓库的独立定义


def load_reference(source):
    """装载原模型、CFM、目标和训练单步，避免未使用 FNO 导入阻断。"""
    source = Path(source).resolve()
    lock = (
        Path(__file__).resolve().parents[3]
        / "packages/ai4e-contrib/ability/model/gencp/source.json"
    )
    if lock.exists():
        for name, expected in json.loads(lock.read_text())["sha256"].items():
            if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"参考源码漂移: {name}")
    sys.path.insert(0, str(source))
    from model.cno import CNO3d
    from model.SiT_FNO import SiT_FNO

    ns = {
        "torch": torch,
        "np": np,
        "OrderedDict": OrderedDict,
        "Union": Union,
        "List": list,
        "Sequence": Sequence,
        "Tuple": tuple,
        "tqdm": lambda iterable, **kwargs: iterable,
    }
    definitions(
        source / "torchcfm/conditional_flow_matching.py",
        ["pad_t_like_x", "ConditionalFlowMatcher"],
        ns,
    )
    definitions(source / "utils/utils.py", ["mse_loss", "rel_l2_loss", "loss_with_mask"], ns)
    definitions(source / "train.py", ["update_ema"], ns)
    tree = ast.parse((source / "train.py").read_text())
    trainer = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    for name in ("train_step", "sample"):
        node = next(n for n in trainer.body if getattr(n, "name", None) == name)
        exec(compile(ast.Module([node], type_ignores=[]), str(source / "train.py"), "exec"), ns)  # noqa: S102 - SHA256 锁定的参考函数
    ns["torchcfm"] = SimpleNamespace(ConditionalFlowMatcher=ns["ConditionalFlowMatcher"])
    definitions(
        source / "infer_multi_ntcouple.py",
        [
            "update_neutron_condition",
            "update_solid_condition",
            "update_fluid_condition",
            "default_ntcouple_updates",
            "compose_flow_ntcouple",
        ],
        ns,
        repair=True,
    )
    definitions(source / "infer_multi.py", ["create_couple_step_fn_fsi"], ns)
    ns.update(CNO3d=CNO3d, SiT_FNO=SiT_FNO)
    return ns


def construct(ns, dataset, backbone, field):
    """缩小实验的原类构造参数；不更改空间/时间尺寸。"""
    nt = dataset == "ntcouple"
    width = {"neutron": 20, "solid": 8, "fluid": 12}[field] if nt else None
    shape = (64, width) if nt else ((128, 128) if dataset == "double_cylinder" else (108, 88))
    output = {"neutron": 1, "solid": 1, "fluid": 4}[field] if nt else (3 if field == "fluid" else 1)
    channels = {"neutron": 3, "solid": 4, "fluid": 5}[field] if nt else 4
    dataset_name = dataset if nt else dataset + "_data"
    common = {"dataset_name": dataset_name, "stage": field, "x0_is_use_noise": True}
    if backbone == "cno":
        return ns["CNO3d"](
            in_dim=channels,
            out_dim=output,
            in_size=shape[0],
            N_layers=2,
            channel_multiplier=4,
            N_res_neck=1,
            latent_lift_proj_dim=16,
            **common,
        )
    patch = (4, 2) if nt else ((8, 8) if dataset == "double_cylinder" else (6, 8))
    return ns["SiT_FNO"](
        input_size=shape,
        patch_size=patch,
        in_channels=channels,
        out_channels=output,
        hidden_size=64,
        depth=2,
        num_heads=4,
        modes=4,
        **common,
    )


def nt_dataset(source, root, field, split):
    """原读取器只补齐下载包实际 split 白名单；数值正文未改。"""
    sys.path.insert(0, str(source))
    from data.ntcouple_dataset import NTcoupleDataset

    NTcoupleDataset._DECOUPLED_SPLITS |= {"decouple_train", "decouple_val"}
    return NTcoupleDataset(field=field, split=split, data_root=Path(root))


def train_nt(args):
    """独立参考真实缩小训练；输出权重、初值、采样与逐更新损失。"""
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    torch.set_num_threads(8)
    ns = load_reference(args.source)
    models, shapes, truths, conditions = [], [], [], []
    report = {"scope": "scaled_reference_not_paper", "fields": {}, "seed": 42}
    for field in ("neutron", "solid", "fluid"):
        dataset = nt_dataset(args.source, args.data, field, "decouple_train")
        ids = np.random.default_rng(42).choice(len(dataset), 256, replace=False)
        inputs, targets = dataset.cond[ids], dataset.target[ids]
        del dataset
        torch.manual_seed(42)
        model = construct(ns, "ntcouple", args.backbone, field).to(args.device)
        initial = deepcopy(model.state_dict())
        settings = yaml.safe_load(
            (
                Path(args.source)
                / f"configs/ntcouple/{field}_{'cno' if args.backbone == 'cno' else 'sit_fno'}.yaml"
            ).read_text()
        )
        settings.update(log_every=100, is_use_tb=False)
        optimizer = torch.optim.Adam(model.parameters(), lr=settings["lr"], betas=(0.9, 0.99))
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, args.updates, eta_min=1e-7
        )
        trainer = SimpleNamespace(
            model=model,
            optimizer=optimizer,
            ema=deepcopy(model).eval(),
            use_accelerator=False,
            args=SimpleNamespace(**settings),
            writer=None,
            train_steps=0,
            device=args.device,
            data_normalizer=SimpleNamespace(preprocess=lambda x, y: (x, y)),
            cfm=ns["ConditionalFlowMatcher"](sigma=settings["sigma"]),
            log_info=lambda msg, field=field: print(field, msg, flush=True),
        )
        history, orders = [], []
        generator = torch.Generator().manual_seed(42)
        for step in range(args.updates):
            if step % 128 == 0:
                order = torch.randperm(256, generator=generator)
                orders.append(order.tolist())
            batch = order[(step % 128) * 2 : (step % 128) * 2 + 2]
            trainer.train_steps = step
            loss, _ = ns["train_step"](
                trainer, inputs[batch].to(args.device), targets[batch].to(args.device), {}
            )
            if not np.isfinite(loss):
                raise ValueError(f"非有限训练: {field}/{step}")
            history.append(loss)
            scheduler.step()
            if time.monotonic() - start > 10500:
                raise TimeoutError("本组合计算预算耗尽")
        torch.save(
            {
                "model": model.state_dict(),
                "initial": initial,
                "ema": trainer.ema.state_dict(),
                "history": history,
                "ids": ids.tolist(),
                "orders": orders,
                "settings": settings,
                "updates": args.updates,
            },
            output / f"{field}.pt",
        )
        report["fields"][field] = {
            "initial_loss": history[0],
            "final_loss": history[-1],
            "updates": args.updates,
        }
        model.eval()
        validation = nt_dataset(args.source, args.data, field, "decouple_val")
        vx = validation.cond[:16].permute(0, 2, 3, 4, 1).to(args.device)
        vy = validation.target[:16].permute(0, 2, 3, 4, 1).to(args.device)
        torch.manual_seed(43)
        with torch.no_grad():
            prediction = ns["sample"](
                trainer,
                torch.randn_like(torch.cat((vx, vy), dim=-1)),
                vy,
                {"x0": vx, "cond": {}},
                model,
            )
        torch.save(
            {"prediction": prediction.cpu(), "target": vy.cpu(), "inputs": vx.cpu()},
            output / f"{field}_single.pt",
        )
        del validation
        models.append(model)
        dataset = nt_dataset(args.source, args.data, field, "couple_val")
        conditions.append(dataset.cond[:16].permute(0, 2, 3, 4, 1).to(args.device))
        truths.append(dataset.target[:16].permute(0, 2, 3, 4, 1).to(args.device))
        shapes.append(tuple(truths[-1].shape))
        del dataset, inputs, targets, trainer, optimizer
    torch.manual_seed(43)
    boundary = [conditions[0][:, :, :, 0:1, 1:2], truths[1][:, :, :, 0:1, :]]
    predictions = ns["compose_flow_ntcouple"](
        models,
        shapes,
        ns["default_ntcouple_updates"](),
        None,
        None,
        timestep=100,
        other_condition=boundary,
        device=args.device,
        use_bc_inpainting=True,
    )
    torch.save(
        {
            "predictions": [p.cpu() for p in predictions],
            "targets": [t.cpu() for t in truths],
            "conditions": [c.cpu() for c in conditions],
        },
        output / "coupled.pt",
    )
    report["data_root"] = str(Path(args.data).resolve())
    report["source_root"] = str(Path(args.source).resolve())
    report["seconds"] = time.monotonic() - start
    (output / "reference.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


def train_fsi(args):
    """原 FSI 读取、归一化、训练单步及同步耦合，在缩小网络上运行。"""
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    torch.set_num_threads(8)
    ns = load_reference(args.source)
    from data.data_normalizer import RangeNormalizer
    from data.double_cylinder_dataset import DoubleCylinderDataset
    from data.turek_hron_dataset import TurekHronDataset

    dataset_type = TurekHronDataset if args.dataset == "turek_hron" else DoubleCylinderDataset
    common = {
        "dataset_path": str(args.data),
        "length": 999,
        "input_size": 3,
        "output_size": 12,
        "stride": 1,
        "num_delta_t": 0,
        "dt": 5 if args.dataset == "turek_hron" else 10,
    }
    models, report = [], {"scope": "scaled_reference_not_paper", "fields": {}}
    for field in ("fluid", "structure"):
        dataset = dataset_type(**common, mode="train", stage=field)
        normalizer = RangeNormalizer(dataset, device=args.device)
        ids = np.random.default_rng(42).choice(len(dataset), 256, replace=False)
        samples = [dataset[int(i)] for i in ids]
        inputs = torch.stack([s[0] for s in samples])
        targets = torch.stack([s[1] for s in samples])
        del samples
        torch.manual_seed(42)
        model = construct(ns, args.dataset, args.backbone, field).to(args.device)
        initial = deepcopy(model.state_dict())
        settings = yaml.safe_load(
            (Path(args.source) / f"configs/{args.dataset}/{field}_{args.backbone}.yaml").read_text()
        )
        settings.update(log_every=100, is_use_tb=False)
        optimizer = torch.optim.Adam(model.parameters(), lr=settings["lr"])
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.updates)
        trainer = SimpleNamespace(
            model=model,
            optimizer=optimizer,
            ema=deepcopy(model).eval(),
            use_accelerator=False,
            args=SimpleNamespace(**settings),
            writer=None,
            train_steps=0,
            device=args.device,
            data_normalizer=normalizer,
            cfm=ns["ConditionalFlowMatcher"](sigma=settings["sigma"]),
            log_info=lambda msg, field=field: print(field, msg, flush=True),
        )
        history, orders = [], []
        generator = torch.Generator().manual_seed(42)
        for step in range(args.updates):
            if step % 128 == 0:
                order = torch.randperm(256, generator=generator)
                orders.append(order.tolist())
            batch = order[(step % 128) * 2 : (step % 128) * 2 + 2]
            trainer.train_steps = step
            loss, _ = ns["train_step"](
                trainer, inputs[batch].to(args.device), targets[batch].to(args.device), {}
            )
            if not np.isfinite(loss):
                raise ValueError(f"非有限训练 {field}/{step}")
            history.append(loss)
            scheduler.step()
            if time.monotonic() - start > 10500:
                raise TimeoutError("计算预算耗尽")
        torch.save(
            {
                "model": model.state_dict(),
                "initial": initial,
                "ema": trainer.ema.state_dict(),
                "history": history,
                "ids": ids.tolist(),
                "orders": orders,
                "settings": settings,
                "updates": args.updates,
            },
            output / f"{field}.pt",
        )
        model.eval()
        models.append(model)
        report["fields"][field] = {
            "initial_loss": history[0],
            "final_loss": history[-1],
            "updates": args.updates,
        }
        valid = dataset_type(**common, mode="val", stage=field)
        valid_ids = np.linspace(0, len(valid) - 1, 16, dtype=int)
        samples = [valid[int(i)] for i in valid_ids]
        vx, vy = (
            torch.stack([s[0] for s in samples]).to(args.device),
            torch.stack([s[1] for s in samples]).to(args.device),
        )
        nx, ny = normalizer.preprocess(vx, vy)
        torch.manual_seed(43)
        with torch.no_grad():
            pred = ns["sample"](trainer, torch.randn_like(ny), ny, {"x0": nx, "cond": {}}, model)
        torch.save(
            {
                "prediction": pred.cpu(),
                "target": ny.cpu(),
                "inputs": nx.cpu(),
                "ids": valid_ids.tolist(),
            },
            output / f"{field}_single.pt",
        )
        del inputs, targets, trainer, optimizer, samples
    dataset = dataset_type(**common, mode="val", stage="couple")
    normalizer = RangeNormalizer(dataset, device=args.device)
    ids = np.linspace(0, len(dataset) - 1, 16, dtype=int)
    samples = [dataset[int(i)] for i in ids]
    x, y = (
        torch.stack([s[0] for s in samples]).to(args.device),
        torch.stack([s[1] for s in samples]).to(args.device),
    )
    nx, ny = normalizer.preprocess(x, y)
    torch.manual_seed(43)
    state = torch.randn_like(ny)
    initial = state.clone()
    step_fn = ns["create_couple_step_fn_fsi"](*models, args.device, flag="jacobi")
    with torch.no_grad():
        for step in range(10):
            state = step_fn(state, step / 10, 0.1, initial, x0=nx, gt=ny, cond={})
    _, physical = normalizer.postprocess(state, state)
    torch.save(
        {
            "prediction": state.cpu(),
            "physical_prediction": physical.cpu(),
            "target": y.cpu(),
            "inputs": nx.cpu(),
            "ids": ids.tolist(),
        },
        output / "coupled.pt",
    )
    report["data_root"] = str(Path(args.data).resolve())
    report["source_root"] = str(Path(args.source).resolve())
    report["seconds"] = time.monotonic() - start
    (output / "reference.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--backbone", choices=["cno", "sit_fno"], default="sit_fno")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--updates", type=int, default=1000)
    parser.add_argument(
        "--dataset", choices=["ntcouple", "double_cylinder", "turek_hron"], default="ntcouple"
    )
    args = parser.parse_args()
    (train_nt if args.dataset == "ntcouple" else train_fsi)(args)
