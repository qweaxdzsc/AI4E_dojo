"""rawprep 阶段：选择组件并调用外流标准装配。"""

import sys
from functools import partial

sys.dont_write_bytecode = True
from configuration import application_parameters, load_configuration
from omegaconf import OmegaConf

from ai4e_contrib.application.aero_cfd import load
from ai4e_core import run
from ai4e_core.run.training import TrainingRun


def rawprep(cfg):
    """同一入口消费案例配置，业务装配保留在 application。"""
    cfg = OmegaConf.create(application_parameters(cfg))
    selected = load(cfg)
    return selected.workflow.datapre(
        cfg,
        dataset_component=selected.dataset,
        model_component=selected.model,
        session=TrainingRun(),
        executor=partial(run.execute, settings=OmegaConf.to_container(cfg, resolve=True)),
    )


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
