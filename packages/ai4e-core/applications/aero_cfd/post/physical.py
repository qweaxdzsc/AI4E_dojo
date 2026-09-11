"""具名物理预测与全点评价交接，独立运行通过产物进行比较。"""

import json
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.abilities.eval.physical import PhysicalMetrics
from ai4e_core.abilities.inference.randomness import preserve_randomness
from ai4e_core.abilities.postproc.coordinate_space import coordinate_space
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation


def execute(config: dict, dataset_component, model_component, session) -> dict:
    """同一测试名单完整点场评价；已提交结果在异常时保留。"""
    space = coordinate_space(config.get("dataset", {}).get("coordinate_space"))
    post = config["post"]
    checkpoint = Path(post.get("checkpoint", "last"))
    if str(checkpoint) in {"last", "latest", "best"}:
        checkpoint = session.run_dir / "checkpoints" / f"{checkpoint}.pt"
    reference = (
        config["train"].get("preparation")
        or checkpoint.parent.parent / "artifacts/preparation.json"
    )
    old = json.loads(Path(reference).read_text())
    config["train"]["manifest"] = old["manifest"]
    view, normalization, record = open_preparation(
        config, dataset_component, model_component, reference
    )
    samples = post["samples"]
    split = post.get("split", "test")
    if (
        len(samples) != len(set(samples))
        or not samples
        or not set(samples) <= set(view.partitions[split])
    ):
        raise ValueError("评价样本名单为空、重复或不属于指定分片")
    if session.dry_run:
        return {"mode": "post_check", "samples": samples}
    device = resolve_device(config["train"]["device"])
    model = (
        model_component.construct(**model_component.training_parameters(config))
        .to(device)
        .float()
        .eval()
    )
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if state["contract"]["preparation"] != record["digest"] or state["contract"][
        "component"
    ] != model_component.describe(model):
        raise ValueError("检查点模型或物理准备来源不一致")
    model.load_state_dict(state["model"], strict=True)
    protocol = {
        "version": 1,
        "dataset": record["dataset"],
        "preparation": record["digest"],
        "weights": file_fingerprint(checkpoint),
        "model": model_component.SOURCE,
        "samples": samples,
        "split": split,
        "settings": post,
        "execution": {"device": str(device), "precision": "fp32"},
    }
    protocol["digest"] = fingerprint(protocol)
    export_vtk = bool(post.get("export_vtk", False))
    progress = PostProgress(session, {"prediction": True, "evaluation": True, "mesh": export_vtk})
    progress.protocol = protocol
    results, overall = [], PhysicalMetrics()
    try:
        with preserve_randomness(), torch.no_grad(), progress.operation("prediction"):
            torch.manual_seed(config["sampling"]["seed"])
            for name in samples:
                with progress.unit([{"sample": name, "partition": split}]):
                    sample = view.read(split, view.partitions[split].index(name))
                    predictions = model_component.predict_sample(
                        model,
                        sample,
                        config,
                        normalization,
                        preparation_id=record["digest"] + ":" + name,
                    )
                    payloads, domains, metrics = {}, {}, PhysicalMetrics()
                    for domain, binding in config["trainprep"]["domains"].items():
                        domain_data = sample["domains"][domain]
                        position = sample["fields"][binding["position"]]
                        payloads[f"{domain}.position"] = position
                        payloads[f"{domain}.ids"] = domain_data["ids"]
                        targets = {}
                        for field, source in binding["targets"].items():
                            pred, truth = predictions[source].cpu(), sample["fields"][source]
                            if pred.shape != truth.shape or len(pred) != len(position):
                                raise ValueError(f"{name}/{domain}/{field}: 全点预测覆盖不一致")
                            key = f"{domain}.{field}"
                            metrics.update(key, pred.numpy(), truth.numpy())
                            overall.update(key, pred.numpy(), truth.numpy())
                            payloads[key + ".prediction"], payloads[key + ".truth"] = pred, truth
                            targets[field] = key
                        comparison = (
                            dataset_component.comparison_metadata(config, sample, domain)
                            if hasattr(dataset_component, "comparison_metadata")
                            else {}
                        )
                        domains[domain] = {
                            "position": f"{domain}.position",
                            "ids": f"{domain}.ids",
                            "targets": targets,
                            "identity_basis": domain_data["identity_basis"],
                            "coordinate_space": space,
                            "topology": comparison.get("topology", domain_data["topology"]),
                            "entity_set": comparison.get("entity_set"),
                            "units": {
                                field: comparison.get("units", {}).get(source)
                                for field, source in binding["targets"].items()
                            },
                        }
                    root = Path(config["paths"]["datasets"]["predictions"]) / name
                    metadata = {
                        "identity": sample["identity"],
                        "protocol": protocol["digest"],
                        "domains": domains,
                        "metrics": metrics.finalize(),
                    }
                    filemap = {key: key + ".pt" for key in payloads}
                    metadata["filemap"] = filemap
                    write_named_tensors(
                        root,
                        payloads,
                        filemap,
                        overwrite=post.get("overwrite", False),
                        extra_writers={
                            "manifest.json": lambda p, metadata=metadata: save_json(p, metadata)
                        },
                    )
                    progress.committed(root / "manifest.json")
                    results.append(
                        {
                            "sample": name,
                            "manifest": str(root / "manifest.json"),
                            "metrics": metadata["metrics"],
                        }
                    )
        if export_vtk:
            from .mesh_export import export_prediction_meshes

            with progress.operation("mesh"):
                for item in results:
                    with progress.unit([{"sample": item["sample"], "partition": split}]):
                        item["meshes"] = export_prediction_meshes(
                            config,
                            dataset_component,
                            item["manifest"],
                            committed=progress.committed,
                        )
        with progress.operation("evaluation"):
            report = {
                "version": 1,
                "status": "succeeded",
                "protocol": protocol,
                "results": results,
                "metrics": overall.finalize(),
            }
            path = session.artifact("physical-predictions.json", report)
            progress.committed(path)
        progress.finish()
        return report
    except BaseException as exc:
        progress.finish(exc)
        raise
    finally:
        del model
        if device.type == "mps":
            torch.mps.empty_cache()
