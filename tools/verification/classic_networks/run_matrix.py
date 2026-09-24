"""经典网络统一串行校验：公开recipe步骤、独立参考及完整恢复。

本文件是验证调度器，不是第二套Dojo训练器；仅参考侧使用独立Adam循环。
所有记录位于用户指定实验根，失败和重试始终共用预算账本。
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import yaml

from ai4e_contrib.application.classic_networks.binding import FieldModel, batch, construct
from ai4e_contrib.application.classic_networks.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import read_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from tools.verification.classic_networks.budget import BudgetLedger
from tools.verification.classic_networks.protocol import (
    COMBINATIONS,
    configuration_for,
    select_updates,
)

ROOT = Path(__file__).resolve().parents[3]


def synchronize(device):
    """把设备异步计算计入真实耗时。"""
    if str(device) == "mps":
        torch.mps.synchronize()
    elif str(device).startswith("cuda"):
        torch.cuda.synchronize()


def reference_network(cfg, source):
    """独立构造或公式绑定；映射参数不等于复用生产forward。"""
    from tools.verification.classic_networks import reference_features as f
    from tools.verification.classic_networks import reference_spatial as s
    from tools.verification.classic_networks.reference_interactions import reference_model

    m = cfg["model"]
    family = m["family"]
    if family == "mlp":
        reference = f.feed_forward_reference(m["in_channels"], m["out_channels"], **m["parameters"])
        reference.load_state_dict(
            f.feed_forward_weights(source.feed_forward.state_dict()), strict=True
        )
    elif family == "rnn":
        reference = f.RNNReference(m["in_channels"], m["out_channels"], **m["parameters"])
        reference.load_state_dict(
            f.rnn_model_weights(source.state_dict(), num_layers=m["parameters"]["num_layers"]),
            strict=True,
        )
    elif family in {"cnn", "resnet", "unet"}:
        reference = s.build_reference_model(
            family, m["spatial_dims"], m["in_channels"], m["out_channels"], **m["parameters"]
        )
        s.copy_weights(source, reference)
    else:
        # 显式公式另有前后向测试；长FP32轨迹使用独立PyTorch原生算术参考。
        reference = reference_model(
            source, attention_backend="torch_native" if family == "transformer" else "explicit"
        )
    return reference


def execute(cfg, directory, phases):
    """实际调用可复制recipe的公开步骤并保留writer产生的运行记录。"""
    scripts = ROOT / "recipes" / "classic_networks" / cfg["dataset"]["case"]
    sys.path.insert(0, str(scripts))
    # 三案例采用同一组步骤正文，配置case决定局部业务连接。
    stages = {name: getattr(importlib.import_module(name), name) for name in phases}
    effective = copy.deepcopy(cfg)
    effective.update(run_root=str(directory / "runs"), data_root=str(directory / "data"))
    effective["pipeline"]["stages"] = list(phases)
    directory.mkdir(parents=True, exist_ok=True)
    config_path = directory / "config.yaml"
    config_path.write_text(yaml.safe_dump(effective, sort_keys=False))
    outputs = {}

    def pipeline(config):
        trained = None
        results = None
        if "train" in phases:
            trained = outputs["train"] = run.stage("train", stages["train"], config)
        if "infer" in phases:
            results = outputs["infer"] = run.stage("infer", stages["infer"], config, None, trained)
        if "post" in phases:
            outputs["post"] = run.stage("post", stages["post"], config, results)
        return outputs

    try:
        code = run.launch(
            pipeline,
            script=str(scripts / "pipeline.py"),
            config_loader=lambda path, overrides: effective,
            argv=["--config", str(config_path)],
        )
        if code:
            raise RuntimeError(f"公开步骤失败，详见{directory}/runs")
        return outputs
    finally:
        sys.path.remove(str(scripts))


def compare_states(left, right):
    """冻结CPU FP32容差核对全部状态，不放宽以通过。"""
    if len(left) != len(right):
        raise AssertionError("双方状态数不匹配")
    maximum = 0.0
    for (name, x), (ref_name, y) in zip(left.items(), right.items(), strict=True):
        x, y = x.detach().cpu(), y.detach().cpu()
        torch.testing.assert_close(x, y, rtol=1e-5, atol=1e-6, msg=f"{name} / {ref_name}")
        if x.numel():
            maximum = max(maximum, float((x.double() - y.double()).abs().max()))
    return maximum


def _compare_nested(left, right, path, *, exact=False):
    """按键和容器身份递归检查恢复状态；整数、随机状态及配置严格相等。"""
    if isinstance(left, dict):
        if not isinstance(right, dict) or left.keys() != right.keys():
            raise AssertionError(f"{path}: 状态键不匹配")
        return max(
            (
                _compare_nested(value, right[key], f"{path}.{key}", exact=exact)
                for key, value in left.items()
            ),
            default=0.0,
        )
    if isinstance(left, (list, tuple)):
        if type(right) is not type(left) or len(left) != len(right):
            raise AssertionError(f"{path}: 状态序列不匹配")
        return max(
            (
                _compare_nested(x, y, f"{path}[{i}]", exact=exact)
                for i, (x, y) in enumerate(zip(left, right, strict=True))
            ),
            default=0.0,
        )
    if isinstance(left, torch.Tensor):
        if (
            not isinstance(right, torch.Tensor)
            or left.dtype != right.dtype
            or left.shape != right.shape
        ):
            raise AssertionError(f"{path}: 张量形状或精度不一致")
        x, y = left.detach().cpu(), right.detach().cpu()
        strict = exact or not x.is_floating_point() or path.endswith(".step")
        torch.testing.assert_close(
            x, y, rtol=0 if strict else 1e-5, atol=0 if strict else 1e-6, msg=path
        )
        return float((x.double() - y.double()).abs().max()) if x.numel() else 0.0
    if isinstance(left, np.ndarray):
        if (
            not isinstance(right, np.ndarray)
            or left.dtype != right.dtype
            or left.shape != right.shape
        ):
            raise AssertionError(f"{path}: 数组形状或精度不一致")
        if exact or not np.issubdtype(left.dtype, np.floating):
            np.testing.assert_array_equal(left, right, err_msg=path)
        else:
            np.testing.assert_allclose(
                left, right, rtol=1e-5, atol=1e-6, equal_nan=False, err_msg=path
            )
        return (
            float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64))))
            if left.size
            else 0.0
        )
    if type(left) is not type(right):
        raise AssertionError(f"{path}: 状态类型不一致")
    if isinstance(left, float) and not exact:
        np.testing.assert_allclose(left, right, rtol=1e-5, atol=1e-6, equal_nan=False, err_msg=path)
        return 0.0 if left == right else abs(left - right)
    if left != right:
        raise AssertionError(f"{path}: 状态值不一致")
    return 0.0


def compare_checkpoints(left, right):
    """比较实际迭代检查点全部可恢复状态，执行路径元数据单独明确排除。"""
    required = {
        "version",
        "model",
        "optimizer",
        "epoch",
        "updates",
        "best",
        "contract",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "cuda_rng",
        "mps_rng",
        "ema",
        "scaler",
        "scheduler",
        "loop_kind",
        "stream",
        "history",
        "algorithm_state",
        "status",
    }
    if not required <= left.keys() or not required <= right.keys():
        raise AssertionError("完整恢复检查点缺少必需状态")
    ignored = {"effective_config"}
    if left.keys() - ignored != right.keys() - ignored:
        raise AssertionError("完整检查点状态集合不一致")
    components = {}
    for name in sorted(left.keys() - ignored):
        # 浮点模型/优化器矩/损失容差固定；RNG、stream、contract、超参数等严格相等。
        exact = name not in {"model", "optimizer", "history", "ema"}
        if name == "optimizer":
            _compare_nested(
                left[name]["param_groups"],
                right[name]["param_groups"],
                "optimizer.param_groups",
                exact=True,
            )
        components[name] = _compare_nested(left[name], right[name], name, exact=exact)
    return {
        "maximum_difference": max(components.values(), default=0.0),
        "components": components,
        "ignored_execution_metadata": sorted(ignored),
        "contract_compared_exactly": True,
    }


def reference_test_predictions(model, cfg, arrays, record, device):
    """独立遍历全部test，经原统计反变换和有效域处理；不调用生产预测函数。"""
    modes = {module: module.training for module in model.modules()}
    states = (random.getstate(), np.random.get_state(), torch.get_rng_state())
    cuda_rng = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
    mps_rng = torch.mps.get_rng_state() if torch.backends.mps.is_available() else None
    values = []
    try:
        model.eval()
        with torch.no_grad():
            for index in range(len(arrays["target"])):
                item = batch(
                    arrays,
                    [index],
                    device=device,
                    case=cfg["dataset"]["case"],
                    sample_points=None,
                    point_sequence=cfg["model"]["family"] == "rnn",
                )
                prediction = model(item["input"], item["valid"], item.get("coordinates"))
                values.append(prediction.detach().cpu())
        result = torch.cat(values).numpy().reshape(arrays["target"].shape)
        stats = record["metadata"]["statistics"]["target"]
        result = result * np.asarray(stats["scale"]) + np.asarray(stats["mean"])
        result[~np.asarray(arrays["valid"], bool)] = 0
        return result.astype(np.float32)
    finally:
        for module, mode in modes.items():
            module.training = mode
        random.setstate(states[0])
        np.random.set_state(states[1])
        torch.set_rng_state(states[2])
        if cuda_rng is not None:
            torch.cuda.set_rng_state_all(cuda_rng)
        if mps_rng is not None:
            torch.mps.set_rng_state(mps_rng)


def compare_reference_predictions(reference, cfg, prepared, fixed_results, output, device):
    """读回两侧完整test身份和固定结果，先保存差异证据再执行固定容差门禁。"""
    record, arrays = read_prepared(prepared, "test")
    result_record, fixed = read_arrays(fixed_results, kind="classic-results-v1")
    for key in ("case", "ids", "fields", "units", "statistics"):
        _compare_nested(
            record["metadata"][key], result_record["metadata"][key], f"prediction.{key}", exact=True
        )
    for name, original in (
        ("valid", "valid"),
        ("entity_ids", "entity_ids"),
        ("target", "physical_target"),
        ("physical_input", "physical_input"),
    ):
        np.testing.assert_array_equal(fixed[name], arrays[original], err_msg=f"prediction.{name}")
    if "times" in arrays:
        np.testing.assert_array_equal(fixed["times"], arrays["times"], err_msg="prediction.times")
    predicted = reference_test_predictions(reference, cfg, arrays, record, device)
    synchronize(device)
    if predicted.shape != fixed["prediction"].shape:
        raise AssertionError("独立参考与固定预测的完整形状不一致")
    difference = np.abs(predicted.astype(np.float64) - np.asarray(fixed["prediction"], np.float64))
    mask = np.asarray(arrays["valid"], bool)
    if not mask.any():
        raise AssertionError("test没有有效评价点")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    np.savez(
        output / "reference-prediction.npz",
        prediction=predicted,
        valid=mask,
        entity_ids=arrays["entity_ids"],
    )
    report = {
        "samples": len(predicted),
        "shape": list(predicted.shape),
        "valid_points": int(mask.sum()),
        "maximum_difference": float(difference.max()),
        "valid_maximum_difference": float(difference[mask].max()),
        "per_sample_maximum_difference": [float(item.max()) for item in difference],
        "rtol": 1e-5,
        "atol": 1e-6,
        "scope": "complete test, physical space and identical valid domain",
        "prediction": str(output / "reference-prediction.npz"),
    }
    save_json(output / "comparison.json", report)
    np.testing.assert_allclose(
        predicted, fixed["prediction"], rtol=1e-5, atol=1e-6, equal_nan=False
    )
    return report


def train_reference(cfg, initial_path, prepared, updates, device):
    """参考侧独立优化器循环；不调用Dojo objective、update或训练循环。"""
    initial = torch.load(initial_path, map_location="cpu", weights_only=False)
    source = construct(cfg)
    source.load_state_dict(initial["model"], strict=True)
    network = reference_network(cfg, source.network).to(device)
    model = FieldModel(network, cfg["model"]["family"], cfg["model"]["spatial_dims"]).to(device)
    _, arrays = read_prepared(prepared, "train")
    # 独立重建IterationStream的种子排列/尾批；batch1无丢尾歧义。
    rng = torch.Generator().manual_seed(cfg["seed"])
    order, cursor = [], 0
    torch.set_rng_state(initial["rng"])
    if str(device) == "mps":
        torch.mps.set_rng_state(initial["mps_rng"])
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["train"]["lr"])
    history = []
    model.train()
    start = time.monotonic()
    for _ in range(updates):
        if cursor == len(order):
            order = torch.randperm(len(arrays["target"]), generator=rng).tolist()
            cursor = 0
        sample = [order[cursor]]
        cursor += 1
        values = batch(
            arrays,
            sample,
            device=device,
            case=cfg["dataset"]["case"],
            sample_points=cfg["train"]["sample_points"],
            point_sequence=cfg["model"]["family"] == "rnn",
        )
        optimizer.zero_grad()
        prediction = model(values["input"], values["valid"], values.get("coordinates"))
        loss = ((prediction - values["target"])[values["valid"]] ** 2).mean()
        if not torch.isfinite(loss):
            raise FloatingPointError("参考损失非有限")
        loss.backward()
        if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
            raise FloatingPointError("参考梯度非有限")
        optimizer.step()
        history.append(float(loss.detach()))
    synchronize(device)
    return model, history, time.monotonic() - start


def verify_combination(cfg, identity, paths, root, ledger, device):
    """先测速，再恢复初始条件执行完整两侧/恢复/固定结果检查。"""
    prepared = paths["prepared"]
    cfg["inputs"]["train"]["preparation"] = prepared
    cfg["inputs"]["infer"]["preparation"] = prepared
    cfg["train"]["device"] = cfg["infer"]["device"] = device
    target = root / identity / f"attempt-{time.time_ns()}"
    target.mkdir(parents=True)
    with ledger.measure(identity, "calibration-dojo", training=True):
        cfg["train"]["updates"] = 20
        cfg["train"]["seconds"] = min(9000, ledger.remaining(identity) - 5)
        start = time.monotonic()
        calibration = execute(cfg, target / "calibration", ("train",))
        synchronize(device)
        dojo_seconds = time.monotonic() - start
    with ledger.measure(identity, "calibration-reference", training=True):
        reference, _, reference_seconds = train_reference(
            cfg, calibration["train"]["initial"], prepared, 20, device
        )
        del reference
    estimate = select_updates(
        dojo_seconds / 20,
        reference_seconds / 20,
        available_seconds=ledger.remaining(identity),
        spent_seconds=10800 - ledger.remaining(identity),
        recovery_factor=1.0,
        fixed_seconds=120,
    )
    save_json(target / "estimate.json", estimate)
    print(
        f"BUDGET {identity}: {estimate['updates']} updates; estimate={estimate['estimated_seconds']:.1f}s; used={10800 - ledger.remaining(identity):.1f}s",
        flush=True,
    )
    cfg["train"]["updates"] = estimate["updates"]
    with ledger.measure(identity, "dojo-train-infer-post", training=True):
        cfg["train"]["seconds"] = min(9000, ledger.remaining(identity) - 5)
        outputs = execute(cfg, target / "dojo", ("train", "infer", "post"))
        synchronize(device)
    with ledger.measure(identity, "checkpoint-update-verification"):
        final = torch.load(outputs["train"]["checkpoint"], map_location="cpu", weights_only=False)
        initial = torch.load(outputs["train"]["initial"], map_location="cpu", weights_only=False)
        if final["updates"] != estimate["updates"] or final["status"] != "complete":
            raise AssertionError("训练未达到冻结的更新预算")
        if not any(
            not torch.equal(initial["model"][k], v)
            for k, v in final["model"].items()
            if v.is_floating_point()
        ):
            raise AssertionError("权重未有效更新")
    with ledger.measure(identity, "reference-train", training=True):
        reference, history, duration = train_reference(
            cfg, outputs["train"]["initial"], prepared, estimate["updates"], device
        )
        # 不同参考模块树使用严格参数顺序映射，交互类保持同键。
        max_difference = compare_states(final["model"], reference.state_dict())
        np.testing.assert_allclose(outputs["train"]["history"], history, rtol=1e-5, atol=1e-6)
        torch.save({"model": reference.state_dict(), "history": history}, target / "reference.pt")
    with ledger.measure(identity, "reference-complete-test-verification"):
        prediction_comparison = compare_reference_predictions(
            reference, cfg, prepared, outputs["infer"], target / "reference-test", device
        )
        del reference
    with ledger.measure(identity, "resume", training=True):
        split_cfg = copy.deepcopy(cfg)
        split_cfg["train"]["updates"] = min(20, max(1, estimate["updates"] // 2))
        split_cfg["train"]["seconds"] = min(9000, ledger.remaining(identity) - 5)
        part = execute(split_cfg, target / "split", ("train",))
        resume_cfg = copy.deepcopy(cfg)
        resume_cfg["inputs"]["train"]["resume"] = part["train"]["checkpoint"]
        resume_cfg["train"]["seconds"] = min(9000, ledger.remaining(identity) - 5)
        resumed = execute(resume_cfg, target / "resumed", ("train", "infer", "post"))
        restored = torch.load(
            resumed["train"]["checkpoint"], map_location="cpu", weights_only=False
        )
        recovery_comparison = compare_checkpoints(final, restored)
        recovery_difference = recovery_comparison["components"]["model"]
        save_json(target / "recovery-comparison.json", recovery_comparison)
        _, p = read_arrays(outputs["infer"], kind="classic-results-v1")
        _, r = read_arrays(resumed["infer"], kind="classic-results-v1")
        for key in ("valid", "entity_ids", "target"):
            np.testing.assert_array_equal(p[key], r[key], err_msg=f"resume.{key}")
        np.testing.assert_allclose(
            p["prediction"], r["prediction"], rtol=1e-5, atol=1e-6, equal_nan=False
        )
        synchronize(device)
    report = {
        "status": "passed",
        "identity": identity,
        "device": device,
        "updates": estimate["updates"],
        "reference_max_difference": max_difference,
        "recovery_max_difference": recovery_difference,
        "recovery_state_comparison": recovery_comparison,
        "reference_prediction_comparison": prediction_comparison,
        "estimate": estimate,
        "outputs": outputs,
        "resumed": resumed,
        "reference_seconds": duration,
        "used_seconds": 10800 - ledger.remaining(identity),
        "scope": "small-data structural integration, not paper accuracy",
    }
    with ledger.measure(identity, "verification-report-save"):
        save_json(target / "report.json", report)
    report["used_seconds"] = 10800 - ledger.remaining(identity)
    return report


def main():
    """统一队列，失败不删除账本；已通过组合不重复训练。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    torch.set_num_threads(2)
    preparation = json.loads((args.root / "evidence/preparation.json").read_text())
    ledger = BudgetLedger(args.root / "budget")
    summary_path = args.root / "evidence/matrix.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    for case, family in COMBINATIONS:
        identity = family + "-" + case
        if args.only and identity not in args.only:
            continue
        if summary.get(identity, {}).get("status") == "passed":
            continue
        try:
            report = verify_combination(
                configuration_for(case, family),
                identity,
                preparation[case],
                args.root / "matrix",
                ledger,
                args.device,
            )
            summary[identity] = report
        except Exception as exc:
            summary[identity] = {
                "status": "failed",
                "error": repr(exc),
                "used_seconds": 10800 - ledger.remaining(identity),
            }
            save_json(summary_path, summary)
            raise
        save_json(summary_path, summary)
        print(f"COMPLETE {identity}: {report['used_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
