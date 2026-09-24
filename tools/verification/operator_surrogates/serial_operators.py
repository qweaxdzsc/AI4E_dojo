"""算子网络的串行核对入口；生产训练实际调用公开 recipe 和 train_model。

只在显式 run_combo/CLI 调用时训练。两侧共享冻结准备和初始权重，参考侧
独立实现布局、取批、Adam 和目标；上游算术及其范围见 reference_operators。
本工具不调度并行，也不拥有总预算账本，主控须将重试/扩展传入同一 deadline。
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import yaml
from torch import nn

from ai4e_contrib.application.operator_learning.binding import batch, construct
from ai4e_contrib.application.operator_learning.configuration import validate
from ai4e_contrib.application.operator_learning.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.inference.randomness import seeded_randomness
from ai4e_core.abilities.training.optimization import resolve_device
from tools.verification.operator_surrogates.reference_operators import (
    DeepONetReference,
    FNOReference,
    copy_deeponet_weights,
    copy_fno_weights,
    load_sources,
)

ROOT = Path(__file__).resolve().parents[3]
RTOL, ATOL = 1e-5, 1e-6


def _sync(device):
    if device.type == "mps":
        torch.mps.synchronize()
    elif device.type == "cuda":
        torch.cuda.synchronize(device)


def _check_time(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("本组合共享累计截止时间已到，未执行步骤不计通过")


def _source_cache(cfg):
    path = cfg.get("verification", {}).get("reference_cache") or os.environ.get(
        "DOJO_OPERATOR_REFERENCE_CACHE"
    )
    if not path:
        raise ValueError("须指定 verification.reference_cache 或 DOJO_OPERATOR_REFERENCE_CACHE")
    return load_sources(path)


def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法读取公开步骤: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute_recipe(cfg, directory, *, deadline, batch_trace):
    """在独立模块命名空间调用真实 train/infer/post，writer 保存生产状态。"""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    scripts = ROOT / "recipes" / "operator_learning" / cfg["dataset"]["case"]
    previous_configuration = sys.modules.get("configuration")
    try:
        # 可复制模板使用局部 configuration 导入；临时替换后原样恢复，避免串案缓存。
        sys.modules["configuration"] = _load_module("configuration", scripts / "configuration.py")
        modules = {
            name: _load_module(f"operator_serial_{name}", scripts / f"{name}.py")
            for name in ("train", "infer", "post")
        }
    finally:
        if previous_configuration is None:
            sys.modules.pop("configuration", None)
        else:
            sys.modules["configuration"] = previous_configuration
    original_batch = modules["train"].batch

    def observed_batch(arrays, ids, **options):
        batch_trace.append([int(x) for x in ids])
        return original_batch(arrays, ids, **options)

    # 只观察 recipe 已公开使用的取批函数；不读训练器或运行器私有状态。
    modules["train"].batch = observed_batch
    effective = copy.deepcopy(cfg)
    effective.update(run_root=str(directory / "runs"), data_root=str(directory / "data"))
    effective["pipeline"]["stages"] = ["train", "infer", "post"]
    effective["train"]["seconds"] = min(10800, deadline - time.monotonic())
    if effective["train"]["seconds"] <= 0:
        raise TimeoutError("启动生产步骤前累计预算已耗尽")
    config_path = directory / "config.yaml"
    config_path.write_text(yaml.safe_dump(effective, sort_keys=False), encoding="utf-8")
    outputs = {}

    def pipeline(config):
        _check_time(deadline)
        trained = outputs["train"] = run.stage("train", modules["train"].train, config)
        _check_time(deadline)
        predicted = outputs["infer"] = run.stage(
            "infer", modules["infer"].infer, config, None, trained
        )
        _check_time(deadline)
        outputs["post"] = run.stage("post", modules["post"].post, config, predicted)
        return outputs

    code = run.launch(
        pipeline,
        script=str(scripts / "pipeline.py"),
        config_loader=lambda path, overrides: validate(effective),
        argv=["--config", str(config_path)],
    )
    if code:
        raise RuntimeError(f"公开算子步骤未完成，见 {directory / 'runs'}")
    return outputs


class ReferenceField(nn.Module):
    """独立场布局：不用生产 OperatorField.forward 来证明布局相同。"""

    def __init__(self, network, model):
        super().__init__()
        self.network, self.family = network, model["family"]
        self.grid = tuple(model["grid_shape"])
        self.history = model.get("history", 1)
        self.stride = model["parameters"].get("sensor_stride", 1)

    def forward(self, input, valid=None, coordinates=None):
        """按完整网格预测，DeepONet 保留每个样本自己的坐标查询。"""
        if self.history > 1:
            input = torch.cat([input[:, i] for i in range(self.history)], dim=-1)
        if tuple(input.shape[1:-1]) != self.grid:
            raise ValueError("参考输入网格与配置不符")
        if self.family == "fno":
            permutation = (0, input.ndim - 1, *range(1, input.ndim - 1))
            result = self.network(input.permute(permutation))
            return result.permute(0, *range(2, result.ndim), 1)
        if coordinates is None or coordinates.shape[:-1] != input.shape[:-1]:
            raise ValueError("参考查询与场位置不符")
        sensors = input
        for axis, size in enumerate(self.grid, start=1):
            indices = torch.arange(0, size, self.stride, device=input.device)
            sensors = sensors.index_select(axis, indices)
        result = self.network(
            sensors.flatten(1),
            coordinates.reshape(len(input), -1, len(self.grid)),
            query_layout="per_sample",
        )
        return result.reshape(len(input), *self.grid, result.shape[-1])


def build_reference(cfg, candidate, sources):
    """从明确参数建立独立参考并映射候选权重，拒绝未经对照的自定义构造器。"""
    if (
        cfg["components"]["model"]
        != "ai4e_contrib.application.operator_learning.binding.build_network"
    ):
        raise ValueError("本基础参考只覆盖已冻结构造器，自定义组件另行对照")
    model, parameters = cfg["model"], dict(cfg["model"]["parameters"])
    if model["family"] == "fno":
        if "dtype" in parameters:
            raise ValueError("真实上游串行参考固定 FP32，配置不接受 dtype 覆盖")
        network = FNOReference(
            sources,
            model["in_channels"] * model.get("history", 1),
            model["out_channels"],
            **parameters,
        )
        copy_fno_weights(network, candidate.network)
    else:
        stride = parameters.pop("sensor_stride")
        sensors = math.prod(len(range(0, n, stride)) for n in model["grid_shape"])
        latent = parameters.pop("latent_dim")
        outputs = model["out_channels"]
        branch_hidden = parameters.pop("branch_hidden", (64, 64))
        trunk_hidden = parameters.pop("trunk_hidden", (64, 64))
        activation = parameters.pop("activation", "tanh")
        final_activation = parameters.pop("trunk_final_activation", "tanh")
        if parameters:
            raise ValueError(f"DeepONet 参考未声明参数: {sorted(parameters)}")
        network = DeepONetReference(
            sources,
            (sensors * model["in_channels"], *branch_hidden, latent * outputs),
            (model["spatial_dims"], *trunk_hidden, latent),
            out_channels=outputs,
            multi_output=None if outputs == 1 else "split_branch",
            activation=activation,
            trunk_final_activation=final_activation,
        )
        copy_deeponet_weights(network, candidate.network)
    return ReferenceField(network, model)


def reference_batch(arrays, indices, *, case, device):
    """独立按样本身份复制准备数组，不调用生产取批函数。"""
    indices = [int(i) for i in indices]
    result = {
        name: torch.tensor(
            np.asarray(arrays[name])[indices].copy(),
            device=device,
            dtype=torch.bool if name == "valid" else torch.float32,
        )
        for name in ("input", "target", "valid")
    }
    if case != "double_cylinder":
        dimensions = 2 if case == "darcy" else 3
        result["coordinates"] = torch.tensor(
            np.asarray(arrays["physical_input"])[indices, ..., :dimensions].copy(),
            dtype=torch.float32,
            device=device,
        )
    return result


def reference_loss(prediction, item, statistics, weight):
    """独立监督与 Darcy 非负约束；不导入生产 objective 或 constraint。"""
    valid, target = item["valid"], item["target"]
    if prediction.shape != target.shape or not valid.any():
        raise ValueError("参考监督形状或有效域不符")
    result = (prediction[valid] - target[valid]).square().mean()
    if weight:
        mean = torch.tensor(
            statistics["target"]["mean"], device=prediction.device, dtype=prediction.dtype
        )
        scale = torch.tensor(
            statistics["target"]["scale"], device=prediction.device, dtype=prediction.dtype
        )
        negative = torch.clamp(-(prediction * scale + mean)[valid], min=0) / scale
        result = result + weight * negative.square().mean()
    return result


def train_reference(cfg, reference, arrays, statistics, *, updates, device, deadline):
    """唯一手写训练循环属于独立参考；同种子排列、同批次和标准 Adam。"""
    reference.to(device).train()
    optimizer = torch.optim.Adam(reference.parameters(), lr=cfg["train"]["lr"])
    generator = torch.Generator().manual_seed(cfg["seed"])
    count, batch_size = len(arrays["target"]), cfg["train"]["batch_size"]
    if count % batch_size:
        raise ValueError("参考与 IterationStream 同样要求整除批次")
    order, offset = list(range(count)), count
    history, trace = [], []
    for _ in range(updates):
        _check_time(deadline)
        if offset == count:
            order, offset = torch.randperm(count, generator=generator).tolist(), 0
        indices = order[offset : offset + batch_size]
        offset += batch_size
        trace.append(indices)
        item = reference_batch(arrays, indices, case=cfg["dataset"]["case"], device=device)
        optimizer.zero_grad()
        prediction = reference(item["input"], item["valid"], item.get("coordinates"))
        loss = reference_loss(prediction, item, statistics, cfg["train"].get("physical_weight", 0))
        if not torch.isfinite(loss):
            raise FloatingPointError("参考损失非有限")
        loss.backward()
        if any(
            p.grad is not None and not torch.isfinite(p.grad).all() for p in reference.parameters()
        ):
            raise FloatingPointError("参考梯度非有限")
        optimizer.step()
        history.append(float(loss.detach()))
    _sync(device)
    if any(not torch.isfinite(p).all() for p in reference.parameters()):
        raise FloatingPointError("参考参数非有限")
    return {
        "model": reference.state_dict(),
        "optimizer": optimizer.state_dict(),
        "history": history,
        "updates": updates,
        "batch_trace": trace,
        "stream": {
            "count": count,
            "batch_size": batch_size,
            "offset": offset,
            "order": torch.tensor(order),
            "rng": generator.get_state(),
        },
    }


def _state_difference(expected, actual):
    if expected.keys() != actual.keys():
        raise AssertionError("映射后的参考状态键不一致")
    maximum = 0.0
    for name in expected:
        left, right = expected[name].detach().cpu(), actual[name].detach().cpu()
        torch.testing.assert_close(left, right, rtol=RTOL, atol=ATOL, msg=name)
        if left.numel():
            maximum = max(maximum, float((left - right).abs().max()))
    return maximum


def compare_predictions(cfg, reference, arrays, record, fixed_path, output, *, device, deadline):
    """独立完整 test 前向与物理反变换，读回生产固定结果及实体身份后核对。"""
    predictions = []
    reference.eval()
    with torch.no_grad():
        for index in range(len(arrays["target"])):
            _check_time(deadline)
            item = reference_batch(arrays, [index], case=cfg["dataset"]["case"], device=device)
            predictions.append(
                reference(item["input"], item["valid"], item.get("coordinates")).cpu()
            )
    normalized = torch.cat(predictions).numpy()
    stats = record["metadata"]["statistics"]["target"]
    prediction = normalized * np.asarray(stats["scale"]) + np.asarray(stats["mean"])
    valid = np.asarray(arrays["valid"], bool)
    prediction[~valid] = 0
    prediction = prediction.astype(np.float32)
    fixed_record, fixed = read_arrays(fixed_path, kind="classic-results-v1")
    for key in ("case", "ids", "fields", "units", "statistics"):
        if fixed_record["metadata"][key] != record["metadata"][key]:
            raise AssertionError(f"固定预测与准备元数据不同: {key}")
    for name, original in (
        ("entity_ids", "entity_ids"),
        ("valid", "valid"),
        ("target", "physical_target"),
        ("physical_input", "physical_input"),
    ):
        np.testing.assert_array_equal(fixed[name], arrays[original], err_msg=name)
    if "times" in arrays:
        np.testing.assert_array_equal(fixed["times"], arrays["times"], err_msg="times")
    reference_path = save_arrays(
        output,
        {"prediction": prediction, "valid": valid, "entity_ids": arrays["entity_ids"]},
        kind="operator-reference-predictions-v1",
        metadata=record["metadata"],
    )
    difference = np.abs(prediction.astype(np.float64) - np.asarray(fixed["prediction"], np.float64))
    report = {
        "manifest": reference_path,
        "samples": len(prediction),
        "shape": list(prediction.shape),
        "valid_count": int(valid.sum()),
        "maximum_difference": float(difference.max()),
        "valid_maximum_difference": float(difference[valid].max()),
        "rtol": RTOL,
        "atol": ATOL,
        "scope": "complete prepared test; physical units; identical valid grid support",
    }
    save_json(Path(output).parent / "prediction-comparison.json", report)
    np.testing.assert_allclose(prediction, fixed["prediction"], rtol=RTOL, atol=ATOL)
    return report


def check_connections(cfg):
    """真实准备的一次纯前向连接核对，不建立优化器或写入训练状态。"""
    cfg = validate(cfg)
    sources = _source_cache(cfg)
    record, arrays = read_prepared(cfg["inputs"]["train"]["preparation"], "train")
    with seeded_randomness(cfg["seed"]), torch.no_grad():
        candidate = construct(cfg).cpu().eval()
        reference = build_reference(cfg, candidate, sources).cpu().eval()
        left = batch(arrays, [0], device="cpu", case=cfg["dataset"]["case"], sample_points=None)
        right = reference_batch(arrays, [0], case=cfg["dataset"]["case"], device="cpu")
        for key in right:
            torch.testing.assert_close(left[key], right[key], rtol=0, atol=0)
        expected = reference(right["input"], right["valid"], right.get("coordinates"))
        actual = candidate(left["input"], left["valid"], left.get("coordinates"))
        torch.testing.assert_close(actual, expected, rtol=RTOL, atol=ATOL)
        return {
            "status": "passed",
            "training_updates": 0,
            "sample": record["metadata"]["ids"][0],
            "shape": list(actual.shape),
            "maximum_difference": float((actual - expected).abs().max()),
        }


def run_combo(cfg, output, deadline=None, updates=100):
    """串行完成一个组合的生产/参考/完整 test 对照；失败保存记录后抛异常。

    deadline 是 time.monotonic 的绝对截止时刻，覆盖本函数所有步骤；传入
    主控父组合剩余预算即可让扩展/重试共用三小时账本。默认总上限三小时。
    此处不包含独立安装或恢复重放，它们仍须由主控在同一预算内调度。
    """
    if type(updates) is not int or updates < 1:
        raise ValueError("updates 须为正整数")
    started = time.monotonic()
    deadline = min(started + 10800, deadline) if deadline is not None else started + 10800
    _check_time(deadline)
    cfg = copy.deepcopy(cfg)
    cfg["train"]["updates"] = updates
    cfg = validate(cfg)
    if cfg["inputs"]["train"]["resume"] is not None:
        raise ValueError("基础两侧对照从同初值开始；恢复重放由主控另行调度")
    if cfg["inputs"]["infer"]["preparation"] != cfg["inputs"]["train"]["preparation"]:
        raise ValueError("train/infer 必须使用同一冻结准备入口")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "status": "running",
        "case": cfg["dataset"]["case"],
        "family": cfg["model"]["family"],
        "updates": updates,
        "physical_weight": cfg["train"].get("physical_weight", 0),
        "timings": {},
    }
    try:
        sources = _source_cache(cfg)
        prepared = cfg["inputs"]["train"]["preparation"]
        train_record, train_arrays = read_prepared(prepared, "train")
        test_record, test_arrays = read_prepared(prepared, "test")
        device = resolve_device(cfg["train"]["device"])
        cfg["train"]["device"] = cfg["infer"]["device"] = str(device)
        report["device"] = str(device)
        # 提前验证构造和参考可用性，避免生产训练结束才发现参数不匹配。
        with seeded_randomness(cfg["seed"]):
            candidate = construct(cfg)
            build_reference(cfg, candidate, sources)
        trace = []
        mark = time.monotonic()
        outputs = execute_recipe(cfg, output / "dojo", deadline=deadline, batch_trace=trace)
        _sync(device)
        report["timings"]["dojo_train_infer_post"] = time.monotonic() - mark
        report["dojo"] = outputs
        final = torch.load(outputs["train"]["checkpoint"], map_location="cpu", weights_only=False)
        initial = torch.load(outputs["train"]["initial"], map_location="cpu", weights_only=False)
        if final["updates"] != updates or final["status"] != "complete":
            raise AssertionError("生产训练未完成约定更新数")
        if not any(
            not torch.equal(initial["model"][key], tensor) for key, tensor in final["model"].items()
        ):
            raise AssertionError("生产模型没有有效参数更新")
        with seeded_randomness(cfg["seed"]):
            candidate = construct(cfg).cpu()
            candidate.load_state_dict(initial["model"], strict=True)
            reference = build_reference(cfg, candidate, sources).to(device)
            mark = time.monotonic()
            reference_state = train_reference(
                cfg,
                reference,
                train_arrays,
                train_record["metadata"]["statistics"],
                updates=updates,
                device=device,
                deadline=deadline,
            )
        report["timings"]["reference_train"] = time.monotonic() - mark
        torch.save(reference_state, output / "reference.pt")
        save_json(
            output / "batches.json",
            {"production": trace, "reference": reference_state["batch_trace"]},
        )
        if trace != reference_state["batch_trace"]:
            raise AssertionError("双方实际训练取批身份不同")
        for key in ("count", "batch_size", "offset"):
            if final["stream"][key] != reference_state["stream"][key]:
                raise AssertionError(f"参考最终数据游标不同: {key}")
        for key in ("order", "rng"):
            torch.testing.assert_close(
                final["stream"][key], reference_state["stream"][key], rtol=0, atol=0
            )
        np.testing.assert_allclose(
            final["history"], reference_state["history"], rtol=RTOL, atol=ATOL
        )
        report["history_maximum_difference"] = float(
            np.max(np.abs(np.asarray(final["history"]) - np.asarray(reference_state["history"])))
        )
        candidate.load_state_dict(final["model"], strict=True)
        mapped_final = build_reference(cfg, candidate, sources)
        report["weight_maximum_difference"] = _state_difference(
            mapped_final.state_dict(), reference.state_dict()
        )
        _check_time(deadline)
        mark = time.monotonic()
        report["prediction_comparison"] = compare_predictions(
            cfg,
            reference,
            test_arrays,
            test_record,
            outputs["infer"],
            output / "reference-test",
            device=device,
            deadline=deadline,
        )
        _sync(device)
        report["timings"]["reference_test_comparison"] = time.monotonic() - mark
        _check_time(deadline)
        report.update(
            status="passed",
            metrics=outputs["post"],
            reference_checkpoint=str(output / "reference.pt"),
            rtol=RTOL,
            atol=ATOL,
            scope="small-data integration; upstream arithmetic harness; not paper accuracy",
            recovery="not run by this function",
            installation="not run by this function",
        )
    except Exception as error:
        report.update(status="failed", error_type=type(error).__name__, error=str(error))
        raise
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        save_json(output / "result.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--updates", type=int, default=100)
    parser.add_argument("--seconds", type=float, default=10800)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    from ai4e_contrib.application.operator_learning.configuration import load_configuration

    configuration = load_configuration(args.config)
    if args.check_only:
        print(check_connections(configuration))
    else:
        if args.output is None or not 0 < args.seconds <= 10800:
            parser.error("训练须提供新 output 目录且 seconds 在 (0,10800] 内")
        print(run_combo(configuration, args.output, time.monotonic() + args.seconds, args.updates))
