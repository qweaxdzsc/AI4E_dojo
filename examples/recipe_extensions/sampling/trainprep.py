"""训练准备：绑定字段、冻结变换，登记在线采样与拼批。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.trainprep import preparation as prep
from ai4e_core.run.training import TrainingRun


def trainprep(cfg, dataset=None):
    """返回可被训练和独立后处理消费的准备引用。"""
    components = load_components(cfg)
    session = TrainingRun()
    config = application_parameters(cfg)
    data = prep.open_dataset(config, dataset)
    data = prep.bind_fields(data, settings=cfg.trainprep)
    data = prep.freeze_normalization(data, settings=cfg.trainprep.normalization)
    # 这里登记模型输入组织；每轮实际取样发生在训练迭代中。
    data = prep.configure_sampling(
        data, settings=cfg.model.sampling, model_component=components.model
    )
    data = prep.configure_batching(
        data, batch_size=cfg.train.batch_size, model_component=components.model
    )
    data = prep.validate_preparation(data)
    if session.dry_run:
        return prep.check_report(data, session=session)
    return prep.publish(data, session=session)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
