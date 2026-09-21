"""外流独立参考：模型/优化定义来自锁定上游，准备数组另行审计。"""

import copy
import time

import numpy as np
import torch

from .reference import load_reference, reference_optimizer


def compare_batch(options, inputs, targets):
    """完整配置同权重前向、梯度和单步更新；固定 CPU float32 容差。"""
    from ai4e_contrib.ability.model.geotransolver import GeoTransolver
    from ai4e_contrib.application.geotransolver import build_optimizer

    torch.manual_seed(42)
    dojo = GeoTransolver(**options)
    reference = load_reference().GeoTransolver(**options)
    reference.load_state_dict(dojo.state_dict(), strict=True)
    a, b = dojo(**inputs), reference(**inputs)
    differences = {}

    def check(name, x, y):
        torch.testing.assert_close(x, y, atol=1e-6, rtol=1e-5)
        differences[name] = float((x.detach() - y.detach()).abs().max())

    for i, (x, y) in enumerate(zip(a, b, strict=True)):
        check(f"forward_{i}", x, y)
        selected = dojo.forward_stream(
            inputs["local_embedding"][i],
            stream_index=i,
            **{k: v for k, v in inputs.items() if k != "local_embedding"},
        )
        check(f"stream_{i}", x, selected)
    # targets 包含逐物理场切片；每一项独立求均值，保留原监督权重。
    loss_a = sum((a[i][0, :, lo:hi] - target).square().mean() for i, lo, hi, target in targets)
    loss_b = sum((b[i][0, :, lo:hi] - target).square().mean() for i, lo, hi, target in targets)
    loss_a.backward()
    loss_b.backward()
    for (name, p), (_, q) in zip(
        dojo.named_parameters(), reference.named_parameters(), strict=True
    ):
        check("gradient/" + name, p.grad, q.grad)
    build_optimizer(dojo, lr=0.001, weight_decay=0.0001).step()
    reference_optimizer(reference, lr=0.001, weight_decay=0.0001).step()
    for name, value in dojo.state_dict().items():
        check("update/" + name, value, reference.state_dict()[name])
    return {
        "max_abs": max(differences.values()),
        "checks": len(differences),
        "differences": differences,
    }


def audit_statistics(data):
    """独立 NumPy 复算训练统计，不以双方共享准备数组代替输入正确性证据。"""
    checked, coordinate_values = {}, {}
    for name, spec in data.normalization.record["fields"].items():
        values = []
        for i in range(len(data.view.partitions["train"])):
            sample = data.view.read("train", i)
            value = sample["conditions" if spec["scope"] == "condition" else "fields"][name]
            values.append(value.numpy().astype(np.float64))
        values = np.concatenate(values)
        parameters = spec["parameters"]
        if spec["method"] == "zscore":
            np.testing.assert_allclose(parameters["mean"], values.mean(0), rtol=1e-10, atol=1e-10)
            np.testing.assert_allclose(parameters["std"], values.std(0), rtol=1e-8, atol=1e-10)
        elif spec["method"] == "coordinate":
            coordinate_values[name] = (float(values.min()), float(values.max()))
        checked[name] = {"rows": len(values), "method": spec["method"]}
    for name in coordinate_values:
        spec = data.normalization.record["fields"][name]
        group = spec.get("coordinate_group")
        names = (
            [
                n
                for n in coordinate_values
                if group is not None
                and data.normalization.record["fields"][n].get("coordinate_group") == group
            ]
            if group
            else [name]
        )
        low = min(coordinate_values[n][0] for n in names)
        high = max(coordinate_values[n][1] for n in names)
        np.testing.assert_array_equal(spec["parameters"]["minimum"], [low])
        np.testing.assert_array_equal(spec["parameters"]["maximum"], [high])
    return checked


def target_slices(config, batch):
    """声明监督字段对应的流及通道边界。"""
    targets = []
    for i, (domain, spec) in enumerate(config["model"]["data_specs"]["domains"].items()):
        offset = 0
        for field, width in spec["output_dims"].items():
            targets.append(
                (i, offset, offset + width, batch["targets"][f"{domain}_{field}_target"])
            )
            offset += width
    return targets


def train_reference(data, config, options, *, epochs):
    """独立训练循环及锁定上游优化器；采样数组由已审计输入能力提供。"""
    from ai4e_core.applications.aero_cfd.trainprep.point_inputs import prepare_point_sample

    reference_type = load_reference().GeoTransolver
    torch.manual_seed(config["sampling"]["seed"])
    model = reference_type(**options)
    optimizer = reference_optimizer(
        model, lr=config["train"]["learning_rate"], weight_decay=config["train"]["weight_decay"]
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=config["train"]["step_size"], gamma=config["train"]["gamma"]
    )
    loader = torch.utils.data.DataLoader(
        range(len(data.view.partitions["train"])),
        batch_size=None,
        shuffle=True,
        num_workers=0,
        generator=torch.Generator().manual_seed(config["sampling"]["seed"]),
    )
    history = []
    started = time.monotonic()
    for epoch in range(epochs):
        for index in loader:
            batch = prepare_point_sample(
                data.view.read("train", index), config, data.normalization, epoch=epoch
            )
            optimizer.zero_grad(set_to_none=True)
            prediction = model(**batch["inputs"])
            loss = sum(
                (prediction[i][0, :, lo:hi] - target).square().mean()
                for i, lo, hi, target in target_slices(config, batch)
            )
            loss.backward()
            optimizer.step()
            history.append(float(loss.detach()))
        scheduler.step()
    return model, {
        "history": history,
        "seconds": time.monotonic() - started,
        "optimizer": copy.deepcopy(optimizer.state_dict()),
        "scheduler": scheduler.state_dict(),
    }
