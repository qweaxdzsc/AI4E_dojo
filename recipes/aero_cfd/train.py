"""train 阶段：选择组件并调用外流标准装配。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_configuration
from omegaconf import OmegaConf

from ai4e_contrib.application.aero_cfd import load
from ai4e_core import run
from ai4e_core.run.training import TrainingRun


def train(cfg, prepared=None):
    """同一入口消费案例配置，业务装配保留在 application。"""
    cfg = OmegaConf.create(application_parameters(cfg))
    selected = load(cfg)
    return selected.workflow.train(
        cfg,
        prepared,
        dataset_component=selected.dataset,
        model_component=selected.model,
        session=TrainingRun(),
    )


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
