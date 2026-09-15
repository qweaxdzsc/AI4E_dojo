"""历史共享物理工作流兼容包装；新 recipe 直接排列公开步骤。"""

from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd.train import physical as fitting
from ai4e_core.applications.aero_cfd.train.physical import PreparedSamples  # noqa: F401
from ai4e_core.applications.aero_cfd.trainprep import physical as preparation


def datapre(cfg, *, dataset_component, model_component, executor, session):
    """兼容历史来源组件的原始处理入口。"""
    return dataset_component.prepare_physical(cfg, executor=executor, session=session)


def trainprep(cfg, dataset=None, *, dataset_component, model_component, session):
    """兼容旧调用；使用与显式 recipe 相同的公开步骤。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    data = preparation.open_dataset(config, dataset_component, model_component, dataset=dataset)
    data = preparation.bind_fields(data)
    data = preparation.freeze_normalization(data)
    data = preparation.configure_sampling(data)
    data = preparation.configure_batching(data)
    data = preparation.validate_preparation(data)
    return preparation.publish(data, session=session)


def train(cfg, prepared=None, *, dataset_component, model_component, session):
    """兼容历史物理训练；算法只维护在训练业务步骤内。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    job = fitting.open_training(
        config,
        reference=prepared or config["train"].get("preparation"),
        dataset_component=dataset_component,
        model_component=model_component,
        session=session,
    )
    if session.dry_run:
        return fitting.check_report(job)
    job = fitting.build_model(job)
    job = fitting.configure_objectives(job)
    job = fitting.configure_optimization(job)
    job = fitting.configure_evaluation(job)
    job = fitting.configure_resume(job, checkpoint=config["train"].get("resume"))
    return fitting.execute_training(job)


def post(cfg, *, dataset_component, model_component, session):
    """兼容历史完整物理预测。"""
    from ai4e_core.applications.aero_cfd.post.physical import execute

    return execute(
        model_component.resolve(OmegaConf.to_container(cfg, resolve=True)),
        dataset_component,
        model_component,
        session,
    )
