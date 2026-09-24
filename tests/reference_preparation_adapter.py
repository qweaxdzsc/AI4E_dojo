"""冻结参考的测试连接：核验真实来源后提供只读视图，不改历史字节。

普通 v2 的字段映射仅在内存交接，digest 始终是原准备的真实摘要。
参考的预测循环、物理指标和保存仍由冻结 physical_post 执行。
锚点视图调用采样/模型原子能力，不调用待测 infer 编排。
"""

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import torch


def reference_loader_state(frozen, checkpoint, *, restore=False):
    """旁录冻结参考遗漏的独立 DataLoader 随机状态，不改权重或采样序列。

    仅用于本次参考运行；旧历史检查点缺此旁录时不能凭空补齐。
    返回保存函数，调用者在真实轮次检查点发布后调用。
    """
    checkpoint = Path(checkpoint)
    sidecar = checkpoint.with_suffix(".loader-state.pt")
    loaders = []
    original = frozen.torch
    saved = None
    if restore:
        saved = torch.load(sidecar, weights_only=True)
        assert saved["checkpoint_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()

    def loader(*args, **kwargs):
        result = original.utils.data.DataLoader(*args, **kwargs)
        if result.generator is not None:
            if saved is not None:
                result.generator.set_state(saved["generators"][len(loaders)])
            loaders.append(result.generator)
        return result

    frozen.torch = SimpleNamespace(**{
        **vars(original),
        "utils": SimpleNamespace(**{
            **vars(original.utils),
            "data": SimpleNamespace(**{**vars(original.utils.data), "DataLoader": loader}),
        }),
    })

    def save():
        torch.save({
            "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            "generators": [generator.get_state() for generator in loaders],
        }, sidecar)

    return save


def execute_reference(frozen, config, dataset, component, session, *, anchors=False):
    """把当前准备和检查点投影给冻结参考，记录桥接且保留完整来源门禁。"""
    from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint
    from ai4e_core.abilities.inference.randomness import seeded_randomness
    from ai4e_core.abilities.inference.rebuild import rebuild
    from ai4e_core.applications.aero_cfd.trainprep import preparation

    config = copy.deepcopy(config)
    checkpoint = Path(config["post"]["checkpoint"])
    reference = Path(
        config["train"].get("preparation")
        or checkpoint.parent.parent / "artifacts/preparation.json"
    )
    record = json.loads(reference.read_text())
    physical = "dataset" in record
    if physical and not anchors:
        return frozen.execute(config, dataset, component, session)
    config["train"]["manifest"] = record["manifest"]
    if physical:
        from ai4e_core.applications.aero_cfd.trainprep.physical import consume

        prepared = consume(config, dataset, component, reference)
        partitions = prepared.view.partitions
        data = preparation.prepare_fields(preparation.open_dataset(config, overlay=partitions))
        data.normalization = prepared.normalization
    else:
        partitions = record["partitions"]
        data = preparation.consume(
            config, reference, prepare=component.prepare_inputs, collate=component.collate
        )
        original_data = preparation.prepare_fields(preparation.open_dataset(config))
        assert original_data.index.content_digest() == record["dataset_digest"]
    config["sampling"]["random_stream"] = config["post"].get("random_stream", "global")
    view = dataset.open_physical(config)
    view.remap_partitions(partitions)
    split = config["post"].get("split", "test")
    selected = config["post"]["samples"]
    assert (
        selected
        and len(set(selected)) == len(selected)
        and set(selected) <= set(view.partitions[split])
    )
    view.partitions[split] = list(selected)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if not physical:
        assert (
            state["contract"]["manifest_digest"]
            == hashlib.sha256(json.dumps(data.index.manifest, sort_keys=True).encode()).hexdigest()
        )
    else:
        assert state["contract"]["preparation"] == record["digest"]
    normalization = data.normalization
    original_read = view.read
    current = {}

    def read(partition, index):
        sample = original_read(partition, index)
        if not anchors:
            return sample
        fields = data.index.read(
            partition, data.index.partitions[partition].index(sample["identity"]["sample"])
        )
        fields = normalization.apply(data.physical_prepare(fields))
        item = component.prepare_inputs(
            fields,
            config["sampling"],
            sample=sample["identity"]["sample"],
            sample_index=index,
            data_specs=config["model"]["data_specs"],
            bindings=config["trainprep"],
            normalization=normalization,
            geometry_conditioning_dims=config["model"].get("geometry_conditioning_dims"),
            evaluation=True,
        )
        current["batch"] = component.collate([item])
        sample = copy.deepcopy(sample)
        for domain, binding in config["trainprep"]["domains"].items():
            rows = item["metadata"]["domain_rows"][domain]["anchor"]
            sample["fields"][binding["position"]] = normalization.inverse(
                binding["position"],
                current["batch"]["inputs"]["domain_anchor_positions"][domain][0],
            )
            for source in binding["targets"].values():
                term = next(t for t in config["model"]["supervision"] if t["prediction"] == source)
                sample["fields"][source] = normalization.inverse(
                    source, current["batch"]["targets"][term["target"]][0]
                )
            sample["domains"][domain].update(
                ids=torch.arange(len(rows)), identity_basis="sampled", topology=None
            )
        return sample

    view.read = read

    def construct(**parameters):
        model = component.construct(**parameters)
        if physical:
            assert state["contract"]["component"] == component.describe(model)
            model.load_state_dict(state["model"], strict=True)
        else:
            rebuild(
                checkpoint,
                model,
                contract={
                    "model_version": component.describe(model)["model_version"],
                    "model": config["model"],
                    "trainprep": config["trainprep"],
                    "normalization": normalization.record,
                },
            )
            assert (
                tuple(state["contract"]["input_layout"])
                == component.describe(model)["input_layout"]
            )
        current["model"] = model
        return model

    def predict(model, sample, values, norm, *, preparation_id):
        if not anchors:
            return component.predict_sample(
                model, sample, values, norm, preparation_id=preparation_id
            )
        result = component.predict(model, current["batch"]["inputs"])
        return {
            source: norm.inverse(source, result[source][0]).cpu()
            for binding in config["trainprep"]["domains"].values()
            for source in binding["targets"].values()
        }

    def load(path, **kwargs):
        assert Path(path) == checkpoint
        # 字段映射只服务旧读取器；检查已由 rebuild 核验，不写回 checkpoint。
        return {
            **state,
            "contract": {
                **state["contract"],
                "preparation": record["digest"],
                "component": component.describe(current["model"]),
            },
        }

    bridge = {
        "preparation": file_fingerprint(reference),
        "weights": file_fingerprint(checkpoint),
        "original_preparation_digest": record["digest"],
        "mode": "anchors" if anchors else "full",
        "samples": selected,
        "normalization": normalization.digest,
    }
    session.artifact("reference-bridge.json", bridge)
    original_open, original_torch = frozen.open_preparation, frozen.torch
    frozen.open_preparation = lambda *_: (
        view,
        normalization,
        {**record, "dataset": record.get("dataset", record.get("dataset_digest"))},
    )
    frozen.torch = SimpleNamespace(
        load=load,
        no_grad=torch.no_grad,
        mps=torch.mps,
        manual_seed=(lambda _: None) if anchors else torch.manual_seed,
    )
    model_view = SimpleNamespace(
        **{name: getattr(component, name) for name in dir(component) if not name.startswith("__")}
    )
    model_view.construct, model_view.predict_sample = construct, predict
    dataset_view = SimpleNamespace(
        comparison_metadata=(lambda *_: {"entity_set": "sampled_anchors"})
        if anchors
        else dataset.comparison_metadata
    )
    try:
        with seeded_randomness(int(config["sampling"]["seed"])):
            return frozen.execute(config, dataset_view, model_view, session)
    finally:
        frozen.open_preparation, frozen.torch = original_open, original_torch


def compare_full_fields(frozen, config, dataset, component, session):
    """全点对全点：冻结循环作期望，当前公开预测/物理步骤作被测实现。"""
    from ai4e_core.abilities.eval.physical import PhysicalMetrics
    from ai4e_core.abilities.inference.randomness import seeded_randomness
    from ai4e_core.applications.aero_cfd.infer.stage import (
        InferenceSample,
        configure_physical_output,
        configure_prediction,
    )
    from ai4e_core.applications.aero_cfd.trainprep import preparation

    expected = execute_reference(frozen, config, dataset, component, session)
    checkpoint = Path(config["post"]["checkpoint"])
    reference = checkpoint.parent.parent / "artifacts/preparation.json"
    data = preparation.consume(
        config, reference, prepare=component.prepare_inputs, collate=component.collate
    )
    values = copy.deepcopy(config)
    values["train"]["manifest"] = data.record["manifest"]
    view = dataset.open_physical(values)
    view.remap_partitions(data.record["partitions"])
    model = component.construct(**component.training_parameters(values)).float().eval()
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model"], strict=True)
    job = SimpleNamespace(
        config=values,
        model=model,
        model_component=component,
        dataset_component=dataset,
        steps=[],
        extensions={},
        data=SimpleNamespace(view=view, normalization=data.normalization, record=data.record),
    )
    configure_prediction(job)
    configure_physical_output(job)
    metrics = PhysicalMetrics()
    with seeded_randomness(int(values["sampling"]["seed"])), torch.no_grad():
        for result in expected["results"]:
            name = result["sample"]
            split = values["post"].get("split", "test")
            item = InferenceSample(name, view.read(split, view.partitions[split].index(name)))
            for _, operation in job.steps:
                item = operation(item)
            manifest = Path(result["manifest"])
            meta = json.loads(manifest.read_text())
            assert item.domains == meta["domains"]
            assert set(item.payloads) == set(meta["filemap"])
            for key, filename in meta["filemap"].items():
                torch.testing.assert_close(
                    item.payloads[key],
                    torch.load(manifest.parent / filename, weights_only=True),
                    rtol=0,
                    atol=0,
                )
            for domain in item.domains.values():
                for key in domain["targets"].values():
                    metrics.update(
                        key,
                        item.payloads[key + ".prediction"].numpy(),
                        item.payloads[key + ".truth"].numpy(),
                    )
    assert metrics.finalize() == expected["metrics"]
    return {"samples": len(expected["results"]), "metrics": expected["metrics"]}
