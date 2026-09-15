"""锚点外流标准装配；数据与模型组件由普通 recipe 显式注入。"""

from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd import rawprep as pre
from ai4e_core.applications.aero_cfd.post.stage import run as post_run
from ai4e_core.applications.aero_cfd.train import fitting
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep import preparation
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe


def datapre(cfg, *, dataset_component, model_component, executor, session):
    """旧整段入口复用显式步骤，保持统计、事务提交和发布的同一实现。"""
    source = pre.open_source(component=dataset_component, settings=cfg.dataset)
    data = pre.read(source, sources=cfg.sources)
    data = pre.extract_fields(data, fields=cfg.fields, extraction=cfg.get("extraction"))
    data = pre.derive_geometry(data, features=cfg.geometry)
    data = pre.select_fields(data, fields=cfg.save_fields, extraction=cfg.get("extraction"))
    data = pre.validate_fields(data)
    data = pre.filter_points(data, filters=cfg.filters)
    data = pre.validate_fields(data)
    data = pre.encode(
        data,
        **(
            {"formats": list(cfg["formats"])}
            if "formats" in cfg
            else {"format": cfg.get("format", "pt")}
        ),
        vtkhdf=cfg.get("vtkhdf", False),
    )
    results = executor(data, save=pre.save_sample, output=cfg.paths.datasets)
    statistics = pre.compute_statistics(results, settings=cfg.statistics)
    return pre.publish_dataset(results, statistics=statistics)


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
