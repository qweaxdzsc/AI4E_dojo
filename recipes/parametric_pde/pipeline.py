"""参数化 PDE 的显式阶段调用，无算法或训练循环。"""

import sys

sys.dont_write_bytecode = True
from configuration import components, load_configuration, validate
from omegaconf import OmegaConf

from ai4e_core import run
from ai4e_core.applications import parametric_pde
from ai4e_core.run.training import TrainingRun


def execute(name, cfg):
    """配置映射与公开装配调用，独立阶段使用相同入口。"""
    cfg = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else cfg
    validate(cfg)
    return getattr(parametric_pde, name)(cfg, **components(cfg), session=TrainingRun())


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {
                name: (lambda cfg, name=name: execute(name, cfg))
                for name in ("rawprep", "trainprep", "train", "post")
            },
            script=__file__,
            config_loader=load_configuration,
        )
    )
