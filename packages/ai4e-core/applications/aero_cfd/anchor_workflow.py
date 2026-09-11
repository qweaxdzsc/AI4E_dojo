"""锚点外流标准装配；数据与模型组件由普通 recipe 显式注入。"""

from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd import rawprep as pre
from ai4e_core.applications.aero_cfd.post.stage import run as post_run
from ai4e_core.applications.aero_cfd.train import fitting
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep import preparation
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe


def datapre(cfg, *, dataset_component, model_component, executor, session):
    """配置直接使用 cfg；样本循环和文件布局由 Dataset 与运行器承担。"""
    if cfg.get("format", "pt") not in {"pt", "zarr"}:
        raise ValueError("rawprep.format 必须为 pt 或 zarr")
    dataset = dataset_component.open_dataset(
        root=cfg.dataset.root,
        manifest=cfg.dataset.manifest,
        samples=cfg.dataset.samples,
        partition=cfg.dataset.partition,
    )

    # 只登记步骤，不装载网格；真正读盘在 execute。
    prep = pre.read(dataset, sources=cfg.sources)
    extraction_output = None
    selected_fields = OmegaConf.to_container(cfg.fields, resolve=True)
    if cfg.get("extraction"):
        from ai4e_core.applications.aero_cfd.rawprep.extraction import compile_extraction

        extraction_output = compile_extraction(
            OmegaConf.to_container(cfg.extraction, resolve=True),
            format=cfg.get("format", "pt"),
            declarations=dataset.metadata["outputs"],
            source_catalog=dataset.metadata["fields"],
        )
        for domain, fields in extraction_output.pop("source_fields", {}).items():
            selected_fields.setdefault(domain, {}).update(fields)
    prep = pre.extract_fields(prep, fields=selected_fields)
    prep = pre.derive_geometry(prep, features=cfg.geometry)

    # 选择训练字段并验证行身份；过滤会同步更新同组字段。
    if extraction_output is not None:
        prep = pre.select_fields(prep, output=extraction_output)
    else:
        prep = pre.select_fields(prep, fields=cfg.save_fields)
        if cfg.get("format", "pt") == "zarr":
            output = dict(prep.options["output"])
            output["filemap"] = {key: key + ".zarr" for key in output["filemap"]}
            prep = pre.select_fields(prep, output=output)
    prep = pre.validate_fields(prep)
    prep = pre.filter_points(prep, filters=cfg.filters)
    prep = pre.validate_fields(prep)
    prep = pre.to_tensors(prep, vtkhdf=bool(cfg.get("vtkhdf", False)))

    # 实际逐样本执行和安全提交；不在模板内编写循环。
    results = executor(prep, save=pre.save_sample, output=cfg.paths.datasets)
    published = pre.publish_dataset(results)
    pre.compute_statistics(published, cfg.statistics)
    return published


def trainprep(cfg, dataset=None, *, dataset_component, model_component, session):
    """独立或在 pipeline 中交付可重复消费的准备引用。"""
    config = apply_resolved(OmegaConf.to_container(cfg, resolve=True))
    data = preparation.open_dataset(config, dataset)
    data = preparation.prepare_fields(data)
    data = preparation.freeze_normalization(data)
    data = preparation.configure_sampling(data, prepare=model_component.prepare_inputs)
    data = preparation.configure_batching(data, collate=model_component.collate)
    data = preparation.validate_preparation(data)
    result = preparation.publish(data, session)
    return result


def train(cfg, prepared=None, *, dataset_component, model_component, session):
    """已有准备结果优先；直接训练已有数据时自动执行同一准备链。"""
    config = apply_resolved(OmegaConf.to_container(cfg, resolve=True))
    mode = config["train"].get("mode", "fit")
    reference = prepared or config["train"].get("preparation")
    if session.dry_run and reference:
        data = preparation.consume(
            config,
            reference,
            prepare=model_component.prepare_inputs,
            collate=model_component.collate,
        )
        result = {"mode": "train_check", "split_counts": data.record["split_counts"]}
        session.report(result)
        return result
    if session.dry_run or mode in {"probe", "prepare"}:
        config["train"]["mode"] = "prepare" if mode == "fit" else mode
        result = probe(config, prepare=model_component.prepare_inputs, dry_run=session.dry_run)
        session.report(
            {
                "mode": config["train"]["mode"],
                "sample_id": result["sample_id"],
                "split_counts": result["split_counts"],
                "names": list(result["physical"]),
            }
        )
        return result

    job = fitting.open_training(
        config,
        session,
        reference=prepared,
        factory=model_component.construct,
        predict=model_component.predict,
        prepare=model_component.prepare_inputs,
        collate=model_component.collate,
        source=model_component.SOURCE,
    )
    job = fitting.build_model(job)
    job = fitting.configure_objectives(job)
    job = fitting.configure_optimization(job)
    job = fitting.configure_evaluation(job, callbacks=())
    result = fitting.execute_training(job)
    return result


def post(cfg, *, dataset_component, model_component, session):
    """只声明使用的贡献组件，评估、保存、点云和完整网格回贴由应用装配。"""
    return post_run(
        OmegaConf.to_container(cfg, resolve=True),
        session,
        construct=model_component.construct,
        predict=model_component.predict,
        prepare_inputs=model_component.prepare_inputs,
        collate=model_component.collate,
        context_factory=model_component.InferenceContext,
    )
