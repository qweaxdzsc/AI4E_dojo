"""旧双域锚点模板的独立推理适配；保留评价与保存各自的随机流。"""

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.applications.aero_cfd.infer import anchor_stage as steps
from ai4e_core.applications.aero_cfd.infer.vtk_export import (
    VTK_DISABLED,
    VTK_FULL_KIND,
    VTK_NO_PREDICTION,
    merge_full_mesh_record,
    skip_vtk,
    write_anchor_prediction_vtk,
)

from .configuration import inference_parameters


def open_inference(config, *, model_component, session, dataset_component=None, trained=None):
    """登记旧锚点输入的独立推理；原子计算与历史 post 共用。"""
    cfg = inference_parameters(config)
    if not cfg["infer"]["samples"]:
        raise ValueError("infer.samples 需要明确的样本名单")
    job = steps.open_post(cfg, model_component=model_component, session=session, trained=trained)
    job.dataset_component = dataset_component
    return job


configure_restore = steps.configure_restore
configure_prediction = steps.configure_prediction
configure_physical_output = steps.configure_physical_output


def configure_evaluation(job, *, settings=None, operation=None, sample_operation=None):
    """原生锚点评价允许普通逐场函数，历史评价入口保持原契约。"""
    from ai4e_core.base.config import operation_record, plain, resolve_operation

    from .evaluation import evaluate_sample

    value = plain(settings or job.config["infer"])
    if operation is not None or value.get("metric", {}).get("target"):
        raise ValueError(
            "原生锚点评价请使用sample_metric或sample_operation，旧metric仅用于历史post"
        )
    fn = resolve_operation(
        value.get("sample_metric", {}), default=evaluate_sample, operation=sample_operation
    )
    job.sample_metric = fn
    if sample_operation is not None or value.get("sample_metric", {}).get("target"):
        record = operation_record(fn)
        job.extensions["sample_metric"] = record
        job.config["infer"]["sample_metric"] = {
            "target": record["name"],
            "parameters": record["parameters"],
        }
    return steps.configure_evaluation(job, settings=value)


configure_save = steps.configure_save


def configure_mesh_export(job, *, settings=None):
    """网格化导出走完整查询或来源回贴；没有可还原拓扑时不登记网格步骤。"""
    from ai4e_core.applications.aero_cfd.infer.configuration import apply_export_aliases
    from ai4e_core.applications.aero_cfd.infer.vtk_capability import describe_vtk_exports
    from ai4e_core.base.config import plain

    value = apply_export_aliases(plain(settings or job.config["infer"]))
    capability = describe_vtk_exports(
        job.config, dataset_component=getattr(job, "dataset_component", None)
    )
    mesh_on = bool(value.get("export_mesh", value.get("export_vtk", True)))
    if mesh_on and not capability["mesh"]["available"]:
        job.mesh_skip_reason = capability["mesh"]["reason"]
        value["export_mesh"] = False
        value["export_vtk"] = False
        mesh_on = False
    sources = capability["mesh"].get("sources") or []
    value["query"] = mesh_on and "source_vtk" in sources and value.get("query", True)
    value["export_mesh"] = mesh_on
    value["export_vtk"] = mesh_on
    job.vtk_exports = capability
    job.config["infer"].update(value)
    if isinstance(job.config.get("post"), dict):
        job.config["post"].update(value)
    return steps.configure_mesh_export(job, settings=value)


check_report = steps.check_report


def execute(job):
    """执行原有锚点流并发布统一索引，不把数组写入索引。"""
    result = steps.execute(job)
    protocol = {
        "version": 1,
        "checkpoint": str(job.restored["checkpoint"]),
        "settings": job.config["infer"],
    }
    protocol["digest"] = fingerprint(protocol)
    # 完整网格保留真实来源身份，清单中的锚点实体声明不冒充原始网格。
    import json
    from pathlib import Path

    from ai4e_core.abilities.data.save.arrays import save_json

    for item in result.get("predictions", []):
        if not item.get("manifest"):
            continue
        path = Path(item["manifest"])
        metadata = json.loads(path.read_text())
        for mesh in result.get("meshes", []):
            if mesh["sample_id"] != item.get("sample_id", item.get("sample")):
                continue
            item.setdefault("timings", {})["full_mesh_prediction"] = mesh.get("prediction_seconds")
            if item.get("evidence"):
                item["evidence"] = fingerprint(
                    {
                        k: item[k]
                        for k in ("identity", "fields", "metrics", "metric_records", "timings")
                    }
                )
            for domain in ("surface", "volume"):
                if mesh.get(domain):
                    source = Path(mesh[domain])
                    if source.parent != path.parent:
                        raise ValueError("原生网格必须位于本样本结果目录")
                    fields = mesh.get("fields", {}).get(
                        domain,
                        ["pred_pressure", "gt_pressure"]
                        if domain == "surface"
                        else ["pred_velocity", "gt_velocity"],
                    )
                    merge_full_mesh_record(
                        metadata,
                        domain,
                        {
                            "path": source.name,
                            "entity_set": "full_source_mesh",
                            "kind": mesh.get("kind", VTK_FULL_KIND),
                            "association": "point",
                            "fields": fields,
                            "point_count": mesh["points"][domain],
                            "sample_id": mesh.get("sample_id"),
                            "source_sample_id": mesh.get("source_sample_id", mesh.get("sample_id")),
                        },
                    )
            if mesh:
                metadata.setdefault("vtk", {})["full_mesh"] = {
                    "exported": True,
                    "kind": VTK_FULL_KIND,
                    "sample_id": mesh.get("sample_id"),
                }
        save_json(path, metadata)
    modern = result.get("inference_protocol")
    if modern:
        protocol = modern
    report = {
        "version": 1,
        "status": "succeeded",
        "kind": "anchor-predictions",
        "protocol": protocol,
        "results": result.get("predictions", []),
        "metrics": result.get("evaluation", {}).get("metrics", {}),
        "meshes": result.get("meshes", []),
        "timings": result.get("timings", {}),
    }
    job.session.artifact("physical-predictions.json", report)
    if modern:
        path = job.session.artifact("inference-results.json", {**report, "version": 2})
        from .indexing import register_results

        register_results(job.session, path, report)
    job.session.report(report, stage="infer")
    return report


def configure_selection(job, *, fields=None):
    """锚点模板使用同一字段目录，保存仍保留原始向量分量。"""
    from .selection import resolve_selection

    job.selection = resolve_selection(job.config, getattr(job, "dataset_component", None), fields)
    job.config["infer"]["fields"] = [f["id"] for f in job.selection]
    job.config["post"]["fields"] = job.config["infer"]["fields"]
    return job


def run_selected_batches(config, restored, batches, *, predict, progress, protocol):
    """原生锚点推理一次预测后评价和保存，旧 post 保留原两次遍历。"""
    import json
    from pathlib import Path
    from time import perf_counter
    from types import SimpleNamespace

    import torch

    from ai4e_core.abilities.data.save.arrays import save_json
    from ai4e_core.abilities.data.save.store import write_named_tensors
    from ai4e_core.abilities.eval.physical import PhysicalMetrics
    from ai4e_core.abilities.inference.timing import measure
    from ai4e_core.applications.aero_cfd.model.objectives import objectives

    from .evaluation import evaluate_sample
    from .selection import resolve_selection

    settings = config["infer"]
    from ai4e_core.base.config import resolve_operation

    sample_fn = resolve_operation(settings.get("sample_metric", {}), default=evaluate_sample)
    selected = resolve_selection(config, fields=settings.get("fields"))
    terms = {t["prediction"]: t for t in objectives(config["model"])}
    all_metrics, results = PhysicalMetrics(), []
    # 身份来自同一次采样的具名锚点；不宣称等于完整原网格点集。
    for batch in batches:
        with measure(restored["device"]) as elapsed, torch.no_grad():
            prediction = predict(restored["model"], batch["inputs"])
        count = len(batch["metadata"])
        for index, metadata in enumerate(batch["metadata"]):
            with progress.unit([{"sample_id": metadata["sample"], "partition": settings["split"]}]):
                started = perf_counter()
                name = metadata["sample"]
                item = SimpleNamespace(name=name, domains={}, payloads={})
                for domain, binding in config["trainprep"]["domains"].items():
                    positions = (
                        batch["inputs"]["domain_anchor_positions"][domain][index].detach().cpu()
                    )
                    positions = restored["normalization"].inverse(binding["position"], positions)
                    item.payloads[domain + ".position"] = positions
                    item.payloads[domain + ".ids"] = torch.arange(len(positions))
                    targets = {}
                    for field, source in binding["targets"].items():
                        if not any(f["domain"] == domain and f["field"] == field for f in selected):
                            continue
                        term = terms[source]
                        key = domain + "." + field
                        p = restored["normalization"].inverse(
                            term["normalization"], prediction[source][index].detach().cpu()
                        )
                        t = restored["normalization"].inverse(
                            term["normalization"],
                            batch["targets"][term["target"]][index].detach().cpu(),
                        )
                        item.payloads.update({key + ".prediction": p, key + ".truth": t})
                        targets[field] = key
                        if settings["evaluate"]:
                            all_metrics.update(key, p.numpy(), t.numpy())
                    if targets:
                        item.domains[domain] = {
                            "targets": targets,
                            "position": domain + ".position",
                            "ids": domain + ".ids",
                            "identity_basis": "sampled",
                            "topology": None,
                            "entity_set": "sampled_anchors",
                            "units": {f: None for f in targets},
                        }
                records = []
                if settings["evaluate"]:
                    # 评价与保存共用预测，但各自登记实际交付和失败。
                    if settings["save_predictions"]:
                        with (
                            progress.operation("evaluation"),
                            progress.unit(
                                [{"sample_id": metadata["sample"], "partition": settings["split"]}]
                            ),
                        ):
                            records = sample_fn(item, selected, settings.get("metrics"))
                    else:
                        records = sample_fn(item, selected, settings.get("metrics"))
                timing = {
                    "prediction": elapsed["seconds"] / count,
                    "evaluation": perf_counter() - started,
                }
                value = {
                    "sample": name,
                    "sample_id": name,
                    "split": settings["split"],
                    "identity": {"sample": name, "split": settings["split"]},
                    "fields": item.domains,
                    "metrics": {},
                    "metric_records": records,
                    "timings": timing,
                    "manifest": None,
                }
                if settings["save_predictions"]:
                    started = perf_counter()
                    dest = Path(config["paths"]["datasets"]["predictions"]) / name
                    if not dest.resolve().is_relative_to(
                        Path(config["paths"]["datasets"]["predictions"]).resolve()
                    ):
                        raise ValueError("推理样本输出路径越界")
                    keep = {
                        key
                        for domain in item.domains.values()
                        for key in (domain["position"], domain["ids"])
                    }
                    keep |= {
                        key + s
                        for domain in item.domains.values()
                        for key in domain["targets"].values()
                        for s in (".prediction", ".truth")
                    }
                    arrays = {key: item.payloads[key] for key in keep}
                    filemap = {key: key + ".pt" for key in arrays}
                    saved = {
                        "identity": value["identity"],
                        "domains": item.domains,
                        "protocol": protocol["digest"],
                        "filemap": filemap,
                        "metric_records": records,
                        "component_selection": selected,
                    }
                    write_named_tensors(
                        dest,
                        arrays,
                        filemap,
                        overwrite=settings.get("overwrite", False),
                        extra_writers={
                            "manifest.json": lambda path, saved=saved: save_json(path, saved)
                        },
                    )
                    value["manifest"] = str(dest / "manifest.json")
                    progress.committed(value["manifest"])
                    if settings.get("export_pointcloud", settings.get("export_vtk", True)):
                        write_anchor_prediction_vtk(
                            value["manifest"],
                            overwrite=settings.get("overwrite", False),
                            committed=progress.committed,
                        )
                    elif not settings.get("export_mesh", settings.get("export_vtk", True)):
                        skip_vtk(value["manifest"], VTK_DISABLED, channel="pointcloud")
                        skip_vtk(value["manifest"], VTK_DISABLED, channel="mesh")
                    saved = json.loads(Path(value["manifest"]).read_text())
                    value["vtk"] = saved.get("vtk")
                    timing["save"] = perf_counter() - started
                if (
                    settings.get("export_pointcloud", settings.get("export_vtk", True))
                    or settings.get("export_mesh", settings.get("export_vtk", True))
                ) and not value.get("manifest"):
                    value["vtk"] = {"exported": False, "reason": VTK_NO_PREDICTION}
                value["evidence"] = fingerprint(
                    {
                        k: value[k]
                        for k in ("identity", "fields", "metrics", "metric_records", "timings")
                    }
                )
                results.append(value)
                progress.report.update(
                    results=results, completed=len(results), total=len(settings["samples"])
                )
                progress.publish()
    return {
        "results": results,
        "predictions": results,
        "evaluation": {"metrics": all_metrics.finalize() if settings["evaluate"] else {}},
    }
