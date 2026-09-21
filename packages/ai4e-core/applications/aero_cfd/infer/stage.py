"""完整物理推理业务步骤；旧后处理入口委托此处，避免维护第二套数值路径。"""

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import torch

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.abilities.eval.physical import PhysicalMetrics
from ai4e_core.abilities.inference.randomness import preserve_randomness
from ai4e_core.abilities.inference.timing import measure, synchronize
from ai4e_core.abilities.postproc.coordinate_space import coordinate_space
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.trainprep.physical import consume
from ai4e_core.base.config import operation_record, plain, resolve_operation


@dataclass
class InferenceSample:
    """一个样本的预测交接；不把整个测试集张量保存在作业中。"""

    name: str
    sample: dict
    predictions: dict | None = None
    payloads: dict = field(default_factory=dict)
    domains: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    manifest: str | None = None
    meshes: object = None
    metric_records: list = field(default_factory=list)
    timings: dict = field(default_factory=dict)


@dataclass
class PhysicalInference:
    """步骤只由 recipe 登记；执行器不另建固定业务顺序。"""

    config: dict
    dataset_component: object
    model_component: object
    session: object
    checkpoint: Path
    data: object
    samples: list
    split: str
    steps: list = field(default_factory=list)
    model: object = None
    device: object = None
    progress: object = None
    protocol: dict = field(default_factory=dict)
    overall: object = field(default_factory=PhysicalMetrics)
    extensions: dict = field(default_factory=dict)
    restore: bool = False
    phase: str = "infer"


def open_inference(config, *, dataset_component, model_component, session, trained=None):
    """解析检查点和准备引用并验证来源；不构建模型或执行预测。"""
    config = deepcopy(config)
    post = config["infer"]
    value = post.get("checkpoint", "last")
    if trained is not None:
        if trained.get("mode", "").endswith("_check") or "checkpoints" not in trained:
            raise ValueError("训练检查报告不是检查点产物")
        if value in (None, "last", "latest", "best"):
            value = trained["checkpoints"][value or "last"]
    checkpoint = Path(value or "last")
    if str(checkpoint) in {"last", "latest", "best"}:
        checkpoint = session.run_dir / "checkpoints" / f"{checkpoint}.pt"
    if not checkpoint.is_file():
        raise ValueError(f"post 需要可用检查点: {checkpoint}")
    reference = (
        post.get("preparation")
        or config["train"].get("preparation")
        or checkpoint.parent.parent / "artifacts/preparation.json"
    )
    old = json.loads(Path(reference).read_text())
    config["train"]["manifest"] = old["manifest"]
    data = consume(config, dataset_component, model_component, reference)
    split = post.get("split", "test")
    samples = list(post["samples"] or data.view.partitions.get(split, []))
    if (
        not samples
        or len(samples) != len(set(samples))
        or not set(samples) <= set(data.view.partitions.get(split, []))
    ):
        raise ValueError("评价样本名单为空、重复或不属于指定分片")
    return PhysicalInference(
        config, dataset_component, model_component, session, checkpoint, data, samples, split
    )


def configure_restore(job, *, settings=None):
    """登记权重恢复；优化器状态不会进入推理。"""
    if job.restore:
        raise ValueError("恢复步骤重复")
    job.restore = True
    return job


def _register(job, name, operation):
    if any(key == name for key, _ in job.steps):
        raise ValueError(f"后处理步骤重复: {name}")
    job.steps.append((name, operation))
    return job


def configure_prediction(job, *, settings=None, operation=None):
    """注入 model/sample/config/normalization → 物理预测映射。"""
    selection = plain(settings or job.config["infer"]).get("prediction", {})
    predict = resolve_operation(
        selection, default=job.model_component.predict_sample, operation=operation
    )
    if operation is not None or selection.get("target"):
        job.extensions["prediction"] = operation_record(predict)

    def apply(item):
        from ai4e_core.abilities.inference import predict as predict_once

        item.predictions = predict_once(
            job.model,
            item.sample,
            job.config,
            job.data.normalization,
            operation=predict,
            preserve_rng=False,
            preparation_id=job.data.record["digest"] + ":" + item.name,
        )
        return item

    return _register(job, "prediction", apply)


def configure_physical_output(job, *, operation=None):
    """校验完整物理场覆盖；默认模型接口已反变换，不再重复反归一化。"""
    if operation is not None:
        job.extensions["physical_output"] = operation_record(operation)

    def apply(item):
        if item.predictions is None:
            raise ValueError("物理输出需要前一步预测")
        if operation is not None:
            item.predictions = operation(item.predictions, job.data.normalization)
        for domain, binding in job.config["trainprep"]["domains"].items():
            domain_data = item.sample["domains"][domain]
            position = item.sample["fields"][binding["position"]]
            item.payloads[f"{domain}.position"] = position
            item.payloads[f"{domain}.ids"] = domain_data["ids"]
            targets = {}
            for field_name, source in binding["targets"].items():
                pred, truth = item.predictions[source].cpu(), item.sample["fields"][source]
                if pred.shape != truth.shape or len(pred) != len(position):
                    raise ValueError(f"{item.name}/{domain}/{field_name}: 全点预测覆盖不一致")
                key = f"{domain}.{field_name}"
                item.payloads[key + ".prediction"] = pred
                item.payloads[key + ".truth"] = truth
                targets[field_name] = key
            component = job.dataset_component
            comparison = (
                component.comparison_metadata(job.config, item.sample, domain)
                if hasattr(component, "comparison_metadata")
                else {}
            )
            item.domains[domain] = {
                "position": f"{domain}.position",
                "ids": f"{domain}.ids",
                "targets": targets,
                "identity_basis": domain_data["identity_basis"],
                "coordinate_space": coordinate_space(
                    job.config.get("dataset", {}).get("coordinate_space")
                ),
                "topology": comparison.get("topology", domain_data["topology"]),
                "entity_set": comparison.get("entity_set"),
                "units": {
                    name: comparison.get("units", {}).get(source)
                    for name, source in binding["targets"].items()
                },
            }
        return item

    return _register(job, "physical_output", apply)


def configure_evaluation(job, *, settings=None, operation=None, sample_operation=None):
    """登记逐样本及总体物理指标；指标工厂可通过配置或对象替换。"""
    settings = plain(settings or job.config["infer"])
    if not settings.get("evaluate", True):
        return job
    selection = settings.get("metric", {})
    factory = resolve_operation(selection, default=PhysicalMetrics, operation=operation)
    job.overall = factory()
    if operation is not None or selection.get("target"):
        job.extensions["metric"] = operation_record(factory)

    from .evaluation import evaluate_sample

    sample_fn = resolve_operation(
        settings.get("sample_metric", {}), default=evaluate_sample, operation=sample_operation
    )
    if sample_operation is not None or settings.get("sample_metric", {}).get("target"):
        job.extensions["sample_metric"] = operation_record(sample_fn)

    def apply(item):
        if not item.domains:
            raise ValueError("评价前必须交接物理输出")
        metrics = factory()
        for declaration in item.domains.values():
            for key in declaration["targets"].values():
                pred, truth = item.payloads[key + ".prediction"], item.payloads[key + ".truth"]
                metrics.update(key, pred.numpy(), truth.numpy())
                job.overall.update(key, pred.numpy(), truth.numpy())
        item.metrics = metrics.finalize()
        if job.phase == "infer":
            from .catalog import describe_fields

            selections = getattr(job, "selection", None)
            if selections is None:
                choices = describe_fields(job.config, dataset_component=job.dataset_component)
                selections = [f for f in choices if f["default"]]
            item.metric_records = sample_fn(item, selections, settings.get("metrics"))
            if not isinstance(item.metric_records, list) or {
                row.get("field_id") for row in item.metric_records
            } != {f["id"] for f in selections}:
                raise ValueError("用户评价必须交付每个所选字段的具名指标记录")
        return item

    return _register(job, "evaluation", apply)


def configure_save(job, *, output, settings=None):
    """登记物理张量及单样本清单事务保存。"""
    settings = plain(settings or job.config["infer"])
    if not settings.get("save_predictions", True):
        return job
    root = Path(output)

    def apply(item):
        if not item.domains:
            raise ValueError("保存前必须交接物理输出")
        # 选择按原始字段保存完整向量，不能把一个分量伪装成标量场。
        payloads, domains = item.payloads, item.domains
        if getattr(job, "selection", None):
            domains, payloads = {}, {}
            selected = {(f["domain"], f["field"]) for f in job.selection}
            for domain, declaration in item.domains.items():
                targets = {
                    name: key
                    for name, key in declaration["targets"].items()
                    if (domain, name) in selected
                }
                derived = {
                    name: value
                    for name, value in declaration.get("derived_fields", {}).items()
                    if (domain, name) in selected
                }
                if not targets and not derived:
                    continue
                domains[domain] = {**declaration, "targets": targets}
                if "derived_fields" in declaration:
                    domains[domain]["derived_fields"] = derived
                keys = [declaration["position"], declaration["ids"]]
                keys += [
                    key + suffix for key in targets.values() for suffix in (".prediction", ".truth")
                ]
                keys += [value["field"] for value in derived.values()]
                payloads.update({key: item.payloads[key] for key in keys})
        metadata = {
            "identity": item.sample["identity"],
            "protocol": job.protocol["digest"],
            "domains": domains,
            "metrics": item.metrics,
            "metric_records": item.metric_records,
            "component_selection": getattr(job, "selection", None),
        }
        filemap = {key: key + ".pt" for key in payloads}
        metadata["filemap"] = filemap
        target = root / item.name
        if (
            not target.resolve().is_relative_to(root.resolve())
            or target.resolve() == root.resolve()
        ):
            raise ValueError("推理样本输出路径越界")
        write_named_tensors(
            target,
            payloads,
            filemap,
            overwrite=settings.get("overwrite", False),
            extra_writers={"manifest.json": lambda path: save_json(path, metadata)},
        )
        item.manifest = str(target / "manifest.json")
        job.progress.committed(item.manifest)
        return item

    return _register(job, "save", apply)


def configure_mesh_export(job, *, settings=None):
    """登记已保存预测的网格回贴；关闭或失败时把原因写进清单，不静默缺文件。"""
    settings = plain(settings or job.config["infer"])
    from ai4e_core.applications.aero_cfd.infer.vtk_export import VTK_DISABLED, skip_vtk

    enabled = bool(settings.get("export_mesh", settings.get("export_vtk", True)))
    if enabled:
        from ai4e_core.applications.aero_cfd.infer.vtk_capability import describe_vtk_exports

        capability = describe_vtk_exports(
            job.config, dataset_component=getattr(job, "dataset_component", None)
        )
        if not capability["mesh"]["available"]:
            enabled = False
            skip_reason = capability["mesh"]["reason"]
        else:
            skip_reason = VTK_DISABLED
    else:
        skip_reason = VTK_DISABLED

    def apply(item):
        from ai4e_core.applications.aero_cfd.post.mesh_export import export_prediction_meshes

        if item.manifest is None:
            if enabled:
                raise ValueError("网格回贴需要先保存预测清单")
            return item
        if not enabled:
            skip_vtk(item.manifest, skip_reason, channel="mesh")
            return item
        try:
            item.meshes = export_prediction_meshes(
                job.config,
                job.dataset_component,
                item.manifest,
                committed=job.progress.committed,
                source_meshes={k: v.get("mesh") for k, v in item.sample["domains"].items()},
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            skip_vtk(item.manifest, str(exc), channel="mesh")
            raise
        return item

    return _register(job, "mesh", apply)


def check_report(job):
    """只校验检查点元数据与步骤依赖，不构建网络或发布产物。"""
    _validate_steps(job)
    state = torch.load(job.checkpoint, map_location="cpu", weights_only=False)
    if state["contract"]["preparation"] != job.data.record["digest"]:
        raise ValueError("检查点物理准备来源不一致")
    result = {"mode": job.phase + "_check", "samples": job.samples}
    job.session.report(result, stage=job.phase)
    return result


def _validate_steps(job):
    if job.phase == "infer" and getattr(job, "selection", None) is None:
        from .selection import resolve_selection

        job.selection = resolve_selection(
            job.config,
            job.dataset_component,
            job.config["infer"].get("fields"),
            derived_fields=job.extensions.get("derived_fields"),
        )
    names = [name for name, _ in job.steps]
    if not job.restore or "prediction" not in names or "physical_output" not in names:
        raise ValueError("后处理需要恢复、预测与物理输出步骤")
    dependencies = {
        "physical_output": "prediction",
        "evaluation": "physical_output",
        "save": "physical_output",
        "selection": "physical_output",
        "mesh": "save",
    }
    for name in names:
        if name.startswith("derived:"):
            dependencies[name] = "physical_output"
            if "save" in names and names.index(name) >= names.index("save"):
                raise ValueError("派生字段必须在保存之前登记")
    for step, parent in dependencies.items():
        if step in names and (parent not in names or names.index(parent) >= names.index(step)):
            raise ValueError(f"{step} 必须位于 {parent} 之后")


def _execute(job, dataset_component=None, model_component=None, session=None):
    """执行登记顺序；保留旧 config/component/session 入口作为兼容包装。"""
    if isinstance(job, dict):
        config = job
        job = open_inference(
            config,
            dataset_component=dataset_component,
            model_component=model_component,
            session=session,
        )
        job = configure_restore(job)
        job = configure_prediction(job)
        job = configure_physical_output(job)
        job = configure_evaluation(job)
        job = configure_save(job, output=config["paths"]["datasets"]["predictions"])
        job = configure_mesh_export(job)
    if job.session.dry_run:
        return check_report(job)
    _validate_steps(job)
    if job.phase == "infer":
        job.session.artifact(
            "inference-progress.json",
            {
                "mode": "infer",
                "status": "running",
                "phase": "restore",
                "total": len(job.samples),
                "completed": 0,
                "results": [],
            },
        )
    restore_started = perf_counter()
    job.device = resolve_device(job.config["train"]["device"])
    job.model = (
        job.model_component.construct(**job.model_component.training_parameters(job.config))
        .to(job.device)
        .float()
        .eval()
    )
    state = torch.load(job.checkpoint, map_location="cpu", weights_only=False)
    if state["contract"]["preparation"] != job.data.record["digest"] or state["contract"][
        "component"
    ] != job.model_component.describe(job.model):
        raise ValueError("检查点模型或物理准备来源不一致")
    job.model.load_state_dict(state["model"], strict=True)
    synchronize(job.device)
    restore_seconds = perf_counter() - restore_started
    job.protocol = {
        "version": 1,
        "dataset": job.data.record["dataset"],
        "preparation": job.data.record["digest"],
        "weights": file_fingerprint(job.checkpoint),
        "model": job.model_component.SOURCE,
        "samples": job.samples,
        "split": job.split,
        "settings": job.config["infer"],
        "execution": {"device": str(job.device), "precision": "fp32"},
    }
    if job.extensions:
        job.protocol["extensions"] = job.extensions
    job.protocol["digest"] = fingerprint(job.protocol)
    names = [name for name, _ in job.steps]
    job.progress = PostProgress(
        job.session,
        {
            name: name in names
            for name in dict.fromkeys(
                ["prediction", "physical_output", "evaluation", "save", "mesh", *names]
            )
        },
        phase=job.phase,
    )
    job.progress.protocol = job.protocol
    for record in job.progress.report["operations"].values():
        record["expected"] = len(job.samples)
    results = []
    try:
        with preserve_randomness(), torch.no_grad():
            torch.manual_seed(job.config["sampling"]["seed"])

            def process(name):
                item = InferenceSample(
                    name,
                    job.data.view.read(job.split, job.data.view.partitions[job.split].index(name)),
                )
                for step, operation in job.steps:
                    with (
                        job.progress.operation(step),
                        job.progress.unit([{"sample": name, "partition": job.split}]),
                    ):
                        with measure(job.device if step == "prediction" else "cpu") as elapsed:
                            item = operation(item)
                        item.timings[step] = elapsed["seconds"]
                result = {
                    "sample": name,
                    "split": job.split,
                    "manifest": item.manifest,
                    "metrics": item.metrics,
                    "metric_records": item.metric_records,
                    "timings": item.timings,
                    "identity": item.sample["identity"],
                    "fields": item.domains,
                }
                if job.phase == "infer":
                    from ai4e_core.abilities.data.validate.fingerprint import fingerprint as digest

                    result["evidence"] = digest(
                        {
                            k: result[k]
                            for k in ("identity", "fields", "metrics", "metric_records", "timings")
                        }
                    )
                if item.meshes is not None:
                    result["meshes"] = item.meshes
                results.append(result)
                job.progress.report["results"] = list(results)
                job.progress.report["completed"] = len(results)
                job.progress.publish()
                return result

            job.progress.report["total"] = len(job.samples)
            job.progress.report["completed"] = 0
            job.progress.publish()
            # 同一检查点的样本顺序和随机流不变，循环归公共运行执行器。
            job.session.execute_samples(job.samples, process, stage=job.phase)
        report = {
            "version": 1,
            "status": "succeeded",
            "protocol": job.protocol,
            "results": results,
            "metrics": job.overall.finalize() if "evaluation" in names else {},
        }
        report["timings"] = {"restore": restore_seconds}
        job.session.artifact("physical-predictions.json", report)
        if job.phase == "infer":
            path = job.session.artifact("inference-results.json", {**report, "version": 2})
            from .indexing import register_results

            register_results(job.session, path, report)
        job.progress.finish()
        job.session.report(report, stage=job.phase)
        return report
    except BaseException as exc:
        job.progress.finish(exc)
        raise
    finally:
        job.model = None
        if job.device.type == "mps":
            torch.mps.empty_cache()


def execute(job, dataset_component=None, model_component=None, session=None):
    """运行完整物理推理；包括模型构造在内均不污染调用者的随机流。"""
    try:
        with preserve_randomness():
            return _execute(job, dataset_component, model_component, session)
    except BaseException as exc:
        if isinstance(job, PhysicalInference) and not job.session.dry_run and job.progress is None:
            progress = PostProgress(job.session, {"restore": True}, phase=job.phase)
            progress.finish(exc)
        raise
    finally:
        if isinstance(job, PhysicalInference):
            job.model = None
