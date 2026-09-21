"""原始处理：登记单样本步骤，再统一执行和发布。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.rawprep import physical


def rawprep(cfg):
    """按 NASA 物理字段契约交付完整数据清单。"""
    session = run.TrainingRun()
    config = application_parameters(cfg, session=session)
    components = load_components(cfg)
    return physical.execute(config, components.dataset, run.execute, session)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
